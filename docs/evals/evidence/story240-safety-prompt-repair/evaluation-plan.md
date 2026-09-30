# Story240 — Revised safety prompt evaluation plan

**Plan only, September29,2026. No provider calls or fixture generation. Proposed hard cap: US$18 inclusive of qualification, subjects, controls, operational recovery and unknown-charge reservations.** The original campaign's US$14 cap does not authorize this new run; separate execution approval is required. Worst planned reservation before recovery is **US$15.931930**, so retaining14 would not admit the whole declared comparison.

## Decision and frozen contract

Measure whether the revised source-boundary/neighbor/uncertainty contract reliably rejects unsafe crops while preserving valid unified/compound visuals at the selected configurations. This is a repaired-contract comparison, **not a causal thinking-level sweep**: candidate none/low arms are absent. One screen or synthetic diagrams cannot qualify production safety.

Freeze `benchmarks/prompts/validate-page-level-crop.js` at SHA256 `ef4395838929b208fe65f21500d81ade902072bef3f8e53f81ef3d3b83fbc421`. No post-outcome prompt, settings, golden, scorer or fixture tuning. The strict `page_context_validation` schema and `crop_validation_scorer.py` remain unchanged; a manual source-backed reason review supplements labels, with zero LLM judge spend. Goldens remain authoritative; errors or ambiguity are quarantined and diagnosed on saved outputs, never silently corrected to make an arm pass.

| Arm | Endpoint and identity | Requested effort | Total output cap | Image detail |
|---|---|---|---:|---|
| Luna | Direct OpenAI Responses `gpt-6-luna`; exact served ID required | medium |4096|high|
| Sol6.1 | Direct OpenAI Responses `gpt-6.1-sol`; exact served ID required | medium |4096|high|
| Maintained comparator | Direct OpenAI Responses `gpt-5.5`, documented served snapshot `gpt-5.5-2026-04-23` | none |2048|auto|

Control preserves its maintained settings, so output allowance/image detail differ intentionally. Compare identical instructions, source/crop bytes, order, schema and cases; report these operational differences instead of claiming effort-only fairness. Capture requested and served identities, actual reasoning/cache/write tokens, terminal status, raw output, latency and cost. Medium may produce zero reasoning tokens on an individual call.

Public established benchmark scans and new synthetic diagrams only. No private inputs, account changes or new credentials. Use owner-configured credentials only through the existing wrapper. Standard direct nonregional route, under272K tokens, `store:false`; existing disclosed retention/no-training posture, unverified ZDR. No tools, fallback models or paid judge.

## Progressive stages and admission

1. **Qualification: at most3 calls, one per arm.** Recheck each exact native two-image strict-schema/terminal contract with tiny generated square images and the frozen revised prompt, sufficient configured output. These are transport probes, not semantic evidence or synthetic confirmation cases. Reuse exact native/parity proofs only if unchanged adapter/schema/route makes them applicable; released reservations are bookkeeping. Start fresh owner-harness parity on the first screen row. Invalid usage/identity, partial output or lossy requests cannot be scored.
2. **Maintained exposed screen:6 calls per arm,18 total.** Independently repeat `page-122-001` three times, then one call each on `page-009-000` unified-photo pass, `page-126-001` integral-plaque-text pass and `page-127-000` compound-monument-photo pass. All are exposed maintained corpus, never described as held-out. Fresh calls, no cache, independent single-user sessions. No reuse of one scored screen row as a new full22 result.
3. **Full maintained gate:22 fresh calls per admitted arm, maximum66.** Each arm advances independently only after all three neighbor repetitions correctly reject the unrelated visual, all three positive examples pass, and source-backed reasons support the intended contract. An incidental-mark rejection is insufficient neighboring-visual evidence. A valid false-safe stops that arm; a valid false-reject fails its declared screen rather than being tuned away. Stop unadmitted arms before full22. The maintained comparator follows the same admission rule and can fail; no presumed winner. Screen/control failures do not block another admitted arm. Full22 requires22/22, zero false-safe and zero false-reject; preserve all reliability/transport errors separately.
4. **Fresh synthetic confirmation:6 calls per full22-passing arm, maximum18.** Build, source-inspect and freeze all six cases below **before the first provider call**, with fixed goldens and no scored calibration. They are held out from prior paid evaluations but designed around known failure classes, so narrow synthetic generality evidence only. A full22 failure stops that arm's confirmation stage. All six labels and source-reasons must match; uncertainty must be disclosed as uncertainty, not invented text/blank content. Require zero unresolved transport/schema/identity/usage errors before stage admission; successful recoveries remain reported as reliability faults, not erased.

