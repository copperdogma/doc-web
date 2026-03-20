# Story 158 — Evaluate `Docling` as a Full Replacement Candidate for `doc-web`

**Priority**: High
**Status**: In Progress
**Ideal Refs**: Requirement #1 (Ingest), Requirement #2 (Detect), Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Any format, any condition, Zero configuration, Dossier-ready output, Traceability is the Product, Graduate, don't accumulate
**Spec Refs**: spec:1.1 C2 (Format-Specific Conversion Recipes), spec:2.1 C1 (Multi-Stage OCR Pipeline), spec:3.1 C3 (Heuristic + AI Layout Detection), spec:5.1 C7 (Page-Scope Extraction with Document-Level Consistency Planning), spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Build Map Refs**: spec:1 Intake & Routing — substrate partial, `C2` climb; spec:2 OCR & Text Extraction — substrate exists, `C1` climb; spec:3 Layout & Structure Understanding — substrate exists, `C3` climb; spec:5 Consistency & Normalization — substrate exists, `C7` climb; spec:7 Graduation & Dossier Handoff — substrate partial, accepted `doc-web` direction; Input Coverage rows: `scanned-pdf-prose`, `scanned-pdf-tables`, and `image-directory-scans` are the incumbent passing lanes, while `born-digital-pdf` and `docx` remain high-priority untested gaps that a stronger external substrate might close faster
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `docs/notes/doc-web-dossier-readiness-gap-analysis.md`, `docs/stories/story-151-name-and-define-standalone-dossier-intake-runtime.md`, `docs/stories/story-156-pinned-doc-web-runtime-adoption-and-dossier-readiness.md`
**Depends On**: Story 156

## Goal

Determine whether `Docling` can replace `doc-web` as the Dossier-facing intake boundary, or whether the right end state is still the current `doc-web` bundle contract or a thinner hybrid adapter. The point is not to preserve sunk cost. The point is to give Storybook and Dossier the strongest possible ingestion engine with the least long-term custom runtime code. This story should produce a decision-ready comparison grounded in local artifacts, manual inspection, and explicit pass/fail criteria so the repo can either keep `doc-web` with confidence or supersede ADR-002 cleanly.

## Acceptance Criteria

- [ ] `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md` contains a researched comparison of three end states:
  - keep `doc-web` as the incumbent Dossier contract
  - adopt a hybrid `Docling` upstream + thin adapter/handoff layer
  - let Dossier ingest native `DoclingDocument` output and retire or sharply narrow `doc-web`
- [ ] A local comparison corpus and scorecard exist before any adapter code is written, covering at minimum:
  - one incumbent `doc-web` bundle smoke lane
  - one scanned-prose or image-directory input
  - one repeated-structure/table-heavy input such as the Onward genealogy path
  - explicit pass/fail checks for provenance, reading order, table fidelity, repeated-structure consistency, and Dossier/Storybook integration fit
  - if a required hard-case source is missing from the current worktree, the story first establishes a durable local comparison input by either adding a repo-owned/publicly licensable fixture or pinning an ADR-local external-source procedure before interpreting the replacement result
- [ ] The story leaves an explicit next state, backed by artifact evidence and manual inspection:
  - keep `doc-web`
  - pursue a hybrid adapter
  - or supersede ADR-002
  And the write-up names the removal or supersession targets that follow from that choice

## Out of Scope

- Migrating Dossier or Storybook to native `DoclingDocument` in this story
- Deleting `doc-web`, superseding ADR-002, or rewriting public contracts before local evidence exists
- General external-tool benchmarking beyond the specific replacement question raised by `Docling`
- Performance tuning unrelated to the architectural decision
- Inventing a second long-lived public boundary just to avoid choosing between `doc-web` and `DoclingDocument`

## Approach Evaluation

