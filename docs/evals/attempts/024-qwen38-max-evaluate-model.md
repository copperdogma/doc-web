# Attempt 024 — Qwen3.8 Max OpenRouter crop evaluation

**Date:** 2026-08-04
**Worker:** Codex
**Base SHA:** `b97870faa44fecc5710c02faa4d9b25a73b93388` (evaluated dirty state described below)
**Owner:** Stories 207 and 209; `image-crop-extraction` first, conditional `crop-page-level-deletion-gate`

## Decision

**Do not adopt Qwen3.8 Max for doc-web's crop detector.** Access and multimodal strict-schema transport qualified, but the frozen detector reached only `12/13`, `0.9411`, below the `overall >= 0.95` entry gate and the maintained Gemini 3 Flash proof (`13/13`, `0.9703`). Qwen was also slower and more expensive on this surface. The conditional 22-case page-context gate was not run, so Qwen capability there is **not measured**.

## Interpreted brief and ownership

The user supplied only `qwen-3.8-max`; this evaluation resolved it to OpenRouter `qwen/qwen3.8-max`, canonical snapshot `qwen/qwen3.8-max-20260803`, through the sole live `Alibaba` endpoint. Alibaba's separately documented `qwen3.8-max-preview` Token Plan route was not substituted. The maintained crop ladder outranked OCR and historical benchmark lanes because it is a current multimodal decision surface with executable runtime ownership, source-backed public fixtures, and explicit promotion gates.

The owning pre-spend contracts are recorded in Story 207 (detector) and Story 209 (conditional page-context). Runtime remains `gemini-3-flash-preview` for the bounded Onward rescue detector, with the maintained page-context role pinned to GPT-5.5 Responses. No default, prompt, scorer, golden, or maintained task provider changed.

## Current provider contract (2026-08-04)

