"""Testes da exportação (arquivos finais e relatório) sem chamar API real."""

import json
from pathlib import Path

from langgraph.types import Command

from content_pipeline.export import build_report
from content_pipeline.graph import build_graph, make_checkpointer
from content_pipeline.models import Briefing
from tests.fakes import FakeStructuredLLM, make_article, make_briefing, make_carousel
from tests.test_graph import config, make_deps, run_interview

ARQUIVOS = ["article.md", "slides.json", "caption.txt", "report.md"]


def run_until_accept(tmp_path: Path) -> Path:
    """Roda o pipeline até o fim com `accept` e devolve a pasta de saída."""
    _llm, graph, _ = run_interview(tmp_path, ["Minha experiência.", ""])
    final = graph.invoke(Command(resume="accept"), config())
    return Path(final["output_dir"])


def test_accept_grava_os_4_arquivos(tmp_path: Path) -> None:
    out = run_until_accept(tmp_path)

    assert sorted(p.name for p in out.iterdir() if p.is_file()) == sorted(ARQUIVOS)


def test_article_md_comeca_com_o_titulo(tmp_path: Path) -> None:
    out = run_until_accept(tmp_path)

    assert (out / "article.md").read_text(encoding="utf-8").startswith("# Título do artigo")


def test_slides_json_tem_5_slides_e_caption_tem_hashtag(tmp_path: Path) -> None:
    out = run_until_accept(tmp_path)

    slides = json.loads((out / "slides.json").read_text(encoding="utf-8"))
    caption = (out / "caption.txt").read_text(encoding="utf-8")
    assert len(slides["slides"]) == 5
    assert caption == "Legenda do carrossel.\n\n#teste\n"


def test_fonte_irrelevante_nao_cria_article_md(tmp_path: Path) -> None:
    llm = FakeStructuredLLM({Briefing: [make_briefing(relevant=False)]})
    graph = build_graph(make_deps(tmp_path, llm=llm), checkpointer=make_checkpointer())

    graph.invoke({"source_text": "Texto da fonte."}, config())

    assert list(tmp_path.rglob("article.md")) == []


def arquivos(out: Path) -> list[str]:
    return sorted(p.name for p in out.iterdir() if p.is_file())


def test_fonte_irrelevante_grava_so_o_relatorio_com_o_motivo(tmp_path: Path) -> None:
    briefing = make_briefing(relevant=False)
    llm = FakeStructuredLLM({Briefing: [briefing]})
    graph = build_graph(make_deps(tmp_path, llm=llm), checkpointer=make_checkpointer())

    final = graph.invoke({"source_text": "Texto da fonte.", "author_direction": ""}, config())

    out = Path(final["output_dir"])
    report = (out / "report.md").read_text(encoding="utf-8")
    assert arquivos(out) == ["report.md"]
    assert f"- **Relevante:** não. {briefing.relevance_reason}" in report
    assert "## Entrevista" not in report  # não houve entrevista


def test_reject_no_limite_grava_so_o_relatorio_com_feedback_e_aviso(tmp_path: Path) -> None:
    _llm, graph, _ = run_interview(tmp_path, ["a", "b"], max_rewrites=0)

    final = graph.invoke(Command(resume={"action": "reject", "feedback": "Não gostei."}), config())

    out = Path(final["output_dir"])
    report = (out / "report.md").read_text(encoding="utf-8")
    assert arquivos(out) == ["report.md"]
    assert "- **Último feedback do autor:** Não gostei." in report
    assert "Artigo rejeitado após o limite de 0 reescrita(s)." in report


def test_relatorio_tem_entrevista_e_avisos() -> None:
    state = {
        "source_url": "https://exemplo.com/post",
        "source_title": "Post de exemplo",
        "briefing": make_briefing(),
        "answers": ["Minha experiência.", ""],
        "decision": "edit",
        "rewrites": 1,
        "carousel_attempts": 2,
        "article": make_article(),
        "carousel": make_carousel(),
        "warnings": ["Carrossel seguiu com erros."],
    }

    report = build_report(state)

    assert report.startswith("# Relatório da execução")
    assert "- **Fonte:** https://exemplo.com/post" in report
    assert "- **Decisão sobre o artigo:** edit" in report
    assert "**Qual é a sua experiência com isso?**\n\nMinha experiência." in report
    assert "**Que exemplo você daria?**\n\n(pulou)" in report
    assert "## Avisos\n\n- Carrossel seguiu com erros." in report


def test_relatorio_mostra_a_direcao_do_autor_so_quando_houver() -> None:
    state = {"briefing": make_briefing(), "answers": ["a", "b"], "source_text": "Texto."}

    com = build_report({**state, "author_direction": "Defenda a tese X."})
    sem = build_report({**state, "author_direction": ""})

    assert "## Direção do autor\n\nDefenda a tese X." in com
    assert "Direção do autor" not in sem


def test_relatorio_sem_avisos_nao_tem_a_secao() -> None:
    state = {"briefing": make_briefing(), "answers": ["a", "b"], "source_text": "Texto."}

    report = build_report(state)

    assert "## Avisos" not in report
    assert "(texto informado diretamente)" in report
