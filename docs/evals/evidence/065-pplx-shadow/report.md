# Final owner verdict — Story246 / Attempt065

**Do not promote this frozen advisory workflow.** A correct low-confidence
Decider warning fell back to the full planner's unsafe clean verdict. Retain
current defaults; no additional paid expansion is justified by unused budget.

Fresh first-document screen,3chapters, before doc02/repeats:

| Chapter | Source gold | Raw/normalized GPT planner | Raw Decider | Guarded result |
| --- | --- | --- | --- | --- |
|001|conformant|conformant|conformant, confidence.99606|conformant; candidate accepted|
|002|format_drift|format_drift|not called: generated convention contradiction|format_drift; planner fallback|
|003|row_semantic_issue|conformant|row_semantic_issue, confidence.42031|conformant; low-confidence planner fallback|

Source003 gives Ada3birth1876; extraction gives1881. Both years survived into
the full planner's actual prompt and Decider state. Root independently verified
source/gold/request/envelopes and the inherited unsafe result. Decider's native
choice is correct (probability.53625), but reported confidence.42031 fails the
frozen.8threshold. No threshold tuning or semantic retry. The safety failure is
in the combined fallback policy, not a newly introduced Decider error.

Raw candidate2/2correct on valid answers, available2/3screenchapters; final
workflow2/3correct,1inherited false-clean/0introducedfalsecleans. Candidate
accepted1/3; accepted useful corrections0. Ch002 was not a candidate miss:
planner canonicalized its fused header while calling it a defect, and the
existing convention-conflict safeguard skipped the call. Full planner2/3.
Remaining15unique chapters and33planned observations unmeasured; all second
repeats and missing-source/ambiguity strata have offline evidence only.

## Layered verdict

- Access/transport: both exact native IDs qualified;5completecalls, no errors,
  refusals or retries. Perplexity response model echo is not hosted weight attestation.
- Capability: Decider correctly recognized the one observed semantic defect;
  two answers are insufficient for independent model superiority. The frozen
  guarded workflow fails its declared safety/utility gate.
- Economics: qualificationUSD.00010488; full plannerUSD.025706;
  incremental sidecarUSD.00007228; measured driver all-inUSD.02577828.
  TotalUSD.02588316/4, unknown0. Sidecar adds.28118%cost to required planner;
  narrow projection94%savings do not transfer to this workflow.
- Timing: full planner8.065s; candidate calls474/457ms; real driver11.186s.
  One document/two candidate calls do not support a stable p95 or production claim.
- Adoption: do not promote this frozen path; preserve default-off experimental
  work. A possible next experiment is offline disagreement-to-review routing,
  separately declared and independently validated before further paid use.

## Configuration, validity and artifacts

Worktree codex/pplx-docweb-shadow-20261006, base19b30b1d0db4a7f3b2e31614ba9846dfdb93355c.
Full planner gpt-4.1-2025-04-14, native Chat Completions JSON-object/temperature0,
max8000output; exact native pplx-decider-v1.1-27b Choice. Serial, no caches or
hidden SDK/model retries, no paidjudge, hardrequest counts andUSD4ledger.
New18chapters across6templated synthetic genealogy documents; source/gold reviewed
before outputs. Full planner inferred conventions, oracle stayed reviewer-only.
Perplexity Decisions retention/training remains unresolved: synthetic-only.

The normal compact path omitted ordinary values/source context. Distinct
DOC_WEB_PPLX_SHADOW_EVIDENCE/EVAL switches add observed content/advisory sidecar;
this declared evaluation configuration is not unchanged production parity.
Default-off dossier/prompt equivalence tested. Initial zero-spend preflight
silently lost sourcepages due missing required PageHtml pagefield; root caught
this in rendered payloads before paid calls. Invalid proof preserved under
invalid-preflight-source-drop. Schema metadata repaired from unchanged reviewed
HTML, then15available/3missing membership, exactsourcebytes, attrs/notes/breaks
and state fidelity verified. Real driver canonical hashes identical for same
mocked planner responses with sidecar off/on/timeout/malformed.

Durable native receipts in native/, paid driver artifacts in paid-artifacts/,
source snapshots and hashes in frozen-source-manifest.json/snapshots/; paired
layers in four-output-results.json, lineage in live-lineage.json, spend ledger,
summary.json and stop.json. Original ignored output/runs artifacts retained.

## Verification and custody

55focused tests pass across candidate, transport, existing Jev, evidence contract
and full planner; scoped Ruff passes. Offline replay verifies70frozen sources,
10native receipts,2guard replays and exactcanonical hashes with zero network.
Root manually inspected source003 and actual paid request/responses plus canonical
conformance/plan/source data. Methodology/whitespace receipts recorded at closure.
Temporary DOC_WEB_PERPLEXITY_API_KEY removed by helper and absence checked by name;
existing owner OpenAI retained in its original custody. No private uploads,
default activation, repair, deployment, commits or pushes. ADR001 remains accepted;
this evaluation does not replace document-wide planning or change its decision.
