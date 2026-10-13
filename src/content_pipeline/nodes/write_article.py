"""Nó `write_article`: escreve o artigo de autoridade com o briefing, a entrevista e a fonte."""

from content_pipeline.deps import Deps
from content_pipeline.models import Article
from content_pipeline.nodes.analyze import source_block
from content_pipeline.nodes.common import ask
from content_pipeline.state import PipelineState

SKIPPED = "(o autor pulou esta pergunta)"


def build_article_request(state: PipelineState) -> str:
    """Monta a mensagem do usuário para o LLM escrever (ou reescrever) o artigo.

    Junta resumo, pontos-chave, ângulo, a entrevista em pares "P:/R:" e a fonte delimitada.
    Se houver `feedback` e um artigo anterior, acrescenta a versão anterior e o pedido de
    reescrita (usado quando o autor rejeita o artigo, no T12).
    """
    briefing = state["briefing"]
    key_points = "\n".join(f"- {point}" for point in briefing.key_points)
    interview = "\n\n".join(
        f"P: {question}\nR: {answer or SKIPPED}"
        for question, answer in zip(briefing.questions, state.get("answers") or [], strict=False)
    )

    parts = [
        f"## Resumo da fonte\n{briefing.summary}",
        f"## Pontos-chave\n{key_points}",
        f"## Ângulo sugerido\n{briefing.angle}",
        f"## Entrevista com o autor\n{interview}",
        source_block(state),
    ]

    feedback = state.get("feedback")
    previous = state.get("article")
    if feedback and previous:
        parts += [
            f"<versao_anterior>\n{previous.to_markdown()}</versao_anterior>",
            f"## Feedback do autor\n{feedback}",
            "Reescreva o artigo aplicando o feedback do autor.",
        ]
    return "\n\n".join(parts)


def make_write_article(deps: Deps):
    """Cria o nó `write_article`."""

    def write_article(state: PipelineState) -> dict:
        article = ask(deps, Article, ["context", "article_style"], build_article_request(state))
        return {"article": article}

    return write_article
