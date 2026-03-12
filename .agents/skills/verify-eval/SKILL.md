---
name: verify-eval
description: Investigate eval mismatches — classify as model-wrong, golden-wrong, or ambiguous. Fix golden when wrong, re-run eval.
user-invocable: true
---

# /verify-eval

> Decision check: If this task affects golden conventions, scoring rules, or cross-cutting evaluation policy, read relevant runbooks, scout docs, or notes before choosing an approach. If none apply, say so explicitly.

Investigate every mismatch between model output and golden reference after an eval
run. Classify each as model-wrong, golden-wrong, or ambiguous. Fix the golden when
it's wrong, re-run the eval, and report verified scores.

**Raw eval scores are meaningless. Only verified scores count.**

## When to Run

After ANY eval that compares model output against golden references:
- promptfoo evals (`cd benchmarks && promptfoo eval`)
- pytest tests with golden comparisons
- Ad-hoc comparison scripts
- Any time metrics are computed against a golden file

This is not optional. An eval without verification is incomplete.

## Arguments

- `[eval-command]` — (optional) The eval command that was just run. If not provided,
  the skill will ask which eval to verify.
- `[story-file]` — (optional) Path to the story file where the work log should be
  updated. If not provided, the skill will look for the active story.

## Phase 1: Locate Eval Results

1. Identify which eval was run (promptfoo, pytest, ad-hoc script).
2. Find the output showing mismatches — extra items, missing items, scoring failures.
3. If the eval hasn't been run yet, run it now to establish raw scores.

## Phase 2: Enumerate Mismatches

### Getting the comparison data

Eval output (scores, pass/fail) is not enough — you need the actual outputs side
by side. How to get them depends on the eval type:

- **promptfoo evals**: The eval output includes model responses. Load the golden
  from `benchmarks/golden/`. Compare outputs.
- **pytest tests**: Run the pipeline on fixture input, capture output. Load the
  golden. Compare field by field.
- **Ad-hoc scripts**: Write a short script that runs the pipeline (or loads cached
  output) and prints both outputs sorted for easy diffing.

### Build the mismatch table

For each mismatch between model output and golden reference:

```
| # | Type    | Model says        | Golden says       | Classification | Notes |
|---|---------|-------------------|-------------------|----------------|-------|
| 1 | Extra   | "value A"         | (not in golden)   | ?              |       |
| 2 | Missing | (not in output)   | "value B"         | ?              |       |
| 3 | Diff    | "variant X"       | "variant Y"       | ?              |       |
```

## Phase 3: Classify Each Mismatch

For EVERY mismatch, examine the source material and determine:

| Finding | Action |
|---------|--------|
| **Model-wrong** — hallucination, over-extraction, wrong value | Golden stands. Document as a real failure mode. |
| **Golden-wrong** — missing item, wrong value, incomplete | Fix the golden. See Phase 4. |
| **Ambiguous** — insufficient evidence to decide | Note in work log. Defer until more evidence. |

### How to decide

- Read the actual source material. What does it say?
- Is the model's output supported by the source? → Model may be right, golden needs fixing.
- Is the model producing something not in the source? → Model is wrong.
- Is the golden using a convention the model doesn't follow? → May need alias or normalization.

### Thresholds for user consultation

- **Always ask the user** before making structural changes to golden files.
- **Always ask the user** if golden fixes would change >5% of test cases.
- Minor corrections (typos, missing variants) can proceed without asking.

## Phase 4: Fix Golden & Re-run

If any golden-wrong findings:

1. **Apply fixes** to the golden files.
2. **Run relevant tests** to verify golden fixture tests still pass.
3. **Re-run the original eval** to get verified scores.
4. **Document the delta**: raw score → verified score.

If no golden-wrong findings, skip to Phase 5.

### Cost Discipline for Re-runs

Eval runs cost real money. Minimize waste:

1. **Use cached model outputs when only the scorer or golden changed.** If the prompt and provider set are unchanged, reuse cache so only judges or scorers rerun.
2. **Drop the LLM judge during iteration when possible.** While tuning scorers or goldens, prefer deterministic assertions first and restore the expensive judge for the final verification run.
3. **Filter to relevant providers when debugging one model.** Do not rerun a full matrix if only one provider is under investigation.
4. **Reserve `--no-cache` for prompt changes or the final verification run.** Intermediate iterations should usually use cache.

## Phase 5: Report

Write a verification summary in the story work log (or return it to the caller):

```
## Eval Verification — [YYYY-MM-DD]

**Eval**: [command or description]
**Raw scores**: {metric}={value}

### Mismatch Classification (N total)

**Model-wrong (N):**
- [item]: [brief reason]

**Golden-wrong (N):**
- [item]: [what was fixed]

**Ambiguous (N):**
- [item]: [why deferred]

### Golden Fixes Applied
- [list of changes to golden files]

### Verified Scores (after golden fixes)
{metric}={value}

### Delta
- {metric}: {raw} → {verified}
```

Update `docs/evals/registry.yaml` with the verified scores, `git_sha`, and date.

## Guardrails

- Never skip a mismatch — every one must be classified
- Never assume the golden is right just because it's the golden
- Never assume the model is right just because it's SOTA
- Ask the user before structural golden changes
- If golden fixes change >5% of test cases, flag for user review before proceeding
- If mismatches reveal a code bug, document it and return to the calling story —
  this skill fixes goldens, not pipeline code
- Always update `docs/evals/registry.yaml` after verified re-runs
- Do not commit or push without explicit user request
