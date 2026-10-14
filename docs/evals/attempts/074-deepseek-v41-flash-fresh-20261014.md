# Attempt 074 — DeepSeek V4.1 Flash fresh Image011 screen

**Eval:** `image-crop-extraction`
**Date:** 2026-10-14
**Worker Model:** Codex GPT-6
**Subject Model / Surface:** `deepseek/deepseek-v4.1-flash`, low reasoning, maintained conservative-count Image011 lane
**Mission:** Recheck the prior Image011 failure; full-corpus target remains 13/13, overall at least 0.95.
**Registry Lineage:** stories `133`, `183`, `207`, `226`, `232`, `235`–`239`, `249`; categories `spec:4`, `spec:8`; compromise `C4`.

Base: `e44c0a41abf02ad266c10afdf5d95d48bb1b1fe2` (fresh `origin/main`).
Branch: `codex/deepseek-v41-retry-20261014`.
Worktree: `/Users/cam/.codex/worktrees/deepseek-v41-retry-20261014-docweb`.

## Frozen plan

Cam explicitly selected a fresh retry of the previously tested image-crop lane.
This run uses only `deepseek/deepseek-v4.1-flash`, canonical catalog checkpoint
`deepseek/deepseek-v4.1-flash-20260910`, pinned OpenRouter provider `deepinfra/fp8`,
low reasoning, 16384 output tokens, strict `crop_regions`, no fallback, no subject
cache and concurrency one. The maintained `conservative-count` prompt, scorer,
goldens and 13 public/owner-cleared source fixtures are frozen. The attempt excludes
page-deletion, page-context, OCR/literal work and new cases. The first semantic
request is Image011; any decisive scorer or source-completeness miss ends this
candidate run without changing reasoning or tuning the prompt.

Qualification order is one synthetic native image/schema response, identical
owner-adapter parity, then Image011. Only if Image011 passes both the maintained
per-case assertion and source inspection may the full13 run proceed; its gate is
13/13 per-case passes, aggregate at least 0.95, zero transport/schema errors and
source-complete crops. A fresh exact Gemini 3 Flash comparator is conditional on
that gate and a separately feasible reservation; otherwise report candidate-only
evidence and no fresh superiority claim.

## Budget and prior evidence

New owner hard cap: US$0.50 inclusive of requests, controls and any permitted
operational recovery. This new ledger is separate from Attempt036's preserved
US$0.013388168 reported-plus-unresolved exposure; it does not reset or reconcile
that historical ledger. Current request guard reserves up to 50,000 input tokens
at US$0.20/M plus 16,384 output tokens at US$0.60/M, or US$0.0198304 per candidate
request. The plan permits at most 18 candidate requests (2 qualification, 1
Image011, 13 full13, 2 operational recovery), reserving US$0.3569472. It protects
US$0.06 for a possible comparator, for a planned bound of US$0.4169472, leaving
US$0.0830528. The comparator amount is a gate reserve, not a certified worst-case
Gemini bound; a fresh comparator is inadmissible unless its exact conservative
reservation fits the remaining cap.

Attempt036's authorized heartbeat1 low arm qualified native and owner parity,
then scored Image011 0.5551/1 (count 2/2, mean IoU .453, minimum IoU .255,
coverage .595) with zero contract errors. Source review found the logo crop ended
halfway through the logo and the seal/signatures crop omitted upper/right source
area. That is prior model localization evidence, not a golden or numeric-unit
defect. It stopped before full13 or incumbent comparison. This fresh retry checks
repeatability only; it does not erase that miss or reset historical spend.

## Source and contract checks

The current fixture decodes to a 1545x2000 JPEG, SHA-256
`ae3524cb58ac940c912c7885d65ec9d21221415d97d1ea21d97be9615161a860`, matching the
prior canonical source. The golden's two intended regions are logo
`[.376863,.075455,.58,.231061]` and seal/signatures
`[.119804,.686061,.876863,.896667]` in normalized xyxy coordinates. Offline
preflight confirmed all 13 fixtures, one prompt, the Python scorer only, no paid
judge, low effort, 16384 output allowance, exact provider pin, strict schema and
serial topology. Native and adapter response envelopes are saved before parsing.
Both outputs contained valid numeric normalized xyxy values; there was no
malformed numeric or unit evidence. A future raw response violating the schema
is a model contract failure when the native response itself is malformed; a
mismatch introduced by the owner adapter/parser is an owner-contract failure.

