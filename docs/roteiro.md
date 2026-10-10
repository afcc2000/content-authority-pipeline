---
titulo: Roteiro passo a passo do miniprojeto (Microcurso 4)
curso: AKCIT · Engenharia de Software com IA · Microcurso 4
projeto: content-authority-pipeline
versao_do_documento: 1.2 (2026-10-10)
documento_irmao: "[projeto](projeto.md)"
fontes: Ebooks M4 Unidades 2 a 5 (vault Bedrock/Microcurso 4); apoio do Microcurso 1 (Panorama do SDLC com IA), Microcurso 2 Unidade 1 (fundamentos de engenharia de prompts) e Microcurso 3 (Prompt Engineering aplicado ao SDLC)
---

# Roteiro passo a passo do miniprojeto

> **Como usar.** Siga os passos na ordem. Cada passo diz **o que o material pede** (com a seção do ebook), **o que fazer no nosso projeto**, o **prompt sugerido** no padrão do curso, os **comandos**, o **entregável** e a **mensagem de commit**. O "porquê" das decisões técnicas está no documento irmão **[projeto](projeto.md)**.
>
> **Legenda.** **[Material]** é exigência ou orientação dos ebooks. **[Decisão]** é escolha nossa. **[Verificado]** foi conferido ou executado. **[A verificar]** ainda não foi confirmado.
>
> **Comandos.** Escritos para **Windows (PowerShell)**, que é a sua máquina, com a versão para Git Bash/Linux quando muda.
>
> **Ordem de execução.** A ordem de execução e os commits estão em [tickets](tickets.md) (`docs/tickets.md`). Este roteiro mapeia o que o curso pede; quando os dois divergirem na forma, vale o ticket.

---

## 0. Visão geral

| Fase | Unidade do M4 | Fase do SDLC (Microcurso 1) | Horas sugeridas **[Decisão]** | Status |
|---|---|---|---|---|
| Fundamentos | U1 | — | — | ⚠️ Ebook ainda não está no vault |
| Ideação, arquitetura e Git | U2 | Requisitos + Arquitetura | 4 h | Em andamento (T00 e T01 feitos) |
| Núcleo da aplicação | U3 | Desenvolvimento | 12 h | A fazer |
| Testes, refatoração, docs | U4 | Teste e validação | 8 h | A fazer |
| Empacotamento e submissão | U5 | Manutenção e evolução (README, próximos passos) | 4 h | A fazer |
| Fórum | Encerramento U5 | — | 2 h | A fazer |

O total fica em 30 h, o tamanho de referência do laboratório **[Material, U2 §2.1.1]**. A coluna "Status" acompanha os tickets (ver a nota "Ordem de execução" no início deste roteiro).

---

## T. Práticas transversais (valem para todos os passos)

### T1. Log de uso da IA

Desde o Passo 6 (no nosso projeto, desde o T02), mantenha [docs/uso-de-ia.md](uso-de-ia.md) no repositório. A cada interação relevante com a IA, registre uma linha na tabela do log: data, etapa, ferramenta/modelo, prompt resumido, o que aceitou, o que mudou ou rejeitou e por quê, e como validou.

O log não começa vazio: ele já parte do histórico da ideação e das decisões de arquitetura e dependências, copiado para `docs/uso-de-ia.md` no T02 (o documento do projeto, §11, agora só aponta para ele).

**Por quê:** a U5 §5.2.1 pede uma seção no README sobre o papel da IA (desafios superados, ganhos de produtividade, decisões influenciadas, lições aprendidas), e o fórum pede exatamente isso nos itens (c), (d) e (e). Reconstruir isso de memória no fim é o que costuma dar errado.

### T2. Como escrever os prompts

O padrão usado em todos os exemplos dos ebooks do M4 é **Contexto / Objetivo / Estilo / Resposta** (chamado aqui de **COER**). Os microcursos anteriores complementam:

- **Elementos de um prompt [Microcurso 3, U1 §1.1]:** persona (papel), tarefa (instrução com verbo de ação), contexto, exemplos, formato de resposta e restrições. Prompts tratados como artefatos versionados ("promptware").
- **Especificidade [Microcurso 2, U1 §1.3]:** dizer nome da função, comportamento esperado, restrições e formato de documentação dá respostas muito melhores do que um pedido vago. Em depuração, cole o erro e o código exatos, não um resumo.
- **Técnicas [Microcurso 3, U1 §1.2]:** zero-shot para tarefas simples; few-shot quando quiser um formato específico (ex.: estilo de teste ou de docstring); Chain-of-Thought para depuração e lógica; Skeleton-of-Thought quando a saída é longa (README, artigo): primeiro o esqueleto, depois as partes.
- **Refinamento iterativo [Microcurso 3, U2]:** se a primeira resposta não serviu, refine o prompt com o que faltou, em vez de aceitar uma resposta ruim.

### T3. Revisão crítica de toda sugestão da IA

**[Material, U3 §3.3.1]** Antes de aceitar qualquer código gerado, passe por estes cinco pontos:

- [ ] **Leitura e compreensão:** entendo cada linha? Conseguiria escrever isso sozinho?
- [ ] **Lógica e requisitos:** resolve o problema que eu pedi, no meu contexto, ou é genérico?
- [ ] **Segurança:** expõe chave? Trata entrada não confiável? Usa biblioteca ou API desatualizada? (Referência: OWASP Top 10 para LLM.)
- [ ] **Padrões:** PEP 8, nomes claros, responsabilidades separadas?
- [ ] **Teste imediato:** rodei? Os testes passam?

Para avaliar respostas que não são código (README, prompts, artigo gerado), use os três critérios do **Microcurso 3, U3 §3.2**: **coerência** (lógica e sem contradições), **pertinência** (responde ao que foi pedido, não só às palavras-chave) e **alinhamento** (atende ao objetivo real e às restrições implícitas).

---

## Unidade 1 — (ebook ainda não disponível no vault)

