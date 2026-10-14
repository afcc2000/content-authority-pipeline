"""Testes da porta ImageGenerator, do adaptador fake e do adaptador Higgsfield (sem rede)."""

import os
import struct
from pathlib import Path

import higgsfield_client as hf
import httpx
import pytest
from dotenv import find_dotenv, load_dotenv

from content_pipeline.images import (
    FakeImageGenerator,
    HiggsfieldImageGenerator,
    ImageConfigError,
    ImageGenerationError,
    make_image_generator,
)
from tests.fakes import make_settings

IMAGE_URL = "https://cdn.exemplo.com/abc/imagem.png"
PNG = b"\x89PNG\r\n\x1a\nconteudo-falso"


def test_fake_grava_prompt_e_registra_chamada(tmp_path: Path) -> None:
    fake = FakeImageGenerator()

    path = fake.generate(
        "Um café sobre a mesa", aspect_ratio="4:5", out_path=tmp_path / "images" / "slide_01.png"
    )

    assert path == tmp_path / "images" / "slide_01.prompt.txt"
    conteudo = path.read_text(encoding="utf-8")
    assert "4:5" in conteudo
    assert "Um café sobre a mesa" in conteudo
    assert fake.calls == ["Um café sobre a mesa"]


def test_dry_run_devolve_fake_mesmo_com_higgsfield() -> None:
    settings = make_settings(image_provider="higgsfield")

    assert isinstance(make_image_generator(settings, dry_run=True), FakeImageGenerator)


def test_higgsfield_sem_dry_run_usa_o_adaptador_com_o_modelo_de_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HF_KEY", "id-falso:segredo-falso")
    settings = make_settings(image_provider="higgsfield", image_model="modelo/de/teste")

    generator = make_image_generator(settings, dry_run=False)

    assert isinstance(generator, HiggsfieldImageGenerator)
    assert generator.model == "modelo/de/teste"


def test_higgsfield_sem_credencial_falha_antes_de_comecar(monkeypatch: pytest.MonkeyPatch) -> None:
    for nome in ("HF_KEY", "HF_API_KEY", "HF_API_SECRET"):
        monkeypatch.delenv(nome, raising=False)
    settings = make_settings(image_provider="higgsfield")

    with pytest.raises(ImageConfigError, match="HF_KEY"):
        make_image_generator(settings, dry_run=False)


class FakeController:
    """Imita o `SyncRequestController` do SDK: devolve os status na ordem dada."""

    def __init__(self, statuses: list[hf.Status], result: dict | None = None) -> None:
        self.request_id = "pedido-1"
        self._statuses = statuses
        self._result = result or {"status": "completed", "images": [{"url": IMAGE_URL}]}
        self.cancelled = False

    def status(self) -> hf.Status:
        return self._statuses.pop(0) if len(self._statuses) > 1 else self._statuses[0]

    def get(self) -> dict:
        return self._result

    def cancel(self) -> None:
        self.cancelled = True


class FakeClient:
    """Imita o `SyncClient` do SDK: registra o `submit` e devolve o controller."""

    def __init__(self, controller: FakeController | None = None, error: Exception | None = None):
        self.controller = controller
        self.error = error
        self.calls: list[tuple[str, dict]] = []

    def submit(self, application: str, arguments: dict) -> FakeController:
        self.calls.append((application, arguments))
        if self.error:
            raise self.error
        return self.controller


def download_ok(request: httpx.Request) -> httpx.Response:
    assert str(request.url) == IMAGE_URL
    return httpx.Response(200, content=PNG)


def make_generator(
    client: FakeClient, handler=download_ok, **overrides
) -> HiggsfieldImageGenerator:
    """Adaptador sem rede e sem espera real (`sleep` falso)."""
    options = {
        "client": client,
        "http": httpx.Client(transport=httpx.MockTransport(handler)),
        "sleep": lambda _seconds: None,
        **overrides,
    }
    return HiggsfieldImageGenerator("higgsfield-ai/soul/v2/standard", **options)


