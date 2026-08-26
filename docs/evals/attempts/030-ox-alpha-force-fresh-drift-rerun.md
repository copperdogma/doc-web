# Attempt 030 — Ox Alpha force-fresh drift rerun

**Eval:** `image-crop-extraction`, conditionally `crop-validation` and
`crop-page-level-deletion-gate`
**Date:** 2026-08-25
**Worker Model:** Codex GPT-5
**Subject:** OpenRouter `stealth/ox-alpha`; resolved provider recorded from each
response

## Decision contract (recorded before inference)

- Objective: test whether exact Ox Alpha behavior has materially improved since
  Attempt 028 on 2026-08-22. This can measure behavioral drift on the frozen
  bounded fixtures; it cannot prove that the provider is learning live or
  identify the mechanism behind any change.
- Freshness: force-fresh candidate-only rerun with new result and raw-response
  identities, no cache, and concurrency `1`. Preserve Attempt 028 unchanged.
- Exact requested and served model: `stealth/ox-alpha`; no alternate-model
  fallback. Provider routing remains unpinned because endpoint identity is not
  decision-bearing, but the resolved provider must be recorded.
- Fixture policy: the generated and checked-in crop fixtures are public
  evaluation inputs. Cam previously approved this bounded route even if the
  anonymous provider retains or trains on them. Omit request-level ZDR and
  `data_collection=deny`; do not change account settings.
- Repeat the Attempt 028 transport/configuration shape: mandatory low
  reasoning, hidden reasoning output, `max_tokens=16384`, strict crop schema,
  and a strict `require_parameters=true` probe before the already-declared
  diagnostic arm that omits only router parameter enforcement and performs
  fence-only cleanup after protected raw retention.
- Frozen detector surface: Story 207's 13-case `image-crop-extraction` task,
  `conservative-count`, unchanged prompt, scorer, golden, fixtures, and
  diagnostic float crop contract. The task-file hash may differ because the
  current registry contains later provider entries; the filtered provider and
  all semantic/scoring hashes must remain identical to Attempt 028.
- Detector gate: `13/13`, overall `>= 0.95`, zero provider/schema errors. Only
  after it passes, run the independent 40-case `crop-validation` gate (`40/40`)
  and 22-case `crop-page-level-deletion-gate` (`22/22`) under their maintained
  prompts and scorers.
- This candidate-only rerun may compare Ox Alpha against its 2026-08-22 result
  (`13/13`, `0.915146`, `8538.85 ms` mean, `$0`) to assess drift. It does not
  support a contemporaneous superiority claim. If Ox Alpha clears the complete
  decision ladder and adoption could advance, rerun the relevant incumbent
  symmetrically before any superiority recommendation.
- Spend cap: US$0.75 including probes and diagnostics. Current endpoint pricing
  is zero; stop if live usage reports an unexpected charge or the cap could be
  exceeded.
- No private data, runtime/default change, prompt/scorer/golden change, commit,
  push, or deployment.

## Frozen provenance before inference

- Base HEAD: `1ee9f7a845c9e5a8e6e6229cfb08f48037d50faf`
- Detector task SHA-256 before adding the inline reproducible Ox Alpha provider
  entry: `5b848f87ed7b4ba9e58aebbeb5eb77cf8a3a694245400fcc9bf839fb92080f9d`
- Executed detector task SHA-256:
  `0dbac27f12ed7ab56f840676eb72cb8d79798d8e4e3a6a142da19b26bd8a0531`.
  The only change was the filtered Ox Alpha provider entry; prompt, fixtures,
  scorer, golden, and every non-Ox provider remained unchanged.
- Detector prompt source SHA-256:
  `bca281e0fbe547e3f3ef049b436d87c73ed7bb066e86f51145fb444b48211b64`
- Detector scorer SHA-256:
  `7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7`
- Detector golden SHA-256:
  `2ac0a8f01e00a252439da1f4827a85bc5118bf96460a3ff1780e642eafc60f90`
- Eval-only adapter SHA-256:
  `f93c72b566e4bdced8b7eef59cf4d6228dfd07d3771753f1d0308d63964bc2ab`
- Attempt 028 Ox Alpha diagnostic provider-fragment SHA-256:
  `40c737a8c38c8b46bb86c0f8a93f32732ece89091cf476f2954fc021f4394473`

## Results

**Do not adopt; the fresh candidate result regressed rather than improved.**
The strict `require_parameters=true` text contract still returned router HTTP
404 before inference. The same public-fixture diagnostic configuration then
reached exact `stealth/ox-alpha` on `Stealth` without parameter enforcement.
The one-case `Image000` smoke passed at `0.8851`. The full no-cache detector
completed with exact identity, terminal `stop`, valid usage, and protected raw
retention on all 13 calls, but passed only `12/13` at mean `0.880846`.

`Image001` returned `{"images": []}` and scored `0.075`. Manual inspection of
the source page and source-backed golden confirmed the stylized `ONWARD TO THE
UNKNOWN 1887 - 1987` title is the intended standalone artwork region, so this
is a model-wrong miss rather than a transport, parser, scorer, or golden error.
The failure is especially decision-bearing because Attempt 028 passed all 13
cases. The new mean is `0.034300` lower than Attempt 028's `0.915146`, and the
pass rate fell from `13/13` to `12/13`. Mean latency improved by `1290.93 ms`
(`15.12%`), from `8538.85 ms` to `7247.92 ms`, and the previous `38641 ms`
outlier did not recur, but that speed change does not offset the quality
regression or strict transport block.

