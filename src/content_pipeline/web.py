"""Acesso à web via Tavily: leitura opcional de links e busca por tema.

O conteúdo devolvido é NÃO CONFIÁVEL, como no `fetcher`: só aceitamos links http(s) e o
texto é tratado como dado pelos nós que o usam.
"""

import logging
import os
from collections.abc import Callable
from functools import partial
from typing import Any

from tavily import TavilyClient

from content_pipeline.config import Settings
from content_pipeline.fetcher import FetchBlockedError, FetchError, fetch_url, require_http_url
from content_pipeline.models import SearchResult

logger = logging.getLogger(__name__)

Fetch = Callable[[str], tuple[str | None, str]]
Search = Callable[[str], list[SearchResult]]


class SearchError(RuntimeError):
    """A busca na web falhou."""


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
    require_http_url(url)

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


def fetch_with_fallback(url: str, *, primary: Fetch, fallback: Fetch) -> tuple[str | None, str]:
    """Lê `url` com `primary`; se o site bloquear a leitura direta (403), tenta `fallback`.

    Outros erros (link quebrado, página sem texto, grande demais) não acionam o fallback.
    """
    try:
        return primary(url)
    except FetchBlockedError as exc:
        logger.warning(
            "Leitura direta de %s bloqueada (HTTP %s); tentando pelo Tavily.", url, exc.status_code
        )
        return fallback(url)


def make_fetch(settings: Settings) -> Fetch:
    """Escolhe a função de leitura de links conforme `WEB_READER`.

    Com o padrão (`trafilatura`) e `TAVILY_API_KEY` no ambiente, o Tavily vira o fallback para
    sites que bloqueiam a leitura direta.

    Raises:
        FetchError: `WEB_READER=tavily` sem `TAVILY_API_KEY` no ambiente.
    """
    has_tavily_key = bool(os.environ.get("TAVILY_API_KEY"))
    if settings.web_reader == "tavily":
        # Sem chave, o TavilyClient não falha: entra num modo "keyless" limitado.
        # Checamos aqui para dar uma mensagem clara antes de o pipeline começar.
        if not has_tavily_key:
            raise FetchError("WEB_READER=tavily exige TAVILY_API_KEY no .env.")
        return partial(tavily_fetch, client=TavilyClient())
    if has_tavily_key:
        tavily = partial(tavily_fetch, client=TavilyClient())
        return partial(fetch_with_fallback, primary=fetch_url, fallback=tavily)
    return fetch_url


def tavily_search(query: str, *, client: Any = None, max_results: int = 5) -> list[SearchResult]:
    """Busca `query` com o Tavily Search e devolve os resultados.

    Args:
        query: Tema ou pergunta a buscar.
        client: Cliente com o método `search` (um `TavilyClient`; nos testes, um falso).
        max_results: Número máximo de resultados.

    Raises:
        SearchError: Erro do Tavily (chave inválida, limite de uso, rede).
    """
    tavily = client or TavilyClient()
    try:
        response = tavily.search(query, max_results=max_results)
    except Exception as exc:  # as exceções do Tavily não têm classe-base comum
        raise SearchError(f"Falha na busca por '{query}': {exc}") from exc

    return [
        SearchResult(
            url=item["url"],
            title=item.get("title") or item["url"],
            snippet=item.get("content") or "",
        )
        for item in response.get("results") or []
        if item.get("url")
    ]


def make_search(settings: Settings) -> Search | None:
    """Devolve a função de busca, ou None se não houver `TAVILY_API_KEY` no ambiente.

    `settings` não é usado ainda; fica na assinatura para espelhar `make_fetch`.
    """
    if not os.environ.get("TAVILY_API_KEY"):
        return None
    return partial(tavily_search, client=TavilyClient())
