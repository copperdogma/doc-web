# Attempt 026 — Gemini 3.7 Flash evaluation

**Eval:** `image-crop-extraction`, `crop-validation`, conditional `crop-page-level-deletion-gate`, and corrected real-handwriting screen
**Date:** 2026-08-13
**Worker Model:** Codex GPT-5
**Subject:** first-party Google Gemini Developer API `gemini-3.7-flash`

## Decision

**No runtime/default change.** The strict integer-coordinate detector remains a credible future replacement candidate, and the handwriting path is not adopted because both corrected real fixtures miss `0.99`. The crop-only result is now classified more narrowly: Gemini 3.7 fails a valid production-safety regression case, but model selection is blocked rather than lost because the full corpus is selection-exposed and has no held-out confirmation slice. Keep the currently configured providers until decision-grade held-out evidence exists. No runtime default, scorer, golden, or maintained provider changed. The evaluation harness prompt source did change for the authorized integer-coordinate repair; that change routes the strict-integer-labeled arm to an integer coordinate instruction while leaving existing maintained-provider behavior unchanged.

## Provider and privacy qualification

Google's 2026-08-13 changelog and model documentation identify exact GA model `gemini-3.7-flash`, a 1M-token input window, 64K output, multimodal input, structured outputs, and supported `low`, `medium`, and `high` thinking (`medium` default; `minimal` unsupported). Introductory standard pricing through 2026-12-31 is `$0.75/M` input and `$3.75/M` output including thinking tokens. Paid-tier prompts and responses are not used to improve Google products.

Repo-scoped discovery returned the exact model. Native strict text and synthetic-image probes returned exact served identity `gemini-3.7-flash`, terminal `STOP`, valid usage, and schema-valid JSON. One checked-in `Image000` PromptFoo parity case also passed with exact identity and `STOP`. Crop lanes used explicit `low` thinking; the OCR client intentionally omitted `thinking_config`, selecting the documented `medium` default for quality-sensitive transcription. Only public checked-in fixtures were sent, and credentials were neither printed nor recorded.

## Progressive results

| Surface | Result | Mean latency | Estimated subject cost | Decision |
| --- | ---: | ---: | ---: | --- |
| Detector, normalized floats | `12/13`, `0.9364` | `2503 ms` | `$0.023377` | configuration ambiguity on `Image037` |
| Detector, strict integer `0-1000` | `13/13`, `0.970277` | `2251 ms` | `$0.020378` | clears detector gate |
| Crop-only validator | `39/40`, `0.975` | `3023 ms` | `$0.063905` | regression veto; selection blocked |
| Page-context validator | not measured | — | `$0` | stopped after crop-only failure |
| Barney handwriting, image entry | `0.981622` | `15.71 s` OCR stage | lower bound included below | fails `0.99` |
| Alverson handwriting, image entry | `0.985233` | `6.75 s` OCR stage | lower bound included below | fails `0.99` |

The normalized detector's sole failure serialized an intended leading value near `0.097` as `0.97` for the second `Image037` box. This repeated a known float-contract ambiguity, so one pre-authorized diagnostic changed both the effective rendered coordinate instruction and the response schema from normalized numbers to `0-1000` integers. The failed-case retry passed at `0.9844`, and the required frozen full integer rerun then passed all 13 cases at `0.970277`. This repair is pipeline/configuration-wrong evidence, not a subject-quality rescue, and the integer score must not be described as using byte-identical prompt/schema inputs to the normalized arm.

The crop-only failure is model-wrong as production-regression evidence. On `page-126-000`, Gemini returned `pass` and said all text was integral to the memorial plaques. The checked golden and manual image inspection show a partial separate plaque at the left edge, so the candidate missed the exact exclusion defect the gate protects. Per the declared ladder, the 22-case page-context capability is not measured rather than failed.

## Selection-validity follow-up

The initial adoption wording overreached. The `caption-focus` prompt was chosen
from six variants on the full 40-case corpus, and the recorded incumbent plus
challengers were repeatedly ranked on those same cases. The page-context prompt
was likewise repaired on observed cases (`page-126-000`, then GPT-5.5-specific
failures) before the configured provider was selected. Historical challengers
did not receive a symmetric declared configuration-selection budget.

`benchmarks/golden/crop-eval-provenance.json` now records every current
crop-only and page-context case as calibration plus production regression, with
zero held-out confirmation cases. Frozen-output regrading preserves Gemini 3.7
at `39/40`, sole failure `page-126-000`, while correctly setting
`selection_claim_allowed = false`. The April Gemini 3.1 Flash Lite `40/40`
incumbent proof also predates the current GA provider ID and is stale for a
fresh comparison. An identical paid rerun on the exposed set would not make the
result decision-bearing, so no provider call was made in this follow-up.

A bounded inventory of existing unscored Onward crops found only
`page-012-002`, `page-122-002`, and `page-002-000`. Visual source/crop review
found all three pass-style, while the first two reuse source pages already in
calibration. They were not mislabeled as held out. The next decision-bearing
slice is predeclared as 12 natural production crops, balanced `6 pass / 6 fail`,
from at least eight previously unused source pages, with independent visual
review and hashes frozen before calls; see the evidence packet for the fixed
four-page expansion rule.

