---
title: "Authoritative golden model reevaluation"
status: "Done"
priority: "High"
ideal_refs: ["Traceability", "AI-First", "Fidelity to Source"]
spec_refs: ["spec:4", "spec:8", "C4", "C5"]
adr_refs: []
depends_on: ["207", "209"]
category_refs: ["spec:4", "spec:8"]
compromise_refs: ["C4", "C5"]
input_coverage_refs: []
architecture_domains: ["crop-evaluation"]
roadmap_tags: ["model-refresh", "sota"]
legacy_system: ""
---

# Story 232 — Authoritative Golden Model Reevaluation

**Priority**: High
**Status**: Done
**Decision Refs**: Eval README, crop workflow/runbook, Stories 207/209, Attempt 026; no ADR change is required.
**Depends On**: Stories 207 and 209

## Goal

Restore the hand-authored crop goldens as the complete authoritative model-selection truth surface, remove the unnecessary requirement for a separate 12-case held-out set, and use current retained evidence plus only warranted fresh parity calls to identify the best eligible detector and crop validator.

## Eval Ladder Context

- **Root / parent**: `image-crop-extraction` followed by `crop-validation` and the `crop-page-level-deletion-gate`.
- **Latest evidence**: Gemini 3.7 clears detector 13/13 but fails `page-126-000` on crop validation; GPT-5.5 Responses remains the recorded 22/22 page-context provider; GPT-5.6 Terra slightly exceeds the historical detector score but misses page-context perfection.
- **Measured failure**: Attempt 026 incorrectly treated the human-created authoritative goldens as tuning-only evidence and invented an additional held-out requirement.
- **Current child work**: remove that policy without changing labels/scorers/goldens, regrade retained exact outputs, and run fresh candidate/incumbent calls only when current artifacts cannot answer the SOTA question.

## Acceptance Criteria

- [x] Current docs, registry, provenance, regrader, and tests state that the existing hand-authored goldens are authoritative and no 12-case held-out prerequisite exists.
- [x] Regrading remains fail-closed for malformed, duplicate, missing, extra, or mislabeled result rows and preserves `page-126-000` as a valid safety failure.
- [x] A frozen rerun matrix identifies reusable current evidence versus fresh-call candidates and records quality, latency, cost, exact identity, and provenance.
- [x] Any paid comparison reruns candidate and incumbent symmetrically on unchanged prompts/scorers/goldens under the USD 5 cap.
- [x] Name the highest valid comparable score as the measured quality leader even if it misses the absolute target; separately require hard safety/schema/runtime gates for production promotion.
- [x] No runtime/default change, commit, push, or Dossier work occurs implicitly.
- [x] After explicit promotion approval, require exact production-recipe parity
      and source/crop inspection before changing the maintained detector.

## Out of Scope

- Creating another book/crop corpus now, changing any human labels, weakening the 1.0 crop-safety targets, or deleting C5 solely from model ranking.
- Handwriting/table OCR reruns: current Gemini 3.7 evidence is already current and below the fixed bars.

## Approach Evaluation

- **Simplification baseline**: retained exact outputs can be regraded for free because the goldens/scorers are unchanged.
- **AI-only**: new provider calls are needed only for a stale or absent candidate/incumbent comparison.
- **Hybrid**: deterministic exact-label scoring plus human-authored source truth; no LLM judge is necessary for binary crop verdicts.
- **Pure code**: remove the mistaken selection-partition policy and preserve strict evidence validation.
- **Existing patterns to reuse**: current Promptfoo tasks, source/crop fixture hashes, `regrade_crop_result.py`, and provider-env wrapper.
- **Eval**: the existing 13-case detector, 40-case crop-only validation, and 22-case page-context validation.

## Frozen Decision Matrix

