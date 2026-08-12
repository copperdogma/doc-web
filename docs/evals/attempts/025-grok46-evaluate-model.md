# Attempt 025 — Grok 4.6 crop evaluation

**Eval:** `image-crop-extraction`, conditionally `crop-page-level-deletion-gate`
**Date:** 2026-08-12
**Worker Model:** Codex GPT-5
**Subject Model / Surface:** OpenRouter `x-ai/grok-4.6`, xAI provider, maintained crop ladder
**Mission:** Determine whether Grok 4.6 repairs Grok 4.5's source-verified crop-detector failures and, only if so, whether it clears the page-context safety gate.
**Registry Lineage:** detector `story_refs: [133, 183, 207]`, `category_refs: [spec:4, spec:8]`, `compromise_refs: [C4]`; conditional page context `story_refs: [209]`, `category_refs: [spec:4, spec:8]`, `compromise_refs: [C5]`.

## Interpreted brief and ownership

This is an execution request and a fresh candidate run, not a planning-only audit. The exact candidate is the authenticated OpenRouter route `x-ai/grok-4.6`; the catalog maps it to xAI's `x-ai/grok-4.6-20260810` endpoint family. Direct xAI credentials are not configured in doc-web, so the repo-scoped OpenRouter credential is the narrowest authorized access path. No model, tier, provider, or snapshot substitution is allowed.

The 13-case detector remains owned by Story 207. The materially distinct 22-case page-context surface remains owned by Story 209 and is locked until the detector passes all `13/13` cases and reaches `overall >= 0.95`. This continuation shares the existing subsystem and validation boundaries, so no new story is warranted.

## Alignment and current decision surfaces

- Ideal alignment: a stronger single-call detector pressures C4 toward deletion while preserving source fidelity and inspectable evaluation evidence.
- Current phase: `spec:4` substrate `exists`; C4 is `converge`; C5 is `climb`. This run measures whether the new subject can simplify the bounded crop residue without adding runtime complexity.
- Detector runtime default: the executable Onward recipe uses `gemini-3-flash-preview` as `rescue_model`.
- Best eligible detector evidence: Gemini 3 Flash `13/13`, `overall = 0.9703`, about `7878 ms/case`, about `$0.059` total.
- Page-context runtime/eval default and best eligible evidence: OpenAI Responses `gpt-5.5`, hard `22/22` contract.
- No new ADR is needed: this is a bounded model-selection measurement with frozen contracts and no authorized default or architecture change.

## Frozen matrix and stop rules

| Surface | Candidate configuration | Comparator | Entry / decision gate |
| --- | --- | --- | --- |
| `image-crop-extraction` | `x-ai/grok-4.6`, provider `xAI`, low reasoning with reasoning excluded, strict `crop_regions` schema, `max_tokens=16384`, `conservative-count`, public checked-in fixtures, no cache, concurrency 1 | Reuse maintained Gemini 3 Flash proof; no fresh superiority claim | Advance only at `13/13` and `overall >= 0.95` |
| `crop-page-level-deletion-gate` | Same pinned route, strict `page_context_validation`, frozen page-context prompt/scorer/golden, no cache, concurrency 1 | Maintained GPT-5.5 `22/22`; fresh control only if a decision-changing superiority/value claim becomes plausible | Hard contract `22/22` |

Before scoring, transport must prove exact served model and provider, terminal `finish_reason=stop`, valid usage/cost, strict schema, lossless image normalization, and PromptFoo parity. The adapter must send `allow_fallbacks=false`, `require_parameters=true`, `data_collection=deny`, and `zdr=true`. Public checked-in fixtures are eligible; no private material is authorized.

This is candidate-only fresh evidence. It may establish that Grok 4.6 passes or fails the maintained gates, but it cannot by itself support a contemporaneous superiority claim over an incumbent. Maintained prompts, fixtures, scorers, goldens, and runtime defaults are frozen. At most two evidence-led transport/configuration repairs are allowed. Total paid-call spend is capped at **US$5** across probes, subjects, retries, and any conditional control. Stop immediately if pricing or identity cannot be bounded or attributed.

## Provider contract and provenance before spend

