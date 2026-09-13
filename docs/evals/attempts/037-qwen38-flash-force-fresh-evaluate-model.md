# Attempt 037 — Qwen3.8 Flash force-fresh crop evaluation

**Date:** 2026-09-13
**Worker:** Codex owner agent
**Owner:** Stories 207 and 209; `spec:4`, C4/C5
**Base:** `bb3c6ffaaa9163a831635ffee5429be9debfcd01`
**Branch:** `codex/qwen38-flash-eval-20260913`
**Worktree:** `/Users/cam/.codex/worktrees/qwen38-flash-retry-20260913/doc-web`

## Pre-spend decision contract

Cam explicitly requested a force-fresh retry after the 2026-08-27 Qwen3.8
Flash evaluation stopped at provider capacity. The exact candidate is
OpenRouter `qwen/qwen3.8-flash`, canonical snapshot
`qwen/qwen3.8-flash-20260826`. The primary arm pins the non-quantization-stated
Alibaba endpoint without fallback; a Makora FP4 arm is predeclared only as a
transport alternative if Alibaba remains capacity-blocked. Provider arms are
reported separately and never silently pooled.

The decision surface is the frozen 13-case `image-crop-extraction` detector
with `conservative-count`, strict `crop_regions` JSON Schema, low reasoning
excluded from visible output, `max_tokens=16384`, checked-in owner-identified
public fixtures, force-fresh/no-cache execution, and concurrency one. Current
runtime remains Gemini 3 Flash; best bounded quality evidence is GPT-6 Astra
medium at `13/13`, `0.980392`, but it is production-unqualified. The candidate
must clear `13/13`, aggregate `>=0.95`, zero provider/schema errors, and remain
latency-competitive to advance. A minimal strict text access probe, generated
synthetic strict-image probe, same-case owner-adapter parity, and one
representative maintained case precede the full detector. Crop-safety
follow-ons are measured only after the detector passes its entry gate.

The maintained prompt, fixtures, scorer, goldens, runtime defaults, and
downstream cleanup are frozen. No implicit judge is used: detector assertions
are the deterministic maintained Python scorer plus manual source inspection.
No private data, Dossier work, default change, commit, push, merge, or deploy
is authorized. Total OpenRouter spend is capped at **US$0.75**, including all
probes, retries, both endpoint arms, and any conditional follow-ons. No
automatic retries are allowed; at most one evidence-led retry for a transient
capacity response and the predeclared Makora endpoint alternative may be used.

Provider truth checked 2026-09-13: OpenRouter currently lists both Alibaba and
Makora endpoints for the exact public route, with structured outputs,
`response_format`, image input, and reasoning controls. Alibaba advertises 1M
context, 131072 max completion, unknown quantization, 99.83% 30-minute uptime,
and prices of $0.15/M input, $0.47/M output, $0.016/M cache read, and $0.20/M
cache write. Makora advertises 262144 context, the same uncached input/output
prices, FP4 quantization, and 99.11% 30-minute uptime. Endpoint listing is
zero-cost catalog evidence, not callability proof.

## Result

The initial normalized-coordinate arm qualified minimal text, generated strict
image, owner-adapter parity, and a representative `Image011` call. The first
full detector exposed a transport/configuration mismatch rather than a valid
semantic matrix: eight rows were rejected locally because seven returned
0-1000-style coordinates despite the API-enforced 0-1 numeric bounds, and one
returned an extra root field. The raw envelopes were retained before parsing.
One request also received a zero-cost capacity-coded 429 and PromptFoo retried
that row once, an observed reliability/retry deviation retained in the ledger.

The single evidence-led transport repair is to use the maintained prompt's
existing integer-coordinate branch with the adapter's existing strict
`crop_regions_integer` schema. This changes representation only, not crop
semantics, fixtures, scorer, or golden. It is a declared corrected arm and must
requalify native strict image and owner-adapter parity before scoring.

Alibaba passed that corrected arm's native and parity qualification, but the
first maintained representative request then returned two consecutive
capacity-coded 429s. PromptFoo's Python-provider retry behavior attempted the
second request automatically; the owner agent interrupted the command before a
third retry to preserve the declared retry bound. The already-predeclared
Makora FP4 route therefore becomes the corrected-arm transport alternative and
must qualify independently before any maintained scoring.

## Final decision

