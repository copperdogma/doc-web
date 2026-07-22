# Gemini 3.6 Flash and Gemini 3.5 Flash-Lite Bounded Challengers

Date: 2026-07-21
Repo HEAD at measurement: `ac574bf` (evaluation files uncommitted)

## Trigger and access proof

Google announced the generally available `gemini-3.6-flash` and
`gemini-3.5-flash-lite` model IDs. Official documentation lists a 1M-token
input window, a 65K-token output limit, multimodal input, and standard API
pricing of `$1.50 / $7.50` per million input/output tokens for Gemini 3.6
Flash and `$0.30 / $2.50` for Gemini 3.5 Flash-Lite.

Sources:

- <https://ai.google.dev/gemini-api/docs/latest-model>
- <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/>

`python scripts/discover-models.py --check-new` found both exact IDs in the
configured Google account. A misleading first promptfoo failure came from a
stale global `GOOGLE_API_KEY` overriding the repo-local key. With that variable
unset and the repo wrapper mapping `DOC_WEB_GEMINI_API_KEY`, both one-case image
smokes completed successfully. This was transport/configuration-wrong, not
model-wrong.

## Maintained crop results

| Surface | Candidate | Result | Mean latency | Estimated cost | Decision |
| --- | --- | ---: | ---: | ---: | --- |
| Detector, 13 pages | Gemini 3.6 Flash | `13/13`, `0.9692` | `4459.8 ms` | `$0.0897` | Do not replace Gemini 3 Flash (`13/13`, `0.9703`, about `$0.059`) |
| Detector, 13 pages | Gemini 3.5 Flash-Lite, prompt-only JSON | `8/13`, `0.6427` | `1431.0 ms` | `$0.0083` | Provisional; output contract was not enforced |
| Detector, 13 pages | Gemini 3.5 Flash-Lite, structured integer bboxes | `12/13`, `0.8988` | `1591.1 ms` | `$0.0087` | Reject as maintained detector; one material bbox miss remains and incumbent is `13/13`, `0.9703` |
| Crop-only, 40 crops | Gemini 3.6 Flash | `39/40`, `0.975` | `4145.3 ms` | `$0.1730` | Reject; incumbent Gemini 3.1 Flash Lite is `40/40` |
| Crop-only, 40 crops | Gemini 3.5 Flash-Lite | `39/40`, `0.975` | `4183.9 ms` | `$0.0230` | Reject; incumbent is more accurate and was faster in its maintained proof |
| Page context, 22 cases | Gemini 3.6 Flash | `21/22`, `0.9545` | `4569.5 ms` | `$0.1532` | Reject; incumbent GPT-5.5 Responses is `22/22` |

Costs are estimates from the raw promptfoo token counts and Google's current
standard prices; Gemini 3.6 Flash reasoning tokens are counted as output.
Gemini 3.5 Flash-Lite was not promoted to the page-context gate because its
corrected detector score still did not beat the incumbent and its crop-only
result also missed the maintained bar.

### Flash-Lite structured-output correction

The first detector call relied on prompt-only JSON. That made the malformed
JSON and nested/mixed-coordinate results pipeline/configuration-wrong rather
than decisive model failures. The maintained promptfoo task now gives this
provider a Gemini `responseSchema`. A first schema pass using normalized
floating-point coordinates eliminated the structural errors and reached
`11/13`, `overall = 0.8617`. Its two remaining misses both serialized an
intended leading value near `0.098` as `0.98`, so a final generic contract used
integer `0-1000` boxes with the same golden and scorer. That final no-cache run
reached `12/13`, `overall = 0.8988`, `0` provider errors, average latency
`1591.1 ms`, and estimated cost `$0.0087`.

The remaining `Image121` failure is model-wrong. The candidate correctly found
three visuals, but returned `[452, 448, 506, 896]` for the lower-left oval
portrait, reducing the box to a narrow vertical strip. Manual source review
confirmed the portrait actually spans roughly the left half of the lower page;
the checked golden is correct. The corrected run therefore clears the eval's
`0.90` pass-rate component (`12/13 = 0.9231`) but still misses its `0.95`
overall target and the maintained detector's `13/13`, `0.9703` result.

