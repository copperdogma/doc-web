---
title: "Related-document reference resolution"
status: "Done"
priority: "High"
ideal_refs: ["req:5", "req:6", "req:7"]
spec_refs: ["spec:3.1", "spec:6", "spec:7"]
adr_refs: ["ADR-002"]
depends_on: ["243"]
category_refs: ["spec:3", "spec:6", "spec:7"]
compromise_refs: []
input_coverage_refs: ["scanned-pdf-prose", "born-digital-pdf", "docx"]
architecture_domains: ["document_structure_and_consistency", "doc_web_runtime"]
roadmap_tags: []
legacy_system: ""
---

# Story 250 — Related-document reference resolution

**Priority**: High
**Status**: Done
**Decision Refs**: ADR-002; docs/notes/related-document-references.md
**Depends On**: Story 243

## Goal

An explicit caller declaration groups separately converted Doc-web bundles for
optional, source-supported reference binding. Produce a portable derivative set
with relative links, unchanged source wording and provenance, and inspectable
abstentions without OCR or provider calls. Preserve normal document-local use.

New story requested by the user and warranted by the new cross-bundle identity,
publication and validation boundary. Story 243 remains the document-local policy.

## Eval Ladder Context

Ideal faithful navigable export → Story 243 local resolver → observed companion
references remain plain because their targets are outside document scope.
The child proof is offline exact occurrence-to-heading, abstention, preservation
and portable-copy controls, followed by independent consumer testing. This is
symbol binding over extracted structure, not a new model-capability evaluation.

## Acceptance Criteria

- [x] Explicit opt-in public CLI/Python contract for declared related bundles;
  existing default builds and document-local links remain useful and unchanged.
- [x] Unique source-backed heading identifiers at heading start or terminal
  parentheses resolve across members, including lettered subsections and inline
  citation markup. Generic identifiers; no document-specific rules or prefixes.
- [x] Missing, ambiguous, duplicate identity/DOM identifiers, unsupported scope,
  unrelated documents, mismatched evidence and declared edition conflicts never
  yield guessed links. Discoverable abstentions remain in a structured report.
- [x] Source text, source provenance, assets and valid existing local links
  survive. Original inputs are untouched. Output preserves member identity and
  reports input/output hashes and source/target evidence.
- [x] Copy the entire output set to a different root and independently resolve
  every generated relative href to its exact unique target. No original paths
  are needed at runtime.
- [x] Real offline driver execution in output/runs/, 5–10 manually checked report
  samples, rendered inspection and appropriate regression/security checks.
- [x] Public docs describe inputs, supported reference grammar, evidence and
  edition policy, output layout, repeat-use behavior and practical limits.
- [x] Deliver exact candidate/files/evidence to authorized consumer chat and
  address feedback; record consumer acceptance separately from build evidence.

## Out of Scope

Paid providers/OCR, source editing, fuzzy semantic references, inferred relatedness
or edition equivalence, downstream application code/contracts. Commits/pushes
were initially excluded; the subsequent finish-and-push request authorized landing.
No new GUI: CLI, portable HTML and reports are the operator surface.

## Approach Evaluation

- AI-only or a decision model could interpret broader prose but cannot establish
  caller relationship authority or absent evidence. Not measured or rejected on
  quality; no paid inference authorized. Broader semantics are deferred.
- Hybrid retains exact code binding and adds optional judgments later only with
  a measured need and explicit enablement.
- Pure code selected for bounded explicit symbol/identity matching and portable
  artifact mutation, reusing existing DOM range, scope and URI helpers.
- Simplification baseline: original resolver is single-document by contract;
  two-bundle probe recorded zero companion links before changes in
  output/story250-baseline/baseline.json.
- Established practice: explicit Sphinx inventories and RFC3986 relative URI
  resolution; source evidence/uniqueness gates remain Doc-web responsibilities.

## Tasks

