# Doc-Forge — Methodology Bootstrap Checklist

> Working copy generated from `.agents/skills/setup-methodology/templates/setup-checklist.md`.
> This repo currently uses it as the package-state checklist for refresh runs.

## Mode

- [x] Mode chosen: `refresh`
- [x] Canonical references reviewed (`AGENTS.md`, methodology doc, setup runbook, relevant ADRs)

## Canonical Surface

- [x] `/setup-methodology` is the canonical setup or refresh entrypoint
- [x] `AGENTS.md` advertises the methodology package and build-map-first operating rule
- [x] `docs/runbooks/setup-methodology.md` exists and matches the skill
- [x] `docs/setup-checklist.md` exists as the working checklist

## Methodology Graph

- [x] `docs/ideal.md` contains both product and execution ideals
- [x] `docs/spec.md` is category-aligned and matches the build map
- [x] `docs/build-map.md` is the central planning / triage dashboard
- [x] `docs/methodology-ideal-spec-compromise.md` documents the graph and deletion model
- [x] Story planning surfaces reference build-map context and substrate checks

## Baseline Evidence Setup

- [x] Benchmark and golden guidance is current for the active repo mission
- [x] `docs/evals/registry.yaml` remains the eval source of truth
- [x] `docs/evals/README.md` and `docs/evals/attempt-template.md` exist and match local practice
- [x] The recurring eval-improvement path is documented honestly
- [x] Benchmark / runbook docs still match actual repo commands and directories

## Story / Planning Setup

- [x] Story drafting is anchored to ideal + spec + build-map + decision context
- [x] Story build guidance verifies substrate before treating `Pending` as buildable
- [x] Validation / close-out guidance distinguishes fresh verification from stale confidence
- [x] Scout surfaces capture proof for real cross-repo pattern transfers

## Validation

- [x] Reference audit completed (`rg` for stale setup or methodology promotions)
- [x] Skill sync completed (`scripts/sync-agent-skills.sh`)
- [x] Skill sync check completed (`scripts/sync-agent-skills.sh --check`)
- [x] Eval-surface audit completed
- [x] Methodology alignment sweep completed
