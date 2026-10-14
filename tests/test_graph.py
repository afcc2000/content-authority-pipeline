"""Testes dos nós e do grafo com fakes (sem chamar API real)."""

from pathlib import Path

import pytest
from langgraph.types import Command

from content_pipeline.deps import Deps
from content_pipeline.graph import build_graph, make_checkpointer
from content_pipeline.images import FakeImageGenerator
from content_pipeline.models import Article, Briefing, CarouselPlan, SearchResult, SourceChoice
from content_pipeline.nodes.approval import article_from_markdown
from content_pipeline.nodes.direction import DIRECTION_QUESTION
from content_pipeline.nodes.ingest import make_ingest, slugify
from content_pipeline.nodes.write_article import build_article_request
from tests.fakes import (
    FakeStructuredLLM,
    make_article,
    make_briefing,
    make_carousel,
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

    # Direção já no estado: o grafo não pausa (sem checkpointer, uma pausa daria erro).
    final = graph.invoke({"source_text": "Texto da fonte.", "author_direction": ""})

    assert final["briefing"] is briefing
    schema, _system, user = llm.calls[0]
    assert schema is Briefing
    assert "<fonte>" in user and "Texto da fonte." in user


def config(thread_id: str = "t1") -> dict:
    return {"configurable": {"thread_id": thread_id}}


def test_fonte_irrelevante_termina_depois_da_direcao(tmp_path: Path) -> None:
    llm = FakeStructuredLLM({Briefing: [make_briefing(relevant=False)]})
    graph = build_graph(make_deps(tmp_path, llm=llm), checkpointer=make_checkpointer())

    graph.invoke({"source_text": "Texto da fonte."}, config())  # pausa na direção
    final = graph.invoke(Command(resume=""), config())

    assert "__interrupt__" not in final
    assert final["answers"] == []


def test_direcao_e_a_primeira_pausa_antes_do_analyze(tmp_path: Path) -> None:
    llm = FakeStructuredLLM({Briefing: [make_briefing()]})
    graph = build_graph(make_deps(tmp_path, llm=llm), checkpointer=make_checkpointer())
    arquivo = tmp_path / "fonte.md"
    arquivo.write_text("# Título X\n\nTexto da fonte.", encoding="utf-8")

    result = graph.invoke({"source_path": str(arquivo)}, config())

    assert result["__interrupt__"][0].value == {
        "type": "direction",
        "question": DIRECTION_QUESTION,
        "source_title": "Título X",
    }
    assert llm.calls == []  # o briefing (e as perguntas) ainda não foi gerado


def test_direcao_ja_no_estado_nao_pausa(tmp_path: Path) -> None:
    llm = FakeStructuredLLM({Briefing: [make_briefing()]})
    graph = build_graph(make_deps(tmp_path, llm=llm), checkpointer=make_checkpointer())

    result = graph.invoke({"source_text": "Texto.", "author_direction": "Seja direto."}, config())

    assert result["__interrupt__"][0].value["type"] == "question"


def test_fonte_relevante_pausa_uma_vez_por_pergunta(tmp_path: Path) -> None:
    llm = FakeStructuredLLM({Briefing: [make_briefing()], Article: [make_article()]})  # 2 perguntas
    graph = build_graph(make_deps(tmp_path, llm=llm), checkpointer=make_checkpointer())

    direcao = graph.invoke({"source_text": "Texto da fonte."}, config())
    primeira = graph.invoke(Command(resume="Enfatize o lado prático."), config())
    segunda = graph.invoke(Command(resume="contribuição 1"), config())
    final = graph.invoke(Command(resume=""), config())

    assert direcao["__interrupt__"][0].value["type"] == "direction"
    payloads = [r["__interrupt__"][0].value for r in (primeira, segunda)]
    assert [p["index"] for p in payloads] == [1, 2]
    assert {p["total"] for p in payloads} == {2}  # só as do briefing
    assert final["__interrupt__"][0].value["type"] == "approval"  # a entrevista acabou
    assert final["answers"] == ["contribuição 1", ""]
    assert final["author_direction"] == "Enfatize o lado prático."


def test_payload_do_interrupt_tem_os_campos_do_contrato(tmp_path: Path) -> None:
    briefing = make_briefing()
    llm = FakeStructuredLLM({Briefing: [briefing]})
    graph = build_graph(make_deps(tmp_path, llm=llm), checkpointer=make_checkpointer())

    graph.invoke({"source_text": "Texto da fonte."}, config())
    result = graph.invoke(Command(resume=""), config())  # pula a direção

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


def run_interview(
    tmp_path: Path,
    answers: list[str],
    articles: list[Article] | None = None,
    carousels: list[CarouselPlan] | None = None,
    images: FakeImageGenerator | None = None,
    direction: str = "",
    **settings_overrides,
):
    """Roda o grafo com fonte relevante até a 1ª aprovação, respondendo a entrevista.

    Responde primeiro a pergunta de direção com `direction` ("" = pulou) e, depois, `answers`.

    Returns:
        (llm falso, grafo compilado, resultado do último `invoke`).
    """
    llm = FakeStructuredLLM(
        {
            Briefing: [make_briefing()],
            Article: articles or [make_article()],
            CarouselPlan: carousels or [make_carousel()],
        }
    )
    deps = make_deps(tmp_path, llm=llm)
    deps.settings = make_settings(output_root=tmp_path / "outputs", **settings_overrides)
    if images is not None:
        deps.images = images
    graph = build_graph(deps, checkpointer=make_checkpointer())
    graph.invoke({"source_text": "Texto da fonte."}, config())
    final: dict = {}
    for answer in [direction, *answers]:
        final = graph.invoke(Command(resume=answer), config())
    return llm, graph, final


def test_direcao_do_autor_vai_para_o_pedido_do_analyze(tmp_path: Path) -> None:
    llm, _graph, _final = run_interview(tmp_path, ["a", "b"], direction="Defenda a tese X.")

    schema, _system, user = llm.calls[0]
    assert schema is Briefing
    assert "## Direção do autor\nDefenda a tese X." in user
    assert user.index("Direção do autor") < user.index("<fonte>")


def test_direcao_do_autor_vai_para_o_pedido_com_prioridade(tmp_path: Path) -> None:
    llm, _graph, _final = run_interview(tmp_path, ["a", "b"], direction="Defenda a tese X.")

    _schema, _system, user = llm.calls[1]
    assert "## Direção do autor (prioridade)\nDefenda a tese X." in user
    assert "prevalece sobre o ângulo sugerido" in user
    assert user.index("Direção do autor") < user.index("<fonte>")  # antes da fonte


def test_direcao_pulada_nao_cria_a_secao(tmp_path: Path) -> None:
    llm, graph, _final = run_interview(tmp_path, ["a", "b"])

    assert "Direção do autor" not in llm.calls[0][2]  # analyze
    _schema, _system, user = llm.calls[1]
    assert "Direção do autor" not in user
    assert graph.get_state(config()).values["author_direction"] == ""


def test_reescrita_mantem_a_direcao_do_autor(tmp_path: Path) -> None:
    llm, graph, _ = run_interview(
        tmp_path, ["a", "b"], articles=[make_article(), make_article()], direction="Seja direto."
    )

    graph.invoke(Command(resume={"action": "reject", "feedback": "Mais curto."}), config())

    _schema, _system, user = llm.calls[2]  # 2ª escrita do artigo
    assert "Seja direto." in user and "Mais curto." in user


def test_resposta_da_entrevista_vai_para_o_prompt_do_artigo(tmp_path: Path) -> None:
    llm, _graph, _final = run_interview(tmp_path, ["Atendo há 10 anos.", "Um caso real."])

    schema, _system, user = llm.calls[1]
    assert schema is Article
    assert "R: Atendo há 10 anos." in user
    assert "<fonte>" in user


def test_pergunta_pulada_aparece_marcada_no_prompt(tmp_path: Path) -> None:
    llm, _graph, _final = run_interview(tmp_path, ["Atendo há 10 anos.", ""])

    assert "R: (o autor pulou esta pergunta)" in llm.calls[1][2]


def test_estado_final_tem_o_artigo(tmp_path: Path) -> None:
    _llm, _graph, final = run_interview(tmp_path, ["a", "b"])

    assert isinstance(final["article"], Article)
    assert final["__interrupt__"][0].value["type"] == "approval"


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


def test_accept_termina_com_decisao_accept(tmp_path: Path) -> None:
    _llm, graph, _ = run_interview(tmp_path, ["a", "b"])

    final = graph.invoke(Command(resume="accept"), config())

    assert final["decision"] == "accept"
    assert "__interrupt__" not in final


def test_accept_gera_o_carrossel_com_uma_imagem_por_slide(tmp_path: Path) -> None:
    images = FakeImageGenerator()
    _llm, graph, _ = run_interview(tmp_path, ["a", "b"], images=images)

    final = graph.invoke(Command(resume="accept"), config())

    assert len(images.calls) == 5
    assert len(final["images"]) == 5
    assert final["images"][0].endswith("slide_01.prompt.txt")
    assert final["validation_errors"] == []


def test_payload_da_aprovacao(tmp_path: Path) -> None:
    _llm, _graph, final = run_interview(tmp_path, ["a", "b"])

    payload = final["__interrupt__"][0].value
    assert payload["type"] == "approval"
    assert payload["article_markdown"].startswith("# Título do artigo")
    assert (payload["rewrites"], payload["can_reject"]) == (0, True)


def test_edit_converte_o_markdown_editado_em_article(tmp_path: Path) -> None:
    _llm, graph, _ = run_interview(tmp_path, ["a", "b"])
    editado = "# Título editado\n\n*Novo subtítulo*\n\nCorpo editado."

    final = graph.invoke(Command(resume={"action": "edit", "article_markdown": editado}), config())

    article = final["article"]
    assert final["decision"] == "edit"
    assert (article.title, article.subtitle, article.body_markdown) == (
        "Título editado",
        "Novo subtítulo",
        "Corpo editado.",
    )


def test_reject_reescreve_com_feedback_e_versao_anterior(tmp_path: Path) -> None:
    llm, graph, _ = run_interview(
        tmp_path, ["a", "b"], articles=[make_article("Versão 1"), make_article("Versão 2")]
    )

    final = graph.invoke(
        Command(resume={"action": "reject", "feedback": "Mais exemplos práticos."}), config()
    )

    segundo_pedido = llm.calls[2][2]  # calls: analyze, artigo V1, artigo V2
    assert "Mais exemplos práticos." in segundo_pedido
    assert "# Versão 1" in segundo_pedido
    assert final["rewrites"] == 1
    assert final["__interrupt__"][0].value["article_markdown"].startswith("# Versão 2")


def test_reject_no_limite_termina_com_aviso(tmp_path: Path) -> None:
    _llm, graph, first = run_interview(tmp_path, ["a", "b"], max_rewrites=0)
    assert first["__interrupt__"][0].value["can_reject"] is False

    final = graph.invoke(Command(resume={"action": "reject", "feedback": "Não gostei."}), config())

    assert "__interrupt__" not in final
    assert any("limite" in aviso for aviso in final["warnings"])


@pytest.mark.parametrize(
    "resposta",
    [{"action": "edit"}, {"action": "reject", "feedback": "  "}, {"action": "publicar"}],
)
def test_resposta_invalida_levanta_value_error(tmp_path: Path, resposta: dict) -> None:
    _llm, graph, _ = run_interview(tmp_path, ["a", "b"])

    with pytest.raises(ValueError):
        graph.invoke(Command(resume=resposta), config())


def test_article_from_markdown_sem_titulo_mantem_o_do_fallback() -> None:
    fallback = make_article("Título original")

    article = article_from_markdown("Só o corpo novo.", fallback)

    assert article.title == "Título original"
    assert article.body_markdown == "Só o corpo novo."
    assert article.tags == fallback.tags


def test_article_from_markdown_sem_subtitulo_e_negrito_nao_vira_subtitulo() -> None:
    article = article_from_markdown("# T\n\n**Negrito** no corpo.", make_article())

    assert article.subtitle is None
    assert article.body_markdown == "**Negrito** no corpo."
