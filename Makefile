# Makefile for doc-forge
# Prefer the active environment's Python so `make test`/`make lint` use the
# same interpreter the repo dependencies were installed into.
PYTHON ?= $(shell command -v python 2>/dev/null || command -v python3 2>/dev/null)

.PHONY: test lint format smoke skills-sync skills-check check-size

# ── Testing & Linting ─────────────────────────────────────────────────
test:
	$(PYTHON) -m pytest tests/

lint:
	$(PYTHON) -m ruff check doc_web/ modules/ tests/

format:
	$(PYTHON) -m ruff format doc_web/ modules/ tests/

# ── Smoke Tests ───────────────────────────────────────────────────────
smoke:
	@echo "No single generic smoke target exists for the active intake/doc-web mission."
	@echo "Use the narrowest real recipe-specific driver path from docs/RUNBOOK.md."
	@exit 2

# ── Skills ────────────────────────────────────────────────────────────
skills-sync:
	./scripts/sync-agent-skills.sh

skills-check:
	./scripts/sync-agent-skills.sh --check

# ── Code Health ───────────────────────────────────────────────────────
check-size:
	@echo "Python source files over 400 lines:"
	@find doc_web modules -name "*.py" -exec wc -l {} \; | sort -rn | awk '$$1 > 400 {print "  LARGE: " $$1 " lines — " $$2}'
