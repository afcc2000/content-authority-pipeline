r"""Nó `approval`: o autor aceita, edita ou rejeita (com feedback) o artigo.

O nó devolve um `Command`, que atualiza o estado E diz para onde ir: não há função de
rota separada. Respostas aceitas no `Command(resume=...)`:

    "accept" ou {"action": "accept"}
    {"action": "edit", "article_markdown": "# Título\n\n..."}
    {"action": "reject", "feedback": "O que mudar."}
"""

import re
from typing import Literal

from langgraph.types import Command, interrupt

from content_pipeline.deps import Deps
from content_pipeline.models import Article
from content_pipeline.state import PipelineState

_SUBTITLE = re.compile(r"^\*(?!\*)(.+?)\*$")


def article_from_markdown(markdown: str, fallback: Article) -> Article:
    """Converte o Markdown editado pelo autor em `Article`.

    A primeira linha "# X" vira o título e uma linha "*Y*" logo depois vira o subtítulo; o
    resto é o corpo. Sem "# " no início, título e subtítulo vêm de `fallback` e todo o texto
    vira corpo. As tags sempre vêm de `fallback`.
    """
    lines = markdown.strip().splitlines()
    if not lines or not lines[0].startswith("# "):
        return fallback.model_copy(update={"body_markdown": markdown.strip()})

    title = lines[0][2:].strip() or fallback.title
    rest = lines[1:]
    while rest and not rest[0].strip():
        rest = rest[1:]

    subtitle = None
    if rest and (match := _SUBTITLE.match(rest[0].strip())):
        subtitle = match.group(1).strip()
        rest = rest[1:]

    body = "\n".join(rest).strip()
    return fallback.model_copy(update={"title": title, "subtitle": subtitle, "body_markdown": body})


def make_approval(deps: Deps):
    """Cria o nó `approval`."""
    max_rewrites = deps.settings.max_rewrites

    def approval(
        state: PipelineState,
    ) -> Command[Literal["design_carousel", "write_article", "export_report"]]:
        article = state["article"]
        rewrites = state.get("rewrites") or 0
        can_reject = rewrites < max_rewrites

        response = interrupt(
            {
                "type": "approval",
                "article_markdown": article.to_markdown(),
                "rewrites": rewrites,
                "can_reject": can_reject,
            }
        )
        if isinstance(response, str):
            response = {"action": response}
        action = response.get("action")

        if action == "accept":
            return Command(goto="design_carousel", update={"decision": "accept"})

        if action == "edit":
            markdown = (response.get("article_markdown") or "").strip()
            if not markdown:
                raise ValueError('A ação "edit" exige "article_markdown" com o artigo editado.')
            edited = article_from_markdown(markdown, article)
            return Command(goto="design_carousel", update={"decision": "edit", "article": edited})

        if action == "reject":
            feedback = (response.get("feedback") or "").strip()
            if not feedback:
                raise ValueError('A ação "reject" exige "feedback" dizendo o que mudar.')
            if can_reject:
                return Command(
                    goto="write_article",
                    update={"decision": "reject", "feedback": feedback, "rewrites": rewrites + 1},
                )
            warning = f"Artigo rejeitado após o limite de {max_rewrites} reescrita(s)."
            return Command(
                goto="export_report",
                update={
                    "decision": "reject",
                    "feedback": feedback,
                    "warnings": [*(state.get("warnings") or []), warning],
                },
            )

        raise ValueError(f"Ação de aprovação desconhecida: {action!r}.")

    return approval
