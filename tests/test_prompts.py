"""Testes do carregador de prompts."""

from pathlib import Path

import pytest

from content_pipeline.prompts import PromptNotFoundError, compose, load_prompt

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


@pytest.mark.parametrize(
    "name", ["context", "analyze", "article_style", "carousel_brand", "carousel_rules"]
)
def test_prompt_existe_e_nao_esta_vazio(name: str) -> None:
    assert load_prompt(name, PROMPTS_DIR)


def test_estilo_do_artigo_proibe_comentar_pergunta_pulada() -> None:
    # Na execução real, o artigo publicado dizia "Eu pulei a pergunta sobre...".
    style = load_prompt("article_style", PROMPTS_DIR)
    assert "não mencione no texto que ele pulou" in style


def test_analyze_julga_relevancia_so_pela_fonte() -> None:
    # A direção do autor orienta ângulo e perguntas, mas não pode "aprovar" uma fonte.
    assert "relevância é julgada só pela fonte" in load_prompt("analyze", PROMPTS_DIR)


def test_prompt_inexistente_levanta_erro_com_nome_do_arquivo(tmp_path: Path) -> None:
    with pytest.raises(PromptNotFoundError, match="nao_existe.md"):
        load_prompt("nao_existe", tmp_path)


def test_compose_respeita_ordem_e_separador(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("  texto A\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("texto B", encoding="utf-8")

    assert compose(tmp_path, "a", "b") == "texto A\n\n---\n\ntexto B"
    assert compose(tmp_path, "b", "a") == "texto B\n\n---\n\ntexto A"
