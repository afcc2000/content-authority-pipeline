"""Baixa uma página web e extrai o texto principal.

O conteúdo baixado é NÃO CONFIÁVEL (prompt injection, OWASP LLM01): aceitamos só http(s),
com limite de tamanho e timeout. O texto extraído deve ser tratado como dado, nunca como
instrução, pelos nós que o usam.
"""

from urllib.parse import urlparse

import httpx
import trafilatura

MAX_BYTES = 2_000_000
TIMEOUT_SECONDS = 20.0


class FetchError(RuntimeError):
    """A página não pôde ser baixada ou não tem texto aproveitável."""


def require_http_url(url: str) -> None:
    """Recusa links que não sejam http(s) (ex.: file://, javascript:).

    Raises:
        FetchError: Se o esquema de `url` não for http nem https.
    """
    scheme = urlparse(url).scheme.lower()
    if scheme not in ("http", "https"):
        raise FetchError(f"Só links http(s) são aceitos (recebido: '{scheme or 'sem esquema'}').")


def fetch_url(
    url: str, *, client: httpx.Client | None = None, max_bytes: int = MAX_BYTES
) -> tuple[str | None, str]:
    """Baixa `url` e devolve (título ou None, texto principal).

    Args:
        url: Endereço http(s) da página.
        client: Cliente httpx a usar; existe para os testes (com `httpx.MockTransport`).
        max_bytes: Tamanho máximo do corpo; acima disso o download é abortado.

    Raises:
        FetchError: Esquema diferente de http(s), erro HTTP ou de rede, página maior que
            `max_bytes` ou página sem texto extraível.
    """
    require_http_url(url)

    owns_client = client is None
    http = client or httpx.Client(timeout=TIMEOUT_SECONDS, follow_redirects=True)
    try:
        html = _download(http, url, max_bytes)
    finally:
        if owns_client:
            http.close()

    text = trafilatura.extract(html)
    if not text or not text.strip():
        raise FetchError(f"Nenhum texto extraído de {url}.")
    metadata = trafilatura.extract_metadata(html)
    title = metadata.title if metadata and metadata.title else None
    return title, text.strip()


def _download(http: httpx.Client, url: str, max_bytes: int) -> str:
    """Baixa o corpo em streaming, abortando acima de `max_bytes`, e o decodifica."""
    try:
        with http.stream("GET", url, follow_redirects=True) as response:
            response.raise_for_status()
            chunks: list[bytes] = []
            total = 0
            for chunk in response.iter_bytes():
                total += len(chunk)
                if total > max_bytes:
                    raise FetchError(f"Página maior que o limite de {max_bytes} bytes: {url}")
                chunks.append(chunk)
            encoding = response.encoding or "utf-8"
    except httpx.HTTPError as exc:
        raise FetchError(f"Falha ao baixar {url}: {exc}") from exc
    return b"".join(chunks).decode(encoding, errors="replace")
