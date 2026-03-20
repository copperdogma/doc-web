# `doc-web` Dossier Readiness Gap Analysis

**Date:** 2026-03-19  
**Purpose:** assess what still blocks `doc-web` from being presented to Dossier as a usable pinned component, using Storybook's Dossier dependency model as the reference pattern.

## Bottom Line

`doc-web` is now ready to present to Dossier as a usable pinned component.

The repo-side blockers that previously kept this boundary aspirational are
closed:

- installable package metadata exists in `pyproject.toml`
- `doc-web` exposes a machine-readable runtime preflight via
  `doc-web contract --json`
- the live current-repo builder emits `manifest.json`,
  `provenance/blocks.jsonl`, and matching `blk-*` anchors
- a repo-owned real-run smoke lane exists at
  `configs/recipes/doc-web-fixture-bundle-smoke.yaml`
- clean-venv install smoke and contract tests exist in
  `tests/test_doc_web_cli_contract.py`

What remains is downstream adoption work inside Dossier, not readiness work in
this repo.

## Storybook Pattern To Copy

Storybook treats Dossier as a repo-owned pinned runtime, not as an ambient
sibling checkout.

Reference surfaces:

- `/Users/cam/Documents/Projects/Storybook/storybook/dossier-runtime.json`
- `/Users/cam/Documents/Projects/Storybook/storybook/scripts/dossier-runtime.mjs`
- `/Users/cam/Documents/Projects/Storybook/storybook/packages/backend/src/ai/dossier-runtime.ts`
- `/Users/cam/Documents/Projects/Storybook/storybook/packages/backend/src/ai/dossier-adapter.ts`
- `/Users/cam/Documents/Projects/Storybook/storybook/docs/runbooks/dossier-runtime.md`

That operational model still stands as the right one for Dossier consuming
`doc-web`:

- Dossier owns a repo-local pin manifest
- the pinned runtime installs into `.runtime/doc-web-pinned/`
- pinned is the default source; local override is explicit
- upgrade bumps run contract preflight and fixture validation before merge
- deploy builds use a pinned source snapshot, not a fresh git clone

## Ready Now

### Installable runtime surface

Evidence:

- `pyproject.toml`
- `doc_web/__init__.py`
- `doc_web/cli.py`
- `tests/test_doc_web_cli_contract.py`

Result:

- `python -m pip install .` is now valid package-install input
- the installed console script exposes `doc-web`

### Machine-readable runtime preflight

Evidence:

- `doc_web/runtime_contract.py`
- `doc_web/cli.py`
- `python -m doc_web contract --json`

Result:

- Dossier can cheaply inspect `runtime_version`, `requires_python`,
  supported schema versions, and `schema_fingerprint` before accepting a bump

### Live bundle contract emission from current repo code

Evidence:

- `modules/build/build_chapter_html_v1/main.py`
- `output/runs/story156-docweb-fixture-bundle-r1/output/html/manifest.json`
- `output/runs/story156-docweb-fixture-bundle-r1/output/html/provenance/blocks.jsonl`
- `output/runs/story156-docweb-fixture-bundle-r1/output/html/chapter-001.html`
- `output/runs/story156-docweb-fixture-bundle-r1/output/html/page-001.html`

Result:

- the active builder now emits the published Dossier-facing contract from a
  real `driver.py` run, not only from a committed handoff pack

### Repo-owned smoke lane

Evidence:

- `configs/recipes/doc-web-fixture-bundle-smoke.yaml`
- `tests/fixtures/doc_web_bundle_smoke/`
- `docs/RUNBOOK.md`

Result:

- the active bundle seam can be rebuilt without relying on ignored `/tmp`
  recipes or historical `output/runs/` artifacts

## Gaps Closed In Story 156

These were the repo-side blockers before Story 156 and are no longer open:

1. No installable package/runtime surface
2. No machine-readable runtime preflight
3. Live current-repo build did not prove the published Dossier contract
4. Release/version policy was documented but not executable
5. No install-smoke proving the packaged runtime shape

## Remaining Dossier-Only Work

These are downstream implementation tasks, not reasons to delay presenting
`doc-web` as a usable component:

- create `doc-web-runtime.json` or equivalent pin manifest in Dossier
- add `install`, `check-upstream`, and `bump` scripts in Dossier
- install the pinned runtime into `.runtime/doc-web-pinned/`
- enforce pinned-by-default with explicit local overrides only
- implement the `doc_web_bundle_v1` intake adapter and `semantic_html`
  stop-point
- export a pinned source snapshot for Docker/deploy builds

## Later / Non-Blocking Improvements

These matter, but they are not blockers on Dossier adopting the component:

- PDF-to-HTML performance improvements
- new input formats
- broader fixture coverage
- private registry infrastructure
- deeper runtime extraction beyond the current structural bundle boundary

## Ready-To-Present Definition

`doc-web` now meets the repo-side ready-to-present bar:

- a tagged ref can be installed as a package
- the installed runtime exposes a machine-readable contract preflight
- the live current-repo bundle build reproduces the published contract
- the docs tell Dossier how to pin, smoke, and upgrade it

The next move is to adopt the pinned runtime pattern in Dossier, not to do more
boundary cleanup here first.
