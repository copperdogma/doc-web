# Attempt 053 evidence: Grok 4.7 reasoning calibration

This is tracked evidence for a fresh, bounded Doc Web detector calibration on Image001 and Image059. It contains response envelopes, a final settlement ledger, per-case result extraction, the exact adapter wrapper used, preflight/source hashes, and source-page overlays. The original Promptfoo JSONs embed the public fixture images, so they remain in the ignored worktree results directory; their byte sizes and SHA-256 values are recorded in `original-promptfoo-results.json`. The checked-in `case-results.json` retains the per-case scores, outputs, latency, and settled cost without duplicating input image payloads.

`raw/` retains all eight actual xAI Responses envelopes; `native-low-probe.json` and `parity-low-probe.json` point to the two synthetic qualification envelopes. Portable `raw/` paths and response hashes are in `ledger.json`; `ledger-original.json` preserves the original run ledger byte-for-byte, including its local absolute pointers. `original-promptfoo-results.json` records hashes and byte sizes for the ignored original run outputs and control files. `sha256-manifest.json` hashes all files in this directory except itself. The `visual-review/` overlays draw golden boxes in green and model boxes in red. The two `source-*.jpg` files are source-page previews derived from the repository's tracked base64 fixtures.

The ledger records eight actual requests settled for `$0.075754`, zero unresolved charges, and one overlapping reservation event reconciled to the low/Image001 provider receipt. Two relative-path coordination bookkeeping attempts ran from the wrong cwd and did not update the intended ledger at the time; the later reconciliation preserves the original event and links it to the real provider response. No provider call was repeated to repair bookkeeping.

The original per-call reservation used a 500,000-token input ceiling and the requested 8,192-token output ceiling at the official xAI long-context prices, reserving `$2.098304`. After this run, a separate Dossier receipt showed xAI can report combined output above a requested output cap. Thus the historical reservation mechanism and actual settlement remain documented, but `$2.098304` is not claimed as a proven theoretical maximum for future xAI requests. These eight responses each reported completion usage at or below 1,140 tokens, and actual aggregate charges remained below the campaign's `$5` ceiling. No actual over-bound response, unresolved charge, or spend above the cap was observed in this Doc Web run.

## Source provenance

Base revision: `b90c0da0f95eff852eeaea16419051a0b0a2e10d` in isolated worktree `/Users/cam/.codex/worktrees/grok47-docweb-reasoning-20261002`. `source-hashes.json` gives SHA-1 Git blob IDs, SHA-256, and byte counts for the maintained provider, prompt, scorer, golden, task, and image helper. The isolated run wrapper is copied here as `xai_grok_responses_budgeted.py`; its SHA-256 is in the manifest. No tracked owner code, prompt, scorer, golden, runtime default, or evaluation configuration was changed for the run.

The provider key was supplied to the owner worktree through the Conductor credential helper for the authorized run, then removed. A name-only post-cleanup check confirmed that the ignored owner `.env` contains no `XAI_API_KEY` entry. No credential value is present in this evidence directory.

The exact wrapper snapshot passed `python -m py_compile`. Ruff check on that preserved historical source reported `E401`, `F401`, and `E702` formatting/import findings; the snapshot was not reformatted because its bytes must remain an exact record of the code used for these receipts. No maintained runtime provider or executable repository source changed in this campaign.

## Calibration commands

The following command form records the fresh Promptfoo calls. It was run serially (`-j 1`) once for each effort. The API credential was present in the owner worktree `.env` at execution and is intentionally omitted here. Paths and environment settings resolve to the recorded worktree and ledger; the original ignored Promptfoo outputs are hashed in `original-promptfoo-results.json`.

```bash
cd /Users/cam/.codex/worktrees/grok47-docweb-reasoning-20261002/benchmarks
GROK47_BUDGET_LEDGER=/Users/cam/.codex/worktrees/grok47-docweb-reasoning-20261002/benchmarks/results/grok47-reasoning-20261002/ledger.json \
XAI_GROK_MODEL=grok-4.7 \
XAI_GROK_EXPECTED_SERVED_MODEL=grok-4.7 \
XAI_GROK_REASONING_EFFORT=low \
XAI_GROK_MAX_OUTPUT_TOKENS=8192 \
XAI_GROK_IMAGE_DETAIL=high \
XAI_GROK_RAW_ENVELOPE_DIR=/Users/cam/.codex/worktrees/grok47-docweb-reasoning-20261002/benchmarks/results/grok47-reasoning-20261002/raw \
PROMPTFOO_EVAL_TIMEOUT_MS=120000 \
../scripts/run_with_doc_web_env.py promptfoo eval \
  -c /Users/cam/.codex/worktrees/grok47-docweb-reasoning-20261002/benchmarks/results/grok47-reasoning-20261002/calibration.yaml \
  --providers python:/Users/cam/.codex/worktrees/grok47-docweb-reasoning-20261002/benchmarks/results/grok47-reasoning-20261002/xai_grok_responses_budgeted.py \
  --no-cache --no-share --no-table -j 1 \
  --output /Users/cam/.codex/worktrees/grok47-docweb-reasoning-20261002/benchmarks/results/grok47-reasoning-20261002/low-calibration.json
```

For the medium and high arms, only replace `XAI_GROK_REASONING_EFFORT=low` and the output basename with `medium` or `high`. The task YAML contains the unchanged maintained prompt and scorer and exactly the two public source cases. The native and adapter parity probes used one generated 128×128 black-square image each; their raw response envelopes and extracted receipts are retained. No provider calls were made during evidence packaging or validation.

## Case results

| Effort | Image001 | Image059 | Arithmetic case mean | Pair settled cost | Total case latency |
| --- | --- | --- | ---: | ---: | ---: |
| low | 0.0750, fail | 0.7918, pass | 0.4334 | $0.019836 | 17,613 ms |
| medium | 0.0750, fail | 0.9180, pass | 0.4965 | $0.022902 | 25,795 ms |
| high | 0.0750, fail | 0.6993, fail | 0.38715 | $0.024030 | 28,548 ms |

The values above are arithmetic means of the two case scores. Promptfoo's prompt-level aggregate is retained separately in `case-results.json`; it is not this arithmetic mean. Every effort fails the predeclared eligibility gate because Image001 fails. The existing golden correctly expects the decorative title artwork, confirmed independently by the supervising reviewer. No remaining11 full detector cases, Gemini comparison, page-safety cases, or adoption decision were performed.
