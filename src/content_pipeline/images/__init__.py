"""Geração de imagens: porta, adaptadores e a fábrica que escolhe o adaptador."""

from content_pipeline.config import Settings
from content_pipeline.images.base import ImageGenerator
from content_pipeline.images.fake import FakeImageGenerator

__all__ = ["FakeImageGenerator", "ImageGenerator", "make_image_generator"]


def make_image_generator(settings: Settings, *, dry_run: bool) -> ImageGenerator:
    """Escolhe o adaptador de imagem.

    Em dry-run, ou com `IMAGE_PROVIDER=fake`, devolve o fake (nunca gasta créditos).

    Raises:
        NotImplementedError: Provedor real ainda não implementado (ver ticket E1).
    """
    if dry_run or settings.image_provider == "fake":
        return FakeImageGenerator()
    raise NotImplementedError(
        f"O provedor de imagem '{settings.image_provider}' ainda não foi implementado: "
        "a API está [A verificar] (ticket E1). Use IMAGE_PROVIDER=fake ou --dry-run."
    )
