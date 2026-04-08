# doc-web
AI-first runtime for turning scanned books, PDFs, office documents, and images into structural, provenance-rich HTML website bundles for Dossier and related downstream consumers.

## Current Role
- Own the structural website contract: semantic HTML pages, reading order, minimal navigation, manifests, and provenance sidecars.
- Provide the versioned runtime boundary Dossier can consume without pulling in codex-forge's research and workflow overhead.
- Evolve the proven codex-forge ingestion path into a reusable runtime while keeping polished presentation and publication UX outside this repo.

`doc-web` intentionally owns structural output, not the final themed website experience. Presentation-layer website generation remains outside this repo's scope.

## 📚 Documentation
- **[Runbook & Operations Guide](docs/RUNBOOK.md)**: **START HERE** for running the pipeline, resuming runs, and troubleshooting.
- **[Agent Guide](AGENTS.md)**: Guidelines for AI agents and developers contributing to the codebase.
- **[doc-web Bundle Contract](docs/doc-web-bundle-contract.md)**: Frozen v1 structural website bundle and provenance contract for the `doc-web` runtime boundary.
- **[Dossier Handoff](docs/dossier-doc-web-handoff.md)**: The downstream-facing contract, fixture pack, and versioning expectations Dossier should implement against.
- **[Dossier Readiness Gap Analysis](docs/notes/doc-web-dossier-readiness-gap-analysis.md)**: Current blocker inventory and the split between repo-side and Dossier-side work.
- **[Benchmarks](benchmarks/README.md)**: Systematic model evaluation using `promptfoo`.

## Pinned Consumer Surface

`doc-web` now exposes explicit pinned-runtime install shapes Dossier can depend on:

```bash
# Contract preflight only
python -m pip install .
doc-web contract --json

# Repo-owned driver smoke lanes from this checkout
python -m pip install '.[driver]'

# Maintained DOCX lane from this checkout
python -m pip install '.[driver,docx]'

# Maintained XLSX lane from this checkout
python -m pip install '.[driver,xlsx]'

# Maintained PPTX lane from this checkout
python -m pip install '.[driver,pptx]'
```

The contract preflight returns:

- package/runtime version
- required Python version
- supported bundle schema versions
- a schema fingerprint Dossier can use to block incompatible upgrades
- explicit compatibility-policy guidance for interpreting those fields

The `driver` extra keeps the base package small while making the repo-owned
smoke lanes installable. It covers the maintained proof lanes in this README
and the runbook that need YAML parsing plus HTML bundle building, without
claiming that the base package alone can run `driver.py`.

The `docx`, `xlsx`, and `pptx` extras add the narrow office-document partition
dependencies needed by the maintained office-native recipes without turning the
default `driver` install into the full OCR/runtime stack.

The recommended downstream operating model mirrors Storybook's pinned-Dossier
pattern:

- Dossier owns a repo-local pin manifest such as `doc-web-runtime.json`
- the pinned install root lives under `.runtime/doc-web-pinned/`
- Dossier defaults to the pinned install and only allows a local override
  explicitly for co-development
- every pin bump reruns the committed `doc-web` contract smoke lane before merge

## For Dossier Consumers

If you want to adopt `doc-web` as a component, use this README as the entry
point, then follow the two downstream-facing docs it points to:

- Start here in `README.md` for the install shape, pinned-runtime model, and
  runtime preflight command
- Read [Dossier Handoff](docs/dossier-doc-web-handoff.md) for the exact bundle
  contract, pinning expectations, and Dossier-side adapter responsibilities
- Use [Runbook & Operations Guide](docs/RUNBOOK.md) for the concrete smoke and
  validation commands that prove a pinned `doc-web` version is still compatible

Recommended first-pass adoption loop:

```bash
# Cheap compatibility preflight
python -m pip install .
doc-web contract --json

# Repo-owned smoke lane from this checkout
python -m pip install '.[driver]'
python driver.py \
  --recipe configs/recipes/doc-web-fixture-bundle-smoke.yaml \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --force
python validate_artifact.py \
  --schema doc_web_bundle_manifest_v1 \
  --file output/runs/<run_id>/output/html/manifest.json
python validate_artifact.py \
  --schema doc_web_provenance_block_v1 \
  --file output/runs/<run_id>/output/html/provenance/blocks.jsonl
```

For the maintained born-digital PDF proof lanes, keep the same `.[driver]`
install and add the non-Python runtime prerequisites up front:

- Docker available on `PATH`
- `pdftotext` available on `PATH`

Story 196 widened the bounded maintained born-digital slice to four repo-owned
fixtures across both explicit lanes:

- Book-like: `testdata/tbotb-mini.pdf`, `testdata/born-digital-handbook-mini.pdf`
- Flat / non-TOC: `testdata/flat-born-digital-mini.pdf`, `testdata/flat-born-digital-form-mini.pdf`

