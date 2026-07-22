# Grok 4.5 Bounded Challenger

Date measured: 2026-07-20
Repo HEAD at measurement: `ac574bf`

## Trigger and alignment

xAI's Grok 4.5 release surfaced as a new multimodal frontier-model candidate.
The official xAI announcement is dated 2026-07-16, although this evaluation was
requested and run on 2026-07-20. The bounded ladder remains:

1. `image-crop-extraction` with `conservative-count` (13 cases; maintained
   Gemini 3 Flash baseline `0.9703`, `13/13`).
2. `crop-page-level-deletion-gate` (22 cases; hard `22/22` contract; maintained
   GPT-5.5 Responses winner).

This directly tests the Ideal's fidelity and illustration requirements and the
active C4/C5 compromise-detection surfaces. No narrower crop ADR applies; this
attempt changes no architecture, prompts, scorers, goldens, or maintained
providers.

## Live access and transport

Official xAI documentation and authenticated first-party API checks confirmed:

- direct model ID `grok-4.5` and aliases `grok-4.5-latest` and
  `grok-build-latest`;
- text and image input, text output, a 500,000-token context window, structured
  output support, and low/medium/high reasoning;
- Responses and Chat Completions API support;
- short-context pricing of `$2.00/M` input, `$0.30/M` cached input, and
  `$6.00/M` output, with higher rates at 200,000+ prompt tokens.

Authenticated `GET /v1/models/grok-4.5` and a minimal Responses request both
returned HTTP 200. The bounded promptfoo path used
`benchmarks/providers/xai_grok_responses.py`, which normalizes the maintained
OpenAI-style image blocks into xAI Responses `input_text` / `input_image`
content, sets `store: false` for image requests, preserves usage, and records
xAI's returned cost. The credential stayed in the sibling ignored Dossier env
file and was selected by name without printing or copying it.

## Detector result

The one-case low-reasoning vision smoke passed with valid scored JSON. The full
maintained detector command was:

```bash
cd benchmarks
DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/dossier/.env.local \
XAI_API_KEY_ENV=DOSSIER_XAI_API_KEY \
XAI_GROK_REASONING_EFFORT=low \
PROMPTFOO_EVAL_TIMEOUT_MS=240000 \
../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/image-crop-extraction.yaml \
  --providers "python:$(pwd)/providers/xai_grok_responses.py" \
  --filter-prompts conservative-count --no-cache \
  --output results/grok45-low-image-crop-extraction-20260720.json -j 3
```

Result artifact:
`benchmarks/results/grok45-low-image-crop-extraction-20260720.json`.

- `12/13` scorer passes, `0` provider errors
- `overall = 0.8026`, `pass_rate = 0.9231`
- `38,122` total tokens (`36,959` prompt, `1,163` completion,
  `4,480` cached)
- average latency about `2,433 ms` per page
- total reported cost `$0.07328` (`$0.00564` per page)

This is faster than the maintained Gemini 3 Flash proof, but quality is far
below the maintained `0.9703` score and below the `0.95` detector target.

## Failure classification and bounded retry

The only failing case was `Image011`. Grok correctly found two visual regions,
but it cropped the lower certificate artwork to only the embossed seal
(`bbox ≈ [0.12, 0.68, 0.38, 0.88]`). The maintained source-backed region
includes the seal and adjacent official signatures
(`bbox ≈ [0.12, 0.69, 0.88, 0.90]`). Manual inspection of the decoded source
confirmed the signatures are visibly grouped with the seal at the bottom of the
certificate, and previous passing frontier results cover that full region.

Classification: **model-wrong**. No golden or scorer change is warranted.

A single high-reasoning retry used the low-run failures as its filter. It still
failed `Image011`, scoring `0.5095` versus `0.5000` at low reasoning and again
cropping only the seal. Artifact:
`benchmarks/results/grok45-high-image-crop-failure-retry-20260720.json`.
Higher reasoning did not change the failure class, so the retry cap was reached.

## Page-context gate and decision

The 22-case `crop-page-level-deletion-gate` was intentionally not run. The eval
ladder requires the candidate to clear the cheaper maintained detector gate
before spending on the stricter page-context gate. Grok 4.5 missed both the
`0.95` target and the maintained `0.9703` winner by a wide margin, and high
reasoning did not repair its only hard failure.

**Detector decision: do not adopt.** Its low-reasoning path is fast and
inexpensive, but the bbox fidelity loss is decisive for this maintained surface.

**Page-context capability: not measured; adoption not advanced.** The upstream
detector failure validly stopped spend under the declared ladder, but it is not
semantic evidence about the materially different page-context task. The
maintained page-context validator remains unchanged. Do not rerun the same
detector prompt/reasoning variants; advance to page context only after a
materially revised Grok model or new visual-grounding evidence first clears the
detector prerequisite.

Official references:

- <https://x.ai/news/grok-4-5>
- <https://docs.x.ai/developers/grok-4-5>
- <https://docs.x.ai/developers/models/grok-4.5>
- <https://docs.x.ai/developers/model-capabilities/images/understanding>
- <https://docs.x.ai/developers/pricing>
