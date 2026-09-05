# Attempt 033 — GPT-6 Astra crop reasoning frontier

**Eval:** `image-crop-extraction`, conditional `crop-page-level-deletion-gate`
**Date:** 2026-09-05
**Worker Model:** GPT-5.6 Sol
**Subject Model / Surface:** first-party OpenAI Responses `gpt-6-astra`; maintained `conservative-count` detector
**Mission:** Determine which GPT-6 Astra reasoning effort, if any, is Pareto-efficient for the maintained crop detector and whether it earns the conditional C5 page-context gate.
**Registry Lineage:** Story 207 / Story 232; `spec:4`, `spec:8`; `C4`, conditional `C5`.

## Prior Attempt and Changed Trigger

Attempt 032 stopped at exact-model retrieval on 2026-09-04 with `404 model_not_found` and zero spend. Its narrow retry trigger is now satisfied: an owner-context authenticated retrieval returned exact ID `gpt-6-astra` on 2026-09-05. This attempt preserves Attempt 032 and uses a new raw-result identity.

## Predeclared Decision Contract

- Candidate: exact first-party Responses model `gpt-6-astra`; `low`, `medium`, `high`, `xhigh`, and `max` reasoning arms; strict `crop_regions` JSON Schema; `store=false`; image detail `high`; no sampling parameters.
- Maintained detector: unchanged `benchmarks/prompts/crop-conservative-count.js`, `benchmarks/scorers/image_crop_scorer.py`, and `benchmarks/golden/image-crops.json`. The campaign task only narrows the maintained prompt and adds explicit Astra arms; it does not change prompt or truth.
- Calibration case: public checked-in `Image001`, predeclared because its source-reviewed stylized-title artwork is a known frontier differentiator. All five effort settings run once, no cache, concurrency `1`.
- Selection: eliminate any contract-invalid, incomplete, failed, or strictly dominated effort. Treat calibration selection on a decision fixture as exploratory. Run the complete 13-case authoritative detector only for a Pareto-efficient survivor when observed spend plus a conservative projection stays below the ceiling.
- Detector gate: aggregate `>=0.95`, pass rate `>=0.90`, zero transport/schema errors, exact identity, and acceptable economics. Compare with maintained Gemini 3 Flash `13/13`, `0.9703`; Terra `13/13`, `0.9689` remains production-ineligible because its exact-runtime crops retained captions.
- Conditional C5 gate: run the unchanged 22-case `crop-page-level-deletion-gate` only if a full detector arm clears the detector gate and projected total spend remains below the same ceiling. The page-context target is `22/22`; current incumbent is GPT-5.5 Responses `22/22`.
- Qualification ladder: exact retrieval; minimal native strict-schema text call; minimal native strict-schema synthetic-image call; then PromptFoo parity on `Image001` before expanding the effort matrix.
- Freshness/fairness: all Astra subject calls are uncached. No fresh incumbent is budgeted, so this run can rank Astra against maintained eligible evidence but cannot claim contemporaneous superiority.
- Retry budget: at most one evidence-led retry for a transient provider failure or one narrow adapter repair after native success. No score-led prompt, schema, golden, or scorer tuning.
- Cost: US$1.50 hard ceiling across probes, all Astra arms, retries, and any conditional follow-on. Ledger starts at `$0.00`; stop before a call whose conservative projection could cross the ceiling.
- Privacy: only public checked-in fixtures and a synthetic probe image. `store=false` is recorded but is not treated as ZDR proof.
- Not authorized: private payloads, runtime/default changes, product prompt/scorer/golden changes, provider-account changes, commit, push, deployment, or broader rollout.

Official contract checked 2026-09-05: <https://developers.openai.com/api/docs/models/gpt-6-astra>, <https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra>, and <https://developers.openai.com/api/docs/guides/structured-outputs>.

## Work Log

20260905-0000 — contract frozen before inference: current remote base `18c8c1509ba015ea80a4f6b6a4294075944681a6`; reusable isolated branch `codex/gpt6-astra-eval-20260904`; public/synthetic fixtures only; US$1.50 hard ceiling; no paid call yet.