Endpoint and pricing evidence captured on 2026-10-14 is in the ignored run
directory alongside hashes and request/response envelopes. DeepSeek official
references: https://api-docs.deepseek.com/quick_start/pricing/ and
https://api-docs.deepseek.com/guides/thinking_mode/. OpenRouter endpoint metadata
is evidence of route listing only; actual pinned callability and served identity
must be verified by the native response.

## Conclusion

**Result: failed for source-complete detector eligibility.**

**Score before:** Attempt036 Image011 `0.5551` (one case; full13 not run).
**Score after:** Image011 scorer `0.7171` (one case); source-complete gate failed, full13 unmeasured.
**Latency / cost:** native `7568 ms / $0.00020902`; parity `10569 ms / $0.00044674`; Image011 `43202 ms / $0.00155442`; total `$0.00221018`.

**What worked:** Exact pinned route qualified native strict vision and owner parity; all three calls returned valid usage with zero reported cached tokens.

**What did not work:** Both Image011 boxes omitted source-visible artwork. The one-case scorer pass did not establish the full13 `>=.95` gate.

**What not to retry without new evidence:** The same V4.1 checkpoint with the same prompt, any different reasoning effort, or another provider route; the source-backed localization miss is decisive.

**Stop after Image011 source-completeness failure.** Native synthetic vision
qualified exact served ID/provider, strict schema, terminal stop, and valid
usage in 7,568 ms at `$0.00020902`. Identical owner-adapter parity qualified in
10,569 ms at `$0.00044674`; native and parity request hashes match. Both had
zero cached prompt tokens. The no-cache Promptfoo Image011 call completed in
43,202 ms at `$0.00155442`, with one assertion pass, zero errors, and a one-case
score of `0.7171` (count 2/2, mean IoU `.649`, min IoU `.472`, coverage `.769`).
That passes the scorer's individual `.70` threshold only; it is not a 13-case
aggregate score or the `>=.95` full13 gate.

The output boxes were logo `[.38,.04,.62,.18]` and seal/signatures
`[.12,.70,.83,.91]`. Source overlay inspection shows the logo box cuts off the
lower artwork and year; the lower box starts below the seal's top points and
ends before the right-hand signature/rule extent. The current source/golden
geometry confirms these are source-completeness misses. Classification:
**model-wrong localization**, not owner-contract or golden/source error. The
coordinates are valid normalized floats in `[0,1]`; no malformed numeric/unit
output was observed. The predeclared stop rule therefore ended the run before
full13 and before any fresh Gemini comparator.

Cam's 2026-10-14 stop instruction is explicit: do not run another DeepSeek
V4.1 checkpoint evaluation, including a different reasoning effort or provider
route, unless Cam explicitly reverses that instruction. A changed checkpoint,
route availability or effort setting alone does not authorize another run.

**Retry when:** Cam explicitly reverses the no-further-V4.1 instruction. This
does not block separately authorized evaluation of other subject models.

This new run settled `$0.00221018` across three successful calls, with zero
unresolved reservation and no control/judge spend. The new inclusive owner cap
was `$0.50`; this does not reconcile or reset Attempt036's separate historical
`$0.013388168` reported-plus-unresolved exposure. Temporary
`DOC_WEB_OPENROUTER_API_KEY` was removed with the Conductor helper, and its
absence was verified. `27` focused offline owner adapter/substrate tests passed;
new attempt adapter/probe syntax and the 13-case task manifest passed offline
preflight.

The complete current-attempt source hashes, commands, raw response hashes, ledger,
fixture identity, source overlay, stop decision and cleanup evidence are in
`docs/evals/evidence/074-deepseek-v41-fresh-manifest.json` and the ignored raw
directory `benchmarks/results/deepseek-v41-fresh-20261014/`. Image011 output JSON
and raw request/response files are mode `0600`. The tracked overlay is
`docs/evals/evidence/074-image011-source-overlay.jpg`; a raw run copy remains in
`benchmarks/results/deepseek-v41-fresh-20261014/`.
No runtime defaults, maintained prompt/scorer/golden, commits or pushes changed.

## Definition of Done

- [x] Read prior attempts and maintained registry lineage
- [x] Confirmed the existing baseline and recorded this attempt's one-case measurements
- [x] Updated `docs/evals/registry.yaml` and classified the source mismatch
- [x] Recorded exact stop conditions, future V4.1 restriction, and evidence manifest
