"""Adaptador Higgsfield: gera a imagem com o SDK oficial (`submit` + polling limitado).

A documentação da Higgsfield recomenda `submit` (e não `subscribe`) quando é preciso controlar o
ciclo de vida do pedido. O polling do SDK não tem limite, então o laço aqui é nosso: desiste após
`max_polls` consultas ou `timeout` segundos e cancela o pedido. Geramos um slide por vez, o que
respeita o limite de pedidos simultâneos da conta.
"""

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import higgsfield_client as hf
import httpx

from content_pipeline.images.base import ImageGenerationError

POLL_INTERVAL_SECONDS = 3.0
MAX_POLLS = 100
TIMEOUT_SECONDS = 300.0
DOWNLOAD_TIMEOUT_SECONDS = 60.0


class HiggsfieldImageGenerator:
    """Implementa `ImageGenerator` com a API da Higgsfield."""

    def __init__(
        self,
        model: str,
        *,
        resolution: str | None = None,
        client: Any = None,
        http: httpx.Client | None = None,
        poll_interval: float = POLL_INTERVAL_SECONDS,
        max_polls: int = MAX_POLLS,
        timeout: float = TIMEOUT_SECONDS,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Configura o adaptador.

        Args:
            model: Endpoint do modelo, ex.: "higgsfield-ai/soul/v2/standard".
            resolution: Enviada só se definida (nem todo modelo aceita o campo).
            client: Cliente com `submit` (um `SyncClient`; nos testes, um falso).
            http: Cliente httpx para baixar a imagem; existe para os testes (`MockTransport`).
            poll_interval: Espera entre consultas de status, em segundos.
            max_polls: Máximo de consultas de status por imagem.
            timeout: Tempo máximo de espera por imagem, em segundos.
            sleep: Função de espera; injetável para os testes não dormirem.
            clock: Relógio monotônico; injetável para testar o tempo limite.
        """
        self.model = model
        self.resolution = resolution
        self._client = client or hf.SyncClient()
        self._http = http
        self._poll_interval = poll_interval
        self._max_polls = max_polls
        self._timeout = timeout
        self._sleep = sleep
        self._clock = clock

    def generate(self, prompt: str, *, aspect_ratio: str, out_path: Path) -> Path:
        """Pede a imagem, espera ficar pronta e grava em `out_path` (extensão da URL, se houver).

        Raises:
            ImageGenerationError: Pedido recusado, status final sem sucesso, tempo esgotado ou
                falha de rede/download.
        """
        arguments = {"prompt": prompt, "aspect_ratio": aspect_ratio}
        if self.resolution:
            arguments["resolution"] = self.resolution
        try:
            controller = self._client.submit(self.model, arguments=arguments)
            result = self._wait(controller)
            return self._download(_image_url(result), out_path)
        except (hf.HiggsfieldClientError, httpx.HTTPError) as exc:
            raise ImageGenerationError(f"Falha na Higgsfield: {exc}") from exc

    def _wait(self, controller: Any) -> dict:
        """Consulta o status até um estado final, respeitando `max_polls` e `timeout`."""
        deadline = self._clock() + self._timeout
        for _ in range(self._max_polls):
            if isinstance(controller.status(), hf.DONE_STATUSES):
                return controller.get()
            if self._clock() >= deadline:
                break
            self._sleep(self._poll_interval)

        try:
            controller.cancel()  # só funciona se o pedido ainda não começou; o erro é esperado
        except hf.HiggsfieldClientError:
            pass
        raise ImageGenerationError(
            f"A imagem não ficou pronta em {self._timeout:.0f}s ou {self._max_polls} consultas "
            f"(pedido {controller.request_id})."
        )

    def _download(self, url: str, out_path: Path) -> Path:
        """Baixa `url` e grava ao lado de `out_path`, com a extensão da URL quando houver."""
        http = self._http or httpx.Client(timeout=DOWNLOAD_TIMEOUT_SECONDS, follow_redirects=True)
        try:
            response = http.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ImageGenerationError(f"Não foi possível baixar a imagem ({url}): {exc}") from exc
        finally:
            if self._http is None:
                http.close()

        suffix = Path(urlparse(url).path).suffix or out_path.suffix
        path = out_path.with_suffix(suffix)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
        return path


def _image_url(result: dict) -> str:
    """Extrai a URL da primeira imagem; status final sem sucesso vira `ImageGenerationError`."""
    status = result.get("status")
    images = result.get("images") or []
    if status != "completed" or not images:
        raise ImageGenerationError(
            f"A geração terminou com status {status!r} (erro: {result.get('error')!r})."
        )
    return images[0]["url"]