O vault tem a nota `Microcurso 4.md` só com o título "Unidade 1", sem conteúdo. Quando o ebook estiver disponível, confira se ele traz algum requisito que não aparece nas Unidades 2 a 5 (por exemplo, ferramentas obrigatórias ou critérios de avaliação) e ajuste este roteiro.

---

## Unidade 2 — Ideação, Arquitetura Mínima e Git/GitHub

### Passo 1 — Validar o MVP (§2.1) ✅ decidido

**Material:** escolher um MVP pelos cinco critérios do §2.1.1: escopo limitado e claro (cerca de 30 h), potencial de uso da IA em várias etapas, familiaridade tecnológica, relevância pessoal e testabilidade. A Tabela 2 traz quatro projetos de referência; um deles é um chatbot RAG com LangChain, o que mostra que a stack LangChain é bem-vinda.

**No nosso projeto:**

| Critério | Avaliação |
|---|---|
| Escopo limitado e claro | Atendido com o corte de escopo (documento do projeto, §2.1) e a definição de pronto |
| Potencial de uso da IA | Atendido duas vezes: a IA ajuda a construir e também é o produto (LLMs no pipeline) |
| Familiaridade tecnológica | **Parcial.** Python é familiar; LangGraph e LangSmith estão sendo estudados em paralelo. Mitigação: fluxo explícito, MVP pequeno, testes com fakes |
| Relevância pessoal | Atendido: uso real para produção de conteúdo |
| Testabilidade | Atendido: validadores determinísticos, fakes para LLM e imagem, respostas roteirizadas |

**Entregável:** o parágrafo do MVP (documento do projeto, §2) vira a descrição do README no Passo 6.

### Passo 2 — Arquitetura mínima (§2.2.1) ✅ decidido

**Material:** usar a IA como "arquiteto virtual" para gerar diagramas em linguagem de texto (Mermaid ou PlantUML) e sugerir a estrutura de módulos e pastas, com um prompt de contexto e objetivo claros.

**No nosso projeto:** os dois diagramas Mermaid e a estrutura de pastas já existem (documento do projeto, §3 e §7) e foram validados no Mermaid CLI. Falta só levá-los para o repositório no Passo 6 (seção "Arquitetura" do README).

**Prompt usado (registrar no log):**

```
Contexto: Estou fazendo um miniprojeto de um curso de Engenharia de Software com IA.
É um pipeline multiagente em Python (LangChain v1 + LangGraph v1 + LangSmith) que recebe
o link de um conteúdo, verifica a relevância, entrevista o autor (interrupt), escreve um
artigo de autoridade em Markdown, pede aprovação humana (accept/edit/reject) e depois gera
um carrossel de Instagram com legenda, usando uma interface plugável de geração de imagem
(Higgsfield, outro modelo ou um fake para testes). Há modo dry-run. O prazo é de cerca de 30h.
Objetivo: Propor a arquitetura mínima do MVP: (1) diagrama do fluxo do grafo,
(2) diagrama de componentes por camadas, (3) estrutura de pastas.
Estilo: Mermaid válido (flowchart). Nós com os mesmos nomes das funções em snake_case.
No máximo ~15 nós por diagrama. Sem camadas que o MVP não precise.
Resposta: Dois blocos mermaid, uma árvore de pastas e uma justificativa
de uma linha para cada decisão não óbvia.
```

**O que a revisão mudou (bom exemplo para o fórum, item e):** a primeira versão validava o carrossel depois de gerar as imagens; a revisão moveu a validação para antes, para não pagar por imagens descartadas.

### Passo 3 — Dependências e tecnologias (§2.2.2) ✅ verificado

**Material:** pedir à IA as bibliotecas necessárias e um arquivo de dependências com versões.

**No nosso projeto:** a lista e o `pyproject.toml` estão no documento do projeto, §6, com versões conferidas no PyPI em 2026-10-09 e instalação testada.

**Prompt (padrão do ebook adaptado):**

```
Contexto: Estou construindo em Python um pipeline com LangGraph v1, LangChain v1 e LangSmith.
Preciso de: chamada a LLM com saída estruturada (Pydantic), configuração por .env,
CLI, download e extração de texto de páginas web, testes com pytest e lint/format.
Objetivo: Liste as bibliotecas essenciais e gere um pyproject.toml (layout src/,
gerenciado com uv, grupo de dependências "dev", script de console "content-pipeline").
Estilo: Apenas o essencial. Limites de versão no formato ">=X.Y,<próxima major".
Resposta: Apenas o pyproject.toml.
```

**Cuidado que vale registrar no log:** o próprio ebook pede "as versões mais recentes", mas um modelo de linguagem não sabe a versão de hoje e pode inventar ou sugerir versões antigas. Sempre confira no PyPI (o comando abaixo só consulta, não instala nada; no projeto, a instalação é com `uv add`):

```powershell
pip index versions langgraph
pip index versions langchain
```

### Passo 4 — Preparar o ambiente local **[Decisão]**

O ebook assume esse passo (terminal do VS Code ou Cursor, U2 §2.3.1). Faça uma vez:

No nosso projeto, este passo é o **T00** e o começo do **T01** ([tickets](tickets.md)).

1. Instale o **uv** (ele gerencia o Python 3.12, o ambiente virtual e o lockfile), o **Git** e, opcionalmente, o **GitHub CLI** (`gh`), que facilita criar o repositório e a release.
2. Crie a pasta do projeto **fora do OneDrive e do vault**: `C:\Users\afcc2\dev\content-authority-pipeline`. O OneDrive sincroniza `.venv` e `.git` e costuma travar arquivos.
3. Fixe a versão do Python e crie o ambiente:

```powershell
cd C:\Users\afcc2\dev\content-authority-pipeline
uv python pin 3.12
uv sync
```

O `uv sync` cria o `.venv` e instala o que está no `pyproject.toml` e no `uv.lock`. Não é preciso ativar o ambiente: os comandos rodam com `uv run` (por exemplo, `uv run pytest`). Os comandos são os mesmos no PowerShell e no Git Bash/Linux.