- **Simplification baseline**: Run stock `Docling` first on representative local documents and inspect its native `DoclingDocument` plus built-in export surfaces before writing any adapter logic. If those artifacts are already good enough for Dossier, custom code should approach zero. Scout 011 says `Docling` is the strongest first benchmark, but no local pilot artifacts exist yet.
- **AI-only**: An LLM can compare contracts and synthesize migration options, but it cannot prove whether native `Docling` outputs satisfy provenance, repeated-structure, and Dossier-fit requirements on this repo's actual documents.
- **Hybrid**: Treat the current `doc-web` bundle as the incumbent acceptance bar, then compare three concrete end states with evidence: incumbent `doc-web`, hybrid `Docling` plus thin adapter, and native `DoclingDocument` ingestion. This is the leading candidate because it keeps the decision grounded in deletion power instead of repo loyalty.
- **Pure code**: Start translating `doc-web` concepts into `Docling`-shaped adapters before measuring stock `Docling`, or keep extending `doc-web` because it already exists. Both approaches bias the result and violate the "measure before building" rule.
- **Repo constraints / prior decisions**: ADR-002 currently settles `doc-web` as the accepted boundary, Story 156 made that boundary executable and installable, and `docs/spec.md` / `docs/build-map.md` still describe `doc-web` as the graduation target. Scout 011 reopened the question only because `Docling` appears broad enough to pressure `C1`, `C2`, `C3`, `C7`, and `spec:7` at once. Any replacement direction must therefore be strong enough to justify superseding accepted direction, not just adding another option.
- **Existing patterns to reuse**: `configs/recipes/doc-web-fixture-bundle-smoke.yaml`, `tests/fixtures/doc_web_bundle_smoke/`, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `doc_web/runtime_contract.py`, `tests/test_doc_web_bundle_contract.py`, `tests/test_doc_web_cli_contract.py`, and the evidence/decision framing in Scout 011 and Story 156.
- **Eval**: No reusable benchmark exists yet for this exact question. The first evaluation should be a manual scorecard plus inspectable artifacts. If that comparison becomes durable enough to rerun, promote it into `docs/evals/registry.yaml` as a real benchmark rather than leaving it as one-off prose.

## Tasks

- [x] Finish the ADR-003 decision scaffold:
  - record the incumbent `doc-web` boundary, the `Docling` replacement question, and the explicit success/falsification criteria
  - cross-link ADR-002, Story 156, Scout 011, and this story
  - prepare ADR-local research artifacts and report stubs
- [x] Define the comparison corpus and scorecard before writing glue code:
  - reuse the current repo-owned `doc-web` smoke lane as the incumbent baseline
  - select representative local inputs for scanned prose/image intake and repeated-structure tables
  - if the needed hard-case source is absent in this worktree, establish it first as a repo-owned/publicly licensable fixture or an ADR-local pinned local-source procedure so the comparison stays reproducible
  - if available without widening scope too much, include one born-digital or office-document sample to test whether `Docling` closes real coverage gaps faster than the current pipeline
  - define explicit pass/fail questions for provenance, reading order, table fidelity, repeated-structure consistency, installability, and Dossier/Storybook fit
- [x] Run stock `Docling` locally and inspect native outputs:
  - prefer native `DoclingDocument` plus built-in exports first
  - record exact commands, versions, and artifacts
  - inspect sample JSON/HTML outputs manually and note unsupported cases before writing adapters
- [x] Compare the concrete end states:
  - incumbent `doc-web` bundle/handoff
  - hybrid `Docling` upstream plus thin adapter
  - native `DoclingDocument` ingestion in Dossier
  - explicitly record which docs, schemas, runtime surfaces, and tests become redundant if each option wins
- [x] Produce the decision package:
  - update ADR-003 `Research Summary`, `Discussion`, and recommendation
  - if native `DoclingDocument` or the hybrid path wins, name the surfaces that would supersede ADR-002 and the `doc-web` contract docs
  - if `doc-web` remains incumbent, record why and demote `Docling` to benchmark/reference status instead of leaving the question half-open
