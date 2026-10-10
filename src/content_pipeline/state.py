"""Estado compartilhado pelos nós do grafo."""

from typing import Literal, TypedDict

from content_pipeline.models import Article, Briefing, CarouselPlan, SearchResult


class PipelineState(TypedDict, total=False):
    """Estado do pipeline.

    `total=False` torna todas as chaves opcionais: cada nó lê o que precisa e devolve
    só as chaves que alterou, e o LangGraph junta essas atualizações ao estado.
    """

    topic: str
    search_results: list[SearchResult]
    source_url: str
    source_path: str
    source_text: str
    source_title: str | None
    briefing: Briefing
    answers: list[str]
    article: Article
    decision: Literal["accept", "edit", "reject"]
    feedback: str | None
    rewrites: int
    carousel: CarouselPlan
    validation_errors: list[str]
    carousel_attempts: int
    images: list[str]
    warnings: list[str]
    output_dir: str