Manual image review classified the decisive misses as model-wrong:

- Flash-Lite's original mixed/nested/malformed outputs were corrected by the
  structured-output contract and are classified pipeline/configuration-wrong.
  Its final `Image121` lower-left portrait box remains model-wrong.
- Both candidates passed `page-126-000` even though the crop visibly includes
  external book-page text along its left edge.
- Gemini 3.6 Flash passed page-context case `page-122-001` even though the crop
  visibly leaks a slice of the neighboring Sophie portrait.

Local raw results:

- `benchmarks/results/gemini36-flash-image-crop-extraction-20260721.json`
- `benchmarks/results/gemini35-flash-lite-image-crop-extraction-20260721.json`
- `benchmarks/results/gemini35-flash-lite-structured-image-crop-extraction-20260721.json`
- `benchmarks/results/gemini35-flash-lite-structured-int-bbox-image-crop-extraction-20260721.json`
- `benchmarks/results/gemini36-flash-crop-validation-20260721.json`
- `benchmarks/results/gemini35-flash-lite-crop-validation-20260721.json`
- `benchmarks/results/gemini36-flash-crop-page-level-deletion-gate-20260721.json`

## Corrected real-handwriting screen

Both candidates ran through `driver.py` on the corrected Barney and Alverson
image-entry fixtures and produced real `page_html_v1` artifacts. During
scoring, the default `difflib.SequenceMatcher` autojunk heuristic collapsed
near-matching long, repetitive OCR strings to implausibly low ratios. The
scorer now disables autojunk and has a focused regression test. This is a
scorer-wrong correction; it changes historical raw ratios but does not turn
either new candidate into a passing OCR path.

| Candidate | Barney | Alverson | Real-pair floor | Fixtures at `0.99` |
| --- | ---: | ---: | ---: | ---: |
| Gemini 3.6 Flash | `0.984527` | `0.984052` | `0.984052` | `0/2` |
| Gemini 3.5 Flash-Lite | `0.974964` | `0.989935` | `0.974964` | `0/2` |

Manual comparison against both source scans confirmed genuine remaining
literal-transcription errors: name/spelling substitutions on Barney and
normalization or omission of original spellings on Alverson. Candidate-token
cost lower bounds are about `$0.0113` for Gemini 3.6 Flash and `$0.0030` for
Gemini 3.5 Flash-Lite; the 3.6 estimate excludes hidden thinking tokens not
reported by the current OCR client.

Primary driver artifacts:

- `output/runs/eval-barney-image-gemini-3-6-flash/02_ocr_ai_gpt51_v1/pages_html.jsonl`
- `output/runs/eval-alverson-image-gemini-3-6-flash/02_ocr_ai_gpt51_v1/pages_html.jsonl`
- `output/runs/eval-barney-image-gemini-3-5-flash-lite/02_ocr_ai_gpt51_v1/pages_html.jsonl`
- `output/runs/eval-alverson-image-gemini-3-5-flash-lite/02_ocr_ai_gpt51_v1/pages_html.jsonl`

## Decision

**Do not adopt either model in doc-web.** Keep Gemini 3 Flash for maintained
crop detection, Gemini 3.1 Flash Lite for crop-only validation, GPT-5.5
Responses for the page-context deletion gate, and the existing handwriting
rescue path. Gemini 3.6 Flash is competitive but fails one crop-only case, one
page-context case, and both strict real-handwriting cases. Gemini 3.5
Flash-Lite is inexpensive and its API-enforced output contract is reliable, but
its final detector quality still misses the maintained overall target and it
also misses the crop-only and handwriting bars. Story 191 remains blocked.
Its single-surface speed/cost advantage does not justify a second detector plus
fallback route when the maintained single-model detector already clears all 13
cases at higher overall quality.

Retry only after a materially new model or prompt/runtime change can plausibly
clear a maintained incumbent or the `0.99` corrected-real-handwriting bar.
