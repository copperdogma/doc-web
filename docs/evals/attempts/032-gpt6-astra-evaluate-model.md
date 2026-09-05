# Attempt 032 — GPT-6 Astra crop detector evaluation

**Eval:** `image-crop-extraction`, conditional `crop-page-level-deletion-gate`
**Date:** 2026-09-04
**Worker Model:** GPT-5.6 Sol
**Subject Model / Surface:** first-party OpenAI Responses `gpt-6-astra`; maintained `conservative-count` detector
**Mission:** Determine whether GPT-6 Astra can clear the maintained C4 detector gate and reopen the conditional C5 page-context decision.
**Registry Lineage:** Story 207 / Story 232; `spec:4`, `spec:8`; `C4`, conditional `C5`.

## Prior Attempts

The current comparable detector leader is GPT-5.6 Terra at `13/13`, `0.9689`, but its exact production check retained captions on two page-122 crops and left it production-ineligible. The maintained C4 reference remains Gemini 3 Flash at `13/13`, `0.9703`. The separate page-context C5 gate remains GPT-5.5 Responses at `22/22`. Recent Attempt 031 showed why transport, strict schema, quality, and economics must be gated separately before a costly follow-on.

## Predeclared Decision Contract

- Candidate: exact first-party model `gpt-6-astra`, Responses API, `reasoning.effort=low`, strict `crop_regions` JSON Schema, `store=false`, image detail `high`, and no sampling parameters.
- Official contract checked 2026-09-04: text and image input, text output, structured outputs, Responses support, low/medium/high/xhigh/max reasoning, 1,050,000 context, 128,000 maximum output, and short-context list prices of `$10/M` input, `$1/M` cached input, `$12.50/M` cache writes, and `$50/M` output. OpenAI says rollout begins with Trusted Access and broader API access follows in coming days, so authenticated callability remains a live gate.
- Frozen detector: `benchmarks/tasks/image-crop-extraction.yaml`, `benchmarks/prompts/crop-conservative-count.js`, `benchmarks/scorers/image_crop_scorer.py`, `benchmarks/golden/image-crops.json`; public checked-in fixtures only.
- Progressive ladder: free catalog/retrieval evidence; smallest native strict text call; smallest native strict generated-image call; one maintained PromptFoo parity case; one representative maintained case; then all 13 detector cases only if access, identity, terminal completion, strict schema, usage, spend, and parity remain valid.
- Detector entry gate: `13/13`, aggregate `>= 0.95`, zero transport/schema errors, and total repo-provider spend below the US$1.00 ceiling.
- Conditional follow-on: run the existing 22-case `crop-page-level-deletion-gate` only if the detector gate passes and conservative projected follow-on spend remains under the same ceiling. Do not recreate any absent uncommitted lane.
- Comparison claim: this candidate-first screen compares with maintained eligible evidence; no fresh incumbent is budgeted, so it cannot by itself support a contemporaneous superiority claim.
- Cache/concurrency/retries: `--no-cache`, `-j 1`, at most one evidence-led retry for a transient provider failure or one narrow adapter repair isolated by native success.
- Safety/privacy: no private input; no claim that `store=false` proves ZDR. Exact requested/served identity, terminal completion, complete output, strict local validation, and sane usage are mandatory.
- Spend ledger starts at `$0.00`; every successful inference call is priced from returned usage. Stop before any call whose conservative projection could cross `$1.00`.
- No default, runtime recipe, prompt, scorer, golden, commit, push, deploy, or provider-account change is authorized.

Official sources: <https://developers.openai.com/api/docs/models/gpt-6-astra>, <https://developers.openai.com/api/docs/guides/latest-model>, <https://developers.openai.com/api/docs/guides/your-data>.

## Work Log

20260904-0025 — contract frozen before inference: current official docs and clean-base owner surfaces were reviewed; repo discovery could not authenticate because it intentionally requires `DOC_WEB_OPENAI_API_KEY`, while the user authorized the existing process-level `OPENAI_API_KEY`. The owner wrapper preserves that existing process credential without copying or persisting it. Zero-cost syntax and dependency preflight passed using the established shared checkout environment. No paid call had occurred.

20260904-0028 — exact access stopped the ladder before inference: authenticated `GET /v1/models/gpt-6-astra`, executed through `scripts/run_with_doc_web_env.py`, returned HTTP `404`, `invalid_request_error`, code `model_not_found`, parameter `model`, and message `The model 'gpt-6-astra' does not exist`. The response is preserved at ignored mode-`0600` path `benchmarks/results/gpt6-astra-20260904/model-retrieve.json`, SHA-256 `7bea5c03cb640d285e9921662c06aa9ce8bc2eb6f7e7e0535b1402d84cb96d3e`; its parent directory is mode `0700`. No Responses inference request was made, so spend is exactly `$0.00`. Native generation, strict image contract, PromptFoo parity, representative fixture, 13-case detector, and 22-case page-context follow-on are all not measured. The temporary task-provider stanza used only to preflight config resolution was removed rather than adding an inaccessible arm to the maintained unfiltered task.

## Conclusion

**Result:** inconclusive — exact-model access blocked before inference

**Score before:** maintained Gemini 3 Flash `13/13`, `0.9703`; comparable detector leader Terra `13/13`, `0.9689` but production-ineligible; page-context incumbent GPT-5.5 Responses `22/22`.

**Score after:** not measured; authenticated access returned `404 model_not_found`.

**What worked:**
- Current first-party docs resolved the exact requested identity and call contract without substitution.
- Owner-wrapped authenticated retrieval produced a definitive account-level access result without exposing or persisting the key.
- The local adapter built the expected low-reasoning, strict-schema, `store=false` body with no unsupported sampling parameters.

**What did not work:**
- The authorized account cannot currently retrieve exact model `gpt-6-astra`; OpenAI's public page still describes a staged rollout.
- Because access failed, no valid subject output exists and no reliability, latency, semantic, or economic production evidence can be scored.

**What not to retry without new evidence:**
- Do not repeat inference, PromptFoo, detector, or page-context calls until authenticated model retrieval succeeds for the exact slug.
- Do not substitute another GPT-6 alias, snapshot, router, or GPT-5.6 tier for the requested model.

**Retry when:**
- `dependency-available`: authenticated `GET /v1/models/gpt-6-astra` returns exact ID `gpt-6-astra` for this account after the staged API rollout reaches it.

**Layered verdict:** access `blocked`; transport `not qualified`; reliability `not measured`; capability `not measured`; economics `not measured` except exact campaign spend `$0.00`; adoption `defer`.

## Definition of Done

- [x] Read the target eval's prior attempts first
- [x] Confirm the eval's explicit lineage fields in `docs/evals/registry.yaml`
- [x] Confirm current recorded baselines and freeze the decision contract
- [x] Record after-state metrics or a classified access/transport stop
- [x] Update `docs/evals/registry.yaml`
- [x] Classify major mismatches when the eval uses a golden — no subject output or golden mismatch existed
- [x] Fill in the Conclusion section completely
- [x] Document retry conditions or dead ends if the attempt fails
