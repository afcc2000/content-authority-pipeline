"""Adaptador fake: grava o prompt em texto em vez de gerar a imagem (sem custo, sem rede)."""

from pathlib import Path


class FakeImageGenerator:
    """Usado em dry-run e nos testes; registra os prompts recebidos em `calls`."""

    def __init__(self) -> None:
        """Começa sem nenhum prompt registrado."""
        self.calls: list[str] = []

    def generate(self, prompt: str, *, aspect_ratio: str, out_path: Path) -> Path:
        """Grava `<out_path sem extensão>.prompt.txt` com a proporção e o prompt."""
        self.calls.append(prompt)
        path = out_path.with_suffix(".prompt.txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"aspect_ratio: {aspect_ratio}\n\n{prompt}\n", encoding="utf-8")
        return path
