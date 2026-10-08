---
title: "Fresh manual source fidelity"
status: "Done"
priority: "High"
ideal_refs: ["req:3", "req:4", "req:5", "req:6", "req:7"]
spec_refs: ["spec:3.1", "spec:4.1", "spec:4.2", "spec:6", "spec:7"]
adr_refs: ["ADR-001", "ADR-002"]
depends_on: ["243", "250"]
category_refs: ["spec:3", "spec:4", "spec:6", "spec:7"]
compromise_refs: ["C3", "C4", "C5"]
input_coverage_refs: ["born-digital-pdf"]
architecture_domains: ["document_structure_and_consistency", "doc_web_runtime"]
roadmap_tags: []
legacy_system: ""
---

# Story 251 — Fresh manual source fidelity

**Status**: Done
**Priority**: High
**Decision Refs**: ADR-001; ADR-002; docs/notes/fresh-manual-source-fidelity.md
**Depends On**: Story243, Story250

## Goal

Repair source-fidelity failures demonstrated by a fresh, self-contained manual
conversion: preserve source illustrations alongside transcribed descriptions or
tables, keep literal URLs separate across line breaks, and resolve printed TOC
rows only when their complete source title/page evidence identifies one target.
Produce an offline regenerated derivative with readable correction/provenance
records and exact producer identity. Retain all original ordered wording and
upstream evidence. Consumer acceptance is a separate final gate.

User explicitly requested a new story. This adds a native PDF occurrence recovery
and immutable replay boundary distinct from Story250's cross-document binding
and Story226's broad graphics/OCR pilot. Reuse those runtimes without claiming
completion of Story226's all-page or maximum embedded-pixel requirements.

## Eval Ladder Context

Ideal faithful structural export → fresh retained paid OCR/planner/build output
→ independently observed missing illustrations, broken line-break URL and 16
unresolved TOC entries. Baseline is preserved at
/tmp/doc-web-fresh-manual-review-20261008/retained-run/. Root visual inspection
confirms the source card panels and text-only output table. Child proof is a
zero-inference replay with synthetic behavioral controls and source/pixel/text
comparison. No new model evaluation or broader format graduation is authorized.

## Acceptance Criteria

- [x] Preserve the entire supplied fixture, especially paid OCR/planner outputs
  and initial final bundle, with before/after SHA-256 inventory equality.
- [x] Restore all 28 observed missing card-image occurrences on the affected
  logical pages alongside their exact descriptions/table rows. Preserve the
  repeated small occurrence separately from the existing enlarged illustration.
- [x] Reuse the eight existing unplaced crops; recover the 20 uncropped
  occurrences from original PDF geometry and retained source pixels, with
  source/orientation/hash evidence. No invented pixels or microprint.
- [x] General reusable opt-in native recovery policy and inspectable accepted/
  rejected occurrence inventory; no source title, page numbers, card names or
  fixture-specific replacements in runtime logic. Ambiguous associations hold.
- [x] URL discovery respects authored line breaks, preserves literal wording and
  markup, and produces only source-supported destinations. The next line's word
  remains outside the URL anchor. Existing correct links survive.
- [x] TOC resolution uses source row title and observed printed-page evidence,
  with unique heading fallback only when independently justified. No inferred
  page-label authority, guessed duplicate choice or unrelated number binding.
- [x] Existing ordered text, choices, costs, exceptions and block provenance
  survive. New figures add source-located provenance; source wording is not
  removed merely because a crop also contains text.
- [x] Real driver replay writes a new derivative under output/runs/ with zero
  new inference, original retained output intact, readable source-to-output
  correction report and complete producer/source identity.
- [x] Focused positive/refusal/regression tests, decoded-pixel checks, manual
  source/result inspection and rendered browser navigation prove current output.
- [x] Measure restored-illustration sampling against original PDF placements,
  preserving protected crop boundaries and distinguishing rendered pixels from
  embedded source bytes/channels.
