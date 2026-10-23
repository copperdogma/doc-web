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

20260926-1330 — Scout 075's separately approved direct Anthropic `claude-opus-5-5` medium evaluation used an isolated current-base worktree and public owner fixtures. Native strict image/page schemas and owner parity qualified. The detector's Image011 case passed, but full13 produced 12 valid scorer passes averaging `0.9177` plus one locally rejected out-of-range integer coordinate, so it failed both maintained admission gates; fresh Gemini was not run. The independent page-context differentiator `page-122-001` made a source-verified false-safe `pass`, stopping full22 and fresh GPT-5.5. Total all-call spend `$0.352940/$2.00`; no retry, default, prompt, golden or scorer change. Evidence: `docs/evals/attempts/041-opus55-crop-and-page-context.md` and its protected-evidence manifest.

## October 23 continuation — Gemini 4 Argon qualification

20261023 — autonomous triage/evaluate-model decision contract: previous goal turn made concrete progress (Story216 discovery repair, 50 offline regressions, single authorized catalog observation; mixed HTML failure composition also clean). Three credible next candidates: (1) a newly documented/catalog-observed Gemini4 subject can change an existing explicit detector retry trigger; (2) static local HTML structure may already close a stale legacy inventory gap; (3) the mixed-input failure-propagation hypothesis warranted one end-product proof, now clean. Prefer (1) because C4 is converging and a new capable model could collapse decomposition; it has stronger current leverage than another coverage bookkeeping pass. The suspected duplicate inventory key was disproved by strict parsing and receives no fix. Existing missing Story226 source files and real handwriting failures remain held.

Reuse Story232's authoritative-golden comparison ownership instead of a new story per model. Relevant current state/graph: spec:4/spec:8 exist, C4 converge, C5 climb; ADR-002 runtime boundary retained, no new architecture decision. Root/parent: faithful source illustration preservation, current13-case detector plus independent crop/publication safety. Latest parent failure: Attempt061 numeric13/13 but Image011 logo clipping, plus source-adjudicated page-context false-safe. New child: exact native image/strict-output qualification and a source-reviewed frozen detector comparison for `gemini-4-argon`. No handwriting/table calls or automatic default changes.

Official contract research (checked October23): https://ai.google.dev/gemini-api/docs/models/gemini-4-argon establishes exact stable ID and image input/structured outputs; https://ai.google.dev/gemini-api/docs/latest-model recommends medium thinking and at least32768 output for existing apps, with ignored sampling controls removed; GenerateContent remains a documented supported path. https://ai.google.dev/gemini-api/docs/pricing gives current Standard USD2/M input and10/M generated tokens including thoughts through November30. Use that existing native endpoint and header authentication, no tools/cache creation/background jobs/router/fallback. The account catalog's32768 output limit is the conservative configured cap, below documented synchronous65536. Reuse established locked intent/receipt accounting from `mistral4_guard`, with a frozen campaign profile/new ledger rather than old campaign state; bind new implementation/prompt/scorer/golden/config hashes and require complete usage totals before settling charges. This is deterministic transport/accounting work; no decision model or LLM should assign identities, permissions or money.

Frozen matrix: candidate direct Google `gemini-4-argon`, medium thinking, maxOutputTokens32768, strict0–1000 integer crop JSON and local exact contract validation; fresh runtime control direct Google `gemini-3-flash-preview`, unchanged temperature0/16384/plain detector shape. Preserve maintained `crop-conservative-count.js`, canonical b64 image bytes, `image_crop_scorer.py`, `image-crops.json`, all13 test definitions and dynamic target overall>=.95/pass_rate>=.90. Integer instruction comes from the already maintained strict-integer label, not a rewritten semantic prompt. Best retained bounded detector evidence is GPT-6Sol Attempt044 .992731/13, separately production-unqualified; historical leader is not a contemporaneous superiority comparator. No general quality/SOTA/adoption claim from a one-case screen. Structural scorer plus manual source/artwork review; no paid rubric judge (task has no rubric assertion), no judge shopping.

