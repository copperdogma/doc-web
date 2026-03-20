# The Ideal-First Methodology

## TLDR

Instead of writing a spec from requirements alone, you first describe:

- the **Product Ideal** — what doc-forge should be for the user if there were
  no limitations
- the **Execution Ideal** — what building doc-forge should feel like if AI had
  perfect reasoning, perfect memory, and zero friction

Then you document every place where reality forces a compromise. Those
compromises live in `docs/spec.md`. `docs/build-map.md` tracks where those
compromises live in the codebase, whether their substrate exists yet, and
whether each one is still climbing, merely being held, or ready to converge
away.

The architecture is supposed to collapse as the limitations disappear.

## What It Produces

The methodology produces one connected graph of artifacts:

1. **Ideal** — `docs/ideal.md`
   Product ideal + execution ideal + vision-level preferences
2. **Spec** — `docs/spec.md`
   Active product constraints and build-process constraints with stable
   `spec:N` / `spec:N.N` identifiers
3. **Build Map** — `docs/build-map.md`
   Central planning dashboard: category scope, substrate status, phase
   governance, input coverage, and graduation readiness
4. **Decision Records** — `docs/decisions/`
   Hard-to-reverse architecture, workflow, schema, and cross-cutting choices
5. **Stories** — `docs/stories/`
   Build slices under the build-map categories and spec refs
6. **Evals** — `docs/evals/registry.yaml` plus benchmark assets
   Quality signals, compromise-deletion gates, and attempt history

## The Core Idea

Most specs describe what to build.

This methodology starts by describing what you should **not** have to build if
the world were kinder:

- no manual recipe choice if intake routing were good enough
- no OCR ensemble if one model could read every page perfectly at sane cost
- no document-consistency planning layer if one source-aware extraction pass
  already produced globally consistent structure
- no heavy story / eval / runbook scaffolding if AI could plan, verify, and
  remember perfectly

Every piece of complexity must justify itself against a named limitation. When
that limitation changes, the complexity should either:

- disappear
- collapse into a lighter residual form
- remain only because a human still prefers it

## Product Constraints vs Execution Constraints

Doc-forge tracks two kinds of active constraints.

### Product constraints

These are limits on what the runtime can do directly.

Doc-forge examples:

- YAML recipe selection instead of true auto-routing
- multi-stage OCR instead of one universal extractor
- crop detection with validator + trim heuristics instead of one perfect pass
- document-consistency planning artifacts instead of inherently consistent
  whole-document extraction

### Execution constraints

These are limits on what AI-assisted development can do directly.

Doc-forge examples:

- eval registry and benchmark workspace
- story / backlog system
- build map and phase tracking
- ADR process
- manual artifact inspection
- setup / methodology docs and cross-CLI skill sync

These do not exist because the product needs them. They exist because the
current build process still needs scaffolding.

## How Constraints Work

Each active compromise should answer the same questions:

- **Ideal** — what should happen in the zero-limitation world?
- **Constraint** — what do we do instead right now?
- **Limitation** — what specific reality forces that workaround?
- **Limitation type** — AI capability, ecosystem, economics, physics, human
- **Detection or evolution signal** — what tells us the limitation changed?
- **Residual form** — what remains after that change?

Typical residual patterns:

- **AI -> deletion** — the workaround should disappear entirely
- **AI -> transformation** — the heavy managed harness disappears, but a
  lighter artifact may remain
- **Economics / ecosystem -> evolution** — the need persists, but the form
  should get simpler over time
- **Human -> preference** — the process collapses to whatever level of human
  involvement is still wanted

## Category-Aligned Spec

The spec is organized by shared categories, not by an unstructured list of
"AI compromises."

Why that matters:

- the spec and build map align 1:1
- stable IDs survive heading-name edits
- product and build constraints get explicit homes
- triage can reason by category instead of by scattered notes

Doc-forge currently organizes the graph into nine categories:

