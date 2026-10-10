"""Dublês de teste e fábricas de dados de exemplo (nenhum chama API real)."""

from pathlib import Path
from typing import Any

from content_pipeline.config import Settings
from content_pipeline.models import Article, Briefing, CarouselPlan, Slide

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


class FakeStructuredLLM:
    """Devolve objetos Pydantic pré-definidos, por schema, na ordem das chamadas."""

    def __init__(self, responses: dict[type, list]) -> None:
        self.responses = {schema: list(items) for schema, items in responses.items()}
        self.calls: list[tuple[type, str, str]] = []

    def generate(self, schema: type, system: str, user: str) -> Any:
        self.calls.append((schema, system, user))
        return self.responses[schema].pop(0)


def make_settings(**overrides: Any) -> Settings:
    """Settings que ignora o `.env` local e usa a pasta de prompts do repositório."""
    values: dict[str, Any] = {"prompts_dir": PROMPTS_DIR, **overrides}
    return Settings(_env_file=None, **values)


def make_briefing(relevant: bool = True) -> Briefing:
    return Briefing(
        is_relevant=relevant,
        relevance_reason="Tema dentro do contexto do autor." if relevant else "Fora do tema.",
        summary="Resumo do conteúdo de referência.",
        key_points=["Ponto 1", "Ponto 2"],
        angle="A experiência prática do autor com o tema.",
        questions=["Qual é a sua experiência com isso?", "Que exemplo você daria?"],
    )


def make_article(title: str = "Título do artigo") -> Article:
    return Article(
        title=title,
        subtitle="Subtítulo do artigo",
        body_markdown="## Seção 1\n\nTexto.\n\n## Seção 2\n\nTexto.\n\n## Seção 3\n\nTexto.",
        tags=["teste"],
    )


def make_carousel(
    n_slides: int = 5, cta: str = "Quer se aprofundar? O artigo completo está no blog."
) -> CarouselPlan:
    return CarouselPlan(
        slides=[
            Slide(index=i, headline=f"Headline {i}", image_prompt=f"Imagem do slide {i}")
            for i in range(1, n_slides + 1)
        ],
        caption="Legenda do carrossel.",
        hashtags=["#teste"],
        cta_text=cta,
    )
