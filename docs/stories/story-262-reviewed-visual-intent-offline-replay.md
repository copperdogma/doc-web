---
title: "Reviewed visual intent: offline crop driver qualification"
status: "Done"
priority: "High"
ideal_refs: ["req:3", "req:4", "req:6"]
spec_refs: ["spec:4.1", "spec:4.2", "spec:6"]
adr_refs: ["ADR-002"]
depends_on: []
category_refs: ["spec:4", "spec:6"]
compromise_refs: ["C4", "C5"]
input_coverage_refs: ["image-directory-scans"]
architecture_domains: ["ocr_and_extraction", "doc_web_runtime"]
roadmap_tags: []
legacy_system: ""
---

# Story262 — Reviewed visual intent offline replay

## Goal

Make the approved reviewed-plan route reproducible through the actual driver,
retaining complete title/date source pixels and historical OCR content with
honest authored provenance. No automatic admission, detector/model promotion,
renderer/export proof, default change, source deletion or paid inference.
This new story crosses from sealed Story261's model evaluation into explicit
reviewed-plan wiring and driver artifacts; reopening that sealed eval is wrong.
CLI/evidence is the intended operator surface; no new user UI is needed.

## Context and decision refs

Approved plan is protected local historical evidence, not a landing dependency:
`/Users/cam/.codex/worktrees/scout102-docweb-20261023/docs/evals/evidence/083-scout102-contract-followup/grouping-admission-fix-plan.md`.
Earlier Story261/Attempts082–083 remain outside this scoped landing; no executable dependency requires them.
ADR-002 retains runtime/source provenance boundary. State/graph spec:4 substrate
exists; C4 converge/C5 climb remain. Image-directory-scans coverage row remains
unchanged: this is a reviewed opt-in route, not broader automatic format proof.
Existing Attempts050/054 establish planner ownership/no-amputation precedent.
Historical onward-book-r1 is unsafe globally (later empty pages/portion failure);
selected complete early OCR rows are quarantined producer evidence, validated
independently for this bounded replay, never relabeled globally reusable.

## Eval ladder and approach evaluation

Attempt083 exact detector contract parsed but both arms classified the date as
caption, conflicting with the reviewed title/date pixel-group gate. Full pipeline
and renderer fidelity are deferred. The planning substrate check passed four
synthetic admission cases; next child is real offline driver preservation.
Single-call/AI-only does not resolve unstated grouping or skipped-page admission.
Pure code is appropriate orchestration of already reviewed intent; no new
semantic classifier is implemented. Reuse load_artifact, critical plan and crop
ownership. No new schema or semantic prompt changes. TEI/ALTO research in the
approved plan supplies representation precedent only.

## Acceptance criteria

- [x] Dedicated opt-in recipe and generic runner freeze reviewed intent, complete
  source rows, source images/mappings and producing module/config identities.
- [x] Network/credential/env-file access fails closed throughout driver children;
  no native/mock model responses or fabricated request IDs.
- [x] Actual new driver run emits lossless PNG crops and inspectable manifest;
  title/date edges complete, external caption controls excluded, integral text
  and signature retained on reviewed controls. All cropped RGB equals the
  selected original source rectangles.
- [x] Loaded OCR content equals complete original records except declared run
  envelope changes and registered literal_fidelity:null default addition; native source rows and bytes remain immutable. No renderer
  or downstream source-text deletion claims.
- [x] Focused guard/mapping/validation tests and lint pass; actual artifacts are
  manually inspected. Safety/publication hold remains explicit.

## Tasks and plan

- [x] Add `configs/recipes/recipe-reviewed-visual-intent-offline.yaml`, generic
  `scripts/replay_reviewed_visual_intent.py`, startup guard and reviewed fixtures.
- [x] Fail on stale hashes, malformed/missing target intent, ambiguous source
  mapping, bad dimensions and unexpected crop/provider activity; no silent repair.
- [x] Run actual driver and compare exact source pixels/OCR content. Inspect crops
  and JSONL, record holds and source review in new Attempt084 evidence.
- [x] Focused tests/lint and methodology compile/check. No new format coverage,
  defaults or unrelated code removal; existing route is reused, not duplicated.
- [x] Document commands/results, failures and limits; preserve sealed082/083/plan.

## Workflow gates

- [x] Build complete
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via /mark-story-done

## Central tenets

- [x] T0 — Original producer rows, source hashes/mappings and reviewed author truth retained.
- [x] T1 — No code-based semantic inference; orchestration only.
- [x] T2 — Attempt083 failure and planning substrate precede this implementation.
- [x] T3 — Original text and decoded source pixels preserved; no source deletion.
- [x] T4 — Existing modules with dedicated opt-in recipe; no document-specific code.
- [x] T5 — Actual driver crops/manifest manually inspected.

## Work log

20261023 — Read current AGENTS/Ideal/spec/state/graph/coverage/ADR and local
create-story/build-story skills; the user approved the complete prior plan.
Remote main remains ec0043b. Existing fullmodule admission and crop ownership
are present; no product-module patch is presently needed. Normal conda has cv2.
Reuse prior source-preserving stamping/offline guard patterns; no new provider
or dependency. Full historical run remains unsafe; curated row/source use is
explicitly quarantined and independently hash/schema/mapping checked.

20261023 — Build complete: opt-in recipe/runner/guard and authored public fixtures;
actual r5 driver emits five source-exact PNGs. Original complete OCR content is
exact, with run envelope changes and explicit added literal_fidelity:null default.
Illustration envelope is unregistered; dedicated verifier checks actual fields.
26 new tests + five presence-aware correction tests pass, 59 affected existing
tests pass, focused Ruff passes. r1 loader mismatch, r2 probe stop, interim r3,
r4 ENOSPC retained. All binds blocked in final guard. Producing v1 runner/proof
frozen before v2 offline verification; no driver rerun for that correction.
Opened actual manifest/OCR and final title crop; five final hashes match inspected
controls. No source/default/product-module changes or cleanup; spend0.
See Attempt084 and docs/evals/evidence/084-reviewed-visual-intent/proof-v2.json.
Formal validation/closure remains separate; no auto-admission/rendering claim.

20261023 — Scoped finish-and-push authorized by user. Formal validation: all five
acceptance criteria and six tenets met (grade A for this bounded reviewed-input
route); no remaining implementation gaps. Fresh clean sparse integration against
origin/main ec0043b includes only replay/084/262 and required docs/generated
changes. Both focused commands pass:61 tests across replay+loader+driver+recipe+
planner and29 selected critical crop tests (90 total); focused Ruff passes.
Code/config/fixtures remain exact to the original validated replay; reuse the
actual guarded r5 driver and manually inspected source-exact images rather than
rerun inference or reproduce large sources. No model call, source/default change
or automatic admission claim. Close now via mark-story-done; all workflow gates
checked. Original155-member evidence manifest remains an immutable historical
snapshot including earlier unlanded work. Separate closeout-20261023.json binds
current closed-story/candidate files to frozen proof versions. Original worktree
and old evidence remain untouched. Pertinent inbox inspection found no changes.
Learning review considered: existing probe/schema-default research is retained
in Attempt084; no additional workflow promotion is part of this closeout.
