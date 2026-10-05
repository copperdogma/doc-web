---
title: "Optional source-grounded reference resolution"
status: "Done"
priority: "High"
ideal_refs: ["req:5", "req:6", "req:7"]
spec_refs: ["spec:3.1", "spec:6", "spec:7"]
adr_refs: ["ADR-002"]
depends_on: ["226"]
category_refs: ["spec:3", "spec:6", "spec:7"]
compromise_refs: []
input_coverage_refs: ["scanned-pdf-prose", "born-digital-pdf", "docx"]
architecture_domains: ["document_structure_and_consistency", "doc_web_runtime"]
roadmap_tags: []
legacy_system: ""
---

# Story 243 — Optional source-grounded reference resolution

**Priority**: High
**Status**: Done
**Decision Refs**: ADR-002; docs/notes/reference-resolution-design.md
**Depends On**: Story 226 (final HTML/provenance exists; broader crop work is not a blocker)

## Goal

Make final structural HTML navigable from explicit printed-page and section/label
references without inventing destinations or adding unnecessary model cost.
Validate existing links on final builds; add links to plain text only with
`--resolve-references` or its recipe/module equivalent. Preserve wording, inline
markup, provenance, document boundaries and originals. Emit inspectable evidence
for independent downstream checking.

A new story is warranted: Story 226 owns rulebook extraction/figure fidelity and
its unmerged existing-link repair slice. This story adds optional discovery,
printed-label policy, a reusable invocation contract and measured economics.
Reuse that resolver; do not close Story 226's remaining work.

## Eval Ladder Context

Root: Ideal5/6/7 source-faithful navigable export. Parent: Ingester's 34 broken
provisional section links, repaired by its unmerged resolver. Fresh child
baseline (2026-10-05) with “See page 12”, “section 3” and an HTTP URL emitted zero
records/links. Child eval `reference-resolution` measures exact targets, recall,
abstention, preservation, latency and API cost. Broken-link count alone is not
correctness. Full all-format quality/graduation is not claimed.

## Acceptance Criteria

- [x] Default-off caller flag and recipe/module parameter reach final builds.
  Off skips discovery/enrichment/API work. Existing-link inspection always runs
  on supported final emitters; unsupported flagged surfaces fail explicitly.
- [x] After final IDs exist, resolve explicit printed-page, chapter/section/
  numbered-paragraph, figure/table/footnote labels and HTTP(S) URL references
  when uniquely supported. Preserve visible text and inline markup. Skip code,
  scripts, styles, existing anchors and generated navigation; never nest links.
  Source-authored TOC/index navigation is eligible.
- [x] Tables of contents and indices link their explicit destinations, including
  labelled lists/table rows and page-number lists, preserving exact wording,
  leaders and numbers. Conservative range/repeated-label abstention is reported.
- [x] Printed labels (Arabic/Roman) require explicit source evidence and retain
  scan/logical identity separately. Never substitute PDF index or inferred
  offset. Missing/duplicate/inferred labels and undifferentiated spreads
  abstain with explicit reasons.
- [x] Preserve valid existing links; rebind changed source IDs and repair only
  unique source-supported destinations. Respect filenames, aliases, duplicate
  IDs and external resources. Validate actual final href destinations.
- [x] Report every discovered occurrence with original text/href, source file/
  block/location and available page provenance, candidates/evidence, chosen
  target, canonical resolved/ambiguous/missing status and reason. Record policy,
  scope, latency, calls/cost. Uncertain references remain visible.
- [x] Repeated resolution is safe. Text/provenance IDs/quotes remain intact,
  and finalization occurs before hashes/manifest sealing.
- [x] Fresh driver on/off runs in `output/runs/` prove offset/Roman/ambiguity,
  link repair and downstream consumption. Inspect 5–10 report records and
  rendered output.
- [x] Frozen development/independent goldens measure wrong existing targets,
  missed references, abstention and source/opt-out parity. No known wrong links
  on the declared supported fixture set; natural-document limits explicit.
