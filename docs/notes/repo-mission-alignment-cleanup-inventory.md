# Repo Mission Alignment Cleanup Inventory

**Date:** 2026-03-19
**Decision context:** `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`

This note records the final state of Story 155 after the inventory pass, the
removal tranches, and the closeout documentation polish.

## Kept

- Active intake and `doc-web` recipes:
  - `configs/recipes/recipe-images-ocr-html-mvp.yaml`
  - `configs/recipes/recipe-onward-images-html-mvp.yaml`
  - `configs/recipes/onward-genealogy-build-regression.yaml` (artifact-reuse regression lane; requires the referenced Story 140 / 143 artifacts under the shared `output/` root)
  - the active story-scoped Onward validation recipes
- Active bundle/runtime surfaces:
  - `modules/build/build_chapter_html_v1`
  - active genealogy and intake validation modules
  - run registries and the structural HTML bundle contract
- Mission docs:
  - `README.md`
  - `AGENTS.md`
  - `docs/RUNBOOK.md`
  - `docs/ideal.md`
  - `docs/requirements.md`
  - `docs/document-ir.md`

## Removed

- The retained FF/gamebook recipe family:
  - top-level `configs/recipes/recipe-ff*.yaml`
  - FF/gamebook legacy recipes under `configs/recipes/legacy/`
- The FF export, validation, and packaging runtime:
  - `modules/export/build_ff_engine_*`
  - `modules/export/initialize_output_v1`
  - `modules/export/package_game_ready_v1`
  - `modules/validate/validate_ff_engine_*`
  - `modules/validate/validate_gamebook_smoke_v1`
  - related edgecase and turn-to claim helper modules
- The former live gamebook/runtime seams removed in the final tranche:
  - `driver.py` compatibility branches that still special-cased `gamebook` inputs, deleted portionize modules, or non-existent transform modules
  - `modules/adapter/report_pipeline_issues_v1`
  - `modules/adapter/context_aware_post_process_v1`
  - `modules/adapter/context_aware_t5_v1`
  - the stale `associate_illustrations_to_sections_v1` catalog entry in `modules/module_catalog.yaml`
- FF-only operator tools, scripts, tests, and fixtures:
  - OCR bench helpers and checked-in bench artifacts
  - FF smoke settings and stubs
  - FF regression tests and builder/validator tests
  - checked-in gamebook examples and robot/sample-book analysis notes
- Root fossils:
  - `snapshot.md`
  - `example-prompt.md`
  - `prompts/macro_ff_single_call.md`
  - `settings.fast-intake.yaml`

## Updated

- `tools/run_manager.py` now seeds the active image-to-HTML recipe instead of a legacy FF recipe and sample PDF.
- Mission-facing docs, defaults, and fixtures were rewritten to remove live sample-book references and stale FF/default-path guidance.
- `docs/pipeline-visibility.html` now prefers the active chapter build artifact instead of the retired FF build stage.
- Active prompts, schema comments, and boundary/OCR helper wording were generalized away from FF/gamebook framing where the underlying code remains part of the maintained repo.

## Intentional Historical Record

The following surfaces still contain old FF/sample-book names on purpose:

- completed story files in `docs/stories/`
- story titles in `docs/stories.md`
- `CHANGELOG.md`
- scan/report artifacts in `docs/reports/`
- retired-compromise and migration-history notes in `docs/spec.md` and `docs/notes/standalone-dossier-intake-runtime-plan.md`
- decision records and research artifacts under `docs/decisions/adr-002-doc-web-runtime-boundary/`

Those references are preserved as project history or decision context, not as
active mission guidance.
