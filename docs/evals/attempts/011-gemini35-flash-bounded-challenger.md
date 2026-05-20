# Gemini 3.5 Flash Bounded Challenger

Date: 2026-05-20
Repo HEAD at measurement: `99450a3`

## Trigger

The inbox noted Conductor Scout 035's claim that Google's `gemini-3.5-flash`
is a plausible doc-web challenger for image/PDF inputs, structured output, and
1M context. Current Google documentation lists the stable model code as
`gemini-3.5-flash`, with text/image/video/audio/PDF inputs, 1,048,576 input
tokens, 65,536 output tokens, and a 2026-05-19 page update:
<https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash>.

Repo-local model discovery using the canonical project `.env` confirmed the
model is callable through the Gemini models endpoint and is not yet recorded in
`docs/evals/registry.yaml`.

## Detector Result

Command:

```bash
cd benchmarks && promptfoo eval \
  -c tasks/image-crop-extraction.yaml \
  --providers google:gemini-3.5-flash \
  --filter-prompts 'conservative-count' \
  --no-cache \
  --output results/gemini35-flash-image-crop-extraction-20260520.json \
  -j 1
```

The run used `DOC_WEB_GEMINI_API_KEY` from the canonical project checkout and
explicitly unset stale `GOOGLE_API_KEY` after `nvm use`, because promptfoo's
Google provider otherwise prefers the broader Google key when both are present.

Metrics:

- Result artifact:
  `benchmarks/results/gemini35-flash-image-crop-extraction-20260520.json`
- Result: `13/13`, `0` failures, `0` provider errors
- Mean score: `0.9679`
- Average latency: `9675 ms`
- Token use: `26609` total (`17329` prompt, `1443` completion, `7837`
  reasoning)
