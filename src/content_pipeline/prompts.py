"""Carrega e compõe os prompts editáveis de `prompts/*.md`."""

from pathlib import Path

SEPARATOR = "\n\n---\n\n"


class PromptNotFoundError(FileNotFoundError):
    """O arquivo de prompt pedido não existe na pasta de prompts."""


def load_prompt(name: str, prompts_dir: Path) -> str:
    """Lê um prompt da pasta de prompts.

    Args:
        name: Nome do prompt, sem a extensão (ex.: "analyze").
        prompts_dir: Pasta onde ficam os arquivos `.md`.

    Returns:
        O conteúdo do arquivo em UTF-8, sem espaços nas pontas.

    Raises:
        PromptNotFoundError: Se `prompts_dir/<name>.md` não existir.
    """
    path = prompts_dir / f"{name}.md"
    if not path.is_file():
        raise PromptNotFoundError(f"Prompt não encontrado: {path}")
    return path.read_text(encoding="utf-8").strip()


def compose(prompts_dir: Path, *names: str) -> str:
    """Junta vários prompts em um só, na ordem dada.

    Args:
        prompts_dir: Pasta onde ficam os arquivos `.md`.
        *names: Nomes dos prompts, sem a extensão.

    Returns:
        Os prompts separados por uma linha horizontal do Markdown (`---`).
    """
    return SEPARATOR.join(load_prompt(name, prompts_dir) for name in names)
