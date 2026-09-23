# Attempt 040 — MiMo V2.6 DeepInfra access stop

**Date:** 2026-09-22
**Owner:** Story 207 / `image-crop-extraction`
**Base:** `f9dcf158bff0eea6f7695c592d777db83e1cc800`
**Route:** OpenRouter `/chat/completions`, exact requested model, pinned
`DeepInfra`, `allow_fallbacks=false`, `require_parameters=true`, strict
integer crop schema, public/synthetic fixtures only, serial no-cache execution.

## Decision contract and preflight

Scout 074 handle 1 selected both `xiaomi/mimo-v2.6-flash` and
`xiaomi/mimo-v2.6-pro`, with a combined hard cap of US$0.50. The maintained
decision is whether either is a cheaper accurate detector alternative to
Gemini 3 Flash. The frozen ladder was native synthetic integer-image contract,
owner harness `Image011`, then full 13 only after a passing anchor (`13/13`,
overall `>=0.95`); a fresh Gemini control was conditional on that success.

The zero-cost rendered-matrix and unit preflight passed. It confirmed two
candidate arms only, `Image011` only, concurrency one, exact DeepInfra pin,
no fallback, strict integer schema, and a conservative US$0.02353176 reserve
per call. Existing adapter behavior initially sent `reasoning.exclude=true`
but not `reasoning.enabled=false`. The first valid Flash response reported
305 reasoning tokens, so it is retained as an unqualified configuration,
not evidence that reasoning was off. The adapter then added the explicit
`enabled=false` request before further qualification.

## Stop evidence

| Arm | Stage | Result | Spend |
| --- | --- | --- | ---: |
| Flash, prior `exclude`-only request | native synthetic strict schema | Exact Flash / DeepInfra, terminal strict output; 42,526 ms; 305 reasoning tokens | $0.0001036 |
| Flash, explicit `enabled=false` | native synthetic strict schema | HTTP 429, `upstream_provider_shared_pool`, `engine_overloaded` | unknown |
| Pro, explicit `enabled=false` | native synthetic strict schema | HTTP 429, `upstream_provider_shared_pool`, `engine_overloaded` | unknown |
| Flash owner harness `Image011` | one-case serial screen | four HTTP 429 envelopes before the stop was observed | unknown |

The six 429 response envelopes contained no served identity, terminal output,
usage, or cost. They are transport/capacity evidence, never semantic misses.
The harness's repeated capacity calls were an orchestration defect, not valid
retry evidence. Their conservative reserve exposure is US$0.14119056; with the
attributed US$0.0001036 it remains below the US$0.50 cap. No alternative
provider, fallback, full13, Gemini control,
judge, crop-only, or page-context call was made. Flash and Pro capability,
reliability, and economics beyond the single unqualified native Flash call are
not measured. Actual attributed spend is US$0.0001036 of US$0.50.

## Layered verdict

| Candidate | Access | Transport | Capability | Adoption |
| --- | --- | --- | --- |
| MiMo V2.6 Flash | constrained by DeepInfra shared-pool capacity | blocked before qualified reasoning-off harness parity | not measured | defer |
| MiMo V2.6 Pro | constrained by DeepInfra shared-pool capacity | blocked at native reasoning-off contract | not measured | defer |

No default changed. Reopen only with a new explicit approval and changed route
availability evidence; do not use this capacity stop to infer model quality.
Protected raw envelope hashes and safe regeneration instructions are in
`docs/evals/evidence/040-mimo26-openrouter-deepinfra-manifest.md`.
