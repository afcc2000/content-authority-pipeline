"""Nó `interview`: faz ao autor uma pergunta do briefing por vez, pausando o grafo.

Regras do `interrupt` (projeto §5.2):
1. Nunca dentro de `try/except` genérico: ele funciona lançando uma exceção interna.
2. Ao retomar, o nó roda de novo do início; por isso nada de efeito colateral antes dele.
3. A ordem dos `interrupt` dentro do nó é estável (aqui, um só por execução).
"""

from typing import Literal

from langgraph.graph import END
from langgraph.types import interrupt

from content_pipeline.state import PipelineState


def interview(state: PipelineState) -> dict:
    """Pergunta `questions[len(answers)]` e guarda a resposta ("" se o autor pulou)."""
    questions = state["briefing"].questions
    answers = list(state.get("answers") or [])
    index = len(answers)

    answer = interrupt(
        {
            "type": "question",
            "index": index + 1,
            "total": len(questions),
            "question": questions[index],
        }
    )
    return {"answers": [*answers, answer or ""]}


def route_after_interview(state: PipelineState) -> Literal["interview", "__end__"]:
    """Volta para `interview` enquanto faltar resposta; depois termina (no T11, vai escrever)."""
    if len(state.get("answers") or []) < len(state["briefing"].questions):
        return "interview"
    return END
