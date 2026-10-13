# Content Authority Pipeline

Um pipeline em LangGraph que recebe o link de um conteúdo, verifica se ele é relevante para o
contexto configurado e gera um briefing. Em seguida entrevista o autor (com `interrupt`) para
coletar suas contribuições e escreve um artigo de autoridade em Markdown, que o autor pode
aceitar, editar ou rejeitar com feedback. Aprovado o artigo, um subgrafo gera um carrossel de
Instagram (slides com frases curtas e chamada para o blog) e a legenda, seguindo uma identidade
visual definida em arquivos de prompt, com validação automática e geração de imagem por uma
interface plugável. Um modo `dry-run` roda tudo sem chamar a API de imagem.

> 🚧 **Em construção.** Miniprojeto do Microcurso 4 (AKCIT · Engenharia de Software com IA).

## Sumário

- [Como funciona](#como-funciona)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Testes](#testes)
- [Licença](#licença)

## Como funciona

1. **Fonte:** você informa um link (`--url`), um arquivo (`--file`) ou um tema (`--topic`, que
   busca a melhor fonte na web).
2. **Relevância:** o LLM decide se a fonte combina com os temas do autor (`prompts/context.md`).
   Se não combinar, o pipeline para e grava um relatório com o motivo.
3. **Entrevista:** o pipeline pausa e faz ao autor, uma por vez, as perguntas do briefing. São as
   contribuições pessoais que transformam um resumo num artigo de autoridade.
4. **Artigo:** o LLM escreve o artigo; o autor aceita, edita no próprio arquivo ou rejeita com
   feedback (o artigo é reescrito, até um limite de reescritas).
5. **Carrossel:** com o artigo aprovado, o LLM planeja os slides e a legenda. Regras
   determinísticas (número de slides, tamanho das headlines, legenda, hashtags, chamada e link
   para o blog) validam o plano; se falharem, o LLM corrige a partir da lista de erros.
6. **Saída:** artigo, slides, legenda, imagens (ou seus prompts, em dry-run) e um relatório da
   execução numa pasta própria.

## Arquitetura

O projeto é um **workflow explícito** em LangGraph: cada nó é uma etapa especializada, com o
próprio system prompt (montado a partir de `prompts/*.md`) e saída estruturada em um modelo
Pydantic. As pausas para o autor usam `interrupt` e um checkpointer. As dependências externas
(LLM, gerador de imagem, leitura e busca na web) são injetadas nos nós por um objeto `Deps`, o
que permite testar o grafo inteiro com implementações falsas.

### Fluxo do grafo

```mermaid
flowchart TD
    TEMA(["Tema (--topic)"]) --> RES["research<br/>busca na web + escolhe a fonte"]
    RES --> ING
    IN(["Link ou arquivo (--url / --file)"]) --> ING["ingest<br/>lê e limpa o texto"]
    ING --> ANA["analyze<br/>relevância + briefing"]
    ANA -->|irrelevante| REP["export_report<br/>só o relatório"]
    ANA -->|relevante| INT["interview<br/>interrupt: uma pergunta por vez"]
    INT -->|faltam perguntas| INT
    INT -->|entrevista concluída| WA["write_article<br/>artigo em Markdown"]
    WA --> HITL{{"approval<br/>interrupt: accept, edit ou reject"}}
    HITL -->|reject + feedback, dentro do limite| WA
    HITL -->|reject após o limite| REP
    HITL -->|accept ou edit| CAR

    subgraph CAR["design_carousel (subgrafo)"]
        direction TB
        PL["plan_slides<br/>slides + legenda"] --> VAL{"validate<br/>regras determinísticas"}
        VAL -->|erros e tentativas sobrando| PL
        VAL -->|ok, ou tentativas esgotadas com aviso| IMG["render_images<br/>ImageGenerator"]
    end

    IMG --> EXP["export"]
    EXP --> OUT(["article.md, slides.json, caption.txt, report.md, images/"])
    REP --> OUT2(["report.md"])

    PROMPTS[("prompts/*.md<br/>contexto, estilo, marca")] -.-> RES
    PROMPTS -.-> ANA
    PROMPTS -.-> WA
    PROMPTS -.-> PL
```

### Componentes

```mermaid
flowchart LR
    CLI["cli.py<br/>Typer"] --> GRAPH["graph.py<br/>StateGraph + checkpointer"]
    CFG["config.py<br/>pydantic-settings + .env"] --> DEPS["deps.py<br/>dependências injetadas"]
    CLI --> DEPS
    GRAPH --> NODES["nodes/*<br/>uma etapa por nó"]
    GRAPH --> SUB["carousel/<br/>subgrafo + validators"]
    GRAPH --> EXPO["export.py<br/>arquivos de saída"]
    NODES --> ASK["nodes/common.py<br/>ask: prompts + LLM"]
    SUB --> ASK
    ASK --> PRM["prompts.py<br/>carrega prompts/*.md"]
    ASK --> LLM["llm.py<br/>StructuredLLM + init_chat_model"]
    NODES --> FETCH["fetcher.py<br/>httpx + trafilatura (padrão)"]
    NODES --> WEB["web.py<br/>Tavily: leitura opcional + busca por tema"]
    SUB --> PORT["images/base.py<br/>ImageGenerator (Protocol)"]
    PORT --> FAKE["images/fake.py<br/>dry-run e testes"]
    PORT -.-> HF["Higgsfield<br/>planejado (E1)"]
    GRAPH -. traces .-> LS[("LangSmith")]
```

O adaptador real de imagem (Higgsfield) ainda não está implementado: hoje cada imagem sai como um
arquivo `.prompt.txt` com o prompt do slide.

## Tecnologias

| Área | Ferramenta |
|---|---|
| Linguagem e pacotes | Python 3.12, [uv](https://docs.astral.sh/uv/) |
| Orquestração | LangGraph 1.2 (`StateGraph`, `interrupt`, checkpointer em memória) |
| LLM | LangChain 1.4 (`init_chat_model`, `with_structured_output`), provedor configurável (OpenAI por padrão) |
| Modelos e configuração | Pydantic 2, pydantic-settings, python-dotenv |
| CLI | Typer |
| Web | httpx + trafilatura (leitura de links); Tavily (busca por tema e leitura opcional) |
| Imagem | interface `ImageGenerator`; SDK `higgsfield-client` instalado para o adaptador real |
| Observabilidade | LangSmith (traces) |
| Qualidade | pytest, ruff |

<!-- T26: ferramentas de IA usadas no desenvolvimento -->

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (ele instala o Python 3.12 se
  precisar).
- Uma chave de API de LLM (por padrão, OpenAI).
- Opcionais: chave do [Tavily](https://tavily.com) (busca por tema), do
  [LangSmith](https://smith.langchain.com) (traces) e da Higgsfield (imagens, quando o adaptador
  real existir).

## Instalação

```bash
git clone https://github.com/afcc2000/content-authority-pipeline.git
cd content-authority-pipeline
uv sync
copy .env.example .env      # Windows; no Linux/macOS: cp .env.example .env
```

Depois, preencha no `.env` pelo menos `LLM_MODEL` e a chave do provedor (ex.: `OPENAI_API_KEY`).

<!-- T25: instalação alternativa com pip/requirements.txt e comandos sem make -->

## Configuração

Tudo é lido do ambiente ou do arquivo `.env`, que nunca é versionado.

| Variável | Obrigatória? | Para que serve |
|---|---|---|
| `LLM_MODEL` | sim | Modelo no formato `provedor:modelo`, ex.: `openai:<nome-do-modelo>` |
| `OPENAI_API_KEY` | com OpenAI | Chave do provedor do LLM (outro provedor usa a própria variável) |
| `WEB_READER` | não | Como ler links: `trafilatura` (padrão, sem chave) ou `tavily` |
| `TAVILY_API_KEY` | para `--topic` ou `WEB_READER=tavily` | Chave do Tavily |
| `IMAGE_PROVIDER` | não | `fake` (padrão) ou `higgsfield` (adaptador ainda não implementado) |
| `HF_KEY` | com Higgsfield | Credencial no formato `key-id:key-secret` |
| `BLOG_URL` | não | Se definido, a legenda do carrossel precisa conter este link |
| `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `LANGSMITH_ENDPOINT` | não | Envio de traces para o LangSmith |

Limites ajustáveis no mesmo `.env` (padrão entre parênteses): `MAX_REWRITES` (3),
`MAX_CAROUSEL_ATTEMPTS` (2), `MIN_SLIDES` (5), `MAX_SLIDES` (10), `HEADLINE_MAX_CHARS` (80),
`CAPTION_MAX_CHARS` (2200), `MAX_HASHTAGS` (5), `IMAGE_ASPECT_RATIO` (4:5) e `PROMPTS_DIR`
(`prompts`).

Os textos que definem o autor, o estilo do artigo e a identidade visual ficam em `prompts/*.md` e
podem ser editados sem mexer no código.

## Uso

```bash
uv run content-pipeline run --url https://exemplo.com/artigo   # a partir de um link
uv run content-pipeline run --file meu_texto.md                # a partir de um arquivo
uv run content-pipeline run --topic "tema do artigo"           # busca a fonte (exige Tavily)
uv run content-pipeline demo                                   # exemplo de samples/, em dry-run
```

Informe exatamente uma fonte. Opções:

- `--out PASTA`: onde salvar os resultados (padrão: `outputs`).
- `--dry-run` / `--no-dry-run`: o padrão é dry-run, que não chama a API de imagem e grava só os
  prompts das imagens.

Durante a execução o pipeline pausa duas vezes:

1. **Entrevista:** cada pergunta aparece como `Pergunta i/n`; responda ou tecle Enter para pular.
2. **Aprovação:** o artigo é mostrado e você escolhe `accept`, `edit` (o artigo é salvo em
   `article_draft.md`; edite, salve e tecle Enter) ou `reject` (escreva o que deve mudar; a opção
   some quando o limite de reescritas acaba).

Cada execução gera uma pasta `outputs/AAAA-MM-DD-<slug>/` com:

| Arquivo | Conteúdo |
|---|---|
| `article.md` | Artigo aprovado |
| `slides.json` | Slides (headline, complemento, prompt da imagem), legenda, hashtags e chamada para o blog |
| `caption.txt` | Legenda pronta para colar, com as hashtags |
| `report.md` | Fonte, relevância, decisão, entrevista e avisos |
| `images/slide_NN.prompt.txt` | Prompt de cada imagem (dry-run) |

Se a fonte for irrelevante ou o artigo for rejeitado depois do limite de reescritas, a pasta
recebe só o `report.md`, com o motivo.

## Estrutura do projeto

```text
content-authority-pipeline/
├── src/content_pipeline/
│   ├── cli.py            # comandos run e demo; responde às pausas no terminal
│   ├── graph.py          # monta o StateGraph e o checkpointer
│   ├── state.py          # estado compartilhado do grafo
│   ├── models.py         # modelos Pydantic (Briefing, Article, CarouselPlan...)
│   ├── config.py         # Settings (pydantic-settings)
│   ├── deps.py           # dependências injetadas nos nós
│   ├── llm.py            # porta StructuredLLM e implementação com LangChain
│   ├── prompts.py        # carrega e compõe prompts/*.md
│   ├── fetcher.py        # leitura de links com httpx + trafilatura
│   ├── web.py            # Tavily: leitura opcional e busca por tema
│   ├── export.py         # grava os arquivos de saída e o relatório
│   ├── nodes/            # research, ingest, analyze, interview, write_article, approval
│   ├── carousel/         # subgrafo do carrossel: planner, validators, subgraph
│   └── images/           # porta ImageGenerator e adaptador fake
├── prompts/              # contexto do autor, estilo do artigo, marca e regras do carrossel
├── tests/                # testes com LLM e gerador de imagem falsos (tests/fakes.py)
├── samples/              # entrada de exemplo do comando demo
├── scripts/              # teste de fumaça da API de imagem (gasta créditos)
└── docs/                 # projeto, roteiro, tickets e log de uso de IA
```

## Testes

```bash
uv run pytest                 # todos os testes, sem chave de API e sem rede
uv run ruff check .           # lint
uv run ruff format --check .  # formatação
```

Os testes usam um LLM falso (`tests/fakes.py`), que devolve respostas roteirizadas, e um gerador
de imagem falso. Assim cobrem o grafo inteiro (entrevista, `accept`, `edit`, `reject`, fonte
irrelevante, validação do carrossel e exportação) sem custo. O marcador `integration` fica
reservado para testes que chamam APIs reais: eles ficam fora da execução padrão e rodam com
`uv run pytest -m integration`.

<!-- T26: Como a IA acelerou este projeto, limitações e créditos -->
<!-- T27: demonstração e exemplos -->

## Licença

[MIT](LICENSE) © 2026 André Felipe Cunha
