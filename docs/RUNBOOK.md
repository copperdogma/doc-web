# Pipeline Operations Runbook

**Audience:** AI Agents & Engineering Operators
**Scope:** Execution, Recovery, and Configuration of the Doc Forge pipeline.

## 🛑 Critical Safety Rules
1.  **NEVER use `--force` when resuming.** It deletes the entire run directory.
2.  **ALWAYS use `run_driver_monitored.sh`** for production runs (handles logging, PID tracking, crash detection).
3.  **CHECK `pipeline_state.json`** before resuming to confirm the correct `--start-from` stage.

---

## 🚀 Standard Execution

There is no single default recipe for the active mission. Choose the narrowest
recipe that matches the document family you are validating.

### Structural Website / `doc-web` Runs
Use these when validating the active structural HTML bundle path.

```bash
scripts/run_driver_monitored.sh \
  --recipe <active_recipe> \
  --run-id <run_id> \
  --output-dir output/runs \
  -- --instrument --force
```
*   `--instrument`: Enables cost/timing tracking (Required for production).
*   `--force`: **DELETES** `<run_id>` dir if it exists. Use only for fresh starts.

Active recipe examples:
- `configs/recipes/recipe-images-ocr-html-mvp.yaml`
- `configs/recipes/recipe-onward-images-html-mvp.yaml`
- `configs/recipes/onward-genealogy-build-regression.yaml` (artifact-reuse path; requires the referenced Story 140 / 143 artifacts under `output/`)

### Smoke Test (Verification)
Use the same recipe you are actually touching, but narrow the run to the
smallest real slice that still exercises the changed seam.

```bash
scripts/run_driver_monitored.sh \
  --recipe <active_recipe> \
  --run-id <smoke_run_id> \
  --output-dir output/runs \
  -- --instrument --max-pages <N> --force
```

- There is no generic `make smoke` target for the active intake / `doc-web`
  path.

---

## 🔄 Recovery & Resume (The "Happy Path")

**Scenario:** The pipeline crashed (API error, quota limit, timeout) mid-run.
**Goal:** Resume without losing expensive OCR data.

### 1. Identify Failed Stage
Check `output/runs/<run_id>/pipeline_events.jsonl` or `driver.log`.

### 2. Resume Command
**Crucial:** Remove `--force`. Add `--start-from <stage_id>`.

```bash
scripts/run_driver_monitored.sh \
  --recipe <original_recipe> \
  --run-id <original_run_id> \
  --output-dir output/runs \
  -- --instrument --start-from <failed_stage_id>
```

*   **`--start-from <stage_id>`**: Driver loads state up to this stage and resumes execution.
*   **Automatic Skipping:** Most expensive modules (OCR, Extract) support internal resuming. If they see partial output, they skip completed items.
*   **`--skip-done`**: Optional. Tells driver to skip any stage that has a valid output artifact in `pipeline_state.json`. Useful if you aren't sure exactly which stage failed but know earlier ones are good.

---

## 🛠️ Configuration Reference

### Recipes (`configs/recipes/`)
| Recipe | Purpose |
| :--- | :--- |
| `recipe-images-ocr-html-mvp.yaml` | Active structural HTML bundle path for image-directory inputs. |
| `recipe-onward-images-html-mvp.yaml` | **Genealogy.** Specialized for *Onward* tables. |
| `onward-genealogy-build-regression.yaml` | No-AI artifact-reuse regression path that rebuilds chapters and genealogy validation from accepted Onward artifacts already present under the shared `output/` root. |

### Presets (`configs/presets/`)
| Preset | Usage |
| :--- | :--- |
| `cost.ocr.yaml` | Low cost (gpt-4.1-mini). |
| `quality.ocr.yaml` | Max quality (gpt-5). |
| `speed.text.yaml` | Fast text processing. |

### CLI Overrides
Append these after `--` in the wrapper script.

*   `--model <name>`: Global model override.
*   `--max-pages <N>`: Stop after N pages.
*   `--start-from <stage>`: Resume point.
*   `--end-at <stage>`: Halt point.
*   `--dry-run`: Validate recipe/graph without execution.

---

## 🔍 Troubleshooting

### Common Failures

**429 RESOURCE_EXHAUSTED (Quota)**
*   **Fix:** Pause. Wait for quota reset (UTC midnight). Resume using **Recovery** steps above.

**TypeError: Object of type ResponseUsage...**
*   **Fix:** Code bug in Gemini client serialization. Update module to convert `usage` object to dict.

**KeyError: 'stage_id' (during resume)**
*   **Cause:** Artifacts missing. Did you use `--force` by mistake?
*   **Fix:** Restart from scratch or restore artifacts from backup.

### Monitoring
*   **Tail Logs:** `scripts/monitor_run.sh output/runs/<run_id> output/runs/<run_id>/driver.pid 5`
*   **Dashboard:** `python -m http.server 8000` -> `http://localhost:8000/docs/pipeline-visibility.html`

## Run Registry

Use the shared output-root registries before reusing an old run for validation or as an upstream.

Registry files:
*   `output/run_manifest.jsonl`: factual run index
*   `output/run_health.jsonl`: machine-generated health facts
*   `output/run_assessments.jsonl`: AI-written review judgments

### Reuse Safety Check

Ask the registry whether a run is safe for a specific scope before citing it as a validation source.

```bash
python tools/run_registry.py check-reuse \
  --run-id <run_id> \
  --scope page_presence
```

Recommended scopes:
*   `page_presence`
*   `chapter_structure`
*   `page_break_stitching`
*   `table_fidelity`
*   `full_book_fidelity`

If `recommendation` is `unsafe`, do not use that run for review even if older notes said it was good.

From a git worktree, omit `--output-root`; the CLI resolves the shared project `output/` root automatically. Only pass `--output-root` when you are intentionally targeting a different output tree.

### Recording Review Notes

When a human reviews a run in conversation, the AI should convert that judgment into a structured assessment entry.

```bash
python tools/run_registry.py record-assessment \
  --run-id <run_id> \
  --scope page_presence \
  --status unsafe \
  --summary "Missing printed pages 6 and 8 in source page HTML." \
  --finding "Pages 6 and 8 are empty in extract_page_numbers_html output." \
  --evidence output/runs/<run_id>/05_extract_page_numbers_html_v1/pages_html.jsonl
```

Assessments are scope-specific. A run can be safe for one scope and unsafe for another.
