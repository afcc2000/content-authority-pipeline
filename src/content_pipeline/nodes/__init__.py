"""Nós do grafo. Cada `make_x(deps)` devolve a função do nó com as dependências presas."""

from content_pipeline.nodes.analyze import make_analyze
from content_pipeline.nodes.ingest import make_ingest

__all__ = ["make_analyze", "make_ingest"]