### Passo 5 — `.gitignore` antes de tudo (§2.3.2)

**Material:** o `.gitignore` precisa existir **antes** do primeiro `git add .`, para não versionar ambiente virtual, cache ou credenciais. O ebook sugere pedir à IA, organizado por tecnologia.

**Prompt (padrão do ebook adaptado):**

```
Contexto: Projeto Python 3.12 com layout src/, ambiente virtual .venv, pytest, ruff,
VS Code/Cursor no Windows. Gera saídas em outputs/ e usa .env para chaves.
O arquivo .env.example (sem valores) deve ser versionado.
Objetivo: Gere um .gitignore abrangente.
Estilo: Seções por tecnologia, com comentários.
Resposta: Apenas o conteúdo do .gitignore.
```

**Resultado esperado (revisado):**

```gitignore
# Python
__pycache__/
*.py[cod]
build/
dist/
*.egg-info/

# Ambientes virtuais
.venv/
venv/

# Testes e ferramentas
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/

# Variáveis de ambiente (segredos)
.env
.env.*
!.env.example

# Saídas do pipeline
outputs/

# IDEs
.vscode/
.idea/
.history/

# Sistema operacional
.DS_Store
Thumbs.db
```

**Pegadinha (registre no log, é um ótimo exemplo de revisão crítica):** o `.gitignore` de exemplo do ebook tem a linha `.env.*`, que também ignora o `.env.example`. A linha `!.env.example` desfaz isso para esse arquivo.

### Passo 6 — Esqueleto mínimo do projeto **[Decisão]**

Crie só o suficiente para o primeiro commit fazer sentido e para o `pytest` rodar. No nosso projeto, o esqueleto foi **dividido em tickets** ([tickets](tickets.md)), para cada commit ter uma mudança que dá para explicar em uma frase:

| Ticket | O que entra |
|---|---|
| T01 · Estrutura e setup | `.gitignore`, `.python-version`, `LICENSE` (MIT), `README.md` (título, parágrafo do MVP, "Em construção"), `pyproject.toml` sem dependências, `uv.lock`, `src/content_pipeline/__init__.py`, `tests/test_smoke.py` |
| T02 · Documentação | `docs/projeto.md`, `docs/roteiro.md`, `docs/tickets.md`, `docs/uso-de-ia.md` (log com as linhas da ideação e dos Passos 2 e 3) e `CLAUDE.md` |
| T03 · Configuração | `.env.example` (documento do projeto, §6.2) |
| T05 · Prompts | Modelos de `prompts/context.md` e `prompts/carousel_brand.md` (documento do projeto, §15.2 e §15.3) |
| T16 e T17 · Texto de exemplo e insumos | `samples/sample_input.md` provisório no T16; no T17, o texto real (documento do projeto, §15.4) e os insumos de `prompts/` preenchidos |

Ao copiar os documentos para `docs/` (T02), troque os links do Obsidian por links Markdown relativos (`[projeto](projeto.md)`, `[roteiro](roteiro.md)`, `[tickets](tickets.md)`). O GitHub não entende a sintaxe `[[...]]`.

Verifique:

```powershell
uv run pytest
```

### Passo 7 — Repositório local e primeiro commit (§2.3.1)

```powershell
git init
git status          # CONFIRA: .venv, .env e outputs NÃO podem aparecer na lista
git add .
git commit -m "feat: estrutura inicial do projeto e setup básico"
```

A mensagem é a mesma do ebook. Se `git status` mostrar `.venv` ou `.env`, pare e corrija o `.gitignore` antes do `add`.

No nosso projeto, este commit é o **T01**: o `git add .` acontece com os arquivos de estrutura e setup, **sem a pasta `docs/`**, que entra no commit seguinte (T02).

### Passo 8 — Repositório remoto no GitHub (§2.3.1)

**Material:** criar um repositório **vazio** no GitHub e conectar.

1. No GitHub (conta `afcc2000`), crie `content-authority-pipeline` como **público** e **sem** README, `.gitignore` ou licença (já temos localmente; criar lá gera conflito no primeiro push).
2. Conecte e envie:

```powershell
git remote add origin https://github.com/afcc2000/content-authority-pipeline.git
git branch -M main
git push -u origin main
```

Alternativa com o GitHub CLI, que faz os três passos de uma vez: `gh repo create afcc2000/content-authority-pipeline --public --source . --remote origin --push`.

### Passo 9 — Plano de commits (§2.3.3)

**Material:** Conventional Commits (`<tipo>[escopo]: <descrição>`, tipos `feat`, `fix`, `docs`, `chore`, `refactor`, `test`). A U2 §2.3.4 recomenda de 5 a 10 commits significativos; a U5 §5.3.1 exige pelo menos 5. O ebook sugere pedir a mensagem à IA depois do `git add`:

```
Contexto: Fiz alterações em <arquivos>. <O que mudou e por quê>.
Objetivo: Gere uma mensagem de commit seguindo o padrão Conventional Commits.
Estilo: Use o tipo e o escopo adequados; descrição no imperativo, em português.
Resposta: Apenas a mensagem de commit.
```

**Plano [Decisão]:** o plano de commits é o mapa de tickets ([tickets](tickets.md), seção "Mapa dos tickets"), com 28 commits, cada um com a mensagem indicada no seu ticket.

### Passo 10 — Ler o checklist de submissão agora (§2.3.4)

Leia o checklist consolidado do Passo 30 antes de começar a U3. Saber desde já o que será cobrado (README, testes, dependências, nenhuma chave no histórico) evita retrabalho.

No nosso projeto, esta leitura é feita no **T00**, antes do primeiro commit.

---

## Unidade 3 — Implementação Guiada (Parte 1): Núcleo da Aplicação

**Material, visão geral:** construir o núcleo deixando explícito como os dados entram, como são processados e como saem (§3.1); integrar a API de LLM tratando autenticação, formato de mensagens, erros e limites (§3.1.2); usar o assistente para esqueletos e docstrings (§3.2); revisar criticamente tudo que a IA sugerir e depurar pedindo explicação, não só correção (§3.3).

