"""Testes da CLI com o CliRunner do Typer (sem chamar API real)."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from content_pipeline.cli import app

SAMPLE = Path(__file__).resolve().parents[1] / "samples" / "sample_input.md"
runner = CliRunner()


@pytest.fixture
def sem_dotenv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Roda a partir de `tmp_path`, para o `load_dotenv` não achar o .env real do projeto."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_help_lista_run_e_demo() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "run" in result.output
    assert "demo" in result.output


def test_sem_llm_model_termina_com_codigo_1_e_mensagem(
    sem_dotenv: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LLM_MODEL", "")

    result = runner.invoke(app, ["run", "--file", str(SAMPLE), "--out", str(sem_dotenv)])

    assert result.exit_code == 1
    assert "LLM_MODEL" in result.output


@pytest.mark.parametrize(
    "args",
    [
        ["--url", "https://exemplo.com", "--file", "x.md"],
        ["--file", "x.md", "--topic", "tema"],
        [],
    ],
)
def test_run_exige_exatamente_uma_fonte(sem_dotenv: Path, args: list[str]) -> None:
    result = runner.invoke(app, ["run", *args])

    assert result.exit_code == 2
    assert "exatamente um" in result.output


def test_topic_sem_tavily_termina_com_codigo_1(
    sem_dotenv: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LLM_MODEL", "openai:gpt-qualquer")
    monkeypatch.setenv("OPENAI_API_KEY", "chave-falsa-de-teste")
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    result = runner.invoke(app, ["run", "--topic", "tema", "--out", str(sem_dotenv)])

    assert result.exit_code == 1
    assert "TAVILY_API_KEY" in result.output


def test_demo_responde_entrevista_e_aprovacao_ate_exportar(
    sem_dotenv: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from content_pipeline import cli
    from content_pipeline.models import Article, Briefing, CarouselPlan
    from tests.fakes import FakeStructuredLLM, make_article, make_briefing, make_carousel

    fake = FakeStructuredLLM(
        {Briefing: [make_briefing()], Article: [make_article()], CarouselPlan: [make_carousel()]}
    )
    monkeypatch.setattr(cli, "LangChainStructuredLLM", lambda model: fake)
    monkeypatch.setattr(cli, "SAMPLE_INPUT", SAMPLE)
    monkeypatch.setenv("PROMPTS_DIR", str(SAMPLE.parents[1] / "prompts"))  # cwd é o tmp_path

    # 1ª pergunta respondida, 2ª pulada (Enter), ação inválida, depois accept.
    result = runner.invoke(
        app, ["demo", "--out", str(sem_dotenv)], input="Minha resposta\n\nx\naccept\n"
    )

    assert result.exit_code == 0, result.output
    assert "Pergunta 1/2" in result.output and "Pergunta 2/2" in result.output
    assert "Pronto! Arquivos em:" in result.output
    assert len(list(sem_dotenv.rglob("article.md"))) == 1
