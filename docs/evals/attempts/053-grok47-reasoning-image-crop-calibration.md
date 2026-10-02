# Attempt 053 — Grok 4.7 Reasoning Calibration for Image Crops

**Eval:** `image-crop-extraction`
**Date:** 2026-10-02
**Worker model:** GPT-6 Luna
**Subject model / surface:** direct xAI Responses `grok-4.7`, reasoning low/medium/high; maintained Doc Web `image-crop-extraction` detector
**Mission:** Determine whether higher reasoning effort repairs the previously observed Image001 title-art omission and Image059 upper-photo crop misses.
**Registry lineage:** `story_refs: [133, 183, 207, 226, 232, 235, 236, 237, 238, 239]`; `category_refs: [spec:4, spec:8]`; `compromise_refs: [C4]`.

## Prior Attempts

Attempt039 qualified exact Grok 4.7 native strict image/integer output and owner-adapter parity, then reached 11/13 on the frozen low-effort detector (`0.745785`). Source review found a missed stylized title illustration on Image001 and top-edge undercoverage on both Image059 photographs. That attempt used `max_output_tokens=2048` and stopped before a fresh Gemini comparison after failing the detector gate.

## Plan

Run one native synthetic contract probe and one adapter parity probe, then a fresh serial 2-case calibration for each reasoning effort. Keep the maintained prompt, scorer, goldens, high image detail, `store=false`, strict `crop_regions` integer schema, and no-cache behavior. Each arm uses `max_output_tokens=8192`; this differs from Attempt039, so the comparison measures the effort/configuration bundles, not reasoning effort alone. An effort is eligible only if both cases pass and both outputs are source-acceptable. If no effort qualifies, stop before the other 11 detector cases and the Gemini comparator.

The preflight budget ledger reserved up to `$2.098304` per xAI dispatch based on 500,000 input tokens and an 8,192-token output ceiling at the documented long-context rates. A later independent Dossier receipt showed xAI can report combined output above a requested `max_output_tokens`; that invalidates the output-ceiling assumption as a proof of a hard theoretical reservation bound. This campaign had already completed, and none of its eight actual receipts exceeded 1,140 completion tokens or its recorded reservation. There is no evidence of an actual charge above the `$5` campaign ceiling, but the per-dispatch theoretical bound is not independently established by these results. No further provider calls were made after this uncertainty was surfaced.

## Work Log

The run was isolated at `/Users/cam/.codex/worktrees/grok47-docweb-reasoning-20261002`, based on `b90c0da0f95eff852eeaea16419051a0b0a2e10d`. The primary checkout was left untouched. The task, prompt, scorer, golden, and owner provider were unchanged from that base; hashes and byte counts are in the evidence manifest. Exact model identity was `grok-4.7`; all six calibration receipts completed with reported usage and cost, no provider/schema errors, and `store=false`.

| Effort | Case | Score | Assertion | Latency | Cost | Source finding |
| --- | --- | ---: | --- | ---: | ---: | --- |
| low | Image001 | 0.0750 | fail | 8,594 ms | $0.009828 | Returned no boxes; missed the golden's prominent stylized title artwork. |
| low | Image059 | 0.7918 | pass | 9,019 ms | $0.010008 | Found both photographs; source overlay shows upper-boundary undercoverage. |
| medium | Image001 | 0.0750 | fail | 17,717 ms | $0.013296 | Returned no boxes; same title-art omission. |
| medium | Image059 | 0.9180 | pass | 8,078 ms | $0.009606 | Both boxes pass; source overlay shows the predicted boundaries against the goldens. |
| high | Image001 | 0.0750 | fail | 15,374 ms | $0.012156 | Returned no boxes; same title-art omission. |
| high | Image059 | 0.6993 | fail | 13,174 ms | $0.011874 | Both objects found, but localization score is below the scorer threshold. |

Arithmetic means of the two per-case scores are low `0.4334`, medium `0.4965`, and high `0.38715`. Promptfoo's prompt-level aggregate is separately retained in `case-results.json`; it is not the arithmetic mean of the case scores and is not used as a pair-mean claim here. Every effort fails the predeclared per-case eligibility gate because Image001 fails. Source review confirms the golden is the intended target: root reviewer independently verified the decorative title artwork on the source page, consistent with the existing golden. The green outlines show golden boxes; red outlines show the model boxes.

The eight campaign calls settled for total reported spend `$0.075754`: native synthetic `$0.003404`, parity synthetic `$0.005582`, and six image cases `$0.066768`. The final ledger contains eight actual calls plus one reconciled bookkeeping event for an overlapping pre-call hold. That hold links to the completed Image001 low request and does not count a duplicate provider charge. There were no unresolved provider charges, no operational recoveries, and no actual spend above the `$5` hard ceiling. Two coordination-side ledger commands used a relative path from the wrong current directory and initially failed to update the intended ledger; the stale hold was reconciled to the matching provider response UUID, with the event preserved in the final ledger. Raw receipts, the ledger, original ignored Promptfoo result hashes, source/output images, and overlays are retained or referenced by `docs/evals/evidence/053-grok47-reasoning-crop/`.

## Conclusion

**Result:** failed; no effort qualified.

**Score before:** Attempt039 low effort, full detector `11/13`, overall `0.745785`, mean latency `8,059 ms`, detector cost `$0.116280`; the run used a 2,048-token output ceiling.
**Score after:** fresh low/medium/high 2-case diagnostic only; each arm fails Image001. No comparable full-detector score, incumbent control, page-safety score, or adoption claim is produced.

**What worked:**

- Native and owner-adapter synthetic requests returned valid strict integer crop output and exact served model identity.
- Raw provider envelopes and actual reported usage/cost were retained for all eight calls.
- Medium improved the Image059 localization row, but this did not repair the Image001 omission or qualify the effort.

**What did not work:**

- All three efforts omitted the Image001 golden artwork entirely.
- High effort also failed Image059; no effort passed both per-case gates.
- The run did not reach the full 13-case acceptance gate, so no fresh Gemini comparator was warranted.
- The stated full-context reservation is not a proven worst-case bound if xAI may exceed the requested output-token cap. Actual receipts stayed within the recorded reserve; theoretical maximum exposure is not established by this campaign.

**What not to retry without new evidence:**

- Do not repeat these same three effort/configuration arms on this pair.
- Do not treat the partial calibration as detector qualification or page-safety evidence.
- Do not rely on `max_output_tokens` alone as a hard spending bound until the provider contract or a safer admission control establishes one.

**Retry when:**

- `new-approach`: there is a source-grounded visual-grounding change or materially revised model/checkpoint that specifically addresses stylized title artwork, and the owner can establish an enforceable per-request spend bound before additional calls.

## Definition of Done

- [x] Read the target eval's prior attempts first
- [x] Confirm the eval's explicit lineage fields in `docs/evals/registry.yaml`
- [x] Measured a before state from Attempt039
- [x] Recorded after-state per-case metrics
- [x] Updated `docs/evals/registry.yaml`
- [x] Classified major mismatches against the source and golden
- [x] Filled in the conclusion and retry conditions