- [x] Loop-verify and bounded speed/quality/cost hillclimb complete with
  loop-review, accepted/rejected evidence and honest diminishing-returns stop.
- [x] Tests/lint/methodology/skills checks, operator docs and work log current.

## Out of Scope

New OCR; guessed pagination; fuzzy or semantic coreference (“paragraph above”);
automatic cross-document/edition links; external availability fetching; upstream
Ingester packaging changes; crop/transcription fixes; restoring legacy FF
pipeline. No new UI: driver/module callers, HTML and report are the existing
operator surface. Preview remains non-final.

## Approach Evaluation

- **AI-only**: can propose references, but HTML rewriting risks text/ID drift
  and recurring cost; cannot supply absent pagination evidence. Not a tested
  model-quality rejection.
- **Hybrid**: exact binding then bounded AI for unresolved language later,
  only if measured benefit justifies it.
- **Pure code**: chosen for explicit labels, URI parsing and exact symbol lookup;
  upstream AI already supplies structure. No semantic inference is claimed.
- **Simplification baseline**: donor probe detects zero plain references; this
  task's selected behavior is navigation binding/plumbing, not new AI reasoning,
  so no paid model comparison is necessary.
- **Established approaches**: EPUB page-list preserves print-label-to-location
  mappings; Sphinx explicit stable targets. Adopt identity/scope principles.
- **Reuse**: donor `manual_navigation.py`, source-ID aliases and tests.
  Snapshot with SHA256 in `output/story243-baseline/donor/snapshot.json`.
- **Eval**: exact occurrence-to-target goldens, no wrong links, text preservation,
  default-off parity, independent final HTML checks and timed corpus runs.
- **Constraints**: ADR-002 structural bundle/provenance; immutable originals.

## Tasks

- [x] Fetch/pull GitHub; isolate latest origin/main, preserve dirty main.
- [x] Inspect Ideal/spec/state/graph/coverage and resolver substrate.
- [x] Copy current Conductor loop-review and sync compatibility wrappers.
- [x] Record baseline and approach before implementation.
- [x] Extend shared resolver/index/discovery/report and focused controls.
- [x] Wire flag through driver/module/recipe and final emitters; retain raw
  printed-label evidence and original IDs before provenance stamping.
- [x] Add typed report schema and consumer discovery contract.
- [x] Add frozen fixtures/eval, real driver recipe and operator docs.
- [x] Inspect real artifacts and run downstream/regression checks.
- [x] Run strict bounded loop-verify across executable/schema/eval contracts.
- [x] Use improve-eval autonomously: baseline and bounded hillclimb, registry.
- [x] Inspect Codex Forge/Fighting Fantasy methodology/goldens per user steering;
  reserve independent material and avoid book-specific production assumptions.
- [x] Update coverage/state only to bounded demonstrated reality.
- [x] Remove redundant alternatives; no parallel heading resolver.
- [x] `make test`, `make lint`, `make skills-check`,
  `make methodology-check`, `git diff --check`.
- [x] Validate and close with concrete artifact evidence.
- [x] T0: references retain source/evidence.
- [x] T1: upstream intelligence, exact code-owned binding.
- [x] T2: baseline precedes build; no unsupported AI incapability claims.
- [x] T3: faithful text, inline markup and provenance.
- [x] T4: shared helpers/parameters, no book-specific mappings.
- [x] T5: manually inspect rendered output and data.

## Workflow Gates

- [x] Build complete: implementation finished, checks run and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Blocker Summary

None in isolated checkout. Original main cannot fast-forward over unrelated dirt.

## Blocker Evidence

`git pull --ff-only` fetched3bba309 but refused to overwrite registry/Story207.
New worktree HEAD3bba309 is current fetched origin/main.

## Unblock Condition

Satisfied by isolated reference-resolution-4523/doc-web; preserve original dirt.

## Architectural Fit

- Owner: shared final HTML resolver with small emitter call sites.
- State/graph: spec:3/spec:6 substrate exists; spec:7 partial. No new format
  graduation claim or active compromise deletion.
