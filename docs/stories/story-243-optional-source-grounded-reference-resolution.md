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

None. Consumer repair acceptance is pending the independent frozen replay.
The original dirty-checkout obstacle was resolved separately at ba4c84a;
its initial implementation evidence below is retained as history.

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

## Consumer regression continuation — 2026-10-05

Cam authorized fixing the Ingester repair packet with direct back-and-forth
between this thread and “Triage and complete project work”. Reopen this same
resolver story; the owner/seam/artifact boundary is unchanged. Earlier proofs
remain historical and do not cover the newly exposed failure classes.

### Repair acceptance criteria

- [x] Existing links with exact source-authored prefixed heading identifiers
  resolve uniquely with both flags; preserve complete identities, duplicate
  abstention and wrong-but-valid target checks. No game prefix dictionary.
- [x] Plain explicit prefixed references and index/contents entries use the
  same exact source evidence. Ordinary code-like prose remains untouched.
- [x] Spelled-out reference kinds require lexical separation; “noted”,
  “annotated”, “denoted” and related prose produce no spurious annotation.
  Explicit note D and documented compact symbol/abbreviation syntax work.
- [x] Explicit companion/other-document references abstain with inspectable
  scope reason, including scope before/after citation and existing anchors.
  Local references in mixed prose continue to resolve when scope is clear.
- [x] Real driver on/off artifacts preserve text/IDs/provenance and inspect
  final links, reports, uncertainty markers; existing 34 matched consumer
  opportunities recovered and new correct-link benefit assessed independently.
- [x] Ingester verifies frozen candidate/content/input hashes, source-backed
  target meaning and packaged destinations, then replies directly here. Keep
  consumer packaging/adoption separate; no edits in its repo by DocWeb.
- [x] Focused producer regression checks and independent consumer generic
  controls pass. Preserve originals, no new OCR or paid calls, no corpus tuning
  from reserved FF answers.

### Authorized repair plan and approach

Use isolated origin/main worktree reference-repairs-1005 at ba4c84a. Delegated
Sol6.1 medium workers own manual_navigation.py/existing-link tests and
reference_resolution.py/discovery tests respectively; coordinator owns shared
story, new driver fixture, integration evidence and repo coordination. Workers
set bounded goals. Budget is three repair/consumer rounds before explicit
strategic reassessment; /loop-review after three substantive rounds or roughly
30active minutes. No schedule created, no blanket commit/push authorization.

The measured parent eval is Ingester's Story038 packet: 0/34 restored links,
false noted/FootnoteD match, wrong local destination for companion citation.
These are deterministic identity/lexical/scope defects, not an extraction or
open-ended generation problem. Compare exact code (chosen), decision model
(typed scope judgement possible later, but adds provider dependency/uncertainty
for explicit source grammar), and language model (broader interpretation but
unnecessary latency/cost and text-mutation risk for these confirmed cases).
No inference or model capability rejection claimed. Candidate enumeration,
source IDs, final mutation and exact validation remain in code.

Relevant spec:3.1, spec:6, spec:7 and ADR002 retain source/identity/document
boundaries; state/graph spec:3/spec:6 exist, spec:7 partial; no graduation or
coverage-matrix promotion. Reuse current APIs/typed report and emitters.

Research: Python re lexical boundary/repetition documentation
https://docs.python.org/3/library/re.html and Sphinx explicit-label/document
cross-reference model https://www.sphinx-doc.org/en/master/usage/referencing.html.
Adopt required word separators and complete unique label identities. Explicit
other-document qualifiers cannot acquire local authority from a matching
number. General natural-language scope remains outside this bounded grammar;
unknown scope is not proof of a local target.

### Continuation work log

20261005 — Read Ingester report and latest thread, reproduced source shape,
confirmed independent owner contract by directly messaging the thread under
Cam's explicit authorization. Frozen historical documents/runtimes retained.
Ingester prepared eight cached flag-pair builds plus fifteen original and twelve
independent controls; it waits for tested-content freeze before candidate runs.

