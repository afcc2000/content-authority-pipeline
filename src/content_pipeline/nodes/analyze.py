"""Nó `analyze`: julga a relevância da fonte e gera o briefing com perguntas para o autor."""

from typing import Literal

from content_pipeline.deps import Deps
from content_pipeline.models import Briefing
from content_pipeline.nodes.common import ask
from content_pipeline.state import PipelineState


def source_block(state: PipelineState) -> str:
    """Monta a mensagem com a fonte delimitada por <fonte>, para o LLM tratá-la como dado."""
    title = state.get("source_title") or "(sem título)"
    return f"Título da fonte: {title}\n\n<fonte>\n{state['source_text']}\n</fonte>"


def build_analyze_request(state: PipelineState) -> str:
    """Monta o pedido do briefing: a direção do autor (se houver) e a fonte delimitada."""
    direction = state.get("author_direction")
    if not direction:
        return source_block(state)
    return f"## Direção do autor\n{direction}\n\n{source_block(state)}"


def make_analyze(deps: Deps):
    """Cria o nó `analyze`."""

    def analyze(state: PipelineState) -> dict:
        briefing = ask(deps, Briefing, ["context", "analyze"], build_analyze_request(state))
        return {"briefing": briefing}

    return analyze


def route_after_analyze(state: PipelineState) -> Literal["interview", "export_report"]:
    """Fonte relevante segue para a entrevista; irrelevante só grava o relatório e termina."""
    return "interview" if state["briefing"].is_relevant else "export_report"