- Verified: chapter `_tag_entry_body` emits blk-* anchors/provenance, raw
  page_html carries labels/inferred flags; office/Marker have final bundle seams.
- Critical gap: provenance alone drops inferred-label distinction. Use raw
  metadata, not fallback printed fields, as resolution authority.
- Contract: additive typed report; resolve before inventories/hashes are sealed.
- Builder ~3747 lines; driver/schemas also large. New logic goes in helpers.
- ADR-002 already owns the runtime boundary; no new ownership ADR is needed.

## Files to Modify

- modules/common/manual_navigation.py and focused reference helpers/tests.
- modules/build/build_chapter_html_v1, driver.py, relevant final emitters.
- schemas.py, doc_web/runtime_contract.py, module metadata.
- tests/fixtures, benchmarks, configs/recipes.
- README.md, docs/RUNBOOK.md, docs/evals, docs/notes/reference-resolution-design.md.
- This story, methodology generated views, state/coverage only as warranted.
- .agents/skills/loop-review/SKILL.md (Conductor refresh).

## Redundancy / Removal Targets

Reuse existing resolver; avoid second heading-repair path, OCR reruns and
post-publication scripts that invalidate hashes.

## Plan

1. Parent owns story/design/acceptance. User-requested Sol6.1 medium workers each
   create goals. Core owns helper/tests; integration owns driver/schemas/emitters;
   eval owns fixtures/benchmark. Disjoint edits.
2. Shared interface: `resolve_navigation(entries, ..., resolve_references=False,
   source_pages=(), provenance_rows=())`. Entries hold final bodies/filenames and
   original-ID aliases. Expand `navigation_resolution_report.json` with canonical
   resolution status, policy/source/target records. Reuse donor legacy behavior.
3. Exact development controls precede natural-document runs. Supported grammar
   is explicit references; unsupported semantics remain visible. No network calls.
4. Loop-verify: fresh find-only core/integration/eval shards, strict-until-clean
   while bounded/converging. Parent verifies findings before fixes. Stop widening
   or repeated nonprogress, not on arbitrary test count.
5. Freeze post-verification baseline. Hillclimb maximum: three revisions/two
   strategies,60 active minutes,zero paid pipeline calls,one independent final
   confirmation. Quality never regresses; require zero wrong targets and content
   loss. Speed adoption: >=10% paired median gain across repeated measurements;
   otherwise retain simpler code. Stop two non-improving attempts or negligible
   remaining user-visible overhead. Never tune on heldout results.
6. Loop-review every three substantive rounds or30 active minutes, earlier for
   unfamiliar obstacles. Record cadence/decision/budget here. Separate resolver
   latency/cost from full OCR/pipeline performance.
7. User authorized plan/build/verification/optimization together; no redundant
   plan gate needed. Commit/push are unrequested.

## Work Log

20261005-0048 — Planning: fetched GitHub and isolated3bba309. Original checkout
preserved. Two Sol6.1 medium scouts verified seams, raw page-label limitations
and fixtures. Refreshed Conductor loop-review. Donor snapshot captured before
edits; fresh probe links/detects zero of three plain reference forms. Exact
binding plus abstention selected. First review due after3 substantive rounds or
30 active minutes. User added FF/Codex Forge goldens as a candidate stress corpus;
read-only research delegated with independent validation separation.


20261005 — User explicitly included tables of contents and indices; absorbed into
the same reference discovery and validation boundary, with independent controls.

20261005-0052 — Loop-review planning checkpoint recorded in
docs/notes/reference-resolution-design.md. Continue exact binding and explicit
abstention; no scope change. Three implementation shards now active, each with
its own goal; FF research complete and independent corpus reserved.

20261005-0101 — Worker loop-reviews: core (three rounds) is aligned but identifies
page identity and DOM range fidelity as primary risks; broad page fallback was
removed and controls added. Integration reuses shared Office/Marker/chapter
seams;203existing focused controls pass, fresh driver/schema proof pending.
Eval first dev probe13/22 reveals real semantic errors, so quality remains the
bottleneck and speed work has not started. One initially omitted TOC page
expectation is classified test-wrong (1of22, same schema/source; preserve prior
receipt). Inline leaf anchors are scored as one logical occurrence with raw
anchor count retained. Independent corpora stay reserved. Next review after
three further material rounds or30active minutes; continue current approach.

