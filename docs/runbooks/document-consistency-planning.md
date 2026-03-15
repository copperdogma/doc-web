# Document Consistency Planning

Use this runbook when a page-scope extraction pipeline produces internally inconsistent structure across one document and the right answer is not a rigid cross-document style guide.

## Goal

Produce explicit, inspectable document-local policy artifacts instead of hiding normalization choices in prompts or ad hoc code.

Required artifacts:
- `pattern_inventory` — repeated pattern families, member chapters/pages, representative evidence
- `consistency_plan` — chosen document-local conventions for each family
- `conformance_report` — which chapters/pages violate that plan, and whether the problem is format drift, row-semantic drift, or mixed

## Workflow

1. Extract normally.
   - Keep the strongest practical source-aware extractor.
   - Do not start by globally rewriting HTML.

2. Build a compact dossier.
   - Summarize chapter/page signals instead of feeding raw whole-document HTML back to the model.
   - Include provenance, header shapes, fragmentation signals, subgroup/context-row evidence, and any row-semantic warning snippets.

3. Run one document-level planning pass.
   - Ask the model to infer document-local pattern families and choose conventions for each.
   - The plan may vary by pattern family inside one document.
   - The output must be explicit JSON, not hidden prompt state.

4. Normalize the model output into the three canonical artifacts.
   - Preserve chapter/page provenance.
   - Normalize missing chapters or weak evidence conservatively.
   - Keep a stamped summary artifact only if pipeline integration needs one.

5. Validate manually.
   - Open the emitted artifacts and the corresponding HTML chapters.
   - Confirm the plan captures the real failure classes you observed.
   - Confirm row-semantic issues are not flattened into pure format drift.

6. Only then drive repair or rerun passes from the emitted `consistency_plan`.
   - Later passes should conform to the emitted plan or explicitly revise it.

## Guardrails

- Document-local, not global:
  - Let the model choose conventions fresh for each document.
  - Do not hardcode Onward-specific formatting rules into generic workflow code.

- Explainability over magic:
  - If the model chooses a bad policy, the artifacts should make that obvious.
  - If the policy is good but execution is bad, the artifacts should make that obvious too.

- Distinguish problem classes:
  - Format drift: split tables, fused headers, concatenated subgroup rows, left-column-only family rows
  - Row-semantic drift: child notes or marginal annotations landing in the wrong data column

- Prefer source-aware follow-up:
  - HTML-only cleanup is a secondary tool.
  - The main downstream move is plan-guided selective reruns from source where justified.

## Model-call guidance

- Prefer the strongest practical planner first.
- If the primary planner returns empty or malformed structured output, retry once with a stable JSON-oriented fallback model.
- Record enough provenance in the artifacts to explain what the planner saw and what policy it chose.

## Success criteria

- The new artifacts explain known failure classes better than the previous detector.
- The `conformance_report` surfaces previously missed format-drift chapters.
- Known row-semantic cases are not treated as pure format drift.
- The result is specific enough to drive a later repair/rerun story.