- Starting clean HEAD: `e117c0da16d9516e3cb782f4a11f89fc30bc03c3`.
- Authenticated OpenRouter catalog on 2026-08-12: exact route `x-ai/grok-4.6`; xAI endpoint snapshot label `x-ai/grok-4.6-20260810`; text, image, and file input; text output; 500,000-token context; strict structured-output and reasoning parameters listed.
- Standard pricing: `$2/M` prompt, `$0.50/M` cache read, `$6/M` completion; above 200k prompt tokens: `$4/M`, `$1/M`, `$12/M`. The maintained crop cases are far below the long-context threshold.
- OpenRouter's current provider-routing documentation supports `allow_fallbacks`, `require_parameters`, `data_collection`, and per-request `zdr`; the live endpoint catalog exposes xAI ZDR endpoints for this model.
- Public xAI docs did not yet expose a reliable Grok 4.6 model page during the pre-spend check. The authenticated catalog plus exact served-response evidence are therefore mandatory, and the access path is recorded as OpenRouter rather than misrepresented as direct xAI.
- Frozen detector hashes: task `7edae5fe3c935517396a8d37cd8f148cb2b592ed4d206168dbb62273d758cf3e`; prompt `9a22e566f30eac6258a78a28107d77a17940eca06858dd20cb8d7bc97fc84aba`; scorer `7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7`; golden `2ac0a8f01e00a252439da1f4827a85bc5118bf96460a3ff1780e642eafc60f90`.
- Conditional page-context hashes: task `b2b8d2ca4cfd48a09936764715941d914d5c1e4e6115e30d7916fe2ebe770e63`; prompt `2ccc8c96ef69c14102d7ffd13b5a39715e5cd136b497510b1b2f88243009a5a0`; scorer `12eb63725523bd00d59ce12b7486db8c9244124a0c57bb68cae8b8e9e7d288fb`; golden `4bcba8f4ab8a742608e7cfc1438464a71cf56aa4cd9cbe9e0a67e4a410ac18a5`.

## Spend ledger

| Stage | Successful-call spend | Status |
| --- | ---: | --- |
| Catalog and endpoint discovery | `$0.000000` | Complete; read-only API calls |
| Access / contract / parity probes | `$0.013924` | Qualified |
| 13-case detector | `$0.072818` | Failed quality gate |
| Conditional 22-case page context | `$0.000000` | Not run |
| **Total** | **`$0.086742`** | Below `$5` cap |

## Work log

20260812-1627 — pre-spend contract: read the alignment, registry, prior Grok 4.5/Qwen challenger evidence, frozen tasks/prompts/scorers/goldens, provider adapters, and crop runbook. Authenticated catalog discovery resolved only `x-ai/grok-4.6` through xAI endpoints and exposed an eligible ZDR route. Added fail-closed per-request ZDR and data-collection denial to the existing generic OpenRouter vision adapter. No paid inference has occurred. Next: validate the adapter change, then run exact-model text, synthetic-image strict-schema, and one-case PromptFoo parity probes.

20260812-1630 — transport qualification: exact-model strict text returned `{"images":[]}` with xAI provider, terminal stop, valid usage, and `$0.001858` cost. The first image request received HTTP 400 `invalid_image` before inference because the checked-in fixture already contained a data-URL prefix and the probe added a second prefix; correcting that one input-shape variable produced a strict image response with exact identity and `$0.005968` cost. The frozen `Image000` PromptFoo parity smoke then passed at `1.0000`, `2884 ms`, and `$0.006098`. Classification: transport/harness input formatting, repaired before scoring; no semantic evidence came from the 400 response.

20260812-1633 — detector and source review: the full no-cache, concurrency-1 detector completed `11/13`, `overall = 0.8414`, `0` provider/schema errors, `3260 ms` average latency, and `$0.072818` total subject cost. Inspected all 13 row scores and outputs, then opened the two failing source images against the frozen golden. `Image011` (`0.5992`) returned the anniversary logo plus a seal-only crop `[0.130, 0.710, 0.399, 0.920]`, omitting the signatures required by the source-backed combined region `[0.119804, 0.686061, 0.876863, 0.896667]`. `Image021` (`0.6639`) returned `[0.074, 0.475, 0.44, 0.752]`, cutting off the top/right of the portrait and extending into the page caption instead of the source-backed `[0.107255, 0.433182, 0.478627, 0.666667]`. Both are prompt/pipeline-wrong -> model-wrong; neither golden nor scorer changed. No high-reasoning rescue was justified because the frozen low arm decisively failed, Grok 4.5 high reasoning previously repaired neither analogous miss, and tuning on decision cases would not create promotion-grade evidence.

## Detector result

