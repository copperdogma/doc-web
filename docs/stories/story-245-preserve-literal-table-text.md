---
title: "Preserve literal table text through OCR and export"
status: "Done"
priority: "High"
ideal_refs: ["req:3", "req:5", "req:6", "req:7"]
spec_refs: ["spec:2.1", "spec:2.2", "spec:3.1", "spec:6"]
adr_refs: ["ADR-001", "ADR-002"]
depends_on: []
category_refs: ["spec:2", "spec:3", "spec:6"]
compromise_refs: ["C1", "C3", "C6"]
input_coverage_refs: ["scanned-pdf-tables", "born-digital-pdf"]
architecture_domains: ["ocr_and_extraction", "document_structure_and_consistency", "doc_web_runtime"]
roadmap_tags: ["source-fidelity"]
legacy_system: ""
---

# Story 245 — Preserve literal table text through OCR and export

**Priority**: High
**Status**: Done
**Relative effort**: M, subject to the bounded baseline comparison
**Decision Refs**: ADR-001; ADR-002; [source investigation](../notes/table-literal-fidelity-2026-10-06.md); document-consistency planning runbook
**Depends On**: None. Reuse Stories 128/140/170/226/243 without waiting for Story 226's broader visual qualification.

## Goal

Preserve literal table contents from source to final semantic HTML, including
unusual spellings, apparent source typos and lookalike characters. The reproduced
example is Star Smuggler physical/printed page 19, `r236 Equipment Table`:
`LSU: life support unit (r2l3)` becomes `LSU: life support unit (r213)` in the
first saved OCR artifact. Lowercase `l` must survive even if digit `1` would
make a plausible rule reference. Detect source disagreements and resolve them
with inspectable evidence, or report uncertainty explicitly.

The operator should receive faithful table text and an actionable source
location for unresolved cells. Existing HTML, provenance and quality-report
surfaces are sufficient; no separate UI is proposed.

## Eval Ladder Context

- **Root**: Ideal 3/5/6/7, accurate extraction through source-linked export. A
  fresh whole-book run is deferred until this bounded failure class is resolved;
  it would spend on unrelated pages without isolating the defect.
- **Parent**: Ingester's sealed F FINAL audit reports equipment rows 17/18 and
  numeric cells 84/84. This is external consumer evidence, not a new DocWeb
  corpus score. Local inspection independently confirms the LSU substitution
  in first OCR and final HTML; no complete package quality claim follows.
- **Existing child**: `onward-table-fidelity` and its cell-diff scorer offer
  reusable machinery, but their genealogy slice does not establish coverage
  for this literal reference-token failure.
- **Next child**: bounded literal-table fidelity eval comparing current OCR, a
  strongest practical single-call baseline, and qualified native evidence with
  targeted escalation only if needed. Freeze exact source goldens and separate
  confirmation material. After adoption, rerun the final-bundle/consumer slice,
  not merely the intermediate scorer.

## Acceptance Criteria

- [x] Preserve a reproducible source-bound case: source/recipe/runtime hashes,
  physical/logical/printed page, glyph/row location, OCR raw/cleaned HTML, later
  stages and final bundle. Separate earliest observed mutation from unproved
  model/raster causality.
- [x] Measure current and strongest practical single-call source reading before
  adding repair logic. Record served model, raster/crop parameters, prompt,
  calls, cost, latency and quality. Prefer the simplest approach meeting the
  fixed gate; one historical model miss does not establish AI incapability.
- [x] Final HTML preserves LSU `r2l3` and neighboring cell text/order. No global
  lookalike replacement, inferred intended reference, case folding or
  document-specific production rule is allowed.
- [x] Generic controls cover `l/1/I`, `O/0`, apparent source typos, case and
  punctuation, repeated values, empty versus dash cells, `1+`, row ownership
  and spans. Evaluate multiple documents with different fonts, layouts and
  subject matter, including native-text and image-only sources. Reserve an
  unseen document for confirmation after prompts, thresholds and repair policy
  are frozen; do not tune on its results. Include already-correct ordinary text
  and legitimate lookalike tokens to detect harmful corrections. Grade literal
  accuracy and structure separately; require zero known silent substitutions
  on the declared slice. A gain confined to Star Smuggler does not qualify.