20260905-1003 — access and native contract qualified: authenticated exact-model retrieval returned HTTP 200 and ID `gpt-6-astra`. Native low-reasoning strict text returned `{"images":[]}` for `$0.001290`; native strict synthetic-image returned the semantically identical `{"images": []}` for `$0.001360`. The first version of the local probe incorrectly byte-compared those spellings; preserved raw evidence proved valid strict JSON, so the validator was repaired to parse JSON without purchasing a retry. This was harness-wrong, not model-wrong.

20260905-1009 — five-effort calibration complete on predeclared `Image001`: low `0.9939`, `3271 ms`, `$0.005744`; medium `0.9946`, `4135 ms`, `$0.007794`; high `0.9930`, `6735 ms`, `$0.016444`; xhigh `0.9939`, `7572 ms`, `$0.022244`; max `0.9940`, `13705 ms`, `$0.039294`. All arms were exact-identity, terminal, strict-schema passes. High, xhigh, and max were strictly dominated by medium. Low and medium stayed Pareto-efficient and advanced.

20260905-1012 — full detector and progressive stop: low passed `13/13`, `0.979562`, zero errors, `3556 ms` mean latency, `$0.431904`; medium passed `13/13`, `0.980392`, zero errors, `4134 ms`, `$0.434804`. Total campaign spend reached `$0.960878`, leaving `$0.539122`. The 22-case page-context gate did not run: each case contains a full page plus a crop, while the observed full-page input floor alone projects to `22 × 3167 × $10/M = $0.696740`, already above the remainder before crop-image or output tokens.

20260905-1015 — source inspection: manually opened canonical `Image000`. It is a decorative full book cover and the golden correctly requires `[0,0,1,1]`. Both Astra arms inset the box to roughly `[0.069,0.042,0.956,0.942]`, yielding about `0.83`; this is model-wrong undercoverage, not golden/scorer ambiguity. Other outputs retained correct counts and close source-reviewed boxes. No prompt, scorer, or golden changed.

20260905-1020 — credential and validation closeout: reused the already-present process `OPENAI_API_KEY` through `scripts/run_with_doc_web_env.py`; no credential file or variable was injected, copied, persisted, or removed. Raw results remain in the ignored mode-0700 campaign directory with mode-0600 files. YAML/result integrity checks, `make methodology-check`, focused provider/crop tests (`22 passed`), probe-script Ruff check/format, and repo `make lint` all passed.

## Resolved Matrix and Reproduction

- Base: `18c8c1509ba015ea80a4f6b6a4294075944681a6`; branch `codex/gpt6-astra-eval-20260904`.
- Frozen prompt SHA-256: `bca281e0fbe547e3f3ef049b436d87c73ed7bb066e86f51145fb444b48211b64`.
- Frozen scorer SHA-256: `7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7`.
- Frozen golden SHA-256: `2ac0a8f01e00a252439da1f4827a85bc5118bf96460a3ff1780e642eafc60f90`.
- Provider SHA-256: `f8b3b3f6b93c9ec4a0c0e20e496f8c2e2189179ec461bfac4cc0ac66dc643346`.
- Campaign task SHA-256: `c4fe58126d854d1fabb8d649f39f6439b440981b071abd4265124babe901a8e8`.
- Native probe behavior-producing SHA-256 after the JSON-validator repair:
  `58305140e7d066f02ec88659789f5fb5fd6bdbfc31b5a9b1c9c033b50d7ce7e9`;
  formatting-only current SHA-256:
  `b1757233f0ab628af5142c1adcfe06de9d43130e1025e7904c316734bf6fa278`.
- Resolved full matrix: one frozen prompt × 13 independent cases × selected low/medium providers = 26 rows; no model judge; Python structural scorer; subject cache disabled; concurrency one.

Run from `benchmarks/` with the repo environment wrapper and the documented list-price variables:

```text
OPENAI_RESPONSES_INPUT_PRICE_PER_1M=10 \
OPENAI_RESPONSES_CACHED_INPUT_PRICE_PER_1M=1 \
OPENAI_RESPONSES_OUTPUT_PRICE_PER_1M=50 \
PROMPTFOO_PYTHON=/Users/cam/Documents/Projects/doc-web/.venv/bin/python \
../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/gpt6-astra-crop-detector-20260905.yaml \
  --filter-providers 'GPT-6 Astra medium' --no-cache \
  --output results/gpt6-astra-20260905/detector-full-medium.json \
  --no-share -j 1
```

