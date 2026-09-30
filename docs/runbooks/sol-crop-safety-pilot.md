# Opt-in Sol proposals and source review

Story242 adds a new opt-in proposer. Standard recipes, detector/caption models, C5, benchmark prompt and canonical goldens stay unchanged. Every model pass AND fail needs source review; an unavailable native response cannot be approved away. Rejecting a crop never authorizes source deletion. Authority is an explicit trusted local operator assertion, not secure external authentication. The existing [review gate runbook](crop-safety-review.md) describes release, supersession, recrop and builder enforcement.

The runtime owns `modules/transform/propose_crop_safety_v1/prompt.txt` (SHA256 `9931ded6b7e732687b0889e6959ef9a873e6f459a292c132443db0f6bc9a7371`), extracted exactly from the measured prompt JS (SHA256 `ef4395838929b208fe65f21500d81ade902072bef3f8e53f81ef3d3b83fbc421`). Request parity against saved Attempt048 request068 includes the full-page image first, crop second, both high detail, exact strict four-field schema, gpt-6.1-sol, medium effort, 4096 output tokens and store=false. Replay reproduces that exact body. Future live mode additionally pins `service_tier: default` and requires that served tier: this disclosed pricing/operational difference replaces the benchmark's omitted tier. No retry, tool, fallback or alternate route exists. Terminal identity, envelope, refusal/incomplete, strict output and usage failures close the run and retain raw evidence.

## Preparation and review

Use a new disjoint custody directory. The source map is an operator-verified JSON list of `{source_page, source_image}` for EVERY page, including pages without crops. Paths must refer to the actual native crop source under the explicit source root. Preparation safely normalizes absolute guided paths, retains original manifest/page/portion/map and encoded source/crop/alpha bytes, and writes an incomplete inventory plus operator input templates. Native dimensions/source-pixel geometry and crop dimensions must agree; historical rows without provenance require exact decoded rectangular pixel proof, otherwise they fail closed. Alpha/masked crops retain exact encoded bytes and explicit transform metadata; no implicit resize or mapping to a lower-resolution page is allowed. Alpha copies are auxiliary retained original assets: this slice proposes, binds and publishes only the primary crop, not a separately approved alpha rendition. The guided producer now records its actual high-resolution source and geometry metadata without changing crop pixels.

```sh
PYTHONPATH=. python tools/crop_safety_review.py prepare \
  --manifest INPUT/manifest.jsonl --pages INPUT/pages.ndjson \
  --portions INPUT/portions.ndjson --source-map INPUT/source-map.json \
  --source-root INPUT --custody-root NEW-CUSTODY --run-id NEW-RUN
PYTHONPATH=. python modules/transform/propose_crop_safety_v1/main.py \
  --custody-root NEW-CUSTODY --manifest NEW-CUSTODY/manifest.jsonl \
  --out NEW-CUSTODY/proposals.jsonl --run-id NEW-RUN \
  --mode replay --replay-manifest EXACT-BOUND-REPLAY/mapping.json
PYTHONPATH=. python tools/crop_safety_review.py show \
  --custody-root NEW-CUSTODY --manifest NEW-CUSTODY/manifest.jsonl \
  --proposals NEW-CUSTODY/proposals.jsonl --run-id NEW-RUN \
  --html-out NEW-DISJOINT-REVIEW.html
```

Replay requires explicit hashed request/response bindings and cannot access credentials or network; mock receipts are labelled and require explicitly synthetic test authority. Display works BEFORE authority/completeness and includes all source pages, including zero-candidate pages, source-pixel red boundaries, encoded crops and proposal reasons. Inspect full page ownership/captions, crop edges and missed visuals. Multiple components or absent captions alone do not establish ambiguity; S3 plausibly groups coherently. The model verdict/confidence never substitutes for review.

Copy/edit the generated authority and inventory-review templates outside retained evidence. An operator supplies their own identity/reference/reason, source-completeness assertion, timestamp, all source page hashes, true visual inventory and an explicit action/reason for EVERY candidate. Never set completeness from candidate enumeration. The actions are `approve_current_crop`, `require_recrop`, or `unresolved_ownership`; the latter two hold publication. No synthetic fixture statement represents Cam approval.

```sh
PYTHONPATH=. python tools/crop_safety_review.py initialize \
  --custody-root NEW-CUSTODY --run-id NEW-RUN --operator-input OPERATOR-AUTHORITY.json
PYTHONPATH=. python tools/crop_safety_review.py finalize \
  --custody-root NEW-CUSTODY --run-id NEW-RUN \
  --operator-input OPERATOR-REVIEW.json --proposals NEW-CUSTODY/proposals.jsonl
```