- [x] Production prompts, detection and repair contain no fixture names, page
  IDs, expected tokens, game-specific reference syntax or hardcoded replacement
  pairs. Decisions use supplied source evidence and generic alignment/fidelity
  rules. An unusual token alone is not evidence that it needs correction.
- [x] If native text is used, qualify agreement with visible source and
  unambiguous row/cell mapping. Bind source digest, page/coordinate space,
  region, old/new text, reason and extraction/repair stage. Corrupt, hidden,
  stale, missing or conflicting text layers and ambiguous alignment must not
  silently overwrite OCR; use source-image review or explicit uncertainty.
- [x] If repair is needed, preserve initial OCR and emit a typed, inspectable
  disagreement/repair report. Permit only declared presentation-whitespace
  normalization, never glyph or wording normalization. Repair before final
  provenance, navigation and bundle sealing. Cap re-reads/retries/cost;
  unresolved cases cannot silently pass a fidelity-qualified result.
- [x] Reference resolution preserves corrected visible text. A source typo may
  remain unresolved; never turn `r2l3` back into `r213` to create a link.
  Existing valid references and provenance remain correct after rebuilding.
- [x] Real `driver.py` execution or qualified partial resume produces artifacts
  in `output/runs/`. Open 5–10 JSON/JSONL records, visually inspect source/output
  tables, verify final provenance and downstream consumption, and report exact
  artifact paths, examples and remaining limits.
- [x] Focused tests, applicable lint and methodology checks pass; `/improve-eval`,
  registry/attempt notes and coverage claims reflect measured truth.

## Out of Scope

Ingester correction APIs, repeated workspace snapshot optimization, package
publication, whole-manual layout repair, reference interpretation, global model
substitution, source errata editing and full format graduation. Ingester repair
remains useful but cannot replace producer fidelity. Existing group-header
geometry defects stay visible as non-regression context, not claimed fixed here.

## Approach Evaluation

- **Simplification baseline / AI-only**: a capable single call may preserve the
  glyphs. The historical recipe requested `gpt-5.1`, 2048px longest edge and
  8192 output tokens. Test model and raster choices without conflating changes.
- **Pure code / native extraction**: text plus coordinates can supply exact
  literals cheaply when qualified. Poppler extracted this row correctly.
  Geometry/encoding errors make blind replacement or wholesale routing unjustified.
- **Hybrid (recommended candidate, not selected)**: compare source-backed table
  text with OCR, use exact qualified witnesses, escalate ambiguous regions to a
  source-aware VLM and validate again. Avoid adding repair machinery if the
  single-call baseline clears the complete gate.
- **Decision model**: may rank enumerated textual disagreements later, but
  cannot establish a glyph in an image. Exact comparison, identities and
  mutation belong in code; visual transcription belongs to a source-aware
  model. No Jev/provider lane is needed for this first probe.
- **Reuse / constraints**: raw/cleaned page HTML, existing table scorer, targeted
  rescue reports, native PDF preview extraction, ADR-001 source-aware repair
  and ADR-002 bundle provenance. Never guess corrections from damaged HTML.
- **Eval discriminator**: exact case-sensitive cell content plus row/span
  ownership and independent source review. Numeric scores, schema success,
  model confidence or working links do not establish fidelity. Review existing
  scorer quote normalization/alignment before claiming exact-literal coverage.

## Tasks

- [x] Inspect Ideal/spec/state/graph/coverage, related stories and runtime.
- [x] Read active Ingester thread; reproduce source-to-OCR-to-final mismatch
  read-only; record research and local native-witness/scorer controls.
- [x] Freeze diagnostic evidence and create a minimally retained source fixture,
  goldens and a cross-document panel. Assign development and unseen confirmation
  roles before tuning, and include unchanged-text negative controls. Preserve
  source permissions; do not commit private documents by default.
- [x] Verify historical receipt/image-preparation lineage; run bounded current
  and strongest practical single-call baselines with explicit cost/retry caps.