A semantic source-backed failure is a stop, not permission to add an effort arm or keep tuning. Repair demonstrated adapter/time/token/receipt faults within the stated recovery reserve, preserving originals. If output budget changes can alter answer behavior, declare a matched configuration repair before rerunning affected rows. No hidden SDK retries. Unknown charges retain full reservations. A hard-budget/eligibility boundary stops affected sends; no cap transfer from other projects.

## Six fresh diagram pairs — preparation still required

Use deterministic, locally rendered plain SVG→PNG diagrams, not edits to existing scans or generated model images. Every full page is1000×1000px RGB; crop coordinate rectangles below are pixel extraction bounds for fixture creation only and **never added to the model prompt**. Fixed simple fonts/shapes/colors; no personal names. Freeze final source/crop PNG bytes, rendering version, construction SVG, coordinates and label JSON before inference. Manual owner source inspection/adjudication must confirm each declared ownership/blank/text claim; unresolved fixtures are withheld and the exact plan revised before calls, never fake coverage.

| ID | Exact proposed source/crop construction | Frozen expected label and reason |
|---|---|---|
| S1 coherent multipart | One outer frame `[100,180,900,650]` encloses two diagram panels with connecting arrows and one shared caption below the frame. Crop the whole frame, excluding its caption. |pass; panels form one source-unified figure; no external text/blank|
| S2 separate caption-free neighbor | Two separately framed diagrams at `[100,180,430,650]` and `[570,180,900,650]`, each with its own caption below. Crop `[100,180,900,650]` containing both diagrams but no captions. |fail; separately presented neighboring visual, despite no leaked text|
| S3 unresolved ownership | Two similar unframed geometric fragments centered at x350/x650 on plain paper, without caption, connector, enclosing boundary or other grouping cue; overlapping faint strokes make a shared visual versus neighbor indeterminate. Crop `[220,200,780,700]` across both. |fail for uncertainty/non-acceptance pending review; reason acknowledges absent ownership evidence; no invented page text or excessive blank. This case requires explicit manual owner adjudication of intended ambiguity before freeze.|
| S4 integral text | One bordered badge at `[250,220,750,720]` containing the words `FIELD STATION` as part of its design; a separate page caption sits below at y800. Crop the badge only. |pass; text is integral to one visual, caption excluded|
| S5 external text | One framed illustration at `[250,220,750,620]` with separate caption below at y680. Crop `[250,220,750,710]`, including that caption. |fail; external page text visible, not integral image text|
| S6 excessive blank | One complete high-contrast square diagram at `[400,400,600,600]` on otherwise empty page. Crop `[100,100,900,900]`. Blank paper occupies93.75% of crop. |fail; excessive page margin, no page text; complete visual alone does not make crop acceptable|

S3 is **policy-defined non-acceptance**, not a source-confirmed physically bad crop. Report its uncertainty handling separately from leakage false-safe/false-reject rates; a bare matching fail label without an honest uncertainty reason does not pass.

S3 must be constructed with enough drawn content that empty margin alone does not exceed40%; inspect measured blank-area estimate before freezing. If the proposed geometry does not meet that requirement, adjust it **before any inference**, document the construction change, then freeze the actual bytes/golden. S1/S2 source boundaries/caption grouping, not a component/subject count, determine ownership. Separate diagrams are narrow semantic probes; representative book scans and an actual driver/publication path remain necessary before production promotion. No claim that these six unbuilt fixtures already provide fresh coverage. Manual owner source review is ordinary authorized setup; ask the user only for a genuine unresolved label/preference disagreement, not a ceremonial fixture approval.

## Zero-cost execution readiness required before approval is consumed

