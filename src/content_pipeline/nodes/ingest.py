"""Nó `ingest`: obtém o texto da fonte (texto direto, arquivo local ou link)."""

import re
import unicodedata
from datetime import date
from pathlib import Path

from content_pipeline.deps import Deps
from content_pipeline.state import PipelineState


def slugify(text: str, max_length: int = 50) -> str:
    """Transforma um texto em um nome de pasta seguro: "Olá, Mundo!" -> "ola-mundo".

    Remove acentos, deixa só letras minúsculas, números e hífens. Vazio -> "conteudo".
    """
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    slug = slug[:max_length].strip("-")
    return slug or "conteudo"


def _title_from_markdown(text: str) -> str | None:
    """Título = primeira linha que começa com "# ", ou None."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or None
    return None


def make_ingest(deps: Deps):
    """Cria o nó `ingest`."""

    def ingest(state: PipelineState) -> dict:
        title = state.get("source_title")
        if state.get("source_text"):
            text = state["source_text"]
            fallback_name = "conteudo"
        elif state.get("source_path"):
            path = Path(state["source_path"])
            text = path.read_text(encoding="utf-8")
            title = title or _title_from_markdown(text)
            fallback_name = path.stem
        elif state.get("source_url"):
            fetched_title, text = deps.fetch(state["source_url"])
            title = title or fetched_title
            fallback_name = state["source_url"]
        else:
            raise ValueError("Informe source_text, source_path ou source_url.")

        update: dict = {
            "source_text": text,
            "source_title": title,
            "answers": [],
            "rewrites": 0,
            "carousel_attempts": 0,
            "warnings": list(state.get("warnings") or []),  # preserva avisos do research
        }
        if not state.get("output_dir"):
            folder = f"{date.today().isoformat()}-{slugify(title or fallback_name)}"
            update["output_dir"] = str(deps.settings.output_root / folder)
        return update

    return ingest
