"""Montagem do grafo do pipeline."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import START, StateGraph

from content_pipeline.deps import Deps
from content_pipeline.models import Article, Briefing, CarouselPlan, SearchResult, Slide
from content_pipeline.nodes import (
    interview,
    make_analyze,
    make_ingest,
    make_research,
    route_after_analyze,
    route_after_interview,
)
from content_pipeline.state import PipelineState


def route_start(state: PipelineState) -> str:
    """Com `topic`, começa pela busca; senão, direto pela ingestão."""
    return "research" if state.get("topic") else "ingest"


def make_checkpointer() -> InMemorySaver:
    """Checkpointer em memória com os modelos do pipeline registrados no serializador.

    Sem o registro, o LangGraph avisa que vai bloquear a desserialização desses tipos; com a
    lista explícita e um tipo de fora (ex.: `SearchResult`), ele volta como `dict`.
    """
    serde = JsonPlusSerializer(
        allowed_msgpack_modules=[Briefing, Article, Slide, CarouselPlan, SearchResult]
    )
    return InMemorySaver(serde=serde)


def build_graph(deps: Deps, checkpointer=None):
    """Monta e compila o grafo: START -> [research] -> ingest -> analyze -> [interview]* -> END.

    Args:
        deps: Dependências injetadas nos nós (LLM, imagens, settings, fetch, search).
        checkpointer: Onde salvar o estado entre passos; obrigatório a partir do `interrupt`.
    """
    builder = StateGraph(PipelineState)
    builder.add_node("research", make_research(deps))
    builder.add_node("ingest", make_ingest(deps))
    builder.add_node("analyze", make_analyze(deps))
    builder.add_node("interview", interview)

    builder.add_conditional_edges(START, route_start, ["research", "ingest"])
    builder.add_edge("research", "ingest")
    builder.add_edge("ingest", "analyze")
    builder.add_conditional_edges("analyze", route_after_analyze)
    builder.add_conditional_edges("interview", route_after_interview)
    return builder.compile(checkpointer=checkpointer)