**Ordem de implementação [Decisão]:** de dentro para fora. Primeiro o que não depende de nada (modelos, prompts), depois o que chama serviços (LLM, fetcher), depois os nós, o grafo e por último a CLI. Faça um commit ao fim de cada ticket. Os testes de cada peça entram no mesmo ticket da peça; a U4 aprofunda.

**Correspondência com os tickets** ([tickets](tickets.md)). Os commits indicados nos passos abaixo são os do curso; os que valem são os dos tickets:

| Passo | Ticket(s) |
|---|---|
| 11 | T03 e T04 |
| 12 | T05 |
| 13 | T06 |
| 14 | T07 e T09 |
| 15 | T09 a T12 |
| 16 | T08, T13 e T14 |
| 17 | T15, T16 e T18 |
| 18 e 19 | Prompt-base e definição de pronto (início de [tickets](tickets.md)) e T18 |

### Passo 11 — Modelos de entrada e saída (§3.1.1)

**Material:** usar a IA para gerar os modelos Pydantic a partir de uma descrição dos campos, com tipagem e docstrings.

**No nosso projeto:** `models.py` (`Briefing`, `Article`, `Slide`, `CarouselPlan`), `state.py` (`PipelineState`) e `config.py` (`Settings` com `pydantic-settings`). Esboço no documento do projeto, §5.1.

**Prompt (padrão do ebook adaptado):**

```
Contexto: Pipeline LangGraph que gera um artigo e um carrossel de Instagram a partir de
um conteúdo. Preciso dos modelos Pydantic v2 das saídas estruturadas dos LLMs.
Objetivo: Crie os modelos Briefing, Article, Slide e CarouselPlan com estes campos:
<colar os campos do documento do projeto, §5.1>. Crie também um TypedDict PipelineState
para o estado do grafo e uma classe Settings (pydantic-settings) que leia o .env
com LLM_MODEL, IMAGE_PROVIDER e os limites do carrossel.
Estilo: Tipagem estática, Field com description em cada campo (o LLM lê essas descrições),
docstrings no formato Google, Pydantic v2 (nada de class Config / orm_mode).
Resposta: Apenas o código Python, um bloco por arquivo.
```

**Revisão específica:** o exemplo do ebook usa `class Config` e `datetime.utcnow`, que são estilo antigo (Pydantic v1 e uma função depreciada no Python 3.12). Se a IA repetir esse padrão, corrija para `model_config = ConfigDict(...)` e `datetime.now(timezone.utc)`. Bom item para o log.

**Commit:** `feat(models): adiciona modelos Pydantic e estado do grafo`

### Passo 12 — Prompts editáveis

**No nosso projeto:** crie `prompts/context.md`, `analyze.md`, `article_style.md`, `carousel_brand.md` e `carousel_rules.md`, e o carregador `prompts.py` (lê o arquivo, compõe por nó, falha com mensagem clara se faltar arquivo).

Escreva os prompts com os elementos do Microcurso 3 (persona, tarefa, contexto, exemplos, formato, restrições). No `article_style.md`, inclua um ou dois exemplos curtos de abertura de artigo que você considera bons (few-shot). No `carousel_brand.md`, descreva a identidade visual: paleta, tipografia, tom, estilo de imagem e o que evitar.

**Commit:** `feat(prompts): adiciona prompts editáveis e carregador`

### Passo 13 — Integração com o LLM (§3.1.2)

**Material:** a IA gera o código de integração; a chave vem de variável de ambiente; trate erros básicos.

**No nosso projeto:** `llm.py` com a classe que implementa a porta `StructuredLLM` (documento do projeto, §5.3): usa `init_chat_model(settings.llm_model)` e `with_structured_output(schema)`. O provedor escolhido é a **OpenAI** (pacote `langchain-openai`, adicionado com `uv add` no T06), com `LLM_MODEL=openai:<nome-do-modelo>` e `OPENAI_API_KEY` no `.env`.

**Prompt (padrão do ebook adaptado):**

```
Contexto: Projeto Python com LangChain 1.4 (pacotes langchain e langchain-core).
Os nós do meu grafo dependem desta interface:
    class StructuredLLM(Protocol):
        def generate(self, schema: type[T], system: str, user: str) -> T: ...
Objetivo: Implemente LangChainStructuredLLM, que cria o modelo com
langchain.chat_models.init_chat_model a partir de uma string "provedor:modelo"
e devolve o objeto Pydantic usando with_structured_output(schema).
Trate erro de autenticação e de validação com mensagens claras.
Estilo: Tipagem estática, docstrings Google, a chave NUNCA no código (vem do ambiente).
Não use APIs anteriores ao LangChain v1 (LLMChain, create_react_agent).
Resposta: Apenas o código do arquivo llm.py.
```

**Verifique:** com a chave no `.env`, rode uma chamada manual simples (ex.: gerar um `Briefing` de um parágrafo) antes de seguir. Assim você separa problema de integração de problema do grafo.

**Commit:** `feat(llm): adiciona gerador estruturado configurável por .env`

### Passo 14 — Ingestão

**No nosso projeto:** `fetcher.py` (baixa com `httpx`, timeout e limite de tamanho, só `http(s)`; extrai o texto com `trafilatura`) e o nó `ingest` (URL ou arquivo local). Crie `samples/sample_input.md` com um texto de exemplo para rodar offline.

**Segurança (§3.3.1):** o texto baixado é não confiável. Nos prompts dos nós seguintes, coloque-o entre delimitadores (ex.: `<fonte>...</fonte>`) e diga ao modelo que é dado, não instrução (documento do projeto, §5.8).

**Commit:** `feat(ingest): extrai texto de URL ou arquivo local`

### Passo 15 — Nós de análise, entrevista, artigo e aprovação + grafo

**No nosso projeto:** nós `analyze`, `interview`, `write_article` e `approval`, e `graph.py` com `build_graph(deps)` compilado com `InMemorySaver`. Comportamento de cada nó e roteamento no documento do projeto, §4; o padrão de `interrupt` e `Command(resume=...)` em §5.2 (testado).

