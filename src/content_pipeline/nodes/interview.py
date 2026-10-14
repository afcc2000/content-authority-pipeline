"""Nó `interview`: faz ao autor uma pergunta do briefing por vez, pausando o grafo.

Regras do `interrupt` (projeto §5.2):
1. Nunca dentro de `try/except` genérico: ele funciona lançando uma exceção interna.
2. Ao retomar, o nó roda de novo do início; por isso nada de efeito colateral antes dele.
3. A ordem dos `interrupt` dentro do nó é estável (aqui, um só por execução).
"""

from typing import Literal

from langgraph.types import interrupt

from content_pipeline.state import PipelineState

# Pergunta fixa, feita depois das perguntas do briefing: dá ao autor uma forma de conduzir o
# artigo além do que o LLM perguntou. A resposta prevalece sobre o ângulo sugerido.
DIRECTION_QUESTION = (
    "Antes de escrever: que direção você quer dar ao artigo? Algo a enfatizar, evitar, um "
    "ângulo, exemplo ou opinião sua que deve aparecer?"
)


def interview(state: PipelineState) -> dict:
    """Faz a próxima pergunta: as do briefing, uma por vez, e por fim a de direção.

    Cada resposta vazia vira "" (o autor pulou). As do briefing vão para `answers`; a de
    direção, para `author_direction`.
    """
    questions = state["briefing"].questions
    answers = list(state.get("answers") or [])
    index = len(answers)
    total = len(questions) + 1  # + a pergunta de direção

    if index < len(questions):
        answer = interrupt(
            {"type": "question", "index": index + 1, "total": total, "question": questions[index]}
        )
        return {"answers": [*answers, answer or ""]}

    answer = interrupt(
        {"type": "question", "index": total, "total": total, "question": DIRECTION_QUESTION}
    )
    return {"author_direction": answer or ""}


def route_after_interview(state: PipelineState) -> Literal["interview", "write_article"]:
    """Volta para `interview` até responder o briefing e a direção; depois `write_article`."""
    if len(state.get("answers") or []) < len(state["briefing"].questions):
        return "interview"
    if state.get("author_direction") is None:
        return "interview"
    return "write_article"
