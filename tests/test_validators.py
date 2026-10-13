"""Testes dos validadores determinísticos do carrossel (funções puras, sem LLM)."""

import pytest

from content_pipeline.carousel.validators import (
    check_blog_link,
    check_caption,
    check_cta,
    check_headlines,
    check_slide_count,
    check_slides_complete,
    validate_carousel,
)
from tests.fakes import make_carousel, make_settings


def test_carrossel_valido_nao_tem_erros() -> None:
    assert validate_carousel(make_carousel(), make_settings()) == []


@pytest.mark.parametrize("n_slides", [4, 11])
def test_numero_de_slides_fora_do_limite_gera_erro(n_slides: int) -> None:
    errors = check_slide_count(make_carousel(n_slides), min_slides=5, max_slides=10)

    assert errors == [f"O carrossel tem {n_slides} slides (mínimo 5, máximo 10)."]


def test_headline_longa_gera_a_mensagem_exata() -> None:
    plan = make_carousel()
    plan.slides[0].headline = "x" * 81

    assert check_headlines(plan, max_chars=80) == [
        "Slide 1: headline com 81 caracteres (máximo 80)."
    ]


def test_headline_no_limite_e_valida() -> None:
    plan = make_carousel()
    plan.slides[0].headline = "x" * 80

    assert check_headlines(plan, max_chars=80) == []


def test_cta_so_com_espacos_gera_erro() -> None:
    assert len(check_cta(make_carousel(cta="   "))) == 1


def test_legenda_e_hashtags_acima_do_limite_geram_2_erros() -> None:
    plan = make_carousel()
    plan.caption = "x" * 2201
    plan.hashtags = [f"#tag{i}" for i in range(6)]

    errors = check_caption(plan, max_chars=2200, max_hashtags=5)

    assert errors == ["Legenda com 2201 caracteres (máximo 2200).", "6 hashtags (máximo 5)."]


def test_indice_fora_de_sequencia_headline_e_image_prompt_vazios_geram_3_erros() -> None:
    plan = make_carousel()
    plan.slides[1].index = 5
    plan.slides[2].headline = " "
    plan.slides[3].image_prompt = ""

    errors = check_slides_complete(plan)

    assert len(errors) == 3
    assert "em ordem" in errors[0]
    assert errors[1] == "Slide 3: headline vazia."
    assert errors[2] == "Slide 4: image_prompt vazio."


def test_validate_carousel_usa_os_limites_de_settings() -> None:
    plan = make_carousel(n_slides=7)

    assert validate_carousel(plan, make_settings(max_slides=6)) == [
        "O carrossel tem 7 slides (mínimo 5, máximo 6)."
    ]


BLOG_URL = "https://meublog.com/artigo"


def test_legenda_sem_link_do_blog_gera_erro() -> None:
    errors = check_blog_link(make_carousel(), BLOG_URL)

    assert len(errors) == 1
    assert BLOG_URL in errors[0]


def test_legenda_com_link_do_blog_passa() -> None:
    plan = make_carousel()
    plan.caption = f"Legenda do carrossel. Leia o artigo completo: {BLOG_URL}"

    assert check_blog_link(plan, BLOG_URL) == []


def test_sem_blog_url_regra_nao_se_aplica() -> None:
    assert check_blog_link(make_carousel(), None) == []