- [x] Select the approach on quality/cost/latency. Extend the relevant ADR before
  build if persisted evidence authority or publication semantics change beyond
  ADR-001/002; do not invent a new framework for this one case.
- [x] Implement the selected producer fix and regressions. Add schema fields
  before cross-stage evidence would otherwise be dropped by driver stamping.
- [x] Clear affected stale Python caches; rebuild through driver, reusing
  scope-qualified upstream artifacts when OCR is unchanged. For OCR changes,
  rerun only the bounded affected pages.
- [x] Inspect source/output tables, 5–10 report records and final link/provenance
  behavior; obtain independent review of literal and structural outcomes.
- [x] Run `/improve-eval`; record actual attempts in `docs/evals/registry.yaml`.
- [x] Update coverage/state only to demonstrated reality; remove superseded
  paths if any. Run proportional tests/lint, `make check-size` when relevant,
  `make methodology-compile`, `make methodology-check`, `git diff --check`.
- [x] Verify T0 provenance, T1 appropriate AI/code division, T2 eval before build,
  T3 fidelity, T4 generic modularity and T5 visual/data inspection.

## Workflow Gates

- [x] Build complete
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via /mark-story-done

## Blocker Summary

N/A. User authorized story completion on 2026-10-06. Extraction, source artifacts,
provider credentials and fixture-generation dependencies are verified. The story
was promoted through Pending to In Progress; no external blocker is proven.

## Blocker Evidence

N/A.

## Unblock Condition

N/A.

## Architectural Fit

- State/graph `spec:2/3/6` substrate exists; C1/C3 remain `climb`, C6 `hold`.
  No compromise is deleted by this one case.
- `scanned-pdf-tables` is passing on bounded Onward evidence; `born-digital-pdf`
  is passing on four repo-owned fixtures. Star Smuggler has embedded text but
  this recipe rasterizes/OCRs it. Neither matrix claim proves literal accuracy
  here. Record this failure class without declaring all tables/native PDFs broken.
- A new story is justified by the **literal transcription validation boundary**.
  Story 226 owns graphics-heavy manual structure/pixels; Story 243 owns faithful
  reference enrichment; Stories 128/140 own historical genealogy verification/
  rescue. The defect precedes normalization/linking, so reopening crop or
  navigation work would misidentify its owner.
- Owner: extraction plus source-fidelity validation. `page_html_v1` has source,
  page, image, raw and cleaned HTML; no cell-level witness contract exists.
  Any new evidence must survive stamping and be discoverable downstream.
- ADR-001 constrains repair to source-aware work; ADR-002 owns bundle/provenance.
  No new top-level architecture is selected during planning.

## Files to Modify

Candidate surfaces; narrow after the baseline:

- `modules/extract/ocr_ai_gpt51_v1/main.py` (761 lines) and recipe parameters —
  extraction changes if selected; keep new logic out of the oversized entrypoint.
- `modules/adapter/table_rescue_html_loop_v1/main.py` (442 lines) — reuse only if
  needed. It did not run here; changing it alone would not fix this path.
- Small extraction/validation helper and focused tests if evidence requires it.
- `benchmarks/scorers/html_table_diff.py` (212 lines), bounded task/goldens,
  `docs/evals/registry.yaml` and attempt notes.
- `schemas.py` (2233 lines), metadata and recipe for selected typed evidence;
  builder (3761 lines) only if a small integration hook is necessary.
- This story, investigation note, relevant runbook and generated graph/index;
  coverage/state only when behavior warrants an update.

## Redundancy / Removal Targets

Avoid a parallel HTML patcher, second table scorer, game-specific token rules
and full-book re-OCR. Reuse source-rescue machinery where justified; remove
superseded branches only after equivalent evidence passes.

## Plan

User authorized completion of this story, including its genericity gates and
hourly loop-review; that authorization covers routine evaluation, implementation,
validation and mark-done. No further plan approval is needed inside this scope.

1. Freeze current OCR prompt/code and inputs before product edits. Dev roles:
   original Star page19, bounded reviewed Onward table region, two synthetic
   subjects/fonts. A separate unseen document is prepared by the fixture worker;
   parent will not open its expected content until policy/model freeze.
