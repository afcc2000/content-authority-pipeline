"""Porta `StructuredLLM` e sua implementação com LangChain."""

from typing import Protocol, TypeVar, cast

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class StructuredLLM(Protocol):
    """Interface que os nós usam para pedir uma saída estruturada a um LLM."""

    def generate(self, schema: type[T], system: str, user: str) -> T:
        """Gera um objeto do tipo `schema` a partir dos prompts de sistema e de usuário."""
        ...


class LLMConfigError(RuntimeError):
    """O LLM não pôde ser criado (modelo não definido, provedor inválido, chave ausente)."""


class LangChainStructuredLLM:
    """Implementação de `StructuredLLM` com `init_chat_model` e `with_structured_output`."""

    def __init__(self, model: str | None) -> None:
        """Cria o modelo de chat.

        Args:
            model: String "provedor:modelo" (ex.: "openai:<modelo>"), vinda de `LLM_MODEL`.

        Raises:
            LLMConfigError: Se `model` estiver vazio ou o LangChain não conseguir criar o modelo.
        """
        if not model:
            raise LLMConfigError(
                'LLM_MODEL não definido. Configure no .env, ex.: LLM_MODEL="openai:<modelo>".'
            )
        try:
            self._model = init_chat_model(model)
        except Exception as exc:
            raise LLMConfigError(f"Não foi possível criar o LLM '{model}': {exc}") from exc

    def generate(self, schema: type[T], system: str, user: str) -> T:
        """Chama o LLM e devolve a resposta validada no formato de `schema`.

        Args:
            schema: Modelo Pydantic esperado na resposta.
            system: Prompt de sistema (instruções).
            user: Mensagem do usuário (dados da tarefa).

        Returns:
            Uma instância de `schema`.
        """
        structured = self._model.with_structured_output(schema)
        result = structured.invoke([SystemMessage(system), HumanMessage(user)])
        return cast(T, result)
