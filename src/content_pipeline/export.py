"""Nó `export`: grava artigo, slides, legenda e relatório na pasta da execução."""

from pathlib import Path

from content_pipeline.state import PipelineState


def _source(state: PipelineState) -> str:
    return state.get("source_url") or state.get("source_path") or "(texto informado diretamente)"


def build_report(state: PipelineState) -> str:
    """Monta o relatório da execução em Markdown."""
    briefing = state["briefing"]
    relevance = "sim" if briefing.is_relevant else "não"
    lines = [
        "# Relatório da execução",
        "",
        f"- **Fonte:** {_source(state)}",
        f"- **Título da fonte:** {state.get('source_title') or '(sem título)'}",
        f"- **Relevante:** {relevance}. {briefing.relevance_reason}",
        f"- **Decisão sobre o artigo:** {state.get('decision', '(sem decisão)')}",
        f"- **Reescritas:** {state.get('rewrites') or 0}",
        f"- **Tentativas do carrossel:** {state.get('carousel_attempts') or 0}",
    ]
    if state.get("feedback"):
        lines.append(f"- **Último feedback do autor:** {state['feedback']}")

    answers = state.get("answers") or []
    if answers:
        lines += ["", "## Entrevista"]
    for question, answer in zip(briefing.questions, answers, strict=False):
        lines += ["", f"**{question}**", "", answer or "(pulou)"]

    if state.get("author_direction"):
        lines += ["", "## Direção do autor", "", state["author_direction"]]

    warnings = state.get("warnings") or []
    if warnings:
        lines += ["", "## Avisos", "", *(f"- {warning}" for warning in warnings)]
    return "\n".join(lines) + "\n"


def _write(state: PipelineState, files: dict[str, str]) -> None:
    """Grava cada `nome: conteúdo` de `files` em `output_dir`, criando a pasta se preciso."""
    out = Path(state["output_dir"])
    out.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")


def export(state: PipelineState) -> dict:
    """Grava `article.md`, `slides.json`, `caption.txt` e `report.md` em `output_dir`.

    Não altera o estado: devolve `{}`.
    """
    carousel = state["carousel"]
    caption = carousel.caption.strip()
    if carousel.hashtags:
        caption += "\n\n" + " ".join(carousel.hashtags)

    _write(
        state,
        {
            "article.md": state["article"].to_markdown(),
            "slides.json": carousel.model_dump_json(indent=2) + "\n",
            "caption.txt": caption + "\n",
            "report.md": build_report(state),
        },
    )
    return {}


def export_report(state: PipelineState) -> dict:
    """Grava só o `report.md`: o pipeline terminou sem artigo aprovado.

    Usado quando a fonte é irrelevante ou o autor rejeita o artigo depois do limite de
    reescritas, para que o motivo do encerramento fique registrado. Devolve `{}`.
    """
    _write(state, {"report.md": build_report(state)})
    return {}
