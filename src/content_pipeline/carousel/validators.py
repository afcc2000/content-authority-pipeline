"""Validadores determinísticos do carrossel.

Rodam ANTES de gerar imagens: são regras puras e baratas, sem LLM. Cada função devolve uma
lista de mensagens de erro em português; lista vazia significa válido.
"""

from content_pipeline.config import Settings
from content_pipeline.models import CarouselPlan


def check_slide_count(plan: CarouselPlan, min_slides: int, max_slides: int) -> list[str]:
    """Confere se o número de slides está entre `min_slides` e `max_slides`."""
    n = len(plan.slides)
    if min_slides <= n <= max_slides:
        return []
    return [f"O carrossel tem {n} slides (mínimo {min_slides}, máximo {max_slides})."]


def check_headlines(plan: CarouselPlan, max_chars: int) -> list[str]:
    """Confere se cada headline cabe em `max_chars` caracteres."""
    return [
        f"Slide {slide.index}: headline com {len(slide.headline)} caracteres (máximo {max_chars})."
        for slide in plan.slides
        if len(slide.headline) > max_chars
    ]


def check_cta(plan: CarouselPlan) -> list[str]:
    """Confere se há chamada para o blog."""
    if plan.cta_text.strip():
        return []
    return ["A chamada para o blog (cta_text) está vazia."]


def check_caption(plan: CarouselPlan, max_chars: int, max_hashtags: int) -> list[str]:
    """Confere o tamanho da legenda e o número de hashtags."""
    errors = []
    if len(plan.caption) > max_chars:
        errors.append(f"Legenda com {len(plan.caption)} caracteres (máximo {max_chars}).")
    if len(plan.hashtags) > max_hashtags:
        errors.append(f"{len(plan.hashtags)} hashtags (máximo {max_hashtags}).")
    return errors


def check_slides_complete(plan: CarouselPlan) -> list[str]:
    """Confere se os índices são 1..n em ordem e se nenhum slide tem headline ou imagem vazia."""
    errors = []
    indexes = [slide.index for slide in plan.slides]
    if indexes != list(range(1, len(indexes) + 1)):
        errors.append(f"Os índices dos slides devem ser 1, 2, 3... em ordem (recebido: {indexes}).")
    for slide in plan.slides:
        if not slide.headline.strip():
            errors.append(f"Slide {slide.index}: headline vazia.")
        if not slide.image_prompt.strip():
            errors.append(f"Slide {slide.index}: image_prompt vazio.")
    return errors


def validate_carousel(plan: CarouselPlan, settings: Settings) -> list[str]:
    """Roda todos os validadores com os limites de `settings` e junta os erros."""
    return [
        *check_slide_count(plan, settings.min_slides, settings.max_slides),
        *check_headlines(plan, settings.headline_max_chars),
        *check_cta(plan),
        *check_caption(plan, settings.caption_max_chars, settings.max_hashtags),
        *check_slides_complete(plan),
    ]
