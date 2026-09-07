# Attempt 035 — Qwen3.8 Max 0902 detector re-evaluation

**Date:** 2026-09-06
**Worker:** Codex owner agent
**Owner:** Stories 207 and 209; spec:4, C4/C5
**Base:** `b67f001481307ed1d4f2a4194436620dda16528b`
**Branch:** `codex/qwen38-max-0902-eval-20260906`
**Worktree:** `/Users/cam/.codex/worktrees/qwen38-max-0902-20260906/doc-web`

## Decision

**Do not adopt the frozen low-reasoning 0902 detector.** The exact new checkpoint
is callable through Alibaba on OpenRouter and passed strict synthetic vision
plus owner-adapter parity. It then repeated the older snapshot's known
`Image011` grouping error: three crop boxes instead of two, scoring `0.6001`
against the unchanged maintained scorer. This is a source-verified semantic
failure, not an API or harness failure. The predeclared differentiator stop
avoided buying a full suite that could no longer clear the required 13/13 gate.

Total provider spend was **US$0.013964 / $0.75**, with three successful terminal
calls and no retries. The full 13-case detector, fresh Gemini control, separate
page-context contract, `page-122-001` safety screen, and 22-case safety suite are
**not measured**. No full-suite score or contemporaneous superiority claim is made.

## Approval, ownership, and provider truth

The user approved Conductor's single Doc Web proposal with the $0.75 total cap.
Pre-spend plans are appended to Stories 207/209, continuing their existing proof
surfaces. The exact checkpoint is distinct from Attempt 024's August snapshot.
The September 2 access stop is Conductor history, not Attempt 032 in this current
checkout (032 belongs to Astra).