| Surface | Candidate | Comparator | Decision |
|---|---|---|---|
| Detector | GPT-5.6 Terra, reasoning none | configured Gemini 3 Flash | Retained rows are close (0.9723 vs 0.9703) but not fresh parity; run both 13-case tasks once after policy repair because Terra could become the measured leader. |
| Crop-only validator | Gemini 3.7 Flash | configured Gemini 3.1 Flash Lite | The retained Gemini 3.7 raw artifact is absent, so rerun both models symmetrically on all 40 authoritative goldens; rank by exact score while retaining 40/40 as the production-promotion gate. |
| Page-context validator | GPT-5.6 Terra | configured GPT-5.5 Responses promptfix | No fresh Terra call: retained Terra is 21/22 while the current provider is exact 22/22 on the same authoritative labels; it cannot become SOTA without a changed model/config trigger. |
| Handwriting | Gemini 3.7 Flash | Gemini 3.6 Flash | No rerun: both corrected-real results are current; 3.7 is lower and both miss 0.99. |

## Tasks

- [x] Replace held-out/calibration policy with one authoritative-golden provenance contract and adversarial tests.
- [x] Verify `page-126-000` visually/source-backed without changing its label and record that the prior raw result was not retained.
- [x] Freeze hashes and execute detector Terra/incumbent plus crop-only Gemini 3.7/incumbent parity.
- [x] Record the outcome in a new attempt, registry, story, changelog, and generated methodology surfaces.
- [x] Run focused tests, `make lint`, methodology checks, JSON/YAML validation, credential scan, and `git diff --check`; run broader tests proportionate to the final diff.
- [x] Verify Central Tenets and workflow gates.

## Workflow Gates

- [x] Build complete: implementation/evidence finished and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Blocker Summary

N/A

## Blocker Evidence

N/A

## Unblock Condition

N/A

## Architectural Fit

- **Owning area**: existing crop benchmark provenance/regrader and registry.
- **Methodology reality**: `spec:4` C4/C5; the hand-authored goldens are the source-of-truth fixtures.
- **Substrate evidence**: 13/40/22 tracked cases, source-page/crop assets, exact retained result artifacts, and adversarial regrader tests all exist.
- **Data contracts / schemas**: provenance metadata only; no runtime artifact schema changes.

## Files to Modify

- `benchmarks/golden/crop-eval-provenance.json`, `benchmarks/scripts/regrade_crop_result.py`, `tests/test_crop_benchmark_substrate.py` — authoritative-golden policy.
- `docs/evals/README.md`, `benchmarks/README.md`, `docs/evals/registry.yaml`, Attempt 026 evidence — remove the future-heldout prerequisite while preserving history.
- this story, a new attempt/evidence bundle, `CHANGELOG.md`, and generated methodology files.

## Redundancy / Removal Targets

- The 12-case held-out creation contract and selection-blocked status introduced on 2026-08-13.

## Plan

1. Remove the held-out prerequisite without changing human goldens or scorer semantics; validate retained exact outputs fail closed.
2. Reuse current decisive rows for crop validation, page context, and handwriting; buy only the fresh Terra/Gemini detector parity.
3. Inspect artifacts, update durable evidence, validate the full touched scope, and report SOTA/adoption separately.

The user approved this plan, the policy removal, and bounded paid calls on 2026-08-14.

## Work Log

20260814-0032 — campaign opened: live authenticated discovery confirmed all shortlisted provider IDs. Historical registry review found only the detector Terra/Gemini comparison lacks current symmetric parity; all other candidate decisions are already answered by unchanged authoritative goldens. No paid call has yet occurred. Next: remove the held-out policy and rerun focused integrity/regrade checks.

20260814-0145 — complete: the hand-authored goldens are again the complete authoritative decision surface. Fresh parity made GPT-5.6 Terra the detector quality leader at `13/13`, `0.9689`, and retained Gemini 3.1 Flash Lite as crop-only leader at `40/40`, `1.0`; Gemini 3.7 repeated its source-backed `page-126-000` safety miss. Retained page-context and handwriting evidence remained decisive. Attempt 029, registry history, provenance, changelog, and methodology record the outcome; conservative spend was `$0.29152`. No default changed.

20260825-0001 — close-out renumbering: upstream Ox Alpha work added Attempts 027–028 while this isolated branch awaited landing. Renumbered this unchanged retrospective evidence to Attempt 029 before integration; no score, artifact, or selection claim changed.

20260825-2030 — explicit promotion check complete: a mechanically parity-locked four-page Onward recipe ran GPT-5.6 Terra through the exact production crop route. Terra returned nine crops for `$0.045452`, but source/crop inspection found printed captions retained below both page-122 portraits, repeating Luna's hard C5 defect. Terra remains the measured detector-benchmark quality leader but is production-ineligible; `gemini-3-flash-preview` remains the runtime default. Story total subject spend is `$0.336972`.