- [x] Exact runtime/files/derivative/evidence handoff reaches the authorized
  consumer chat; independently reported acceptance remains distinguishable.

## Out of Scope

Paid OCR/models, secrets, source text correction, guessed semantic references,
source-pixel reconstruction, universal format/model promotion, other projects or
chats and modification of frozen Story250 runtime. The original no-landing
restriction was superseded by the direct human finish-and-push request on
2026-10-08; scoped commit and landing are now authorized.
No new UI: structural HTML, reports and CLI/driver artifacts provide inspection.

## Approach Evaluation

- Single language/VLM call: retained current conversion already supplies a paid
  parent baseline with explicit suppression errors. New calls are unauthorized;
  no conclusion about general model incapability follows.
- Decision model: could classify importance or rank candidates but cannot create
  absent source pixels or establish native identity. No provider use enabled.
- Hybrid: retained model outputs plus deterministic native occurrence evidence
  and explicit inclusion policy. Selected for the new opt-in repair boundary.
- Code: exact title/DOM joins, PDF occurrence geometry, verified raster mapping,
  crop/receipt generation and link mutation are appropriate deterministic work.
  Association remains a bounded spatial policy with conservative abstention,
  followed by manual verification, not proof by confidence score alone.

## Tasks

- [x] Fetch current main; isolate work; read Ideal/spec/state/graph/coverage/ADRs.
- [x] Read fixture brief, hash all303 files and inspect initial source/output.
- [x] Diagnose omission/URL/TOC classes and inspect reusable native PDF substrate.
- [x] Implement separate opt-in native occurrence supplement with safeguards.
- [x] Attach retained/recovered catalog figures to unique headings/table cells.
- [x] Repair line-break URL tokenization and source-supported TOC row binding.
- [x] Add synthetic positive/refusal tests and preservation checks.
- [x] Regenerate through driver offline; inspect source/output and correct issues.
- [x] Write correction report, producer pins, operator docs and consumer handoff.
- [x] Reassess coverage/state honestly without broadening maintained claims.
- [x] T0: native occurrence, raw source page, crop and target provenance verified.
- [x] T1/T2: retained paid baseline reused; no unapproved model calls.
- [x] T3: source pixels, literal wording, ordered blocks and originals preserved.
- [x] T4: generic recipes and policy, no document-specific runtime conditions.
- [x] T5: personally inspect all recovered examples and rendered destinations.

## Workflow Gates

- [x] Build complete
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via /mark-story-done

## Architectural Fit

spec:3/4/6 substrate exists; spec:7 partial. C3/C4/C5 remain active; this bounded
native PDF supplement does not delete crop compromises. Born-digital coverage
is passing only for maintained book-like/flat fixtures, not arbitrary designed
manuals. ADR-001 requires explicit policy/artifact evidence; ADR-002 owns the
structural bundle and block provenance. No new ownership decision is needed.

Verified substrate: PyMuPDF native image occurrences and text lines; physical
page raster and exact left/right splits; existing crop manifest; retained raw
page labels; normalized page HTML and portions; source-backed local reference
index; generic driver artifact loader and chapter builder. Native labels and
image candidates exist for all20 uncropped occurrences. Missing/unproven cases
in other documents remain held, not silently routed to heuristic repair.

## Files to Modify

- New native occurrence recovery helper and transform module plus synthetic tests.
- modules/build/build_chapter_html_v1/main.py and figure-placement tests.
- doc_web/reference_resolution.py and URL boundary tests.
- modules/common/manual_navigation.py and TOC source-row tests.
- Offline replay recipe/tool and source-to-output proof artifacts/docs.
- Story, notes, generated methodology graph/index; schema metadata only if needed.

## Redundancy / Removal Targets

Do not fork the 6,000-line guided crop implementation or replace the local
reference resolver. A separate source-native supplement consumes and retains
existing evidence; existing crops keep their bytes. No replacement OCR route.

