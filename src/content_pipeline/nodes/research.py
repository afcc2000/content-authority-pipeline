"""Nó `research`: busca o tema na web e escolhe a melhor fonte para o `ingest`."""

from content_pipeline.deps import Deps
from content_pipeline.models import SearchResult, SourceChoice
from content_pipeline.nodes.common import ask
from content_pipeline.state import PipelineState


def results_block(topic: str, results: list[SearchResult]) -> str:
    """Monta a mensagem com os resultados numerados dentro de <resultados> (dados, não instrução)."""
    items = "\n\n".join(
        f"{i}. {r.title}\n   URL: {r.url}\n   Trecho: {r.snippet}"
        for i, r in enumerate(results, start=1)
    )
    return f"Tema: {topic}\n\n<resultados>\n{items}\n</resultados>"


def make_research(deps: Deps):
    """Cria o nó `research`."""

    def research(state: PipelineState) -> dict:
        topic = state["topic"]
        if deps.search is None:
            raise ValueError("A busca por tema exige TAVILY_API_KEY no .env.")
        results = deps.search(topic)
        if not results:
            raise ValueError(f"A busca por '{topic}' não trouxe resultados.")

        choice = ask(deps, SourceChoice, ["context", "research"], results_block(topic, results))

        urls = [r.url for r in results]
        warnings = list(state.get("warnings") or [])
        url = choice.url
        if url not in urls:
            # O LLM pode "inventar" ou alterar a URL; só seguimos com URLs que a busca trouxe.
            warnings.append(f"URL escolhida fora dos resultados ({url}); usando o 1º resultado.")
            url = urls[0]
        return {"source_url": url, "search_results": results, "warnings": warnings}

    return research