| Candidate | Structural result | Source review | Avg latency | Subject cost | Decision |
| --- | --- | --- | ---: | ---: | --- |
| Grok 4.6 / OpenRouter xAI / low | `11/13`, `0.8414`, `0` errors | `Image011` and `Image021` model-wrong | `3260 ms` | `$0.072818` | Do not adopt |
| Maintained Gemini 3 Flash evidence | `13/13`, `0.9703` | Maintained source-backed proof | about `7878 ms` | about `$0.059` | Retain runtime |

The task has a deterministic structural scorer but no active semantic rubric assertion; its stale YAML comment names a judge that the assertions do not invoke. Adding a rubric after predeclaration would change the frozen surface, so direct source inspection supplies the semantic classification. Grok 4.6 repaired Grok 4.5's `Image001` miss but repeated the safety-relevant `Image011` grouping failure and introduced the `Image021` caption/undercoverage miss. It was faster than the maintained evidence but worse in quality and slightly more expensive on the 13-case subject run.

## Progressive stop and adoption

- Detector access: **available** through repo-scoped OpenRouter.
- Detector transport: **qualified** with exact Grok/xAI identity, strict schema, terminal stop, ZDR, data denial, and reported usage/cost.
- Detector reliability: **acceptable**, `0` provider/schema errors in the scored run.
- Detector capability: **worse** than the maintained winner and below target.
- Detector adoption: **do not adopt**.
- Page-context capability: **not measured** because the detector prerequisite failed.
- Page-context adoption: **defer / not advanced under the declared ladder**.
- Runtime/default changes: none.

## Evidence and reproduction

Ignored raw results:

- `benchmarks/results/grok46-harness-smoke-20260812.json` — SHA-256 `396c7229a1d28efffaf039cc1cce505002c7a68164e0a01c06c0ed711c8cd12e`, `1,205,287` bytes.
- `benchmarks/results/grok46-image-crop-extraction-20260812.json` — SHA-256 `ec9228b3aa51d6b3c9bbee945f43339ed8c1f302f1c347a2e355a7553545f273`, `9,648,358` bytes.

Both PromptFoo runs used version `0.121.1`, the repo credential wrapper, `--no-cache`, and concurrency `1`. The detector command was:

```bash
cd benchmarks && OPENROUTER_VISION_MODEL=x-ai/grok-4.6 OPENROUTER_VISION_EXPECTED_MODEL=x-ai/grok-4.6 OPENROUTER_VISION_EXPECTED_PROVIDER=xAI OPENROUTER_VISION_REASONING_EFFORT=low OPENROUTER_VISION_MAX_TOKENS=16384 PROMPTFOO_EVAL_TIMEOUT_MS=240000 ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --providers "python:$(pwd)/providers/openrouter_vision_chat.py" --filter-prompts conservative-count --no-cache --output results/grok46-image-crop-extraction-20260812.json -j 1
```

## Result

**Failed. Do not adopt Grok 4.6 for the maintained crop detector.** It remains ineligible for the page-context gate. Retry only after a materially revised Grok snapshot; do not rescue this result by changing the prompt, scorer, golden, grouping rule, or reasoning setting on the observed decision cases.

## Validation

- Registry YAML parsed successfully with the repo's configured Python.
- Focused provider and crop-substrate tests: `12 passed`.
- `make lint`: passed.
- `make methodology-compile` and `make methodology-check`: passed.
- Full `make test`: `936 passed, 4 warnings in 808.47s`; warnings are the existing Pydantic `dict()` deprecations in `portionize_headers_numeric_v1`.
- `git diff --check`: passed.
- No `driver.py` run was applicable because no production pipeline module, recipe, schema, or runtime default changed.

## Definition of Done

- [x] Read the target evals' prior attempts and explicit lineage
- [x] Record the decision contract before provider spend
- [x] Qualify exact access, strict multimodal transport, and harness parity
- [x] Run and inspect the frozen detector
- [x] Run page context only if the detector prerequisite passes (not run; prerequisite failed)
- [x] Classify every material mismatch against source evidence
- [x] Update `docs/evals/registry.yaml` and owning story work logs
- [x] Regenerate and validate methodology surfaces

## Sources

- <https://openrouter.ai/docs/guides/routing/provider-selection>
- <https://openrouter.ai/docs/guides/features/structured-outputs>
- <https://openrouter.ai/docs/guides/features/zdr>
- <https://docs.x.ai/developers/rest-api-reference/inference/models>
