"""Testes da leitura via Tavily com um cliente falso (sem rede)."""

from typing import Any

import pytest
from pydantic import ValidationError

from content_pipeline.fetcher import FetchBlockedError, FetchError, fetch_url
from content_pipeline.web import fetch_with_fallback, make_fetch, tavily_fetch
from tests.fakes import make_settings

MARKDOWN = "# Artigo de Exemplo\n\nPequenas mudanças geram grandes resultados."


class FakeTavilyClient:
    """Imita o `TavilyClient.extract`, devolvendo uma resposta pronta."""

    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def extract(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        return self.response


def test_raw_content_em_markdown_devolve_titulo_e_texto() -> None:
    client = FakeTavilyClient(
        {"results": [{"url": "https://exemplo.com", "raw_content": MARKDOWN}], "failed_results": []}
    )

    title, text = tavily_fetch("https://exemplo.com", client=client)

    assert title == "Artigo de Exemplo"
    assert "grandes resultados" in text
    assert client.calls == [{"urls": "https://exemplo.com", "format": "markdown"}]


def test_url_em_failed_results_levanta_fetch_error() -> None:
    client = FakeTavilyClient({"results": [], "failed_results": ["https://exemplo.com"]})

    with pytest.raises(FetchError, match="exemplo.com"):
        tavily_fetch("https://exemplo.com", client=client)


def test_esquema_file_levanta_fetch_error_sem_chamar_o_cliente() -> None:
    client = FakeTavilyClient({"results": [], "failed_results": []})

    with pytest.raises(FetchError, match="http"):
        tavily_fetch("file:///etc/passwd", client=client)
    assert client.calls == []


def test_make_fetch_padrao_sem_chave_tavily_devolve_fetch_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    assert make_fetch(make_settings()) is fetch_url


def test_make_fetch_padrao_com_chave_tavily_usa_o_tavily_como_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "chave-falsa-de-teste")

    fetch = make_fetch(make_settings())

    assert fetch.func is fetch_with_fallback
    assert fetch.keywords["primary"] is fetch_url


def bloqueado(url: str) -> tuple[str | None, str]:
    raise FetchBlockedError(f"Falha ao baixar {url}: 403 Forbidden", status_code=403)


def test_fallback_le_pelo_tavily_quando_a_leitura_direta_e_bloqueada(
    caplog: pytest.LogCaptureFixture,
) -> None:
    lidos = []

    def tavily(url: str) -> tuple[str | None, str]:
        lidos.append(url)
        return "Título", "Texto lido pelo Tavily."

    with caplog.at_level("WARNING"):
        resultado = fetch_with_fallback("https://exemplo.com/a", primary=bloqueado, fallback=tavily)

    assert resultado == ("Título", "Texto lido pelo Tavily.")
    assert lidos == ["https://exemplo.com/a"]
    assert "403" in caplog.text and "Tavily" in caplog.text


def test_fallback_nao_e_usado_em_outros_erros() -> None:
    def quebrado(url: str) -> tuple[str | None, str]:
        raise FetchError(f"Falha ao baixar {url}: 404 Not Found")

    def tavily(url: str) -> tuple[str | None, str]:
        raise AssertionError("o Tavily não deveria ser chamado")

    with pytest.raises(FetchError, match="404"):
        fetch_with_fallback("https://exemplo.com/a", primary=quebrado, fallback=tavily)


def test_make_fetch_tavily_sem_chave_levanta_fetch_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    with pytest.raises(FetchError, match="TAVILY_API_KEY"):
        make_fetch(make_settings(web_reader="tavily"))


def test_web_reader_invalido_levanta_validation_error() -> None:
    with pytest.raises(ValidationError):
        make_settings(web_reader="xyz")
