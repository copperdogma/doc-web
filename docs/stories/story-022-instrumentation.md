---
title: Pipeline instrumentation (timing & cost)
status: Done
priority: Unknown
ideal_refs: []
spec_refs: ["spec:2", "spec:8"]
adr_refs: []
depends_on: []
category_refs: ["spec:2", "spec:8"]
compromise_refs: ["C6", "B3"]
input_coverage_refs: []
architecture_domains: []
roadmap_tags: []
legacy_system: ''
---

# Story: Pipeline instrumentation (timing & cost)

**Status**: Done

---

## Acceptance Criteria
- Capture per-stage wall time, CPU time, and count of LLM/API calls with model names and token usage (prompt/completion).
- Emit run-level cost estimate using configurable price sheet per model.
- Expose a human-readable report (JSON + markdown summary) in the run directory.
- Wire instrumentation into `driver.py` without breaking existing recipes; can be toggled via recipe or CLI flag.
- Document how to enable instrumentation and interpret reports.

## Tasks
- [x] Define instrumentation data schema (per stage + run summary) and add to `schemas.py` or dedicated report format.
- [x] Add driver hooks to record start/end timestamps, durations, and system resource info (CPU wall/elapsed).
- [x] Integrate OpenAI usage capture (model, prompt_tokens, completion_tokens, total_cost via price table).
- [x] Add price table configuration (YAML) and default pricing for current models; allow overrides per run.
- [x] Emit report files (JSON + markdown) into `output/runs/<run_id>/` and link from manifest.
- [x] Provide CLI/recipe flag to enable instrumentation; ensure default off to avoid overhead where undesired.
- [x] Add validator or smoke test to ensure instrumentation outputs parse and include required fields.
- [x] Update docs (`README` or `docs/requirements.md`) with enablement and sample report.
- [x] Add module-side helper to append per-call LLM usage (model/tokens/cache hit) to a driver-managed sink file.
- [x] Link instrumentation artifacts (JSON + markdown) from `run_manifest.jsonl` and stage progress for discoverability.

## Notes
- Consider piggybacking on existing `ProgressLogger` events; append instrumentation instead of duplicating state.
- Pricing: store cents/token for prompt/completion by model; fall back to defaults if model not found.
- Should work for both local-only stages and LLM stages; local stages can record duration without cost.

## Design Outline (draft)
- **Report files:** `instrumentation.json` (machine-readable) and `instrumentation.md` (human summary) in `output/runs/<run_id>/`; manifest entry points to both when enabled.
- **JSON shape (run):** `{ run_id, recipe_name/path, started_at, ended_at, wall_seconds, cpu_user_seconds, cpu_system_seconds, stages: [...], totals: {calls, prompt_tokens, completion_tokens, cost, per_model:{}} , pricing:{source, models:{model:{prompt_per_1k, completion_per_1k, currency}}}, env:{python_version, platform} }`.
- **Stage record:** `{ id, module_id, stage, status, started_at, ended_at, wall_seconds, cpu_user_seconds, cpu_system_seconds, artifact, schema_version, llm:{calls:[{model, provider, prompt_tokens, completion_tokens, cached, request_ms, request_id, cost}], totals:{calls, prompt_tokens, completion_tokens, cost}} }`.
- **Timing capture:** driver wraps each stage with `time.perf_counter()` for wall and `resource.getrusage()` (children) deltas for CPU; fallback to wall-only on platforms lacking `resource`.
- **LLM usage capture:** driver provides env vars `INSTRUMENT_SINK` (jsonl path) and `INSTRUMENT_STAGE`/`RUN_ID`; modules call a new helper `log_llm_usage(model, prompt_tokens, completion_tokens, cached=False, provider=\"openai\", request_ms=None, request_id=None)` that appends events; driver aggregates per stage after process exit.
- **Pricing config:** YAML (e.g., `configs/pricing.default.yaml`) with `models: {gpt-4.1-mini: {prompt_per_1k: 0.00015, completion_per_1k: 0.0006, currency: USD}, ...}` and optional `default` fallback; CLI flag `--price-table` to override path.
- **Enablement knobs:** CLI `--instrument` (default false) plus optional `--instrument-config <yaml>`; recipe may specify `instrumentation: {enabled: true, price_table: ..., include_calls: true}` with CLI able to override.
- **Markdown summary:** single-page digest with totals, per-model cost table, per-stage timings, and top-N expensive stages; link to raw JSON.

