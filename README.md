# Content Authority Pipeline

Um pipeline em LangGraph que recebe o link de um conteúdo, verifica se ele é relevante para o
contexto configurado e gera um briefing. Em seguida entrevista o autor (com `interrupt`) para
coletar suas contribuições e escreve um artigo de autoridade em Markdown, que o autor pode
aceitar, editar ou rejeitar com feedback. Aprovado o artigo, um subgrafo gera um carrossel de
Instagram (slides com frases curtas e chamada para o blog) e a legenda, seguindo uma identidade
visual definida em arquivos de prompt, com validação automática e geração de imagem por uma
interface plugável. Um modo `dry-run` roda tudo sem chamar a API de imagem.

> 🚧 **Em construção.** Miniprojeto do Microcurso 4 (AKCIT · Engenharia de Software com IA).
