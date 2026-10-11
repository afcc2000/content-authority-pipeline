"""Nós do grafo. Cada `make_x(deps)` devolve a função do nó com as dependências presas."""

from content_pipeline.nodes.analyze import make_analyze, route_after_analyze
from content_pipeline.nodes.approval import make_approval
from content_pipeline.nodes.ingest import make_ingest
from content_pipeline.nodes.interview import interview, route_after_interview
from content_pipeline.nodes.research import make_research
from content_pipeline.nodes.write_article import make_write_article

__all__ = [
    "interview",
    "make_analyze",
    "make_approval",
    "make_ingest",
    "make_research",
    "make_write_article",
    "route_after_analyze",
    "route_after_interview",
]