2. Prompt-first comparison: historical gpt-5.1 configuration versus the same
   model with generic literal-preservation instructions; compare strongest
   practical single-call gpt-6-astra against the same input. Explicitly retain
   spelling/case/punctuation and apparent errors, without fixture-specific tokens.
3. Initial experiment cap: 24 subject requests, 8 final rubric requests,
   $10 estimated conservative total; reserve before dispatch, max output8192,
   no SDK retry, bounded timeouts. Stop the phase on cap/transport failure or
   two non-improving strategies; reassess rather than accumulating repairs.
   Adoption requires zero known literal/ownership errors on the fixed declared
   panel and frozen unseen confirmation, no harmful changes to correct cells,
   compatible final links/provenance and reported cost/latency.
4. Review exact strings and row/span geometry without legacy quote folding or
   score averaging that hides a bad cell. Use source visual adjudication and
   final semantic rubric as well as deterministic checks. Register all attempts.
5. If prompt-only succeeds, adopt the generic prompt; do not build a witness
   framework. If not, compare qualified native context/targeted source rereading
   in a bounded next phase before implementation. Native disagreement cannot
   authorize a blind overwrite. Keep immutable originals and fail/flag uncertainty.
6. Existing sanitizer drops table rowspan/colspan attributes. Preserve validated
   positive span geometry if encountered by the panel; that is a small coupled
   fidelity fix, not whole-manual layout repair. Tests cover preserved cell text,
   unsafe attrs and structure, not prompt-string snapshots.
7. Run the smallest real driver path on source inputs to extraction and final
   HTML/provenance. Inspect emitted JSONL/HTML and source/output visuals. Freeze
   candidate before unseen grading; no retuning from confirmation answers.
8. Validate under proportional-check policy, update eval/runbook/coverage truth,
   invoke mark-story-done and update changelog. Keep all Git changes uncommitted.

Hourly strategy cadence starts 2026-10-06T20:13:36Z; first loop-review due
2026-10-06T21:13:36Z, then each hour anchored to that schedule. Carry deadlines
across interruptions. Earlier review if technique repeatedly fails. No automation
or separate task is created. A bounded corpus worker owns fixture generation;
parent owns prompt/runtime/scorer/integration and final decisions.

## Work Log

20261006-1353 — Planning: read active “Triage and complete project work” and
frozen artifacts. Confirmed native PDF `r2l3`, first OCR raw/cleaned `r213`,
unchanged downstream row and final auto-link. Read-only Poppler witness and
existing scorer controls demonstrate a detection route, not a repair. Created
Draft and investigation note; no runtime behavior changed. Luna lookup worker
was unavailable at capacity; Sol6.1 medium supplied bounded code/story evidence,
which the parent checked against the artifact chain.

Planning verification: `make methodology-compile`, `make methodology-check`
and `git diff --check` pass. Story 245 is unique and follows prior maximum 243;
graph/index include it as Draft. Independent read-only review found no planning
blockers. No implementation, provider eval, commit or push performed.

20261006 — User clarification: generic behavior is mandatory. Strengthened
acceptance with varied cross-document evidence, frozen unseen confirmation,
unchanged-text controls and an explicit prohibition on example-specific prompts,
syntax or replacements. Success on the reported example alone cannot qualify.

20261006-1418 — Build exploration/plan: completion goal created; user approval supersedes prior planning-only scope. Generic prompt-first baseline selected for first experiment, not for unconditional adoption. Current sanitizer loses span attributes; coupled fidelity fix may be required. Existing repo key will be reused under project instructions and authorized evaluation scope; no key creation/change. First hourly review due21:13:36Z.

### 2026-10-06 — Candidate development evidence

Autonomous `/improve-eval literal-table-fidelity` uses new Attempt 062. Current gpt5.1 and literal-prompt variants fail all three cases; Astra at2048passes Star/lab but misses transit; retained original200dpi still misses another transit glyph. One documented300dpi compositedPNG comparison clears all three raw/sanitized cases. Frozen target remains zero text/ownership errors on every admitted case; no golden weakening or favorable reruns. Root visually inspected source equipment/lab/transit tables, including blank Hypercharge CU and source typos. Existing shadow native text is never supplied to the model; no witness/repair framework needed so far. Scorer has40focused controls, product profiles have transport/identity/receipt controls, and sanitizer no longer drops safe spans or decodes literal entities into markup. Rendering gets a generic losslessPNG knob. NewOCRoptions are recipe-scoped; existing model defaults unchanged.

