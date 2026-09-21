# Optional JEV consistency shadow routing

The `plan_onward_document_consistency_v1` module can run an advisory JEV classifier
**after** saving its normal planner/conformance/issue artifacts. Those artifacts
remain authoritative; no JEV result chooses a repair or suppresses an issue.
Default behavior makes no TypeSafe request.

## Owner configuration

In the owner's ignored `.env`, set these only after choosing to send the relevant
extracted document text to TypeSafe:

```dotenv
DOC_WEB_JEV_SHADOW=enabled
DOC_WEB_TYPESAFE_RUNTIME_API_KEY=
```

Fill the runtime key locally. Run the normal recipe using
`scripts/run_with_doc_web_env.py` so `.env` entries reach the stage subprocess.
The distinct evaluation-only `DOC_WEB_TYPESAFE_API_KEY` is deliberately ignored
by this feature. A runtime key alone does not enable it. No key was provisioned
and shadow was not activated as part of implementation.

Enabling sends compact chapter/page extracted-text examples and matching
planner-generated document conventions to `https://api.typesafe.ai/v1/systemone`.
Examples can include names and personal document text. No original source images,
filesystem paths, chapter titles, authoritative classifications or repair reasons
are included. This is extracted-HTML evidence, not independent source validation.
The TypeSafe vendor states customer requests are not training data; retention/ZDR
is not asserted. Owner activation is the explicit opt-in for that data transfer.

## Limits and behavior

- Exact `jev-1.13.0`, native five-class Choice, no provider redirects or retries.
- At most three eligible chapters per module invocation in dossier order; sixteen
  KiB maximum serialized state per chapter;64KiB maximum response.
- Two-second **caller deadline** around one HTTP request. The daemon doing that
  request may finish after timeout; late results are never applied and delivery
  is recorded as unknown. There is also a two-second socket timeout. At most
  three outstanding attempts can exist per invocation; no retry occurs.
- Reserve the documented64k input-token maximum at$0.042/M before each attempt:
  $0.002688/call, maximum$0.008064/invocation. Unknown usage retains reservation;
  known native usage settles actual input cost. Output tokens are uncharged.
  This is a per-invocation cap, not a global account/monthly cap.
- Missing or ambiguous conventions, oversized state, exhausted chapter budget
  and unavailable runtime key produce explicit coverage/skip diagnostics.
- Explicit `uncertain` stays review-routed regardless of confidence. Other labels
  below0.8 use the already-computed authoritative planner result. Deterministic
  layout evidence overrides a shadow clean/semantic-only proposal to review.
- Provider/contract failure uses the same existing planner fallback. No extra GPT
  call is made; this is shadow routing with observed added JEV cost, not the serial
  narrow-GPT cascade evaluated in Story233. It does not save production costs today.

The separate `jev_consistency_shadow.json` contains ordinal chapter references,
raw class probabilities/confidence, routes, generic reason codes, latency, usage,
known cost and unknown reservations, coverage counts, timestamp/run ID and hashes
of input/plan/authoritative artifacts. It contains no excerpt text or error bodies.
It is atomically replaced; a stale owned sidecar is removed before every attempt
including disabled runs. Sidecar failure cannot invalidate saved planner outputs.

The existing compact dossier already truncates/samples text. Shadow data explicitly
states that limitation. The synthetic eval's accuracy does not transfer to this
runtime input without a representative, owner-approved comparison. Keep this in
shadow; do not use the sidecar to change repair/acceptance behavior.

## Verification

`pytest tests/test_jev_consistency_shadow.py tests/test_plan_onward_document_consistency_v1.py`
checks transport, deadline, bounds, uncertain/low-confidence separation, layout
veto, key isolation, redaction, immutable inputs and stale-sidecar behavior.

`scripts/verify_jev_shadow.py --output-dir output/runs/<fresh-verification-id>`
runs the real driver in disabled/enabled/provider-failure modes with synthetic
inputs and explicit mock providers. It blocks network, scrubs inherited provider
credentials, checks all authoritative artifacts are invariant (excluding run ID
and timestamps), and retains files for inspection. Use a fresh output directory;
previous verification artifacts are not overwritten.
