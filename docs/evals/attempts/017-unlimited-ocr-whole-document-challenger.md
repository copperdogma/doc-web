# Unlimited-OCR Whole-Document Challenger

Date: 2026-07-20
Repo HEAD at measurement: `ac574bf` (Story 230 files uncommitted)

## Trigger and decision gate

Scout 016 found Baidu Unlimited-OCR credible enough to test because its
Reference Sliding Window Attention and one-shot multi-page mode directly target
cross-page OCR continuity. Cam approved a bounded benchmark with a stricter
project-value rule: a tiny or isolated improvement does not justify operating a
second OCR model.

The precommitted adoption gate required either:

- meaningful, routeable wins on at least two independent Onward cases with at
  least `+0.01` mean gain or an exact-pass conversion and no material page loss;
  or
- both corrected real handwriting fixtures at `overall_min_ratio >= 0.99`,
  `page_min_ratio >= 0.99`, and `pass_rate = 1.0`.

## Runtime and parity proof

The benchmark used the exact official weight object with a narrowly reviewed
community device/dtype patch, not a GGUF, MLX, or quantized conversion:

- official model revision:
  `ee63731b6461c8afcdcc7b15352e7d2ffecc2ead`
- community Universal code revision:
  `bc00ae36def7fe8d23980adf5a901125fe0040a2`
- official Space revision:
  `fece8f832e1c8691b375da69f810191c67840a3d`
- safetensors SHA-256:
  `2bc48a7a110061ea58fff65d3169367eebe3aee371ca6968dc2219c1b2855fc6`
- weight size: `6,672,547,120` bytes; license: MIT
- local runtime: native arm64 Python `3.12.9`, Torch `2.10.0`, Transformers
  `4.57.1`, exact-weight FP32 CPU on the M4 Pro Mac
- prompts: `<image>document parsing.` and `<image>Multi page parsing.`;
  deterministic temperature `0.0`, `max_length = 32768`, no-repeat n-gram
  size `35`, and windows `128` single-page / `1024` multi-page

MPS execution outside the sandbox was not used because it would execute
third-party custom model code beyond the approved trust boundary. The exact
weights were practical on CPU inside the sandbox. On Unlimited-OCR's public
sample, the official Baidu BF16 Space result and local exact-weight FP32 result
matched exactly after removing only the official UI's grounding metadata:
`2,263` characters, sequence ratio `1.0`. No repo-owned source image was
uploaded to the public Space.

Runtime and parity artifacts:

- `output/runs/story230-unlimited-ocr-benchmark-r1/local-cpu/runtime.json`
- `output/runs/story230-unlimited-ocr-benchmark-r1/official-space/public-sample-gundam/`
- `output/runs/story230-unlimited-ocr-benchmark-r1/local-cpu/public-sample-gundam/`
- `output/runs/story230-unlimited-ocr-benchmark-r1/parity-public-sample-gundam-clean.json`

Command shapes:

```bash
python scripts/spikes/unlimited_ocr_benchmark.py run-space \
  --image /path/to/explicitly-public-sample.png --source-page 1 \
  --mode gundam --allow-public-upload --out-dir /path/to/official-control
python scripts/spikes/unlimited_ocr_benchmark.py run-local-single \
  --model-dir /path/to/pinned-checkout --image /path/to/public-sample.png \
  --source-page 1 --mode gundam --device cpu --out-dir /path/to/local-control
python scripts/spikes/unlimited_ocr_benchmark.py compare-parity \
  --reference /path/to/official-control/raw.txt \
  --candidate /path/to/local-control/clean.md --out /path/to/parity.json
python scripts/spikes/unlimited_ocr_benchmark.py run-local \
  --model-dir /path/to/pinned-checkout --device cpu \
  --out-root output/runs/story230-unlimited-ocr-benchmark-r1/local-cpu
```

## Onward result

All three candidate modes used the same local source rasters. Whole-case scores
used the independently reviewed Onward goldens; Story 134 per-page references
were diagnostic only.