Selected profile before reserved confirmation: shared literalpolicy, Astra medium,300dpi compositedPNG, original detail, no localdownsampling,8192tokens, oneattempt, SDKretry0/180stimeout. Exactprompt hash b2560dfe4e5a031b7eea50523d8b3cfe7d2299a70f9d7e0b24809858f865c473. No newADR required: no native overwrite, evidence-authority contract orpublication change. Runtimeprofile stores requestreceipts and fails incomplete/wrong-served-model responses; legacychat fallback cannot bypass them. Narrow MIME propagation also preserves JPEG MIME when localresize changed PNGencoding.

Next: freeze all tested runtime/scorer/source identities; realdriver proofs of original sourcepage19, native lab and unseen image-only confirmation; reuse qualified transit OCR for finalexport. Four independent standardOpus4.6 semantic rubrics supplement exactsource-cell scorer. Total planned reservations remainUSD10, with16subjectcalls and4judges; transport/status errors are not qualityobservations. No headlinefull-book/native-extraction claim.

### 2026-10-06 — Independent confirmation and course correction

Frozen single-call candidate fails unseen image-only workshop by one character while preserving structure. Full extraction adoption is rejected; no prompt/golden tuning or favorable rerun. Phase2 source-only structured reread identifies three optical ambiguities covering the known error; transit source review clears8rows30cells. Original source review preserves correct equipment text but flags three l/I uncertainties. One padded complete-table reread leaves those unresolved; workshop crop has malformedJSON (raw retained), so no crop loop is adopted. Native font authority would require reconstruction beyond this slice: subset cmap is not Unicode, ToUnicode cannot validate itself, and painted/opaque or redaction-difference tests alone admit hidden/overlapping artifacts. Independent Astra review recommends the existing explicit-uncertainty branch rather than forcing source truth from ambiguous pixels.

Selected product is safe literal-fidelity handling, not universal exact OCR: one independent source-image-only inventory, exact complete initial/source cell and span agreement, zero reported uncertainty, typed bound report/receipt, enforced builder gate and portable final qualification. Otherwise retain originalOCR and emit a source-located hold before qualified export. Source-authored strings are not presented as visually recoverable in identical-glyph fonts. Original correct finalHTML and its unqualified status are demonstrated separately. No repairs or native overwrite are claimed; conditional native/repair ACs apply only when used. Clear native and image-only fresh cases must pass so refusal alone cannot close the story. Held cases remain transcription failures/coverage gaps in the eval, never counted as correct.

Narrow ADR001/002 extensions record report authority and export semantics before implementation. Optional typed PageHtml metadata survivesdriver stamping; builder checks receipt/report/source/image/raw/tablesequence identities and source-reading request lineage, then rechecks final tables after navigation. Production is B-only; rejected crop/native paths are not added as unused framework. The defaultrecipe declares a three-page batch (range configurable), eighttables, threereviewrequests andUSD4.50 review reservations plus initialOCR. Phase2 keeps16subject/fourjudge/USD15 experiment caps.

Verification sofar:120focused extraction/scorer/source-reader/parser tests pass. Related current/total printedpage defect fixed generically (`p.19/24`, `Page14/80`), barefractions stayunassigned; physicalpage19 is carried separately fromlogicalpage1 into finalprovenance. Scope-specific registry assessments retain previous OCR as partially qualified diagnostic input, not trusted faithful exports. Fresh independent panel remains sealed until candidatefreeze. First hourlyloopreview remainsdue21:13:36Z.

### 2026-10-06T21:15Z — Hourly loop-review

