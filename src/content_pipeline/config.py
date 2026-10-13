"""Configuração do pipeline lida do ambiente e do arquivo `.env`."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parâmetros do pipeline.

    Cada campo pode ser definido por uma variável de ambiente com o mesmo nome em
    maiúsculas (ex.: `MAX_SLIDES=7`) ou no arquivo `.env`. Chaves de API não ficam aqui:
    as bibliotecas dos provedores as leem direto do ambiente.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_model: str | None = None  # "provedor:modelo", ex.: "openai:<modelo>"
    image_provider: Literal["fake", "higgsfield"] = "fake"
    web_reader: Literal["trafilatura", "tavily"] = "trafilatura"  # leitura dos links
    prompts_dir: Path = Path("prompts")
    output_root: Path = Path("outputs")

    max_rewrites: int = 3  # reescritas de artigo permitidas
    max_carousel_attempts: int = 2  # tentativas de gerar um carrossel válido

    # Limites do Instagram verificados em 2026-10-10 (imprensa especializada; sem página oficial):
    # o app aceita 20 slides, mas a API da Meta e os agendadores ainda limitam a 10; legenda
    # mantida no valor conservador de 2.200; hashtags reduzidas a 5 por post (dez/2025).
    min_slides: int = 5  # escolha editorial do projeto, não limite do Instagram
    max_slides: int = 10
    headline_max_chars: int = 80
    caption_max_chars: int = 2200
    max_hashtags: int = 5
    image_aspect_ratio: str = "4:5"
    blog_url: str | None = None  # se definido, a legenda precisa conter este link