## Plan

1. URL lane: whitespace boundary for br with zero raw-source width, retaining
   opaque-node protection and accurate raw offsets. Exercise existing-anchor,
   mixed-inline and repeated-pass controls.
2. TOC lane: bind adjacent source title and destination cells with source row
   evidence; match full titles (case-equivalent only in this contract), use raw
   observed printed labels to disambiguate, and reuse semantics in final validation.
3. Figure lane: enumerate original native PDF image occurrences and title lines;
   require exact retained raster/split registration and unique bounded spatial
   association with an existing catalog label. Group nested occurrence layers,
   retain geometry/orientation/hash receipts, and crop existing page pixels.
   Keep supplements separate from immutable model manifests. Place table figures
   inside the matching label cell, preserve prose and suppress duplicate placement.
4. Root integration: first load retained artifacts into a fresh driver replay;
   then prepare a disjoint clone with the exact original graph as a prefix and
   append offline recovery/build/validation. Never resume the immutable parent. Compare initial text/order/provenance and manually inspect all
   restored assets, URL, TOC and neighboring retained pages. Publish readable
   correction/producer records and independent consumer handoff.

Authorization: delegated request explicitly says choose the approach and
validation, implement a reusable repair, and deliver an inspected derivative;
that authorizes this plan without an additional permission pause. No new
provider/dependency spend, source mutation or commit/push is inferred.
Workers: Sol high for bounded semantic diagnosis/implementation; root owns
source inspection, design decisions, integration and completion judgment.

## Work Log

20261007-2122 — Baseline/exploration: current main2f0df93 fetched; created isolated
fresh-manual-source-fidelity/doc-web worktree. Recorded303 fixture files totaling
455,792,284bytes in output/story251-inspection/fixture-input-receipt.json. Root
opened logical25/28/2 source images and initial chapter010 in the browser: page28
has all eight textual table rows but no card images; page25 contains six source
cards whose HTML renders duplicate text without figures. Existing p27/30 retain
figures. Three independent read-only packets identified planned-empty/decorative
suppression, missing table-cell attachment, br stream loss, and numeric-only TOC
resolution. Native PDF image occurrences/native text and exact split registration
provide an offline substrate; no paid calls or original changes made.

20261007-2154 — Offline integration and inspection: final current run
`output/runs/story251-fidelity-20261008-r4/` completed through driver (three retained
loads, native recovery, build). Comparison at
`output/story251-inspection/comparison-r4.json` passes 110 checks: all303 fixture
hashes equal; 103 original crop rows/encoded assets exact; all95 previously
exported figures retained, now123; 20 new native crops plus8 reused table crops;
539 ordered nonfigure source joins/quotes exact; complete ordered article text
equal after HTML whitespace normalization. Root opened restored crops for25/26/28/29,
source pages2/25/26/27/28/29/30/32, table placement and transcribed text in browser.
Clicked all16 final TOC links and inspected separate Australia/New Zealand links.
The enlarged Brakes and small native occurrence remain distinct. Native Checkpoints
overlap is held; no protected rectangle is expanded. Source artwork remains
source artwork, including original low-resolution microprint.

Runtime/proof records: `output/story251-inspection/producer-pin.json`,
`correction-report.md`, `browser-inspection.json`; generic operator instructions
at `docs/runbooks/native-manual-source-fidelity.md`. First preflight caught mixed
schema declaration; second attempt exposed loader out-param mismatch. First
completed run r3 preserved all graphics/text but held15 TOC targets because
builder prepared pages dropped spread identity. Preserving page_id, spread_side
and inferred-label flag in both chapter and fallback constructors resolves that
without weakening identity. New real builder controls cover both paths.

