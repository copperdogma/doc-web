# Scout 012 — dossier-methodology-hardening-audit

**Source artifact:** `/Users/cam/Documents/Projects/doc-web/docs/scout/scout-012-dossier-methodology-hardening-audit.md`
**Audited against:** `/Users/cam/.codex/worktrees/aed0/doc-web`
**Audited:** 2026-04-08
**Re-verified:** 2026-04-08
**Scope:** Audit the Dossier-generated methodology hardening list against the current worktree, then re-check after implementation to confirm which findings still need follow-up.
**Result:** All 20 findings are now implemented in this worktree. A second-pass re-audit found one residual miss in the published lint-contract prose (item 10), and that mismatch is now fixed too.

## Post-Implementation Re-Audit

| # | Finding | Status | Verification note |
|---|---|---|---|
| 1 | Active-surface lint boundary too narrow | [x] Fixed | `ACTIVE_SURFACE_PATHS` now covers 46 live methodology surfaces, including canonical docs, ADRs, scout history, setup refs, and generated wrappers. |
| 2 | Included methodology docs still teach a pre-migration build-map mental model | [x] Fixed | `docs/methodology-ideal-spec-compromise.md`, `docs/runbooks/setup-methodology.md`, and `AGENTS.md` now teach the state/graph model as current. |
| 3 | Eval lineage is still heuristic instead of explicit canonical metadata | [x] Fixed | All 11 evals now carry explicit lineage fields in `docs/evals/registry.yaml`, and `parse_eval_registry()` consumes those fields directly. |
| 4 | Live eval workflow docs still teach build-map-era linkage | [x] Fixed | `docs/evals/README.md` and `docs/evals/attempt-template.md` now teach the explicit registry-lineage contract. |
| 5 | Audit artifact is still a migration plan, not a completed contract record | [x] Fixed | `docs/methodology-artifact-audit-and-migration.md` is now framed as a migration record with historical language where appropriate. |
| 6 | Story 187 now overstates the remaining migration debt | [x] Fixed | `docs/stories/story-187-methodology-graph-state-migration.md` now frames the old warning set as certification-time context, not current graph state. |
| 7 | Decision-record layer is outside the guardrail and already has stale current-state claims | [x] Fixed | ADR files are inside `ACTIVE_SURFACE_PATHS`, and ADR-001 through ADR-003 now use explicit historical framing where they mention the retired build-map surface. |
| 8 | Methodology regression coverage has not caught up to long-tail hardening | [x] Fixed | `tests/test_methodology_graph.py` now covers explicit eval lineage, widened active surfaces, build-map framing, and generated-view framing. |
| 9 | Canonical spec is outside the guardrail and still encodes the retired build-map model | [x] Fixed | `docs/spec.md` is now inside the guardrail and renames `B8` to `Methodology state & phase tracking`. |
| 10 | Published lint contract no longer matches actual compiler behavior | [x] Fixed | Re-verified in the second pass. `docs/methodology-artifact-audit-and-migration.md` now matches the compiler on blocking vs warning lints. |
| 11 | Bundled `/setup-methodology` mode reference still teaches a retired build-map migration step | [x] Fixed | `.agents/skills/setup-methodology/references/modes.md` now says `Reshape spec plus methodology state/graph around shared categories`. |
| 12 | Scout history is outside the guardrail and still contains a false present-tense build-map claim | [x] Fixed | `docs/scout/scout-011-external-document-ingestion-systems.md` now frames those claims as historical and is covered by the compiler guardrail. |
| 13 | Older scout-history docs still teach a false present-tense pre-migration triage/story-index model | [x] Fixed | `docs/scout/scout-004-dossier-triage-skills.md` and `docs/scout/scout-010-dossier-storybook-upgrades.md` now frame the old model as historical. |
| 14 | Scout history also still teaches a false present-tense missing-methodology-package state | [x] Fixed | `docs/scout/scout-001-dossier-patterns.md` and `docs/scout/scout-003-storybook-patterns.md` now say `Us (at scout time)` instead of presenting that state as current. |
| 15 | Cross-CLI wrapper surface is outside the guardrail and still republishes ambiguous generated-index wording | [x] Fixed | `.agents/skills/create-story/SKILL.md` and `.gemini/commands/create-story.toml` now talk about regenerating generated views, not updating a story index manually. |
| 16 | ADR research workflow still routes operators through build-map-era impact guidance | [x] Fixed | `docs/runbooks/deep-research.md` now routes changes through `state/graph guidance`, not `build-map guidance`. |
| 17 | Compiler still under-enforces generated-view framing for `docs/stories.md` | [x] Fixed | The compiler now rejects unqualified `docs/stories.md` / `story index` references in active surfaces unless they carry generated-view framing. |
| 18 | Live helper script still preserves obsolete `docs/stories.md` substrate residue | [x] Fixed | `.agents/skills/create-story/scripts/start-story.sh` no longer carries the dead `INDEX="$ROOT/docs/stories.md"` variable. |
| 19 | Settled story-workflow migration runbook still teaches a mixed transitional tracking model | [x] Fixed | `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md` now points directly at graph, generated `docs/stories.md`, methodology state, and eval registry. |
| 20 | Rerunnable benchmark harness still emits stale build-map-era next-step guidance | [x] Fixed | `scripts/spikes/surya_component_benchmark.py` now says `Stop after updating scout and methodology-surfaces notes.` |

## Historical Initial Audit

The initial audit snapshot preserved below is now superseded by the
post-implementation re-audit above. It is retained only as the before-state
record that justified Story 199.

## Bundle Notes

- Compiler and guardrail sweep: 1, 3, 7, 8, 10, 15, 17
- Live methodology docs and runbooks sweep: 2, 4, 5, 6, 9, 11, 16, 19
- Scout-history stale-current-state sweep: 12, 13, 14
- Small helper and benchmark residue cleanup: 18, 20

## Verification

- `make methodology-compile`
- `make methodology-check`
- `python -m pytest tests/test_methodology_graph.py -q`
- `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
- targeted `rg` sweeps across `AGENTS.md`, `docs/`, `.agents/skills/`, `.gemini/commands/`, and `scripts/`
