# Triage Runbook

This is the operational companion to `/triage`. Use it for full-sweep
methodology triage before treating stories as a flat backlog. The orchestrator
starts from the Ideal/spec/state/graph and coverage frame, gathers neutral lane
packets, shows the top three candidates, then chooses one yes-ready next action.

## Completion Sanity Gate

Before accepting a "nothing ready", "maintenance only", or idle
recommendation, inspect the v1/MVP promise, input coverage, future/unplanned
state lines, inbox items, and recent stories/evals. If those surfaces show
missing user-facing capability, recommend creating, promoting, reshaping, or
validating that work before routing to routine maintenance. Never equate "no
ready story" with "feature-complete" without concrete evidence.

## Eval Ladder Gate

For AI-capability work, name the root/parent/child eval placement before
recommending implementation work. Prefer a root or parent eval rerun when new
models, provider changes, code changes, scorer fixes, or changed constraints
could collapse the current decomposition. Prefer a child eval or
failure-classification attempt when the parent failure is too vague to choose an
implementation path honestly.

## Triage Shape

1. Read `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`,
   `docs/methodology/graph.json`, and
   `tests/fixtures/formats/_coverage-matrix.json`.
2. Treat the coverage matrix as part of the shared frame, especially when a
   candidate gap touches formats, input routing, provenance, artifacts, or
   channels.
3. Start neutral lane packets when delegation is available:
   - `/triage-stories`
   - `/triage-inbox scan`
   - `/triage-evals`
   - `/triage-architecture`
   - `/triage-health scan`

   If delegation is unavailable, collect the same scoped lane packets
   sequentially after the direct fact pass.
4. In the main thread, run:

   ```bash
   python scripts/triage_facts.py --json
   ```

   Use this as direct evidence for branch/dirty state, generated wrapper drift,
   story/eval recommendations, inbox counts, architecture-audit cadence,
   coverage matrix status, codebase-improvement freshness, lane presence, and
   recent churn. Keep it as a main-thread fact source, not as a substitute for
   lane judgment. If it fails, report the blocker and continue with lower
   confidence.
5. Name 2-4 candidate unmet Ideal/spec/state gaps without picking the final
   winner before lane packets report.
6. Run completion sanity before accepting maintenance-only work.
7. Run the eval-ladder gate for AI-capability gaps.
8. Run the actionability gate for plausible winners: last meaningful action,
   date, proof artifact, and what materially changed.
9. Check existing stories, inbox items, evals, architecture audit state, health
   surfaces, and ADRs for candidate gaps.
10. Add a short `Vs Ideal` read that distinguishes literal north-star distance
   from current-tech progress, then rank candidates against that Ideal/spec
   frame.
11. Build a visible top-three shortlist with Ideal/spec value, why now, action
   shape, validation/stop condition, and rank rationale.
12. Recommend one next action and state why it is the right move now.
13. End with the exact handoff:
    `Reply yes to proceed with: {exact next command or concrete action}.`

## Guardrails

- Do not let a smaller ready story outrank the chosen Ideal/spec/state gap just
  because it is easier to start.
- Do not create implementation backlog when a parent eval failure is still too
  vague to classify.
- Do not force exact wording from another repo when the local product surface
  needs different examples or validation paths.
- Do not pick a final winner before neutral lane evidence can surface stronger
  domain-specific candidates.
- Do not hide the lower-ranked top-three candidates; Cam may choose
  recommendation 2 or 3.
- Keep full-sweep triage read-only.
- Treat `doc-web` as the checkout, package, and fact JSON identity. Do not
  rewrite intentional `doc-forge` product-doc wording when it is describing the
  product surface rather than the repo/package.
- Do not recommend a new story for same-line entry-form parity, later-state
  progression, or docs/test codification unless the runtime seam or validation
  boundary materially changed.
- Do not recommend work that fights the doc-web runtime boundary or maintained
  intake contract.
