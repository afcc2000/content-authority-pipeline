"""Nós do grafo. Cada `make_x(deps)` devolve a função do nó com as dependências presas."""

from content_pipeline.nodes.analyze import make_analyze, route_after_analyze
from content_pipeline.nodes.ingest import make_ingest
from content_pipeline.nodes.interview import interview, route_after_interview
from content_pipeline.nodes.research import make_research

__all__ = [
    "interview",
    "make_analyze",
    "make_ingest",
    "make_research",
    "route_after_analyze",
    "route_after_interview",
]
