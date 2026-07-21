.PHONY: help init test lint format typecheck clean build ci-lint

init:
	uv venv
	source .venv/bin/activate
	uv pip install -e ".[dev]"

test:
	pytest tests/

lint:
	ruff format --check src/ tests/
	ruff check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

typecheck:
	mypy src/

build:
	python -m build

ci-lint: lint typecheck build
	twine check dist/*

clean:
	rm -rf src/whenever_django.egg-info/ build/ dist/ .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
