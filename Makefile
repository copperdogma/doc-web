# Makefile for codex-forge
PYTHON ?= python3

.PHONY: test lint format smoke smoke-ff skills-sync skills-check check-size

# ── Testing & Linting ─────────────────────────────────────────────────
test:
	$(PYTHON) -m pytest tests/

lint:
	$(PYTHON) -m ruff check modules/ tests/

format:
	$(PYTHON) -m ruff format modules/ tests/

# ── Smoke Tests ───────────────────────────────────────────────────────
smoke: smoke-ff

smoke-ff:
	@echo "Running Fighting Fantasy smoke test (stubbed, no AI calls)..."
	PYTHONPATH=. python driver.py --recipe configs/recipes/recipe-ff-smoke.yaml --force
	@echo "Smoke test complete. Artifacts in output/runs/smoke-ff/"
	@echo "Checking validation report..."
	@grep '"is_valid": true' output/runs/smoke-ff/validation_report.json > /dev/null || (echo "Validation FAILED" && exit 1)
	@echo "Validation PASSED"

# ── Skills ────────────────────────────────────────────────────────────
skills-sync:
	./scripts/sync-agent-skills.sh

skills-check:
	./scripts/sync-agent-skills.sh --check

# ── Code Health ───────────────────────────────────────────────────────
check-size:
	@echo "Python source files over 400 lines:"
	@find modules -name "*.py" -exec wc -l {} \; | sort -rn | awk '$$1 > 400 {print "  LARGE: " $$1 " lines — " $$2}'
