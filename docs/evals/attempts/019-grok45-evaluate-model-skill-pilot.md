# Grok 4.5 `/evaluate-model` Skill Pilot

Date started: 2026-07-22
Repo HEAD at start: `41c06e20f08127fd8bbddb1997bf75a9879798c7`
Status: Complete — detector do not adopt; page-context capability not measured

## Interpreted brief and duplicate-evidence override

Evaluate xAI Grok 4.5 again as a full real-world acceptance test of the new
`/evaluate-model` skill. The user explicitly requires every step to run fresh
as though the 2026-07-20 attempt did not exist. That instruction overrides the
skill's normal duplicate-evidence stop gate for this pilot, while the earlier
attempt remains prior evidence rather than a baseline to copy.

## Alignment and ownership

This tests the Ideal's illustration fidelity, source traceability, and
eval-before-build requirements. The primary decision surface is the existing
`image-crop-extraction` C4 eval owned by Stories 133, 183, and 207. The
progressive hard gate is `crop-page-level-deletion-gate`, owned by Story 209.
No new story is warranted because the subsystem, fixture family, artifact
contract, and adoption decision are unchanged. No crop-specific ADR applies.
The workflow installation itself follows doc-web's canonical cross-CLI skill
contract and does not create a separate product or eval surface for the crop
stories to own.

## Predeclared decision contract

- Candidate: exact direct xAI model `grok-4.5` through the Responses API.
- Candidate configuration: `reasoning.effort=low`, image detail `high`,
  `max_output_tokens=4096`, `store=false`, maintained `conservative-count`
  prompt, normalized 0.0-1.0 bounding boxes.
- Incumbent arm: fresh rerun of maintained Gemini 3 Flash with the same
  `conservative-count` prompt and 13-case detector surface. The historical
  maintained evidence is `0.9703` overall and `13/13`, but the fresh arm owns
  this pilot's comparison.
- Primary target: `image-crop-extraction` overall score at least `0.95` and
  pass rate at least `0.90`; adoption also requires an honestly competitive
  result against the maintained incumbent.
- Progressive hard gate: run the 22-case `crop-page-level-deletion-gate` only
  if Grok clears the detector prerequisite; the maintained contract is `22/22`.
- Fixed comparison inputs: current maintained prompt, 13 checked-in fixtures,
  scorer, and source-backed golden at `41c06e2`; no golden, scorer, or prompt
  edits are permitted to rescue the candidate.
- Freshness/cache/concurrency: new result filenames, `--no-cache`, start at
  `-j 1`; raise no higher than `-j 3` only after transport qualification.
- Matrix: one fresh maintained incumbent arm plus one Grok low-reasoning arm.
- Diagnostic/configuration cap: one low-reasoning maintained arm, then at most
  one high-reasoning failed-case retry if the low arm has source-backed misses.
  No medium or full-high matrix.
- Transport ladder: authenticated exact-ID access probe, smallest native text
  probe, native image/strict-schema contract probe, one-case PromptFoo
  harness-parity smoke, then the bounded task.
- Reliability gate: zero unclassified provider, adapter, parser, or scorer
  failures. Every retry and failure remains in the end-to-end result.
- Economics: capture status, served model, latency, token usage, reported cost,
  and retry overhead where the API exposes them.
- Privacy: use the user-authorized `DOSSIER_XAI_API_KEY` in place without
  copying or printing it; only checked-in public benchmark images may be sent.
  `store=false` is required and is not treated as proof of ZDR.
- Adoption question: should doc-web replace or supplement the maintained crop
  detector or page-context validator with Grok 4.5?

## Execution log

- 20260722 — decision contract frozen before provider spend; next: run the
  fresh transport qualification ladder.
- 20260722 — official xAI docs, authenticated transport, strict-schema harness
  repair, fresh incumbent/challenger comparison, failure review, and bounded
  high-reasoning retry completed. The candidate failed the detector prerequisite,
  so the page-context gate was not started.

## Fresh provider contract and access evidence

Official xAI sources checked on 2026-07-22 identify `grok-4.5` as the direct
model ID, with `grok-4.5-latest` and `grok-build-latest` aliases, text and image
input, text output, a 500,000-token context window, Responses and Chat
Completions support, strict structured output, and low/medium/high reasoning.
Reasoning defaults to high and cannot be disabled; `presencePenalty`,
`frequencyPenalty`, and `stop` are invalid for reasoning models. Short-context
pricing is `$2/M` input, `$0.30/M` cached input, and `$6/M` output; requests at
or above 200,000 prompt tokens use `$4/M`, `$0.60/M`, and `$12/M` for all
request tokens. Default retention is 30 days unless team-level ZDR is active.
The xAI security FAQ also states that API inputs and outputs are not used for
training unless the customer explicitly grants permission.

