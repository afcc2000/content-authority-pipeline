"""Testes da porta ImageGenerator e do adaptador fake."""

from pathlib import Path

import pytest

from content_pipeline.images import FakeImageGenerator, make_image_generator
from tests.fakes import make_settings


def test_fake_grava_prompt_e_registra_chamada(tmp_path: Path) -> None:
    fake = FakeImageGenerator()

    path = fake.generate(
        "Um café sobre a mesa", aspect_ratio="4:5", out_path=tmp_path / "images" / "slide_01.png"
    )

    assert path == tmp_path / "images" / "slide_01.prompt.txt"
    conteudo = path.read_text(encoding="utf-8")
    assert "4:5" in conteudo
    assert "Um café sobre a mesa" in conteudo
    assert fake.calls == ["Um café sobre a mesa"]


def test_dry_run_devolve_fake_mesmo_com_higgsfield() -> None:
    settings = make_settings(image_provider="higgsfield")

    assert isinstance(make_image_generator(settings, dry_run=True), FakeImageGenerator)


def test_higgsfield_sem_dry_run_nao_esta_implementado() -> None:
    settings = make_settings(image_provider="higgsfield")

    with pytest.raises(NotImplementedError, match="E1"):
        make_image_generator(settings, dry_run=False)
