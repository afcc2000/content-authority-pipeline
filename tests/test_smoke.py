"""Teste de fumaça: o pacote instala e importa."""

import content_pipeline


def test_pacote_importa_e_tem_versao() -> None:
    assert content_pipeline.__version__ == "0.1.0"
