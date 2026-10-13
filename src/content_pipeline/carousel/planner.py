"""Planejamento do carrossel: o LLM transforma o artigo aprovado em slides e legenda."""

from content_pipeline.deps import Deps
from content_pipeline.models import CarouselPlan
from content_pipeline.nodes.common import ask
from content_pipeline.state import PipelineState


def build_carousel_request(state: PipelineState, deps: Deps) -> str:
    """Monta a mensagem do usuário: limites (de `settings`), o artigo e, se houver, os erros.

    Os limites vêm de `settings` para o LLM receber os mesmos números que os validadores
    vão conferir depois.
    """
    s = deps.settings
    limits = [
        "## Limites",
        f"- Entre {s.min_slides} e {s.max_slides} slides, com `index` 1, 2, 3... em ordem.",
        f"- Headline com no máximo {s.headline_max_chars} caracteres.",
        f"- Legenda com no máximo {s.caption_max_chars} caracteres, sem hashtags.",
        f"- No máximo {s.max_hashtags} hashtags.",
        "- `cta_text` obrigatório.",
    ]
    if s.blog_url:
        limits.append(f"- A legenda deve conter o link do blog: {s.blog_url}")
    parts = [
        "Crie o carrossel de Instagram para o artigo abaixo.",
        "\n".join(limits),
        f"<artigo>\n{state['article'].to_markdown()}</artigo>",
    ]

    errors = state.get("validation_errors")
    if errors:
        listed = "\n".join(f"- {error}" for error in errors)
        parts.append(
            "A versão anterior foi reprovada pela validação automática. "
            f"Corrija estes erros:\n{listed}"
        )
    return "\n\n".join(parts)


def make_plan_slides(deps: Deps):
    """Cria o nó `plan_slides`."""

    def plan_slides(state: PipelineState) -> dict:
        carousel = ask(
            deps,
            CarouselPlan,
            ["context", "carousel_brand", "carousel_rules"],
            build_carousel_request(state, deps),
        )
        return {"carousel": carousel}

    return plan_slides
