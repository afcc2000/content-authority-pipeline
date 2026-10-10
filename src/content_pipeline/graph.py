"""Montagem do grafo do pipeline."""

from langgraph.graph import END, START, StateGraph

from content_pipeline.deps import Deps
from content_pipeline.nodes import make_analyze, make_ingest
from content_pipeline.state import PipelineState


def build_graph(deps: Deps, checkpointer=None):
    """Monta e compila o grafo: START -> ingest -> analyze -> END (por enquanto).

    Args:
        deps: Dependências injetadas nos nós (LLM, imagens, settings, fetch).
        checkpointer: Onde salvar o estado entre passos; obrigatório a partir do `interrupt`.
    """
    builder = StateGraph(PipelineState)
    builder.add_node("ingest", make_ingest(deps))
    builder.add_node("analyze", make_analyze(deps))

    builder.add_edge(START, "ingest")
    builder.add_edge("ingest", "analyze")
    builder.add_edge("analyze", END)
    return builder.compile(checkpointer=checkpointer)
