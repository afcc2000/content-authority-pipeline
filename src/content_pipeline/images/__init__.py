"""Geração de imagens: porta, adaptadores e a fábrica que escolhe o adaptador."""

import os

from content_pipeline.config import Settings
from content_pipeline.images.base import ImageConfigError, ImageGenerationError, ImageGenerator
from content_pipeline.images.fake import FakeImageGenerator
from content_pipeline.images.higgsfield import HiggsfieldImageGenerator

__all__ = [
    "FakeImageGenerator",
    "HiggsfieldImageGenerator",
    "ImageConfigError",
    "ImageGenerationError",
    "ImageGenerator",
    "make_image_generator",
]


def make_image_generator(settings: Settings, *, dry_run: bool) -> ImageGenerator:
    """Escolhe o adaptador de imagem.

    Em dry-run, ou com `IMAGE_PROVIDER=fake`, devolve o fake (nunca gasta créditos).

    Raises:
        ImageConfigError: `IMAGE_PROVIDER=higgsfield` sem credencial no ambiente.
    """
    if dry_run or settings.image_provider == "fake":
        return FakeImageGenerator()
    # O SDK só lê a credencial no primeiro pedido; checamos aqui para falhar antes de começar.
    has_key = os.environ.get("HF_KEY") or (
        os.environ.get("HF_API_KEY") and os.environ.get("HF_API_SECRET")
    )
    if not has_key:
        raise ImageConfigError(
            "IMAGE_PROVIDER=higgsfield exige HF_KEY no .env (formato key-id:key-secret)."
        )
    return HiggsfieldImageGenerator(
        settings.image_model, resolution=settings.image_resolution or None
    )