20261005 — Producer baseline on clean primary ba4c84a via real driver:
`output/runs/story243-original-repair-baseline-on/output/html` has missingR123,
false clickable “noted” to FootnoteD and multiple foreign section3 links. An
initial concurrently edited worktree run was not a trustworthy baseline and is
retained as diagnostic only. Local new driver acceptance exposed the broader
“other installation guide” noun phrase; repair rather than relax the expectation.
Three substantive worker rounds prompted /loop-review: aligned; lexical/source
identity code remains the simplest established applicable technique; 237+ tests
are only producer checks, consumer coverage/adoption still unproved. No new
scope or provider calls. Retain explicit-field grammar limits; investigate new
classes rather than widening to heuristic natural-language inference.

20261005 — Two fresh reviewer shards per round found boundary/source-authority
defects. Accepted findings and exact probes are recorded in
`docs/notes/story243-consumer-repair-validation.md`. After two same-class
material rounds, stop the repeated loop per loop-verify systemic-audit rule;
use bounded coordinator invariant audit, focused regression confirmations and
independent consumer acceptance. No strict clean-round claim for this repair.
All assigned fixes finished;570 affected tests and make lint pass. Fresh driver
`output/runs/story243-repairs-accepted-on/output/html` and corresponding off
build pass; inspected16 provenance rows, seven correct on links, one recovered
legacy off link, three foreign abstentions, plain noted/annotations/denoted.
Static non-scripted renders inspected for both chapters; interactive browser
verification unavailable because local-file navigation was rejected. No browser
workaround. PDF/PNG evidence under output/story243-repair-verification.
Frozen891files in output/story243-repair-candidate-freeze.json; handed directly
to Ingester for prepared v2 no-network replay. Runtime writers stopped.

20261005 — Independent Ingester v2 restored34/34 baseline existing links off/on
and improved fresh14→30/34; zero wrong matched targets, exact content/native
bytes, valid separate packages. Still failed pre-frozen G07 according-to
installationguide scope. Repair accepted explicit source-document qualifier
without foreignmodifier; abstain unestablished rather than infer identity.
C11 coordinated Q/APP/R labels share direct navigation cue; each source heading
required. Actual e121 four misses are compact dice outcome mappings, not C11
ordinary coordinated references; keep distinct unsupported coverage limit.
New604tests/lint and driver v3on/off passed; static/JSON/provenance inspection
verified18rows, seven correct onlinks, five scope abstentions. New891-file
manifest v3 sent to consumer; previous failedcandidate/results preserved.
No broad verification-loop restart or additional paid/OCR work.

20261005 — /validate continuation: implementation complete for admitted grammar,
all7repairACs met. Independent direct Ingester v3 closure confirms34baseline
existing targets bothflags,27passages/34assertions,535addedliteral heading
checks across overlappingframes, exact sixpaired preservation and12relocated
packages with0danglingfragments. Fresh30/34on; four compact dice mappings
remain visible/unsupported, no fullrecallclaim. Final891file/test/inputfreeze
unchanged before/after consumer replay. Attempt060 registry and operator docs
updated;604affected producer tests/lint/realdriver/manualstaticinspection pass.
Skip extra codexreview: two fresh delegated review rounds and systemic-audit
stop already govern current bounded verification; no repeated broad review
for stronger wording. No strict clean-round/fullsuite/interactivebrowser claim.
Original workflow/tenet gates remain verified for this source-preserving slice.

20261005 — /mark-story-done continuation: Close now. All7repairACs and3workflow
gates complete; original11ACs,22tasks andT0–T5 verified within documented
limits. Same owning Story243 closed on bounded producer and independent
consumer acceptance; broader Story226/Ingester gates not promoted. Existing
Story243 CHANGELOG entry updated without duplicate; registry Attempt060
records original failures, finalfrozenquality and efficiencylimits. Generated
methodology graph/index refreshed. No implicit commit/push; recommended next
step /finish-and-push only on Cam's explicit landing authorization.

20261005 — Cam invoked /finish-and-push, explicitly authorizing scoped commit,
execution-branch push and fast-forward main landing, including linked consumer
flag integration. All891v3runtime/test files still match the accepted freeze;
reuse604affected tests, lint, real driver/static inspection and independent
consumer v3 acceptance. Inbox reviewed unchanged against primary; unrelated
Gemini challenger note stays live. No extra paid eval or redundant code suite.
Producer origin/main still ba4c84a; no integration changes required. Consumer
owner prepares narrow public-option/evidence slice in isolation, preserving
unrelated source-fidelity work and incomplete story gates. All-repo preflight
precedes first push; dependency producer lands before consumer. Worktrees and
outputs retained because --cleanup was not requested.