1. Intake & Format Routing
2. OCR & Text Extraction
3. Layout & Structure Understanding
4. Illustration Extraction
5. Document Consistency Planning
6. Validation, Provenance & Export
7. Graduation & Dossier Handoff
8. AI Harnesses & Tooling
9. Planning Infrastructure

## The Build Map

The spec says what the active constraints are.
The build map answers the operational questions:

- where does this category live?
- does the substrate actually exist?
- which stories cover it?
- is the current job to improve quality, hold the floor, or delete complexity?
- how much format coverage or graduation confidence do we really have?

Every category tracks:

- product need
- tech need
- substrate status
- story coverage
- spec refs
- ADR refs
- absorbed legacy scope

### Phase Governance

Each active compromise carries a phase:

- **climb** — below target; improve quality or close a real gap
- **hold** — working for the current stage; protect the floor and avoid sprawl
- **converge** — deletion or collapse should now be the focus

This matters because the same work can be high-value or low-value depending on
phase:

- in `climb`, quality improvement is the right next move
- in `hold`, simplification or cost reduction is usually higher leverage
- in `converge`, adding more workaround logic is usually the wrong move

## Build-Map-First Operating Rule

Planning and triage start from `docs/build-map.md`.

Implementation starts from the active story, but the story is not enough on its
own. The build-map category and linked `spec:N` sections supply the strategic
context:

- what category owns this work
- whether the substrate is `exists`, `partial`, or `missing`
- whether the phase says "improve," "hold," or "delete"
- whether input coverage or graduation state should change if the work lands

`Pending` is not proof of buildability. It is only a planning status. For
architecture-dependent work, the substrate must still be verified in code,
schemas, artifacts, or tests before the story is treated as honestly ready.

## Daily Use

The methodology is most useful as a filter.

### Product filter

For any feature idea:

- under what ideal requirement or vision-level preference does it fit?
- if nowhere, it probably does not belong

### Process filter

For any new workflow step or planning artifact:

- under what execution limitation does it fit?
- if nowhere, it is probably process theater

This is what keeps doc-forge from drifting into:

- over-engineered runtime logic
- over-engineered process scaffolding

## Doc-Forge Examples

### Example 1 — Multi-stage OCR

The ideal says one call should read any page perfectly.

Reality says the repo still needs:

- expensive OCR treated as a single-run upstream
- targeted downstream rescue for hard layouts
- artifact reuse so iteration does not re-spend the expensive stage

That is why `spec:2` exists, and why the build map still shows `C1` as
`climb` rather than `converge`.

### Example 2 — Document consistency planning

The ideal says repeated structures should already render consistently from a
single source-aware pass.

Reality says page-by-page extraction still drifts, so the repo emits
inspectable policy artifacts:

- `pattern_inventory`
- `consistency_plan`
- `conformance_report`

Those artifacts are compromises, not the ideal end state. The methodology keeps
them explicit so they can be deleted once a stronger extractor makes them
unnecessary.

### Example 3 — Planning infrastructure

The ideal says you should describe what you want and the AI should build it.

Reality says the repo still needs:

- stories
- build-map tracking
- ADRs
- scout records
- eval registry discipline

Those are execution constraints, not product value. They should stay only as
heavy as current AI limitations require.

## Bootstrap Surface

The canonical bootstrap or refresh entrypoint for this methodology package is
`/setup-methodology`, with `docs/runbooks/setup-methodology.md` as the prose
front door.

The setup package is not only:

- ideal/spec/build-map alignment

It also includes:

- the working setup checklist
- eval-surface docs
- AGENTS wiring
- skill-sync hygiene

Once the package exists, recurring work moves to `/improve-eval`, `/align`,
`/triage`, and the normal story/build/validate/closeout flow.

## What It Is Not

- Not a roadmap
- Not a guarantee that every compromise will delete quickly
- Not a license to under-build current compromises
- Not a second planning system beside stories and the build map
- Not a reason to cargo-cult another repo's setup surface when doc-forge's
  local runtime, benchmarks, or workflows differ
