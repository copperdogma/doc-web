# Attempt 028 — Ox Alpha public-fixture rerun

**Eval:** `image-crop-extraction`, conditionally `crop-validation` and
`crop-page-level-deletion-gate`
**Date:** 2026-08-22
**Worker Model:** Codex GPT-5
**Subject:** OpenRouter `stealth/ox-alpha`; resolved provider recorded from each
response

## Decision contract (recorded before inference)

- This is a new follow-up to Attempt 027. Preserve its router-policy failure;
  do not overwrite or reinterpret it.
- Exact requested and served model: `stealth/ox-alpha`. No alternate model
  fallback is configured. Provider routing is not pinned because the owner
  decision does not depend on endpoint identity; the resolved provider must be
  recorded.
- Fixture policy: generated images and the checked-in crop fixtures are public
  evaluation inputs. Cam explicitly approved this bounded run even though the
  anonymous provider may retain or train on them. Omit request-level ZDR and
  `data_collection=deny`; do not change account settings.
- First transport arm: mandatory low reasoning, hidden reasoning output,
  `max_tokens=16384`, API-enforced strict integer `0-1000` crop JSON Schema,
  and `require_parameters=true`.
- If strict transport fails before a valid response, at most one clearly
  labeled diagnostic may relax only schema/parameter enforcement. That result
  may measure raw capability but cannot prove drop-in transport or adoption.
- Frozen detector surface: Story 207's 13-case `image-crop-extraction` task,
  `conservative-count`, no cache, concurrency `1`. Advance from generated image
  to one maintained case, then all 13 cases only while exact identity, terminal
  success, schema validity, and usage/cost remain attributable.
- Detector gate: `13/13`, overall `>= 0.95`, zero provider/schema errors. Only
  after it passes, run the independent 40-case `crop-validation` gate (`40/40`)
  and 22-case `crop-page-level-deletion-gate` (`22/22`) under their maintained
  prompts and scorers. These hand-authored goldens are the authoritative
  bounded selection surface; production promotion additionally requires every
  hard safety/runtime gate.
- Spend cap: US$0.75 including probes and any diagnostic. Current catalog token
  price is zero; stop if live usage reports an unexpected charge or the cap
  could be exceeded.
- No private data, runtime/default change, prompt/scorer/golden change, commit,
  push, or deployment.

## Frozen provenance before inference

- Base HEAD: `009afed44da2494273983449b73c9f4c0a5cde37`
- Detector task SHA-256:
  `7edae5fe3c935517396a8d37cd8f148cb2b592ed4d206168dbb62273d758cf3e`
- Detector prompt source SHA-256 (renders coordinates by provider label):
  `bca281e0fbe547e3f3ef049b436d87c73ed7bb066e86f51145fb444b48211b64`
- Detector scorer SHA-256:
  `7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7`
- Detector golden SHA-256:
  `2ac0a8f01e00a252439da1f4827a85bc5118bf96460a3ff1780e642eafc60f90`

## Results

**Do not adopt; diagnostic capability measured below the detector gate.**
Removing the privacy filters and endpoint pin isolated the strict-route failure:
the text probe still returned router HTTP 404 when
`require_parameters=true`. The first generated-image diagnostic omitted only
that router flag, reached exact Ox Alpha, and returned Markdown-fenced JSON. The
initial hash-only adapter correctly rejected the wrapper. An offline inspection
could not recover those discarded bytes, so the bounded follow-up added an
explicit public-diagnostic retention path under ignored `benchmarks/results/`
with mode `0600`, then repeated one fresh generated-image call.

The fresh generated output was retained before parsing. Removing only its
Markdown fence yielded valid strict integer crop JSON; no JSON content or
coordinates were repaired. The first maintained-case attempt then exposed an
adapter topology mismatch: the rendered maintained prompt requested normalized
`0-1` coordinates while the client still validated the generated probe's
integer schema. Its exact-model response was valid float crop JSON but was
quarantined. After correcting only that diagnostic client schema to match the
frozen prompt, the one-case smoke passed and the resolved 13-case matrix ran.

The full diagnostic detector completed `13/13` scorer passes with no provider
or parser errors, but its mean score was only `0.915146`, below the predeclared
`0.95` gate and the maintained Gemini 3 Flash `0.9703` reference. Average
provider latency was `8538.85 ms` (median `5683 ms`, range `3057-38641 ms`),
usage was `56,315` prompt plus `965` completion tokens (`57,280` total), and
OpenRouter reported `$0` cost. Because quality missed the detector entry gate,
the independent 40-case crop-only and 22-case page-context surfaces were not
run.

