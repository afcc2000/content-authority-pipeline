"""Testes da configuração (Settings)."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from content_pipeline.config import Settings


@pytest.fixture(autouse=True)
def ambiente_limpo(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove do ambiente as variáveis que mudariam os padrões testados."""
    for nome in Settings.model_fields:
        monkeypatch.delenv(nome.upper(), raising=False)


def test_padroes_sem_env_file() -> None:
    settings = Settings(_env_file=None)

    assert settings.llm_model is None
    assert settings.image_provider == "fake"
    assert settings.prompts_dir == Path("prompts")
    assert settings.output_root == Path("outputs")
    assert settings.max_rewrites == 3
    assert settings.max_carousel_attempts == 2
    assert settings.min_slides == 5
    assert settings.max_slides == 10
    assert settings.headline_max_chars == 80
    assert settings.caption_max_chars == 2200
    assert settings.max_hashtags == 5
    assert settings.image_aspect_ratio == "4:5"
    assert settings.blog_url is None


def test_variavel_de_ambiente_sobrescreve_padrao(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_SLIDES", "7")

    assert Settings(_env_file=None).max_slides == 7


def test_image_provider_invalido_levanta_erro(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMAGE_PROVIDER", "xyz")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
