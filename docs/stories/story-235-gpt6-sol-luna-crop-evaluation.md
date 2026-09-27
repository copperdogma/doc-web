---
title: "GPT-6 Sol and Luna crop evaluation"
status: "Done"
priority: "Medium"
ideal_refs: ["Fidelity to Source", "Eval Before Build"]
spec_refs: ["spec:4", "spec:8", "C4", "C5"]
adr_refs: []
depends_on: ["207", "209", "232"]
category_refs: ["spec:4", "spec:8"]
compromise_refs: ["C4", "C5"]
input_coverage_refs: ["scanned-pdf-tables", "image-directory-scans"]
architecture_domains: ["illustration-extraction"]
roadmap_tags: ["model-evaluation"]
legacy_system: ""
---

# Story 235 — GPT-6 Sol and Luna crop evaluation

**Status**: Done

## Goal

Measure the approved bounded GPT-6 Sol/Luna detector and independent page-context safety lanes against the maintained Doc Web contracts, without changing runtime defaults.

## Acceptance Criteria

- [x] Exact owner access and native/adapter strict schemas qualified or stopped with evidence.
- [x] Both independent candidate/lane screens and admitted full detector matrices recorded under the shared cap.
- [x] Fresh same-input detector control, source-backed mismatch review, exact costs and durable raw manifest recorded.
- [x] Registry, methodology graph, coverage summary and owner story reflect layered verdicts; no runtime/default change.

## Tasks

- [x] Freeze source, prompt, scorer, golden, case topology, privacy and spend reservations.
- [x] Run guarded native and owner-harness stages; stop page lanes on false-safe results.
- [x] Inspect artifacts and source image, classify outcomes, run focused checks and record evidence.

## Central Tenets

- [x] T0: source page, crop, scorer and raw envelope provenance retained.
- [x] T1/T2: bounded AI model ability measured before any runtime change.
- [x] T3: page-context failure keeps the source-fidelity publication seam intact.
- [x] T4: strict swappable adapter and frozen task projections used.
- [x] T5: raw responses, scorer rows and source images manually inspected.

Spec Refs: spec:4.1, spec:4.2, spec:8
Eval Refs: image-crop-extraction, crop-page-level-deletion-gate
Compromises: C4, C5
Decision Refs: None found for this bounded model comparison.

## Decision contract

Evaluate exact direct Responses `gpt-6-sol` and `gpt-6-luna` on public Doc Web benchmark images only, under Scout 076 item 2 and a shared US$3.00 cap inclusive of fresh controls. Use Standard foreground processing, `store:false`, no router, no automatic retries, serial no-cache calls. Candidate detector uses medium reasoning with the frozen conservative-count prompt, integer 0–1000 strict schema, scorer and 13 human goldens. Qualify then screen Image011; advance to full13 and fresh Gemini 3 Flash only after a valid pass. Require 13/13 and mean overall >=0.95. Independently run the page-context gate with candidates at none reasoning, frozen two-image prompt, strict verdict schema, scorer and 22 goldens. Screen page-122-001; any false-safe stops that candidate's page lane. Advance to full22 and fresh GPT-5.5 Responses only after a valid screen. Require 22/22 with zero false-safe judgments. A stop in either candidate or lane does not cancel the others.

Runtime default is Gemini 3 Flash detection; page-context regression provider is GPT-5.5 Responses. These exposed goldens can support bounded ranking but cannot by themselves justify removing C5 or promotion without separately frozen held-out truth and exact production-output safety proof. No runtime/default change, private payload, commit or push is authorized.

Before paid calls, resolve projected row matrices, image accounting, all-output reservations and total exposure. Keep raw response envelopes in ignored owner storage before parsing; track hashes and sizes in an evidence manifest. Quarantine contract-invalid outputs from semantic scoring. Update registry for measured/blocked attempts and run focused provider and substrate tests.

## Work log

- 2026-09-26: Fetched origin/main `92f341e169f7e81775a7f006ae39757303a8e88f` and created isolated worktree. Existing owner credential is present by variable name only. Authenticated exact model retrieval returned HTTP 200 for both IDs. No paid calls at this point.
- 2026-09-26: Resolved frozen 13 detector and 22 page-context rows, prompts, scorer, goldens, image order, independent case topology, no judge and cache policy before spending. Native strict image and two-image schema probes qualified both exact models. Sol and Luna each passed Image011, then each made a valid false-safe pass on independent page-122-001, stopping both page lanes.
- 2026-09-26: Admitted full13 detector runs completed with Sol 13/13 at 0.978308 and Luna 13/13 at 0.987554; fresh Gemini 3 Flash control was 13/13 at 0.961238. Visually inspected source page/crop and confirmed the separate Sophie portrait inside the rejected page-122-001 crop. No full22 or GPT-5.5 control ran. All-call measured exposure $0.201644875 of $3.00. See Attempt 042 and its raw/result hash manifest.
- 2026-09-26: Focused adapter and crop substrate tests passed (24). Registry records bounded detector quality and targeted page safety distinctly. Runtime and C5 remain unchanged. No commit or push.

## Workflow Gates

- [x] Build complete for the bounded evaluation and evidence record.
- [x] Validation complete for the touched adapter and frozen benchmark substrate.
- [x] Story marked done via /mark-story-done; held-out production-output safety proof remains a separate adoption question.

Luna now leads this bounded detector comparison and is much cheaper than the fresh Gemini arm. Both GPT-6 candidates missed the page-context safety differentiator, so neither has a basis to replace the current crop publication seam or remove its text-trim protection.

2026-09-26 — Closure: dependencies 207/209/232 are Done; all four acceptance criteria, three tasks and listed tenets above are supported by Attempt 042, its ignored raw/result receipts, current registry, 41 focused tests, Ruff, methodology check and whitespace check. No pipeline module or recipe changed, so driver integration is outside this bounded eval. Story 235 is closed; `/finish-and-push` is the optional next landing workflow and requires separate authorization to commit/push.
