# GPT-5.6 Luna Price-Refresh Evaluation

Date: 2026-08-03
Repo HEAD at start: `185dadea7701131ee95d2e9d44bdd03d1e0e1a33`
Status: Complete — conditional detector value winner; page-context replacement rejected

## Brief and decision contract

The user requested a force-fresh Luna evaluation because OpenAI cut its price.
The frozen primary surface was Story 207's 13-case `image-crop-extraction`
benchmark with the maintained `conservative-count` prompt. Luna had to clear
`overall >= 0.95`, preserve at least the maintained per-case pass-rate gate,
and offer a material cost/latency advantage against a fresh Gemini 3 Flash
control. The distinct Story 209 page-context gate would run only if detector
quality materially reopened its hard safety decision; a lower price alone
could not erase Attempt 015's source-verified `19/22` Luna result against the
required `22/22`.

Candidate configuration: first-party OpenAI Responses `gpt-5.6-luna`,
`reasoning.effort=none`, strict `crop_regions` JSON Schema, `store=false`,
public checked-in fixtures, `--no-cache`, and concurrency `1`. Prompt,
fixtures, scorer, and golden were frozen. Candidate-plus-incumbent spend was
capped at US$5.

## Current provider contract

OpenAI's current model documentation identifies exact model ID
`gpt-5.6-luna`, 1,050,000-token context, 922,000 maximum input, 128,000 maximum
output, text and image input, text output, Responses and Chat Completions, and
structured outputs. Current standard short-context prices per million tokens
are `$0.20` input, `$0.02` cached input, `$0.25` cache writes, and `$1.20`
output. The July 30 changelog describes this as an 80% price reduction.

Official references:

- <https://developers.openai.com/api/docs/models/gpt-5.6-luna>
- <https://developers.openai.com/api/docs/pricing>
- <https://developers.openai.com/api/docs/changelog>
- <https://developers.openai.com/api/docs/guides/your-data>

`store=false` disables response storage/statefulness for these calls, but it is
not evidence that the account has Zero Data Retention. No ZDR response header
was observed. Only checked-in public benchmark fixtures were therefore sent.

## Qualification and harness repair

`python scripts/discover-models.py --check-new` listed exact
`gpt-5.6-luna` and confirmed the repo credential. The existing PromptFoo shim
was hardened before scoring to require strict task schemas, exact served-model
identity, terminal `completed` status, lossless multimodal normalization, valid
usage, local output validation, `store=false`, final-message extraction, and
cache-aware current pricing. Focused provider tests passed `5/5`.

Live qualification then passed in order:

- strict-schema text: exact Luna, `completed`, output `{"images":[]}`;
- native public-fixture image plus strict schema: exact Luna, `completed`, one
  valid bbox, 3,219 prompt and 67 completion tokens, `$0.0007242`;
- one-case PromptFoo parity: `1/1`, no error, `$0.00022032`.

An earlier image diagnostic was rejected before inference because the local
probe accidentally double-prefixed the data URL. Correcting only that probe
construction error produced the successful native image result; it is not
model-quality evidence.

## Fresh detector comparison

Both arms used the same frozen 13 fixtures, prompt, scorer, golden, no cache,
and concurrency `1`.

| Model | Passes | Mean score | Avg latency | Total cost |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Luna | `13/13` | `0.9650` | `2,306 ms` | `$0.00892992` |
| Gemini 3 Flash, fresh control | `13/13` | `0.9634` | `6,355 ms` | `$0.0483065` |
| Gemini 3 Flash, best eligible historical proof | `13/13` | `0.9703` | `7,878 ms` | about `$0.059` |

Luna was `2.76x` faster and `5.41x` cheaper than the fresh incumbent, while
scoring `+0.0015` higher. The score difference is too small to claim a quality
win and Luna remains `0.0053` below the best historical Gemini result, but it
comfortably clears the maintained quality target and materially wins current
value.

The maintained task contains a deterministic structural scorer only; despite a
default judge setting, it has no semantic rubric assertion. Source-image review
therefore supplied the semantic classification rather than inventing a
non-comparable judge arm:

- `Image000` (`0.8232`): Luna selected the full decorative cover but excluded
  thin outer margins. The golden is the full page; this is a reasonable crop,
  not a serious semantic failure.
