# Attempt 027 — Ox Alpha evaluation

**Eval:** `image-crop-extraction`, conditionally `crop-validation` and `crop-page-level-deletion-gate`
**Date:** 2026-08-22
**Worker Model:** Codex GPT-5
**Subject:** OpenRouter `stealth/ox-alpha`, provider `Stealth`

## Decision

**Defer; capability not measured.** OpenRouter's authenticated catalog exposed
the exact model and one `Stealth` endpoint, but the endpoint could not satisfy
the required fail-closed routing and strict-output request. Both the native
strict text probe and the generated synthetic-image strict probe returned HTTP
404 `No endpoints found that can handle the requested parameters` before a
subject response. No checked-in fixture, one-case PromptFoo smoke, maintained
13-case detector, 40-case crop-only validator, or 22-case page-context gate ran.
This is an access/transport-policy block, not model-quality evidence.

No runtime default, maintained provider, prompt, scorer, golden, or production
code changed. The existing Gemini 3 Flash detector evidence remains the eligible
maintained reference (`13/13`, `0.9703`), and the conditional C5 surfaces remain
not measured for Ox Alpha.

## Decision contract

- Exact route: OpenRouter `stealth/ox-alpha`; do not substitute another slug,
  tier, snapshot, or provider.
- Surface: Story 207's maintained `image-crop-extraction` detector using
  `conservative-count`, public/checked-in fixtures, strict integer `0-1000`
  bounding boxes, no cache, and concurrency `1`.
- Frozen detector entry gate: `13/13`, `overall >= 0.95`, zero provider/schema
  errors, exact served identity, terminal success, and attributable usage/cost.
- Progressive follow-ons: only after the detector passes, run the maintained
  40-case `crop-validation` gate and then the 22-case
  `crop-page-level-deletion-gate`; their hard contracts are `40/40` and `22/22`.
- Candidate configuration: mandatory reasoning at supported `low` effort,
  hidden reasoning output, `max_tokens=16384`, API-enforced strict JSON Schema,
  provider pinned to `Stealth`, fallbacks disabled, required-parameter routing,
  data collection denied, and per-request ZDR.
- Total spend cap: US$0.75. At most two evidence-led transport/configuration
  repairs. No private payload, default change, commit, push, or deployment.

## Provider and privacy evidence

Authenticated OpenRouter discovery on 2026-08-22 returned exact model
`stealth/ox-alpha`, 1,048,576-token context, 131,072 maximum completion tokens,
text/image/video input, text output, and zero-priced prompt/completion tokens.
The catalog lists `response_format`, `reasoning`, `reasoning_effort`, tools, and
sampling controls. The sole endpoint is `Stealth | stealth/ox-alpha`; its
`data_policy` is unspecified. Catalog presence therefore proves discovery, not
eligible privacy or strict-schema transport.

The eval-only OpenRouter adapter retained the existing fail-closed route:
`allow_fallbacks=false`, `require_parameters=true`, `data_collection=deny`, and
`zdr=true`. A separate strict integer crop contract was added and locally
validated; existing float and page-context contracts are unchanged. Both
zero-priced provider probes stopped at the router with the same HTTP 404 before
inference. Relaxing ZDR, data denial, provider pinning, required-parameter
routing, or strict output would weaken the predeclared production contract and
was not authorized.

## Progressive results and spend

| Stage | Result | Spend |
| --- | --- | ---: |
| Authenticated catalog and endpoint discovery | exact model found; one endpoint; policy unspecified | `$0.000000` |
| Native strict text probe | router 404 before inference | `$0.000000` |
| Generated synthetic-image strict probe | router 404 before inference | `$0.000000` |
| One-case PromptFoo parity | not run | `$0.000000` |
| Maintained 13-case detector | not run | `$0.000000` |
| 40-case crop-only validator | not run | `$0.000000` |
| 22-case page-context gate | not run | `$0.000000` |
| **Total** | **no successful subject call** | **`$0.000000`** |

## Provenance and validation

- Clean base HEAD: `009afed44da2494273983449b73c9f4c0a5cde37`
- Detector task SHA-256: `7edae5fe3c935517396a8d37cd8f148cb2b592ed4d206168dbb62273d758cf3e`
- Prompt SHA-256: `bca281e0fbe547e3f3ef049b436d87c73ed7bb066e86f51145fb444b48211b64`
- Scorer SHA-256: `7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7`
- Golden SHA-256: `2ac0a8f01e00a252439da1f4827a85bc5118bf96460a3ff1780e642eafc60f90`
- Eval-only adapter SHA-256 after integer-contract addition:
  `0814cf8fa3d360ae10a3f86af8a86cb2e3ab3317414313a22d8ec8a3bcccbf03`
- Ox Alpha provider config SHA-256:
  `b5859b7a8a95e4636fbac74d7fbc7f3977f01b85cf9e3a94a45f90b7e0d968d3`
- Focused adapter/environment tests: `10 passed`; focused Ruff passed.
- PromptFoo CLI resolved through `scripts/run_with_doc_web_env.py` before calls.

## Layered verdict

- Access: **constrained** — authenticated discovery succeeds, but no eligible
  endpoint accepts the required request contract.
- Transport: **blocked** — strict schema and privacy-preserving routing never
  reached a subject response.
- Reliability: **not measured**.
- Capability: **not measured**.
- Economics: catalog price is zero, and observed spend is `$0`; value cannot be
  judged without valid responses.
- Adoption: **defer**. Retry only when OpenRouter exposes an endpoint that can
  honor the same fail-closed privacy and strict-output contract; do not relax the
  contract or reinterpret this transport block as a semantic failure.
