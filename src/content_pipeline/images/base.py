"""Porta `ImageGenerator`: o que o grafo precisa de qualquer provedor de imagem."""

from pathlib import Path
from typing import Protocol


class ImageGenerator(Protocol):
    """Interface que o nó `render_images` usa para gerar a imagem de cada slide."""

    def generate(self, prompt: str, *, aspect_ratio: str, out_path: Path) -> Path:
        """Gera a imagem descrita por `prompt` e devolve o caminho do arquivo gravado.

        Args:
            prompt: Descrição da imagem.
            aspect_ratio: Proporção, ex.: "4:5".
            out_path: Caminho sugerido para o arquivo (o adaptador pode trocar a extensão).
        """
        ...