def test_higgsfield_envia_o_pedido_espera_e_grava_a_imagem(tmp_path: Path) -> None:
    controller = FakeController([hf.Queued(), hf.InProgress(), hf.Completed()])
    client = FakeClient(controller)
    generator = make_generator(client, resolution="1080p")

    path = generator.generate("Um café", aspect_ratio="3:4", out_path=tmp_path / "slide_01.png")

    assert client.calls == [
        (
            "higgsfield-ai/soul/v2/standard",
            {"prompt": "Um café", "aspect_ratio": "3:4", "resolution": "1080p"},
        )
    ]
    assert path == tmp_path / "slide_01.png"
    assert path.read_bytes() == PNG


def test_higgsfield_sem_resolucao_nao_envia_o_campo(tmp_path: Path) -> None:
    client = FakeClient(FakeController([hf.Completed()]))

    make_generator(client).generate("x", aspect_ratio="1:1", out_path=tmp_path / "s.png")

    assert "resolution" not in client.calls[0][1]


@pytest.mark.parametrize(
    ("status", "result"),
    [
        (hf.Failed(), {"status": "failed", "error": "sem créditos"}),
        (hf.NSFW(), {"status": "nsfw", "error": None}),
    ],
)
def test_higgsfield_status_final_sem_sucesso_vira_erro(
    tmp_path: Path, status: hf.Status, result: dict
) -> None:
    generator = make_generator(FakeClient(FakeController([status], result)))

    with pytest.raises(ImageGenerationError, match=result["status"]):
        generator.generate("x", aspect_ratio="3:4", out_path=tmp_path / "s.png")


def test_higgsfield_desiste_apos_o_maximo_de_consultas_e_cancela(tmp_path: Path) -> None:
    controller = FakeController([hf.InProgress()])
    generator = make_generator(FakeClient(controller), max_polls=3)

    with pytest.raises(ImageGenerationError, match="pedido-1"):
        generator.generate("x", aspect_ratio="3:4", out_path=tmp_path / "s.png")

    assert controller.cancelled


def test_higgsfield_desiste_apos_o_tempo_limite(tmp_path: Path) -> None:
    agora = iter([0.0, 10.0, 999.0])
    controller = FakeController([hf.InProgress()])
    generator = make_generator(
        FakeClient(controller), timeout=60.0, max_polls=100, clock=lambda: next(agora)
    )

    with pytest.raises(ImageGenerationError, match="60"):
        generator.generate("x", aspect_ratio="3:4", out_path=tmp_path / "s.png")

    assert controller.cancelled


def test_higgsfield_pedido_recusado_no_envio_vira_erro(tmp_path: Path) -> None:
    erro = hf.HiggsfieldClientError("aspect_ratio: '4:5' is not one of [...]")
    generator = make_generator(FakeClient(error=erro))

    with pytest.raises(ImageGenerationError, match="4:5"):
        generator.generate("x", aspect_ratio="4:5", out_path=tmp_path / "s.png")


def test_higgsfield_falha_no_download_vira_erro(tmp_path: Path) -> None:
    generator = make_generator(
        FakeClient(FakeController([hf.Completed()])),
        handler=lambda request: httpx.Response(404),
    )

    with pytest.raises(ImageGenerationError, match="baixar"):
        generator.generate("x", aspect_ratio="3:4", out_path=tmp_path / "s.png")

    assert not (tmp_path / "s.png").exists()


@pytest.mark.integration
def test_higgsfield_real_gera_imagem_3x4(tmp_path: Path) -> None:
    """Gera uma imagem de verdade (gasta créditos). Rode com `uv run pytest -m integration`."""
    load_dotenv(find_dotenv(usecwd=True))
    if not os.getenv("HF_KEY"):
        pytest.skip("HF_KEY não está no .env")
    settings = make_settings(image_provider="higgsfield")

    generator = make_image_generator(settings, dry_run=False)
    path = generator.generate(
        "Minimalist flat illustration of a notebook and a coffee cup",
        aspect_ratio=settings.image_aspect_ratio,
        out_path=tmp_path / "slide_01.png",
    )

    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    assert width / height == pytest.approx(3 / 4, abs=0.01)
