# Close-Out

Use this runbook with `/finish-and-push`. The shared skill owns authorization,
coordination, Git integration, landing, recovery, and optional cleanup. This
runbook supplies Doc Web's local completion evidence.

## Story closure

When a story is in scope, use `/mark-story-done` and preserve its status,
workflow-gate, work-log, dependency, tenet, and acceptance-criterion checks.
Regenerate `docs/stories.md` and `docs/methodology/graph.json` with
`make methodology-compile`, then run `make methodology-check`. Update
`CHANGELOG.md` once using the repo's `YYYY-MM-DD-NN` CalVer format. If
`/mark-story-done` was called by `/finish-and-push`, return control to the
invoking skill after closure instead of recommending a new close-out invocation.

## Required evidence

Choose the smallest sufficient checks under the shared skill's `Validation
proportional to the change` policy. Reuse applicable evidence when its tested
content, environment, and check configuration still match the candidate:

- evidence or documentation only: inspect affected claims, links, schemas,
  provenance, and generated records; do not run product suites
- isolated eval or development tooling: run focused pytest and Ruff checks for
  the changed tooling and affected shared interfaces
- runtime, dependency, build, shared-library, or cross-pipeline changes: broaden
  from focused checks to `make lint`, `make test`, and affected consumers when
  the dependency path warrants it
- agent skill changes: `make skills-check`
- story-status or methodology-source changes: `make methodology-compile` and
  `make methodology-check`
- pipeline behavior: the narrowest real `driver.py` route that proves the
  change, followed by manual inspection of the emitted JSON, JSONL, HTML, or
  image artifacts under `output/runs/`
- eval work: classify mismatches and update `docs/evals/registry.yaml` with
  verified evidence before closure

A passing command does not replace artifact inspection where project rules
require semantic or visual evidence. Record skipped or unavailable checks
honestly. Follow the shared skill for authorization, Git handling, landing,
recovery, and cleanup.