The repeatable comparison surface for that slice now lives at:

```bash
python benchmarks/scripts/run_born_digital_pdf_eval.py \
  --output benchmarks/results/born-digital-pdf-story196.json \
  --run-root output/runs/story196-born-digital-benchmark
```

That maintained benchmark also reruns the two shared local comparison-only
PDFs (`rfp`, `release-forms`) when they are present, but the passing gate
rests on the four repo-owned supported cases above.

For the maintained DOCX proof lane, install the explicit DOCX extra:

```bash
python -m pip install '.[driver,docx]'
python driver.py \
  --recipe configs/recipes/recipe-docx-html-mvp.yaml \
  --input-docx testdata/docx-mini.docx \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --force
```

Story 175 widened the DOCX proof surface to three repo-owned fixtures on the
supported slice: `testdata/docx-mini.docx`,
`testdata/docx-sections-mini.docx`, and `testdata/docx-nested-mini.docx`.

For the maintained XLSX proof lane, install the explicit XLSX extra:

```bash
python -m pip install '.[driver,xlsx]'
python driver.py \
  --recipe configs/recipes/recipe-xlsx-html-mvp.yaml \
  --input-xlsx testdata/xlsx-mini.xlsx \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --force
```

Story 193 widened the maintained XLSX proof surface to three repo-owned
fixtures on the supported slice:

- `testdata/xlsx-mini.xlsx`
- `testdata/xlsx-multi-sheet.xlsx`
- `testdata/xlsx-two-tables.xlsx`

That supported slice is still intentionally narrow: simple table-only sheets,
including multiple table regions on one sheet, with sheet-named entries and
anchor-based provenance. `testdata/xlsx-merged-formula.xlsx` remains a bounded
unsupported probe because merged-title / formula-summary structure is currently
promoted into heading blocks instead of staying inside the table.

For the maintained PPTX proof lane, install the explicit PPTX extra:

```bash
python -m pip install '.[driver,pptx]'
python driver.py \
  --recipe configs/recipes/recipe-pptx-html-mvp.yaml \
  --input-pptx testdata/pptx-mini.pptx \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --force
```

Story 197 established the first bounded maintained PPTX slice on the checked-in
`testdata/pptx-mini.pptx` fixture. The supported claim is intentionally narrow:

- one title slide plus simple slide-title/list/prose slides
- slide-number provenance via `source_page_number` and manifest `source_pages`
- direct explicit-recipe entry only

Speaker notes, embedded media, animations, charts, and broader mixed-layout
PowerPoint ownership remain unproven.

Those maintained office lanes are still direct explicit-recipe entry points.
Story 194 did not widen the recommendation-only intake or approved-handoff
automation to office files: `auto-book-type-detection` remains a PDF-only
surface, `approved-intake-handoff` remains limited to `pdf` and `images_dir`,
and office boundary probes now fail explicitly instead of crashing inside the
contact-sheet builder.

## Maintained Intake Recipes

The active maintained entry surfaces are explicit recipes, not hidden routing:

- `configs/recipes/recipe-images-ocr-html-mvp.yaml` for image-directory scans
- `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` for generic PDF-backed intake
- `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml` for the bounded maintained book-like born-digital PDF slice
- `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` for the bounded maintained flat/non-TOC born-digital PDF slice
- `configs/recipes/recipe-docx-html-mvp.yaml` for the maintained DOCX fixture-backed lane
- `configs/recipes/recipe-pptx-html-mvp.yaml` for the maintained PPTX slide-backed lane on the verified bounded probe slice
- `configs/recipes/recipe-xlsx-html-mvp.yaml` for the maintained XLSX workbook-table lane on the verified simple-table slice
- `configs/recipes/recipe-onward-images-html-mvp.yaml` for the image-backed Onward genealogy lane
- `configs/recipes/recipe-onward-pdf-html-mvp.yaml` for the PDF-backed Onward genealogy lane

Recommendation-only intake automation is intentionally narrower than that full
list: maintained `docx`, `xlsx`, and `pptx` support currently starts with explicit
`driver.py --recipe ... --input-docx/--input-xlsx/--input-pptx` entry, not the
recommendation-only contact-sheet flow or approved-handoff automation.

To seed a maintained PDF-backed run config explicitly:

```bash
python tools/run_manager.py create-run smoke-pdf \
  --pdf /absolute/path/to/document.pdf
```

For an Onward-specific PDF-backed run, keep recipe selection explicit:

```bash
python tools/run_manager.py create-run onward-pdf \
  --pdf /absolute/path/to/Onward.pdf \
  --recipe configs/recipes/recipe-onward-pdf-html-mvp.yaml
```

## Pipeline Architecture