Cuidados com `interrupt` (repita para o assistente se ele errar):

1. Nada de `try/except` genérico em volta do `interrupt()`.
2. O nó roda de novo do início quando é retomado; nada de efeito colateral caro antes do `interrupt`.
3. Ordem estável dos `interrupt` dentro do nó.

**Prompt de partida para o assistente (Composer do Cursor ou Claude Code, §3.2.1):**

```
Contexto: Leia docs/projeto.md (seções 3, 4 e 5). Os modelos estão em models.py,
o estado em state.py, a porta StructuredLLM em llm.py e os prompts em prompts.py.
Objetivo: Implemente os nós analyze, interview, write_article e approval em
src/content_pipeline/nodes/, e build_graph(deps) em graph.py com InMemorySaver.
interview faz uma pergunta por vez com langgraph.types.interrupt; approval usa interrupt
e devolve Command(goto=..., update=...) para accept/edit/reject (máx. 3 reescritas).
Estilo: Funções pequenas e puras sobre o estado; dependências recebidas por build_graph;
docstrings Google. Não envolva interrupt em try/except.
Resposta: Mostre o diff por arquivo e explique o roteamento antes do código.
```

**Commits:** `feat(graph): adiciona análise, entrevista com interrupt e escrita do artigo` e `feat(graph): adiciona aprovação accept/edit/reject`

### Passo 16 — Subgrafo do carrossel e imagens

**No nosso projeto:** `carousel/planner.py` (`plan_slides`), `carousel/validators.py` (regras do documento do projeto, §5.4), `carousel/subgraph.py` (plan → validate → retry até 2 → render) e `images/base.py`, `images/fake.py`. O adaptador `images/higgsfield.py` pode vir depois, quando a chave e a documentação da API estiverem confirmadas **[A verificar]**.

**Commit:** `feat(carousel): adiciona subgrafo com validação e geração de imagem plugável`

### Passo 17 — Exportação, CLI e primeira execução de ponta a ponta

**No nosso projeto:** `export.py` (grava `article.md`, `slides.json`, `caption.txt` e as imagens em `outputs/<data>-<slug>/`) e `cli.py` (Typer: chama `load_dotenv()`, roda o grafo, mostra cada `interrupt` no terminal, lê a resposta e retoma com `Command(resume=...)`).

Rode o fluxo real com o LLM e imagens fake:

```powershell
uv run content-pipeline run --file samples/sample_input.md --dry-run
```

Depois, com `LANGSMITH_TRACING=true`, abra o projeto no LangSmith e confirme que o trace aparece com um nó por etapa. Isso cumpre o critério 3 da definição de pronto; tire um print para o README.

**Commit:** `feat(cli): adiciona comando run com dry-run e exportação`

### Passo 18 — Esqueletos e docstrings com o assistente (§3.2)

**Material:** usar o Composer do Cursor (edição multiarquivo, com diff para aceitar ou rejeitar) ou equivalente para criar esqueletos, e Copilot/Cursor para gerar docstrings no formato escolhido.

**No nosso projeto:** padronize docstrings no formato **Google** em todas as funções públicas. O Claude Code também faz edição multiarquivo com diff revisável; use o que tiver à mão e registre no log qual ferramenta usou em cada passo (o README pede a lista de ferramentas de IA).

### Passo 19 — Revisão crítica e depuração assistida (§3.3)

Aplique o checklist T3 a cada passo da U3. Pontos de atenção específicos deste projeto:

- **API desatualizada:** assistentes treinados em versões antigas sugerem `create_react_agent`, `LLMChain` ou imports de `langchain.chains`. Confira com a versão instalada.
- **Saída estruturada em teste:** os modelos falsos do LangChain não suportam `with_structured_output` **[Verificado]**; os testes usam a fake própria (`tests/fakes.py`).
- **Segredos:** nenhuma chave em código, teste, exemplo ou print de tela.

**Depuração (§3.3.2):** quando algo falhar, mande o erro completo, o stack trace, o trecho do código e o cenário, e peça a causa antes da correção:

```
Recebi <erro completo + stack trace> ao rodar <comando>, no arquivo <arquivo>, linha <n>.
Código relevante: <trecho>.
Explique a causa raiz provável e como depurar. Só depois sugira uma correção.
```

Essa forma de pedir é Chain-of-Thought aplicado à depuração (Microcurso 3, U1 §1.2.2).

---

## Unidade 4 — Implementação Guiada (Parte 2): Testes, Refatoração e Documentação

### Passo 20 — Testes unitários gerados com IA (§4.1.1)

**Material:** pedir à IA uma suíte pytest descrevendo explicitamente casos válidos, casos de borda e exceções esperadas; revisar nomes e completar cenários do domínio.

**No nosso projeto:** os testes **acompanham cada ticket** (T03 a T16), gerados com o prompt-base de [tickets](tickets.md) a partir dos critérios de aceite de cada ticket. Não há um commit `test: ...` separado para eles; o único commit só de teste é o T19 (TDD vermelho, Passo 21). O prompt abaixo continua valendo como modelo para pedir os testes de uma peça, e a ordem sugerida é: validadores e funções de roteamento, que são puros; depois modelos, carregador de prompts, fetcher (com `httpx.MockTransport`) e o adaptador fake.

**Prompt (padrão do ebook adaptado):**

```
Contexto: Tenho as funções de validação do carrossel abaixo.
<colar carousel/validators.py>
Objetivo: Gere testes pytest para cada regra, incluindo:
- carrossel válido passa sem erros;
- menos e mais slides que o permitido;
- headline acima do limite de caracteres;
- carrossel sem CTA para o blog;
- legenda acima do limite e excesso de hashtags;
- índices fora de sequência.
Estilo: Nomes descritivos (test_<regra>_<cenario>), uma fixture para um carrossel válido,
pytest.mark.parametrize onde houver repetição.
Resposta: Apenas o código de tests/test_validators.py.
```