- [x] Verify current upstream, isolate work, read Ideal/spec/state/graph/coverage.
- [x] Inspect resolver, bundle/provenance schemas and public CLI; record design.
- [x] Record baseline; implement typed declaration/report and offline set copier.
- [x] Implement source-backed set resolution reusing existing DOM helpers.
- [x] Expose CLI and driver module; publish runtime contract and operator docs.
- [x] Positive/safety/portability tests, driver artifacts and visual inspection.
- [x] Applicable validation, work log and independent consumer handoff.
- [x] Reassess coverage/state truth; no new input-format graduation is claimed.
- [x] Check redundancy: no replacement for document-local policy or OCR paths.
- [x] T0: source/target evidence and digest chain verified.
- [x] T1/T2: bounded binding needs no paid intelligence; baseline recorded.
- [x] T3: exact text/provenance/original preservation verified.
- [x] T4: arbitrary related documents and identifiers verified.
- [x] T5: artifacts and rendered result inspected.

## Workflow Gates

- [x] Build complete
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via /mark-story-done

## Architectural Fit

Owner: doc_web public runtime and shared reference helpers. State/graph:
spec:3/spec:6 substrate exists; spec:7 partial. C3 remains climb, no model/default
or format-coverage promotion. Relevant PDF/DOCX rows already passing on bounded
fixtures. Verified DocWebBundleManifest, DocWebProvenanceBlock, CLI and final
HTML resolver; no related-set runtime existed. ADR-002 owns standalone structural
website/provenance boundary. New set envelope does not redefine a local bundle.

## Files to Modify

- schemas.py / doc_web runtime contract and CLI — versioned set interfaces.
- doc_web/related_documents.py — checked copy/publication and receipts.
- doc_web/related_navigation.py — scoped exact index and enrichment.
- modules/transform/resolve_document_set_v1/ — offline driver adapter.
- tests/test_related_documents.py and tests/test_related_navigation.py.
- docs/notes/related-document-references.md and public bundle contract.

## Redundancy / Removal Targets

Reuse reference_resolution DOM/scope/URI helpers; no duplicate local resolver,
consumer-specific adapters or OCR route. Existing local report is retained as
historical input evidence; set report owns the derivative operation.

## Plan

1. Validate explicit member declaration and ordinary bundle inputs, rejecting
   unsafe paths/symlinks/overlap and duplicate identities before output publication.
2. Index exact source-supported heading labels, report candidate provenance and
   conflicts, wrap only eligible citation text using existing range helpers.
3. Copy complete portable member artifacts to a fresh output, preserve provenance
   bytes, validate generated hrefs, write set inventory/report and digest receipts.
4. Wire CLI, driver adapter and machine-readable contract. Exercise offline
   positive/safety fixtures, current local regressions, real driver and copy proof.
5. Review semantics/security, inspect artifacts, then send concrete consumer
   handoff. Completed after explicit consumer acceptance and final driver proof.

Approval basis: explicit request to choose design and carry planning through
implementation/validation. No additional permission gate is inferred. One small parsing dependency, tinycss2 (>=1.3,<2), is declared for the driver
extra and requirements; it was already installed locally. It parses static CSS
URL dependencies instead of inventing a CSS parser. Existing local policy is untouched. Mechanical inventory
used gpt-6-luna high; bounded resolver implementation uses gpt-6.1-sol high with
root semantic review, per current runtime capabilities and task risk.

## Work Log

20261007 — Exploration/planning: fetched origin/main 3a7bc2c (primary checkout
19b30b1 was nine commits behind and clean). Created isolated managed worktree
related-document-references/doc-web. Verified human permission for bidirectional
consumer coordination. Read current schemas and reference helpers; source HTML
and block text_quote can support offline heading identity. Public set operation
copies bundles, does not reread source scans. Research and uncertainty in design
note. Candidate approach and input requirements sent to consumer before build.