- `Image011` (`0.9047`): Luna correctly found the logo and seal/signatures but
  also selected the ordinary certificate title. The extra crop is model-wrong
  over-detection under the frozen prompt.
- `Image121` (`0.9628`): all three photographs were found with tight boxes.
- `Image124` (`0.9715`): the illustration was isolated cleanly without its
  caption.

No prompt, scorer, or golden change is justified.

## Page-context stop gate

The detector result materially changes the cost/value picture, but not Luna's
known safety capability. Attempt 015 measured Luna at `19/22` (`0.8636`) on the
page-context gate with three source-verified model errors; the maintained
GPT-5.5 route is `22/22`. Since fresh detector quality is within ordinary run
variance rather than a new capability jump, the predeclared progressive gate
stopped without paying to repeat that distinct failed surface.

## Evidence and cost ledger

Ignored raw artifacts:

| Artifact | SHA-256 |
| --- | --- |
| `benchmarks/results/luna-price-refresh-smoke-20260803.json` | `91db7121c93c84060f5990e3b62fb18abbdc6f99d8c0c04737378c984b18915e` |
| `benchmarks/results/luna-price-refresh-detector-20260803.json` | `eaaeec3471f9e7cf97d84eb594272eebadd27a395e550ddfbd58de5048b0e3c5` |
| `benchmarks/results/luna-price-refresh-incumbent-gemini3flash-20260803.json` | `11a46dcd2ebae4771a57789d691e2aa8483d6d08c520a2a5500c2718394d4105` |

Frozen task hash: `7edae5fe3c935517396a8d37cd8f148cb2b592ed4d206168dbb62273d758cf3e`.
Prompt hash: `9a22e566f30eac6258a78a28107d77a17940eca06858dd20cb8d7bc97fc84aba`.
Scorer hash: `7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7`.
Qualified adapter hash: `44c1e1fe5875574aa6322be74b9983be912b0eabe30980e22aa6169f171c984f`.

Successful Luna spend was approximately `$0.00990224`: `$0.0000278` text
qualification, `$0.0007242` native image qualification, `$0.00022032` parity
smoke, and `$0.00892992` full detector. The fresh Gemini control cost
`$0.0483065`. Total successful-call comparison spend was about `$0.05821`, far
below the `$5` cap. The rejected malformed diagnostic request did not run
inference.

## Decision

**Conditionally adopt Luna as the preferred value challenger for this frozen
detector surface only.** At current prices it clears the quality gate, matches
the fresh incumbent within noise, and is substantially cheaper and faster.
This is not authorization to change the production crop module: the benchmark
adapter is not its runtime client, and production integration requires its own
driver-backed comparison and artifact inspection.

**Do not adopt Luna for page-context validation or as a broad crop default.**
Its maintained `19/22` safety result remains disqualifying. Keep GPT-5.5 on the
page-context gate. No maintained runtime, prompt, scorer, golden, or coverage
truth was changed by this evaluation.

## Production follow-on — Story 231

Story 231 qualified a strict first-party Responses route inside the production
crop module and compared Luna with Gemini through separate same-input
`driver.py` runs on `Image000`, `Image011`, `Image121`, and `Image124`. Both
routes used the maintained cover bypass, high-resolution image mapping, exact
upstream image descriptions/counts, and production crop parameters; only the
detector and four-page cap differed. The cover therefore bypassed both models
identically. Luna produced all nine expected crops in `47.71 s`; Gemini
produced eight in `107.42 s` after its page-12 detector response could not be
parsed and CV fallback combined the two signatures.

Manual source comparison found the countervailing hard-gate failure: Luna's
page-122 reunion and Sophie crops included their printed captions, while Gemini
kept those captions out. This is **model-wrong at the production artifact
seam**, not golden-wrong or ambiguous. Luna remains the frozen detector value
winner and improves completeness, but the benchmark-only value recommendation
does not promote to the maintained recipe because production C5 text exclusion
is absolute. Gemini remains the Onward detector, GPT-5.5 remains the independent
page-context validator, and Luna remains available as an explicit
recipe-selected challenger. Driver evidence lives under
`output/runs/story231-gemini-production-parity-r1/` and
`output/runs/story231-luna-production-parity-r1/`; inspected contact sheets live
under `output/inspection/story231/`.