- Estimated paid-standard cost from current Google pricing
  (<https://ai.google.dev/gemini-api/docs/pricing>): about `$0.1095` total,
  `$0.0084` per case. The actual run consumed free-tier quota.

Representative inspected rows:

- `Image000`: pass, `score = 0.8303`, full-cover crop remains the weakest
  case but still clears the scorer.
- `Image020`: pass, `score = 0.9973`, both ranch-photo boxes matched.
- `Image126`: pass, `score = 0.9796`, both monument/plaque boxes matched.

Decision: do not adopt for the maintained detector. It passes the target, but
it is slightly below the current Gemini 3 Flash maintained rerun (`0.9703`,
`13/13`), slower in this run (`9675 ms` vs about `7878 ms` per page), and
costlier on paid-standard pricing (about `$0.1095` total vs about `$0.059` for
the maintained detector proof).

## Validator Results

The crop-only validator and page-context deletion gate were initially blocked.
After the detector run, the Gemini API started returning quota errors for
`gemini-3.5-flash`:

```text
Quota exceeded for metric:
generativelanguage.googleapis.com/generate_content_free_tier_requests,
limit: 20, model: gemini-3.5-flash
```

Evidence artifacts from the stopped direct fallback attempts:

- `benchmarks/results/gemini35-flash-crop-validation-direct-20260520.json`
- `benchmarks/results/gemini35-flash-crop-page-level-deletion-gate-direct-20260520.json`

The first direct fallback artifacts captured that quota-only state and must not
be treated as quality scores. Google's rate-limit documentation says limits
include requests per minute and requests per day, are applied per project rather
than per API key, and vary by usage tier:
<https://ai.google.dev/gemini-api/docs/rate-limits>.

After the user added more credit but before the project was promoted to paid
tier, I rechecked the canonical doc-web Gemini key after the competing local
Gemini 3.5 Flash benchmark ended and a full cooldown window elapsed. The probe
still returned:

```text
quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier
quotaValue: 20
quotaMetric: generativelanguage.googleapis.com/generate_content_free_tier_requests
model: gemini-3.5-flash
```

The alternate shell `GOOGLE_API_KEY` is not usable for this eval; the Gemini API
returned `API_KEY_INVALID` for that key.

After the project was promoted to paid tier, the free-tier quota error cleared:
fresh text-only probes and a one-case crop-validation probe stopped returning
`429` quota errors. They instead returned:

```text
503 UNAVAILABLE
This model is currently experiencing high demand.
```

Availability evidence artifact:

- `benchmarks/results/gemini35-flash-availability-probes-20260520.json`

I then ran five additional low-rate text-only health probes over roughly eight
minutes. All five returned the same `503 UNAVAILABLE` high-demand response.

On the next heartbeat retry, the text-only health gate succeeded on the
canonical doc-web key with `serviceTier: standard`, so I reran the two blocked
crop surfaces through a direct Gemini REST fallback using the maintained prompt
text and Python scorers from the promptfoo tasks. I used `maxOutputTokens:
16384` because Gemini 3.5 Flash emits hidden thinking tokens.

Crop-only validator result:

- Result artifact:
  `benchmarks/results/gemini35-flash-crop-validation-direct-20260520.json`
- Result: `39/40`, `0` provider errors
- Score: `0.975`
- Average latency: `3767 ms`
- Token use: `71027` total (`57182` prompt, `2713` candidate, `11132`
  thinking)
- Estimated paid-standard cost from current Google pricing: about `$0.2104`
  total, `$0.0053` per case
- Failure: `page-126-000`, model-wrong false negative. The golden fails this
  crop because book-page text is visible along the left side, but Gemini 3.5
  Flash treated the text as integral plaque text.

Page-context deletion-gate result:

- Result artifact:
  `benchmarks/results/gemini35-flash-crop-page-level-deletion-gate-direct-20260520.json`
- Result: `21/22`, `0` provider errors
- Score: `0.954545`
- Average latency: `4554 ms`
- Token use: `70296` total (`59636` prompt, `1533` candidate, `9127`
  thinking)
- Estimated paid-standard cost from current Google pricing: about `$0.1854`
  total, `$0.0084` per case
- Failure: `page-122-001`, model-wrong false negative. The corrected golden
  fails the crop for a visible neighboring portrait slice, but Gemini 3.5 Flash
  passed it as a clean two-portrait extraction.

## Handwritten OCR Screen

I then ran the bounded real-fixture image-entry handwritten OCR screen without
editing maintained recipes:

- Barney artifact:
  `output/runs/eval-barney-image-gemini-3-5-flash/02_ocr_ai_gpt51_v1/pages_html.jsonl`
- Alverson artifact:
  `output/runs/eval-alverson-image-gemini-3-5-flash/02_ocr_ai_gpt51_v1/pages_html.jsonl`
- Result summary:
  `benchmarks/results/handwritten-notes-gemini35-flash-image-screen-20260520.json`

Scores:

- Barney image-entry: `overall_ratio = 0.807498`
- Alverson image-entry: `overall_ratio = 0.247350`
- Screen floor: `overall_min_ratio = 0.247350`, `page_min_ratio = 0.247350`,
  `0/2` cases cleared the `0.99` bar

Manual inspection confirmed the low Alverson score is not a scoring quirk: the
artifact contains wrong-source text such as `Danville Va Nov 18th 1863` and
`Battle of Chickamauga` on the Alverson page. Barney is coherent but still
normalizes or drifts on words the maintained rescue path handles better.
Because Gemini 3.5 Flash did not beat both corrected real fixtures, I did not
promote it to a PDF-entry or full five-fixture rerun.

## Decision

Do not change maintained providers.

`gemini-3.5-flash` is a valid new detector challenger and clears the detector
target, but it does not beat the maintained Gemini 3 Flash detector. The
crop-only validator ties the recent GPT-5.5-style `39/40` result but still
loses to the maintained Gemini 3.1 Flash Lite `40/40` score. The page-context
gate also misses `1/22` and does not replace the maintained GPT-5.5 Responses
winner. The handwritten real-fixture screen is worse than the maintained
Gemini 2.5 Pro rescue lane. No maintained providers, prompts, scorers, or
goldens should change.
