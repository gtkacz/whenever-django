.PHONY: help init test lint format typecheck docs docs-clean clean build ci-lint

init:
	uv venv
	source .venv/bin/activate
	uv pip install -e ".[dev,docs,drf]"

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

docs:
	sphinx-build -W --keep-going -b html docs docs/_build/html

docs-clean:
	rm -rf docs/_build/ docs/api/

build:
	python -m build

ci-lint: lint typecheck build
	twine check dist/*

clean:
	rm -rf src/whenever_django.egg-info/ build/ dist/ .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
