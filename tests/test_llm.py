"""Testes da porta StructuredLLM (sem chamar API real)."""

import pytest

from content_pipeline.llm import LangChainStructuredLLM, LLMConfigError
from content_pipeline.models import Article, Briefing
from tests.fakes import FakeStructuredLLM, make_article, make_briefing


@pytest.mark.parametrize("model", [None, ""])
def test_sem_modelo_levanta_erro_mencionando_llm_model(model: str | None) -> None:
    with pytest.raises(LLMConfigError, match="LLM_MODEL"):
        LangChainStructuredLLM(model)


def test_provedor_invalido_vira_llm_config_error() -> None:
    with pytest.raises(LLMConfigError, match="xyz:abc"):
        LangChainStructuredLLM("xyz:abc")


def test_fake_devolve_respostas_em_ordem_e_registra_chamadas() -> None:
    primeiro, segundo = make_article("V1"), make_article("V2")
    briefing = make_briefing()
    llm = FakeStructuredLLM({Article: [primeiro, segundo], Briefing: [briefing]})

    assert llm.generate(Article, "sys 1", "user 1") is primeiro
    assert llm.generate(Briefing, "sys 2", "user 2") is briefing
    assert llm.generate(Article, "sys 3", "user 3") is segundo
    assert llm.calls == [
        (Article, "sys 1", "user 1"),
        (Briefing, "sys 2", "user 2"),
        (Article, "sys 3", "user 3"),
    ]
