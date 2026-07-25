# Claude Opus 5 `/evaluate-model`

Date started: 2026-07-24
Date completed: 2026-07-25
Repo HEAD at start: `3bb7ad93296fef08b3f3bdb6941981a082668f37`
Status: Complete — detector do not adopt; page-context capability not measured

## Interpreted brief and progressive gate

Evaluate Anthropic Claude Opus 5 on the frozen 13-case
`image-crop-extraction` detector first. Run the materially distinct 22-case
`crop-page-level-deletion-gate` only if the detector passes all `13/13` cases
and clears the maintained aggregate `>= 0.95` target.

The candidate configuration was predeclared before spend:

- first-party Claude API model `claude-opus-5`
- adaptive thinking and explicit `output_config.effort = high`
- `max_tokens = 16384`
- native `output_config.format` JSON Schema plus fail-closed local validation
- frozen `conservative-count` prompt, fixtures, scorer, and golden
- `--no-cache`, concurrency `1`, and a total provider-spend cap of US$5
- at most two evidence-led transport/configuration repairs

Stories 207 and 209 remain the coherent owners. No new story or ADR was needed.
This directly tests C4/C5 against the Ideal's one-call, source-faithful crop
goal without changing runtime defaults.

## Current provider contract

First-party Anthropic sources checked on 2026-07-24:

- Models overview:
  <https://platform.claude.com/docs/en/about-claude/models/overview>
- Opus 5 API changes:
  <https://platform.claude.com/docs/en/about-claude/models/whats-new-opus-5>
- Structured outputs:
  <https://platform.claude.com/docs/en/build-with-claude/structured-outputs>
- Pricing:
  <https://platform.claude.com/docs/en/about-claude/pricing>
- API retention:
  <https://platform.claude.com/docs/en/manage-claude/api-and-data-retention>

The exact pinned API ID is `claude-opus-5`. Anthropic documents text and image
input, 1M context, 128k maximum output, adaptive thinking on by default, effort
levels through `max`, and native JSON Schema through
`output_config.format`. Standard pricing is `$5/M` input and `$25/M` output.
Messages, adaptive thinking, and structured outputs are ZDR-eligible when the
organization has ZDR; the current organization-level ZDR state was not proven.
The initial blocked pass sent only a synthetic text prompt. After explicit
approval to resume, the completed detector used the repo's public checked-in
fixtures. No private payload was transmitted.

`python scripts/discover-models.py --check-new` queried the authenticated
repo-scoped Anthropic account and listed `claude-opus-5` as a new available
model. That proves account visibility, not successful inference.

## Transport repair and blocked probes

The existing direct Anthropic PromptFoo adapter omitted unsupported sampling
parameters, but it did not require strict schema output, exact served-model
identity, terminal `end_turn`, valid usage, or lossless multimodal
normalization. Before scoring, the adapter was hardened to enforce those
requirements and received focused fail-closed tests.

The native strict-schema text probe never reached subject generation:

1. Initial request: HTTP 400 because Anthropic structured outputs accept only
   `minItems` values `0` or `1`; the crop schema used `4`.
2. First repair: changed provider-native `minItems` to `1`, retaining exact
   four-coordinate enforcement locally. HTTP 400 because `maxItems` is not
   supported.
3. Second repair: removed provider-native `maxItems`, retaining exact
   four-coordinate enforcement locally. HTTP 400 because numeric `minimum` and
   `maximum` are not supported.

The predeclared two-repair cap was therefore exhausted before any valid subject
response. The next provider-compatible schema candidate removes the unsupported
numeric range keywords while retaining their checks in the local validator,
but it was not sent to Anthropic in this pass. Its live contract remains
unverified.

There was no model output, usage record, result JSON, PromptFoo smoke, detector
score, latency measurement, or mismatch classification. The rejected requests
reported no inference usage, so recorded subject spend is `$0`.

## Local evidence

Prepared but not live-qualified:

