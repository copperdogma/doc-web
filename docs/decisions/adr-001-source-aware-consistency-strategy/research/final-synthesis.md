---
type: synthesis-report
topic: "Source-aware consistency alignment and re-extraction strategy"
synthesis-model: "codex-gpt-5"
source-reports:
  - "xai-research-stub.md"
  - "opus-research-stub.md"
  - "openai-research-report.md"
  - "gemini-research-report.md"
synthesized: "2026-03-14"
---

# Final Synthesis

## Decision Summary

Cross-provider research converges on the same core architecture: codex-forge should treat consistency failures primarily as a source-aware rerun problem, not an HTML-repair problem. The recommended strategy is a phased pipeline of page-scope extraction, cheap deterministic detection/clustering of repeated structures, selective schema-frozen reruns from source for flagged drift pages, and only light deterministic canonicalization afterward. The strongest practical implication is that the first implementation slice should be read-only detection and rerun gating on existing artifacts, not immediate automation of reruns.

## Evidence Summary

- All four external reports reject HTML-only normalization as the primary answer. OpenAI, Gemini, xAI, and Opus each recommend selective source-aware reruns with deterministic detection/gating around them.
- There is strong agreement on the deterministic toolkit for detection: header/column fingerprints, DOM or tag-sequence similarity, MinHash/SimHash-style screening, clustering, and optional tree-edit-distance / record-linkage as higher-cost validation layers.
- There is strong agreement that normalization still matters, but only as narrow canonicalization after a better rerun or as a fallback for trivial residue.
- There is strong agreement that high rerun coverage is the architecture boundary. OpenAI suggests a warning band around `25-30%`, Gemini suggests `30-40%`, and both xAI and Opus land near `30%`. Synthesis recommendation: use `25%` as a warning band and `30%` across multiple documents as the trigger to redesign extraction granularity.
- Story 141's local evidence matches the external research. A stronger model over a broader source-informed scope already outperformed the current deterministic cleanup on the reviewed Onward chapters, which is exactly the pattern the external reports recommend operationalizing.

## Recommended Strategy

Use a four-layer architecture:

1. Preserve the current page-scope AI-first extraction as the baseline artifact.
2. Add deterministic/statistical detection and clustering to identify likely same-schema runs, infer provisional schema hints, and flag drift pages.
3. Re-extract only the flagged pages/runs from source with the frozen schema hint plus nearby context, then accept or reject the rerun with deterministic checks.
4. Apply only light deterministic canonicalization after accepted reruns.

What should be deterministic:
- run detection
- schema fingerprinting and drift scoring
- clustering
- acceptance/rejection checks
- provenance reporting
- cosmetic canonicalization

What should be AI-driven:
- the initial extraction
- schema-sensitive reruns from source
- semantic edge cases that deterministic logic cannot safely resolve, such as heading ownership

What should not be the main path:
- heavy HTML-only rewriting
- fully heuristic semantic normalization without returning to source
- full-document reruns by default

Practical detector stack for the first build:
- header/column/span fingerprints
- tag-sequence or DOM similarity
- clustering over those similarity signals
- report artifacts with confidence, flagged pages, and candidate canonical headers

Optional later enrichments:
- tree-edit-distance mapping for deeper provenance
- record-linkage checks for row-level validation
- layout/table-model augmentation if artifact-only signals prove insufficient

## Rollout Shape

1. First slice: detection and rerun gating only.
Build a report-only stage or tool over reused artifacts that clusters genealogy runs, flags structural drift, records schema hints, and measures rerun coverage. Do not automate reruns yet.

2. Second slice: selective source-aware reruns.
Use the detection output to drive reruns on flagged pages/runs, with schema freezing and deterministic acceptance checks.

3. Third slice: broader extraction granularity where needed.
For recipes that repeatedly exceed the rerun-coverage threshold, move from page-scope extraction plus reruns to section/run-aware extraction from the start.

4. Later work:
- optional structured intermediate representation if constrained JSON output proves more reliable than direct HTML
- optional layout-model augmentation for weakly structured document families
- reusable runbook/skill once the strategy is accepted and battle-tested

## Cost and Quality Guardrails

- Warning band: if rerun coverage is consistently above `25%`, treat the recipe as potentially mis-granular and review the design.
- Redesign trigger: if rerun coverage is consistently above `30%` across multiple documents, prototype broader run-aware extraction instead of scaling selective reruns indefinitely.
- Rerun failure trigger: if more than roughly `15%` of flagged pages in a run still fail acceptance after rerun, assume the schema hypothesis or extraction granularity is wrong.
- Acceptance checks for reruns should include:
  - schema/header conformance
  - no row/field coverage loss
  - preservation of totals/summary structures
  - high text/content preservation versus the baseline artifact
  - non-regression on reviewed good chapters
- Canonicalization rules must be idempotent, reversible where possible, and limited to cosmetic normalization rather than semantic reinterpretation.

## Risks and Unknowns

- Semantic hierarchy remains the hardest unresolved class. Heading ownership across page boundaries still likely requires AI judgment.
- Schema inference can be poisoned by bad first-pass output; the detector must not pretend low-confidence schema guesses are truth.
- Direct HTML constrained decoding is weaker than structured JSON-style constrained output. A mini-IR or structured rerun output may ultimately be safer than direct HTML regeneration.
- Cross-page consistency benchmarks are weak in the public literature; codex-forge will likely need its own internal benchmark/reporting signals.
- This synthesis would be falsified if the read-only detector cannot reliably separate the reviewed bad Onward runs from the reviewed non-regression chapters, or if selective reruns regularly improve structure at the cost of content fidelity.

## Follow-ups

- Update `adr.md` with a real research summary and move ADR-001 from `RESEARCHING` to `DISCUSSING`.
- Re-scope Story 142 to the converged first slice: detection and rerun gating, not immediate rerun automation.
- Create a later follow-up story for automated schema-frozen reruns once Story 142 proves the signals are strong enough.
- Distill the accepted workflow into a reusable skill, runbook, or `AGENTS.md` guidance before ADR-001 is closed.
