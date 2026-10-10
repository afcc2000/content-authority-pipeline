"""Testes da busca por tema (nó research e tavily_search) sem chamar API real."""

from pathlib import Path
from typing import Any

import pytest

from content_pipeline.deps import Deps
from content_pipeline.graph import build_graph
from content_pipeline.images import FakeImageGenerator
from content_pipeline.models import Briefing, SourceChoice
from content_pipeline.nodes.research import make_research
from content_pipeline.web import SearchError, make_search, tavily_search
from tests.fakes import FakeStructuredLLM, make_briefing, make_search_results, make_settings


def make_deps(tmp_path: Path, llm: FakeStructuredLLM, fetched: list[str], **overrides) -> Deps:
    def fake_fetch(url: str) -> tuple[str | None, str]:
        fetched.append(url)
        return "Título da fonte", "Texto da fonte."

    return Deps(
        llm=llm,
        images=FakeImageGenerator(),
        settings=make_settings(output_root=tmp_path / "outputs"),
        fetch=fake_fetch,
        **overrides,
    )


def test_com_topic_o_grafo_busca_e_ingest_recebe_a_url_escolhida(tmp_path: Path) -> None:
    llm = FakeStructuredLLM(
        {
            SourceChoice: [SourceChoice(url="https://exemplo.com/2", reason="Mais completa.")],
            Briefing: [make_briefing()],
        }
    )
    fetched: list[str] = []
    graph = build_graph(make_deps(tmp_path, llm, fetched, search=lambda q: make_search_results()))

    final = graph.invoke({"topic": "hábitos saudáveis"})

    assert fetched == ["https://exemplo.com/2"]
    assert final["source_url"] == "https://exemplo.com/2"
    assert len(final["search_results"]) == 2
    assert "<resultados>" in llm.calls[0][2]


def test_url_fora_dos_resultados_usa_o_primeiro_e_gera_aviso(tmp_path: Path) -> None:
    llm = FakeStructuredLLM(
        {
            SourceChoice: [SourceChoice(url="https://inventada.com", reason="?")],
            Briefing: [make_briefing()],
        }
    )
    fetched: list[str] = []
    graph = build_graph(make_deps(tmp_path, llm, fetched, search=lambda q: make_search_results()))

    final = graph.invoke({"topic": "hábitos saudáveis"})

    assert fetched == ["https://exemplo.com/1"]
    assert any("inventada.com" in aviso for aviso in final["warnings"])


def test_topic_sem_search_levanta_erro_mencionando_a_chave(tmp_path: Path) -> None:
    deps = make_deps(tmp_path, FakeStructuredLLM({}), [])

    with pytest.raises(ValueError, match="TAVILY_API_KEY"):
        make_research(deps)({"topic": "qualquer"})


class FakeTavilyClient:
    def __init__(self, response: dict[str, Any] | Exception) -> None:
        self.response = response

    def search(self, query: str, **kwargs: Any) -> dict[str, Any]:
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def test_tavily_search_converte_resultados() -> None:
    client = FakeTavilyClient(
        {"results": [{"url": "https://a.com", "title": "A", "content": "Trecho A", "score": 0.9}]}
    )

    [result] = tavily_search("tema", client=client)

    assert (result.url, result.title, result.snippet) == ("https://a.com", "A", "Trecho A")


def test_tavily_search_traduz_erro_para_search_error() -> None:
    with pytest.raises(SearchError):
        tavily_search("tema", client=FakeTavilyClient(RuntimeError("limite de uso")))


def test_make_search_sem_chave_devolve_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    assert make_search(make_settings()) is None
