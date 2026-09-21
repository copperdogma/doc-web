---
title: "JEV consistency shadow routing"
status: "Done"
priority: "Medium"
ideal_refs: ["Fidelity to Source", "Traceability"]
spec_refs: ["spec:2", "spec:5", "C7"]
adr_refs: ["ADR-001"]
depends_on: ["233"]
category_refs: ["spec:2", "spec:5"]
compromise_refs: ["C7"]
input_coverage_refs: []
architecture_domains: ["document-consistency"]
roadmap_tags: ["model-integration"]
legacy_system: ""
---

# Story 234 — JEV consistency shadow routing

**Status**: Done

## Goal
Make the measured JEV+fallback triage observable beside the real planner without
changing authoritative outputs or repairs. Story233 is complete frozen evaluation;
this new story owns the separate runtime integration and pipeline verification.

## Plan
Hook after authoritative planner outputs are written. Default-off environment
opt-in and distinct owner runtime key. Reuse the already-computed authoritative
planner result as low-confidence/error fallback; shadow adds no second GPT call.
Preserve explicit uncertain independently of confidence and deterministic layout
flags. Write a separate privacy-minimized sidecar with ordinal chapter references,
labels, generic reason codes, known/unknown usage and cost. Send only bounded
compact extracted-HTML evidence and the matching document-local conventions;
never send existing AI status/repair reasons or filesystem paths. This is not
independent original-source verification, unlike synthetic source prose in Story233.

Pin jev-1.13.0, exact native Choice contract, no redirects or retries,2s caller deadline plus socket timeout,16KiB state cap,64KiB response cap, max3chapters/run and conservative
$0.008064 total reservation. Any provider/parse/output failure leaves saved
planner outputs intact. No private/live inference, key provisioning, deployment,
commits or broad model rerun. Existing user instruction approves this scope.

## Acceptance Criteria
- [x] Explicit default-off opt-in; eval key cannot activate runtime.
- [x] Strict native adapter with bounded input/response/time/cost; redacted diagnostics.
- [x] Existing authoritative artifacts invariant; uncertainty and layout guards retained.
- [x] Meaningful offline tests and synthetic driver pipeline artifacts inspected.
- [x] Independent implementation review and setup/limitations documented.

## Tasks
- [x] Implement shadow adapter/policy and planner hook.
- [x] Add provider-free transport, policy, main/driver integration verification.
- [x] Document owner environment, private payload transfer and failure behavior.

## Workflow Gates
- [x] Build complete
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via /mark-story-done

## Work Log
2026-09-21 — Read owner AGENTS/build-story, ADR001, graph/state, planner and
Story233. Actual source seam exists after build_outputs/main sidecar persistence.
Conformance output normalizes AI status against deterministic suggested issue types;
shadow must not replace that logic. Runtime has extracted HTML profiles, not the
independent source prose used in evaluation. Reuse matched conventions, disclose
this evidence limitation, and leave authoritative outputs intact. Files: new
modules/validate/.../jev_shadow.py, main.py hook, tests, runbook, story/graph.

2026-09-21 — Implementation complete, independent final review pending. Added
exact native Choice transport and default-off post-planner hook. Explicit uncertain
preserved, low-confidence/errors reuse current authoritative planner, layout veto
prevents false-clean shadow clearance. No extra GPT call. Sidecar is atomically
replaced after deleting its stale predecessor; content binds input/plan/authoritative
digests plus run/time. Detached request state cannot mutate planner structures.
Two-second caller wall deadline uses a single daemon-owned request; timeout means
unknown delivery/reservation with no late result applied and no retries. Maximum
three attempts and $0.008064 reserved per invocation; diagnostics disclose coverage.

Verification:26affected tests passed (21newshadow,5existingplanner), targeted Ruff
passed, whitespace clean. Real `driver.py` synthetic mocked-provider verification
passed disabled/enabled/failure modes at output/runs/story234-jev-shadow-verification-r4.
All primary report rows plus three authoritative sidecars were invariant excluding
run/time metadata. Manually inspected: enabled low-confidence uncertain=.1 routes
to review while authoritative status stays conformant; failed provider preserves
authoritative status with$0.002688 unknown reservation. Zero real provider calls.
Initial verifier attempt lacked a required top-level driver input; corrected by
passing synthetic input HTML, preserving failed output for traceability. Current
verifier is rerunnable into a fresh path. No changes to prior222Story233 artifacts.

## Central Tenets
- [x] T0: shadow input/plan hashes, run/time, ordinal provenance; no payload logs.
- [x] T1/T2: builds on measured narrow Story233 outcome, not vendor capability claims.
- [x] T3: original authoritative artifacts remain unchanged; layout checks retained.
- [x] T4: opt-in module hook with environment boundary; no source-specific hardcoding.
- [x] T5: actual pipeline outputs and enabled/failure sidecars inspected.

2026-09-21 — Formal validation and closure authorized within the implementation
goal. Independent docweb_shadow_review returned CLEAR with no unresolved material
findings; rechecked26tests/Ruff/whitespace and r4 driver artifacts, including dossier
and four authoritative outputs invariant modulo run/time. Reused these exact-source
checks for formal validation rather than repeating broad unrelated suites. All5
acceptance criteria and3tasks met; central tenets checked. Separate codex review
CLI omitted because independent findings-first agent review covered the exact
transport/runtime/test diff. No remaining implementation gaps. Story234 closed
via mark-story-done; metadata/index/CHANGELOG updated. Implemented and validated,
not live-enabled, provisioned, deployed, committed or landed.


### Native synthetic observation — 2026-09-21

After Cam supplied the dedicated runtime key, one native runtime-seam request
completed in303ms forUS$0.000044268. JEV returned conformant with0.70 confidence;
configured routing correctly reused the planner on low confidence. All five
existing authoritative JSON artifacts retained their byte hashes. Retained
report and verification: `docs/evals/artifacts/story234-jev-shadow/live-synthetic-observation-01/`.
No private document, extra GPT call or persistent activation. This is a transport
and policy observation, not a production-quality comparison. Existing full-driver
mock integration evidence remains applicable; runtime source did not change.

2026-09-21 — Approved limited native observation after landing: generated six
fully fictional variants preserving one reviewed 48-row chapter DOM; root reviewed
source/gold/requests before calls and excluded the sixth compaction probe from
conditional classifier scoring. Full planner5/5, rawJEV4/5, guarded shadow4/5
exact with a safe review on the remaining format case. Allfour authoritative
artifacts unchanged. Planner conventions contradicted its own format verdict on
fused headers, explaining the JEV clean result; layout guard prevented clearance.
The deliberately ambiguous sixth note was dropped by compaction and both models
missed that missing context. Seven calls cost$0.03386839, unknown$0, no retries or
contract failures under$0.15 cap. Keep shadow-only; no runtime policy changes.
Evidence: `docs/evals/artifacts/story234-anonymized-observation/report.md`, frozen
manifest/review and `run/` raw requests/responses. Five focused harness tests and
Ruff passed; runtime tests reused unchanged. Primary checkout untouched.