Prepare a NEW run ID, NEW ledger and configurable campaign guard output path; do not reuse historical `thinking-safety-20260929` or fixed047 topology destinations. Existing closed ledger intentionally refuses sends. No harness-framework expansion is needed: adapt the established owner guard/task pattern narrowly when execution is approved.

Resolve all planned cases/messages and native bodies without inference, including repaired text and newly frozen diagrams. Verify one user message, two correctly ordered lossless source/crop images, explicit strict schema, selected arm/model, independent repetitions, concurrency1, no subject cache, no implicit judge and the actual rerunnable command. Record adapter/prompt/schema/scorer/golden/fixture SHA256s and versions. The original047 evidence stays immutable. Correct topology before paid calls. Preflight provider pricing/eligibility anew on execution day. Treat structural/render checks as compatibility evidence only.

## Conservative reservation arithmetic

Current official model pages verified by coordinator September29: [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [Sol6.1](https://developers.openai.com/api/docs/models/gpt-6.1-sol), [GPT5.5](https://developers.openai.com/api/docs/models/gpt-5.5). Standard direct nonregional pricing, per million input/cache/cachewrite/output: Luna `.10/.01/.125/.50`; Sol6.1 `2/.10/2.50/10`; GPT5.5 `5/.50/5/30`, using5 as conservative write bound. No long-context uplift admitted.

The existing conservative envelope remains **46,000 total input tokens per two-image request**:20,000 per image plus6,000 for text/instructions/schema. The revised prompt remains comfortably within6K; preflight must verify exact rendered text/schema and image eligibility before dispatch. Reuse this bound for tiny diagrams/probes rather than claiming lower cost from dimensions without token evidence. Reserve highest input/write rate plus every allowed output token. Settle complete validated usage after each receipt; retain unresolved reservations in exposure. A bound violation closes further sends and is an operational failure, not semantic evidence.

| Arm | Worst reserved per call |
|---|---:|
| Luna | `(46000×.125 +4096×.50)/1e6` = **$0.007798** |
| Sol6.1 | `(46000×2.50 +4096×10)/1e6` = **$0.155960** |
| GPT5.5 | `(46000×5 +2048×30)/1e6` = **$0.291440** |
| One complete3-arm case | **$0.455198** |

| Stage | Maximum calls | Worst reservation |
|---|---:|---:|
| Qualification |3|$0.455198|
| Screen:3 neighbor repeats +3 positives, per arm |18|$2.731188|
| Full22, fresh, all three arms |66|$10.014356|
| Six fresh synthetic cases, all three arms |18|$2.731188|
| **Planned calls** |**105**|**$15.931930**|
| **Two global operational recovery attempts at worst arm reservation** |2|**$0.582880**|
| **Maximum planned plus recovery reservation** |**107**|**$16.514810**|
| **Unallocated hard-cap headroom** | |**$1.485190**|
| **Hard inclusive ceiling** | |**$18.000000**|

At most two global recovery requests, each conservatively reserved at the most expensive arm (`2×.291440=$.582880`). The remaining$1.485190 is unallocated protection for unknown-charge accounting, not authority to add cases, effort arms or further retries. Unknown receipts keep their reservation; repeated transport faults or exhausted recovery halt the affected arm. Every attempted request counts, including probes/retries/failed responses. Estimated usage-priced spend is not an account invoice. Stopped arms release unused planned stages; no unrun row is counted as a failure or pass.

## Report and remaining authorization

Return per-arm sample counts, all repeat outcomes, false-safe and false-reject rates, source reason adjudication, requested/actual reasoning tokens, valid-response quality versus end-to-end reliability, latency, subject/control/probe/retry costs, unknown reservations and full provenance. Adoption requires all relevant quality gates plus representative/runtime proof and separate product authorization. No current prompt-repair claim means pipeline safety has improved.

This plan prepares a reviewable comparison only. Fixture construction/adjudication, new run/guard/task setup and final zero-cost topology are still required before paid execution. Approving this plan for execution would authorize up toUS$18 for this exact scoped run, not a default change, rollout, commit, push, private data or broader model tournament.