| Case | Historical applied incumbent | Single Gundam | Single Base | Multi Base | Best candidate | Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Alma | `0.9230` | `0.5821` | **`0.6797`** | `0.3871` | `0.6797` | `-0.2433` |
| Arthur | `0.9890` | **`0.5384`** | `0.4401` | `0.2403`* | `0.5384` | `-0.4506` |
| Marie-Louise | `0.9950` | `0.5460` | **`0.5966`** | `0.5882` | `0.5966` | `-0.3984` |

`*` Arthur multi-page also hard-failed transport by emitting seven `<PAGE>`
segments for six source images.

Best-of-candidate aggregation:

- candidate mean: `0.6049`
- historical applied incumbent mean: `0.9690`
- aggregate delta: `-0.3641`
- meaningful wins: `0/3`
- oracle-hybrid score: `0.9690`
- candidate selection share: `0.0`
- average wall time for the three selected candidate arms: about `168.1 s`
  per case on CPU, excluding model load

Manual scan/output review confirmed the low scores are substantive. Examples
include collapsed `BOY/GIRL` columns and family headings, `George` becoming
`Eorge`, and Arthur multi-page degenerating into duplicated/repeated table
text. These are model-output or runtime-transport failures, not scorer quirks.

Primary artifacts:

- `output/runs/story230-unlimited-ocr-benchmark-r1/local-cpu/onward_results.json`
- `output/runs/story230-unlimited-ocr-benchmark-r1/local-cpu/decision.json`
- per-arm `raw.txt`, `parsed.json`, `transport.json`, `runtime.json`,
  `clean.md`, `normalized.html`, `pages_html.jsonl`, `score.json`, and
  `result.json` under
  `output/runs/story230-unlimited-ocr-benchmark-r1/local-cpu/onward/`

## Handwriting screen

The bounded exact-weight Gundam-mode screen also missed the corrected real
fixture gate decisively:

| Fixture | Overall ratio | Page-min ratio | Pass rate | Main failure |
| --- | ---: | ---: | ---: | --- |
| Barney | `0.200382` | `0.200382` | `0.0` | substantial omissions and substitutions |
| Alverson | `0.022946` | `0.022946` | `0.0` | hallucinated math/repeated text; `21,029` normalized chars for an `848`-char truth; runaway generation near the total cap, with truncation indeterminate because the helper omitted input length and stop reason |

Story 191 therefore remains blocked. Artifacts are under
`output/runs/story230-unlimited-ocr-benchmark-r1/local-cpu/handwriting/`, with
the aggregate in `handwriting_results.json`.

## Mismatch classification

- **Model/runtime-wrong:** every material scored deviation. Eight Onward arms
  preserved page-count transport but remained far below their goldens; Arthur
  multi-page additionally failed transport. Both handwriting outputs are
  visibly wrong against the checked-in scans/transcripts.
- **Golden/scorer-wrong:** none. The whole-case Onward goldens were already
  independently reviewed, representative pages and both handwriting images
  were reopened against the candidate outputs, and no scorer/golden edit was
  needed.
- **Ambiguous:** minor pale/handwritten glyph readings exist, but none is large
  enough to affect a delta of `-0.2433` to `-0.4506` or either handwriting
  blocker result.

## Decision

**Do not adopt Unlimited-OCR and do not add a second-model router.** Keep the
current OCR approach on every tested surface. Unlimited-OCR lost all three
independent Onward cases by large margins, its one-shot mode caused a hard
page-duplication failure on Arthur, and it did not approach the handwriting
unblock threshold. Even a zero-cost local call would not compensate for this
quality loss, the `6.67 GB` model footprint, custom-code/runtime burden, long
CPU latency, missing confidence signal, and additional operational seam.

No maintained module, recipe, router, scorer, or golden changed. An official
CUDA rerun is not warranted because the local exact-weight runtime matched the
official BF16 control exactly and the decision margins are not close. Retry
only after a materially new Unlimited-OCR checkpoint/runtime supplies evidence
that could plausibly reverse these margins.
