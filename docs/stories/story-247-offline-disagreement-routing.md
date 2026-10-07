---
title: "Offline disagreement-to-review routing test"
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
# Story247 — Offline disagreement routing

User approved test only after separate Story246/Attempt065 safety stop. Use
saved synthetic outputs, no new provider calls, credential use or runtime changes.
Keep original paid evidence immutable. ADR001 remains accepted; document planning
and repair authority do not change. Test a pure advisory transformation preserving
valid low-confidence disagreements as review warnings at unchanged.8threshold.

- [x] Copy and verify nonsecret saved evidence with source/hashes/sizes.
- [x] Reproduce original frozen sidecar exactly using original native receipts.
- [x] Compare proposed review warning policy, retaining canonical artifacts/golds.
- [x] Test agreement, threshold, invalid/skipped/failure and reverse-disagreement boundaries.
- [x] Record exploratory outcome, review burden, unchanged exact accuracy and limits.
- [x] Update eval registry and owner evidence; preserve defaults and zero spend.

## Workflow Gates

- [x] Build complete
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via /mark-story-done

## Work log — 2026-10-06

Saved three-chapter screen: falseclean1→0, review0→1, exact labels2/3unchanged.
A review warning preserves the correct Decider birthyear concern without accepting
its low-confidence verdict. Native outputs are unchanged; this is post-hoc policy
analysis, not fresh independent safety or calibrated accuracy evidence.

16focused tests and exactsavedresponse replay pass, scoped Ruff passes. Original
paid adapter/receipts replayed,4canonicalhashes unchanged. Pure offline tooling
changes only, so no new runtime driver/pipeline suite or provider run is warranted.
Tenet verification: source truth unchanged; traceable evidence; original policy
and paid results preserved; non-authoritative review warning. Dependencies233/234
Done; ADR001 remains unchanged. No unresolved work in the approved offline test.

Evidence docs/evals/evidence/066-offline-disagreement/report.md. Recommended next
step: separately approved default-off sidecar integration; fresh held-out evidence
required before adoption. No commits/pushes; /finish-and-push requires a request.

Closure: approved offline evaluation complete; all6tasks/3workflowgates and tenets verified, registry updated, proportional checks pass. No outstanding authorized work.