Finalization binds original operator inputs and immutable decisions; release and opted-in builder re-render/validate native request/response contracts and rehash source/crop/row/inventory/authority/decisions. A changed source, primary crop, geometry/row, proposal, native receipt, reviewed page scope or decision invalidates release. Final publication is staged and every approved crop must appear exactly once. Use a new custody/review for recrops and preserve the old originals. Unresolved, incomplete or operationally unavailable inventory produces held diagnostics, no approved images or chapter.

## Offline proof

The fixture generator and `configs/recipes/story-242-sol-crop-safety-offline.yaml` exercise proposal → explicit SYNTHETIC authority/source review → release → chapter builder. Native068/069 are real saved receipts replayed offline; no fresh inference or spend is claimed. The error variant is explicitly mock/incomplete. Use a fresh fixture/run/recipe binding rather than overwriting historical receipts. Final evidence lists the approved, held and error run identities; all calls/spend are zero. The approved output preserves S3/S4 exactly once and the zero-candidate third page. Focused tests include stale/bypassed review, alias/traversal/symlink/hardlink, native failure, scope completeness and original-byte preservation.

## Proposed live pilot — unexecuted

The next approvable step is a two-attempt public synthetic integration pilot, S3 and S4 ONLY, run ID `story242-public-sol-pilot-001`, hard inclusive US$0.50, max_calls=2, no recovery/probe/repeat/fallback. Both cases are exposed fixtures, not heldout model qualification. S3 is plausibly coherent, so report physical/source quality separately from ownership-policy handling; S4's lettering is integral. This proves live receipt plumbing and real operator workflow, not representative scan quality or automatic promotion.

Prepare a NEW custody bundle from the public S3/S4 and text-only-page original inputs in the final fixture (the input manifest's native mapping is proven). Use the `prepare` command above with that INPUT and a new directory, which emits unfilled real-operator templates; DO NOT use/copy its synthetic authority/review assertions. Review the pending display and freeze input/prompt/geometry identities before dispatch. After separate live authorization, the exact live proposer command is:

```sh
PYTHONPATH=. python modules/transform/propose_crop_safety_v1/main.py \
  --custody-root output/runs/story242-public-sol-pilot-001/custody \
  --manifest output/runs/story242-public-sol-pilot-001/custody/manifest.jsonl \
  --out output/runs/story242-public-sol-pilot-001/custody/proposals.jsonl \
  --run-id story242-public-sol-pilot-001 --mode live --cap-usd 0.50 --max-calls 2
```

This command is NOT authorized/executed by Story242's offline build. Standard nonregional rates used for planning are input/cache/write/output US$2/.10/2.50/10 per million. The supported profile is native PNG/JPEG at most2048 pixels per axis, text/schema under6KB, conservative46K input and4096 total output tokens: US$0.155960 reservation per attempt, two attempts US$0.311920, headroom US$0.188080 is NOT extra-call permission. Refresh official rates before any live dispatch. Settlement uses uncached/write maximum rates when native receipt lacks write decomposition, so it is an upper bound, not asserted exact billing. Unknown charges retain full reservations. The durable owner run anchor and ledger prevent copying fresh custody from resetting the same run's exposure; preserve both. The first requested candidate is the access check, not an extra probe. Any quota/transport/identity/schema failure closes the run; do not resend. Existing owner credentials are accessed only by explicit live transport; no account/key changes are proposed.

Only an explicitly designated real local operator can then review every pass/fail and source page and authorize release. No authority is created automatically, no source is deleted, and no automatic runtime promotion is proposed. A future representative source-reviewed determinate/ambiguous heldout campaign would require its own concrete plan and approval.

## September30 approved pilot result

Cam subsequently approved and executed the exact two-case pilot described above. Both fresh strict native proposals pass with source-compatible reasons; two-attempt limit exhausted, upperUS$0.013025, unknown0. [Attempt049](../evals/attempts/049-sol-native-public-smoke.md) and its separate packet retain live receipts and pending full-source review. The earlier unexecuted language describes the original offline build snapshot; it does not negate this later approval/execution. Real operator authority/inventory/decisions remain pending, so no crop release/publication is authorized by these passes alone. No additional calls or default promotion are proposed.

## Actual Cam approval and local publication

Cam subsequently affirmed BOTH exact displayed crops and complete three-page source inventory, and authorized scoped landing. Bound actual operator inputs are in the pilot packet, with current-chat/date evidence, non-synthetic identity and honest custody observation time. Preapproval drafts/held archive stay historical. The new `configs/recipes/story-242-approved-native-pilot-build.yaml` contains only artifact loads, review release and chapter build, **no proposer/API stage**. It binds the exact run ID and reviewed .ndjson bytes; do not rerun/overwrite its historical output. All4 stages succeeded, exact2crop images published once, page3 retained. This local approved publication changes no standard recipe/model defaults and adds no claim of broader quality/promotion. Any changed source/primary crop/geometry or subsequent run needs newly bound review.
