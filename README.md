# doc-web
AI-first runtime for turning scanned books, PDFs, and images into structural, provenance-rich HTML website bundles for Dossier and related downstream consumers.

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
- **[Benchmarks](benchmarks/README.md)**: Systematic model evaluation using `promptfoo`.

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
