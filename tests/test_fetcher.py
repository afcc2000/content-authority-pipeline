"""Testes do fetcher com `httpx.MockTransport` (sem rede)."""

import httpx
import pytest

from content_pipeline.fetcher import FetchBlockedError, FetchError, fetch_url

PARAGRAPH = "A experiência prática mostra que pequenas mudanças geram grandes resultados. " * 5
HTML = f"""<html>
<head><title>Artigo de Exemplo</title></head>
<body>
  <nav>Início | Blog | Contato</nav>
  <article>
    <h1>Artigo de Exemplo</h1>
    <p>{PARAGRAPH}</p>
    <p>Segundo parágrafo com mais detalhes sobre o tema.</p>
  </article>
  <footer>Todos os direitos reservados.</footer>
</body>
</html>"""


def make_client(status: int = 200, body: str = HTML) -> httpx.Client:
    """Cliente httpx cujas respostas vêm de uma função local, sem rede."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status, text=body, headers={"Content-Type": "text/html; charset=utf-8"}
        )

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_html_de_exemplo_devolve_titulo_e_texto() -> None:
    title, text = fetch_url("https://exemplo.com/artigo", client=make_client())

    assert title == "Artigo de Exemplo"
    assert "pequenas mudanças geram grandes resultados" in text


def test_esquema_file_levanta_fetch_error() -> None:
    with pytest.raises(FetchError, match="http"):
        fetch_url("file:///etc/passwd", client=make_client())


def test_pagina_maior_que_max_bytes_levanta_fetch_error() -> None:
    with pytest.raises(FetchError, match="maior que"):
        fetch_url("https://exemplo.com/artigo", client=make_client(), max_bytes=10)


def test_resposta_404_levanta_fetch_error() -> None:
    with pytest.raises(FetchError, match="404") as info:
        fetch_url("https://exemplo.com/nao-existe", client=make_client(status=404))

    assert not isinstance(info.value, FetchBlockedError)  # link quebrado: sem fallback


def test_resposta_403_levanta_fetch_blocked_error_com_o_status() -> None:
    with pytest.raises(FetchBlockedError, match="403") as info:
        fetch_url("https://exemplo.com/bloqueado", client=make_client(status=403))

    assert info.value.status_code == 403
