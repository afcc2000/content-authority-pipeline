"""CLI do pipeline: roda o grafo e responde aos `interrupt` no terminal."""

from pathlib import Path
from typing import Annotated
from uuid import uuid4

import typer
from dotenv import find_dotenv, load_dotenv
from langgraph.types import Command

from content_pipeline.config import Settings
from content_pipeline.deps import Deps
from content_pipeline.fetcher import FetchError
from content_pipeline.graph import build_graph, make_checkpointer
from content_pipeline.images import ImageConfigError, make_image_generator
from content_pipeline.llm import LangChainStructuredLLM, LLMConfigError
from content_pipeline.web import SearchError, make_fetch, make_search

app = typer.Typer(
    help="Link -> entrevista -> artigo de autoridade -> carrossel + legenda.",
    no_args_is_help=True,
)

SAMPLE_INPUT = Path("samples/sample_input.md")


def ask_question(payload: dict) -> str:
    """Mostra "Pergunta i/n" e lê a resposta; Enter vazio pula a pergunta."""
    typer.secho(f"\nPergunta {payload['index']}/{payload['total']}", bold=True)
    typer.echo(payload["question"])
    return typer.prompt("Sua resposta (Enter para pular)", default="", show_default=False)


def ask_approval(payload: dict, draft_path: Path) -> dict:
    """Mostra o artigo e lê a decisão do autor: accept, edit ou reject (se ainda puder).

    No `edit`, grava o artigo em `draft_path`, espera o autor editar e salvar, e lê o arquivo.
    """
    typer.secho("\n=== Artigo para aprovação ===\n", bold=True)
    typer.echo(payload["article_markdown"])

    actions = ["accept", "edit"]
    if payload["can_reject"]:
        actions.append("reject")
    else:
        typer.secho("Limite de reescritas atingido: reject indisponível.", fg=typer.colors.YELLOW)

    action = ""
    while action not in actions:
        action = typer.prompt(f"Ação ({'/'.join(actions)})").strip().lower()

    if action == "edit":
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(payload["article_markdown"], encoding="utf-8")
        typer.echo(f"Edite e salve o arquivo: {draft_path}")
        typer.prompt("Pressione Enter quando terminar", default="", show_default=False)
        return {"action": "edit", "article_markdown": draft_path.read_text(encoding="utf-8")}
    if action == "reject":
        return {"action": "reject", "feedback": typer.prompt("O que deve mudar no artigo?")}
    return {"action": "accept"}


def build_deps(settings: Settings, dry_run: bool) -> Deps:
    """Monta as implementações reais (LLM, imagens, leitura e busca na web)."""
    return Deps(
        llm=LangChainStructuredLLM(settings.llm_model),
        images=make_image_generator(settings, dry_run=dry_run),
        settings=settings,
        fetch=make_fetch(settings),
        search=make_search(settings),
    )


def answer_interrupts(graph, initial: dict) -> dict:
    """Roda o grafo e responde a cada `interrupt` (pergunta ou aprovação) até o fim."""
    config = {"configurable": {"thread_id": str(uuid4())}}
    result = graph.invoke(initial, config)
    while "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        if payload["type"] == "question":
            answer = ask_question(payload)
        else:
            draft_path = Path(result["output_dir"]) / "article_draft.md"
            answer = ask_approval(payload, draft_path)
        result = graph.invoke(Command(resume=answer), config)
    return result


def report(result: dict) -> None:
    """Mostra o desfecho: fonte irrelevante, avisos e onde ficaram os arquivos."""
    briefing = result.get("briefing")
    if briefing and not briefing.is_relevant:
        typer.secho(
            f"\nConteúdo fora dos temas do autor: {briefing.relevance_reason}",
            fg=typer.colors.YELLOW,
        )
    for warning in result.get("warnings") or []:
        typer.secho(f"Aviso: {warning}", fg=typer.colors.YELLOW)
    out = Path(result["output_dir"])
    if (out / "article.md").exists():
        typer.secho(f"\nPronto! Arquivos em: {out}", fg=typer.colors.GREEN)
    elif (out / "report.md").exists():
        typer.echo(f"\nRelatório em: {out / 'report.md'}")


def run_pipeline(initial: dict, dry_run: bool, out: Path) -> None:
    """Monta as dependências, roda o grafo respondendo às pausas e mostra o desfecho."""
    # usecwd=True: procura o .env a partir da pasta atual, não da pasta deste arquivo.
    load_dotenv(find_dotenv(usecwd=True))
    settings = Settings(output_root=out)

    try:
        deps = build_deps(settings, dry_run)
        if initial.get("topic") and deps.search is None:
            raise SearchError("--topic exige TAVILY_API_KEY no .env.")
        graph = build_graph(deps, checkpointer=make_checkpointer())
        result = answer_interrupts(graph, initial)
    except (LLMConfigError, ImageConfigError, FetchError, SearchError) as exc:
        typer.secho(f"Erro: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from exc

    report(result)


OutOption = Annotated[Path, typer.Option(help="Pasta onde salvar os resultados.")]


@app.command()
def run(
    url: Annotated[str | None, typer.Option(help="Link do conteúdo de referência.")] = None,
    file: Annotated[Path | None, typer.Option(help="Arquivo .md ou .txt com o conteúdo.")] = None,
    topic: Annotated[
        str | None, typer.Option(help="Tema para buscar uma fonte na web (Tavily).")
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Não chama a API de imagem (só grava os prompts). Sem esta opção, quem "
            "decide é o IMAGE_PROVIDER do .env (padrão: fake, sem custo).",
        ),
    ] = False,
    out: OutOption = Path("outputs"),
) -> None:
    """Roda o pipeline a partir de exatamente uma fonte: --url, --file ou --topic."""
    sources = {"source_url": url, "source_path": str(file) if file else None, "topic": topic}
    given = {key: value for key, value in sources.items() if value}
    if len(given) != 1:
        raise typer.BadParameter("Informe exatamente um entre --url, --file e --topic.")
    run_pipeline(given, dry_run=dry_run, out=out)


@app.command()
def demo(out: OutOption = Path("outputs")) -> None:
    """Roda o pipeline com samples/sample_input.md em dry-run."""
    run_pipeline({"source_path": str(SAMPLE_INPUT)}, dry_run=True, out=out)
