# Attempt 034 — GPT-6 Astra page-context safety gate

**Eval:** `crop-page-level-deletion-gate`
**Date:** 2026-09-05
**Worker Model:** GPT-6 Astra
**Subject Model / Surface:** first-party OpenAI Responses `gpt-6-astra`,
reasoning `medium`, maintained `page-context` prompt
**Mission:** Determine whether the detector-quality winner from Attempt 033 can
match the maintained GPT-5.5 Responses `22/22` page-context safety contract.

## Prior Evidence and Changed Gate

Attempt 033 qualified exact access, native strict image transport, and the
PromptFoo adapter, then measured all five reasoning levels on detector
calibration. `medium` was the bounded detector-quality leader at `0.980392` and
13/13. The original US$1.50 detector campaign did not have enough remaining
budget for the distinct two-image page-context surface. Cam separately approved
a fresh US$1.50 ceiling for this follow-on.

## Predeclared Decision Contract

- Candidate: exact first-party Responses `gpt-6-astra`, frozen `medium`
  reasoning, `store=false`, image detail `high`, API-enforced strict
  `page_context_validation` schema, no sampling controls.
- Maintained surface: unchanged
  `benchmarks/prompts/validate-page-level-crop.js`,
  `benchmarks/scorers/crop_validation_scorer.py`, and
  `benchmarks/golden/crop-page-level-deletion-gate.json`.
- Smoke/differentiator: `page-122-001`, the source-reviewed neighboring-
  portrait leakage case missed by multiple prior challengers.
- Progression: run the differentiator once with no cache and concurrency one.
  Require exact identity, terminal strict output, the correct `fail` verdict,
  valid usage/cost, and a conservative projection inside the remaining cap
  before launching all 22 cases.
- Full gate: exactly 22/22, zero provider/schema/parser errors. If Astra clears,
  run a fresh GPT-5.5 comparator only when the remaining cap can fund it; a
  retained 22/22 comparator can support bounded qualification but not a fresh
  superiority claim.
- Retry budget: one evidence-led transient retry or narrow adapter repair; no
  prompt, scorer, golden, or reasoning tuning after observing the result.
- Spend: separate US$1.50 hard ceiling, starting at US$0.00. Stop before a call
  whose conservative projection could cross it.
- Privacy: checked-in public source/crop fixtures only. `store=false` is not
  treated as ZDR proof.
- Not authorized: runtime/default changes, private payloads, provider-account
  changes, commit, push, deployment, or broader rollout.

## Plan

1. Validate the unchanged task, exact two-image topology, strict schema, and
   environment wrapper without inference.
2. Run `page-122-001` through the Astra provider as both the distinct-contract
   and harness-parity smoke.
3. Inspect the full raw result, source page, crop, usage, latency, and cost.
4. Apply the progressive budget/quality gate, then record the result in the
   registry, Story 232, changelog, and generated methodology surfaces.

## Work Log

20260905-0000 — follow-on contract frozen before provider spend. Separate cap
US$1.50; spend US$0.00; exact frozen Astra `medium`; public fixtures only; no
default, prompt, scorer, golden, commit, push, or deployment change authorized.

20260905-1027 — two zero-request launch checks made no provider call and spent
US$0.00: the first resolved the environment wrapper from the wrong working
directory; the second used PromptFoo's `--filter-pattern`, which selected zero
rows because this suite does not expose `crop_key` as a filterable case name.
The frozen `page-122-001` row was therefore copied verbatim into the dedicated
one-case task `benchmarks/tasks/gpt6-astra-page-context-page-122-001.yaml`.
Prompt, scorer, golden, provider, reasoning, and transport remained unchanged.

20260905-1028 — paid differentiator stopped the campaign on quality. The exact
served model was `gpt-6-astra` at `medium`; the response completed under the
strict page-context schema with `store=false`, `6353` prompt tokens, `58`
completion tokens, `8068 ms` latency, and US$0.066430 cost. Astra returned
`pass` and explicitly described “the two oval portraits”; the authoritative
golden requires `fail` because the intended Moise/Edward portrait crop includes
the neighboring Sophie L'Heureux portrait. The maintained scorer returned the
expected false-negative classification. Manual inspection of both source page
and crop confirmed the golden: the crop contains the entire adjacent Sophie
portrait, not merely harmless blank space. Quality failed before the spend
projection gate, so the remaining 21 cases, all retries, and a fresh GPT-5.5
comparator were not run. Final spend: US$0.066430 / US$1.50.

