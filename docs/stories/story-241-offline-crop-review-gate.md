---
title: "Offline opt-in crop review gate"
status: "Done"
priority: "Medium"
ideal_refs: ["Traceability is the product", "Fidelity to the source"]
spec_refs: ["spec:4", "spec:8", "C5"]
adr_refs: []
depends_on: ["240"]
category_refs: ["spec:4", "spec:8"]
compromise_refs: ["C5"]
input_coverage_refs: ["image-directory-scans"]
architecture_domains: ["illustration-extraction"]
roadmap_tags: ["artifact-provenance"]
---

# Story241 — Offline opt-in crop review gate

## Goal

Implement the user-approved offline slice of Story240's uncertainty-review plan: every crop candidate (model pass AND fail) requires a bound explicit local operator decision before opt-in chapter publication. Preserve source/crops; hold rather than omit unresolved visuals. No API calls, live adapter/default/prompt/golden changes, commits or push. This is a new opt-in review seam, not restoration of a retired runtime classifier. Existing C5/detector/caption helpers retained.

## Plan

New shared review contracts, local source/crop inspection and decision tool, deterministic release module, opted-in builder revalidation/staged publication, fixture/loader recipe and regression tests. Bind complete operator source inventory and exact pages/portions as well as run/source/crop/bbox/row/model proposal/decision identities. Review authority is an explicit trusted local operator boundary, not remote authentication. Fixture approvals are synthetic test evidence; never fabricate Cam reviews. Review saved S3 pass as a proposal with plausible grouping; no hidden intent classifier requirement. Existing source-aware ADRs were searched; this reversible opt-in local policy slice adds no global routing/schema architecture decision.

## Acceptance Criteria

- [x] Every candidate remains in custody; model verdict cannot grant/deny publication authority.
- [x] Missing/stale/duplicate/conflicting/unauthorized/unresolved decisions and incomplete source inventory hold release.
- [x] Original source/crop/row/bbox/proposals/decisions/authority/pages/portions changes invalidate released approval at builder; traversal/symlink/output aliases rejected.
- [x] Direct opted-in builder bypass fails before output mutation; no approved crop lost or extra/unreviewed page rendered.
- [x] Real fixture-driver release→build proofs, full-resolution source/crop and finalHTML inspection; zero API spend.
- [x] Focused tests, lint, graph/check, runbook and evidence records complete; defaults/paid eval evidence unchanged.

## Tasks

- [x] Implement shared contracts/release module/review tool.
- [x] Add opt-in builder enforcement and offline recipe/fixtures.
- [x] Run substantive negative and real driver integration tests; inspect outputs.
- [x] Record source-safe evidence/runbook and validation.

## Workflow Gates

- [x] Build complete
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via /mark-story-done

## Central Tenet Verification

- [x] T0: bound source/crop/operator/proposal provenance.
- [x] T1: models propose; code enforces explicit review decisions.
- [x] T2: Attempt048 measured physical capability/policy gap before this slice.
- [x] T3: rejection preserves source and failed candidates.
- [x] T4: opt-in module/recipe, defaults unchanged.
- [x] T5: original/crop/output artifacts manually inspected.

## Work Log

September30 — Cam approved offline implementation. Dedicated existing worktree preserves prior evaluation work. Allocated241 (max existing240). No model calls authorized. Selected source seams from guided crop manifest, driver DAG and chapter builder; blanket all-candidate review protects false-rejects as well as silent passes.


September30 — Build complete. New trusted-local contracts/release/review tool bind run, native source dimensions/pixel bbox, row, source/crop, complete operator inventory, proposal/evidence, explicit append-only review events and operator authority. Builder opt-in revalidates before staging and publication, rejects output aliases/inode aliases and missing/stale/bypass inputs, and requires every approved crop exactly once. No source deletion or model authority. Source-review display includes inventory pages without detected candidates; completeness remains an explicit operator assertion.

Validation evidence: final focused suite passed 208 tests, including the display-completeness case; exact results are recorded in `docs/evals/evidence/story241-crop-review/validation.json`. Real approved driver run `story241-crop-review-approved` completes; unresolved fixture run `story241-crop-review-held` emits structured held counts and no approved manifest/images/HTML. Earlier recipe path/loader preflights and prior proof snapshots are separately retained, never relabelled as successes. Owner inspected S3's plausible coherent grouping and S4 integral badge lettering; coordinator rendered final chapter with both exact assets and source display with red boundaries. Approvals are explicitly synthetic, not Cam reviews. Retained source/crop bytes verified. Runbook: `docs/runbooks/crop-safety-review.md`.

Build handoff remains In Progress with Build complete; formal /validate and /mark-story-done are the next workflow gates. No API calls, defaults/prompt/canonical-golden changes, commits or push in this slice. Story240 remains Done; future live Sol pilot/heldout model qualification are unmeasured and require their own proposal.


September30 — Formal validation and closure approved by Cam. No material findings; all six acceptance criteria Met, grade A, Close now. Reused208 passing tests and selected Ruff under exact76 input/fixture/proof hashes; fresh receipt, source/crop byte, approved/held driver artifact, archive, paid-ledger and graph/whitespace checks pass. Prior independent clean review applies to the same candidate; no redundant broad dirty-worktree review or provider calls. See `docs/evals/evidence/story241-crop-review/formal-validation.md`. All workflow gates checked; Story241 Done. Existing changelog entry retained without duplication. Generated graph/index regenerated and checked. No commits/push/default adoption. Recommended next step: separately authorized `/finish-and-push`.

September30 — Cam authorized scoped finish-and-push of this campaign and linked offline review gate. Landing preparation reuses exact applicable208 test/driver proof inputs, passes10 current guard tests plus selected Ruff, graph, prompt syntax and whitespace checks, and verifies lossless reconstruction of25 original047,54 original048 and179 continuation files against live originals. Primary checkout and prior paid evidence preserved. Candidate is prepared on the current remote-main base; no push until coordinator all-repo preflight completes. See `docs/evals/evidence/story241-crop-review/landing-preflight.json`.
