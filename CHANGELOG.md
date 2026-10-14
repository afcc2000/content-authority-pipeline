# Changelog

Todas as mudanças relevantes deste projeto são registradas aqui.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto usa
[Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2026-10-14

Primeira versão: entrega do miniprojeto do Microcurso 4 (AKCIT · Engenharia de Software com IA).

### Adicionado

- **Pipeline em LangGraph** do link ao carrossel: `research` → `ingest` → `ask_direction` →
  `analyze` → `interview` → `write_article` ⇄ `approval` → `design_carousel` → `export`.
- **Entrada por link, arquivo ou tema** (`--url`, `--file`, `--topic`). A leitura de links usa
  httpx + trafilatura; o Tavily é opcional para leitura e busca por tema e serve de fallback
  quando um site bloqueia a leitura (HTTP 403).
- **Direção do autor antes da análise:** uma pergunta aberta que orienta o ângulo e as perguntas
  do briefing e, no artigo, prevalece sobre o ângulo sugerido. A relevância é julgada só pela
  fonte.
- **Análise de relevância** contra os temas do autor; fonte irrelevante encerra com um relatório
  do motivo.
- **Entrevista com `interrupt`**, uma pergunta do briefing por vez, com checkpointer; Enter
  pula a pergunta sem que o artigo invente a resposta ou comente o pulo.
- **Artigo de autoridade em Markdown** com aprovação humana: `accept`, `edit` (no próprio
  arquivo) ou `reject` com feedback e reescrita, até um limite configurável.
- **Subgrafo do carrossel** (plan → validate → render) com validadores determinísticos: número
  de slides, tamanho das headlines, tamanho da legenda, hashtags, chamada e link para o blog
  (`BLOG_URL`). Se a validação falha, o LLM corrige a partir da lista de erros.
- **Geração de imagens plugável** (`ImageGenerator`): adaptador falso para testes e `--dry-run`,
  e adaptador Higgsfield (Soul, 3:4) com timeout, limite de consultas e cancelamento. Uma falha
  de imagem vira aviso e o pipeline segue.
- **Saída por execução** em `outputs/AAAA-MM-DD-<slug>/`: `article.md`, `slides.json`,
  `caption.txt`, `report.md` e `images/`.
- **CLI com Typer:** `run` (com `--dry-run` opcional) e `demo` (sempre em dry-run, com a
  amostra de `samples/`).
- **Prompts editáveis** em `prompts/*.md`, publicados como templates (`context.md` e
  `carousel_brand.md` com campos `<...>` a preencher).
- **Configuração via `.env`** com pydantic-settings e `.env.example` sem valores.
- **Observabilidade** com traces no LangSmith.
- **Testes sem chave de API** (pytest), com LLM e gerador de imagem falsos
  (`tests/fakes.py`), e um teste de integração real marcado com `@pytest.mark.integration`.
- **Qualidade:** ruff (lint, formatação e docstrings no padrão Google), `requirements.txt`
  exportado do `uv.lock` e `Makefile` com atalhos.
- **Documentação:** README com instalação, uso, arquitetura (diagramas Mermaid), demonstração
  (GIF, exemplo real em `examples/devday-2026/` e trace do LangSmith), uso de IA, limitações e
  créditos; log detalhado em `docs/uso-de-ia.md`.

### Limitações conhecidas

- As imagens saem em 3:4, porque os modelos Soul recusam 4:5.
- O modelo de imagem às vezes desenha pseudo-letras, mesmo com o prompt pedindo imagens sem
  texto.
- O checkpoint fica em memória: uma execução interrompida não pode ser retomada.
- A avaliação no LangSmith (dataset e avaliadores) ficou para uma próxima versão.

[1.0.0]: https://github.com/afcc2000/content-authority-pipeline/releases/tag/v1.0.0
