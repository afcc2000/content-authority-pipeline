"""Testes dos nós e do grafo com fakes (sem chamar API real)."""

from pathlib import Path

import pytest
from langgraph.types import Command

from content_pipeline.deps import Deps
from content_pipeline.graph import build_graph, make_checkpointer
from content_pipeline.images import FakeImageGenerator
from content_pipeline.models import Article, Briefing, SearchResult, SourceChoice
from content_pipeline.nodes.ingest import make_ingest, slugify
from content_pipeline.nodes.write_article import build_article_request
from tests.fakes import (
    FakeStructuredLLM,
    make_article,
    make_briefing,
    make_search_results,
    make_settings,
)


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
    # Irrelevante para o grafo terminar no analyze (relevante pausaria na entrevista).
    briefing = make_briefing(relevant=False)
    llm = FakeStructuredLLM({Briefing: [briefing]})
    graph = build_graph(make_deps(tmp_path, llm=llm))

    final = graph.invoke({"source_text": "Texto da fonte."})

    assert final["briefing"] is briefing
    schema, _system, user = llm.calls[0]
    assert schema is Briefing
    assert "<fonte>" in user and "Texto da fonte." in user


def config(thread_id: str = "t1") -> dict:
    return {"configurable": {"thread_id": thread_id}}


def test_fonte_irrelevante_termina_sem_interrupt(tmp_path: Path) -> None:
    llm = FakeStructuredLLM({Briefing: [make_briefing(relevant=False)]})
    graph = build_graph(make_deps(tmp_path, llm=llm), checkpointer=make_checkpointer())

    final = graph.invoke({"source_text": "Texto da fonte."}, config())

    assert "__interrupt__" not in final
    assert final["answers"] == []


def test_fonte_relevante_pausa_uma_vez_por_pergunta(tmp_path: Path) -> None:
    llm = FakeStructuredLLM({Briefing: [make_briefing()], Article: [make_article()]})  # 2 perguntas
    graph = build_graph(make_deps(tmp_path, llm=llm), checkpointer=make_checkpointer())

    primeira = graph.invoke({"source_text": "Texto da fonte."}, config())
    segunda = graph.invoke(Command(resume="contribuição 1"), config())
    final = graph.invoke(Command(resume=""), config())

    payloads = [primeira["__interrupt__"][0].value, segunda["__interrupt__"][0].value]
    assert [p["index"] for p in payloads] == [1, 2]
    assert "__interrupt__" not in final
    assert final["answers"] == ["contribuição 1", ""]


def test_payload_do_interrupt_tem_os_campos_do_contrato(tmp_path: Path) -> None:
    briefing = make_briefing()
    llm = FakeStructuredLLM({Briefing: [briefing]})
    graph = build_graph(make_deps(tmp_path, llm=llm), checkpointer=make_checkpointer())

    result = graph.invoke({"source_text": "Texto da fonte."}, config())

    assert result["__interrupt__"][0].value == {
        "type": "question",
        "index": 1,
        "total": 2,
        "question": briefing.questions[0],
    }


def test_checkpointer_preserva_search_result_entre_pausas(tmp_path: Path) -> None:
    llm = FakeStructuredLLM(
        {
            SourceChoice: [SourceChoice(url="https://exemplo.com/1", reason="Completa.")],
            Briefing: [make_briefing()],
        }
    )
    deps = make_deps(
        tmp_path,
        llm=llm,
        search=lambda q: make_search_results(),
        fetch=lambda url: ("Título", "Texto."),
    )
    graph = build_graph(deps, checkpointer=make_checkpointer())

    graph.invoke({"topic": "tema"}, config())
    estado = graph.get_state(config()).values

    assert all(isinstance(r, SearchResult) for r in estado["search_results"])


def run_interview(tmp_path: Path, answers: list[str]) -> tuple[FakeStructuredLLM, dict]:
    """Roda o grafo com fonte relevante, respondendo a entrevista com `answers`."""
    llm = FakeStructuredLLM({Briefing: [make_briefing()], Article: [make_article()]})
    graph = build_graph(make_deps(tmp_path, llm=llm), checkpointer=make_checkpointer())
    graph.invoke({"source_text": "Texto da fonte."}, config())
    final: dict = {}
    for answer in answers:
        final = graph.invoke(Command(resume=answer), config())
    return llm, final


def test_resposta_da_entrevista_vai_para_o_prompt_do_artigo(tmp_path: Path) -> None:
    llm, _final = run_interview(tmp_path, ["Atendo há 10 anos.", "Um caso real."])

    schema, _system, user = llm.calls[1]
    assert schema is Article
    assert "R: Atendo há 10 anos." in user
    assert "<fonte>" in user


def test_pergunta_pulada_aparece_marcada_no_prompt(tmp_path: Path) -> None:
    llm, _final = run_interview(tmp_path, ["Atendo há 10 anos.", ""])

    assert "R: (o autor pulou esta pergunta)" in llm.calls[1][2]


def test_estado_final_tem_o_artigo(tmp_path: Path) -> None:
    _llm, final = run_interview(tmp_path, ["a", "b"])

    assert isinstance(final["article"], Article)
    assert "__interrupt__" not in final


def test_pedido_de_reescrita_inclui_versao_anterior_e_feedback() -> None:
    state = {
        "briefing": make_briefing(),
        "answers": ["a", "b"],
        "source_text": "Texto.",
        "article": make_article("Versão 1"),
        "feedback": "Mais exemplos práticos.",
    }

    request = build_article_request(state)

    assert "<versao_anterior>\n# Versão 1" in request
    assert "Mais exemplos práticos." in request
    assert "Reescreva" in request


def test_pedido_sem_feedback_nao_tem_reescrita() -> None:
    state = {"briefing": make_briefing(), "answers": ["a", "b"], "source_text": "Texto."}

    assert "<versao_anterior>" not in build_article_request(state)
