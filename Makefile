.PHONY: install playground run test lint clean

install:
	uv sync

playground:
	uv run adk web app --host 127.0.0.1 --port 18081 --reload_agents

run:
	uv run adk web app --host 127.0.0.1 --port 8080

test:
	uv run pytest

lint:
	uv run ruff check .

clean:
	rm -rf .venv __pycache__ .adk .pytest_cache