## Schema Draft
- **Pydantic class `LLMCallUsage`:** fields `model: str`, `provider: str = "openai"`, `prompt_tokens: int`, `completion_tokens: int`, `cached: bool = False`, `request_ms: Optional[float]`, `request_id: Optional[str]`, `cost: Optional[float]`.
- **Pydantic class `StageInstrumentation`:** `id: str`, `stage: str`, `module_id: str`, `status: str`, `artifact: Optional[str]`, `schema_version: Optional[str]`, `started_at: str`, `ended_at: str`, `wall_seconds: float`, `cpu_user_seconds: Optional[float]`, `cpu_system_seconds: Optional[float]`, `llm_calls: List[LLMCallUsage] = []`, `llm_totals: {calls: int, prompt_tokens: int, completion_tokens: int, cost: float}`, `extra: Dict[str, Any] = {}`.
- **Pydantic class `RunInstrumentation`:** `run_id: str`, `recipe_name: Optional[str]`, `recipe_path: Optional[str]`, `started_at: str`, `ended_at: str`, `wall_seconds: float`, `cpu_user_seconds: Optional[float]`, `cpu_system_seconds: Optional[float]`, `stages: List[StageInstrumentation]`, `totals: {calls: int, prompt_tokens: int, completion_tokens: int, cost: float, per_model: Dict[str, Any]}`, `pricing: Dict[str, Any]`, `env: Dict[str, Any]`.
- **Report schema location:** extend `schemas.py` with these classes and add `SCHEMA_MAP` entry `instrumentation_run_v1` for validation.
- **JSON storage:** `instrumentation.json` stores `RunInstrumentation` object; `instrumentation_calls.jsonl` keeps raw call events (optional) for debugging.

## Driver Aggregation Plan
- On driver start, load pricing table (default path `configs/pricing.default.yaml`; recipe/CLI can override). Build mapping `model -> (prompt_per_tok, completion_per_tok)`.
- When `--instrument` (or recipe instrumentation enabled):
  - Set `instrument_sink = run_dir/instrumentation_calls.jsonl`; pass env vars `INSTRUMENT_SINK`, `INSTRUMENT_STAGE`, `RUN_ID` into each stage process.
  - Before running a stage: record `start_wall = perf_counter()`, `start_ru = resource.getrusage(RUSAGE_CHILDREN)`; log `extra.instrument=true` via ProgressLogger.
  - After stage completion (success/fail): record end times; compute deltas; parse sink events for `stage_id`; accumulate per-stage totals and cost using pricing table; attach to `StageInstrumentation`.
  - Append stage instrumentation to in-memory list; write interim `instrumentation.json` after each stage for crash safety.
  - On completion, compute run-level totals (sum of stage totals) and persist final JSON + markdown summary (tables of top costs/times).
- Stage failure still records timing with status `failed`; cost/tokens may be partial.

## Implementation Plan (WIP)
- Add new pricing file `configs/pricing.default.yaml` (USD, prompt/completion per 1k tokens) and allow overrides via CLI `--price-table` and recipe `instrumentation.price_table`.
- Extend `schemas.py` with `LLMCallUsage`, `StageInstrumentation`, `RunInstrumentation`; wire `SCHEMA_MAP["instrumentation_run_v1"]`.
- Add helper in `modules/common/utils.py`: `log_llm_usage(event: dict | params...)` that writes to `INSTRUMENT_SINK` if set; no-op otherwise; include basic validation.
- Update `driver.py`:
  - Parse flags: `--instrument`, `--instrument-config`, `--price-table`.
  - Load instrumentation settings from recipe override, default off.
  - Create sink path and pass env vars into stage subprocess.
  - Wrap stage execution to record timing, parse sink for stage events, compute cost, and emit incremental `instrumentation.json`.
  - Add `instrumentation.md` rendering (table of stage times/costs, per-model totals); include link in manifest and progress extras.
