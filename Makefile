# ─────────────────────────────────────────────────────────────────────────────
#  Osixr — Makefile
#  Convenience targets for development, testing, and publishing.
#
#  Usage:
#    make install       Install in editable mode (development)
#    make test          Run the test suite
#    make lint          Run ruff linter
#    make format        Auto-format with black
#    make build         Build source + wheel distributions
#    make publish       Upload to PyPI (requires TWINE_PASSWORD or .pypirc)
#    make publish-test  Upload to TestPyPI first
#    make docker-build  Build Docker image
#    make docker-run    Run Docker container (interactive)
#    make clean         Remove build artefacts and caches
# ─────────────────────────────────────────────────────────────────────────────

PYTHON     ?= python3
PIP        ?= $(PYTHON) -m pip
PACKAGE    := osixr
IMAGE      := osixr
VERSION    := $(shell $(PYTHON) -c "from importlib.metadata import version; print(version('$(PACKAGE)'))" 2>/dev/null || echo "dev")

.DEFAULT_GOAL := help

# ── help ──────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  Osixr $(VERSION) — available targets"
	@echo ""
	@echo "  make install        Install package in editable mode"
	@echo "  make install-dev    Install package + dev dependencies"
	@echo "  make test           Run test suite (pytest)"
	@echo "  make lint           Lint with ruff"
	@echo "  make format         Format with black"
	@echo "  make build          Build sdist + wheel"
	@echo "  make publish        Upload to PyPI"
	@echo "  make publish-test   Upload to TestPyPI"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run Docker container"
	@echo "  make clean          Remove build artefacts"
	@echo ""

# ── install ───────────────────────────────────────────────────────────────────
.PHONY: install
install:
	$(PIP) install -e .

.PHONY: install-dev
install-dev:
	$(PIP) install -e ".[dev]"

# ── quality ───────────────────────────────────────────────────────────────────
.PHONY: lint
lint:
	$(PYTHON) -m ruff check src/

.PHONY: format
format:
	$(PYTHON) -m black src/

# ── test ──────────────────────────────────────────────────────────────────────
.PHONY: test
test:
	$(PYTHON) -m pytest tests/ -v

# ── build ─────────────────────────────────────────────────────────────────────
.PHONY: build
build: clean
	$(PYTHON) -m build
	@echo ""
	@echo "  ✔  Built dist/"
	@ls -lh dist/

# ── publish ───────────────────────────────────────────────────────────────────
.PHONY: publish
publish: build
	$(PYTHON) -m twine upload dist/*

.PHONY: publish-test
publish-test: build
	$(PYTHON) -m twine upload --repository testpypi dist/*

# ── docker ───────────────────────────────────────────────────────────────────
.PHONY: docker-build
docker-build:
	docker build -t $(IMAGE):$(VERSION) -t $(IMAGE):latest .
	@echo "  ✔  Image built → $(IMAGE):$(VERSION)"

.PHONY: docker-run
docker-run:
	docker run --rm -it $(IMAGE):latest --help

# ── clean ─────────────────────────────────────────────────────────────────────
.PHONY: clean
clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "  ✔  Clean"