The active repo path is format-aware intake plus structural website output for
`doc-web` and Dossier. A typical active flow looks like:

1. **Intake / normalize (generic)**: PDF, page images, or other source material → page manifests and normalized extraction inputs
2. **Extract + verify (generic)**: OCR/HTML extraction plus completeness and quality checks with provenance preserved
3. **Portionize / structure (format-aware)**: identify logical sections, repeated patterns, and ordering for the document family
4. **Repair + validate (format-aware)**: handle consistency, table rescue, and other targeted recovery loops where needed
5. **Build bundle + handoff (active export path)**: emit structural HTML pages, manifests, navigation, and provenance sidecars for Dossier / `doc-web`

**Reusability goal:** Keep upstream intake/OCR modules as generic as possible. Prefer pushing booktype-specific heuristics/normalization downstream into booktype-aware modules.

## Repository Layout
- `driver.py`: Main orchestration script.
- `modules/`: Pipeline stages (`extract`, `transform`, `adapter`, etc.).
- `configs/recipes/`: YAML files defining pipeline stages (logic).
- `configs/recipes/legacy/`: Archived or reference-only recipes kept for historical reruns.
- `configs/presets/`: YAML files defining model/cost settings (parameters).
- `output/runs/`: All pipeline artifacts and logs.
- `output/run_*.jsonl`: Shared run registries for manifest, health, and AI review assessments.
- `docs/`: Documentation and story tracking.
- `benchmarks/`: Model evaluation workspace.

## Setup & Dependencies

### Python Environment
- **Canonical (GPT-5.1 OCR)**: Runs on any architecture (x86_64 or ARM64).
  ```bash
  pip install --no-cache-dir -r requirements.txt
  ```

### Supply-Chain Freshness Gate
- `pyproject.toml` now sets `tool.uv.exclude-newer = "7 days"` for repo-local `uv` project workflows.
- For the current pip-style install paths, use the repo-owned wrapper to reject packages published within the last 7 days:
  ```bash
  ./scripts/install_with_age_gate.py .
  ./scripts/install_with_age_gate.py '.[driver]'
  ./scripts/install_with_age_gate.py '.[driver,docx]'
  ./scripts/install_with_age_gate.py '.[driver,pptx]'
  ./scripts/install_with_age_gate.py '.[driver,xlsx]'
  ./scripts/install_with_age_gate.py -r requirements.txt
  ```
- The wrapper prefers `uv pip install --exclude-newer ...` and falls back to `pip install --uploaded-prior-to ...` when your pip supports it.
- This is a delay-based mitigation, not a complete supply-chain defense. It does not replace lockfiles, dependency review, or artifact provenance checks.

### Dossier-Facing Install Shapes
- `python -m pip install .` supports the machine-readable contract preflight only.
- `python -m pip install '.[driver]'` supports the repo-owned `driver.py` smoke lanes documented in this README and [docs/RUNBOOK.md](docs/RUNBOOK.md).
- `python -m pip install '.[driver,docx]'` supports the maintained DOCX lane from this checkout.
- `python -m pip install '.[driver,pptx]'` supports the maintained PPTX lane from this checkout.
- `python -m pip install '.[driver,xlsx]'` supports the maintained XLSX lane from this checkout.
- The maintained born-digital PDF lanes also require Docker and `pdftotext`.
- The fuller repo runtime from `requirements.txt` now also includes DOCX, XLSX, and PPTX support, but it is currently validated on Python 3.11/3.12 because the pinned `unstructured==0.16.9` line is limited to that range.

### API Keys
Set the following environment variables:
- `OPENAI_API_KEY`: For GPT-4/5 models.
- `GEMINI_API_KEY`: For Google Gemini models.
- `ANTHROPIC_API_KEY`: For Claude models (benchmarking/judging).

### Legacy Environment (Unstructured/EasyOCR)
If using the deprecated legacy pipeline with local OCR:
- **ARM64 (Apple Silicon)**: Recommended for `hi_res` strategy using `jax-metal`.
- **x86_64 (Rosetta)**: Use for `ocr_only` compatibility.
- See `docs/legacy/environment_setup.md` (if created) or check git history for detailed setup of legacy environments.

## Development

### Unit Tests
```bash
make test
make lint
```

If you are installing or updating Python dependencies locally, prefer the age-gated wrapper above over raw `pip install` commands.

### Runtime Preflight
```bash
doc-web contract --json
```

### Pipeline Verification
Use the narrowest real recipe-specific `driver.py` or monitored run path from
`docs/RUNBOOK.md`. There is no generic `make smoke` default for the active
mission.

### Dashboard
View pipeline progress and artifacts visually:
```bash
python -m http.server 8000
# Open http://localhost:8000/docs/pipeline-visibility.html
```
