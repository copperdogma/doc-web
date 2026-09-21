---
title: "JEV consistency classifier evaluation"
status: "Done"
priority: "Medium"
ideal_refs: ["Fidelity to Source", "Traceability"]
spec_refs: ["spec:2", "spec:5", "C7"]
adr_refs: ["ADR-001"]
depends_on: ["220"]
category_refs: ["spec:2", "spec:5"]
compromise_refs: ["C7"]
input_coverage_refs: []
architecture_domains: ["document-consistency"]
roadmap_tags: ["model-evaluation"]
legacy_system: ""
---

# Story 233 — JEV consistency classifier evaluation

**Status**: Done
**Priority**: Medium
**Ideal Refs**: Fidelity to source, traceability, cheap selective source review
**Spec Refs**: spec:2, spec:5, C7
**Decision Refs**: ADR-001 source-aware consistency strategy; benchmarks/jev-consistency/plan.md
**Depends On**: 220

## Goal and scope
Measure JEV 1.13.0 against the GPT-4.1 Story220 planner model on the bounded
five-class status projection, with explicit existing conventions and source text.
This is a new projection benchmark, not a retry of closed Onward format drift or
replacement of the planner's convention-generation/rationale/repair outputs.
No runtime/default edits, commits, pushes, deployment, or private source transfer.
US$0.60 total, frozen synthetic inputs, two repetitions, exact native evidence.

## Context and approach
C7 document consistency uses inspectable planning artifacts and source-aware
reruns. The previous Onward-only manual lane no longer exposes pure format drift.
New seven-column genealogy tables and maintenance cards introduce two structures
without sending private Onward text. Source-owned human/independent-agent reviewed
labels replace heuristic status truth; deterministic detectors remain comparators.
This separate eval story is warranted by new classifier contract and synthetic
fixture family, unlike Story220's source-aware row-note repair acceptance.

## Acceptance criteria
- [x] Freeze independently reviewed synthetic fixtures and exact model contracts before calls.
- [x] Run fresh JEV and GPT-4.1 projection, real bounded fallback, deterministic baselines.
- [x] Preserve raw synthetic requests/responses, source hashes, exact ledger, errors.
- [x] Classify important misses, report relative quality/economics with sample limits.
- [x] Focused harness tests and artifact inspection; runtime pipeline unmodified.

## Workflow gates
- [x] Build complete
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via /mark-story-done

## Tenets
- T0: request/response/source hash provenance retained.
- T1/T2: measure native AI and deterministic baseline before runtime implementation.
- T3: independent source-based labels; no source edits after scoring.
- T4: evaluation-only module boundaries.
- T5: manually inspect paid artifacts and classify every important mismatch.

## Work log
2026-09-21 — User authorized completion of the portfolio evaluation. Isolated
worktree from origin/main 0a4d20f. TypeSafe and owner evaluate-model skills read.
Fixture review caught four-column detector mismatch, isomorphic structures,
underspecified source notes, and label shortcut; all corrected before calls.
Source text is now prose; actual chapter detector gets lossless HTML; maintenance
cards are explicitly out-of-domain for that existing detector. New generic
structural baseline reported separately. Root and independent reviewer review
fixtures before freeze. No full runtime planner cost or repair success claim.

2026-09-21 — Evaluation complete. Native smoke qualified exact identities and
contracts;97uncached successful calls cost$0.0630996/$0.60. JEV24/40, GPT29/40,
predeclared real cascade33/40;17fallbacks. Cascade54.64% cheaper, median32.18%
faster, p9548.92% slower. Three false-clean defects remain, equal incumbent count.
Independent reviewer classified all34misses across10cases as model-wrong with no
golden defects/changes. Verdict: conditional shadow candidate preserving explicit
uncertain and deterministic layout guards, not full planner replacement.

Verification: focused pytest5/5 and Ruff passed;97raw request/response pairs and
ledger reconciled; formatted parser replay reproduces every stored label/confidence/
cost. Exact paid source was snapshotted before lint formatting, hashes verified.
Methodology graph and whitespace checks pass. Runtime modules untouched; no
driver.py integration claim. Temporary TypeSafe key removed and absence verified;
owner OpenAI unchanged. Eval registry and CHANGELOG updated. All acceptance/tenet
checks met for eval-only scope; Story220 remains existing substrate, ADR001 stays
accepted with no design-policy change. Story233 closed via mark-story-done review.
No commits/push/deployment authorized or performed.
