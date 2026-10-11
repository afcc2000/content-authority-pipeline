"""Nó `analyze`: julga a relevância da fonte e gera o briefing com perguntas para o autor."""

from typing import Literal

from langgraph.graph import END

from content_pipeline.deps import Deps
from content_pipeline.models import Briefing
from content_pipeline.prompts import compose
from content_pipeline.state import PipelineState


def source_block(state: PipelineState) -> str:
    """Monta a mensagem com a fonte delimitada por <fonte>, para o LLM tratá-la como dado."""
    title = state.get("source_title") or "(sem título)"
    return f"Título da fonte: {title}\n\n<fonte>\n{state['source_text']}\n</fonte>"


def make_analyze(deps: Deps):
    """Cria o nó `analyze`."""

    def analyze(state: PipelineState) -> dict:
        system = compose(deps.settings.prompts_dir, "context", "analyze")
        briefing = deps.llm.generate(Briefing, system, source_block(state))
        return {"briefing": briefing}

    return analyze


def route_after_analyze(state: PipelineState) -> Literal["interview", "__end__"]:
    """Fonte irrelevante termina o pipeline aqui; relevante segue para a entrevista."""
    return "interview" if state["briefing"].is_relevant else END
