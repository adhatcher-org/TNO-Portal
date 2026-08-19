POETRY ?= poetry
IMAGE ?= tno-portal
PYTHON ?= python3
TRANSLATE_SCRIPT ?= scripts/generate_translations.py

.PHONY: build check coverage dependencies docker-build format install lint run security test test-local translate translate-force

install:
	$(POETRY) install

test:
	$(POETRY) run pytest -p no:cacheprovider

test-local: translate
	$(POETRY) run pytest

format:
	$(POETRY) run ruff format --check --no-cache .

lint:
	$(POETRY) run ruff check --no-cache .

translate:
	$(PYTHON) $(TRANSLATE_SCRIPT)

translate-force:
	$(PYTHON) $(TRANSLATE_SCRIPT) --force

coverage:
	@coverage_file="$$(mktemp -t tno-coverage.XXXXXX)"; \
	trap 'rm -f "$$coverage_file"' EXIT; \
	$(POETRY) run coverage run --data-file="$$coverage_file" -m pytest; \
	$(POETRY) run coverage report --data-file="$$coverage_file" -m

security:
	$(POETRY) run bandit --quiet --recursive app scripts wsgi.py
	PIP_NO_CACHE_DIR=1 $(POETRY) run pip-audit

dependencies:
	$(POETRY) check --lock

check: format lint test coverage security dependencies

build:
	docker build -t $(IMAGE) .

docker-build: build

run:
	$(POETRY) run gunicorn --bind 0.0.0.0:8000 wsgi:app