Applicable verification: 686 affected offline interface tests before metadata
passthrough; 291 builder/bundle/pipeline tests and376 navigation/reference tests
afterward; current scoped Ruff clean. Full suite is not claimed green: partial
run507passes/11failures/86errors, stopped before fresh-venv dependency-installing
cases. Most failures require a missing retained crop-safety fixture; one separate
unchanged crop-mask assertion failed. Detailed limits in test-receipt.json.
No paid inference or source edits. Native recovery and protected fallback have
synthetic positive/refusal controls. C3/C4/C5, Story226 and maintained format
coverage remain unchanged. Read-only strategic checkpoint recommended finishing
this inspected derivative and stopping technical iteration when clean.

20261007-2215 — Sampling and immutable continuation: measured all100 native image
occurrences across physical13/14/15 and all56 layers of the28 restored crops.
Retained5425x3625 over1302x870pt is exactly300ppi; maximum native axis sampling
is300.0000184ppi (0.01ppi floating-point tolerance). No rerender is needed. Eight
protected p28 rectangles fully contain inner artwork but retain only86.66-87.92%
of the larger outer shadow bounds. This proves rendered RGB sampling and pixel
fidelity, not original encoded streams, channels, masks or arbitrary clipping.
Full measurements and limits: output/story251-inspection/sampling-proof.json.

Added public prepare_native_manual_continuation.py and an append-only overlay.
The helper validates the parent's supplied recipe/plan/state, copies it to a
new disjoint run, archives original snapshots/state, rebases only state artifact
paths, and prints the existing driver start-from command. Original12 stages and
overrides remain an exact graph prefix. The new builder deliberately disables
reference/catalog normalization to preserve the inspected literal wording;
original build params remain untouched. Review caught destination/run-ID mismatch
with driver output-dir semantics; actual preparation caught macOS /tmp alias
rebasing. Both fixed with regression controls before any real stage ran.

Real clone output/runs/story251-continuation-20261008-r1 completed appended
recover/build/validate with no original stage execution. All116 comparison checks
pass, including original stage metadata/paid timestamps, archived snapshots,
original stage and HTML bytes, and event-log prefix. Its123 image assets and all12
HTML files are byte-identical to r4; native inventory differs only in run_id.
That equality carries the complete r4 browser/sampling evidence; root additionally
opened the cloned TOC, clicked Special Programming Cards and inspected Energy
Routine and its unchanged duplicate transcription. Semantic validation has23pass,
1warn,0fail: the existing validator lacks TOC source-row provenance and reports
2 unmeasured numeric-label ambiguities. The builder's provenance-aware report and
actual16 browser targets are clean. No warning was suppressed.

Final continuation helper12tests and make lint pass; applicable earlier tests
remain as recorded. Independent consumer reviewers reported all r4 fidelity gates
accepted, with independent fitz/pdfimages sampling corroboration and no scoped
defect. The final continuation/proof handoff was delivered to the authorized consumer chat;
final clone acceptance remains separate from its reported r4 acceptance. Story250
is already Done and verified on origin/main2f0df93; Story251 remains local under
its separate no-landing instruction while the pending human clarification stands.

20261007-2220 — Delivered final pinned clone to authorized source chat
01a11869-d9b1-75c0-8cb3-b49e3478593a. Producer pin SHA256
ba907f68c8ab386e90662563480fb99fc148b25eb7977a4e7047350be953335d;
proof manifest SHA256
3a6550823929821d8284bbe8494cda578463c2f8a230dc0e4dcf6a793b2e3e0d;
runtime closure SHA256
85cfb5cdcd249eb67418658363c6a17282a72719eee06e088fe1b4a965bcc04a.
Handoff includes commands, exact parent/clone paths, sampling limits, retained
validator warning and incomplete full-suite evidence. No further technical
iteration is planned absent a scoped defect. Final independent clone acceptance
and no-landing clarification remain open; no commit/push or Done claim added.

### Fresh navigation validator continuation (2026-10-08)

