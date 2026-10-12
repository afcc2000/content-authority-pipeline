"""Montagem do grafo do pipeline."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph

from content_pipeline.carousel.subgraph import build_carousel_subgraph
from content_pipeline.deps import Deps
from content_pipeline.models import Article, Briefing, CarouselPlan, SearchResult, Slide
from content_pipeline.nodes import (
    interview,
    make_analyze,
    make_approval,
    make_ingest,
    make_research,
    make_write_article,
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
    """Monta e compila o grafo do pipeline.

    START -> [research] -> ingest -> analyze -> [interview]* -> write_article <-> approval
    -> design_carousel (subgrafo) -> END.

    Args:
        deps: Dependências injetadas nos nós (LLM, imagens, settings, fetch, search).
        checkpointer: Onde salvar o estado entre passos; obrigatório a partir do `interrupt`.
    """
    builder = StateGraph(PipelineState)
    builder.add_node("research", make_research(deps))
    builder.add_node("ingest", make_ingest(deps))
    builder.add_node("analyze", make_analyze(deps))
    builder.add_node("interview", interview)
    builder.add_node("write_article", make_write_article(deps))
    builder.add_node("approval", make_approval(deps))
    builder.add_node("design_carousel", build_carousel_subgraph(deps))

    builder.add_conditional_edges(START, route_start, ["research", "ingest"])
    builder.add_edge("research", "ingest")
    builder.add_edge("ingest", "analyze")
    builder.add_conditional_edges("analyze", route_after_analyze)
    builder.add_conditional_edges("interview", route_after_interview)
    builder.add_edge("write_article", "approval")  # approval roteia sozinho via Command
    builder.add_edge("design_carousel", END)
    return builder.compile(checkpointer=checkpointer)