20261005 — Verification used fresh Sol6.1 medium core/integration/evaluator
workers. Ordinary loop-verify stopped systemic-audit-needed after recurring DOM
and page-identity classes. A bounded source-backed invariant audit plus parent
structural traversal completion replaced example patches. Independent confirmation
closed all reported defects;111core/23integration/21evaluator controls pass,
development24/24 and Deathtrap627/627 with no wrong links. Full broader evidence
and missing-fixture/test-isolation limitations are preserved in the design ledger.
No outside-owned source or golden was changed. Post-verification baseline and
bounded optimization now authorized to proceed; independent material still sealed.

20261005 — Final closure via /validate and /mark-story-done: all11ACs and T0–T5
met; implementation and validation gates complete. User-authorized Sol6.1 medium
workers each completed their task goals. Ordinary loop-verify failures triggered
bounded structural audits; independent confirmations closed every reported
DOM/page/alias-occurrence defect before final freeze. Full history remains in
the design/invariant notes, including rejected corrections and a nonfrozen
Marker source-fixture correction. No frozen answer was changed during tuning.

Final candidate freeze binds273sources, evaluator and corpora (SHAe89ebbfc5f738a7e6ed97f554a89fb5d4e11de3f38669bbd659ae38b6f5c3ad2).
Single independent synthetic12/12 and Freeway491/491 admitted reference checks
pass with0wrongtargets, all source/audit/opt-out/idempotence gates and0APIcalls/$0.
Freeway's29excluded forms and66additional unscored discoveries remain explicit;
historical OCR health limits prevent whole-book accuracy claims. See attempt059.
Final matched-semantics cache/no-cache20ABBApairs yield14.03%synthetic and11.52%
Deathtrap median paired gains,19/20 and20/20wins, exact output parity. Retain the
small source-parse cache and stop for diminishing returns (~43ms on Deathtrap).
No full-driver speed claim or additive gains; see story243-performance.md.

Fresh final driver artifacts: output/runs/story243-acceptance-{on,off}/output/html/.
Parent inspected all10enabled report decisions (8resolved, page99missing,
page22ambiguous), printed12→logical2, Romaniv→logical3, original-note ID rebind,
contents and index links. Disabled mode adds no plain links and repairs only
one original link. Fourteen provenance rows agree apart from run/time identity.
Schema validation passes; rendered contents link lands at Section7Equipment;
output/story243-final-render.png records final visual proof.

Final focused386tests pass in40.09s and lint passes. Full-suite attempt and
available broad run retain unrelated missing saved crop fixtures and guard
isolation limits (1243passed/1skipped/10deselected/3failures that pass alone);
no full-suite green claim. Fresh affected suite, driver/schema and methodology/
skill checks are the sufficient close-out gate under proportional validation.
ADR-002 remains ACCEPTED; Story226's substrate dependency is satisfied but its
broader crop/transcription work stays In Progress. No state/format graduation
claim or active compromise deletion is warranted. Validation gradeB and
learning-review no-candidate are recorded in docs/notes/story243-validation.md.
CHANGELOG and eval registry updated; generated views refreshed at closure.
Recommended next step: /finish-and-push, only after explicit user authorization.

20261005 — User “Yes” authorizes /finish-and-push for Story243. Refreshed origin/main
remains3bba309, so no source integration change is needed. Candidate runtime/config
hashes retain the exact verified273-source freeze; reuse386 focused tests, final
on/off driver artifacts and the single independent evaluation. Scope is this
isolated worktree's Story243 files only. Primary checkout's four unrelated dirty
files and its HEAD remain untouched; inbox has no pending diff to reconcile.
Land execution branch codex/story243-reference-resolution then fast-forward main.
Landing receipt and remote verification will be retained in output/story243-landing-receipt.json.
