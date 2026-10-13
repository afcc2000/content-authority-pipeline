"""Helper comum aos nós que pedem uma saída estruturada ao LLM."""

from collections.abc import Sequence
from typing import TypeVar

from pydantic import BaseModel

from content_pipeline.deps import Deps
from content_pipeline.prompts import compose

T = TypeVar("T", bound=BaseModel)


def ask(deps: Deps, schema: type[T], prompt_names: Sequence[str], user: str) -> T:
    """Compõe o system prompt a partir de prompts/ e chama o LLM estruturado.

    Args:
        deps: Dependências do grafo (usa `settings.prompts_dir` e `llm`).
        schema: Modelo Pydantic esperado na resposta.
        prompt_names: Nomes dos prompts que formam o system, na ordem (ex.: "context", "analyze").
        user: Mensagem do usuário com os dados da tarefa.

    Returns:
        Uma instância de `schema`.
    """
    system = compose(deps.settings.prompts_dir, *prompt_names)
    return deps.llm.generate(schema, system, user)