- Add validator/smoke test script (e.g., `tests/test_instrumentation_schema.py` or CLI check) ensuring JSON conforms and pricing table loads.
- Update docs (`README` + story doc note) with enablement example: `python driver.py --recipe ... --instrument --price-table configs/pricing.default.yaml`.

## Work Log
### 20251122-1424 — Created instrumentation story stub
- **Result:** Success; added story entry and acceptance/tasks for pipeline timing & cost instrumentation.
- **Notes:** Need to design schema and driver hooks next.
- **Next:** Draft instrumentation schema and price table format; plan driver integration approach.
### 20251122-2248 — Reviewed story scope and checklist
- **Result:** Success; confirmed Tasks section already enumerates instrumentation work items and aligns with acceptance criteria.
- **Notes:** No structural gaps spotted; schema design and driver hook decisions remain open.
- **Next:** Draft detailed instrumentation schema and price table fields, then propose driver integration points.
### 20251122-2250 — Drafted instrumentation design outline
- **Result:** Success; added design draft covering report files, JSON shape, stage metrics, LLM usage sink, pricing config, and enablement knobs; expanded tasks for module helper and manifest linking.
- **Notes:** Driver plan uses perf_counter + resource deltas; modules to emit per-call usage via new helper writing to driver-provided sink.
- **Next:** Refine schema fields into `schemas.py`/report validator and sketch driver aggregation steps.
### 20251122-2253 — Added schema draft and driver aggregation plan
- **Result:** Success; drafted Pydantic classes for run/stage/call instrumentation plus driver aggregation algorithm steps.
- **Notes:** Plan includes sink env vars, interim JSON writes, pricing table load, and handling failures.
- **Next:** Map draft classes into `schemas.py` addition and decide on price table file location/name.
### 20251122-2255 — Added implementation plan checklist
- **Result:** Success; outlined concrete implementation steps (pricing file, schema wiring, utils helper, driver flags/aggregation, validator, docs).
- **Notes:** Implementation plan leans on incremental JSON writes and manifest linking; price table path set to `configs/pricing.default.yaml`.
- **Next:** Start editing `schemas.py` to add instrumentation models and wire `SCHEMA_MAP`.
### 20251122-2256 — Added instrumentation schemas to code
- **Result:** Success; added `LLMCallUsage`, `StageInstrumentation`, `RunInstrumentation` to `schemas.py` and registered them in `validate_artifact.py`.
- **Notes:** Stage schema uses `schema_version_output` to avoid clobbering core `schema_version`; token counts validated non-negative.
- **Next:** Add price table file, utils helper for sink logging, and driver flags/wiring.
### 20251122-2258 — Added pricing default and module usage helper
- **Result:** Success; created `configs/pricing.default.yaml` with default OpenAI model rates and added `log_llm_usage` helper in `modules/common/utils.py` to append events to an env-provided sink.
- **Notes:** Helper is a no-op when env is unset; writes schema_version `instrumentation_call_v1`.
- **Next:** Wire driver flags/env propagation and stage timing aggregation; render instrumentation report.
### 20251122-2259 — Wired driver instrumentation scaffolding
- **Result:** Success; added CLI flags `--instrument`, `--price-table`, pricing loader, cost calc, per-stage timing aggregation, env propagation to modules, sink parsing, run/stage report writing (`instrumentation.json`/`instrumentation.md`), manifest linking, and force cleanup of sink.
- **Notes:** Stage instrumentation logs on skip/mock/done/fail; markdown includes per-model and per-stage cost/time tables; run totals accumulate per-model.
- **Next:** Add validation test and doc updates; consider offset-based sink reading to avoid reread for huge runs.
### 20251122-2305 — Added instrumentation tests and docs
- **Result:** Success; added `tests/test_instrumentation_schema.py` for schema round-trip and validation guard, plus README instrumentation section.
- **Notes:** Pytest passing locally; validation covers negative token guard.
- **Next:** Consider sink incremental parsing optimization and ensure driver uses manifest links in dashboard (future).
### 20251122-2309 — Optimized sink parsing and surfaced dashboard links
- **Result:** Success; driver now reads new instrumentation sink events incrementally (byte offset) into per-stage buffers, avoiding re-reads; dashboard shows instrumentation report links from manifest.
- **Notes:** Added `runMeta` cache in dashboard manifest loader; summary now includes JSON/Markdown links when present.
- **Next:** Optional: add dashboard preview of cost/timing from instrumentation.json; monitor sink growth for extremely large runs.
### 20251122-2328 — Added dashboard cost preview
- **Result:** Success; dashboard now fetches `instrumentation.json` when present and shows LLM cost summary plus top models in the summary cards.
- **Notes:** Reuses manifest instrumentation paths; caches instrumentation per run.
- **Next:** Consider stage-level cost overlays and incremental sink growth monitoring.
### 20251122-2329 — Added stage-level cost/time chips in dashboard
- **Result:** Success; stage cards now show instrumentation cost and wall time when available (pulled from instrumentation.json).
- **Notes:** Instrumentation stages mapped by id; chips appear alongside module/schema badges.
- **Next:** Monitor sink growth for huge runs; optional: include per-stage call counts.
### 20251122-2346 — Fixed metrics pane width regression
- **Result:** Success; metrics loader now reuses the existing pane open logic, so the right-hand panel opens at full width instead of a thin sliver; metrics preview renders with syntax highlighting.
- **Notes:** Pane buttons now set open-tab dataset for metrics view.
- **Next:** Add per-stage call counts chip if helpful.
### 20251122-2351 — Unified instrumentation summary + pane details
- **Result:** Success; dashboard summary card now shows run-level cost/calls/tokens and top models, with links to JSON/MD reports; stage “View in pane” now displays cost/call/time chips from instrumentation data.
- **Notes:** Reuses existing pane flow; adds helper to fetch stage instrumentation by id.
- **Next:** Maybe add per-stage call counts chip in the card grid; monitor UI spacing for long model lists.
### 20251122-2354 — Added instrumentation fallback and stage tokens
- **Result:** Success; dashboard now attempts to load `instrumentation.json` even if manifest lacks paths, shows “not available” message when absent, and adds tokens chip to stage detail pane; summary card still shows costs when data exists.
- **Notes:** Handles older runs without instrumentation gracefully.
- **Next:** Verify layout once an instrumented run is available; consider stage card call-count chip.
### 20251122-2355 — Ran instrumented mock recipe for dashboard check
- **Result:** Success; ran `recipe-text.yaml` with `--instrument --mock --force` producing `output/runs/deathtrap-text-ingest/` with instrumentation.json/md for UI verification (costs zero due to mock).
- **Notes:** Manifest entry includes instrumentation paths; stage/run timing populated.
- **Next:** Load the dashboard with this run to confirm cost/tokens display; consider adding per-stage call-count chip.
### 20251122-2358 — Run list sorted chronologically + auto-load latest
- **Result:** Success; manifest runs now sort oldest→newest and newest auto-loads on first view.
- **Notes:** Uses creation timestamps; falls back gracefully if missing.
- **Next:** Verify ordering/auto-load visually; add guard when manifest lacks timestamps if needed.
### 20251123-0002 — Fixed run dropdown ordering (newest first)
- **Result:** Success; run dropdown now sorts manifest entries by created_at descending and auto-selects newest; handles missing timestamps by pushing them last.
- **Notes:** Increased manifest window to last 100 entries.
- **Next:** Reload dashboard to confirm newest (`deathtrap-text-ingest`) auto-selects; adjust if manifest lacks created_at across many runs.
### 20251123-0006 — Added timestamp fallback for manifest sorting
- **Result:** Success; dropdown now fetches pipeline_state.json timestamps when manifest entries lack created_at, sorts newest-first from last 150 runs, and auto-selects newest reliably.
- **Notes:** Falls back to 0 if timestamps missing/unreadable.
- **Next:** Verify in UI that newest run is selected; trim fetch count if performance becomes an issue.
### 20251123-0012 — Manifest preference + enforce newest selection
- **Result:** Success; dashboard now prefers `run_manifest_cleaned.jsonl` (falls back to original), re-sorts newest-first using timestamps from state files, and auto-selects newest when current selection is missing/stale; manifest path surfaced in last-refresh text.
- **Notes:** Cleaned manifest regenerated with existing runs only.
- **Next:** Reload UI to confirm newest run auto-selected; adjust if further deletions occur.
### 20251123-0015 — Reverted to original manifest only
- **Result:** Success; dashboard now reads only `output/run_manifest.jsonl` (cleaned copy removed) while still sorting newest-first via state timestamps and auto-selecting newest.
- **Notes:** Last-refresh text shows manifest path; cleaned file trashed per request.
- **Next:** Verify newest run auto-selected after reload; adjust if manifest lacks timestamps.
### 20251123-0017 — Fixed timestamp parsing for run ordering
- **Result:** Success; manifest sorting now normalizes microsecond ISO stamps to millisecond precision before Date.parse, preventing NaNs that previously forced all runs to ts=0 and kept old ordering.
- **Notes:** Applies to both manifest and pipeline_state timestamps.
- **Next:** Reload dashboard to confirm newest run auto-selects; if still off, log actual ts values for debugging.
### 20251123-0020 — Use max stage timestamps for run ordering fallback
- **Result:** Success; manifest sorting now falls back to the latest stage `updated_at` when run-level timestamps are missing, so rerun stages bubble the run to the top.
- **Notes:** Keeps newest-first ordering without rewriting the manifest.
- **Next:** Hard refresh dashboard to verify newest auto-selection; if still wrong, log resolved timestamps per run.
### 20251123-0022 — Forced dropdown display order (newest first)
- **Result:** Success; options are now appended in newest-first order so the latest run appears at the top of the dropdown, matching auto-selection logic.
- **Notes:** Sorting uses timestamp fallbacks; display order now aligns with computed newest.
- **Next:** Confirm visually that latest run is first and selected; if still off, log resolved timestamps per run.
### 20251123-0025 — Auto-select newest unless user picks
- **Result:** Success; added `userSelectedRun` flag so the dashboard auto-selects the newest run on load/refresh unless the user explicitly changes the dropdown; timestamp sorting unchanged.
- **Notes:** Prevents sticky selection of older runs across reloads.
- **Next:** Verify newest auto-selects after hard refresh; if still wrong, log resolved timestamps in UI.
### 20251123-0028 — Closed story bookkeeping
- **Result:** Marked all tasks complete and set story status to Done per user direction.
- **Notes:** Instrumentation feature set implemented; minor UI ordering quirk accepted as out of scope.
- **Next:** None.


