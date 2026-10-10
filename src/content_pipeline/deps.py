"""Dependências injetadas no grafo: o que muda entre testes (fakes) e execução real."""

from collections.abc import Callable
from dataclasses import dataclass, field

from content_pipeline.config import Settings
from content_pipeline.fetcher import fetch_url
from content_pipeline.images import ImageGenerator
from content_pipeline.llm import StructuredLLM
from content_pipeline.web import Search


@dataclass
class Deps:
    """Tudo de que os nós precisam além do estado.

    Os testes passam `FakeStructuredLLM`, `FakeImageGenerator` e um `fetch` falso;
    a CLI passa as implementações reais.
    """

    llm: StructuredLLM
    images: ImageGenerator
    settings: Settings = field(default_factory=Settings)
    fetch: Callable[[str], tuple[str | None, str]] = fetch_url
    search: Search | None = None  # busca por tema; None sem TAVILY_API_KEY