Current official endpoint evidence was fetched on September 6 from
[OpenRouter's exact canonical endpoint](https://openrouter.ai/api/v1/models/qwen/qwen3.8-max-20260902/endpoints).
It maps public ID `qwen/qwen3.8-max-0902` to canonical
`qwen/qwen3.8-max-20260902`, with a single Alibaba endpoint, text/image/video
input and text output, 1M context, and advertised strict structured output and
reasoning controls. Input is $2/M, cache reads $0.25/M, cache writes $2.50/M,
output $6/M. [Strict-output documentation](https://openrouter.ai/docs/guides/features/structured-outputs)
requires response_format plus parameter enforcement; both were sent. Endpoint
listing alone was not used as proof of callability.

Only owner-identified public checked-in crop fixtures and a generated square
were used. Provider retention/training uncertainty was disclosed and approved;
`zdr` and `data_collection` filters were omitted, while Alibaba routing,
no fallback, exact identity, and `require_parameters=true` stayed mandatory.
The owner wrapper alone loaded the temporary `DOC_WEB_OPENROUTER_API_KEY`.
Conductor removed that injected variable after the final call and reported
successful cleanup. No other provider credential was configured in this worktree.

## Frozen contract and zero-cost preflight

- Maintained `conservative-count` prompt, normalized bbox `crop_regions` strict
  schema, scorer and user-authored goldens; no tuning or truth changes.
- Low reasoning, hidden reasoning output, 16384 maximum completion tokens for
  the real fixture; 1024 for native and parity synthetic qualification.
- Exact model and Alibaba provider pinned; no subject cache, no model fallback,
  no automatic retry; serial calls at concurrency one.
- Campaign-only task selects one prompt and one explicit provider. It removes
  the unused default judge declaration: every maintained assertion is Python
  structural scoring, with manual source review for semantic verification.
- All 13 unique cases were rendered offline: independent single-user messages,
  one downscaled image each (maximum 2048 pixels), no conversation history or
  implicit judge, unchanged input bytes. The full matrix was not executed.
- A conservative per-call reservation bounds 50k input tokens at the highest
  published input price plus maximum output tokens, checked against $0.75
  before sending. All actual input lengths were far below this reservation.
- Detector advance required 13/13 and overall >=0.95 with zero transport errors.
  The predeclared Image011 screen stops first on the previous grouping error.
  Conditional safety would require separately qualified schema, then the
  page-122-001 differentiator, then 22/22 within remaining budget.

Runtime remains Gemini 3 Flash for detection and GPT-5.5 for page-context.
Maintained historical detector reference is 13/13, 0.9703; current Astra bounded
quality leaders likewise do not waive exact runtime safety gates. Current owner
rules make the user-authored goldens authoritative bounded selection truth;
a second heldout corpus is not mandatory. Generalization and runtime adoption
remain separate limits.

## Observed evidence

| Stage | Outcome | Latency | Reported cost |
| --- | --- | ---: | ---: |
| Native synthetic strict vision | Exact 0902/Alibaba, terminal stop, square bbox [0.25,0.25,0.75,0.75] | 6229 ms | $0.001732 |
| Same synthetic case through owner adapter | Exact 0902/Alibaba, strict schema passes, identical bbox | 6163 ms | $0.001720 |
| Maintained Image011 through Promptfoo | Valid output, 0/1 passed, score 0.6001, 0 errors | 19958 ms | $0.010512 |
| **Total** | **3 calls, no retries, no paid judge** | | **$0.013964** |

Native and parity request-body hashes are identical. All three request bodies
were reconstructed offline and verified against their pre-send SHA256 hashes;
complete envelopes were retained before parsing. Promptfoo was 0.121.1.
The Image011 response used 2931 prompt and 775 completion tokens, including
604 reasoning tokens. Cost comes directly from usage.cost, not an estimate.

### Source inspection and failure classification

The decoded maintained Image011 certificate was visually inspected alongside
its golden and raw response. The model returned the top logo
`[0.36,0.07,0.60,0.24]`, the lower-left seal `[0.11,0.68,0.40,0.90]`, and
adjacent signatures `[0.42,0.71,0.88,0.86]` as three separate regions.
The source-backed golden expects the logo and one combined seal/signatures
region `[0.119804,0.686061,0.876863,0.896667]`.
The maintained prompt explicitly says `Signatures next to seals = ONE combined image`.
The image confirms the seal lies immediately beside the signatures.

Classification: **prompt/pipeline-wrong → model-wrong**, blocking this frozen
detector's grouping requirement. Box-count score is 0.50, mean IoU 0.602,
minimum IoU 0.429, coverage 0.715, total 0.6001. No golden, scorer or semantic
prompt repair is justified. One failed screen does not establish full-suite
quality or an exhaustive model-family verdict.

## Layered verdict and retry trigger

- **Access:** available on the exact approved account/model/Alibaba route.
- **Transport:** qualified for tested strict detector vision shape, native and
  owner adapter; separate page-context schema unmeasured.
- **Reliability:** acceptable observed 3/3 terminal responses, zero errors;
  too small to establish sustained reliability or production concurrency.
- **Capability:** failed the required grouping screen; full detector and
  page-context capability not measured.
- **Economics:** $0.013964 measured total; one real case 19.958 seconds and
  $0.010512. No fresh incumbent or suite-level economics comparison.
- **Adoption:** do not adopt this frozen detector; page-context not advanced.

Retry after a materially revised checkpoint or an independently justified
owner contract change that addresses grouping; an explicit fresh rerun is also
possible. Do not retry the unchanged low arm merely because the route remains
listed, or tune the golden/scorer to rescue it.

## Artifacts, reproduction, and validation

Tracked manifest:
`docs/evals/evidence/035-qwen38-max-0902-manifest.json` includes base, branch,
exact commands, ledger, code hashes, raw sizes/hashes and safe pointers.
Ignored durable raw artifacts live in
`benchmarks/results/qwen0902-20260906/`: endpoint catalog, zero-cost preflight,
three full call envelopes and verified request bodies, synthetic results,
Promptfoo Image011 result, decoded source image, and the exact executed guard.

Run from this worktree through `scripts/run_with_doc_web_env.py`; the manifest
preserves exact commands. Reproduction requires a new run/ledger identity and
new spend authorization because this campaign is complete and its key removed.

The campaign spend guard's rejection of nonfinite reported cost was
hardened after the completed calls; its earlier executed source is retained and
hashed separately. This does not retrospectively change the live code identity.
Ruff formatting/import cleanup followed; exact executed guard and probe helper
sources are both retained with separate hashes. All measured costs were finite,
and the owner adapter already rejected invalid usage. No provider request or semantic behavior was changed by that hardening.

Focused verification: 18/18 offline adapter and guard tests passed, including
invalid/nonfinite costs, budget refusal before network, and unresolved timeout
fail-closed behavior. No pipeline/runtime code changed and the detector stopped
before runtime eligibility, so driver integration and broad unrelated tests
were not run. Methodology compile/check and diff checks are recorded in the
story closeout. No commit, push, merge or default change was performed.


## Authorized check-in verification — 2026-09-06

The subsequent user approval authorized scoped commit and fast-forward remote
main landing. Fresh `make test PYTHON=/Users/cam/miniconda3/bin/python` passed
**959 tests**, with four existing Pydantic deprecation warnings, in 1015.12s.
`make lint`, direct campaign-helper Ruff, methodology compile/check, manifest
hash verification and `git diff --check` passed. No new provider calls occurred.
Primary-checkout inbox was unchanged; unrelated dirty DeepSeek work was excluded.
The primary checkout and its local main ref were deliberately left untouched.