Fresh sanitized transport evidence is in the ignored local sidecar
`benchmarks/results/grok45-skill-pilot-transport-20260722.json`:

- `GET /v1/language-models/grok-4.5`: HTTP 200, exact ID `grok-4.5`, xAI-owned,
  fingerprint `fp_9f4fa447be`, text/image input and text output.
- Native text Responses probe: HTTP 200, served `grok-4.5`, status `completed`,
  exact `API_OK`, 261 tokens, `$0.0004844`, ZDR header `false`.
- Native image plus strict JSON Schema probe: HTTP 200, served `grok-4.5`,
  status `completed`, schema-valid JSON, 3,225 tokens, `$0.0081084`, ZDR header
  `false`.

Only the public checked-in crop fixtures were used. `store=false` was sent but
was not treated as ZDR evidence.

## Harness qualification and repair

The existing adapter passed its focused tests, and a prompt-only one-case
PromptFoo smoke passed. That smoke still returned fenced prompt-only JSON, so
it did not meet the production strict-structure contract now required by the
skill. The adapter was repaired before scoring to send xAI Responses
`text.format` with a strict crop JSON Schema and to retain served model,
response status, service tier, and response ID metadata. Focused tests and Ruff
passed after the repair. A second one-case no-cache PromptFoo smoke passed with
unfenced schema-valid JSON and recorded `served_model=grok-4.5`.

## Frozen comparison results

Both full arms used the current 13-case maintained detector, fixed
`conservative-count` prompt, scorer, and golden at starting HEAD `41c06e2`,
with `--no-cache` and `-j 3` after transport qualification.

| Arm | Result | Overall | Avg latency | Cost | Reliability |
| --- | ---: | ---: | ---: | ---: | --- |
| Gemini 3 Flash fresh incumbent | 13/13 | 0.9629 | 7,303 ms | $0.05530 | 0 provider errors |
| Grok 4.5 low, strict schema | 11/13 | 0.7667 | 2,782 ms | $0.07598 | 0 provider errors |
| Grok 4.5 high failed-case retry | 0/2 | 0.4553 mean | 2,674 ms | $0.01247 | 0 provider errors |

The fresh incumbent remained above the `0.95` target despite expected VLM
variance from its maintained `0.9703` best. Grok missed both the target and the
fresh incumbent. The complete Grok pilot, including native probes, two harness
smokes, the full arm, and the retry, cost `$0.10955`.

Including the fresh Gemini incumbent's `$0.05530`, total provider spend for the
invocation was `$0.16485`. The skill's later acceptance hardening added a
default `$5` all-provider ceiling; that numeric ceiling was not predeclared for
this original run and is not presented as a guardrail the pilot exercised.

## Failure classification

- `Image001`, low `0.4460`, high `0.4199`: **model-wrong**. Both boxes were
  vertically shifted and too shallow, excluding the `1887 - 1987` line that is
  visibly integral to the stylized title region. The source-backed golden is
  `[0.192157, 0.269697, 0.853333, 0.382424]`; low returned
  `[0.18, 0.22, 0.82, 0.32]` and high returned
  `[0.22, 0.22, 0.78, 0.32]`.
- `Image011`, low `0.4987`, high `0.4907`: **model-wrong**. Grok split the
  embossed seal and the immediately adjacent official signatures into separate
  boxes, contradicting the explicit prompt rule and visible source grouping.
  The source-backed combined region is
  `[0.119804, 0.686061, 0.876863, 0.896667]`.

No prompt, scorer, or golden was changed to rescue the subject. Higher
reasoning repaired `0/2`, so the declared configuration cap was reached.

## Decision

**Detector — do not adopt.** Grok 4.5's direct xAI transport was callable,
reliable in this bounded run, fast, and strict-schema capable. Its
source-grounded bounding-box fidelity was materially worse than the fresh
incumbent, and it cost more on this slice. There is no detector
second-model/router value case.

**Page-context validator — capability not measured; adoption not advanced.**
Because Grok failed the predeclared detector prerequisite, the materially
different 22-case page-context gate was intentionally not run. That stop is
valid spend and adoption-ladder evidence, but it is not semantic evidence about
Grok's page-context quality. The maintained GPT-5.5 Responses validator and its
`22/22` evidence remain unchanged; retry this surface only if a future Grok
detector first clears the maintained prerequisite.

## Exact sanitized commands

