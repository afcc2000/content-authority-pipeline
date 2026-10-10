"""Testes dos modelos Pydantic."""

import pytest
from pydantic import ValidationError

from content_pipeline.models import Article, Briefing


def test_to_markdown_com_subtitulo() -> None:
    article = Article(title="Título", subtitle="Sub", body_markdown="Corpo")

    assert article.to_markdown() == "# Título\n\n*Sub*\n\nCorpo\n"


def test_to_markdown_sem_subtitulo_nao_deixa_linha_vazia_sobrando() -> None:
    article = Article(title="Título", body_markdown="Corpo")

    assert article.to_markdown() == "# Título\n\nCorpo\n"


@pytest.mark.parametrize("quantidade", [0, 6])
def test_briefing_com_quantidade_invalida_de_perguntas(quantidade: int) -> None:
    with pytest.raises(ValidationError):
        Briefing(
            is_relevant=True,
            relevance_reason="motivo",
            summary="resumo",
            key_points=["ponto"],
            angle="ângulo",
            questions=[f"Pergunta {i}?" for i in range(quantidade)],
        )
