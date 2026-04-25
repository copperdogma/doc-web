# doc-forge Benchmarks

Systematic evaluation of AI models/prompts for pipeline tasks using [promptfoo](https://www.promptfoo.dev/).

## Setup

```bash
# Node.js 22+ required (24 LTS recommended)
source ~/.nvm/nvm.sh && nvm use 24

# Install promptfoo globally
npm install -g promptfoo

# Preferred: put repo-local keys in ../.env
DOC_WEB_OPENAI_API_KEY=...
DOC_WEB_ANTHROPIC_API_KEY=...
DOC_WEB_GEMINI_API_KEY=...

# Then run provider-backed commands through the doc-web env wrapper.
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache -j 3
```

If you want a freshness delay for the global `promptfoo` install, set it in your
user-level npm config. npm added `min-release-age` in `11.10.0`, and this repo
cannot enforce it for a global install from inside the checkout.

## Workspace Layout

```
benchmarks/
├── tasks/              # promptfoo YAML configs (one per eval task)
├── prompts/            # Prompt templates with {{variable}} placeholders
├── golden/             # Hand-crafted reference data for scoring
│   └── crops/          # Manually cropped reference images
├── input/
│   ├── source-pages-b64/      # Tracked page fixtures as data-URI text payloads
│   └── crop-validation-b64/   # Tracked crop fixtures as data-URI text payloads
├── scorers/            # Python scoring scripts (get_assert interface)
├── results/            # JSON output from eval runs
└── scripts/            # Analysis helpers
```

For the maintained crop surfaces, the checked-in `.b64.txt` fixtures under
`input/` are part of the benchmark contract. Do not casually swap these tasks
to raw image files: promptfoo's `file://` path is safe for the text-based
data-URI fixtures but not for raw binary JPEG interpolation in these
multi-provider vision prompts.

## Running Evals

```bash
cd benchmarks/

# Run an eval (no cache for reproducibility)
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache -j 3

# Smoke-check the maintained crop surfaces from a clean checkout
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache --filter-first-n 1 -j 1 --no-write
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/crop-validation.yaml --no-cache --filter-first-n 1 -j 1 --no-write
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml --no-cache --filter-first-n 1 -j 1 --no-write

# Save results
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache --output results/image-crop-run1.json

# Current maintained dedicated C5-linked surface
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/crop-validation.yaml --no-cache \
  --filter-providers 'google:gemini-3.1-flash-lite-preview' \
  --filter-prompts 'caption-focus' \
  --output results/crop-validation-story183-g31-caption-focus.json \
  -j 1

# Current maintained page-context C5 deletion gate
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml --no-cache \
  --output results/crop-page-level-deletion-gate-gpt55-responses-current-20260424.json \
  -j 1

# View results in web UI leaderboard
promptfoo view
```

## Eval Catalog

Quick reference for all promptfoo eval setups. Re-run any eval when new models come out to check for improvements.

### 1. Image Crop Extraction (Story 125)

**Task**: Extract photo/illustration bounding boxes from scanned book pages.
**Best recorded result**: Gemini 3 Flash conservative-count prompt with the heading-safe revision (`0.9678` avg score, `100%` pass rate, refreshed 2026-04-03)
**Config**: `tasks/image-crop-extraction.yaml`
**Scorer**: `scorers/image_crop_scorer.py` — IoU + coverage metrics
**Prompts**: 4 variants (baseline, strict-exclude, two-step, conservative-count)
**Test set**: 13 tracked downscaled page fixtures from *Onward to the Unknown*

```bash
cd benchmarks && source ~/.zshrc && promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache
```

**Key findings**:
- The maintained page-level detector surface is `tasks/image-crop-extraction.yaml`, and it now includes the `conservative-count` prompt that previously only lived in the focused Gemini 3 Flash comparison task.
- Story 133 introduced the winning Gemini 3 Flash `conservative-count` detector prompt; the 2026-04-03 follow-up tightened that prompt to exclude ordinary heading-style display text while keeping standalone text-as-art, which raised the maintained task to `0.9678` overall / `1.0` pass rate.
- The bounded C4 deletion gate now passes on the maintained single-stage Gemini 3 Flash surface; the remaining crop question is broader C5 text-exclusion proof and runtime simplification, not detector selection.

---

### 2. Crop Validation (Story 126 + Story 183)

**Task**: Judge whether an extracted crop should pass or fail based on external page text, excessive blank space, or obvious wrong-region crops.
**Current maintained result**: Gemini 3.1 Flash Lite + `caption-focus` (`1.0` overall, `1.0` pass rate, `40/40` on 2026-04-11)
**Config**: `tasks/crop-validation.yaml`
**Scorer**: `scorers/crop_validation_scorer.py` — pass/fail classification against checked labels
**Golden**: `golden/crop-validation.json`
**Test set**: 40 tracked downscaled crop fixtures with 4 explicit fail cases

```bash
cd benchmarks && source ~/.nvm/nvm.sh && nvm use 24 >/dev/null 2>&1 && \
promptfoo eval -c tasks/crop-validation.yaml --no-cache \
  --filter-providers 'google:gemini-3.1-flash-lite-preview' \
  --filter-prompts 'caption-focus' \
  --output results/crop-validation-story183-g31-caption-focus.json \
  -j 1
```

**Key findings**:
- This is the dedicated current C5-linked text-exclusion / crop-quality surface.
- The repaired local benchmark substrate now makes this surface runnable from a clean checkout.
- Passing this bounded 40-crop corpus does not by itself delete C5; the broader page-level deletion benchmark is still a separate step.

---

### 3. Crop Page-Level Deletion Gate (Story 209)

**Task**: Judge the maintained runtime overlap cases with both the source page and the extracted crop in view, so the benchmark can answer the broader C5 deletion question instead of only the crop-only pass/fail question.
**Current maintained result**: GPT-5.5 Responses + `page-context` promptfix (`1.0` overall, `1.0` pass rate, `22/22` on 2026-04-24 corrected golden)
**Config**: `tasks/crop-page-level-deletion-gate.yaml`
**Scorer**: `scorers/crop_validation_scorer.py` — pass/fail classification against checked labels from the page-context golden
**Golden**: `golden/crop-page-level-deletion-gate.json`
**Test set**: 22 tracked page/crop overlap cases with 4 explicit fail-labeled residue cases

```bash
cd benchmarks && source ~/.nvm/nvm.sh && nvm use 24 >/dev/null 2>&1 && \
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml --no-cache \
  --output results/crop-page-level-deletion-gate-gpt55-responses-current-20260424.json \
  -j 1
```

**Key findings**:
- This is the broader page-context C5 deletion-gate surface; it complements, but does not replace, the bounded crop-only `crop-validation` task.
- The checked-in overlap corpus now covers the page-12 seal/text-bearing case, the page-122 caption/neighboring-portrait leakage cases, and additional reviewed residue-style examples on the maintained Onward seam.
- The maintained task now runs only the corrected-golden winner, `openai:responses:gpt-5.5`; the earlier Gemini 3.1 Flash Lite `22/22` result is stale after the `page-122-001` correction, and its fresh rerun is `21/22`.
- The surface passes cleanly as a judge, but its own golden still includes 5 fail-labeled current-runtime cases, so Story 209's current decision is to keep the surviving C5 residue in place.

---

### 4. OCR Model Eval — Genealogy Pages (Story 127)

**Task**: Single-pass VLM OCR — model sees raw page image, outputs structured HTML with `<table>` elements and `<img>` placeholders.
**Winner**: Gemini 3 Pro + table-strict (0.877 avg score, 100% pass rate)
**Config**: `tasks/ocr-genealogy-tables.yaml`
**Scorer**: `scorers/table_structure_scorer.py` — table detection, column/row/cell accuracy, header detection, img detection
**Prompts**: 2 variants (baseline, table-strict)
**Test set**: 25 pages from *Onward to the Unknown* covering:
  - 14 table-heavy pages (6-column genealogy tables, dense multi-table, TABLE-AS-TEXT failures)
  - 11 image-heavy pages (photos, illustrations, certificates, mixed narrative+images)

```bash
cd benchmarks && source ~/.zshrc && promptfoo eval -c tasks/ocr-genealogy-tables.yaml --no-cache -j 2
```

**Scoring**: Dynamic weights based on page content:
- Table-only: table_detection 25%, column_accuracy 25%, cell_text 25%, row_accuracy 15%, header_accuracy 10%
- Mixed (tables + images): table weights reduced, 15% to img_detection
- Image-only: 100% img_detection

**Golden references**: `golden/ocr-genealogy/page-NNN-golden.html` — hand-corrected HTML with `<table>` and `<img>` tags.
**Inputs**: `input/onward-pages-b64/ImageNNN.b64.txt` — base64-encoded page images.

**Key findings** (Feb 2026):
- `table-strict` prompt dramatically outperforms `baseline` across all models
- Top 4 (table-strict): Gemini 3 Pro (0.877, 100% pass), Gemini 2.5 Pro (0.870), Claude Opus 4.6 (0.866), Claude Sonnet 4.5 (0.861)
- GPT models rate-limited to 14/25 pages even at concurrency 1; best GPT: GPT-5 Mini (0.768)
- Image detection (`<img>` placeholders) near-perfect across all models (0.96-1.00)
- GPT-5.1 (current pipeline model) ranks 8th at 0.761 — switching to Gemini 3 Pro = ~15% improvement

## Adding a New Eval

1. Copy or generate test inputs under `input/`
2. Create golden references in `golden/` (hand-crafted, expert-validated)
3. Write prompt template in `prompts/` (use `{{var}}` placeholders)
4. Write Python scorer in `scorers/` (implement `get_assert(output, context)`)
5. Create promptfoo config in `tasks/` (providers x test cases x assertions)
6. Run eval, analyze, iterate on prompts, pick winning model
