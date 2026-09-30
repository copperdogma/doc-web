---
title: "GPT-6.1 Sol maintained detector, safety and handwriting evaluation"
status: "Done"
priority: "Medium"
ideal_refs: ["Fidelity to Source", "Eval Before Build"]
spec_refs: ["spec:1", "spec:2", "spec:4", "spec:8", "C4", "C5"]
adr_refs: []
depends_on: ["238"]
category_refs: ["spec:1", "spec:2", "spec:4", "spec:8"]
compromise_refs: ["C4", "C5"]
input_coverage_refs: ["handwritten-notes", "image-directory-scans"]
architecture_domains: ["ocr_and_extraction", "illustration-extraction"]
roadmap_tags: ["model-evaluation"]
legacy_system: ""
---

# Story 239 — GPT-6.1 Sol maintained evaluation

## Decision contract

Cam selected Scout078 item2: a bounded Doc Web evaluation up to **USD14.00 inclusive of controls, qualification and recovery**. Direct exact OpenAI `gpt-6.1-sol` through Responses, Standard tier, reasoning low. Fresh origin/main base `5ca3711fb13b12b5b3e261438e7a00ffe450a647`, isolated `codex/gpt61-sol-eval-20260929`. Public checked-in Onward images and public LOC Barney/Alverson scans only. Existing owner OpenAI/Gemini credentials via read-only wrapper. No private sources, default changes, commit, push or deployment.

The detector uses frozen `conservative-count` prompt, integer strict schema, owner scorer/goldens, Image011 first, then full13 only if range/grouping and scorer pass. The comparison is fresh `gemini-3-flash-preview` on the identical13 source keys with maintained normalized coordinates. Require13/13 and overall>=.95, valid local bounds and grouping. This is a bounded selection corpus; avoid claims beyond it. Conditional page-context safety uses frozen two-image prompt, strict verdict schema, page-122-001 first, then full22 only after detector admission and safe screen; fresh GPT-5.5 Responses none/2048/auto control. Require22/22, zero false-safe. A skipped safety stage is not measured and C5 cannot be deleted by a validator alone.

Independent handwriting continues regardless of detector result: actual `driver.py` image-entry OCR on the checked-in public LOC Barney and Alverson scans, each using unchanged OCR system/user/hints, same resize and page HTML scorer. Candidate low and fresh Gemini3.7 maintained default medium; both allow16384 output. Require>=.99 on each page. This two-page screen alone cannot close Story191's broader image/PDF/synthetic requirement.

Serial, no subject cache, no active LLM judge; structural assertions are deterministic. Initial max output4096 detector/safety,16384 OCR. No semantic tuning; at most two evidence-driven operational repairs within cap, retaining failed and unknown receipts. Keep access, transport, semantic, reliability, economics and adoption conclusions separate. Prior Sol.992731 and Gemini3 Flash.962615 full detector, GPT5.5 current safety, and Sonnet/Gemini OCR misses are historical context, not fresh controls.

## Preflight and spend

Zero-cost topology `docs/evals/evidence/046-gpt61-topology.json` resolves independent case messages, prompt/input hashes, exact provider arms, fixed scorers,13 detector and22 safety full-case lists. Every send reserves before HTTP:26k input tokens per one-image call or46k per two-image call, including text/schema allowance; full configured output; highest input/cache-write rate. Actual complete usage settles; unknown billing retains reservation. Full paired matrix maximum **$12.647816**, qualification reserve **$0.42384**, leaving **$0.928344** within the hard cap for recovery. Conditional stages are admitted from settled exposure. GPT5.5 uses $5/$30 per million input/output, GPT6.1 $2/$0.10 cached/$2.50 write/$10. The 250k legacy runtime flag is not used in this campaign guard. Actual SDK HTTP interception, raw retention and before-dispatch cap refusal passed offline tests. No provider calls have occurred at story creation.

## Acceptance criteria

- [x] Native and owner-parity access/contract qualification with exact served identity, complete receipts and cap accounting.
- [x] Independent detector, conditional safety, and OCR decisions with fresh applicable controls and source-backed mismatch review.
- [x] Durable attempt/registry/evidence, artifact inspection and focused verification completed.