The detector used `56,315` prompt plus `882` completion tokens (`57,197`
total, `7,040` cached), versus Attempt 028's `56,315` prompt plus `965`
completion (`57,280` total). OpenRouter reported `$0` for the smoke and full
candidate runs. A command-shape mistake before the filtered run attempted to
load the provider fragment as a second PromptFoo config, which PromptFoo
rejected and then began the task with its default provider matrix. It was
interrupted immediately; the exported partial record contains seven unrelated
single-case calls costing `$0.0073287` total. That operational mistake did not
enter the Ox Alpha score, remains below the `$0.75` repo cap, and is retained as
ignored diagnostic evidence rather than hidden.

| Stage | Result | Spend |
| --- | --- | ---: |
| Current public endpoint discovery | exact `stealth/ox-alpha`; one zero-priced `Stealth` endpoint; multimodal and `response_format` advertised | `$0.000000` |
| Strict text probe | router 404 with `require_parameters=true`; no inference | `$0.000000` |
| Invalid provider-fragment CLI attempt | no provider call; PromptFoo rejected the array fragment | `$0.000000` |
| Interrupted accidental default-matrix smoke | 7 unrelated single-case calls; excluded from candidate evidence | `$0.0073287` |
| Corrected Ox Alpha `Image000` smoke | exact model/provider, `1/1`, `0.8851`, `6137 ms` | `$0.000000` |
| Fresh 13-case Ox Alpha detector | exact model/provider, `12/13`, mean `0.880846`, `7247.92 ms` mean | `$0.000000` |
| 40-case crop-only validator | not run; detector gate failed | `$0.000000` |
| 22-case page-context gate | not run; detector gate failed | `$0.000000` |
| **Total known provider spend** | **candidate drift rerun plus retained accidental smoke** | **`$0.0073287`** |

Fresh candidate evidence:

- smoke eval/result: `eval-xea-2026-08-26T05:48:37`,
  `benchmarks/results/ox-alpha-diagnostic-image000-20260825-r1.json`, SHA-256
  `469f8f67dc98e2a2b927066e72bbd7763b19eb1e57ab04d39252673ac7f5a21c`
- smoke response: `gen-1787723319-vNR9jzDo0HXRb23hm2jH`, exact
  `stealth/ox-alpha` / `Stealth`, terminal `stop`, `4,254` tokens, protected
  raw SHA-256 `3ccb092db45ba33cb37ae965de5743ed2bacda70dbc11fe4df4942de9a39cf5b`
- full eval/result: `eval-dmr-2026-08-26T05:48:50`,
  `benchmarks/results/ox-alpha-diagnostic-image-crop-extraction-20260825.json`,
  SHA-256
  `d390de4b2b05527984822ab79ec930ad001e16e25616df11834565c9568cc12d`
- failed `Image001` response:
  `gen-1787723343-wwzK1GLDmVK9QDsJAHNw`, exact
  `stealth/ox-alpha` / `Stealth`, terminal `stop`, `4,350` tokens, `2767 ms`,
  protected raw SHA-256
  `4c3ebb622647036849c52cc87fdc3b16f4188d526f65b8fca277ba9701ac192b`
- all 14 candidate raw files (one smoke plus 13 full rows) are ignored JSON,
  mode `0600`; the PromptFoo results retain their safe paths and content hashes
- accidental partial eval/result: `eval-gHl-2026-08-26T05:47:27`,
  `benchmarks/results/accidental-unfiltered-smoke-20260825.json`, SHA-256
  `c95687fa0dd70ec55ab85a6e3eb116919715f4aa26e482672631c4ca4e2b1b92`

## Layered verdict

- Access: **available** — exact Ox Alpha returned terminal responses.
- Transport: **blocked for drop-in use** — strict parameter routing still has
  no eligible endpoint; the diagnostic requires client validation after
  relaxing provider enforcement.
- Reliability: **degraded for the decision surface** — transport completed
  `13/13`, but decision reliability fell to `12/13` scorer passes.
- Capability: **worse than its own 2026-08-22 result** — `0.880846` and
  `12/13`, versus `0.915146` and `13/13`. This refutes improvement on this
  frozen sample; it does not prove the provider stopped learning or reveal the
  cause of the change.
- Economics: **candidate calls remained `$0`**; mean latency improved to
  `7247.92 ms`. Total known repo-provider spend including the excluded
  accidental smoke was `$0.0073287`.
- Adoption: **do not adopt** for `image-crop-extraction`. The 40-case and
  22-case follow-ons remain not measured.

## Commands and validation

- Discovery: `python scripts/discover-models.py --check-new` plus the public
  OpenRouter endpoint projection.
- Strict probe: the generic provider via `scripts/run_with_doc_web_env.py` with
  exact model, low reasoning, integer crop schema, unpinned provider, omitted
  privacy filters, and `require_parameters=true`.
- Smoke/full: `cd benchmarks && ../scripts/run_with_doc_web_env.py promptfoo
  eval -c tasks/image-crop-extraction.yaml --filter-providers '^Ox Alpha
  diagnostic \\(low reasoning, client-validated crop JSON\\)$'
  --filter-prompts conservative-count --no-cache --output <new-result> -j 1`,
  with `--filter-first-n 1` on the smoke only.
- Registry and executed-task YAML parsing passed.
- Focused provider/crop-substrate tests: `27 passed`.
- Focused Ruff: passed.
- `make methodology-compile` and `make methodology-check`: passed.
- `git diff --check`: passed.
- Manual artifact review covered all per-row exact identities, finish reasons,
  usage/cost, scores, latency, raw pointers/hashes, and the source image plus
  golden for the failed `Image001` case.