Aligned but at risk until clear unseen cases qualify. Reused source-backed alternative comparison (Tesseract confidence/alternatives; PyMuPDF native hidden/occluded hazards), whose assumptions still fit. Single-call adoption and crop resolution remain rejected. Continue B-only agreement/uncertainty gate; no font-authority framework or further retuning. Existing realdriver holds cover the known workshop error; original correct diagnostic finalHTML is explicitly unqualified. Next discriminator is clear native/image-only qualification plus identical-glyph hold under frozen candidate. Independent review found a postvalidation output-path collision; apply existing path-separation guard beforefreeze. First hourly checkpoint was two minutes late following context recovery; next remains22:13:36Z. No additional authorization or scope change. Detailed four-question review is in Attempt 062.

### 2026-10-06 — Build and independent confirmation complete

The selected behavior is an opt-in, generic literal-table lane. It preserves
initial OCR, asks one independent reader to inventory and transcribe tables from
page pixels alone, and requires exact text and span agreement with no reported
uncertainty. Disagreements and ambiguous cells produce typed, source-located
holds before qualified export. The builder checks report, request, source,
page and final table identities and copies portable qualification evidence.
There are no native replacements, inferred references or document-specific rules.

The frozen fresh panel passed its safe-handling contract: native library
13/13 cells and image-only bakery 23/23 cells qualified; an identical-glyph
warehouse document retained one initial transcription error, flagged both
ambiguous cells and published no bundle. This is 2/3 exact transcription and
2/3 accepted coverage, separately from 3/3 safe disposition. The literal eval's
1.0 transcription target remains unmet. Four independent Opus rubrics and an
Astra artifact audit passed without relaxing exactness. The previously rejected
single-call workshop confirmation remains a failure. No prompt or golden was
retuned after confirmation.

Original equipment final HTML is exact across 19 rows/57 cells, including
`LSU: life support unit (r2l3)`, adjacent `r211b`/`r213`, `1+`, blank Hypercharge
CU and Commercial Vehicle inside Ship's Boat notes. This output is explicitly
an unqualified diagnostic: the production gate separately holds three optical
uncertainties. The known workshop error is also covered by a source-located
hold. Native-authority and repair ACs are conditional and not exercised; their
safe alternative is the implemented uncertainty branch. No claim of resolving
all ambiguous encodings follows.

Inspected artifacts:

- `output/runs/story244-star-unqualified-current/output/html/chapter-001.html`:
  ten equipment rows manually read, source and final table visually inspected;
  logical page 1, original physical page 19 and printed page 19 remain distinct.
- `output/runs/story244-native-positive-v2/output/html/chapter-001.html` and
  `output/runs/story244-image-positive-v2/output/html/chapter-001.html`:
  all 11 table rows and source renders visually inspected; literal examples
  `cataloge`, `recieve`, `Il1-O0`, `o0-LI`, case, quotes, blanks/dashes and spans.
- Each qualified run's `output/html/provenance/literal-fidelity/qualification.json`,
  page report, manifest, page JSONL and provenance records were opened. Every
  portable report and final entry hash matches; schemas validate.
- `output/runs/story244-ambiguity-negative-v2/03_literal_table_review_v1/pages_html_reviewed_reports/row-00000-page-00001-original-00001.json`:
  rows 1/2, cell 1 identify I/l uncertainty; original HTML/raw are unchanged and
  no manifest exists. Original/workshop held reports retain their historical
  candidate identities rather than receiving manual artifact edits.

The corpus is retained at `testdata/literal-table-fidelity/confirmation-v2/` as
exposed regression material. A conflicting hidden layer has identical visible
pixels; offline payload checks demonstrate that native text cannot enter the
reader. No format matrix, compromise status or whole-book claim was promoted.
ADRs 001/002 now describe the narrow evidence and publication contract.

Validation exposed and fixed caption/line-boundary comparison loss, a
receipt-only provider bypass and a literal-only publication path collision.
Restoring one exact ignored historical response fixture exposed three crop
prerequisite-order regressions; moving the existing check before input discovery
restores all 120 crop tests. The change affects no reading policy or literal
comparison. All 236 gate/build/bundle tests pass. Final builder-only driver
resumes reuse frozen requests, preserve the original bundles, and reproduce
byte-identical HTML for both qualified cases and the original diagnostic. The
first two resume preflights omitted the source argument and stopped before
execution; corrected invocations include the same PDF identity. No paid read
was repeated. `candidate-validation-addendum.json` records the isolated delta;
`current-builder-rebuild-proof.json` binds the current artifact evidence.

