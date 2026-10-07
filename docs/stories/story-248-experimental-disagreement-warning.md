---
title: "Experimental sidecar disagreement warning integration"
status: "Done"
priority: "Medium"
ideal_refs: ["Fidelity to Source", "Traceability"]
spec_refs: ["spec:2", "spec:5"]
adr_refs: ["ADR-001"]
depends_on: ["233", "234"]
category_refs: ["spec:2", "spec:5"]
compromise_refs: ["C7"]
input_coverage_refs: []
architecture_domains: ["document-consistency"]
roadmap_tags: ["model-evaluation"]
---
# Story248 — Experimental disagreement warning

User approved integrating the Attempt066 offline rule into default-off sidecar,
with offline regressions; no newpaidcalls or activation. Preserve prior saved
model answers and canonical authority. ADR001 remains accepted, no repair change.

- [x] Carry necessary experimental substrate into new isolated worktree.
- [x] Integrate lowconfidence disagreement as advisoryreview warning, unchanged.8.
- [x] Retain existing guards, agreementfallback and authoritative labels.
- [x] Verify original savedresponse replay and warning; nativeanswers unchanged.
- [x] Run realdriver mocked on/off proof and inspect sidecar/canonical artifacts.
- [x] Update eval records and validate focused tests/lint/methodology.

## Workflow Gates

- [x] Build complete
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via /mark-story-done

## Work log — 2026-10-06

62focusedtests pass, scopedRuff passes. Savedreplay verifies10receipts/2answers/
4canonicalhashes; realdriver mocked warning appears with canonicalhashes identical
to sidecaroff. Artifacts output/runs/pplx-warning-integration-20261006/
offline-warning-integration/03_plan_onward_document_consistency_v1 inspected.

Tenets: source and answers unchanged; warning provenance explicit; canonical
policy/repair untouched; evalfirst via savedresponse+realdriver proof. Dependencies
233/234 Done. Evalregistry Attempt067 records integration only, no fresh quality.
No unresolved approved tasks. No providerkeys/.env, no newcalls/spend, no default,
deployment, commits or pushes. Remains disabled; fresh independent evidence needed
before adoption. Report docs/evals/evidence/067-warning-integration/report.md.
Landing via /finish-and-push requires separate request.

Closure:6tasks/3workflowgates complete, dependencies/ADR checked, tenets/evalrecords and proportional validation verified. Approved integration complete; no remaining authorized work.