Protected ignored evidence (SHA-256):

- `model-retrieve.json`: `540785ff78587d6f67c53701b8949dfc7fe13a2761b58b414ab3150eabcc3c1c`
- `native-text-low.json`: `3d68b5d59673dac22e11acc04c5a91cb3ebba8b090406235b234acda85b4cb32`
- `native-image-low.json`: `ff3aab6ad1552ef937a58a0d56d28d60e790e8ef4e7e2aa05947464c85b0d40b`
- `parity-image001-low.json`: `6017e504357ffc9ae53947fece3ea8811186ee918562373cf31de06bbe4a9e48`
- calibration high/max/medium/xhigh respectively: `3eb43df3ae123dfeed5bb0b59ed5e9a4f6d3bb3c99f2582d5cf7ae0cdc86fb87`, `71bce1d3990ffeae35b6ae66aa413a4db19393a0b3e4b44b82abf68ef69a84ac`, `08f34e26a47dee1840159b8932767504f6d8decbbcda4effdb564e0579dbc590`, `c9ec788fa58599c5ae620ad6900be22d40f857461e7453f930dab8b5f56d5256`
- `detector-full-low.json`: `2d83c4098f7275ba0c9d904425a4a135bb2aea27dd6e816a9ba36bf987fa7b06`
- `detector-full-medium.json`: `a3c782daf7748371c6348b3c85b7cea6749be0d482c0646c3b82b7f2661c0eed`

## Spend Ledger

| Stage | Cost (USD) |
| --- | ---: |
| Native strict text | 0.001290 |
| Native strict synthetic image | 0.001360 |
| Image001 low parity/calibration | 0.005744 |
| Image001 medium | 0.007794 |
| Image001 high | 0.016444 |
| Image001 xhigh | 0.022244 |
| Image001 max | 0.039294 |
| Full detector low | 0.431904 |
| Full detector medium | 0.434804 |
| **Total** | **0.960878** |

No comparator, judge, retry, or page-context provider call was made.

## Conclusion

**Result:** detector succeeded; production adoption deferred pending the unmeasured page-context safety gate.

**Access:** available — exact authenticated retrieval and every inference response served `gpt-6-astra`.

**Transport:** qualified — native text, native image, and PromptFoo image parity all completed with strict API-enforced schemas, exact identity, valid usage, and no incomplete state. The probe's initial whitespace-sensitive local check was repaired offline from the preserved valid envelope.

**Reliability:** acceptable on the measured detector — 33/33 inference calls completed without provider, schema, or parser errors: two native probes, five calibration calls, and 26 full-detector calls. No retries were used.

**Capability:** better on the bounded detector. Low reached `0.979562`; medium reached `0.980392`, above maintained Gemini 3 Flash `0.9703` and production-ineligible Terra `0.9689`. Medium is the new bounded detector-quality leader. Page-context capability is not measured.

**Economics:** Astra is not the detector value leader. Medium was about `7.4×` the maintained Gemini run's recorded `$0.059` total, although it was faster in this run (`4134 ms` versus about `7878 ms`). Low was only `0.000830` behind medium and was faster (`3556 ms`), making both Pareto-efficient; high through max were dominated on the calibration case.

**Adoption:** defer. The detector prerequisite passed strongly, but this crop runtime treats caption and neighboring-visual exclusion as a hard gate. The approved cap prevented the required 22-case page-context measurement, so neither Astra effort is production-qualified and `gemini-3-flash-preview` remains unchanged.

**Evidence limit / smallest follow-up:** if Cam wants the adoption question completed, authorize a separate Astra page-context evaluation with a disclosed cap high enough for 22 two-image cases and a fresh GPT-5.5 comparator if contemporaneous superiority is required. The current result supports benchmark leadership only, not a runtime/default change.

## Definition of Done

- [x] Read the target eval's prior attempts first
- [x] Confirm the eval's explicit lineage fields in `docs/evals/registry.yaml`
- [x] Confirm current recorded baselines and freeze the decision contract
- [x] Record after-state metrics or a classified access/transport stop
- [x] Update `docs/evals/registry.yaml`
- [x] Classify major mismatches against source evidence
- [x] Fill in the Conclusion section completely
- [x] Document retry conditions or dead ends if the attempt fails