Scope: same TOC/source-row module and artifact validation boundary, so this is a
bounded continuation of Story251 rather than a new behavior-class story. Source
consumer explicitly authorized implementation, generic tests and offline delivery;
no commit, push, conversion or paid calls. Only the newly supplied navigation
packet and its same-run supplement are reproduction inputs. Prior accepted
runtime changes are retained; prior delivery artifacts remain historical pins.

Baseline: the new packet reproduces exactly two source_heading_target_mismatch
issues for valid numeric table-cell anchors. The validator build_report calls
inspect_navigation with source pages but omits source_entries and provenance_rows.
The existing _TocNavigation evidence path therefore cannot engage, and numeric
labels collide with unrelated numbered headings. Source table title, href target
and block provenance agree. No href or document content needs changing.

Ideal/spec fit: faithful structural/provenance validation, spec:3.1/6/7; source
structure substrate exists and graduation remains partial. ADR-001's explicit
source evidence and ADR-002's structural bundle contract apply. No schema,
architecture, maintained coverage or compromise movement. Deterministic context
plumbing reuses exact authored title/page/provenance rules; a decision/LLM model
would add unneeded uncertain inference to evidence already present. No new model
comparison or provider documentation is needed because no model is adopted.

Plan (authorized by the explicit implement-and-test request): load existing
bundle block provenance before navigation inspection; reconstruct per-chapter
source entries from declared source_pages and normalized source rows; pass both
through the existing inspector. Do not weaken any inspector rules or alter HTML.
Add end-to-end build_report controls for valid same/cross-file TOC destinations,
wrong existing targets, missing/duplicate fragments, ambiguous source titles or
labels and missing evidence. Revalidate the exact new candidate standalone and
through a validator-only driver recipe with fail_on_blocking enabled. Compare
all input hashes and each unaffected conformance check. A bounded independent
review will inspect the final diff. Only validator, new regression tests and
story/notes/generated planning records should change from the preserved dirty
baseline. Capture the incremental patch and exact runtime/report identity.

- [x] Navigation continuation build and generic regression controls complete.
- [x] Exact new candidate standalone and driver validation pass appropriately.
- [x] All candidate/failed-report input hashes unchanged; handoff delivered.

Luna high performed the bounded read-only packet/hash audit to save context;
root owns semantic correction. Parent supplied a separate complete supplement
when the first packet lacked validator upstream inputs; no placeholders or
inherited unrerun checks are used as fresh full-validation proof.

20261008 — New candidate validation result: baseline standalone exit1 with23pass,
0warn,1fail and the exact two false heading mismatches. After the caller-only
context correction, standalone and real validator-only driver both exit0 with
24pass/0warn/0fail. Their24check records are identical; only local_navigation_targets
changed from baseline. All302 complete supplement files and128 small-packet files
remain exact to before hashes. Original failed reports and every source/output
artifact were preserved. Driver artifact:
output/runs/story251-navigation-validation-20261008-r1/01_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json.
Root inspected the new source witness, actual href/heading pairs and8 report
checks, including both navigation checks and source coverage/crop evidence.

Runtime delta is only13added/3removed lines in the semantic validator; no change
to manual_navigation.py or the earlier dirty source-fidelity runtime. Eleven
new generic tests pass;196 affected interface tests pass; make lint passes.
Sol high independent review found no concrete defect. Missing files/fragments,
duplicate fragments, wrong same/cross-file targets, ambiguous evidence,
missing/inconsistent row provenance and ordinary numeric semantics remain
fail-closed. The correction reuses exact source evidence, not new intelligence.
The initial validator-only driver preflight required a top-level source input;
the corrected recipe declares this packet's PDF without running conversion.
No pipeline stage executed during the preflight failure.

Exact commands, source delta, copies, full conservative runtime pin and input
preservation receipts live under output/story251-navigation-validation-20261008/.
See handoff.md and incremental-code.patch. Full repository suite not rerun for
this narrow validator change; relevant consumers and real driver verified.
Prior accepted delivery pins remain historical; this is a separately pinned
context-only update awaiting source consumer feedback. No commit or push.