**Defer Qwen3.8 Flash for doc-web's crop detector.** The model is now genuinely
callable, unlike the August 27 capacity stop, but this pass still did not
produce a decision-grade frozen 13-case matrix. The initial normalized arm was
contract-invalid on eight cases. The corrected integer arm qualified on
synthetic image transport but could not complete one maintained representative
case on either current endpoint because shared-pool capacity failures exhausted
the declared retry bound. Full crop capability and all crop-safety follow-ons
remain **not measured** under the valid corrected contract.

### Observed evidence by arm

| Arm/stage | Result | Latency | Cost |
| --- | --- | ---: | ---: |
| Alibaba normalized strict text | Exact model/provider, terminal stop, strict empty `images` | 21618 ms | $0.00045681 |
| Alibaba normalized synthetic native | Exact model/provider, terminal stop, valid square bbox | 2865 ms | $0.00009885 |
| Alibaba normalized synthetic owner parity | Exact model/provider, strict local validation | 6711 ms | $0.00020648 |
| Alibaba normalized `Image011` representative | Pass, score 0.9652 | 12032 ms provider | $0.00085404 |
| Alibaba normalized full13 | 4 pass, 1 semantic fail, 8 contract errors; one 429 plus automatic retry | 16473 ms mean end-to-end | $0.008891718 |
| Alibaba integer synthetic native | Strict integer bbox qualified | 6565 ms | $0.00021835 |
| Alibaba integer synthetic owner parity | Strict integer bbox qualified | 7089 ms | $0.00012623 |
| Alibaba integer `Image011` representative | Two capacity 429s; interrupted before a third retry | 1568/5971 ms | $0 |
| Makora FP4 integer synthetic native | One capacity 429; no transport qualification | 430 ms | $0 |
| **Campaign total** | **23 network calls: 19 HTTP 200, 4 capacity 429** | | **$0.010852478 / $0.75** |

The normalized full run's five contract-valid rows are conditional diagnostic
evidence only: `4/5` passed with mean `0.91334`. They cannot be promoted to a
13-case score. Image011 also varied materially: the first representative
combined seal and signatures and passed at `0.9652`, while the fresh full-run
response omitted the signatures and scored `0.6393`. The maintained prompt and
source-backed golden explicitly require adjacent signatures and seal to be one
combined image, so that valid-row miss is **prompt/pipeline-wrong →
model-wrong**, not golden/scorer wrong. It is conditional semantic evidence,
not a complete capability verdict.

### Layered verdict

- **Access:** available for exact `qwen/qwen3.8-flash` on Alibaba; Makora exact
  route is catalog-visible but its one live call was capacity-blocked.
- **Transport:** normalized strict output is blocked for the maintained surface
  because server-side schema enforcement did not hold numeric bounds/root
  shape. The integer repair qualified synthetically on Alibaba but maintained
  parity/scoring remained incomplete. Makora integer transport is unqualified.
- **Reliability:** degraded. Alibaba produced 19 HTTP 200s and three capacity
  429s; Makora produced zero successes and one capacity 429. The normalized
  matrix achieved only five locally contract-valid final rows out of 13.
- **Capability:** not measured decision-grade. Conditional valid-row quality is
  `4/5`, mean `0.91334`, with one source-backed grouping miss and strong
  run-to-run Image011 variance.
- **Economics:** inexpensive at $0.010852478 total, but normalized full-run
  end-to-end latency averaged 16473 ms (median 10165 ms, maximum 72205 ms with
  capacity retry), which is not competitive with the fresh Gemini control's
  recorded 6236 ms mean.
- **Adoption:** defer. No detector/default change, contemporaneous superiority
  claim, or crop-safety advancement is supported.

## Evidence and reproducibility

Tracked manifest `docs/evals/evidence/037-qwen38-flash-manifest.json` records
the exact base, branch, commands, code/task/prompt/scorer/golden hashes, spend,
and protected ignored raw bundle digest. The ignored
`benchmarks/results/qwen38-flash-20260913/` directory retains every complete
public/synthetic request and response envelope before parsing, plus PromptFoo
results, catalog snapshot, preflight, probes, and ledger. No authorization
headers or credential values are retained.

The existing `benchmarks/.gitignore` ignored only top-level `results/*.json`,
not JSON inside the campaign subdirectories already used by recent evaluation
evidence. This pass added the general recursive `results/**/*.json` rule after
inference and verified the Attempt 037 raw bundle is ignored. That evidence-
hygiene change did not affect any provider request or score.

Retry only after the exact endpoints sustain strict integer-image calls long
enough to complete a representative case and full13 without capacity churn.
The retry must use a fresh artifact identity and must not reuse this attempt's
subject outputs as fresh evidence.
