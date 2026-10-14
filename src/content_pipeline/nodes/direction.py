"""Nó `ask_direction`: pergunta ao autor a direção do artigo antes de gerar o briefing.

Vem antes do `analyze` para que a direção oriente o ângulo e as perguntas da entrevista, e não
só o artigo. As regras do `interrupt` são as mesmas da entrevista (ver `nodes/interview.py`).
"""

from langgraph.types import interrupt

from content_pipeline.state import PipelineState

DIRECTION_QUESTION = (
    "Antes de escrever: que direção você quer dar ao artigo? Algo a enfatizar, evitar, um "
    "ângulo, exemplo ou opinião sua que deve aparecer?"
)


def ask_direction(state: PipelineState) -> dict:
    """Pausa uma vez e guarda a resposta em `author_direction` ("" se o autor pulou).

    Se a direção já veio no estado inicial, não pausa.
    """
    if state.get("author_direction") is not None:
        return {}
    answer = interrupt(
        {
            "type": "direction",
            "question": DIRECTION_QUESTION,
            "source_title": state.get("source_title"),
        }
    )
    return {"author_direction": answer or ""}