Credential values were never embedded in these commands or artifacts. The
transport command ran from the repo root; the five PromptFoo commands ran from
`benchmarks/`.

Transport qualification:

```bash
DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/dossier/.env.local scripts/run_with_doc_web_env.py python /tmp/xai_grok45_skill_probe.py benchmarks/input/source-pages-b64/Image011.b64.txt benchmarks/results/grok45-skill-pilot-transport-20260722.json
```

The ephemeral probe made an exact-ID model lookup, a low-reasoning text
Responses call requiring `API_OK`, and a low-reasoning image call with strict
JSON Schema. Both calls used `store=false`; the text call used 128 maximum
output tokens and the image call used 1,024 with `detail=high`. The probe source
was 6,286 bytes with SHA-256
`179cc03fac62e0247d38b01fbada0c168ef02c1a711ce5bafe8ac5b1d00abace`;
the Image011 input SHA-256 was
`71806b69682ae403974ab6090429aa894029c3d3771b77c76bdbe10cb2102f83`.
The probe source itself was not tracked, so this command is historical
provenance, not a standalone regeneration route. Future repetitions should use
a tracked equivalent of the stated three-step contract.

Prompt-only harness smoke before adapter repair:

```bash
source ~/.nvm/nvm.sh && nvm use 24 >/dev/null 2>&1 && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/dossier/.env.local XAI_API_KEY_ENV=DOSSIER_XAI_API_KEY XAI_GROK_REASONING_EFFORT=low PROMPTFOO_EVAL_TIMEOUT_MS=240000 ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --providers "python:$(pwd)/providers/xai_grok_responses.py" --filter-prompts conservative-count --filter-first-n 1 --no-cache --output results/grok45-skill-pilot-harness-smoke-prompt-json-20260722.json -j 1
```

Strict-schema harness smoke after adapter repair:

```bash
source ~/.nvm/nvm.sh && nvm use 24 >/dev/null 2>&1 && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/dossier/.env.local XAI_API_KEY_ENV=DOSSIER_XAI_API_KEY XAI_GROK_REASONING_EFFORT=low PROMPTFOO_EVAL_TIMEOUT_MS=240000 ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --providers "python:$(pwd)/providers/xai_grok_responses.py" --filter-prompts conservative-count --filter-first-n 1 --no-cache --output results/grok45-skill-pilot-harness-smoke-strict-schema-20260722.json -j 1
```

Full Grok low-reasoning arm:

```bash
source ~/.nvm/nvm.sh && nvm use 24 >/dev/null 2>&1 && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/dossier/.env.local XAI_API_KEY_ENV=DOSSIER_XAI_API_KEY XAI_GROK_REASONING_EFFORT=low PROMPTFOO_EVAL_TIMEOUT_MS=240000 ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --providers "python:$(pwd)/providers/xai_grok_responses.py" --filter-prompts conservative-count --no-cache --output results/grok45-skill-pilot-low-strict-schema-20260722.json -j 3
```

Fresh Gemini incumbent:

```bash
source ~/.nvm/nvm.sh && nvm use 24 >/dev/null 2>&1 && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env PROMPTFOO_EVAL_TIMEOUT_MS=240000 ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --filter-providers 'google:gemini-3-flash-preview' --filter-prompts conservative-count --no-cache --output results/grok45-skill-pilot-incumbent-gemini3-flash-20260722.json -j 3
```

High-reasoning retry of the failed Grok cases:

```bash
source ~/.nvm/nvm.sh && nvm use 24 >/dev/null 2>&1 && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/dossier/.env.local XAI_API_KEY_ENV=DOSSIER_XAI_API_KEY XAI_GROK_REASONING_EFFORT=high PROMPTFOO_EVAL_TIMEOUT_MS=240000 ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --providers "python:$(pwd)/providers/xai_grok_responses.py" --filter-prompts conservative-count --filter-failing results/grok45-skill-pilot-low-strict-schema-20260722.json --no-cache --output results/grok45-skill-pilot-high-failure-retry-strict-schema-20260722.json -j 1
```

Those are the exact historical commands. The live provider path now contains
later hardening. To regenerate the scored request contract from the recorded
base, substitute
`python:../docs/evals/evidence/019-xai-grok-responses-evaluated.py` for the
strict-smoke/full/retry provider argument. That tracked snapshot is byte-for-byte
the dirty adapter used for those three runs; it contains no credential.

## Evaluated-code and evidence manifest

The run used PromptFoo `0.121.1`, Node `v24.13.1`, and Darwin arm64. The base
HEAD alone does not identify the Grok scoring code because the strict-schema
repair was uncommitted when the score was produced:

| Surface | SHA-256 | Notes |
| --- | --- | --- |
| Base HEAD | `41c06e20f08127fd8bbddb1997bf75a9879798c7` | Clean task, prompt, scorer, and golden base |
| Original prompt-only adapter | `b2f62248e948dddd4cc0227a4545a9bab65c4910ae35073022ecedd1481ec9f2` | Used only for the first smoke; git blob `c195ae86016c6d66f2f7f90b27287169f6c5a8bf` |
| Repaired evaluated adapter | `f0c1ba9a845471bdf63ef21e013e7a14361095740a66db80003274be019cf8d3` | Used for strict smoke, full Grok arm, and high retry; tracked exact snapshot `docs/evals/evidence/019-xai-grok-responses-evaluated.py`, 7,236 bytes, git blob `5b740d3aa1ba14269197fae9244aa4becf00797d` |
| `tasks/image-crop-extraction.yaml` | `7edae5fe3c935517396a8d37cd8f148cb2b592ed4d206168dbb62273d758cf3e` | Fixed task |
| `prompts/crop-conservative-count.js` | `9a22e566f30eac6258a78a28107d77a17940eca06858dd20cb8d7bc97fc84aba` | Fixed prompt |
| `scorers/image_crop_scorer.py` | `7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7` | Fixed scorer |
| `golden/image-crops.json` | `2ac0a8f01e00a252439da1f4827a85bc5118bf96460a3ff1780e642eafc60f90` | Fixed source-backed golden |

The ignored raw artifacts retained after the pilot were:

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `grok45-skill-pilot-transport-20260722.json` | `f4a20f8d91fb1ceb87ba6adf381fd05abaf8e7119c5754002da0c8cc373d0df1` | 4,175 |
| `grok45-skill-pilot-harness-smoke-prompt-json-20260722.json` | `943db60bdd171fbfc590f6310d20abc1fdffb9ba5612bd1a2aa140cd22461e2c` | 1,202,801 |
| `grok45-skill-pilot-harness-smoke-strict-schema-20260722.json` | `f169658178bc5b4a442eb7ee9ea9992732ca9fa76e8e8b12e5ce54704632b600` | 1,203,163 |
| `grok45-skill-pilot-low-strict-schema-20260722.json` | `6e110c628ff925f423d315fe47f02451cc7cfd768c6abf4603cc753410500df1` | 9,616,943 |
| `grok45-skill-pilot-high-failure-retry-strict-schema-20260722.json` | `370d3423c0a031fb62c13b243857735c71bd4e465070e67a60c25b92619ca0d1` | 438,710 |
| `grok45-skill-pilot-incumbent-gemini3-flash-20260722.json` | `634e83193e5365c757741ef2d3126ef011d556986ea33f4e674a13931b703bbd` | 9,683,027 |

These hashes authenticate retained local copies; they do not make the ignored
JSON files portable by themselves. This tracked note preserves the aggregate
and case-level decision evidence plus safe regeneration commands. The Gemini
artifact records the requested PromptFoo provider but not served-model metadata,
so no served fingerprint is claimed for that arm. Subsequent adapter hardening
is validated separately below and is not represented as the code that produced
the recorded scores.

## Post-pilot adapter hardening

Acceptance review after the scored pilot found residual adapter risks. The
generic provider hard-coded the detector schema even though the page-context
prompt has a materially different output contract; it treated terminal state
too loosely; and a final audit found that it recorded, but did not enforce, the
served-model identity or selected schema before scoring. Those risks were
repaired after the recorded comparison:

- `crop_regions` remains the default strict contract and now permits the
  optional `adjacent_text` field required by the maintained two-step prompt.
- `page_context_validation` is a selectable strict contract matching
  `verdict`, `has_page_text`, `excessive_blank`, and `reason`. It was verified
  locally, not called against the provider, because the pilot did not advance
  to that surface.
- A response now reaches scoring only when xAI reports `status=completed`, no
  provider error or incomplete details are present, the served model matches the
  explicit expected identity, and output is valid JSON matching the selected
  contract. Failure results retain usage, reported cost, ZDR, status, and error
  evidence; invalid output is fingerprinted by SHA-256 rather than sent to the scorer.
- Parsed message input now fails closed when a message or content block is empty,
  malformed, or unsupported instead of silently dropping a required image, file,
  or other payload before evaluation.
- Only documented final-message `output_text` is accepted. Non-object or
  malformed envelopes, malformed/non-finite usage and cost, unexpected output
  item types, empty error objects, extreme numeric values, and pathological JSON
  all fail closed as operational/contract evidence instead of reaching a scorer
  or raising out of the provider.