- `benchmarks/providers/anthropic_opus48_messages.py`
  SHA-256 `f6b76068d915968bbf9790d5447fa7f39f4a21808914c0dccb011986cb748c61`
- `tests/test_anthropic_opus_messages_provider.py`
  SHA-256 `1dbdb4df99110243d44a0dc8a051139af00e0d515ca9d9bc35daa3a55c6972a9`

Focused checks:

```text
python -m pytest tests/test_anthropic_opus_messages_provider.py -q
8 passed

python -m ruff check benchmarks/providers/anthropic_opus48_messages.py tests/test_anthropic_opus_messages_provider.py
All checks passed!

python -m ruff format --check benchmarks/providers/anthropic_opus48_messages.py tests/test_anthropic_opus_messages_provider.py
2 files already formatted
```

## Approved resume and transport qualification

On 2026-07-25 the user explicitly approved one additional
provider-compatible schema probe. The prepared schema removed unsupported
numeric range keywords from the provider-native schema while retaining exact
four-coordinate and `[0,1]` checks in the fail-closed local validator.

Qualification then passed in three steps:

1. Native strict-schema text returned exact served model `claude-opus-5`,
   terminal `end_turn`, valid usage, and locally valid `{"images":[]}`.
   Cost was `$0.004470`.
2. A generated 256×256 synthetic image with a black square returned
   `[0.254, 0.238, 0.746, 0.754]` against the expected approximate
   `[0.25, 0.25, 0.75, 0.75]`, with exact model, terminal state, valid usage,
   and valid schema. Cost was `$0.003800`.
3. A no-cache, one-case PromptFoo parity smoke on `Image000` passed with score
   `1.0`, exact model, terminal state, and cost `$0.026125`. Ignored raw result
   SHA-256:
   `345800ede33636992c4fc5242b00d5bf540166c80a3e5667cb34885e26350570`.

Transport therefore qualified before the maintained detector fixtures were
sent.

## Detector result

The frozen 13-case detector ran with `--no-cache`, concurrency `1`, the
`conservative-count` prompt, and unchanged scorer and golden:

```text
13/13 per-case assertions passed
0 provider errors
aggregate score: 0.8922
maintained promotion target: >= 0.95
average latency: 5458 ms
prompt tokens: 61138
completion tokens: 2001
detector cost: $0.355715
```

Ignored raw result:
`benchmarks/results/opus5-evaluate-model-detector-20260725.json`, SHA-256
`b07a55fab91c78c695417583270be9e00244bd194f5befd4aa76de42c9973cc1`.
Total successful-call spend across qualification, smoke, and detector was
`$0.390110`.

Manual source/golden inspection classified the weakest rows as model-wrong,
not scorer- or golden-wrong:

| Case | Score | Observed mismatch |
| --- | ---: | --- |
| `Image037` | 0.7891 | Both boxes were loose; the lower crop extended through caption/page space to `y=0.955` versus golden `0.897576`. |
| `Image021` | 0.8096 | The crop included caption space to `y=0.716` versus golden `0.666667`. |
| `Image011` | 0.8146 | Both regions were loose; the seal/signature crop extended to `y=0.933` versus golden `0.896667`. |
| `Image013` | 0.8341 | The crop extended into caption space to `y=0.732` versus golden `0.683333`. |
| `Image121` | 0.8755 | All three regions were found, but the lower portraits extended roughly five percent into captions. |

The model consistently found the right number of regions but drew
caption-bearing or otherwise loose boxes. Because the aggregate score did not
clear `0.95`, the detector prerequisite failed even though all per-case
assertions passed.

## Final decision

**Access: available. Transport: qualified. Detector: below target. Adoption:
do not adopt. Page-context capability: not measured.**

Per the predeclared progressive gate, the expensive 22-case
`crop-page-level-deletion-gate` was not run. The maintained Gemini 3 Flash
detector and GPT-5.5 Responses `22/22` page-context validator remain unchanged.
No provider, prompt, scorer, golden, or runtime default was changed.
