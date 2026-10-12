"""Teste de fumaça da Higgsfield: gera 1 imagem real (gasta créditos).

Uso: `uv run python scripts/higgsfield_smoke.py`. Lê `HF_KEY` ("key-id:key-secret") do `.env`
sem nunca mostrar o valor. Sai com código 1 se o pedido falhar, for moderado ou cancelado.
"""

import os
import sys

import higgsfield_client
from dotenv import find_dotenv, load_dotenv

MODEL = "higgsfield-ai/soul/v2/standard"
ARGUMENTS = {
    "prompt": "A cinematic scene at sunset",
    "resolution": "720p",
    "aspect_ratio": "3:4",  # retrato; a página do modelo não aceita 4:5
    "batch_size": 1,
}


def main() -> int:
    load_dotenv(find_dotenv(usecwd=True))
    if not os.getenv("HF_KEY"):
        print("Erro: HF_KEY não está no .env (formato key-id:key-secret).", file=sys.stderr)
        return 1

    # `subscribe` não levanta erro em failed/nsfw/canceled: devolve o JSON com `status`.
    result = higgsfield_client.subscribe(
        MODEL,
        arguments=ARGUMENTS,
        on_enqueue=lambda request_id: print(f"Pedido na fila: {request_id}"),
        on_queue_update=lambda status: print(f"Status: {type(status).__name__}"),
    )

    status = result.get("status")
    images = result.get("images") or []
    if status != "completed" or not images:
        print(f"Erro: status={status!r}, error={result.get('error')!r}", file=sys.stderr)
        return 1

    print(f"Imagem gerada: {images[0]['url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