- Result metadata now records requested model, reasoning, output contract,
  maximum output tokens, image detail, and storage setting alongside served
  model and response metadata.

The first hardened adapter had SHA-256
`1b1509a510d52bf615b0ab50d23d0a7590a4622d99fe3307e360b0e116b13a47`
and computed git blob ID `d264187d19ab120f6ddeb3f573bf18293a2b1441`; that is
the version used by the one paid smoke below. Only those hashes remain—the
first-hardening blob itself was not retained in Git. The final locally validated
adapter, after adding served-model, response-contract, lossless-input, and
final-message enforcement, has SHA-256
`29f1f74019118ddea2b1e40caebc074520e6f1d17bb526991abd32b3f6eff920`
and git blob `1bcd37c441a388a7c211bb78d166ab71693ae280`. Both are deliberately
different from the evaluated adapter fingerprint above.

One new public-fixture parity smoke was run after focused local validation:

```bash
source ~/.nvm/nvm.sh && nvm use 24 >/dev/null 2>&1 && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/dossier/.env.local XAI_API_KEY_ENV=DOSSIER_XAI_API_KEY XAI_GROK_REASONING_EFFORT=low XAI_GROK_OUTPUT_CONTRACT=crop_regions PROMPTFOO_EVAL_TIMEOUT_MS=240000 ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --providers python:/Users/cam/.codex/worktrees/model-eval-skill/doc-web/benchmarks/providers/xai_grok_responses.py --filter-prompts conservative-count --filter-first-n 1 --no-cache --output results/grok45-skill-hardening-parity-crop-20260722.json -j 1
```

It completed `1/1` with strict unfenced JSON, served model `grok-4.5`, response
status `completed`, requested `crop_regions`/low/high-detail metadata, ZDR
header `false`, 3,066 tokens, and reported cost `$0.0062944`. The ignored result
is 1,203,758 bytes with SHA-256
`9e7a0a912dbc2b9601219ab1f83b313b1fd75745527f15bd5bda73a11c13ee95`.
This was contract validation only and ran before the final local-only
served-model/schema, lossless-input, and final-message rejection patches. Its
recorded exact model and schema-valid output satisfy those final gates, but no
second provider call, full comparison score, or adoption verdict was run.

## Artifacts

- `benchmarks/results/grok45-skill-pilot-transport-20260722.json`
- `benchmarks/results/grok45-skill-pilot-harness-smoke-prompt-json-20260722.json`
- `benchmarks/results/grok45-skill-pilot-harness-smoke-strict-schema-20260722.json`
- `benchmarks/results/grok45-skill-pilot-low-strict-schema-20260722.json`
- `benchmarks/results/grok45-skill-pilot-high-failure-retry-strict-schema-20260722.json`
- `benchmarks/results/grok45-skill-pilot-incumbent-gemini3-flash-20260722.json`
- `benchmarks/results/grok45-skill-hardening-parity-crop-20260722.json`
- `docs/evals/evidence/019-xai-grok-responses-evaluated.py`

Official sources checked:

- <https://docs.x.ai/developers/models/grok-4.5>
- <https://docs.x.ai/developers/grok-4-5>
- <https://docs.x.ai/developers/model-capabilities/images/understanding>
- <https://docs.x.ai/developers/model-capabilities/text/reasoning>
- <https://docs.x.ai/developers/model-capabilities/text/structured-outputs>
- <https://docs.x.ai/developers/pricing>
- <https://docs.x.ai/developers/faq/security>
- <https://docs.x.ai/developers/release-notes>

## Validation

- `make methodology-compile` and `make methodology-check`: passed; generated
  graph and story index are current.
- Skill compatibility sync and `scripts/sync-agent-skills.sh --check`: passed
  with 29 canonical skills and valid compatibility links.
- Focused hardened xAI adapter tests: `20 passed`, including lossy prompt-input,
  wrong-served-model, schema-invalid completed-response, malformed envelope/usage,
  multiple-message, extreme numeric, and pathological JSON rejection.
- Independent adversarial review: 24 malformed/valid response envelopes and 34
  pathological contract values produced no exception or fail-open scoring.
- Focused Ruff lint and format checks after hardening: passed.
- One public-fixture, no-cache first-hardening parity smoke: `1/1`, no error,
  exact served model and terminal status recorded; `$0.0062944`. Final
  served-model/schema, lossless-input, and final-message rejection paths were
  subsequently validated locally only.
- `make lint`: passed.
- `make test`: `889 passed`, 4 unrelated existing Pydantic deprecation
  warnings, in `807.17s`.
- `git diff --check`: passed.
