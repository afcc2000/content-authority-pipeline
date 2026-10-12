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
        "",
        "## Entrevista",
    ]
    answers = state.get("answers") or []
    for question, answer in zip(briefing.questions, answers, strict=False):
        lines += ["", f"**{question}**", "", answer or "(pulou)"]

    warnings = state.get("warnings") or []
    if warnings:
        lines += ["", "## Avisos", "", *(f"- {warning}" for warning in warnings)]
    return "\n".join(lines) + "\n"


def export(state: PipelineState) -> dict:
    """Grava `article.md`, `slides.json`, `caption.txt` e `report.md` em `output_dir`.

    Não altera o estado: devolve `{}`.
    """
    out = Path(state["output_dir"])
    out.mkdir(parents=True, exist_ok=True)

    carousel = state["carousel"]
    caption = carousel.caption.strip()
    if carousel.hashtags:
        caption += "\n\n" + " ".join(carousel.hashtags)

    files = {
        "article.md": state["article"].to_markdown(),
        "slides.json": carousel.model_dump_json(indent=2) + "\n",
        "caption.txt": caption + "\n",
        "report.md": build_report(state),
    }
    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")
    return {}