Operational decision: a valid regression failure may still block a
runtime/default change, so Gemini 3.7 is not promoted. It is not valid to claim
that this exposed one-case delta proves the incumbent model is intrinsically
better. A future selection claim requires new source-backed held-out fixtures
frozen before calls, symmetric calibration budgets, frozen configurations, and
then a one-time confirmation run. Visual/provenance packet:
`docs/evals/evidence/026-crop-validity-audit.md`.

Both handwriting misses are also model-wrong. Barney contains literal substitutions including `ald Grove`, `eternel`, `enguish`, and `circumstantes`, plus small omissions. Alverson adds `Clothing`, normalizes `Chickamaga` to `Chickamauga`, and changes literal spellings such as `kneedles` and `shugar`. These source-visible differences are not scorer or fixture defects. Gemini 3.7 is below both the strict bar and Gemini 3.6 Flash's prior `0.984527` / `0.984052` pair floor.

## Spend and evidence

Successful-call estimated spend at official introductory pricing was `$0.117880`, below the `$5` cap: native probes `$0.001148`, PromptFoo parity `$0.001934`, normalized detector `$0.023377`, integer failed-case diagnostic `$0.001481`, full integer detector `$0.020378`, crop-only `$0.063905`, and handwriting `$0.005658` lower bound. PromptFoo 0.121.1 does not know Gemini 3.7 pricing, so costs were recomputed from raw usage. The OCR client records prompt/candidate tokens but not hidden thinking tokens, making its line a lower bound.

The detector task, scorer, and golden stayed fixed at SHA-256 `7edae5fe3c935517396a8d37cd8f148cb2b592ed4d206168dbb62273d758cf3e`, `7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7`, and `2ac0a8f01e00a252439da1f4827a85bc5118bf96460a3ff1780e642eafc60f90`. Prompt/schema provenance differs by arm:

| Detector arm | Effective coordinate instruction | Prompt-source bytes SHA-256 | Rendered instruction bytes SHA-256 | Provider/schema SHA-256 |
| --- | --- | --- | --- | --- |
| normalized-float full run | `Coordinates: normalized 0.0-1.0, origin top-left.` | `9a22e566f30eac6258a78a28107d77a17940eca06858dd20cb8d7bc97fc84aba` | `232075c6982347a921adb3725ab31731f5c96fa2e6cfcdf92fcdef7e68cdfa2a` | `4724af6c5b05f79fc4629f462ad7fd578557a3ea19beebb00385085273c1b496` |
| integer failed-case diagnostic and full rerun | `Coordinates: integers 0-1000, origin top-left, with x0 < x1 and y0 < y1.` | `bca281e0fbe547e3f3ef049b436d87c73ed7bb066e86f51145fb444b48211b64` | `95a09e217118cc010d20ede0e1eb7d01c882b460d32408de8d92e4c1f10a1293` | `23d65bab084fb98d490dbd89997a864e8e72fb70e272035d25a4ec994c4adfad` |

The prompt-source hashes cover the exact `crop-conservative-count.js` bytes used by each arm. The rendered hashes cover the exact instruction text embedded in the first result row of each raw PromptFoo artifact, excluding the image bytes. The normalized result therefore anchors the pre-repair prompt, while the diagnostic and full integer artifacts anchor the repaired prompt/schema together.

Crop-only task/prompt/scorer/golden hashes remain `1ba981ed...23f` / `10f589b9...a74d9` / `12eb6372...8fb` / `71371e68...c68`; the handwriting corpus is `473dda06...b7e`, and the eval-only OCR recipe is `ae2fe23c...762`.

Ignored regenerable raw evidence:

- `benchmarks/results/gemini37-flash-low-image-crop-extraction-20260813.json` — `a5fa3692...1d6a`
- `benchmarks/results/gemini37-flash-low-integer-image037-diagnostic-20260813.json` — `140c692d...f79`
- `benchmarks/results/gemini37-flash-low-integer-image-crop-extraction-20260813.json` — `3414c99d...4704`
- `benchmarks/results/gemini37-flash-low-crop-validation-20260813.json` — `3b2744be...309`
- `output/runs/eval-barney-image-gemini-3-7-flash/02_ocr_ai_gpt51_v1/pages_html.jsonl` — `ce399218...504`
- `output/runs/eval-alverson-image-gemini-3-7-flash/02_ocr_ai_gpt51_v1/pages_html.jsonl` — `817a79cf...a7d`

Sources: <https://ai.google.dev/gemini-api/docs/changelog>, <https://ai.google.dev/gemini-api/docs/latest-model>, <https://ai.google.dev/gemini-api/docs/structured-output>, <https://ai.google.dev/gemini-api/docs/pricing>, <https://ai.google.dev/gemini-api/terms>.

## Validation

- Registry and all new provider/recipe YAML parsed successfully.
- Focused crop, handwriting-harness, image-recipe, and adversarial regrader
  coverage: `33 passed`.
- Focused Ruff and Prettier checks passed.
- Frozen-output regrading remained `39/40`, held-out `0`, and
  `selection_claim_allowed = false` after the fail-closed repair.
- `make lint` passed repo-wide.
- `make methodology-compile` and `make methodology-check` passed.
- `git diff --check` passed.
- A full `make test` run reached `339 passed` before being intentionally
  stopped after 144.94 seconds because the remaining suite was unrelated to
  this evaluation-only change; no failure had occurred. The focused changed
  surfaces and repo-wide lint are the proportional completion gate here.