Crie também `tests/fakes.py`:

```python
class FakeStructuredLLM:
    """Devolve objetos Pydantic pré-definidos, por schema, na ordem das chamadas."""

    def __init__(self, responses: dict[type, list]):
        self.responses = {schema: list(items) for schema, items in responses.items()}
        self.calls: list[tuple[type, str, str]] = []

    def generate(self, schema, system, user):
        self.calls.append((schema, system, user))
        return self.responses[schema].pop(0)
```

**Commit:** nenhum separado; os testes entram no commit de cada ticket (T03 a T16).

### Passo 21 — TDD com IA: red, green, refactor (§4.1.2)

**Material:** red (a IA escreve um teste que falha para uma funcionalidade que ainda não existe), green (a IA escreve o mínimo para passar), refactor (melhora mantendo o teste verde).

**No nosso projeto [Decisão]:** escolha uma regra nova ainda não implementada, por exemplo "a legenda precisa conter o link do blog quando `BLOG_URL` estiver configurado". Faça o ciclo com três prompts e **três commits** (T19, T20 e T21), para o histórico mostrar o TDD:

1. `test(validators): exige link do blog na legenda` (teste falhando)
2. `feat(validators): valida link do blog na legenda` (mínimo para passar)
3. `refactor(validators): simplifica regras de legenda` (mesmo comportamento, código melhor)

Registre os três prompts no log; isso é ouro para o item (e) do fórum.

### Passo 22 — Teste do grafo completo

**No nosso projeto:** o fluxo completo do grafo é testado **incrementalmente do T09 ao T15**: cada ticket que acrescenta um nó acrescenta também os testes do grafo até aquele ponto, gerados com o prompt-base de [tickets](tickets.md). Não há commit `test(graph): ...` separado.

Sem chave de API, com respostas roteirizadas (padrão executado no spike, documento do projeto §5.2):

```python
from langgraph.types import Command

def test_fluxo_completo_com_accept(tmp_path):
    llm = FakeStructuredLLM({Briefing: [briefing_relevante], Article: [artigo],
                             CarouselPlan: [carrossel_valido]})
    graph = build_graph(Deps(llm=llm, images=FakeImageGenerator()))
    config = {"configurable": {"thread_id": "teste-accept"}}

    result = graph.invoke({"source_text": "texto", "output_dir": str(tmp_path)}, config)
    for resposta in ["contribuição 1", "contribuição 2", {"action": "accept"}]:
        assert "__interrupt__" in result
        result = graph.invoke(Command(resume=resposta), config)

    assert "__interrupt__" not in result
    assert (tmp_path / "article.md").exists()
```

Cubra também: `reject` (o artigo é reescrito e o feedback chega ao prompt, o que dá para conferir em `llm.calls`), `edit` (o texto editado é o exportado), fonte irrelevante (encerra sem entrevista) e validação que falha duas vezes.

**Commit:** nenhum separado; os testes do grafo entram nos commits do T09 ao T15.

### Passo 23 — Avaliação no LangSmith (recomendado)

Não é exigência do ebook, mas é o uso natural do LangSmith e reforça o item (e) do fórum. Passos (detalhes no documento do projeto, §5.9):

1. Criar um dataset com 5 a 10 textos de entrada.
2. Função alvo: roda o grafo em `dry-run` com respostas roteirizadas.
3. Avaliadores: os validadores determinísticos e um LLM-as-judge com os critérios coerência, pertinência e alinhamento (Microcurso 3, U3 §3.2). Sem `openevals`: o juiz usa o próprio `StructuredLLM` do projeto, com um modelo Pydantic de notas, e não exige dependência nova (T23).
4. Rodar com `client.evaluate()` e guardar o link do experimento para o README.

Os detalhes da API do SDK para avaliação estão **[A verificar]** na versão instalada antes de codar (o que já foi conferido está no T23).

**Commit:** `feat(evals): adiciona dataset e avaliadores no LangSmith`

### Passo 24 — Refatoração assistida (§4.2)

**Material:** DRY, SOLID, nomes semânticos e modularização, com prompts direcionados; para mudanças maiores, um modelo forte de raciocínio fazendo análise de impacto.

**Onde provavelmente haverá o que refatorar no nosso projeto:**

- **DRY:** a sequência "carregar prompt → montar mensagem → chamar `generate`" vai se repetir em `analyze`, `write_article` e `plan_slides`. Extraia um helper.
- **SRP:** se `cli.py` estiver fazendo laço de interrupts, formatação e gravação, separe.
- **Nomes:** revise nomes genéricos (`data`, `result`, `res`).

**Prompt (padrão do ebook adaptado):**

```
Contexto: Os nós analyze.py, write_article.py e planner.py repetem a lógica de
carregar prompt, montar mensagens e chamar StructuredLLM.generate.
Objetivo: Identifique a duplicação, proponha um helper e refatore os três nós para usá-lo.
Não mude o comportamento externo; os testes atuais devem continuar passando.
Estilo: PEP 8, tipagem estática, docstrings Google.
Resposta: Primeiro a análise da duplicação e do impacto; depois o diff.
```

Rode `uv run pytest` depois de cada refatoração. Esse é o motivo de ter testes antes de refatorar.

**Commit:** `refactor(nodes): extrai helper de chamada estruturada ao LLM` (T22)

### Passo 25 — Documentação: README e docstrings (§4.3)

**Material, seções do README (§4.3.1):** título e descrição; tabela de conteúdos (recomendado); tecnologias usadas, **incluindo modelos de IA e assistentes de código**; pré-requisitos; instalação; uso e exemplos; estrutura do projeto (opcional); como rodar os testes; contribuição (opcional); licença; limitações e próximos passos. Docstrings e comentários com a IA (§4.3.2).

**No nosso projeto:** além dessas, inclua **Arquitetura** (os dois diagramas Mermaid) e **Configuração** (tabela das variáveis do `.env.example`). Use Skeleton-of-Thought: peça primeiro o esqueleto do README com os títulos, revise, depois peça seção por seção.

