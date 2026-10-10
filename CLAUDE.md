# Contexto
Miniprojeto do Microcurso 4 (AKCIT). Pipeline LangGraph: link → entrevista com o autor
(interrupt) → artigo de autoridade (accept/edit/reject) → carrossel de Instagram + legenda.
O quê e porquê: docs/projeto.md. Etapas do curso: docs/roteiro.md. Ordem de construção: docs/tickets.md.

# Stack e comandos
Python 3.12 + uv. Testes: `uv run pytest` (sem chave de API). Lint: `uv run ruff check .`.
LangChain 1.4 / LangGraph 1.2: use `langchain.agents.create_agent`; nada de `create_react_agent`
nem `LLMChain`. Fakes não suportam `with_structured_output`: use tests/fakes.py.

# Como trabalhar comigo
- Um ticket por vez, só os arquivos do ticket. Explique o porquê; sou iniciante-intermediário.
- Não invente APIs; sinalize incertezas. Nada de chaves no código.
- Conventional Commits em português. No fim, proponha a linha de docs/uso-de-ia.md.
