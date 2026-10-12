"""Subgrafo do carrossel: planeja, valida (refazendo se preciso) e gera as imagens.

    START -> plan_slides -> validate -(erro e ainda há tentativas)-> plan_slides
                                     -(válido ou tentativas esgotadas)-> render_images -> END

Usa o mesmo `PipelineState` do grafo principal, então lê e escreve as mesmas chaves.
"""

from pathlib import Path
from typing import Literal

from langgraph.graph import END, START, StateGraph

from content_pipeline.carousel.planner import make_plan_slides
from content_pipeline.carousel.validators import validate_carousel
from content_pipeline.deps import Deps
from content_pipeline.state import PipelineState


def make_validate(deps: Deps):
    """Cria o nó `validate`: grava os erros e conta a tentativa; avisa se esgotou."""
    max_attempts = deps.settings.max_carousel_attempts

    def validate(state: PipelineState) -> dict:
        errors = validate_carousel(state["carousel"], deps.settings)
        attempts = (state.get("carousel_attempts") or 0) + 1
        update: dict = {"validation_errors": errors, "carousel_attempts": attempts}
        if errors and attempts >= max_attempts:
            warning = f"Carrossel seguiu com erros após {attempts} tentativa(s): " + " ".join(
                errors
            )
            update["warnings"] = [*(state.get("warnings") or []), warning]
        return update

    return validate


def make_route_after_validate(deps: Deps):
    """Cria a rota após `validate`: refaz enquanto houver erro e tentativas sobrando."""
    max_attempts = deps.settings.max_carousel_attempts

    def route_after_validate(state: PipelineState) -> Literal["plan_slides", "render_images"]:
        if state.get("validation_errors") and state["carousel_attempts"] < max_attempts:
            return "plan_slides"
        return "render_images"

    return route_after_validate


def make_render_images(deps: Deps):
    """Cria o nó `render_images`: uma imagem por slide em `output_dir/images/slide_NN.png`."""

    def render_images(state: PipelineState) -> dict:
        images_dir = Path(state["output_dir"]) / "images"
        paths = [
            deps.images.generate(
                slide.image_prompt,
                aspect_ratio=deps.settings.image_aspect_ratio,
                out_path=images_dir / f"slide_{slide.index:02d}.png",
            )
            for slide in state["carousel"].slides
        ]
        return {"images": [str(path) for path in paths]}

    return render_images


def build_carousel_subgraph(deps: Deps):
    """Monta e compila o subgrafo; sem checkpointer próprio (usa o do grafo principal)."""
    builder = StateGraph(PipelineState)
    builder.add_node("plan_slides", make_plan_slides(deps))
    builder.add_node("validate", make_validate(deps))
    builder.add_node("render_images", make_render_images(deps))

    builder.add_edge(START, "plan_slides")
    builder.add_edge("plan_slides", "validate")
    builder.add_conditional_edges("validate", make_route_after_validate(deps))
    builder.add_edge("render_images", END)
    return builder.compile()