20261008-0920 — Close-out and fresh positive overlay proof: direct human request
now authorizes finish-and-push. Public preparation correctly refused the first
redacted recipe path; the next transport passed preparation but recovery held all
pages because recipe and physical manifest selected different PDF paths. Neither
failure was treated as positive recovery or repaired by weakening source identity.
The consumer supplied a separate coherent v2 transport; all303 file hashes were
verified before/after and all118 existing output files match the fresh supplement.

The unchanged helper and runtime produced
output/runs/story251-navigation-overlay-20261008-r2/ with only three appended
recover/build/validate stages. It restores20 source-pixel crops, preserves all103
original crop records/assets and old image occurrences, and exports123 images.
All11 chapters preserve ordered article wording; all557 ordered nonfigure
provenance records survive. Fresh conformance24pass/0warn/0fail; navigation35
comprises the original16,17 source-page citations and2 literal URLs under the
existing overlay's explicit resolve_references option. Its598 held decisions and
unassociated groups remain visible; this is no all-image coverage claim.

Independent geometry/sampling proof measures40 layers of the20 new crops with
zero undersampled layers; source/recovery/export pixels and protected records
are exact. Root opened fresh source logical25/28, all20 recovered crops, the
rendered Special Programming Cards table, and clicked numeric2/3 to the correct
THE FIRST TIME YOU PLAY/SET UP headings. ENERGY ROUTINE and SANDBOX ROUTINE
retain their card text and rules beside the images. Independent Sol high review
found no scoped adoption blocker and corroborated all17 new page destinations.
Proof: output/story251-navigation-validation-20261008/overlay-proof-r2.json,
overlay-sampling-r2.json and overlay-producer-pin-r2.json. All earlier failed
reports, packets and no-op overlay remain intact.

Refreshed711 affected offline tests pass with5 dependency deprecation warnings;
make lint passes. closeout-test-receipt.json records commands, environment,
exact test hashes and current424-file runtime closure. This supersedes ambiguous
reuse of the pre-metadata builder test receipt. The full repository suite was not
rerun; earlier missing-fixture/separate-mask failures stay explicitly recorded.
No provider evaluation was performed, so eval registry is unchanged. ADR-001 and
ADR-002 remain ACCEPTED; their broader graduation/review follow-ups, compromises
and maintained format coverage are not closed by this bounded result.


20261008-0925 — Delivery closure: the consumer's requested three-file validator
archive exposed a missing doc_web.reference_resolution dependency. Preserved that
failed archive and supplied validator-standalone-delivery/ with six exact source
files and complete hash inventory. Isolated python -I execution restricts all
project import and namespace origins to the archive, uses only installed third-
party dependencies, and reproduces all24 conformance check records exactly.
Manifest b4fac6b86f7a64f964a1b0883fbb99e9830b0d542be9f55cc6416e80f1876d00.
Root reviewed the launcher and origin proof; sealed archive and full positive
run/pixel/navigation proof were sent to the authorized consumer before landing.
The source archive correction changes packaging only, not runtime semantics.


20261008-0925 — /mark-story-done under /finish-and-push: all11 acceptance criteria,
all15 task/tenet checks and three workflow gates are satisfied. Dependencies243
and250 are Done. Applicable current evidence is711 affected tests, make lint,
fresh validator-only and recover/build/validate driver artifacts, complete source
preservation/pixel/sampling checks, personal rendered inspection, independent
review and both delivered archives. Changelog and generated graph/index updated.
Prior consumer r4 acceptance is recorded separately; downstream adoption of this
fresh supplemental delivery is consumer-owned and is not claimed by local proof.
No eval/default/model/coverage promotion. Recommendation: Close now; scoped
commit and origin/main landing authorized by the direct human request. Primary
checkout is clean and untouched; no inbox reconciliation is needed.
