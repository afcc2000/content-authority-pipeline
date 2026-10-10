"""Acesso à web via Tavily: leitura opcional de links.

O conteúdo devolvido é NÃO CONFIÁVEL, como no `fetcher`: só aceitamos links http(s) e o
texto é tratado como dado pelos nós que o usam.
"""

import os
from collections.abc import Callable
from functools import partial
from typing import Any
from urllib.parse import urlparse

from tavily import TavilyClient

from content_pipeline.config import Settings
from content_pipeline.fetcher import FetchError, fetch_url

Fetch = Callable[[str], tuple[str | None, str]]

MAX_CHARS = 200_000


def tavily_fetch(
    url: str, *, client: Any = None, max_chars: int = MAX_CHARS
) -> tuple[str | None, str]:
    """Lê `url` com o Tavily Extract e devolve (título ou None, texto em Markdown).

    Args:
        url: Endereço http(s) da página.
        client: Cliente com o método `extract` (um `TavilyClient`; nos testes, um falso).
        max_chars: Tamanho máximo do texto devolvido; o excedente é cortado.

    Raises:
        FetchError: Esquema diferente de http(s), erro do Tavily ou página sem conteúdo.
    """
    scheme = urlparse(url).scheme.lower()
    if scheme not in ("http", "https"):
        raise FetchError(f"Só links http(s) são aceitos (recebido: '{scheme or 'sem esquema'}').")

    tavily = client or TavilyClient()
    try:
        response = tavily.extract(urls=url, format="markdown")
    except Exception as exc:  # as exceções do Tavily não têm classe-base comum
        raise FetchError(f"Falha ao ler {url} com o Tavily: {exc}") from exc

    results = response.get("results") or []
    content = (results[0].get("raw_content") or "").strip() if results else ""
    if not content:
        raise FetchError(f"O Tavily não extraiu conteúdo de {url}.")
    return _markdown_title(content), content[:max_chars]


def _markdown_title(markdown: str) -> str | None:
    """Devolve o texto da primeira linha "# " do Markdown, ou None."""
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or None
    return None


def make_fetch(settings: Settings) -> Fetch:
    """Escolhe a função de leitura de links conforme `WEB_READER`.

    Raises:
        FetchError: `WEB_READER=tavily` sem `TAVILY_API_KEY` no ambiente.
    """
    if settings.web_reader == "tavily":
        # Sem chave, o TavilyClient não falha: entra num modo "keyless" limitado.
        # Checamos aqui para dar uma mensagem clara antes de o pipeline começar.
        if not os.environ.get("TAVILY_API_KEY"):
            raise FetchError("WEB_READER=tavily exige TAVILY_API_KEY no .env.")
        return partial(tavily_fetch, client=TavilyClient())
    return fetch_url