- [ ] If this story changes documented graduation reality: update `docs/build-map.md`, `docs/spec.md`, `docs/requirements.md`, and any handoff docs with the before/after state honestly
- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [x] If this remains docs/ADR plus pilot-artifact work only: verify story/ADR links, cited artifact paths, and any repo-owned comparison fixtures
  - [ ] If code, recipes, or adapters are added: `make test`
  - [ ] If code, recipes, or adapters are added: `make lint`
  - [ ] If pipeline or adapter behavior changes: clear stale `*.pyc`, run the relevant `driver.py` lane and/or native `Docling` pilot commands, verify artifacts under `output/runs/` or ADR-local research outputs, and manually inspect sample JSON/JSONL/HTML/`DoclingDocument` data
  - [ ] If agent tooling changed: `make skills-check`
- [ ] If a durable benchmark or eval artifact is added: run `/improve-eval` and update `docs/evals/registry.yaml`, or explicitly record why the comparison remains manual research only
- [x] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [x] T0 — Traceability: any candidate replacement still proves source page, element, and provenance mapping rather than collapsing to a black-box document blob
  - [x] T1 — AI-First: stock `Docling` is measured before building new deterministic glue
  - [x] T2 — Eval Before Build: the replacement decision is made from inspected outputs and an explicit scorecard, not vibes
  - [x] T3 — Fidelity: the comparison checks real hard docs for table/repeated-structure losses, not just clean examples
  - [x] T4 — Modular: the repo avoids growing two public runtime boundaries without an explicit reason
  - [x] T5 — Inspect Artifacts: actual `Docling` and incumbent outputs are opened and reviewed manually

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: This is a cross-cutting evaluation story spanning decision docs, the current `doc-web` runtime boundary, and any thin comparison harness or pilot recipe needed to inspect `Docling` output honestly. Ownership starts in the docs/decision layer, not in `modules/build/`.
- **Build-map reality**: `spec:7` currently says `doc-web` is the accepted graduation target, while `C1`, `C2`, `C3`, and `C7` remain active `climb` seams. That means the incumbent handoff boundary is real, but the intake substrate beneath it is still unsettled enough that a stronger external system could justify reopening the boundary.
- **Substrate evidence**: Verified local incumbent substrate exists in `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `doc_web/runtime_contract.py`, `tests/test_doc_web_bundle_contract.py`, `tests/test_doc_web_cli_contract.py`, `configs/recipes/doc-web-fixture-bundle-smoke.yaml`, and Story 156's published readiness note. Missing or intentionally unverified substrate: no local `Docling` pilot outputs live in this repo yet, and there is no native Dossier `DoclingDocument` intake surface here today. This story exists to decide whether those missing pieces are worth building.
- **Data contracts / schemas**: The incumbent downstream contract is still `doc_web_bundle_manifest_v1` plus `doc_web_provenance_block_v1`. This story should not mutate that contract early. If the decision later favors `DoclingDocument`, the new or superseded contract surface must be made explicit in ADR-003 before code changes spread.
- **File sizes**: `docs/stories.md` is 165 lines; `docs/scout/scout-011-external-document-ingestion-systems.md` is 97 lines; `docs/doc-web-bundle-contract.md` is 218 lines; `docs/dossier-doc-web-handoff.md` is 197 lines; `docs/notes/doc-web-dossier-readiness-gap-analysis.md` is 148 lines; `doc_web/runtime_contract.py` is 53 lines; `tests/test_doc_web_bundle_contract.py` is 294 lines; `tests/test_doc_web_cli_contract.py` is 79 lines. Avoid touching `modules/build/build_chapter_html_v1/main.py` (1626 lines) unless the evidence truly requires a comparison adapter inside the current runtime.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, ADR-002, Scout 011, Story 151, Story 156, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, and `docs/notes/doc-web-dossier-readiness-gap-analysis.md`. ADR-003 is the correct place to track the reopened architecture question rather than hiding it in a build-story plan.

## Files to Modify

- /Users/cam/.codex/worktrees/eb88/doc-web/docs/stories/story-158-docling-doc-web-replacement-evaluation.md — track the evaluation scope, acceptance bar, and evidence trail (new file)
- /Users/cam/.codex/worktrees/eb88/doc-web/docs/stories.md — index the new story and keep backlog visibility honest (165 lines)
- /Users/cam/.codex/worktrees/eb88/doc-web/docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md — track the replacement decision and eventual supersession path (69 lines)
- /Users/cam/.codex/worktrees/eb88/doc-web/docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/research-prompt.md — make the research question stand alone (23 lines)
- /Users/cam/.codex/worktrees/eb88/doc-web/docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/final-synthesis.md — collect the recommendation once evidence exists (11 lines)
- /Users/cam/.codex/worktrees/eb88/doc-web/docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/local-pilot-scorecard.md — pin the local corpus, scoring dimensions, and manual inspection bar for the `Docling` replacement pilot (new file)
- /Users/cam/.codex/worktrees/eb88/doc-web/docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/local-pilot-findings.md — record inspected native `Docling` artifacts, observed gaps, and the provisional architecture read (new file)
- /Users/cam/.codex/worktrees/eb88/doc-web/docs/scout/scout-011-external-document-ingestion-systems.md — tighten recommendations if the local pilot materially changes the external-research conclusion (97 lines)
- /Users/cam/.codex/worktrees/eb88/doc-web/docs/doc-web-bundle-contract.md — incumbent contract reference; only update if the decision actually changes the public boundary (218 lines)
- /Users/cam/.codex/worktrees/eb88/doc-web/docs/dossier-doc-web-handoff.md — incumbent Dossier handoff surface; only update if the recommendation changes the consumer contract (197 lines)
- /Users/cam/.codex/worktrees/eb88/doc-web/docs/notes/doc-web-dossier-readiness-gap-analysis.md — compare the current ready-to-present `doc-web` baseline against the `Docling` alternative (148 lines)
- /Users/cam/.codex/worktrees/eb88/doc-web/doc_web/runtime_contract.py — only if a thin adapter or compatibility comparison needs code-backed contract metadata (53 lines)
- /Users/cam/.codex/worktrees/eb88/doc-web/tests/test_doc_web_bundle_contract.py — only if the comparison formalizes a new or superseding contract gate (294 lines)
- /Users/cam/.codex/worktrees/eb88/doc-web/tests/test_doc_web_cli_contract.py — only if the comparison adds runtime-level contract compatibility checks (79 lines)

## Redundancy / Removal Targets

- The current `doc-web` bundle and handoff surface if native `DoclingDocument` becomes the accepted Dossier contract
- Any temporary thin adapter that survives only because the repo avoided choosing between `doc-web` and `DoclingDocument`
- Any docs or workflow language that treat `doc-web` as unquestionably final if ADR-003 reaches a different conclusion
- Long term: avoid carrying both `doc-web` and native `DoclingDocument` as first-class public boundaries without an explicit accepted reason

## Notes

- The user explicitly prefers the strongest ingestion engine for Storybook/Dossier over preserving `doc-web` for sunk-cost reasons.
- The key question is deletion power: if `DoclingDocument` lets Dossier delete more custom runtime code than it adds while preserving provenance and hard-document quality, the repo should be willing to supersede ADR-002.
- The current `doc-web` work is still useful even if it loses. It defines the incumbent acceptance bar and the exact surfaces a replacement must meet or beat.

## Plan

Implementation order and scope (`M`; becomes `L` if the team must source and sanitize a new committed hard-case fixture from scratch):

1. Freeze the incumbent baseline before any `Docling` work.
   - Re-run and record the current `doc-web` contract guardrails without mutating the runtime surface. Fresh baseline from this planning pass: `python -m pytest tests/test_doc_web_cli_contract.py tests/test_doc_web_bundle_contract.py -q` passed at `16 passed`.
   - Treat `configs/recipes/doc-web-fixture-bundle-smoke.yaml`, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `doc_web/runtime_contract.py`, `tests/test_doc_web_bundle_contract.py`, and `tests/test_doc_web_cli_contract.py` as the incumbent acceptance bar.
   - Done looks like: the story and ADR cite a stable incumbent command set, contract docs, and fixture-backed baseline before any challenger output is collected.

2. Establish the comparison corpus and scorecard first.
   - Use the committed clean-PDF source at `testdata/tbotb-mini.pdf` as the low-friction baseline lane, but do not treat it as sufficient evidence for a replacement decision.
   - Close the missing hard-case substrate explicitly. In this worktree, `input/onward-to-the-unknown-images/` and the previously cited reusable hard-case run roots are absent, so the story must first add or pin a durable local hard-case source before interpreting `Docling` results.
   - Preferred path: add a repo-owned/publicly licensable scanned or repeated-structure fixture in a stable repo location. Fallback path: pin an ADR-local local-source procedure with exact path expectations if the source cannot be committed.
   - Define the comparison scorecard before running pilots: provenance traceability, reading order, table fidelity, repeated-structure consistency, install/install-upgrade burden, and Dossier/Storybook integration fit.
   - Done looks like: at least one clean source and one hard scanned/repeated-structure source are concretely named, available locally, and tied to explicit pass/fail questions.

3. Run stock `Docling` in isolation and inspect native outputs before writing adapters.
   - Install `Docling` in an isolated environment rather than the repo runtime. Current substrate evidence says `Docling` is not installed here, and the dry-run dependency tree is heavy (`torch`, `docling-core`, `docling-parse`, `docling-ibm-models`, `rapidocr`, `rtree`, and related packages).
   - Record exact versions, install commands, and output locations. Start with native `DoclingDocument` plus built-in exports; do not translate them into `doc-web` concepts yet.
   - Manually inspect representative JSON/HTML outputs for provenance fields, reading order, tables, and repeated structures. If stock `Docling` fails badly here, stop before inventing a rescuing adapter.
   - Done looks like: reproducible local `Docling` artifacts exist for the chosen corpus, and the work log/ADR name the inspected files and the concrete quality observed.

4. Compare the three end states against the same evidence bar.
   - Score the incumbent `doc-web` bundle, a hypothetical thin `Docling` adapter, and native `DoclingDocument` ingestion against the same scorecard.
   - Only pursue adapter code if stock `Docling` is close enough that the adapter scope is obviously thinner than the current `doc-web` boundary. If stock `Docling` already satisfies the Dossier-facing needs, the adapter should trend toward zero.
   - Explicitly name which docs, tests, runtime helpers, and handoff surfaces become redundant under keep / hybrid / replace.
   - Done looks like: the story can state keep / hybrid / replace with named removal or supersession targets instead of leaving the architecture question open.

5. Publish the decision package and update project direction only if the evidence justifies it.
   - Update ADR-003 `Research Summary`, `Discussion`, and recommendation using the local pilot evidence.
   - If the outcome changes the accepted graduation direction, then update `docs/build-map.md`, `docs/spec.md`, `docs/requirements.md`, and the `doc-web` handoff docs to reflect the new reality. Do not mutate the incumbent contract early.
   - Done looks like: ADR-003 is decision-ready, the story records the next step, and any project-direction changes are explicit rather than implied.

Impact and risk notes:

- Tests affected: the current contract tests are the safety bar throughout. If the story introduces comparison code, adapter code, or a new reusable contract check, `tests/test_doc_web_bundle_contract.py`, `tests/test_doc_web_cli_contract.py`, and the relevant smoke or pilot commands become mandatory reruns.
- Files at highest risk if the recommendation shifts the public boundary: `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `doc_web/runtime_contract.py`, `tests/test_doc_web_bundle_contract.py`, and `tests/test_doc_web_cli_contract.py`.
- Structural health: keep the first pass in story/ADR/research artifacts and isolated pilot outputs. Avoid touching `modules/build/build_chapter_html_v1/main.py` unless the evidence proves a real runtime comparison adapter is necessary.
- Human-approval blockers:
  - new heavyweight dependency footprint for `Docling` and related packages; use an isolated environment rather than installing into the repo runtime by default
  - missing hard-case comparison source in this worktree; this story now includes the small coherent scope expansion to establish or pin that corpus before drawing conclusions
  - no native Dossier `DoclingDocument` consumer exists in this repo today, so Dossier fit must initially be judged against the incumbent handoff contract and docs, not a full end-to-end Dossier runtime migration
