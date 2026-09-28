---
title: "Sonnet 5.5 maintained detector and handwriting evaluation"
status: "Done"
priority: "Medium"
ideal_refs: ["Fidelity to Source", "Eval Before Build"]
spec_refs: ["spec:1", "spec:2", "spec:4", "spec:8", "C4", "C5"]
adr_refs: []
depends_on: ["237"]
category_refs: ["spec:1", "spec:2", "spec:4", "spec:8"]
compromise_refs: ["C4", "C5"]
input_coverage_refs: ["handwritten-notes", "image-directory-scans"]
architecture_domains: ["ocr_and_extraction", "illustration-extraction"]
roadmap_tags: ["model-evaluation"]
legacy_system: ""
---

# Story 238 — Sonnet 5.5 maintained evaluation

## Decision contract

User authorized direct exact `claude-sonnet-5-5` comparisons up to US$5 total. Base747b376, isolated codex/sonnet55-eval-20260928. Public Onward fixtures plus two public LOC handwriting scans only. Standard provider retention/no training default, ZDR unverified. Existing owner keys via wrapper; no copying. No commit/push/default/deployment.

Detector native integer schema and lossless owner adapter: medium adaptive,4096 output; frozen conservative-count prompt/scorer/goldens. Native synthetic qualification then Image011 anchor and full13 vs fresh Gemini3 Flash maintained normalized prompt/config; require overall>=.95 and pass_rate>=.90. Independent handwriting actual image-entry driver OCR seam, same hints/prompt/resize2048/scorer/goldens, Sonnet medium adaptive and Gemini3.7 maintained default medium,16384 output each; require >=.99 EACH. Both fixtures run regardless of detector failure. Story191 only unblocks after stronger substrate and its broader image/PDF synthetic regression proof; this two-case screen cannot close191.

Conditional page-context follows ONLY after detector maintained prerequisite clears: native schema then page122001, full22 vs fresh GPT5.5 Responses none/auto. Require22/22 and no false-safe. C5 remains independently owned and cannot be deleted by validator success. No post-score tuning; up to two operational repairs only for transport/truncation/harness faults, preserving failed calls. Current best historical detector Sol.992731 (13/13) and runtime Gemini3 Flash; page configured GPT5.5; handwriting Attempt026 Gemini3.7 .981622/.985233. Root publication/full-corpus OCR proof deferred because bounded model screen is selected.

## Spend and topology

Serial no-cache independent single-user inputs, no conversation reuse and no active LLM judge. Source pages1545x2000, large safety crop4244x2958, OCR originals640x502 /638x1024. Full input bound conservatively20k/image+6k other tokens; full output allowance per request. Official Anthropic vision ceiling4784 visual tokens per image permits tighter bound if needed; bounds may tighten only from source-backed sizing. Every request reserves before HTTP; complete raw response saved before parsing; actual usage settles including thoughts/cache creation. Unknown billing retains reservation. Admission checks hard$5 after every call; stages admitted using settled spend. Native probes plus detector arms/OCR fit$5 even at provisional maxima; safety broad run conservatively re-admitted after settlement and qualified screen, never fake a budget pass. No retries on semantic failures.

OCR seam requires a narrow Anthropic compatibility repair: exact Sonnet5.5 omits unsupported temperature, uses adaptive/medium, disables automatic SDK retries, rejects wrong served identity/incomplete output. Semantic prompts/hints/cleanup stay frozen. Driver recipe ends after genuine OCR page_html artifact to exclude unrelated downstream calls.

## Acceptance criteria

- [x] Native/adapter contracts, frozen source identity, full attributable raw receipts and settled costs retained.
- [x] Task winners and source-backed mismatch classes determined independently.
- [x] Registry/attempt/work log plus focused validation complete.

## Work log

- September28: Created clean remote-base worktree; existing owner Anthropic/Gemini/OpenAI key names present. No values copied. Source review confirms LOC literal misspellings and Image011 combined seal/signature golden. Predeclared medium adaptive Sonnet arm, bounded operational recovery, real driver OCR seam and serial HTTP spend guard.

- September28 result: Attempt045 rejects detector substitution on Image011 range-contract failure; full13/safety22 not measured. Independent Sonnet/Gemini real OCR scores are.982734/.982830 and.982014/.985832, all below.99. No OCR winner, no runtime/default/C5 change. Known eight-call spend$.05568125; one quarantined SDK custody fault estimate$.008552 and conservative$.23 exposure, total maximum$.28568125/$5. Fresh complete OCR receipts retained; previous missing SDK attempts had no inference. Shared-client branches plus metering/native/OCR/harness focused tests pass; source scans and output HTML reviewed.


## Workflow gates

- [x] Build complete for selected bounded evaluation.
- [x] Validation complete:36 focused offline tests, changed tooling Ruff, methodology build/check, all116 reproducibility member hashes and diff hygiene.
- [x] Story marked done via /mark-story-done; Story191 remains Blocked. No runtime default change.


## Central Tenet verification

- [x] T0 Traceability: hashes, complete retained responses and explicit custody-fault quarantine.
- [x] T1 AI first: extraction stays model-owned; no handwritten correction code.
- [x] T2 Eval before build: measured contract and quality failures block adoption.
- [x] T3 Fidelity: source-visible mismatches reported; neither model claimed to meet 0.99.
- [x] T4 Modularity: isolated provider/task/recipe arms; maintained defaults retained.
- [x] T5 Inspect artifacts: source scans, Image011 and all four scored OCR HTML outputs inspected.
- [x] Documentation updated: Attempt045, registry, Story191, generated methodology and CalVer changelog.

## Scoped closeout

2026-09-28: /finish-and-push invokes /mark-story-done verification for the already-completed bounded evaluation. All three acceptance criteria, workflow gates and tenets are evidenced; dependency Story237 is Done. No new architectural decision or ADR is required for the existing client compatibility seam. Reuse unchanged36 focused tests and source/HTML review; check new records, retained116 archive members, metadata and diff hygiene. Primary checkout has no inbox-only change. Prepare the scoped candidate against unchanged origin/main747b376; push awaits coordinator global preflight release.