## Work log

- September29: Fresh remote base and isolated worktree created. Primary checkout dirty but untouched. Source hashes show Attempt045 and GPT6 repairs already in current base. Existing owner key names present through wrapper; no key value read, copied or printed. Prepared fixed matrix and guard before paid work.
- September29: All 36 guarded paid requests completed with exact served identity and usage. The 13-case detector scored .979331 versus fresh Gemini3 Flash .965292; Image011 source inspection confirmed seal and signatures inside the lower box. The candidate false-safed page122001 while fresh GPT5.5 correctly rejected it; the gated full22 remained unmeasured. Actual-driver Barney/Alverson OCR scored .902693/.935065 versus Gemini3.7 .980645/.983471 against frozen transcripts. Barney has a source-visible candidate invention; Alverson's original appears to support candidate “no good prospect” over the golden's “a good prospect,” so review that golden before another OCR decision.
- September29: Closed ledger settled $0.29783725 usage-priced exposure under $14, with zero unknown reservations. The manifest identifies all 36 receipt hashes; the 22.1MB archive reconstructed and verified 133 ignored artifacts. Focused tests and methodology/diff checks passed. Keep GPT5.5 safety and Gemini3.7 OCR; detector-only promotion needs actual runtime chain and retained safety proof. No default changed.

## Workflow gates

- [x] Build complete for selected bounded evaluation.
- [x] Validation complete or explicitly skipped.
- [x] Story marked done via /mark-story-done.


## Central Tenet verification

- [x] T0 Traceability: all 36 exact request/response hashes and four driver runs retained.
- [x] T1 AI first: extraction stays model-owned; no deterministic transcription corrections.
- [x] T2 Eval before build: failed safety and handwriting gates block adoption.
- [x] T3 Fidelity: Barney invention and Alverson golden concern remain explicit; goldens unchanged.
- [x] T4 Modularity: isolated provider/task/recipe arms; all existing runtime defaults retained.
- [x] T5 Inspect artifacts: source scans, two diagnostic figures and four OCR HTML outputs reviewed.
- [x] Documentation updated: Attempt046, registry, Story191, generated methodology and changelog.

## Scoped closeout

2026-09-29: `/finish-and-push` rechecks the already-completed Story239 under `/mark-story-done`. Dependency Story238 is Done; all three acceptance criteria and workflow gates are supported. No new architecture decision is required for this existing Responses compatibility seam. Frozen paid receipts, actual-driver runs and source inspection are reused without any provider calls. Closeout independently reconstructs all133 artifacts and verifies original receipt/source hashes; executed native-probe/preflight bytes are preserved separately before formatting-only lint repair. A mocked OCR contract regression covers low reasoning, no temperature, store:false and image preservation; owner lint/test and methodology checks cover the runtime helper and closure. Changelog moved to the newest-first location. Story191 remains Blocked and no golden/default changes are included. Primary checkout untouched; candidate push awaits coordinator all-repo preflight.

Closeout check limit: owner-wide `make lint` reports only the pre-existing E702 at `tests/test_mimo26_budgeted.py:14`, reproduced on the unchanged base file. Changed runtime/tests and current campaign tooling pass targeted Ruff. Coordinator review authorized a single formatting-only repair to that baseline test so the owner lint gate can pass; no semantic or frozen-evidence change. No repository CI workflow is present.

Final verification: `make lint`, changed campaign tooling Ruff, methodology build/check and staged diff hygiene pass. Initial owner suite:1025 passed,1 skipped,3 failed; two untouched requirements install checks fail building newly resolved pikepdf10.16 against local qpdf12.2.0 (`QPDFAcroFormDocumentHelper::validate` missing). The third exposed campaign-test HTTP transport leakage; test teardown now restores both available HTTP libraries, and cross-guard verification passes4 with1 unavailable-library skip. Regression after repair:1019 passed,1 skipped,9 deselected in133.93s, excluding seven successful unchanged fresh-extra integration checks reused from the initial run and the two unavailable native dependency installs. No product/dependency repair was made for those environment failures. Python3.11.5; changed source identities and exact commands/results are retained in the manifest closeout_validation record. No extra provider spend.
