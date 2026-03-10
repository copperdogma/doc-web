---
name: improve-eval
description: Structured improvement loop for a failing eval — measure, read history, diagnose, execute, record
user-invocable: true
---

# /improve-eval [eval-id]

Structured improvement loop for a specific eval. Prevents re-trying failed approaches
and creates a durable history of what's been tried.

## Arguments

- **eval-id** (required): The `id` field from `docs/evals/registry.yaml` (e.g., `image-crop-extraction`, `single-model-crop-detection`).

## Phase 1 — Identify

1. **Read the registry** — Load `docs/evals/registry.yaml`. Find the entry matching `eval-id`.
2. **Display current state**:
   - Name, type, description
   - Target: metric, threshold, latency/cost limits
   - Current best score (from `scores` section) vs. target
   - Gap: how far from target? Which dimension is failing (quality, latency, cost)?

If the eval-id is not found, list available eval IDs and stop.

## Phase 2 — Gate

3. **Check if passing** — If the current best score meets ALL target dimensions:
   - Report: "**No action needed.** Eval `{id}` is passing. Best score: {score} (target: {target})."
   - Stop. Do not proceed to diagnosis.

4. **Check staleness** — If `git_sha` is recorded on the best score and current `HEAD` differs:
   - Warn: "Last measurement was at {git_sha}. Code has changed — re-measuring before diagnosis."
   - Run the eval command from the registry entry.
   - Update the score in the registry with the new measurement.
   - Re-check the gate — if now passing, stop.

## Phase 3 — Read History

5. **List all previous attempts** — From the `attempts` section, display:
   - For each attempt: ID, date, approach summary, model, score before → after, status
   - For failed attempts: what `retry_when` conditions were recorded
   - **Blocked approaches**: List approaches where `retry_when` conditions have NOT been met.
     These must NOT be retried. Explain why each is blocked.
   - **Unblocked approaches**: List approaches where a `retry_when` condition HAS been met
     since the attempt. These CAN be retried with the new context.

6. **Check for unblocked retries** — For each failed attempt with `retry_when`:
   - `new-subject-model`: Has a new pipeline model been released? Check model availability.
   - `cheaper-subject-model`: Has a cheaper model appeared?
   - `golden-fix`: Has the golden been updated since the attempt date?
   - `architecture-change`: Has the pipeline stage changed since the attempt?
   - `new-approach`: Has new context emerged that suggests a fresh strategy?

## Phase 4 — Diagnose

7. **Analyze the gap** — Based on the eval type and failure mode:
   - **Quality eval**: What's the failure mode? Specific test cases failing? Read the scorer and golden to understand what's being measured.
   - **Compromise eval**: What capability limitation does this test? Has it changed since last measurement?

8. **Read the eval config** — If `config` is set, read the promptfoo YAML to understand test cases, models, and scoring rubrics.

9. **Suggest candidate approaches** — List 1-3 approaches that:
   - Have NOT been tried before (not in attempts list)
   - OR have been tried but their `retry_when` condition is now met
   - Include for each: what would change, expected impact, risk level

10. **Present to user** — Show the diagnosis and candidate approaches. Wait for user to pick an approach. Do NOT proceed without user approval.

## Phase 5 — Execute

11. **Baseline measurement** — Run the eval to get a fresh baseline score. Record it.

12. **Implement the approach** — Make the changes the user approved. This may involve:
    - Prompt changes
    - Code changes to pipeline stages
    - Golden reference fixes (use `/verify-eval` for mismatch investigation)
    - Model swaps
    - Configuration changes

13. **Post-measurement** — Run the eval again with the changes in place. Record the new score.

## Phase 6 — Record

14. **Write the attempt** — Add an entry to the `attempts` list in `docs/evals/registry.yaml`:
    ```yaml
    - id: "{next-id}"
      story: {current story file, if applicable}
      date: {today}
      status: succeeded | failed
      approach: |
        {Description of what was tried}
      subject_model: {pipeline model tested}
      score_before:
        {metric}: {baseline value}
      score_after:
        {metric}: {post-change value}
      retry_when:           # only for failed attempts
        - {condition}
      note: "{any context}"
    ```

15. **Update scores** — If the score improved, update the `scores` section with the new measurement. Include `measured` date and `git_sha` (current HEAD).

## Phase 7 — Assess

16. **Compare to target** — Does the new score meet the target?
    - **Yes**: "Eval `{id}` is now passing. Score: {score} (target: {target})."
    - **No**: Show remaining gap. Recommend:
      - Another iteration (back to Phase 4)
      - Flagging as blocked with specific `retry_when` conditions
      - Creating a story for larger architectural changes

17. **Summary** — Report what was tried, what changed, and the current state of the eval.

## Guardrails

- **Never retry a blocked approach** — If a previous attempt failed and its `retry_when` conditions have not been met, that approach is off-limits. Explain why to the user.
- **Always measure before and after** — No claimed improvements without evidence. Run the eval, make changes, run the eval again.
- **Read-only until Phase 5** — Phases 1-4 are analysis only. Do not write any code or make changes until the user approves an approach.
- **Record even failed attempts** — The entire point of the registry is preventing wasted effort. A failed attempt with good `retry_when` conditions is valuable data.
- **Use /verify-eval for golden issues** — If diagnosis suggests the golden reference is wrong, invoke `/verify-eval` rather than fixing it inline. Mismatches need structured investigation.
- **Do not commit or push** without explicit user request.