Frozen/current SHA-256 values:

- prompt: `2ccc8c96ef69c14102d7ffd13b5a39715e5cd136b497510b1b2f88243009a5a0`
- scorer: `12eb63725523bd00d59ce12b7486db8c9244124a0c57bb68cae8b8e9e7d288fb`
- golden: `4bcba8f4ab8a742608e7cfc1438464a71cf56aa4cd9cbe9e0a67e4a410ac18a5`
- provider: `f8b3b3f6b93c9ec4a0c0e20e496f8c2e2189179ec461bfac4cc0ac66dc643346`
- one-case task: `cc4f5a6dc922be47dfaefed29dc6d4f5f48aa7cf07f98643e15912abbff8ce4d`
- protected ignored raw result:
  `0a2e79becedbf812b4967d52e465f50e617e146422c25b9959c5f3cf9691aa71`

Reproduce from `benchmarks/` with the existing repo environment wrapper (the
wrapper supplies the already-authorized key without printing or persisting it):

```text
OPENAI_RESPONSES_MODEL=gpt-6-astra \
OPENAI_RESPONSES_EXPECTED_SERVED_MODEL=gpt-6-astra \
OPENAI_RESPONSES_REASONING_EFFORT=medium \
OPENAI_RESPONSES_OUTPUT_CONTRACT=page_context_validation \
OPENAI_RESPONSES_INPUT_PRICE_PER_1M=10 \
OPENAI_RESPONSES_CACHED_INPUT_PRICE_PER_1M=1 \
OPENAI_RESPONSES_OUTPUT_PRICE_PER_1M=50 \
PROMPTFOO_PYTHON=/Users/cam/Documents/Projects/doc-web/.venv/bin/python \
../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/gpt6-astra-page-context-page-122-001.yaml \
  --providers "python:$(pwd)/providers/openai_responses_model.py" \
  --no-cache \
  --output results/gpt6-astra-20260905/page-context-medium-page-122-001.json \
  --no-share -j 1
```

## Conclusion

**Result:** failed the predeclared safety differentiator; stop before full gate.

**Access and transport:** qualified. The exact requested model was served and
returned a terminal strict-schema response with attributable usage and cost.

**Reliability:** not established by this one-call stop gate. This request
completed without provider error or retry in `8068 ms`; Cam separately reported
availability trouble in another long-running Astra task, so broader service
reliability remains uncertain. That external signal does not explain or soften
this result because the evaluated response completed normally and made a
semantic false-negative judgment.

**Capability:** not safe enough for this adoption surface. The candidate made a
model-wrong false-negative judgment on the deliberately chosen neighboring-
portrait case. This is the same residue class the maintained gate exists to
catch, so a 22-case average cannot repair the failed `1.0` contract.

**Economics:** US$0.066430 spent, leaving US$1.433570 unspent. Cost was not the
stopping reason; the hard quality prerequisite failed.

**Adoption:** reject Astra `medium` as Doc Web's page-context validator and do
not promote the detector result into the crop runtime. GPT-5.5 Responses remains
the recorded `22/22` page-context provider and the current runtime/defaults stay
unchanged. No fresh incumbent claim is made because no comparator was needed.

**Retry condition:** only a materially revised Astra model or page-context
capability change should reopen this gate. Higher effort is not warranted from
this campaign: detector calibration already showed `high`, `xhigh`, and `max`
dominated, and the contract intentionally forbids score-driven effort tuning
after a decisive safety miss.

**Validation:** methodology compile/check, registry YAML parsing, lint, and 25
focused provider/crop-substrate/runtime-contract tests passed. A broader
unrelated repo suite reached 352 passing tests before manual interruption after
10m42s in a slow subprocess-backed integration area; it reported no failure,
but is not claimed as a completed full-suite pass.

## Definition of Done

- [x] Read prior attempts and current owner contracts
- [x] Run no-cache at concurrency one
- [x] Record identity, strict transport, quality, latency, cost, and spend
- [x] Inspect the differentiating source/crop artifact
- [x] Update registry and owning story
- [x] Apply the progressive stop without hidden retries
- [x] Validate methodology and touched eval surfaces
