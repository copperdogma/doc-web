# Claude Fable 5.1 `/evaluate-model`

Date: 2026-09-01
Repo base: `0864678de68246e3fe62fddd90c62585d16e17b3`
Branch: `codex/fable51-docweb-eval-20260901`
Status: Complete — detector do not adopt; page-context capability not measured

## Decision contract

Evaluate first-party Anthropic `claude-fable-5-1` on the frozen 13-case
`image-crop-extraction` detector before considering Story 209's materially
distinct 22-case page-context gate. The candidate arm used adaptive thinking,
explicit high effort, `max_tokens = 16384`, native strict JSON Schema plus
fail-closed local validation, the frozen `conservative-count` prompt, public
checked-in fixtures, no cache, and concurrency `1`.

The detector had to pass `13/13`, reach aggregate `>= 0.95`, and have zero
transport/schema errors before advancing. At most two evidence-led
transport/configuration repairs and US$3.50 total Anthropic spend were allowed.
The separate 40-case crop-only lane, fresh incumbent rerun, runtime-default
changes, commits, pushes, merges, and deployment were outside the approved
screen.

Frozen SHA-256 fingerprints:

- task: `0dbac27f12ed7ab56f840676eb72cb8d79798d8e4e3a6a142da19b26bd8a0531`
- prompt: `bca281e0fbe547e3f3ef049b436d87c73ed7bb066e86f51145fb444b48211b64`
- scorer: `7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7`
- golden: `2ac0a8f01e00a252439da1f4827a85bc5118bf96460a3ff1780e642eafc60f90`
- starting adapter: `f6b76068d915968bbf9790d5447fa7f39f4a21808914c0dccb011986cb748c61`

## Provider and privacy contract

Official Anthropic sources checked for the release and API contract:

- <https://www.anthropic.com/claude-fable-and-mythos-5-1>
- <https://platform.claude.com/docs/en/models/fable-5-1/overview>
- <https://www.anthropic.com/claude/fable>

Fable 5.1 and invitation-only Mythos 5.1 are the same underlying model; the
general first-party API route is exact ID `claude-fable-5-1`. Anthropic
documents image input, adaptive thinking, native structured output, 1M context,
128K maximum output, and standard pricing of `$10/M` input and `$50/M` output.
The normal API retention posture is 30 days unless a stronger organization
agreement applies; this run did not establish account-level ZDR.

Doc Web's existing owner credential was used through `DOC_WEB_ENV_FILE`; no
credential was copied into the worktree or Conductor. Only generated synthetic
content and the repo's approved public checked-in page fixtures were sent.

## Qualification

Authenticated `python scripts/discover-models.py --check-new` listed exact
`claude-fable-5-1`, proving account visibility. The existing direct Anthropic
Messages adapter then passed:

1. strict-schema text: exact served model, terminal `end_turn`, valid usage,
   `{"images":[]}`, cost `$0.003970`;
2. generated 256x256 square vision: exact `[0.25, 0.25, 0.75, 0.75]`, valid
   schema and attribution, cost `$0.007980`;
3. one-case PromptFoo parity on `Image000`: scorer pass, score `0.8384`, exact
   model and terminal state, cost `$0.055320`.

The first parity command used a provider path relative to the process working
directory. PromptFoo resolves custom providers relative to the task file, so
the worker failed locally before any provider call. The first bounded repair
changed only that path to `python:../providers/anthropic_opus48_messages.py`;
the corrected parity call passed. No model setting, prompt, scorer, or fixture
changed.

Ignored parity result:
`benchmarks/results/fable51-evaluate-model-parity-20260901.json`, SHA-256
`4639178f5075bff2d12b3c9f8381be8143fb8ecdf32cfa9be2186165acf35809`.

## Detector result

The candidate-only 13-case run completed all calls:

```text
12/13 scorer passes
1 contract error
aggregate score including quarantined error: 0.870015
mean of 12 schema-valid rows: 0.942517
average latency: 6661 ms
maximum latency: 8097 ms
prompt tokens: 61164
completion tokens: 2405
detector cost: $0.731890 total ($0.056299/call average)
```

`Image059` returned one bbox outside normalized `[0,1]`. The provider-native
schema cannot express numeric ranges, so the adapter's mandatory local
validator quarantined the output and retained only its SHA-256
`ce6c160ef48e7459d974e38c23713fb3376fff089b06a30eeca9f9e8304ef15b`.
This is a model-contract error, not a scorer or golden error. Even excluding
that row, the valid-row mean `0.942517` remained below `0.95`.

Manual source/golden/output inspection found additional model-quality misses:

- `Image000` should cover the full decorative book cover; Fable inset the box
  to `[0.07, 0.04, 0.96, 0.95]`, producing `0.8384`.
- `Image011` found both intended regions but undercovered the lower seal and
  signatures to `y1 = 0.87` versus golden `0.896667`, producing `0.8746`.
- `Image021` extended the portrait into caption space to `y1 = 0.681` versus
  golden `0.666667`, producing `0.9369`.

Ignored detector result:
`benchmarks/results/fable51-evaluate-model-detector-20260901.json`, SHA-256
`601c95e420e384e5c19a02ceab3c085f10b2d4af32b0ebabc1d261d607480600`.

Total measured Anthropic spend was `$0.799160`: `$0.011950` native
qualification, `$0.055320` PromptFoo parity, and `$0.731890` detector. The
failed local command made no provider call. This remained below the US$3.50
cap.

## Reproduction shape

Run from `benchmarks/` through the repo environment wrapper with the owner env
file selected, exact model and expected served model both set to
`claude-fable-5-1`, `max_tokens = 16384`, and Fable 5.1 list-price overrides:

```text
../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/image-crop-extraction.yaml \
  -r python:../providers/anthropic_opus48_messages.py \
  --filter-prompts conservative-count --no-cache -j 1 --no-share \
  --output results/fable51-evaluate-model-detector-20260901.json
```

## Decision

**Access: available. Transport: qualified. Detector reliability/quality: below
target. Economics: not competitive. Adoption: do not adopt. Page-context
capability: not measured.**

The candidate missed both the zero-error gate and the `>= 0.95` quality gate,
while its `$0.731890` detector cost was about fourteen times the fresh
comparable Gemini 3 Flash control's recorded `$0.0526175`. The 22-case
page-context gate therefore did not run. Maintained providers, prompts,
scorers, goldens, and runtime defaults remain unchanged.