## 2026-10-24 continuation: retain recorded spend across resume

### Goal

A logical run keeps its recorded API usage when processing resumes or artifacts
are rebuilt. Story210 exposed the current inconsistency: its four-event ledger
retains6144 input/1532 output tokens while a downstream-only resume overwrites the
summary with zero calls. Re-executing the same stage instead replays old calls
into that stage's new summary. Story022 owns the same driver instrumentation,
report contract and validation boundary, so reopen it rather than create another
story for this repair. The user authorized a continuing triage/build loop.

### Decision and scope

Story022 and dashboard Story100 explicitly promise run-level costs; no document
establishes invocation-only spend. C6 remains hold and B3 hold; this repair makes
existing artifact reuse inspectable without adding model calls. Spec2/8 substrate
exists. Search of `docs/decisions/` found no separate instrumentation ADR; this
is a repair to the existing declared contract, not a new persistence platform.
The graph's prior022 entry was Done with empty lineage; current refs now identify
that existing ownership. No format coverage or model/eval claim changes.

Problem class: rebuilding a derived summary from an append-only usage log after
restart. [Microsoft's event-sourcing guidance](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
describes event history as authority and snapshots as rebuildable projections;
its [materialized-view guidance](https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view)
distinguishes full rebuild from incremental updates. Adapt the full-rebuild
technique to this small existing JSONL sink; do not import an event framework.
Count each valid recorded row once per projection, including identical rows that
could represent separate requests. Missing request IDs prevent independent
provider-event deduplication. Preserve incomplete trailing rows for later reads,
and expose malformed/conflicting-run evidence instead of silently claiming a
complete total. A deterministic projection is the fit: model judgments add no
useful information to exact accounting.

Cumulative usage/cost and execution state are separate. Prior records may supply
known metadata/timing, but invalidated artifacts must not become valid because
cost survives. Run wall/CPU timing remains the current driver invocation;
stage timing is the latest recorded execution or unknown. Explicit event costs
remain authoritative; token-only costs are estimates under the displayed price
sheet, not historical billing receipts. Pricing refresh and missing provider
request IDs are separate from this replay-correctness repair.

### Acceptance criteria

- [x] Preserve a zero-provider failing reproduction of downstream resume omitting
  retained usage and same-stage accounting inconsistency.
- [x] Derive run/stage recorded call/token/cost totals from the retained ledger,
  with stable repeated refreshes, no double addition of old summary totals, and
  no loss of failed/rerun/forced-rebuild recorded costs for the same run ID.
- [x] Reconstruct usage after only the summary is removed; a different run ID
  remains separate. Preserve invalidated-artifact state and explicitly label
  timing/estimate scope and incomplete ledger evidence.
- [x] Add driver integration and narrow projection controls, including failure,
  forced rebuild, identical distinct rows, foreign/malformed rows and incomplete
  final lines. Existing instrumentation/report consumers remain compatible.
- [x] Run a real provider-free driver sequence under `output/runs/`, open both
  JSON and Markdown reports and manually reconcile them to the event rows.
- [x] Validate affected driver/report consumers, update docs/work log/changelog
  and generated methodology views, and close via `/mark-story-done`.

### Tasks and plan

- [x] Diagnose source contract from Story022/100, driver, schemas, tests,
  state/graph/spec and the actual Story210 mismatch.
- [x] Compare established approaches and choose ledger-derived full replay;
  continuing strategy reviewer `/root/resume_strategy` accepted the bounded
  plan with preservation, status, timing, estimate and malformed-tail conditions.
- [x] Add the failing provider-free driver tests before runtime changes.
- [x] Implement a narrow shared projection helper and wire current live/final
  driver reports to it; keep ledger history through forced artifact rebuilding.
- [x] Prove controls and manually inspect a real driver report sequence.
- [x] Update docs, run applicable validation and close the story.

### Workflow Gates

- [x] Build complete
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

### Central Tenets

- [x] T0: raw recorded usage remains traceable; summaries are derived.
- [x] T1: exact counting/pricing uses code; no semantic AI decision added.
- [x] T2: failing local reproduction precedes implementation; no model eval needed.
- [x] T3: original event bytes survive resume/rebuild unchanged.
- [x] T4: shared projection fits existing schema/report consumers.
- [x] T5: actual driver JSON/Markdown and event rows manually inspected.

### Continuation work log

20261024 — selected from fresh post-Story210 triage. Top three: accounting
consistency (new observed mismatch), authentic scanned-prose qualification
(larger product gap, pending trustworthy reference), fresh cleanup scan (no
new concrete defect). One zero-call diagnosis established the hybrid semantics;
fixing it precedes further paid proof work. Neutral packet by lower-cost
`/root/resume_inbox_health`; driver test worker `/root/resume_stories_architecture`
uses gpt-6.1-sol/high for the cross-process boundary. Parent owns runtime/docs and
final quality. No new commits, provider calls or dependency changes planned.


20261024 — reproduction and implementation: the first applicable provider-free
baseline failed4/5 integration cases (`output/triage-20261024-instrumentation-audit/baseline.log`).
Downstream resume retained one raw event but reported zero; same-stage rerun
retained3 events/USD0.625 but reported2/USD0.50; repeated zero-call resumes omitted
other stages; forced rebuilding erased the ledger. A new run ID control passed.
The shared `modules/common/run_instrumentation.py` now rebuilds stage/run usage
from complete valid ledger rows. Forced artifact cleanup retains that ledger.
Reports preserve known stage metadata without restoring invalidated artifacts,
expose incomplete/foreign/malformed records, and retain explicit cost versus
price-sheet estimate distinctions. No provider, pricing-default or schema change.
The dashboard consumes the same fields, labels recorded cost, and warns on a
partial ledger. Touched driver lint cleanup removed unused imports/variables and
redundant string interpolation only.

20261024 — findings-first review: `/root/resume_evals` found skipped stages lost
actual execution timings. A stamped PageDoc regression reproduced this and also
showed a second `--skip-done` reran both stages because the first skip changed
state from done to skipped. The original ElementCore fixture did not meet the
schema reuse gate and is explicitly excluded from evidence; applicable failures
are preserved in `skip-baseline-v2.log`. Skipped timing now retains the latest
known execution or stays unknown; valid done/skipped artifacts remain eligible
for reuse with existence/schema checks. Independent bounded rereview found the
accepted issue resolved and no critical related issue. No additional audit or
provider calls were launched after the user requested finish/push/stop.

20261024 — real driver proof and manual inspection: resumed the existing
`output/runs/story210-20261024-degraded-fullpath` from `portionize_toc`, without
OCR or any provider call. Original report and ledger hash are preserved in
`output/triage-20261024-instrumentation-audit/before-prose-*`; the new JSON/Markdown
reports reconcile exactly to the unchanged four raw events:6144 input tokens,
1532 output tokens, estimated USD0.023 under the explicit run-local GPT5.1
standard price sheet. Original generic-default price estimate remains retained
in the Story210 audit. `prose-reconciliation.json` records the unchanged ledger
and totals. Manual report inspection confirmed `ocr_ai` owns all4 calls and its
lost historical timing is unknown, while the two resumed stages have zero calls
and current timings. Browser inspection of the actual dashboard showed Recorded
Cost USD0.0230, Calls4, Tokens6144/1532, with the estimate/reuse scope text.
The older dashboard progress panel still treats the resume-invalidation warning
as running and mixes event intervals; that pre-existing status-display issue is
outside this accounting repair and was not expanded after the user's stop.
Preview server/tab were stopped. Source/export data stayed unchanged.

20261024 — `/validate`: Grade A for this bounded accounting contract; all6
continuation AC groups met. Final tests:25 accounting/projection/schema tests
(including10 real-driver integration controls) passed21.26s;69 affected driver,
resume, merge, plan, admission, provenance, reference-repair, run-registry,
run-config, handwritten-eval report consumer and dashboard-path tests passed22.38s.
`make lint` and explicit driver Ruff pass. Full-suite repetition is unnecessary:
only the instrumented accounting path, force ledger retention and valid skipped
artifact reuse changed; all driver integration paths and identified report
consumers were covered. The preceding274 export tests remain applicable to their
unchanged module behavior. No new model eval or golden; registry unchanged.
Learning review considered: no new workflow candidate; existing applicable-proof
and provider-free regression requirements cover the findings. Closure
recommendation: Close now, with historical usage gaps and price estimates explicit.

20261024 — `/mark-story-done`: all continuation tasks/ACs and T0–T5 verified,
workflow gates checked, existing changelog entry extended and generated graph/
index refreshed. The user now explicitly requests finishing, validation, commit,
push and then stopping; return to `/finish-and-push`, with no next triage build.
