.PHONY: help install install-dev test test-coverage lint format type-check clean pre-commit setup build test-build

help:
	@echo "Available commands:"
	@echo "  make install          Install package"
	@echo "  make install-dev      Install package with dev dependencies"
	@echo "  make test             Run tests"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo "  make lint             Run linter"
	@echo "  make format           Format code"
	@echo "  make type-check       Run type checker"
	@echo "  make build            Build package for distribution"
	@echo "  make test-build       Test that package builds correctly"
	@echo "  make clean            Clean build artifacts"
	@echo "  make pre-commit       Install pre-commit hooks"
	@echo "  make setup            Complete development setup"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-coverage:
	pytest --cov=osm2geojson --cov-report=html --cov-report=term

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

type-check:
	mypy osm2geojson

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

pre-commit:
	pre-commit install

build:
	python -m build

test-build: clean
	@./test_build.sh

setup: install-dev pre-commit
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify everything works."

all: format lint type-check test
	@echo "All checks passed!"