- Falsifier for this plan: if we cannot obtain a durable local hard-case source, the story can still produce clean-PDF findings but cannot honestly decide whether `Docling` replaces the current `doc-web` boundary for Onward-class documents.

## Work Log

20260320-1016 — story created: user explicitly said the goal is a first-class ingestion engine for Storybook/Dossier, not preservation of the current `doc-web` project. Existing evidence makes this a real evaluation story rather than a speculative idea: ADR-002 and Story 156 provide an executable incumbent `doc-web` boundary, while Scout 011 identifies `Docling` as the strongest external candidate to pressure `C1`, `C2`, `C3`, `C7`, and `spec:7` at once. Next step: use `/build-story` to define the comparison corpus, run stock `Docling`, and update ADR-003 with a decision-ready keep / hybrid / replace recommendation.
20260320-1030 — build-story exploration: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, ADR-002, ADR-003, Scout 011, Story 156, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `docs/notes/doc-web-dossier-readiness-gap-analysis.md`, `doc_web/runtime_contract.py`, `tests/test_doc_web_bundle_contract.py`, `tests/test_doc_web_cli_contract.py`, and `configs/recipes/doc-web-fixture-bundle-smoke.yaml`. This confirms the story is aligned with the Ideal as a deletion-oriented kill test against the incumbent `doc-web` boundary, not as sunk-cost optimization. Verified incumbent substrate exists in code/docs/tests and the fresh regression baseline remains healthy: `python -m pytest tests/test_doc_web_cli_contract.py tests/test_doc_web_bundle_contract.py -q` passed with `16 passed`. Relevant build-map lanes remain `spec:1` `C2` climb, `spec:2` `C1` climb, `spec:3` `C3` climb, `spec:5` `C7` climb, and `spec:7` partial/accepted around `doc-web`. Critical missing substrate is on the challenger side: `Docling` is not installed locally, the dry-run install footprint is heavyweight, and the desired hard-case comparison corpus is not actually present in this worktree (`input/onward-to-the-unknown-images/` and the cited reusable hard-case `output/runs/` roots are absent even though the coverage matrix still references them). Small coherent scope delta folded into the story: establish or pin a durable local hard-case source before interpreting replacement results. Files most likely to change first remain the story and ADR research surface; files at risk later if the public boundary changes are `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `doc_web/runtime_contract.py`, `tests/test_doc_web_bundle_contract.py`, and `tests/test_doc_web_cli_contract.py`. Pattern to follow: use the fixture-backed `doc-web` smoke lane as the incumbent acceptance bar, run stock `Docling` before any adapter code, and delay contract mutation until ADR-003 has evidence strong enough to keep, hybridize, or supersede ADR-002.
20260320-1042 — implementation started: user approved the plan and explicitly chose the Onward source images or source PDF as the hard-case baseline even though `doc-web` was heavily tuned against that exact document. That is acceptable for this story because the goal is gap discovery, not a fair benchmark leaderboard: any `Docling` miss on Onward will show concrete Dossier-facing failure modes and clarify whether the right follow-up is local tuning, wrapper code, or upstream `Docling` contribution. Story status moved to `In Progress` and the active next step is to pin the actual local Onward source path, set up an isolated `Docling` pilot environment, and collect native artifacts before designing any adapter.
20260320-1058 — pilot corpus pinned and `Docling` environment corrected: located the real local Onward source corpus under `/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/`, confirmed that `Optimized Image Output.pdf` is image-only (`pdftotext` returns blank pages), and extracted the exact incumbent hard-case slice into `output/runs/story157-docling-pilot-r1/input/onward-hardcase-slice-imageonly.pdf` using the source-page ranges from the committed Dossier handoff pack (`28-47`, `78-85`, `108-119`). Wrote the reproducible corpus manifest to `output/runs/story157-docling-pilot-r1/input/source_manifest.json` and the explicit pass/fail rubric to `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/local-pilot-scorecard.md`, so the comparison now has a fixed source set and scorecard instead of ad hoc judgement. `Docling` install investigation also produced a concrete operational finding: the first attempt used an x86_64 Python 3.12 interpreter and fell into a slow local `docling-parse` source build, but a quick wheel check showed `docling-parse==5.6.0` has a native `cp314 macOS arm64` wheel on this machine. Pivoted to `.venv-story157-docling-arm64`, installed `docling==2.80.0` successfully there, and started the first control conversion on `testdata/tbotb-mini.pdf`. That control run is still warming models and has not yet emitted inspectable artifacts, so no quality claim is made yet. Next step: let the control export finish, inspect the native JSON/HTML/Markdown outputs, then run the same harness on the 40-page Onward hard-case slice and compare against the incumbent `doc-web` handoff pack.
20260320-1058 — native `Docling` pilot artifacts inspected: the control run on `testdata/tbotb-mini.pdf` completed successfully in `67.87s` and emitted coherent markdown plus a native JSON structure with page-aware provenance (`prov[].page_no` + `prov[].bbox`) under `output/runs/story157-docling-pilot-r1/docling/tbotb-mini/`. The image-only Onward hard-case slice also completed successfully in `68.248s` under `output/runs/story157-docling-pilot-r1/docling/onward-hardcase-slice/` and produced `40` pages, `312` text items, `20` tables, and `7` pictures. Manual inspection shows `Docling` is a real contender, not a gimmick: the Arthur opening paragraph is close to the incumbent `doc-web` paragraph in `benchmarks/golden/onward/dossier-doc-web-handoff-v1/chapter-010.html`, and the native JSON contains real table cell structures with page/bbox provenance. But the gaps are concrete too. The Arthur family section still flattens the first large genealogy block into prose before the first recovered table, subgroup headings leak into table cells, and the built-in export surface is not Dossier-ready: HTML emits `0` `<img>` tags and `0` `id=` anchors, while markdown emits `7` `<!-- image -->` placeholders instead of bundle-local image references. A targeted OCR-backed Arthur follow-up under `output/runs/story157-docling-pilot-r1/docling/onward-arthur-split-ocr/` did not rescue the main table onset; in this case the raw image-only slice actually produced more usable table recovery (`20` tables on the slice vs `5` on the OCR-backed chapter). I recorded the inspected artifacts and provisional interpretation in `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/local-pilot-findings.md`. Current read: `Docling` looks strong enough to justify a hybrid or upstream-improvement path, but its native document/export surface does not yet beat the current Dossier-facing `doc-web` contract.
20260320-1058 — decision package updated: promoted ADR-003 to `DISCUSSING`, filled `research/final-synthesis.md` with the current architecture read, and turned the pilot evidence into a concrete provisional recommendation. Recommended choice is now `hybrid`: keep `Docling` as the leading upstream substrate candidate, but do not recommend native `DoclingDocument` replacement yet because the built-in export surface still misses stable block anchors, bundle-local image exports, and clean enough repeated-structure segmentation. Runner-up remains `keep doc-web` if the next adapter proof turns out not to be materially thinner than the current boundary. Next step: run `/validate` on this story package, then either create the thin hybrid adapter proof story or explicitly freeze the question with `doc-web` remaining incumbent.
