"""Testes dos nós e do grafo com fakes (sem chamar API real)."""

from pathlib import Path

import pytest

from content_pipeline.deps import Deps
from content_pipeline.graph import build_graph
from content_pipeline.images import FakeImageGenerator
from content_pipeline.models import Briefing
from content_pipeline.nodes.ingest import make_ingest, slugify
from tests.fakes import FakeStructuredLLM, make_briefing, make_settings


def make_deps(tmp_path: Path, llm: FakeStructuredLLM | None = None, **overrides) -> Deps:
    return Deps(
        llm=llm or FakeStructuredLLM({}),
        images=FakeImageGenerator(),
        settings=make_settings(output_root=tmp_path / "outputs"),
        **overrides,
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Olá, Mundo!", "ola-mundo"),
        ("  Ação & Reação: 2026  ", "acao-reacao-2026"),
        ("!!!", "conteudo"),
    ],
)
def test_slugify(text: str, expected: str) -> None:
    assert slugify(text) == expected


def test_ingest_a_partir_de_texto(tmp_path: Path) -> None:
    result = make_ingest(make_deps(tmp_path))({"source_text": "Texto da fonte."})

    assert result["source_text"] == "Texto da fonte."
    assert result["answers"] == [] and result["rewrites"] == 0
    assert result["output_dir"].endswith("-conteudo")


def test_ingest_a_partir_de_arquivo(tmp_path: Path) -> None:
    arquivo = tmp_path / "entrada.md"
    arquivo.write_text("# Meu Título\n\nCorpo do texto.", encoding="utf-8")

    result = make_ingest(make_deps(tmp_path))({"source_path": str(arquivo)})

    assert "Corpo do texto." in result["source_text"]
    assert result["source_title"] == "Meu Título"
    assert result["output_dir"].endswith("-meu-titulo")


def test_ingest_a_partir_de_url_usa_fetch_de_deps(tmp_path: Path) -> None:
    urls: list[str] = []

    def fake_fetch(url: str) -> tuple[str | None, str]:
        urls.append(url)
        return "Título Web", "Texto baixado."

    deps = make_deps(tmp_path, fetch=fake_fetch)
    result = make_ingest(deps)({"source_url": "https://exemplo.com/post"})

    assert result["source_text"] == "Texto baixado."
    assert result["source_title"] == "Título Web"
    assert urls == ["https://exemplo.com/post"]


def test_ingest_sem_fonte_levanta_value_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        make_ingest(make_deps(tmp_path))({})


def test_grafo_devolve_briefing_e_envia_fonte_delimitada(tmp_path: Path) -> None:
    briefing = make_briefing()
    llm = FakeStructuredLLM({Briefing: [briefing]})
    graph = build_graph(make_deps(tmp_path, llm=llm))

    final = graph.invoke({"source_text": "Texto da fonte."})

    assert final["briefing"] is briefing
    schema, _system, user = llm.calls[0]
    assert schema is Briefing
    assert "<fonte>" in user and "Texto da fonte." in user