20260904-0025 — GPT-6 Astra challenger contract recorded before inference: exact first-party Responses `gpt-6-astra`, low reasoning, strict crop schema, public checked-in fixtures, no cache, concurrency `1`, and a US$1.00 total ceiling. The progressive lane is native text/image qualification, one maintained parity case, then the frozen 13-case detector; the existing 22-case page-context gate may run only after `13/13`, aggregate `>= 0.95`, zero contract errors, and a safe remaining-budget projection. No fresh incumbent, private payload, default change, commit, push, or deploy is authorized. Evidence owner: `docs/evals/attempts/032-gpt6-astra-evaluate-model.md`.

20260904-0028 — GPT-6 Astra access result: owner-wrapped authenticated retrieval of exact `gpt-6-astra` returned HTTP `404 model_not_found`, consistent with OpenAI's staged-rollout warning. The ladder stopped before inference, fixtures, or spend. Access is blocked; transport, reliability, capability, latency, and semantic quality are not measured; adoption is deferred. The 13-case detector and 22-case page-context gate did not run, the maintained Gemini/GPT-5.5 evidence remains unchanged, and no task provider or default was added. Protected raw diagnostic SHA-256: `7bea5c03cb640d285e9921662c06aa9ce8bc2eb6f7e7e0535b1402d84cb96d3e`. Spend: `$0.00`. Evidence: `docs/evals/attempts/032-gpt6-astra-evaluate-model.md`.

20260905-0000 — GPT-6 Astra retry contract: exact authenticated retrieval now succeeds, satisfying Attempt 032's narrow retry trigger. Attempt 033 predeclares a public-fixture reasoning frontier across `low`, `medium`, `high`, `xhigh`, and `max` on the known-differentiating `Image001` case, with progressive transport, Pareto, full-detector, and conditional page-context gates under a US$1.50 hard ceiling. No prompt, scorer, golden, runtime default, private payload, commit, push, or deploy is authorized.

20260905-1012 — GPT-6 Astra detector result: exact retrieval plus native strict text/image and PromptFoo parity qualified. All five reasoning efforts passed the `Image001` calibration; `high`, `xhigh`, and `max` were dominated, while `low` and `medium` advanced. Fresh full runs passed `13/13` with zero errors: low `0.979562`, `3556 ms`, `$0.431904`; medium `0.980392`, `4134 ms`, `$0.434804`. Medium is the new bounded detector-quality leader, but manual source inspection still found model-wrong inset-cover undercoverage on `Image000`. Total spend was `$0.960878/$1.50`; the remaining `$0.539122` could not conservatively fund the 22-case page-context gate, whose full-page input floor alone projected to `$0.696740` before crop images or output. Page-context capability is not measured, production adoption is deferred, and the Gemini runtime default remains unchanged. Evidence: `docs/evals/attempts/033-gpt6-astra-reasoning-frontier.md`.

20260905-1100 — GPT-6 Astra page-context follow-on opened after separate user approval: Attempt 034 freezes the detector-winning `medium` configuration on the maintained two-image `crop-page-level-deletion-gate`, starts with the source-reviewed `page-122-001` neighboring-portrait differentiator, and permits the full 22-case gate only if the observed quality and projected spend fit a new US$1.50 ceiling. No provider spend yet; evidence: `docs/evals/attempts/034-gpt6-astra-page-context-gate.md`.

20260905-1115 — GPT-6 Astra page-context follow-on stopped at the first paid differentiator. Exact `gpt-6-astra` medium completed the strict two-image contract but returned `pass` on `page-122-001`, despite describing two oval portraits; the golden correctly requires `fail` because the crop includes the entire neighboring Sophie L'Heureux portrait. Manual source/crop inspection confirmed a model-wrong false negative. Spend was `$0.066430/$1.50`; the other 21 cases, retries, and fresh GPT-5.5 comparator were not run. Astra is rejected for this safety-critical validator, the retained GPT-5.5 Responses `22/22` evidence remains decisive, and no runtime/default changed. Evidence: `docs/evals/attempts/034-gpt6-astra-page-context-gate.md`.