Stages/limits: fresh US$5 inclusive ledger for the whole campaign, public Onward + generated qualification image only, serial -j1, no cache, no automatic retries, at most36 sends, no new credentials. Standing autonomous triage/fix authorization and approved existing project-key reuse cover the bounded investigation; no repeat key question. First native synthetic image/strict JSON contract; then Promptfoo parity on Image011 with fresh control and manual complete-logo source review. Stop on source-visible clipping, false content, transport/schema/identity/usage failure, unknown exposure, or insufficient reserve. If source-safe and affordable, continue unchanged frozen configuration over all13 unique cases per arm, reusing the already measured same-config screen row. Source-visible failure can disqualify before full13. Every send reserves26K input plus complete configured generation, including thoughts; one Argon reserve is .37968. Thirteen worst-case Argon requests alone reserve4.93584 before qualification/controls, so the cap does not guarantee a full campaign; released actual usage may permit it. Cap-limited completion is inconclusive, never a fabricated full result. Page-context is not dispatched by this initial plan; after detector qualification it requires a separately written affordable continuation within the same remaining US$5 cap, with current source-adjudicated truth and fresh appropriate control. No hidden cap reset.

Continuation acceptance:
- [x] Fresh frozen profile/ledger binds exact sources; offline tests cover admission, unknown accounting, identity/schema validation and profile drift before a paid call.
- [x] Native image strict-output then Promptfoo parity establishes exact served identity/terminal success/complete usage, or records an explicit unmeasured access/transport stop.
- [x] Source-reviewed Image011 and conditional full13 comparison use frozen canonical inputs without label/scorer/default changes; stop conditions are enforced and partial scope explicit.
- [x] Every call/unknown exposure is retained, registry attempt and evidence manifest are durable, relevant checks pass, generated methodology reflects final disposition.

20261023 — preflight/implementation: reused the current locked campaign guard with an explicit frozen Google-only profile, new ledger, per-model output limits, exact endpoints, finite call count and source-drift checks. A real offline failure was fixed before dispatch: four synthetic cases showed Google missing/incorrect total/candidate/thought usage could be settled as a partial/zero-output charge. All25 focused guard/Argon tests now pass; Ruff and skill compatibility pass, independent semantic/security review found no blocker. The profile binds53 files: actual adapter/guard/schema helper, canonical task/prompt/helper/scorer/goldens, all13 image payloads,26 resolved one-case task files, native runner/bootstrap/envloader and relevant tests. Native and harness requests retain actual bodies/envelopes below parsing, without headers/keys. Runtime: Python3.11.5/httpx0.27.2/jsonschema4.23.0/Pillow10.4.0/Node24.13.1/Promptfoo0.121.1; installed Promptfoo's local source confirms PROMPTFOO_PYTHON support. Fixed evaluate-model's missing promptfoo runbook link to the actual crop workflow and benchmark README. No dependency upgrade.

20261023 — native/parity/source screen: exact native `gemini-4-argon` image request returned STOP, schema-valid black-square bbox[250,250,750,750], complete1514-token usage, USD.003372. First maintained Image011 strict-integer row returns two boxes, score.9914, exact identity/STOP and complete1804-token usage, USD.004624; manual original-source/crop inspection confirms full Celebrate Saskatchewan logo/outer text retained at pixel bbox[582,148,897,464] on1545x2000 source. Fresh unchanged Gemini3Flash control passes.9826, USD.0045395, with1178 thought tokens included. Total settled after these3requests isUSD.0125355, unknown0; credential scan passed. Exact artifacts: `benchmarks/results/gemini4-argon-20261023/{profile.json,ledger.json,request-001.json,response-001.json,native-image-result.json,candidate-Image011.json,control-Image011.json}` and `output/triage-20261023-argon-eval/{preflight.json,runtime-versions.json,Image011-source.jpg,Image011-candidate-logo.png}`. The serial full-candidate continuation's runner and exact commands are separately hash-bound in `candidate-commands.json`; its same-config Image011 row is reused, not queried twice. Full comparison remains in progress, not yet a13-case or adoption claim.