20261007 — Review and coherent corrections: generic independent review found
legacy unclassified-file copying, masked anchor scope, postfix named qualifiers,
URI opacity, missing static resource checks and a manifest read race. Each is
addressed at the owning boundary with direct regression cases; no acceptance
criteria weakened. Related navigation and the shared reference helper
moved into the installed doc_web package so public resolve-set works outside a
source checkout. Existing local/benchmark imports updated; no compatibility shim.
The driver uses the same public operation. Full private consumer positive check
on v1 reported all six intended links, 44 chapters, 295 preserved existing article
hrefs, 8 figures and copied-set validation (2,396 assertions); refusal suite
reported 18/18 expected holds. This was preliminary v1 evidence; final v2 retest
and closure are recorded below.

20261007 — Final review and validation: fixed typed-prefixed postfix/list scope,
paragraph kind, isolated benchmark imports and resume directory collision from
independent review. Existing document-local policy retains its defaults. Fresh
consolidated affected suite: **650 passed in 38.45s** (including installed wheel
outside checkout, resolver/local consumers, benchmark snapshot and driver/resume).
`make lint` and artifact schema validation pass. Final source identities and all
checks/findings/limits are recorded in docs/notes/story250-validation.md. Full
`make test` was not run; the interrupted exploratory CLI environment sweep is
explicitly not claimed green. No paid eval or model score was produced; registry
updates are not applicable.

20261007 — Artifact inspection: fresh driver story250-related-final and actual
`--start-from references` resume complete. Current locator:
output/runs/story250-related-final/02_resolve_document_set_v1/related_set_result.json.
The new derivative is related-set-2d4e2cac48aa41c2a65a15f8d3483a89; original
related-set remains intact. Manually read all six positive report rows against
HTML/provenance (x501b → "x501b: Supply checks", x512 → "Movement rules (x512)",
x528 → "Weather checks (x528):", x503e → "x503e Encounters", x525 →
"Equipment (x525)", x519 → "x519: Final checks"). Source page/element joins,
raw offsets, text/emphasis, existing Contents anchor and assets agree. Final
report: six links, ten local hrefs, 12 static resources, zero issues/calls/cost.
Read two additional refusal samples: edition_conflict and duplicate_exact_targets
have null targets. Independent copy resolves every generated link.

20261007 — Consumer acceptance: authorized consumer chat explicitly accepted
all 12 unchanged public v2 pins. Its retained consumer-acceptance.json and
consumer-report.md (full paths in validation note) record 2,396 preservation/
portability checks, six exact destinations, 18 refusal controls, and bare
identifier boundaries. It clicked all six links in its actual browser on the
relocated output and inspected rendered heading/body. Its 60 originals, 44
article texts/ID sets, 295 existing hrefs and eight figures remain unchanged.
The direct owner instruction is "Link any exact heading identifier"; bare
identifiers are eligible under the same source/uniqueness/scope gates. The later
adapter-only resume fix leaves accepted public pins unchanged. No production
consumer adoption, package replacement or source-fidelity graduation is claimed.

20261007-1713 — /mark-story-done: 14/14 tasks, 8/8 acceptance criteria and T0–T5
verified; validation grade A for this bounded capability, no remaining story
gap. Dependency243 is Done. ADR-002 stays ACCEPTED; its broader extraction and
Dossier integration remaining work is unaffected. State/coverage claims stay
unchanged; generated graph/index and CHANGELOG updated. No commits/pushes.
Recommended next step, only when authorized: /finish-and-push.

20261007-1717 — Finish-and-push authorized by user after consumer acceptance.
Fetched origin/main still equals tested base3a7bc2c; all candidate/runtime/driver
pins match. Reuse 650 passing tests, driver/resume and consumer proof; only
landing documentation and generated records change. No primary/inbox or consumer
changes to reconcile. Land via codex/related-document-references to origin/main;
retain worktree/branch/artifacts. Commit/remote receipt recorded separately in
output/story250-handoff/landing-receipt.json after verified publication.
