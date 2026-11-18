# Attempt 097 — GPT-6.2 Astra source fidelity

2026-11-17. Scout116 item 3, Story273. Base
`56564d95cd2cf9ce498aaaca84537a64b1e89f31`. Recommend the **opt-in OpenAI
source-only table reader** when comparing on the existing Astra route.
Retain Hydrogen for the reviewed historical handwriting option and retain the
current assisted detector and manual crop review.

| Lane | Fresh matched result | Decision |
|---|---|---|
| Literal tables | Both models read 56/56 clear cells across three previously exposed cases and one newly authored independent source. Both correctly held both optically indistinguishable glyphs in the exposed ambiguity control. 6.2 total $0.247616, mean 6.205s vs Astra $0.314920, 7.437s across four pairs. | 21.37% lower source-reader cost, 16.56% lower mean latency and no measured quality loss. Independent candidate call was 7.142s vs 6.565s, so speed did not improve consistently. Prepare bounded opt-in. |
| Handwriting | Barney 6.2 .962170/$0.119454/67.836s, Hydrogen .988497/$0.049185/36.967s, exact Gemini3.8 .982406/$0.02393175/48.259s. | Reject this 6.2 OCR arm. All three missed .99 on this fresh sample. Prior reviewed Hydrogen qualification remains historical evidence, with this fresh variation recorded. No new Alverson inference. |
| Crop detector | 6.2 Image011 .9972 and Image001 .9940, zero frozen ROI dark-pixel loss at fixed XYXY. Gemini tolerant scorer .9839/.9829 but raw coordinates followed a different axis order. Two 6.2 requests $0.090208/4.297s mean vs Gemini $0.012685/9.0836s. | Bounded geometry lead only. The raw candidate seal/signature box included printed attribution captions. Native assisted original-pixel request was blocked by image patch limit before inference. Keep current detector; no full 13 or actual final-crop quality claim. |

OCR meaningful substitutions include adding “once” and normalizing “comrads”
to “comrades.” Retained recognized text records other gaps and substitutions.
The table ambiguity panel's diagnostic HTML has the same single literal
mismatch in both arms. Both explicitly report both ambiguous cells with
alternative glyphs. The driver blocks export on that negative. This is a safe
hold with no false verified result. The independent authored table froze
all cells and spans before either model saw it, including case differences,
dashes, empty fields, spacing, a rowspan and a spanning footer.

## Consumer and adoption boundary

The alternate recipe selects `gpt-6.2-astra` only at source-only review and
explicitly binds the same profile to final publication. Initial OCR continues
on its independent current Astra profile. With the actual OpenAI SDK and an
offline MockTransport, exact request JSON matches the paid wire and the full
original envelope passes the normal reader. The positive independent fixture
then traverses the actual driver, literal reviewer and HTML exporter using a
hash-bound retained receipt. The final table passes exact structural/literal
comparison and the qualification artefact is bound in the manifest. The
negative fixture stops at review with two uncertain cells and no export.
First-stage OCR bytes are deterministic source-authored fixture inputs during
replay; stage A was outside the replacement scope.

The opt-in reader verifies exact native input count before each inference. The
$2 reservation covers at most 68,928 input tokens at the full 30-minute cache
write price and all 32,768 output tokens. The offline replay also refuses a
68,929-token count before inference. Existing Astra receipts and reserves
are unchanged.

Native request selection, caller, and final exporter validation are represented
in the opt-in patch. Two initial offline driver trials exposed a load artifact
filename mismatch and then a missing explicit final-build model authority.
Both were recovered offline with untouched provider outputs and preserved
failure logs. Publication did not accept the different authority early.

See [table consumer](../evidence/097-astra62/table-consumer.json) and
[opt-in recipe and rollback](../../runbooks/astra62-literal-table-reader.md).
The separately available Argon opt-in has lower historical source-reader cost
on the exposed panel. This campaign measures an improvement over the maintained
OpenAI Astra role, not superiority over Argon or end-to-end production savings.
Defaults and publication policy are unchanged. Eligibility is limited to
reviewed public/synthetic source work within the qualified contract.

## Crop transport stop

The native token count endpoint repeated HTTP400 `invalid_value` on the exact
planned Story231 candidate request for the original 5100×6600 Image011,
reporting 33,120 patches against a maximum of 30,000. Other original fixture
pages Image121 and Image124 have the same dimensions and patch count, and the
cover Image000 is 33,920 patches and already bypassed. The consumer selects
the native source image directly. OpenAI detail `high` may reduce the pixels
seen by the model and does not satisfy the selected original-detail comparison.
No resize, model fallback, or additional paid request to force admission. The
remaining 11 benchmark cases can't settle this caller boundary and were
unmeasured. Genuine caption dispatch, assisted cleanup, final image integrity
and adoption were never reached. The raw Gemini tolerant scorer may normalize
axes internally; the fixed-XYXY projection is a separate wire-contract result.

## Provenance and accounting

Exact model visible in authenticated native catalog, then exact served Responses
status and strict structured output where required; OCR retains its maintained
free HTML with first-line metadata. Standard `store:false`, `reasoning.effort:
high`, `max_output_tokens:32768`, original detail, no sampling or fallback.
High was chosen for ambiguous glyphs, literal marks and fine visual positions.
No other Astra 6.2 effort tested. Native usage preserved including reasoning
and cache writes. One request at a time. Public LOC and Onward fixtures and
synthetic tables only. Existing Doc Web owner keys accessed via the standard
wrapper, no credential copy/injection or cleanup needed. OpenAI abuse logging
may apply to API payload; account retention exception and region unverified.

15/15 inference POSTs with valid terminal native outputs. Known estimate
**$0.85799975** of $64 inclusive, zero held, no paid judge. Separate pools:
OCR $0.19257075/$12, table $0.562536/$10, crop $0.102893/$42. Native catalog
and token-count calls separate from inference, no unsettled inference. Cache
writes are charged at reported billed units. Provider meter comparison by
native usage and current public rates, not verified invoice.

- [Model and pricing](https://developers.openai.com/api/docs/models/gpt-6.2-astra)
- [Input image limits](https://developers.openai.com/api/docs/guides/images-vision)
- [Exact input count reference](https://developers.openai.com/api/docs/guides/token-counting)
- [Default 30-minute cache costing](https://developers.openai.com/api/docs/guides/prompt-caching)
- [OpenAI retention](https://developers.openai.com/api/docs/guides/your-data)
- [Google price sheet](https://aistudio.google.com/docs/pricing)
- [Preflight matrix](../evidence/097-astra62/preflight.json), [ledger](../evidence/097-astra62/ledger.json), [manifest](../evidence/097-astra62/manifest.json)

Commands from retained worktree:
`/Users/cam/miniconda3/bin/python benchmarks/scripts/scout116_doc_web.py freeze`
on a fresh owner run, then the same script's `send <matrix name>` through
`DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env python3
scripts/run_with_doc_web_env.py` and the same interpreter. Follow progressive
stops, do not rerun a completed immutable attempt. The confirmation and runtime
matrix scripts extend the frozen matrix in separately captured stages. Offline
consumer replay uses `/Users/cam/miniconda3/bin/python
benchmarks/scripts/scout116_table_consumer.py <fresh-replay-directory>`.

Validated 297 focused owner tests, current methodology graph, SDK request/count replay including over-reservation refusal, and positive/negative final consumer outcomes. No paid replay.