20261023 — comparison complete: Argon medium and fresh unchanged Gemini3Flash each complete13/13, scoring .9781307692 and .9583153846 respectively on the frozen detector. Detector costs total USD.062512 versus .0517895 (mean per case .004808615 versus .003983808). Mean measured HTTP latency is25,633ms versus6,586ms; Promptfoo provider timing separately averages26,096ms versus7,012ms. These are one-campaign observations, not repeated performance estimates. Best retained bounded Sol Attempt044 remains .992731; no quality-leader/default promotion. Argon Image000 has model-wrong whole-cover bounding undercoverage (.8324); full logo text/emblem/date1905–1980 are retained on Image011. All13 sources reviewed across parent and independent semantic reviewer; exact edge/source equivalence and crop/page-context safety remain unqualified. Safety, handwriting and production recipe were not dispatched. No golden, scorer, runtime default, C5 status or Story191 blocker changed.

20261023 — strategic checkpoint at16:24UTC: bounded read-only gpt-6-astra/ultra review (strongest eligible configured reviewer; served identity unverified) recommends closing this detector slice, retaining the separate source/safety gates, finishing the existing HTML truth correction, then returning to source-to-output product triage. No extra paid lane is justified by unused budget. Final ledger is CLOSED at27 unique completed HTTP200 calls, USD.1176735 ofUSD5, unknown0, with nine unused sends of36. No cap reset or further inference is authorized by this closure.

20261023 — evidence/close-out: Attempt063 and registry preserve exact per-case outputs, pricing, full token accounting, both timing definitions and adoption defer. Portable receipts archive SHA256 `81ec708c6fad14bfa0d1cd3e65078e26a8b9b01816953bf4d643393dbf360a94` reconstructs176 exact files offline, including original receipts, frozen code/config/fixtures and three critical review panels. Parent independently rebuilt into `output/triage-20261023-argon-eval/parent-reconstruction-proof`, verified all original/restored hashes and bytes, and scanned configured key values without exposing them (zero provider calls); proof `parent-reconstruction-validation.json`. The separately hash-bound detector runner/commands are retained in addition to the original53-file profile. No claim that all13 visual panels are archived. Summary/source-review report hashes are explicitly outside the receipt archive.

20261023 — proportional validation and /mark-story-done: reused the passing25 focused guard/adapter tests because all tested source hashes, Python environment and check configuration still match the frozen campaign; fresh Ruff,29-skill compatibility check, JSON/YAML/reference inspection, graph compilation/check and diff hygiene pass. Registry primary-quality anchor ordering is preserved: new comparison rows follow the existing Attempt044 primary rows so coverage does not silently switch to an unqualified comparison or change its score/date. This placement preserves current compiler semantics; explicit stable score references are not introduced here. Dependencies207/209 are Done; all original7 and continuation4 acceptance criteria and6 tasks are met. Existing pipeline code is unchanged by this evaluation, so no driver/default parity or production qualification is claimed. Story closed with no unresolved work in the declared detector comparison. The standing goal continues; /finish-and-push remains available only under explicit commit/push authorization.

## October 23 Central Tenet and documentation verification

- [x] T0 Traceability: frozen53-file profile, raw27 request/response pairs, closed ledger and exact offline reconstruction.
- [x] T1 AI-First: measured the new native model before any pipeline implementation or decomposition.
- [x] T2 Eval Before Build: frozen maintained13-case comparison and explicit source/safety holds; no speculative runtime change.
- [x] T3 Fidelity: source-visible Image000 undercoverage remains model-wrong; no label/scorer relaxation or publication claim.
- [x] T4 Modularity: thin native adapter reuses existing schemas, scorer, fixtures and locked campaign accounting.
- [x] T5 Inspect Artifacts: parent and semantic reviewer inspected all13 source panels and critical original/cropped images; review records limits.
- [x] Docs updated: Attempt063, registry, portable evidence, crop workflow, skill link, changelog and generated story/graph.
