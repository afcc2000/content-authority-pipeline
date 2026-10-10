"""Modelos Pydantic das saídas estruturadas dos LLMs.

As `description` de cada campo vão para o LLM como parte do schema JSON, então
funcionam como instrução: escreva-as pensando no modelo que vai preenchê-las.
"""

from pydantic import BaseModel, Field


class Briefing(BaseModel):
    """Análise do conteúdo de referência e perguntas para o autor."""

    is_relevant: bool = Field(
        description="True se o conteúdo é relevante para os temas aceitos do autor."
    )
    relevance_reason: str = Field(description="Justificativa curta da decisão de relevância.")
    summary: str = Field(description="Resumo do conteúdo de referência em 3 a 5 frases.")
    key_points: list[str] = Field(description="Pontos-chave do conteúdo, um por item.")
    angle: str = Field(
        description="Ângulo sugerido para o artigo de autoridade: o que o autor pode acrescentar."
    )
    questions: list[str] = Field(
        min_length=1,
        max_length=5,
        description="Perguntas abertas para o autor (1 a 5), uma ideia por pergunta.",
    )


class Article(BaseModel):
    """Artigo de autoridade em Markdown."""

    title: str = Field(description='Título do artigo, sem o "#" do Markdown.')
    subtitle: str | None = Field(default=None, description="Subtítulo opcional.")
    body_markdown: str = Field(
        description="Corpo do artigo em Markdown, com seções ##, sem repetir o título."
    )
    tags: list[str] = Field(default_factory=list, description="Tags do artigo para o blog.")

    def to_markdown(self) -> str:
        """Monta o artigo completo em Markdown.

        Returns:
            O texto no formato "# título", "*subtítulo*" (se houver) e o corpo,
            separados por uma linha em branco e terminando com uma quebra de linha.
        """
        parts = [f"# {self.title}"]
        if self.subtitle:
            parts.append(f"*{self.subtitle}*")
        parts.append(self.body_markdown.strip())
        return "\n\n".join(parts) + "\n"


class Slide(BaseModel):
    """Um slide do carrossel."""

    index: int = Field(description="Posição do slide no carrossel, começando em 1.")
    headline: str = Field(description="Frase curta de impacto exibida no slide.")
    body: str | None = Field(default=None, description="Complemento curto opcional da headline.")
    image_prompt: str = Field(
        description="Descrição da imagem de fundo, seguindo a identidade visual, sem texto escrito."
    )


class CarouselPlan(BaseModel):
    """Carrossel de Instagram com legenda."""

    slides: list[Slide] = Field(description="Slides do carrossel, em ordem.")
    caption: str = Field(description="Legenda do post, sem hashtags.")
    hashtags: list[str] = Field(
        default_factory=list, description="Hashtags do post, cada uma começando com #."
    )
    cta_text: str = Field(description="Chamada para ler o artigo completo no blog.")


class SearchResult(BaseModel):
    """Um resultado da busca na web (vem do Tavily, não do LLM)."""

    url: str
    title: str
    snippet: str


class SourceChoice(BaseModel):
    """Fonte escolhida pelo LLM entre os resultados da busca."""

    url: str = Field(description="URL do resultado escolhido, exatamente como aparece na lista.")
    reason: str = Field(
        description="Justificativa curta: por que esta fonte é a melhor para o tema."
    )
