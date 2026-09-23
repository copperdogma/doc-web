# Attempt 040 MiMo V2.6 protected artifact manifest

Ignored public/synthetic raw envelopes are retained at
`benchmarks/results/mimo26-20260922/`; no authorization header or credential
is included in this manifest. The current ledger records seven calls:
US$0.0001036 attributed spend plus US$0.14119056 conservative exposure for
six no-usage capacity envelopes, under the US$0.50 cap.

Regenerate only from base `f9dcf158bff0eea6f7695c592d777db83e1cc800`, with
the temporary owner OpenRouter variable through `scripts/run_with_doc_web_env.py`,
the exact campaign task, and no fallback. Do not rerun without fresh approval:
the final two calls stopped on `upstream_provider_shared_pool` capacity.

| Source | SHA-256 |
| --- | --- |
| `benchmarks/providers/mimo26_budgeted.py` | `0c5160ad60fa798c618ef6677f0212ace96028fdeee34cca0deb3302fea216f5` |
| `benchmarks/tasks/image-crop-mimo26.yaml` | `b4f836148ac2be1349b3c10f0d43aa780111e10bb6da6147ac681ea62469633f` |

The source hashes above predate the explicit reasoning-off repair. The attempt
note identifies that repair so no later source is attributed to the first call.

## Protected envelopes

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `call-001.json` | 3833 | `391bcdfb7ac735b29e44abdfdd86efa9e53d23b9d4b366d3cd0baebde42406b9` |
| `call-002.json` | 313924 | `93c058e742bcee91cc30a462d3a2636f44cc647b9f1e33b78478ab2f7904be23` |
| `call-003.json` | 313924 | `18c16704b04cbcdd2fd1317298f614a253599d1e90c8e7b2246b2f51fa6c25fc` |
| `call-004.json` | 3330 | `53b22b5dc64fe4c7a75ce9cf9a86372555cda53263b24f69fddd285c793337c4` |
| `call-005.json` | 3326 | `72037e74e0a0478c1fc0710836868124ff7eb979eb12a0ec5e7568d8f88d844c` |
| `call-006.json` | 313923 | `8e4876fb1d4a911f295849fb5c3f2f31b5210e8df78eb2dcb46e15f5c3b4e346` |
| `call-007.json` | 313923 | `b3acb6de1981d61001d213af31a9236e5525c5960ca99c71157b0db1b2b371f8` |

All seven original requests pin generic `DeepInfra`, not `deepinfra/fp8`; fp8
was catalog-inferred only. The later offline adapter repair adds explicit
`provider_route: deepinfra/fp8` and terminal capacity stopping, but it was not
used for any recorded call. The pre-call tracked owner adapter SHA-256 was
`f93c72b566e4bdced8b7eef59cf4d6228dfd07d3771753f1d0308d63964bc2ab`.
