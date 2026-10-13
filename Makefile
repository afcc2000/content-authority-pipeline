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