**Commit:** `docs(readme): documenta instalação, uso, arquitetura e testes`

---

## Unidade 5 — Empacotamento, README Final, Demonstração e Submissão

### Passo 26 — Dependências reprodutíveis (§5.1.1)

**Material:** arquivo que liste todas as dependências com as versões corretas (requirements.txt é o mais comum; pyproject.toml é a alternativa moderna).

**No nosso projeto (T25):** já temos o `pyproject.toml` e o `uv.lock`. Gere também o `requirements.txt` com versões exatas, a partir do `uv.lock`:

```powershell
uv export --format requirements.txt --no-hashes --no-emit-project -o requirements.txt
```

O `--no-emit-project` evita gravar a linha do próprio projeto. Depois, teste a **instalação alternativa** (para quem não usa `uv`) num ambiente novo:

```powershell
py -3.12 -m venv .venv-teste
.venv-teste\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e . --no-deps
pytest
```

### Passo 27 — Makefile (§5.1.2)

**Material:** centralizar os comandos comuns (`install`, `run`, `test`, `format`) num Makefile, gerado com ajuda da IA.

**No nosso projeto (T25):** todos os comandos rodam com `uv run`.

```makefile
.PHONY: install run demo test lint format

install:
	uv sync

run:
	uv run content-pipeline run --file samples/sample_input.md

demo:
	uv run content-pipeline demo

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .
```

O ebook usa `black`; aqui o `ruff format` faz o mesmo papel com uma ferramenta a menos **[Decisão]**. No Windows, o `make` não vem instalado: use o Git Bash com `make` instalado (por exemplo `choco install make`, **[A verificar]** na sua máquina) ou rode os comandos equivalentes, que o README deve listar também.

**Commit:** `chore: adiciona requirements.txt e Makefile` (T25)

### Passo 28 — README final e a seção sobre IA (§5.2.1)

**Material:** o README final deve destacar o papel da IA: desafios superados com IA, ganhos de produtividade (quantificados se possível), decisões de arquitetura e design influenciadas pela IA, e lições aprendidas (limites da IA, engenharia de prompts, importância da revisão humana).

**No nosso projeto:** crie a seção **"Como a IA Acelerou Este Projeto"** a partir do `docs/uso-de-ia.md`. Exemplos concretos que você já tem:

- **Decisão de arquitetura revisada:** validação movida para antes da geração de imagem (Passo 2).
- **Alucinação de versão evitada:** versões conferidas no PyPI em vez de aceitas da IA (Passo 3).
- **Pegadinha do `.gitignore`:** `.env.*` ignorava o `.env.example` (Passo 5).
- **Limitação real descoberta:** fakes do LangChain sem `with_structured_output`, o que levou à injeção de dependência (documento do projeto, §5.3).
- **O ciclo TDD** (Passo 21) e **as refatorações** (Passo 24).

**Prompt (padrão do ebook adaptado):**

```
Contexto: Meu projeto foi desenvolvido com auxílio de IA generativa. Segue meu log de uso:
<colar docs/uso-de-ia.md>
Objetivo: Escreva a seção do README "Como a IA Acelerou Este Projeto", destacando
desafios superados, ganhos de produtividade, decisões influenciadas e lições aprendidas.
Mencione a importância da revisão humana com os exemplos reais do log.
Estilo: Primeira pessoa, objetivo, sem exagero; não invente números que não estão no log.
Resposta: Apenas a seção em Markdown.
```

Inclua também **Créditos** (social-media-agent como inspiração; documentação LangChain) e **Limitações e Próximos Passos** (o que ficou fora do MVP, documento do projeto §2.1).

**Commit:** `docs(readme): adiciona seção de uso de IA, limitações e créditos`

### Passo 29 — Demonstração visual e exemplos (§5.2.2)

**Material:** imagens ou GIFs mostrando o projeto funcionando (o ebook cita Peek e LICEcap) e exemplos de uso.

**No nosso projeto:**

- Grave um GIF do terminal rodando `uv run content-pipeline run ... --dry-run` (entrevista, aprovação e saída).
- Versione em `examples/` uma saída real de exemplo (`article.md`, `slides.json`, `caption.txt` e, se tiver, as imagens) e linke no README.
- Adicione o print do trace no LangSmith (Passo 17) e, se fizer o Passo 23, do experimento de avaliação.

**Commit:** `docs: adiciona demonstração e exemplos de saída`

### Passo 30 — Checklist final de submissão (§2.3.4 + §5.3.1)

Consolidado das duas listas do material:

- [ ] Repositório **público** e acessível; todos os arquivos necessários presentes (nenhum arquivo essencial barrado pelo `.gitignore`).
- [ ] **README** completo e renderizando: título e descrição, instalação, uso e exemplos, tecnologias (com modelos de IA e assistentes de código), seção de IA, limitações e próximos passos, créditos e licença.
- [ ] **Histórico de commits** claro, em Conventional Commits, com pelo menos 5 significativos (recomendado 5 a 10).
- [ ] **Dependências** listadas com versões (`requirements.txt` e `pyproject.toml`).
- [ ] **Testes** presentes, passando, e com instrução de como rodar.
- [ ] **Nenhuma credencial** no código nem no histórico; chaves só via `.env`, que está no `.gitignore`.
- [ ] **Branch `main` limpo**, sem trabalho em andamento nem arquivos temporários.
- [ ] **`CHANGELOG.md`** criado (formato Keep a Changelog, seção `[1.0.0]`) e commitado antes da tag (T28).
- [ ] **Tag/Release** `v1.0.0` criada.
- [ ] Arquivo de **licença** presente.

Comandos úteis para conferir (no Git Bash):

```bash
git status                                         # nada pendente
git log --oneline                                  # histórico legível
git log -p --all | grep -inE "api_key|secret|sk-"  # deve voltar vazio (só nomes de variáveis do .env.example são aceitáveis)
uv run pytest                                      # tudo verde
```

Se aparecer uma chave real no histórico, **revogue a chave no provedor imediatamente**; apagar do histórico não basta, porque ela já pode ter sido copiada.

