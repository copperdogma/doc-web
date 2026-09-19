# Attempt 038 — Qwen3.8-Omni-Flash direct access stop

**Date:** 2026-09-19
**Campaign status:** Deferred by user on 2026-09-19 because direct access is unavailable.
**Owner:** Story 207; `image-crop-extraction`
**Base:** `9f09aca6ff055d1f9842c0f4ab2e800627f4bdba` (freshly fetched `origin/main`)
**Branch:** `codex/qwen38-omni-flash-20260919`
**Worktree:** `/Users/cam/.codex/worktrees/qwen38-omni-flash-doc-web-20260919`
**Registry lineage:** stories 133, 183, 207, 232; categories `spec:4`, `spec:8`; compromise C4 (converge).

## Decision contract

Cam selected revised Conductor Scout071 item 2. The approved ceiling is
US$0.50 for all qualification, subject, control, diagnostic and judge calls.
Candidate is exact Alibaba Model Studio `qwen3.8-omni-flash`, direct API,
reasoning `low`. This is distinct from the Max and ordinary Flash models in
Attempts 024, 035 and 037; their access/quality does not establish Omni access.

The hypothesis is better localization, grouping/text exclusion, or comparable
quality with better cost/latency on the maintained crop detector. Runtime
`configs/recipes/recipe-onward-images-html-mvp.yaml` remains
`gemini-3-flash-preview`. Historical maintained Gemini evidence is 13/13,
0.9703 (later fresh reference 0.9629); neither was rerun here. The registry's
bounded detector leader is Astra medium at 0.980392, but it is not production
qualified. Passing detector evidence alone cannot select a production winner.

Freeze maintained `conservative-count` semantics, the existing integer
0-1000 crop schema, scorer and goldens. Intended ladder: eligible synthetic
native strict vision and harness parity, Image011 grouping anchor, then full13
only after a passing anchor; require 13/13, overall >=0.95, zero schema/transport
errors. Fresh same-input Gemini comparison only after candidate passes and
within the shared cap. No cache, concurrency one. Strict failure allows at most
one clearly labeled JSON-object diagnostic on an eligible image, never an
adoption/full13 unlock. Page-context/crop-deletion gates are out of scope.

Only owner-established public benchmark images or generated synthetic images
are eligible, with eligibility reverified before transmission. Alibaba's
reported no-training/data-storage posture is not ZDR. No input was sent, and
this stop does not newly establish licensing or private-data eligibility.

## Evidence and stop

The coordinator rechecked the exact official model documentation and public
OpenRouter catalog on 2026-09-19: direct model is API-listed; no exact Omni
router entry was established. References:
[exact model](https://www.alibabacloud.com/help/en/model-studio/qwen3-8-omni-flash),
[structured output](https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output),
[privacy](https://www.alibabacloud.com/help/en/model-studio/privacy-notice).
JSON-object support is documented; strict schema support remains unqualified.
No immutable served snapshot or region/endpoint was established by a response.

Owner credential presence was checked through the required owner wrapper,
using the owner's normal primary `.env` source read-only; no credentials were
copied into this worktree. The following names were all absent/nonempty=false:
`DOC_WEB_DASHSCOPE_API_KEY`, `DOC_WEB_ALIBABA_API_KEY`,
`DOC_WEB_ALIBABA_CLOUD_API_KEY`, `DASHSCOPE_API_KEY`, `ALIBABA_API_KEY`,
`ALIBABA_CLOUD_API_KEY`, `MODEL_STUDIO_API_KEY`. A names-only check of the
wrapper child environment found no names containing `DASHSCOPE`, `ALIBABA`,
`ALIYUN`, or `MODEL_STUDIO`. No values or fingerprints were emitted.

Conductor reports no supported centrally custodied direct Alibaba provider
mapping. This is not proof about arbitrary variables in its vault. No vault
inspection, cross-repo credential borrowing, account provisioning, route
substitution or provider call occurred. Missing configured direct access stops
before an authenticated probe. Do not build an unused adapter or run unrelated
provider discovery while this prerequisite is absent.

Exact credential-presence command (from the primary owner checkout):

```bash
python3 scripts/run_with_doc_web_env.py python3 - <<'PYCODE'
import os, json
keys = ['DOC_WEB_DASHSCOPE_API_KEY', 'DOC_WEB_ALIBABA_API_KEY',
        'DOC_WEB_ALIBABA_CLOUD_API_KEY', 'DASHSCOPE_API_KEY',
        'ALIBABA_API_KEY', 'ALIBABA_CLOUD_API_KEY', 'MODEL_STUDIO_API_KEY']
print(json.dumps({k: bool(os.environ.get(k)) for k in keys}, indent=2))
print('other_alibaba_related_names:', sorted(k for k in os.environ
    if any(s in k.upper() for s in ['DASHSCOPE','ALIBABA','ALIYUN','MODEL_STUDIO'])))
PYCODE
```

Workspace commands: `git fetch origin`; `git worktree add -b
codex/qwen38-omni-flash-20260919
/Users/cam/.codex/worktrees/qwen38-omni-flash-doc-web-20260919 origin/main`;
`git rev-parse HEAD`. Primary checkout dirt and other worktrees were untouched.

## Layered result and spend

| Layer | Result |
| --- | --- |
| Access | Locally blocked: no configured direct Alibaba credential; provider callability unverified |
| Transport | Unqualified / not measured |
| Reliability | Not measured |
| Capability | Not measured; no semantic scores or source mismatches |
| Economics | Response cost/latency not measured; actual provider spend US$0 of US$0.50 |
| Adoption | Defer; no runtime/default change |

All probes, Image011, full13, fresh control, diagnostics, and page-context are
unrun. No raw inference artifacts exist. No secret was injected, so no secret
cleanup was necessary. The initial evaluation pass made no commit/push/merge. The later user instruction
authorizes landing these deferred records; landing identity is reported by the
coordinator.

Do not retry automatically or provision a key. Cam explicitly deferred the
evaluation on 2026-09-19 and may obtain access later. Reopen only on a new explicit
user instruction once an eligible direct Alibaba owner/eval credential and
regional endpoint exist; reconfirm current scope/budget and resume at
access/native strict-contract qualification.
A catalog/pricing update alone does not remove this local access prerequisite.
A different route requires its own scope decision.

## Validation

This is a records-only access stop, not a pipeline behavior change. Registry
parsing, methodology compile/check and whitespace checks validate the durable
record. The system `python3` lacked PyYAML; rerunning build/check with the
existing owner interpreter `/Users/cam/Documents/Projects/doc-web/.venv/bin/python`
passed (registry YAML was parsed by the compiler). `git diff --check` passed.
No runtime suite or driver execution is appropriate; no model quality
or pipeline improvement is claimed. Story 207 remains historically Done; this
is an evidence addendum, not a new completion transition.