Attempt 062 and the eval registry retain every rejected strategy and measured
result. Subject/judge token estimates total USD3.21745 across 33 unique calls;
phase reservations of USD9.40/14.90 are separate. Fresh initial-plus-review
request sums are 13.2–19.7 seconds and USD0.235–0.250 per page. Five early probes
lack latency records; no full-pipeline speed improvement is claimed.

## Central Tenet Verification

- [x] T0: Typed source/request/page/report hashes and final portable provenance.
- [x] T1: Visual interpretation in the model; exact checks, budgets and mutation
  authority in deterministic orchestration.
- [x] T2: Current and strongest single-call evaluations preceded the gate build;
  independent confirmation rejected the first candidate.
- [x] T3: Literal preservation and explicit uncertainty; no inferred errata or
  silent replacement, and held errors remain transcription failures.
- [x] T4: Generic recipe/module parameters and class-based comparison controls;
  no game strings, page IDs or replacement pairs in production.
- [x] T5: Real driver artifacts, manual JSON/HTML inspection, source and final
  browser inspection, exact scoring and independent review.

Documentation is updated in the runbook, ADRs, research note, Attempt 062 and
registry. No Ingester changes, messages, global model changes, commits or pushes.

### 2026-10-06T21:28Z — /validate and /mark-story-done

Validation recommendation: **Close now** for the implemented uncertainty-aware
scope. All ten acceptance criteria are met (two native/repair criteria are
conditional; no such authority or mutation is used), all tasks and T0–T5 are
verified, and no implementation gap remains within this story. Detailed graded
validation and accepted findings are in
`docs/notes/story244-validation-2026-10-06.md`. ADRs 001/002 remain ACCEPTED;
no unrelated remaining ADR work is claimed resolved.

Current fresh broad rerun: **1,639 passed, one skipped**, five name-filtered
checks and the unchanged 12-test package CLI file excluded. The filter also
matched two passing transport checks; they were separately rerun and pass.
The three existing order-sensitive guard checks pass in isolation. Thus 1,644
current applicable checks pass, with ten previously passing unchanged package
CLI checks reused. Lint, changed eval/schema tooling lint, size and diff checks
pass. Final methodology compile/check follows the Done status update.

The original unfiltered `make test` result is retained, not called green:
17 failures/86 setup errors. Ten failures and 86 errors arose from the exact
missing historical fixture and are resolved by restoring its verified bytes;
all 120 affected crop checks pass. Two literal CLI failures occurred while the
old in-process comparator and newly edited subprocess comparator differed;
the current 236 gate/build/bundle checks and fresh broad run pass. The remaining
five baseline failures are outside this patch: three HTTPX wrapper isolation
failures in unchanged benchmark tests (all pass alone), and two unchanged
requirements installers failing the pikepdf10.16.0 native build against the
local QPDF API. These limits remain explicit; no assertions or goldens were
weakened and no dependency upgrade is hidden in this story.

`CHANGELOG.md` has one Story 245 entry. Coverage/state were inspected and retain
existing format/compromise claims. Synthetic confirmation material is now
exposed regression evidence. The hourly review was completed at21:15Z for the
21:13:36Z checkpoint; closure precedes the next22:13:36Z checkpoint, so no
further active-work review or recurring automation is needed. Temporary browser
and localhost servers are closed. No commit or push performed.

**Story marked Done via /mark-story-done.** `/finish-and-push` is the recommended
next step if the user later authorizes landing.

### Authorized landing integration

Remote main concurrently allocated Story244 and Attempt060; this work is
renumbered Story245/Attempt062 while preserving historical run/evidence paths.
Merged reference-resolution consumer checks pass (543 focused checks), and
both qualified driver rebuilds retain byte-identical frozen HTML and valid
portable hashes. The Mistral provider merge retains the OpenAI-only literal
receipt guard with two new controls. Close-out review is recorded in the
existing validation note; paid confirmations and quality claims are unchanged.
