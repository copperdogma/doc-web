# Doc-Forge Requirements
_AI-first intake runtime for provenance-rich structural website bundles_

## Purpose & Goals
- Convert hard document inputs into Dossier-ready structural HTML bundles with full provenance.
- Keep the active runtime focused on reusable intake, OCR, structure, and validation seams rather than legacy game/runtime exports.
- Preserve enough intermediate evidence that every downstream defect can be traced back to a concrete page, crop, OCR decision, or repair stage.

## Scope (Current Mission)
- Input: PDFs, scanned page-image directories, and adjacent document families that can be normalized into page-level extraction inputs.
- Output: structural HTML chapters/pages, bundle manifests, navigation metadata, and provenance sidecars for `doc-web` and Dossier.
- Baseline stages: intake → OCR/HTML extraction → targeted repair loops → portionization/structure → chapter/build output → validation.
- Runs remain restartable and artifact-driven so expensive upstream work can be reused while downstream structure iterates quickly.

## Functional Requirements
1. **Ingestion**: accept PDF or image-directory inputs and normalize them into page manifests with stable identifiers.
2. **Extraction**: produce page-level HTML or equivalent structured text with explicit provenance to source page/image artifacts.
3. **Repair**: run targeted table, layout, and continuity rescue loops where extraction quality drops below the acceptance bar.
4. **Structure**: identify document sections/chapters and preserve reading order, boundaries, and page coverage.
5. **Illustrations**: detect, crop, and publish illustrations with references that downstream HTML can consume.
6. **Validation**: emit inspectable reports that prove page coverage, structural consistency, and downstream bundle readiness.
7. **Bundle Output**: build structural HTML plus manifests and provenance blocks that Dossier can ingest without bespoke repo-local knowledge.
8. **Configuration**: support CLI and YAML-driven recipe selection, model overrides, retry limits, and resume controls without code edits.
9. **Traceability**: retain intermediate JSON/JSONL artifacts, module provenance envelopes, and run registries for audit and replay.
10. **Operational Reuse**: support partial reruns, artifact loading, and no-AI regression recipes for active maintained seams.

## Non-Functional Requirements
- Modularity: new document families should prefer recipe/module composition over code forks.
- Transparency: validation and repair decisions must be inspectable from committed artifacts, not hidden in prompts alone.
- Cost discipline: expensive OCR/intake work should be reusable; downstream iteration should avoid unnecessary recomputation.
- Portability: local files and JSON/JSONL artifacts remain the primary operating model; no database dependency.
- Reliability: active paths must have maintained tests or recipe-backed regression coverage.

## Active Repository Structure
- `modules/`: intake, extraction, transform, adapter, build, and validate stages.
- `configs/recipes/`: active recipes for `doc-web` and maintained regression paths.
- `docs/`: mission docs, runbooks, stories, ADRs, and bundle contracts.
- `output/runs/<run_id>/`: pipeline artifacts, manifests, and validation outputs.
- `output/run_manifest.jsonl`, `output/run_health.jsonl`, `output/run_assessments.jsonl`: shared run registries.

## Acceptance Criteria
- Given a real PDF or image-directory input, the repo can produce a run with page-level extraction artifacts, structural build artifacts, validation output, and shared registry entries.
- A downstream reviewer can inspect any chapter/page output and trace it back to source artifacts without guesswork.
- Active recipes can be resumed or rerun by changed scope without redoing unrelated expensive stages.
- Mission-facing docs and defaults point to the maintained intake + `doc-web` path rather than retired legacy exports.