Também vale fazer o teste de fogo da definição de pronto: clonar o repositório numa pasta nova e seguir só o README.

### Passo 31 — Tag e Release (§2.3.4 e §5.3.1)

**No nosso projeto (T28):** antes da tag, crie o `CHANGELOG.md` no formato Keep a Changelog, com a seção `[1.0.0]` resumindo as funcionalidades, e faça o commit `docs: adiciona CHANGELOG da v1.0.0` com push. Depois:

```powershell
git tag -a v1.0.0 -m "Entrega do miniprojeto do Microcurso 4"
git push origin v1.0.0
```

Depois crie a Release no GitHub a partir da tag (aba Releases → Draft a new release), ou pelo CLI, usando o changelog como notas: `gh release create v1.0.0 --title "v1.0.0" --notes-file CHANGELOG.md`.

---

## Fórum de encerramento

### Passo 32 — Postagem

**Material (enunciado do fórum):** link do repositório; miniprojeto escolhido; como a IA apoiou o desenvolvimento; desafios na organização, documentação ou submissão; cuidados para revisar, testar e validar as sugestões da IA.

Modelo de estrutura, para preencher com o seu log (escreva com a sua voz):

```markdown
**Repositório:** https://github.com/afcc2000/content-authority-pipeline (release v1.0.0)

**Miniprojeto escolhido:** <2 a 3 frases: o pipeline, o fluxo link → entrevista → artigo → carrossel,
e por que fugi do RAG básico>

**Como a IA apoiou:** <arquitetura e diagramas, esqueleto do código, testes, README;
quais ferramentas em cada etapa>

**Desafios:** <ex.: aprender LangGraph em paralelo; human-in-the-loop com interrupt;
testar sem chave de API; organizar commits e documentação ao longo do caminho>

**Cuidados de revisão e validação:** <ex.: versões conferidas no PyPI; .gitignore corrigido;
validação movida para antes das imagens; fakes sem with_structured_output → injeção de
dependência; TDD; testes do grafo com respostas roteirizadas; traces no LangSmith>
```

### Passo 33 — Comentário no post de um colega

**Material:** ler a contribuição de pelo menos um colega e comentar destacando um ponto interessante, uma estratégia diferente ou um aprendizado.

Estrutura sugerida: (1) o que chamou atenção no projeto dele, de forma específica; (2) uma comparação com a sua estratégia (ex.: como ele testou as respostas da IA versus como você testou); (3) uma pergunta ou sugestão concreta. Três ou quatro frases bastam.

---

## Anexo — Rastreabilidade com o material

A coluna "Ticket(s)" aponta para [tickets](tickets.md). "Prompt-base" e "definição de pronto" são as regras do início daquele arquivo, que valem para todo ticket.

| Seção do material | Passo(s) deste roteiro | Ticket(s) |
|---|---|---|
| M4 U2 §2.1 Seleção do MVP | 1 | T02 (registrado em `docs/projeto.md` e no log) |
| M4 U2 §2.2.1 Arquitetura com IA (Mermaid) | 2 | T02 |
| M4 U2 §2.2.2 Dependências | 3, 26 | T02; `uv add` em cada ticket; T25 |
| M4 U2 §2.3.1 Repositório, commit, push | 4, 6, 7, 8 | T00 e T01 (Passo 6 também T02, T03, T05, T16 e T17) |
| M4 U2 §2.3.2 `.gitignore` | 5 | T01 |
| M4 U2 §2.3.3 Conventional Commits | 9 (e todos os commits) | Mapa dos tickets |
| M4 U2 §2.3.4 Requisitos de submissão | 10, 30 | T00 e T28 |
| M4 U3 §3.1.1 Modelos de I/O | 11 | T03 e T04 |
| M4 U3 §3.1.2 Integração com LLM | 13 | T06 |
| M4 U3 §3.2 Copilot/Cursor, esqueletos e docstrings | 15, 18 | T09 a T12; prompt-base |
| M4 U3 §3.3 Revisão crítica e depuração | T3, 19 | Definição de pronto; T18 |
| M4 U4 §4.1.1 Testes unitários com IA | 20, 22 | T03 a T16 (grafo: T09 a T15) |
| M4 U4 §4.1.2 TDD | 21 | T19 a T21 |
| M4 U4 §4.2 Refatoração | 24 | T22 |
| M4 U4 §4.3 README e docstrings | 18, 25 | T24 |
| M4 U5 §5.1.1 Dependências | 26 | T25 |
| M4 U5 §5.1.2 Makefile | 27 | T25 |
| M4 U5 §5.2.1 README e papel da IA | 28 | T26 |
| M4 U5 §5.2.2 Demonstração visual | 29 | T27 |
| M4 U5 §5.3.1 Checklist final | 30, 31 | T28 |
| Fórum | 32, 33 | Sem commit |
| Microcurso 1 (SDLC, ADR) | §0, documento do projeto §10 | T02 |
| Microcurso 2 U1 §1.3 (engenharia de prompts) | T2, 19 | Prompt-base; T18 |
| Microcurso 3 U1 a U3 (elementos, técnicas, refinamento, critérios de qualidade) | T2, T3, 12, 23, 25 | Prompt-base; T05, T23 e T24 |

Correspondência completa, passo a passo: 1 a 3 → T02 (decisões registradas na documentação); 4 → T00 e T01; 5 a 7 → T01; 8 → T00 e T01; 9 → mapa dos tickets; 10 → T00; 11 → T03 e T04; 12 → T05; 13 → T06; 14 → T07 e T09; 15 → T09 a T12; 16 → T08, T13 e T14; 17 → T15, T16 e T18; 18 e 19 → prompt-base, definição de pronto e T18; 20 → T03 a T16; 21 → T19 a T21; 22 → T09 a T15; 23 → T23; 24 → T22; 25 → T24; 26 e 27 → T25; 28 → T26; 29 → T27; 30 e 31 → T28; fórum (32 e 33) → sem commit.
