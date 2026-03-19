# Story 154 — Dossier `doc-web` Semantic HTML Handoff

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #6 (Validate), Requirement #7 (Export), Dossier-ready output, Traceability is the Product
**Spec Refs**: spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/doc-web-bundle-contract.md`, Story 152, Story 153
**Depends On**: Story 152, Story 153

## Goal

Publish the exact handoff contract that Dossier will consume from `doc-web`. ADR-002 settled the architectural direction, but Dossier still needs a concrete compatibility target: what files `doc-web` outputs, what Dossier pins/version-checks, what provenance fields are mandatory for citation, and what fixture or contract-test pack proves compatibility. This story should turn that into a handoff package rather than leaving "Dossier will consume it" as a vague future promise.

## Acceptance Criteria

- [x] A Dossier-facing handoff contract is documented, including expected `doc-web` bundle files, required manifest/provenance fields, versioning expectations, and compatibility-test expectations.
- [x] The story identifies the exact fixture/golden pack that should be used for Dossier-side contract testing once the Dossier work begins.
- [x] The handoff contract clearly distinguishes responsibilities:
  - codex-forge R&D
  - `doc-web` runtime
  - Dossier consumer
- [x] The story names the first concrete Dossier-side follow-up needed to support `--target semantic_html` or equivalent stop-point behavior.

## Out of Scope

- Implementing Dossier code inside this repo
- Building the standalone `doc-web` repo itself
- Visual website theming or polish
- Reworking upstream codex-forge extraction unless the Dossier contract exposes a hard blocker

## Approach Evaluation

- **Simplification baseline**: First ask whether Dossier can consume the accepted `doc-web` bundle with a thin compatibility layer and pinned bundle contract, rather than requiring a bespoke ingestion path immediately.
- **AI-only**: An LLM can draft the handoff contract, but it cannot choose the right mandatory fields without the real `doc-web` bundle contract from Story 152 and seam assumptions from Story 153.
- **Hybrid**: Use the accepted ADR direction plus the bundle contract to synthesize a Dossier-facing contract package and compatibility-test plan. This is the leading candidate.
- **Pure code**: Start changing Dossier blindly before the handoff contract exists. Fastest locally, but it guarantees churn and rework.
- **Repo constraints / prior decisions**: ADR-002 already settled that Dossier consumes `doc-web` via tagged SemVer releases and contract tests, not by pulling codex-forge directly.
- **Existing patterns to reuse**: Story 152 contract outputs, Story 153 seam extraction notes, current Onward structural website outputs, and codex-forge's golden-build discipline.
- **Eval**: The deciding evidence is whether the proposed handoff contract is specific enough that a Dossier implementer could build the consumer without asking basic questions about files, fields, or versioning.

## Tasks

- [x] Define the Dossier-facing `doc-web` handoff package:
  - bundle files
  - manifest expectations
  - provenance expectations
  - versioning expectations
- [x] Define the first Dossier compatibility-test pack:
  - fixture inputs
  - expected bundle outputs
  - failure modes that should block upgrades
  - committed handoff fixture pack path with final `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1` surfaces, rather than a mix of review-pack metadata and test-only examples
- [x] Identify the first Dossier-side implementation slice required to consume `doc-web`
- [x] Publish the handoff artifact where future Dossier work can reference it directly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] This remained docs/fixture/test-focused work, and the referenced bundle/provenance fixture paths were verified manually
  - [x] Contract tests changed, so `make test` and `make lint` both ran clean
  - [x] Pipeline behavior did not change in this repo, so no fresh `driver.py` run was required for Story 154
  - [x] Agent tooling did not change, so `make skills-check` was not required
- [x] This story added a Dossier contract fixture pack rather than changing prompt-eval goldens, so `/improve-eval` and `docs/evals/registry.yaml` were not required
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: Dossier handoff preserves the provenance needed for exact citation and open-original behavior
  - [x] T1 — AI-First: do not introduce unnecessary bespoke Dossier transforms if `doc-web` can own the clean contract directly
  - [x] T2 — Eval Before Build: validate the handoff package against real bundle fixtures before external integration
  - [x] T3 — Fidelity: handoff contract does not erase structure or location data for convenience
  - [x] T4 — Modular: keep codex-forge, `doc-web`, and Dossier responsibilities explicit
  - [x] T5 — Inspect Artifacts: manually inspect the fixture bundles and provenance maps used for handoff

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Handoff and contract-doc layer in `doc-web`, with Dossier implementation deferred to the downstream repo.
- **Data contracts / schemas**: This story consumes the Story 152 contract and should not invent a parallel schema.
- **File sizes**: `README.md` is 72 lines, `docs/spec.md` is 194 lines, and `docs/build-map.md` is 457 lines. Prefer a dedicated handoff doc or note instead of bloating those files further.
- **Decision context**: ADR-002 is the authority. Story 152 defines the contract; Story 153 defines the extraction seam. This story should not reopen either decision.

## Files to Modify

- /Users/cam/.codex/worktrees/2ce8/doc-web/docs/stories/story-154-dossier-doc-web-semantic-html-handoff.md — keep the handoff story current
- /Users/cam/.codex/worktrees/2ce8/doc-web/docs/dossier-doc-web-handoff.md — publish the Dossier-facing handoff contract and first implementation slice directly (new file)
- /Users/cam/.codex/worktrees/2ce8/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1/ — commit the first Dossier compatibility-test pack with the final contract surfaces (new directory)
- /Users/cam/.codex/worktrees/2ce8/doc-web/tests/test_doc_web_bundle_contract.py — extend contract coverage to validate the committed handoff pack if implementation adds fixture surfaces
- /Users/cam/.codex/worktrees/2ce8/doc-web/docs/notes/standalone-dossier-intake-runtime-plan.md — update the migration plan with the published handoff package and first Dossier slice
- /Users/cam/.codex/worktrees/2ce8/doc-web/docs/decisions/adr-002-doc-web-runtime-boundary/adr.md — only if the handoff contract reveals a true architectural change
- /Users/cam/.codex/worktrees/2ce8/doc-web/README.md — only if the handoff expectations require a higher-level repo-role clarification or the new handoff doc is otherwise hard to discover

## Redundancy / Removal Targets

- Any vague doc text that says "Dossier will consume `doc-web`" without naming the expected bundle contract
- Any future ad hoc handoff notes that are not tied back to the accepted ADR and these stories

## Notes

- This story is still owned in `doc-web` because the runtime boundary needs to be published here before the Dossier repo starts implementation.
- The Dossier-side code story should be created in Dossier after this handoff package exists.

## Plan

### Baseline / Eval

- Baseline artifacts inspected:
  - `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/manifest.json` is a reviewed-slice descriptor (`schema_version=onward_reviewed_html_slice_v1`), not the final Dossier-consumer bundle manifest.
  - `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/chapters_manifest_regression.jsonl` plus reviewed chapters `chapter-010.html`, `chapter-011.html`, `chapter-017.html`, `chapter-022.html`, and `chapter-023.html` are the current trusted HTML quality slice.
  - `tests/test_doc_web_bundle_contract.py` proves the `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1` schemas and validator wiring, but its bundle/provenance examples are synthetic and not yet a committed Dossier handoff pack.
- Baseline result from exploration:
  - the repo already has the accepted bundle/provenance contract and a reviewed HTML golden;
  - it does not yet have one committed, Dossier-facing fixture pack that combines final contract surfaces, reviewed HTML content, and upgrade-blocking expectations in a single location;
  - the reviewed slice currently contains no committed `provenance/blocks.jsonl` or emitted `id="blk-..."` anchors, so Story 154 should not point Dossier at that pack alone and pretend the consumer contract is complete.
- Success test for Story 154:
  - a Dossier implementer can use one handoff document and one committed fixture pack to answer all basic integration questions without reopening ADR-002, Story 152, or Story 153;
  - the handoff names the exact files, mandatory fields, version pinning rules, compatibility checks, and first Dossier implementation slice;
  - the committed handoff pack validates mechanically against `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1`.

### Implementation Order

1. Publish the Dossier-facing handoff contract in `/Users/cam/.codex/worktrees/2ce8/doc-web/docs/dossier-doc-web-handoff.md`.
   - Define the consumer-facing bundle contract in Dossier terms: required files, mandatory manifest/provenance fields, version pinning and upgrade rules, responsibilities split across codex-forge / `doc-web` / Dossier, and the first downstream implementation slice.
   - Done looks like: a Dossier engineer no longer has to reconstruct the contract from the ADR plus Stories 152-153.
2. Create a dedicated committed fixture pack in `/Users/cam/.codex/worktrees/2ce8/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1/`.
   - Base it on the real Story 153 emitted bundle output, then narrow it to the reviewed hard-case slice so Dossier can pin final consumer surfaces instead of review metadata: `manifest.json` using `doc_web_bundle_manifest_v1`, `provenance/blocks.jsonl`, the reviewed HTML subset, and a short metadata/readme note naming source lineage and intended assertions.
   - Done looks like: Dossier can pin one pack instead of mixing the reviewed-slice descriptor with synthetic schema examples.
3. Add focused automated validation for the handoff pack in `/Users/cam/.codex/worktrees/2ce8/doc-web/tests/test_doc_web_bundle_contract.py`.
   - Assert that the committed pack validates against the frozen schemas, that the reviewed HTML entries line up with the manifest reading order, and that the named failure modes (missing required fields, reading-order drift, absent provenance sidecar, incompatible version change) are explicitly upgrade-blocking.
   - Done looks like: local contract drift fails in tests before any downstream Dossier integration starts.
4. Update migration and tracking docs.
   - Update `/Users/cam/.codex/worktrees/2ce8/doc-web/docs/notes/standalone-dossier-intake-runtime-plan.md`, this story, and `/Users/cam/.codex/worktrees/2ce8/doc-web/docs/stories.md` so they point at the published handoff doc, the committed fixture pack, and the first Dossier-side slice.
   - Done looks like: future work references stable doc/fixture paths, not story prose.

### Impact / Risk

- **Small scope expansion folded into this story:** create a dedicated committed Dossier fixture pack. Rationale: the existing Story 149 reviewed slice is a trusted quality golden, but its `manifest.json` is review metadata, not the final `doc_web_bundle_manifest_v1` surface Dossier should pin.
- **Files expected to change:** this story, a new `/Users/cam/.codex/worktrees/2ce8/doc-web/docs/dossier-doc-web-handoff.md`, a new fixture directory under `/Users/cam/.codex/worktrees/2ce8/doc-web/benchmarks/golden/onward/`, `/Users/cam/.codex/worktrees/2ce8/doc-web/tests/test_doc_web_bundle_contract.py`, and `/Users/cam/.codex/worktrees/2ce8/doc-web/docs/notes/standalone-dossier-intake-runtime-plan.md`.
- **Files at risk:** `/Users/cam/.codex/worktrees/2ce8/doc-web/docs/doc-web-bundle-contract.md` if the handoff doc drifts from the frozen contract, plus the existing reviewed slice under `/Users/cam/.codex/worktrees/2ce8/doc-web/benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/` if implementation mutates source evidence instead of deriving a separate handoff pack.
- **Human-approval blocker:** whether to create the dedicated committed Dossier pack now. Recommendation: yes. Pointing Dossier at a mixture of the Story 149 review-pack descriptor and synthetic contract examples would keep the contract vague at exactly the point this story is supposed to make concrete.
- **Relative effort:** S

## Work Log

20260318-2337 — story created: captured the Dossier-facing follow-up implied by ADR-002. The architecture is settled, but Dossier still needs a precise handoff package before anyone starts coding against the future `doc-web` runtime.
20260319-1440 — exploration and planning: traced `docs/ideal.md`, `docs/spec.md` (`spec:6`, `spec:7`), ADR-002, `docs/doc-web-bundle-contract.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, Stories 152-153, `tests/test_doc_web_bundle_contract.py`, and the committed Story 149 reviewed slice under `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/`. Result: the accepted runtime contract and a trusted reviewed HTML slice already exist, but the repo still lacks a single committed Dossier-consumer pack that combines final `doc_web_bundle_manifest_v1` / `doc_web_provenance_block_v1` surfaces with reviewed HTML content and explicit upgrade-blocking expectations. Evidence: the reviewed slice `manifest.json` is `schema_version=onward_reviewed_html_slice_v1` review metadata rather than the final consumer bundle manifest; there is no committed `provenance/blocks.jsonl` in that pack; and the current schema examples live only in `tests/test_doc_web_bundle_contract.py`. ADRs / decision docs consulted: ADR-002 only; no additional decision doc was needed because the boundary, release model, and provenance level are already settled there. Patterns to follow: publish a dedicated top-level handoff doc like `docs/doc-web-bundle-contract.md`, keep the reviewed Story 149 slice as source evidence rather than mutating it in place, and add test-backed committed fixtures instead of pointing Dossier at story prose. Surprises: this story still contained stale worktree-specific `codex-forge` paths even though the local repo is `doc-web`, the local worktree has no `output/runs/` checkout to use as a durable source of truth, and the current "golden" pack is a quality-review bundle rather than the final consumer contract pack. Next: human approval on the small scope expansion to create that dedicated Dossier handoff fixture pack before implementation.
20260319-1516 — handoff package implemented: published `/Users/cam/.codex/worktrees/2ce8/doc-web/docs/dossier-doc-web-handoff.md`, added the committed Dossier contract-test pack under `/Users/cam/.codex/worktrees/2ce8/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1/`, extended `/Users/cam/.codex/worktrees/2ce8/doc-web/tests/test_doc_web_bundle_contract.py` to validate the committed pack, and updated `/Users/cam/.codex/worktrees/2ce8/doc-web/docs/notes/standalone-dossier-intake-runtime-plan.md` plus `/Users/cam/.codex/worktrees/2ce8/doc-web/README.md` so the downstream handoff is easy to find. The committed pack now uses real emitted Story 153 surfaces instead of synthetic examples: `manifest.json` validates as `doc_web_bundle_manifest_v1`, `provenance/blocks.jsonl` validates as `doc_web_provenance_block_v1`, the subset HTML keeps real `blk-*` anchors, and all referenced `images/` assets are bundle-local. Manual inspection evidence: `/Users/cam/.codex/worktrees/2ce8/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1/manifest.json` has `5` ordered entries (`chapter-010`, `chapter-011`, `chapter-017`, `chapter-022`, `chapter-023`); `/Users/cam/.codex/worktrees/2ce8/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1/provenance/blocks.jsonl` has `134` rows including `blk-chapter-010-0002 -> p028-b2`, `blk-chapter-011-0006 -> p038-b6`, and `blk-chapter-022-0004 -> p108-b4`; `/Users/cam/.codex/worktrees/2ce8/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1/chapter-011.html` preserves the matching `id="blk-chapter-011-0006"` figure anchor and bundle-local image references. Validation: `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file benchmarks/golden/onward/dossier-doc-web-handoff-v1/manifest.json` passed, `python validate_artifact.py --schema doc_web_provenance_block_v1 --file benchmarks/golden/onward/dossier-doc-web-handoff-v1/provenance/blocks.jsonl` passed, `python -m pytest tests/test_doc_web_bundle_contract.py -q` passed (`13 passed`), `make lint` passed, and `make test` passed (`639 passed, 6 skipped`). Result: the Dossier-facing contract, the exact fixture pack, the responsibilities split, and the first downstream implementation slice are now explicit and test-backed. Next: hand off to `/mark-story-done` if the user wants the lifecycle closed formally.
20260319-1605 — `/mark-story-done` close-out: rechecked the Story 154 acceptance criteria, tenet checklist, docs/test evidence, and related ADR alignment against ADR-002. Added the final story lifecycle updates, replaced the machine-specific absolute source path in the committed handoff-pack README with repo-portable lineage text, and aligned the planning note with the delivered Story 153-derived pack lineage. Completion evidence remains the same validated artifact set: `/Users/cam/.codex/worktrees/2ce8/doc-web/docs/dossier-doc-web-handoff.md`, `/Users/cam/.codex/worktrees/2ce8/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1/manifest.json`, `/Users/cam/.codex/worktrees/2ce8/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1/provenance/blocks.jsonl`, and `/Users/cam/.codex/worktrees/2ce8/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1/chapter-011.html`. Story 154 now closes as Done because the documented handoff contract, committed consumer fixture pack, focused regression coverage, and repo docs are all present and the required validation passed.