| Stage | Result | Spend |
| --- | --- | ---: |
| Current public endpoint discovery | exact model; one zero-priced `Stealth` endpoint; `response_format` advertised | `$0.000000` |
| Strict text probe, privacy filters omitted, provider unpinned | router 404 before inference with `require_parameters=true` | `$0.000000` |
| Original generated diagnostic | exact model/provider and terminal `stop`; wrapper discarded by strict parser | `$0.000000` |
| Fresh generated diagnostic with protected retention | fence-only cleanup produced valid integer crop JSON; `2346 ms` | `$0.000000` |
| First maintained-case topology diagnostic | float JSON rejected by mismatched integer client schema; no semantic score | `$0.000000` |
| Corrected one maintained case | `Image000` passed at `1.0`; `5908 ms` | `$0.000000` |
| Maintained 13-case detector diagnostic | `13/13`, mean `0.915146`; below `0.95` gate | `$0.000000` |
| 40-case crop-only validator | not run | `$0.000000` |
| 22-case page-context gate | not run | `$0.000000` |
| **Total** | **bounded diagnostic completed through detector gate** | **`$0.000000`** |

Diagnostic response evidence:

- response ID: `gen-1787412223-bBpjcJGgVqs4CcL3BOnt`
- requested/served model: `stealth/ox-alpha`
- resolved provider: `Stealth`
- finish reason: `stop`
- latency: `2860 ms`
- usage: `357` prompt, `54` completion, `411` total, `64` cached tokens
- OpenRouter-reported cost: `$0`
- invalid output SHA-256:
  `f6ceaa3740c76ee492c1a2cb1558d010f718a8f5737e0923e7417fba7330da0e`
- generated PNG SHA-256 / size:
  `0c5af173c43734e6298457e119b702f14c50f65b3e7f9f7f9521dc61aeabd6cd`
  / `1410 bytes`
- primary failure class: output-contract / unsupported parameter enforcement,
  not semantic model quality

Fresh diagnostic evidence:

- generated response: `gen-1787412984-sypDmSV5qgBAtKc3Ox2l`, `2346 ms`,
  `393` tokens, `$0`; raw output hash
  `e68595027e7c0bca374645733cebcd88e311f78930d4c7c387c755a0dabf150c`
- generated raw pointer:
  `benchmarks/results/ox-alpha-public-diagnostic-generated-20260822-r2.json`
  (ignored, mode `0600`); tracked manifest hash
  `e290c8ca61add0ed0d5882f8c434d624feb915ebdd5c6c685c360e50418254e5`
- corrected one-case result:
  `benchmarks/results/ox-alpha-diagnostic-image000-20260822-r3.json`, hash
  `44b4896b38fe6d6d4b1b09d0a604c339d4fe73c010bb086c14cc0b2f21049722`
- full result:
  `benchmarks/results/ox-alpha-diagnostic-image-crop-extraction-20260822.json`,
  hash
  `31fa1bd448e76ea35e4d6ca268353f59cf55c7d769b614d9d98bc7c082a504ed`
- the full result carries each protected raw-output pointer and content hash;
  all `14` float-detector raw files are mode `0600`
- manual inspection confirmed the two weakest cases are model-side bbox
  undercoverage rather than obvious golden defects: `Image000` inset the
  full-cover crop (`0.8008`), while `Image011` stopped the seal/signature crop
  at `x1=0.72` versus golden `0.876863` (`0.8155`)

## Layered verdict

- Access: **available** — exact Ox Alpha produced a terminal response once
  strict parameter routing was omitted.
- Transport: **blocked for drop-in use** — `require_parameters=true` has no
  eligible endpoint. Diagnostic client validation works only after relaxing
  provider enforcement and, for one generated response, removing a Markdown
  fence.
- Reliability: **acceptable for the bounded diagnostic** — `13/13` terminal,
  exact-model responses with no provider/parser errors; not production-contract
  evidence.
- Capability: **worse on the maintained detector** — `0.915146` versus the
  `0.95` gate and maintained `0.9703` evidence.
- Economics: **measured diagnostically** — `$0`, `8538.85 ms` average detector
  latency, with one `38641 ms` outlier.
- Adoption: **do not adopt** for `image-crop-extraction`. It is both non-drop-in
  and below the quality gate. Downstream crop safety capability remains not
  measured.

## Commands and validation

- Public discovery: `curl -sS
  https://openrouter.ai/api/v1/models/stealth/ox-alpha/endpoints` with a
  field-limiting JSON projection.
- Native probes ran through `../scripts/run_with_doc_web_env.py` and the local
  `openrouter_vision_chat.py` provider; no key was printed or copied into
  evidence.
- Focused provider plus crop-substrate tests: `27 passed`.
- Focused Ruff: passed.
- Diff hygiene: passed.
- Eval-only adapter SHA-256:
  `f93c72b566e4bdced8b7eef59cf4d6228dfd07d3771753f1d0308d63964bc2ab`
- Ox Alpha provider config SHA-256:
  `40c737a8c38c8b46bb86c0f8a93f32732ece89091cf476f2954fc021f4394473`
- Check-in full-suite pass: `949 passed`; the two unrelated packaging tests
  that create fresh dependency-complete virtual environments failed while pip
  installed OCR/ML wheels with `OSError: [Errno 28] No space left on device`.
  The same PPTX test remained environment-blocked when rerun alone, and a NAS
  temp retry could not create an executable virtualenv because the SMB mount
  denies `chmod`. No requirement, packaging, or office-intake file changed in
  this evaluation. The focused Ox Alpha/provider checks, methodology check,
  lint, YAML parsing, and diff hygiene passed.
