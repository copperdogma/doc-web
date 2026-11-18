---
title: "GPT-6.2 Astra source fidelity evaluation"
status: "Done"
priority: "Medium"
ideal_refs: ["req:3", "req:4", "req:6"]
spec_refs: ["spec:2.1", "spec:4.1", "spec:4.2", "spec:6"]
adr_refs: ["ADR-001", "ADR-002"]
depends_on: []
category_refs: ["spec:2", "spec:3", "spec:4", "spec:8"]
compromise_refs: ["C1", "C4", "C6"]
input_coverage_refs: ["scanned-pdf-tables", "handwritten-notes"]
architecture_domains: ["ocr_and_extraction"]
roadmap_tags: []
legacy_system: ""
---
# Story 273 — GPT-6.2 Astra source fidelity

Cam selected Scout116 item3 at USD64 maximum across handwriting/reader/detector caps USD12/10/42. Base 56564d95cd2cf9ce498aaaca84537a64b1e89f31. Candidate native standard Responses high32768, store false, original source pixels, no sampling, no provider fallback. Existing owner credentials via primary owner env override. Public Library of Congress pages, authored synthetic table fixtures, public Onward benchmark crops only. OpenAI API no training by default, abuse retention may apply. Consumer qualification only upon useful quality and measured economics.

Handwriting starts Barney then Alverson when useful, with fresh exact Gemini3.8 and landed Hydrogen. Require .99 using maintained transcript scorer and acceptable source errors. Reader starts authored Bakery, followed by native digital and ambiguity panel if useful; all clear cells exact, ambiguous text held. Preserve the current Responses reader prompt and strict schema. Detector starts Image011 then Image001 and remaining registered panel only if useful; reuse maintained prompt/scorer and native Gemini benchmark reference, require no material loss/caption intrusion even for passing tolerance metrics. Separate genuine assisted-driver confirmation and held-out source required after benchmark success. No prompt or golden change. No paid judge. Sequential independent sessions, no subject record cache, no effort sweep, one equivalent operational repair where material. Retain first failed receipt. Candidate caps 4/5/16. Freeze render before inference, with admission controls and native response custody.

Relevant compromises: C1 OCR and C6 exact table fidelity can only advance on task evidence. C4 detector cannot remove page safety or review. Worktree retained for evidence. No default changes or landing authorized.

## Work log

- 2026-11-17: The exact native model was callable on all three public/synthetic benchmark surfaces. Handwriting Barney missed .99 against both fresh comparators. Detector won two frozen geometry cases but original page12 failed the authoritative 30,000-patch transport limit before inference, so full13 and final assisted cleanup stopped. Source reader matched 56 clear cells and both holds, including an independently frozen 20-cell source. It cost 21.37% less than the established OpenAI Astra reader with the same observed quality.
- Actual SDK replay matched paid request bytes and validated native response with the new explicit reader profile. Actual export replay qualified positive and rejected ambiguous output. The opt-in profile reserves $2 per source read and checks exact input token count before native inference to enforce the reserve. Existing profile and recipe still select the same model.
- 15/15 inference requests, $0.85799975 known, $0 held. All wallets closed. Review package retained in isolated worktree. See [Attempt097](../evals/attempts/097-gpt62-astra-source-fidelity.md).
- 2026-11-17 close-out: Cam approved landing the opt-in table recipe. The close-out uses the native count endpoint via the SDK's public request method, so it works with the locked SDK. The provider-free SDK 1.109.1 replay preserved the exact count and generation requests, rejected excess reservation before inference, exported the 20-cell held-out table with qualification, and held the two ambiguous cells. [Close-out evidence](../evals/evidence/097-astra62/closeout.md).

## Workflow and tenets

- [x] Build complete
- [x] Validation complete
- [x] Story marked done via /mark-story-done
- [x] T0: Ledger, explicit code epochs and hash-bound native/consumer artifacts.
- [x] T1: Real model outputs on the selected inputs, plus independent authored table.
- [x] T2: Registry records three separate lane decisions and stops.
- [x] T3: Exact source holds, source capture and displayed crop limits preserved.
- [x] T4: Explicit recipe swaps only the source reader and keeps actual review and publication gates.
- [x] T5: Checked output HTML and qualification receipt, original native OCR text and crop images.

The evaluation settled all three decisions. The reviewed table reader is the
only runtime addition. The handwriting and crop findings remain in Attempt097.
