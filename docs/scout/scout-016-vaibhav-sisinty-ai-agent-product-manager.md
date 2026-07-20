# Scout 016 — Baidu Unlimited-OCR from Vaibhav Sisinty's post

**Source:** `https://x.com/vaibhavsisinty/status/2079000862962417996`
**Primary sources:** [paper](https://arxiv.org/abs/2606.23050),
[model card](https://huggingface.co/baidu/Unlimited-OCR),
[official repository](https://github.com/baidu/Unlimited-OCR), and
[vLLM recipe](https://recipes.vllm.ai/baidu/Unlimited-OCR)
**Scouted:** 2026-07-20
**Scope:** Fact-check the social-post claims, determine whether whole-document
OCR moves doc-forge toward the Ideal, and define the smallest honest adoption
gate against the maintained genealogy/table and handwritten OCR surfaces.
**Previous:** Scout 014 (degraded handwriting sources); Story 208 (GLM-OCR
challenger pattern and negative evidence)
**Status:** Complete

## Summary

Unlimited-OCR is a real, unusually relevant OCR challenger, but the post turns
several qualified research results into broader product claims. Baidu's
3-billion-parameter / 500-million-active-parameter model uses Reference Sliding
Window Attention so every generated token can attend to all visual tokens while
only a bounded window of prior output remains in the decode-side cache. This is
a concrete attempt to preserve reading order and repeated structure across a
multi-page document instead of OCRing isolated pages.

The reported quality is strong enough to justify a bounded benchmark, not
adoption. The paper reports `93.23` on OmniDocBench v1.5, versus `87.01` for its
DeepSeek-OCR baseline, and `93.92` on v1.6. Its separate long-document test stays
at `0.1069` normalized edit distance for the `40+`-page bucket. However, that
long-document set is in-house, the multi-page training data was made by
concatenating single-page samples, and the current model is bounded by a 32K
prefill context. "Unlimited" is therefore an architectural direction, not the
current page limit.

The post's "runs 100% locally on your machine" claim is incomplete for this
repo's current M4 Pro Mac. Baidu's documented Python path calls CUDA directly,
and the official vLLM path requires an NVIDIA GPU with at least 8 GB VRAM.
Community Ollama, GGUF, and MLX ports may provide a Mac preflight, but their
quantization and runtime differ from Baidu's published BF16 evidence and cannot
settle adoption by themselves.

**Recommendation:** evaluate, do not adopt. Run one bounded official-BF16
challenger on the existing Onward multi-page goldens, preserve the model's raw
page and grounding tokens for provenance, and use handwriting only as a
separate opportunistic screen. Do not reopen Story 191 unless the candidate
actually clears its existing handwriting gate.

## Result

Cam approved the bounded benchmark with the added rule that a tiny or isolated
win could not justify two OCR models. Story 230 executed the raw-token harness,
single-versus-multi kill gate, all three independently reviewed Onward cases,
and the corrected Barney/Alverson screen.

**Final decision: do not adopt Unlimited-OCR.** Its best transport-valid arm
averaged `0.6049` versus the historical applied Onward record of `0.969`
(`0/3` meaningful wins, oracle-hybrid `0.969`, selection share `0.0`).
Multi-page mode lost to the best single-page arm on every case and emitted seven
page segments for six Arthur inputs. Barney scored `0.200382`; Alverson scored
`0.022946` and ran away near the configured token cap. The exact-weight local
FP32 runtime matched Baidu's official BF16 Space exactly on Baidu's public
sample, so the large local deficits were not close enough to warrant paid CUDA
confirmation. Keep the current OCR path everywhere, do not add a router, and
keep Story 191 blocked.

Portable result: `docs/evals/attempts/017-unlimited-ocr-whole-document-challenger.md`.

## Findings

1. **Benchmark whole-document OCR on the existing Onward truth surface** — HIGH value, story-sized (L)
   What: Unlimited-OCR can ingest multiple page images in one request and emit
   ordered Markdown separated by `<PAGE>` markers. Its attention design targets
   exactly the cross-page context and long-output memory problem described in
   the post.
   Us: `benchmarks/tasks/onward-table-fidelity.yaml` already provides three
   independently reviewed multi-page cases plus Story 134 per-page diagnostic
   references derived from the Gemini 3.1 Pro incumbent. Marie-Louise pages
   `079`–`083` are also the scanned-table seam used by Story 208, while the
   current applied model records `0.969` aggregate structure preservation and
   the current score leader records `0.9714`. ADR-001 already prefers
   source-aware, document-wide understanding over post-hoc HTML repair. This is
   a materially different OCR substrate worth measuring against `spec:2` and
   `spec:3`, not a reason to change the runtime on paper evidence alone.
   Recommendation: Create one bounded benchmark story after approval. Run
   Baidu's official BF16 model on an NVIDIA GPU, starting with Marie-Louise
   `079`–`083`, then Alma and Arthur only if transport and the first quality
   gate pass. Compare the multi-page result both to the whole-case golden and
   to each page golden; manually inspect all emitted artifacts.
   Transfusion:
   Exemplar: R-SWA retains full access to the visual reference while bounding
   decode-side output history, allowing one generation to cover many pages.
   Invariant: Cross-page context may improve table continuity only if every
   source page and cell remains faithfully recoverable.
   Adaptation: Keep doc-forge's reviewed whole-case goldens, diagnostic
   page-level comparisons, and provenance gates around the whole-document call
   instead of accepting one aggregate Markdown score.
   Proof target: Multi-page mode avoids source-confirmed page-level regression,
   improves or preserves the independently reviewed whole-case structure,
   emits no missing/duplicated/reordered pages, and is manually verified
   against the scans.

2. **Capture raw page and grounding tokens instead of accepting clean Markdown** — HIGH value, inline within the benchmark story (M)
   What: The raw model output includes `<PAGE>`, `<|ref|>`, and `<|det|>` tokens
   that carry page separation, recognized regions, and normalized coordinates.
   Baidu's convenience writer removes most grounding tokens when it creates
   `result.md` and separately renders box-overlay images. No confidence score is
   exposed by the documented output.
   Us: Traceability is the product. A clean Markdown file without stable page
   mapping, source coordinates, processing metadata, and explicit uncertainty
   cannot replace the current artifact contracts. The useful source pattern is
   the raw grounded output, not the lossy convenience file.
   Recommendation: Adopt only inside the benchmark harness. Preserve the raw
   response verbatim, parse `<PAGE>` boundaries, retain grounding coordinates,
   and emit an inspectable comparison artifact. Treat the missing confidence
   signal as an adoption gap; do not invent confidence from model coordinates.
   Transfusion:
   Exemplar: Baidu keeps structured reference text and detection coordinates in
   special tokens before rendering clean Markdown.
   Invariant: Every extracted unit remains traceable to its source page and
   region even when downstream output is cleaned for readers.
   Adaptation: Map the tokens into a benchmark-local provenance sidecar before
   considering any `page_html_v1` or bundle integration.
   Proof target: A reviewer can select a model-output block and identify its
   original page, coordinates, raw response, runtime, and model configuration.

3. **Make single-page versus multi-page parity a kill gate** — HIGH value, inline within the benchmark story (S)
   What: Multi-page mode compresses each `1024x1024` page to 256 visual tokens
   and does not support the crop mode used for higher-resolution single-page
   reading. The paper itself attributes long-document errors mainly to small
   text under this base-resolution path.
   Us: Dense genealogy pages contain exactly the small text and repeated tables
   most likely to expose that tradeoff. An aggregate cross-page improvement can
   hide lost names, dates, notes, or rows. The existing per-page Onward goldens
   make this failure measurable without adding a new truth surface.
   Recommendation: Require both modes in the first benchmark. Stop if
   multi-page mode silently omits content, reorders pages, or scores below
   single-page mode/current incumbents on any page without a larger,
   manually-confirmed document-level benefit. Record latency, peak VRAM, token
   usage, and output length alongside quality.

4. **Use a community M4 runtime only as a transport preflight** — MEDIUM value, optional inline step (S)
   What: Community Ollama, GGUF, and MLX conversions make a local Apple-Silicon
   experiment plausible, and the model weights fit within this Mac's 48 GB of
   unified memory.
   Us: The official code and published benchmark are CUDA/BF16. A community
   quantization can cheaply answer whether prompts, special tokens, page
   splitting, and artifact parsing work locally, but it cannot distinguish a
   model-quality failure from a port, quantization, or runtime mismatch.
   Recommendation: Use only if it reduces setup risk before the official run.
   Never use the community result as positive adoption evidence or as the sole
   reason to reject the official model.

5. **Do not reopen the handwritten blocker or replace maintained OCR yet** — LOW value now; skip
   What: The social post says multilingual OCR, but neither the paper nor model
   card establishes historical handwriting quality. The training description
   centers on document OCR data, with single pages annotated by PaddleOCR and
   synthetic multi-page concatenation.
   Us: Story 191 has a precise unblock condition on the corrected Barney and
   Alverson LOC fixtures: `overall_min_ratio >= 0.99`, `page_min_ratio >= 0.99`,
   and `pass_rate = 1.0` through fresh pipeline/eval artifacts. Story 208 showed
   why a new OCR model must be tested rather than trusted from launch claims.
   Recommendation: Keep Story 191 blocked. The benchmark may run Barney and
   Alverson after the Onward transport gate as a low-cost screen, but only a
   pass on the existing corpus can justify reopening that story. Do not wire
   Unlimited-OCR into maintained recipes during the benchmark.

6. **Treat the launch metrics as directional, not adoption evidence** — MEDIUM value, research-only
   What: At scout time the official project showed about 14.8K GitHub stars and
   the model card showed roughly 2.12M Hugging Face downloads in the prior
   month, so the post's popularity figures were approximately current. The
   "93% accuracy" line compresses benchmark-specific metrics, and the
   "below 0.11 past 40 pages" line refers to the paper's small in-house
   `40+`-page bucket rather than a public broad-document benchmark.
   Us: Eval-before-build requires primary-source and local-artifact evidence.
   Popularity supports ecosystem interest, not fidelity, provenance, runtime
   compatibility, or total cost for doc-forge.
   Recommendation: Record the model as a credible challenger, but make the
   local goldens and artifact inspection decisive.

## Proposed Benchmark Gate

1. Pin the official commit, BF16 weights, vLLM release image, exact prompts,
   special-token handling, no-repeat logits processor, and attention window.
2. Run a transport fixture first and reject empty/truncated output, missing page
   markers, or special-token stripping.
3. Run Marie-Louise pages `079`–`083` in single-page and multi-page modes.
4. Score the joined result against the independently reviewed
   `benchmarks/golden/onward/marie_louise.html`; use
   `benchmarks/golden/onward/per_page/` for diagnostics and source-check any
   page-level comparison used in the decision.
5. Continue to Alma and Arthur only if the first case shows no page-level
   regression or silent loss. Run Barney/Alverson only as a separate screen.
6. End with one explicit decision: reject, keep as an escalation candidate, or
   create a maintained-runtime integration story. Do not combine benchmarking
   and runtime adoption in the same story.

## Approved

- [x] 1. Official-BF16-controlled Onward benchmark story — executed as Story 230
- [x] 2. Raw-token provenance adapter inside that benchmark — executed
- [x] 3. Single-page versus multi-page kill gate — executed
- [x] 4. Optional community M4 transport preflight — approved, then superseded by the safer exact-weight FP32 CPU path inside the sandbox

## Skipped / Rejected

- Immediate maintained-runtime adoption — rejected because the published
  evidence does not prove local fidelity, provenance completeness, or M4
  compatibility.
- Reopening Story 191 from multilingual/document-OCR claims — rejected because
  no historical-handwriting result clears the repo's existing blocker gate.
- Treating popularity, OmniDocBench, or the in-house `40+`-page result as a
  substitute for the Onward and handwritten goldens — rejected by the repo's
  eval-before-build and artifact-inspection requirements.
- Maintained runtime/module/recipe/router adoption — rejected by Story 230's
  measured breadth-and-complexity gate.

## Verification

- Opened the exact X status in a live browser and checked its linked official
  Hugging Face source rather than relying on search snippets or reposts.
- Reviewed Baidu's paper, model card, repository, model implementation, and
  official vLLM recipe, including runtime requirements, multi-page code,
  special tokens, model size, training construction, benchmarks, and stated
  limitations.
- Verified the current machine is Apple Silicon (`arm64`, M4 Pro, 48 GB) and
  that Baidu's official Python path explicitly uses CUDA. Story 230 subsequently
  ran the exact weight object on FP32 CPU inside the sandbox and verified exact
  cleaned-output parity against Baidu's official BF16 Space on a public sample;
  no repo-owned source was uploaded and no paid GPU was launched.
- Compared the candidate with `docs/ideal.md`, `docs/spec.md` (`spec:2`,
  `spec:3`), `docs/methodology/state.yaml`, ADR-001,
  `docs/runbooks/document-consistency-planning.md`, Stories 191 and 208, and the
  `ocr-model-genealogy`, `handwritten-notes-transcription`, and
  `onward-table-fidelity` eval entries.
- Verified the existing Onward benchmark owns independently reviewed
  whole-case goldens plus Story 134 incumbent-derived per-page diagnostic
  references for Alma, Arthur, and Marie-Louise, including pages `079`–`083`.
- Story 230 added only a story-local benchmark harness, tests, artifacts, and
  eval/methodology records. No maintained OCR runtime changed and no pipeline
  improvement is claimed.

## Evidence

- Baidu paper: `https://arxiv.org/abs/2606.23050`
- Official model and usage: `https://huggingface.co/baidu/Unlimited-OCR`
- Official code: `https://github.com/baidu/Unlimited-OCR`
- Official vLLM recipe: `https://recipes.vllm.ai/baidu/Unlimited-OCR`
- Local multi-page task: `benchmarks/tasks/onward-table-fidelity.yaml`
- Local whole-case goldens: `benchmarks/golden/onward/alma.html`,
  `benchmarks/golden/onward/arthur.html`, and
  `benchmarks/golden/onward/marie_louise.html`
- Local page goldens: `benchmarks/golden/onward/per_page/`
- Current decision boundaries: Stories 191 and 208; ADR-001; eval registry
  entries `handwritten-notes-transcription` and `onward-table-fidelity`
- Verified benchmark decision:
  `docs/evals/attempts/017-unlimited-ocr-whole-document-challenger.md`