- OpenRouter catalog/API identity: `qwen/qwen3.8-max`; canonical snapshot `qwen/qwen3.8-max-20260803`.
- Endpoint: one `Alibaba` route, pinned with `provider.order=["Alibaba"]`, `allow_fallbacks=false`, and `require_parameters=true`.
- Modality/limits: text, image, and video input; text output; 1,000,000 context; 131,072 maximum completion tokens.
- Reasoning: mandatory; the frozen arm used `low` and excluded reasoning from visible output.
- Structured output: `response_format.type=json_schema`, `strict=true`, plus local fail-closed validation.
- Pricing: `$2/M` uncached input, `$0.25/M` cache reads, `$2.50/M` cache writes, and `$6/M` output. Decisions use OpenRouter-reported `usage.cost`, not estimated cost.
- Privacy: OpenRouter says prompts are not retained unless logging is opted into, but the live Alibaba route was absent from the ZDR endpoint list. Only checked-in public fixtures were eligible.
- Sources: OpenRouter [models API](https://openrouter.ai/api/v1/models), [exact endpoint API](https://openrouter.ai/api/v1/models/qwen/qwen3.8-max-20260803/endpoints), [structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs), and [ZDR policy](https://openrouter.ai/docs/guides/features/zdr); Alibaba [model catalog](https://help.aliyun.com/en/model-studio/models) and [structured output guide](https://help.aliyun.com/en/model-studio/qwen-structured-output).

## Frozen matrix and stop rules

| Surface | Candidate configuration | Comparator | Entry/stop rule |
| --- | --- | --- | --- |
| `image-crop-extraction` | OpenRouter Qwen3.8 Max, Alibaba pinned, low hidden reasoning, strict `crop_regions`, `max_tokens=16384`, `conservative-count`, no cache, `-j 1` | Reuse maintained Gemini 3 Flash `13/13`, `0.9703` evidence; fresh control only after a decision-competitive candidate result | Advance only at `13/13` and `overall >= 0.95` |
| `crop-page-level-deletion-gate` | Same route, strict `page_context_validation` | Maintained GPT-5.5 Responses `22/22` | Run only after detector entry gate; require `22/22` |

The prompt, task, scorer, and golden were frozen at SHA-256 `9a22e566...4aba`, `7edae5fe...cf3e`, `7fcf07e0...c19e`, and `2ac0a8f0...f90`. Total paid-call cap was US$5; no diagnostic arm was used because the lone failure directly violated an explicit prompt rule.

## Transport qualification

The dedicated `benchmarks/providers/openrouter_vision_chat.py` preserves OpenAI-style text and `image_url` blocks losslessly, pins provider/model, requests strict schemas, rejects non-terminal or multi-choice responses, verifies raw token/cost evidence, and locally validates bbox order/range.

1. Strict text probe: exact Qwen/Alibaba identity, terminal `stop`, `{"images":[]}`, `94` tokens, `2841 ms`, `$0.000364`.
2. Generated 128x128 black-square vision probe: exact identity and strict schema; bbox `[0.25,0.25,0.75,0.75]` matched the synthetic square; `449` tokens, `5728 ms`, `$0.001614`.
3. PromptFoo `Image000` parity smoke: passed at `0.8157`; exact identity, `3328` tokens, `14674 ms`, `$0.008352`.

Access: **available**. Transport: **qualified**. Reliability: **acceptable** (`0` transport/schema errors across qualification and the 13-case run).

## Detector result

```bash
cd benchmarks && ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --providers "python:$(pwd)/providers/openrouter_vision_chat.py" --filter-prompts conservative-count --no-cache --output results/qwen38-openrouter-image-crop-extraction-20260804.json -j 1
```

| Candidate | Structural result | Semantic/source review | Avg latency | Subject cost | Decision |
| --- | --- | --- | ---: | ---: | --- |
| Qwen3.8 Max / Alibaba / low | `12/13`, `0.9411`, `0` errors | One source-verified model-wrong miss | `16002 ms` | `$0.107508` total (`$0.00827/case`) | Do not adopt |
| Maintained Gemini 3 Flash evidence | `13/13`, `0.9703` | Maintained source-backed proof | about `7878 ms` | about `$0.059` total | Retain runtime |

The maintained task contains only its deterministic structural scorer despite a stale comment naming an LLM judge. Adding a rubric would have changed the comparison surface, so semantic verification was performed by direct source inspection instead of inventing a post-score judge.

## Visual mismatch classification

**Target:** `benchmarks/input/source-pages-b64/Image011.b64.txt`
**Candidate output:** anniversary logo `[0.36,0.07,0.59,0.23]`, seal `[0.12,0.68,0.39,0.90]`, and signatures/title lines `[0.43,0.72,0.88,0.90]`
**Golden:** anniversary logo plus one combined seal/signatures region `[0.119804,0.686061,0.876863,0.896667]`

Qwen localized the logo and both bottom visual subregions, but emitted `3` regions instead of `2`, splitting the seal from adjacent signatures and explicitly including minister name/title lines. The frozen prompt states `Signatures next to seals = ONE combined image`, so this violates an unambiguous task rule. Classification: **prompt/pipeline-wrong -> model-wrong**, runtime-blocking for this detector decision. The golden and scorer remain unchanged.

## Spend and provenance

- Text probe: `$0.000364`
- Synthetic vision probe: `$0.001614`
- PromptFoo parity smoke: `$0.008352`
- Full 13-case subject: `$0.107508`
- **Total paid-call spend: `$0.117838`**

Ignored raw results:

- `benchmarks/results/qwen38-openrouter-image-crop-smoke-20260804.json` — SHA-256 `f05cae4167d3eaf504b980b3fdd2224c5e196537d1b5d441727dfd4c50648af6`
- `benchmarks/results/qwen38-openrouter-image-crop-extraction-20260804.json` — SHA-256 `04d59c1e692c275e8ff36805bbf7165403f0e1fa8bce78afa9f792143380cf8a`

The evaluated state used base SHA `b97870f` plus the pre-spend Story 207/209 contracts and the new OpenRouter adapter/test files. PromptFoo was `0.121.1`; all paid calls used the repo wrapper, no cache, and concurrency `1`.

Validation: focused adapter/environment coverage passed `9/9`; Ruff, registry YAML parsing, `git diff --check`, methodology compile, and methodology check passed. Full `make test` completed `935 passed, 1 failed, 4 warnings` in `834.68s`; the only failure was an unrelated `pdftoppm` rasterization timeout in `test_preview_manifest_declares_portable_safe_files`. An immediate isolated rerun passed in `2.32s`, classifying it as transient current-environment evidence rather than a Qwen adapter regression. The four warnings are the existing Pydantic deprecations in `portionize_headers_numeric_v1`.

## Adoption and unmeasured limits

- Detector capability: **worse** than the maintained winner and below target.
- Detector adoption: **do not adopt**.
- Page-context capability: **not measured** because the detector prerequisite failed.
- Page-context adoption: **defer / not advanced under the declared ladder**.
- Runtime/default changes: none.

Retry only after a materially revised Qwen snapshot or a new source-backed detector contract. Do not retry this exact snapshot by changing the golden, scorer, grouping rule, or reasoning arm merely to rescue the result.
