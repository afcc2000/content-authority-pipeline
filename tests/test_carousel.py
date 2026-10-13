"""Testes do subgrafo do carrossel (plan_slides -> validate -> render_images) com fakes."""

from pathlib import Path

from content_pipeline.carousel.planner import build_carousel_request
from content_pipeline.carousel.subgraph import build_carousel_subgraph
from content_pipeline.deps import Deps
from content_pipeline.images import FakeImageGenerator
from content_pipeline.models import CarouselPlan
from tests.fakes import FakeStructuredLLM, make_article, make_carousel, make_settings


def run_subgraph(tmp_path: Path, carousels: list[CarouselPlan]):
    """Roda o subgrafo sozinho, como se o artigo já tivesse sido aprovado."""
    llm = FakeStructuredLLM({CarouselPlan: carousels})
    images = FakeImageGenerator()
    deps = Deps(llm=llm, images=images, settings=make_settings(max_carousel_attempts=2))
    state = {
        "article": make_article(),
        "output_dir": str(tmp_path / "saida"),
        "carousel_attempts": 0,
        "warnings": [],
    }
    final = build_carousel_subgraph(deps).invoke(state)
    return llm, images, final


def test_carrossel_valido_de_primeira_gera_uma_imagem_por_slide(tmp_path: Path) -> None:
    llm, images, final = run_subgraph(tmp_path, [make_carousel()])

    assert len(llm.calls) == 1
    assert len(images.calls) == 5
    assert (tmp_path / "saida" / "images" / "slide_05.prompt.txt").exists()
    assert final["carousel_attempts"] == 1


def test_validacao_falha_2_vezes_segue_com_aviso(tmp_path: Path) -> None:
    llm, images, final = run_subgraph(tmp_path, [make_carousel(2), make_carousel(2)])

    assert final["carousel_attempts"] == 2
    assert any("Carrossel seguiu com erros" in aviso for aviso in final["warnings"])
    assert "Corrija estes erros" not in llm.calls[0][2]
    assert "Corrija estes erros" in llm.calls[1][2]
    assert "O carrossel tem 2 slides" in llm.calls[1][2]
    assert len(images.calls) == 2  # segue mesmo com erros, com o que tem


def test_validacao_falha_1_vez_e_depois_passa(tmp_path: Path) -> None:
    _llm, _images, final = run_subgraph(tmp_path, [make_carousel(2), make_carousel()])

    assert final["validation_errors"] == []
    assert final["warnings"] == []
    assert final["carousel_attempts"] == 2


def test_pedido_do_carrossel_tem_limites_de_settings_e_artigo(tmp_path: Path) -> None:
    llm, _images, _final = run_subgraph(tmp_path, [make_carousel()])

    schema, system, user = llm.calls[0]
    assert schema is CarouselPlan
    assert "No máximo 5 hashtags." in user
    assert "<artigo>\n# Título do artigo" in user
    assert "Identidade visual" in system  # carousel_brand entra no system


def make_request(**settings_overrides) -> str:
    """Monta o pedido do carrossel sem rodar o subgrafo."""
    deps = Deps(
        llm=FakeStructuredLLM({}),
        images=FakeImageGenerator(),
        settings=make_settings(**settings_overrides),
    )
    return build_carousel_request({"article": make_article()}, deps)


def test_pedido_do_carrossel_inclui_o_link_do_blog() -> None:
    url = "https://meublog.com/artigo"

    assert f"A legenda deve conter o link do blog: {url}" in make_request(blog_url=url)


def test_pedido_do_carrossel_sem_blog_url_nao_cita_link() -> None:
    assert "link do blog" not in make_request()
