---
title: "GPT-6 Luna detector-only runtime qualification"
status: "Done"
priority: "Medium"
ideal_refs: ["Fidelity to Source", "Eval Before Build"]
spec_refs: ["spec:4", "spec:8", "C4", "C5"]
adr_refs: []
depends_on: ["231", "232", "235"]
category_refs: ["spec:4", "spec:8"]
compromise_refs: ["C4", "C5"]
input_coverage_refs: ["scanned-pdf-tables", "image-directory-scans"]
architecture_domains: ["illustration-extraction"]
roadmap_tags: ["model-evaluation"]
legacy_system: ""
---

# Story 236 — GPT-6 Luna detector-only runtime qualification

**Status**: Done

## Decision contract

Attempt 042 established a bounded 13/13 detector lead for exact `gpt-6-luna` at medium reasoning, while its independent page-context safety lane made a false-safe judgment and stopped. The page-context benchmark retains GPT-5.5. The maintained runtime still uses Gemini 3 Flash for both detector and caption assist, plus deterministic layout-text trimming. This story tests a split route: GPT-6 Luna detector at medium, Gemini 3 Flash caption assist, and unchanged trim, against fresh Gemini detector/caption on the same four established public Onward pages. The four-page source and upstream metadata come from Story 231; page 1 is the deterministic cover bypass, with inference on pages 12, 122, and 125. No page-context rerun, private corpus, default change, commit or push.

The two projected recipes differ only in detector model, its required medium reasoning, and the caption-model split. Same source fixture, high-resolution directory, parameters, and cap. Production output acceptance requires correct page-12 image grouping, page-122 no printed captions below reunion/Sophie portraits and no neighboring-photo leakage, and preserved page-125 line art, using source and actual crop files. Any candidate failure retains Gemini; contract/transport failure remains unscored and does not silently pass. All raw direct provider responses are retained before parsing, with hashes; driver manifests and images are inspected. The prior campaign's USD 3.00 cap includes Attempt 042's USD 0.201644875, leaving USD 2.798355125.

Conservative new-call reservation: allow four detector calls per arm and eight Gemini caption calls total, despite expected three non-cover pages per arm. At 250,000 input tokens and full 8,192 detector / 400 caption output tokens each, OpenAI Luna detector is at most USD 0.141384 using input USD 0.125/M (cache-write upper bound) and output USD 0.50/M. Gemini detector is at most USD 0.598304 and Gemini caption at most USD 1.009600 using input USD 0.50/M and output USD 3/M. Combined reservation USD 1.749288; prior spend plus reservation USD 1.950932875, below USD 3.00. Stop if observed usage invalidates the next-call bound. No automatic retry or sweep.

## Goal

Qualify the detector-only GPT-6 Luna route against the maintained four-page owner runtime seam and make a source-backed adopt-or-retain decision.

## Acceptance Criteria

- [x] Strict exact GPT-6 runtime route and optional caption-model split preserve the maintained default.
- [x] Both recipes resolve and focused contract tests pass before paid calls.
- [x] Fresh same-input owner driver artifacts, raw receipts, costs and source-backed visual adjudication recorded.
- [x] Task-level recommendation states detector, caption, page-context and publication boundaries separately.

## Tasks

- [x] Preserve maintained source, metadata, recipe parameters, prompt boundary and shared campaign cap.
- [x] Run fresh paired owner driver artifacts, preserving raw responses and source-backed visual inspection.
- [x] Classify transport/tooling defects separately from model and downstream crop defects, then update owner eval and methodology records.

## Central Tenets

- [x] T0: source, raw detector box, final crop, provider IDs and costs remain traceable.
- [x] T1/T2: test the AI detector before considering a runtime switch.
- [x] T3: reject the materially clipped and text-contaminated page-12 crop against source.
- [x] T4: optional detector reasoning/caption split keeps the maintained recipe modular and unchanged.
- [x] T5: inspect driver JSONL, crop images and original high-resolution source rather than trusting `done` status.

Spec Refs: spec:4.1, spec:4.2, spec:8
Eval Refs: image-crop-extraction, crop-page-level-deletion-gate
Compromises: C4, C5
Decision Refs: None found for this bounded model comparison.

## Workflow Gates

- [x] Build complete for the bounded split route and evidence record.
- [x] Validation complete for affected modules, adapters, driver artifacts and methodology surfaces.
- [x] Documentation and eval registry updated with source-backed verdict and costs.
- [x] Story marked done via /mark-story-done; runtime adoption remains rejected under Attempt 043.

## Work log

- 2026-09-26: Confirmed Story 232 treats the 13 hand-authored goldens as the bounded selection truth and Story 231 requires owner driver artifact inspection before any runtime adoption. The maintained route's strict Responses support covered GPT-5.6 only and used `none`; a GPT-6 substitution would take a loose unsupported-temperature route. Added optional strict GPT-6 detector reasoning and caption-model split in the isolated worktree. Existing owner credentials are present only through the normal wrapper; no values inspected. Materialized Story 231 public four-page fixture and read-only linked its maintained high-resolution source directory. Plan resolution and 18 focused tests passed before paid calls.
- 2026-09-26: Fresh owner driver runs and recovery diagnostics are preserved in Attempt 043 and its manifest. At the exact maintained caption cap and restored layout model, Luna produced seven crops versus Gemini's eight; a common 2048-token caption diagnostic produced seven versus nine. Luna's page-12 raw detector box itself clips the seal and signatures and includes printed officer text; the failed caption response did not cause that geometry. Gemini's nine-crop control also retains printed labels under signatures, so neither arm proves C5 removal. Page 122 and 125 crops passed the bounded source inspection. The model-selection lead remains Luna, while the task-level decision retains the Gemini detector and GPT-5.5 page regression provider. All 42 new runtime receipts plus the earlier campaign cost total $0.382724960 of the $3 cap. No default or account change, commit, or push.
- 2026-09-26 closeout: 95 focused owner tests passed across provider, parser, recipe and crop modules; Ruff, methodology compilation/check and `git diff --check` passed. All 42 raw response hashes and provider IDs were verified unique. Story 236 evaluates and rejects this runtime switch; the retained default and C5 residue remain explicit in Attempt 043.
- 2026-09-26 — Closure: dependencies 231/232/235 are Done; all four acceptance criteria, three tasks, tenets and workflow gates above are supported by Attempt 043, its paired real `driver.py` manifests, source/crop inspection, raw-response manifest and registry. The only remaining crop cleanup is the existing C5 residual, not an unmet evaluation task. The candidate is closed as a documented non-adoption.
- 2026-09-26 landing validation: A precautionary broad `make test` was started because the changed crop module is shared runtime code, then stopped after 367 passing tests when it reached unrelated slow pip-install CLI tests; it is **not** claimed as a full-suite pass or mandatory gate. The affected shared interfaces already have 95 focused passing tests and real paired driver artifacts. Broad `make lint` reports one pre-existing E702 in untouched `tests/test_mimo26_budgeted.py`, confirmed in the base commit; changed-file Ruff passes. Methodology check, registry/raw hashes and staged diff check pass. No unrelated file was changed to quiet these checks.
