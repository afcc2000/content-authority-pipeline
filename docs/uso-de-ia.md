# Log de uso da IA

Registro de cada interação relevante com IA generativa no projeto: o que pedi, o que aceitei, o
que mudei ou rejeitei (e por quê) e como validei. Alimenta a seção "Como a IA Acelerou Este
Projeto" do README e a postagem do fórum (itens c, d e e). Contexto em [projeto](projeto.md),
etapas do curso em [roteiro](roteiro.md) e ordem de construção em [tickets](tickets.md).

| Data | Etapa | Ferramenta/modelo | O que pedi (prompt resumido) | O que aceitei | O que mudei ou rejeitei, e por quê | Como validei |
|---|---|---|---|---|---|---|
| aprox. 2026-10 | U2 §2.1 Ideação | Claude | Buscar referências de projeto mais ambiciosas que um RAG básico | Fontes: repositórios da LangChain, lista awesome-LangGraph, docs.langchain.com | — | — |
| aprox. 2026-10 | U2 §2.1 Ideação | Claude | Comparar as ideias encontradas e escolher finalistas | Dois finalistas: simulador de usuários com `openevals` e social-media-agent | Simulador descartado como projeto principal; ficou como extensão | — |
| aprox. 2026-10 | U2 §2.1.1 Seleção do MVP | Claude | Avaliar uma ideia própria (nascida para psicologia) e torná-la agnóstica de domínio | Ideia final: o pipeline do documento do projeto, agnóstico de domínio | Domínio específico (psicologia) saiu do código e foi para `prompts/*.md` | Apliquei os 5 critérios do §2.1.1 (roteiro, Passo 1) |
| aprox. 2026-10 | U2 §2.1 Referências | Claude | Levantar o que aproveitar do social-media-agent | Prompts como componentes editáveis, verificação de relevância com relatório, aprovação accept/edit/reject | DeepWiki marcado como fonte secundária, usado porque as páginas de árvore de arquivos do GitHub estavam bloqueadas | README do repositório como fonte primária |
| aprox. 2026-10 | U2 Revisão das orientações | Claude | Revisar as orientações iniciais à luz do ebook original da U2 | Orientações ajustadas ao texto do ebook | As primeiras orientações vinham da nota parafraseada, não do ebook original | Leitura do ebook original da U2 |
| 2026-10-09 | U2 §2.2 Arquitetura | Claude (Cowork) | Prompt COER pedindo diagramas Mermaid e estrutura de pastas | Fluxo e componentes | Validação movida para antes da geração de imagem | Renderizei os diagramas no Mermaid CLI |
| 2026-10-09 | U2 §2.2.2 Dependências | Claude (Cowork) | Lista de dependências com versões | Lista e pyproject | — | Conferi versões e `Requires-Python` no PyPI; instalei e testei imports |
| 2026-10-10 | U2 PoC | Claude | Gerar uma PoC completa do pipeline em uma sessão | Estrutura, contratos e decisões da PoC (25 testes passando, ruff limpo) | Gerei uma PoC completa com IA em uma sessão; funcionou, mas o histórico ficaria sem evolução e eu não dominava cada parte. Descartei e reconstruí em tickets, usando a PoC como especificação | Testes e ruff da PoC; plano de 28 tickets em [tickets](tickets.md) |
| 2026-10-10 | U2 T01 Estrutura inicial | Claude Code (Opus 5.5) | Implementar o T01: `.gitignore`, `pyproject.toml`, LICENSE MIT, README, teste de fumaça, `uv add --dev` | Arquivos do ticket; o `uv add --dev` criou `[dependency-groups] dev` | Desvios aprovados: o ruff 0.17 formata blocos Python dentro de `.md` e reprovava os esboços de `docs/`, então entrou `extend-exclude = ["docs"]`; `docs/` ficou no `.gitignore` só até o T02; `authors` com o nome completo | `uv run pytest` (1 passou), `ruff check`, `ruff format --check`, `git status` sem `.venv` |
| 2026-10-10 | U2 T02 Documentação | Claude Code (Opus 5.5) + subagente | Atualizar projeto e roteiro para a v1.2 (OpenAI, `uv`, tickets como ordem de execução), trocar os links do Obsidian e criar o log e o `CLAUDE.md` | Edições das tabelas do T02 | O subagente não citou a OpenAI no roteiro e eu acrescentei no Passo 13; ele também trocou os comandos por `uv run`, o que mantive | Buscas por `pip install`, `pip freeze`, `anthropic`, `openevals` e pela versão 1.2; `pytest` e `ruff` verdes |

> **Nota [A verificar]:** as linhas com data "aprox." reconstroem a ideação de memória. Confirme as datas (e a ferramenta/modelo exata) no histórico das conversas e ajuste antes de usar o log no README e no fórum.
