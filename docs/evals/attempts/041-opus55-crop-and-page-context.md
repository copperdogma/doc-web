# Attempt 041 — Opus 5.5 crop and page-context screen

Date: 2026-09-26. Owner: Doc Web, Stories 207/209/232. Base:
`b75324c69a0fcf5578d5909f28c95a44dc0d3f5e` (current `origin/main`).

## Frozen decision contract before inference

- Candidate: direct Anthropic Messages `claude-opus-5-5`, adaptive thinking,
  explicit `medium` effort, native strict JSON Schema, owner adapter, serial
  execution and fresh subject outputs. No model/route substitution or automatic
  retry. Authenticated `GET /v1/models/claude-opus-5-5` returned HTTP 200 and
  the exact ID using Doc Web's existing ignored credential; no key was copied.
- Detector: maintained `image-crop-extraction` `conservative-count` prompt,
  source images, scorer and goldens. Native integer `0-1000` bbox type is
  projected into the original scorer's normalized-coordinate semantics by its
  existing scale normalization. The adapter locally enforces four ordered,
  bounded integer coordinates because Anthropic's strict schema subset omits
  numeric range and full array-size constraints. Qualify synthetic image,
  then `Image011`; advance to full 13 and fresh Gemini 3 Flash only if admitted.
  Required: 13/13 structural passes and mean overall >=0.95.
- Independently qualify maintained `crop-page-level-deletion-gate` with the
  unchanged page-context prompt, scorer, 22 goldens and direct strict verdict
  schema. Start `page-122-001`; a false-safe `pass` stops this lane. Advance to
  full 22 and fresh GPT-5.5 Responses only if admitted and affordable. Required:
  22/22, with no false-safe label. Detector failure does not cancel this lane.
- Existing runtime remains Gemini 3 Flash for detection; the configured
  page-context regression provider is GPT-5.5 Responses. The selected corpus
  is public but selection-exposed, so this can establish bounded compatibility,
  not promotion or C5 deletion without separately frozen held-out truth.
- Price: standard Anthropic $4/M input and $20/M total output, including
  thinking; no fast/batch route. All provider calls, failed billing, controls
  and any judge share a hard US$2.00 ceiling. Reserve each call's complete
  `max_tokens` output and conservative input bound before dispatch; unresolved
  billing keeps its reservation. No cap redistribution, prompt tuning, or
  expanded configuration. Public owner-established benchmark images only.
- Transport gates: exact served identity, terminal `end_turn`, complete output,
  native strict schema plus local numeric validation, valid usage, raw response
  retention and owner-harness parity. An access/contract failure is not a
  capability loss. Raw payloads stay in ignored `benchmarks/results/` with a
  tracked hash/size manifest. No defaults, private payloads, commit, push or
  merge are authorized.

Provider source checked 2026-09-26: https://platform.claude.com/docs/en/models/opus-5-5/overview
and https://platform.claude.com/docs/en/build-with-claude/structured-outputs .

## Zero-cost matrix and contract preflight

Four projected tasks were compared row-for-row with their maintained YAML:
`opus55-detector-image011.yaml` (1), `opus55-detector-full13.yaml` (13),
`opus55-page-context-122-001.yaml` (1), and
`opus55-page-context-full22.yaml` (22). Each selected row is an exact original
test row. The rendered detector cases are independent one-image messages with
the unchanged `conservative-count` text plus its existing integer-coordinate
branch. The page-context cases are independent two-image messages in source,
crop order. There is one candidate provider and one Python structural assertion
per row; no rubric judge or session chain. No output cache; concurrency one.
The original task also has other prompts and models, so the projected YAML is
an explicitly recorded narrow slice, not a claim that the original full matrix
ran. All referenced fixtures and goldens resolved locally before inference.

Frozen semantic file SHA-256: detector prompt
`d15c7fd6f20389e5e7b2af9f15dd3697a31c28f47cfea8147c8114fe82f1e8f9`,
page prompt `2ccc8c96ef69c14102d7ffd13b5a39715e5cd136b497510b1b2f88243009a5a0`,
detector scorer `7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7`,
page scorer `12eb63725523bd00d59ce12b7486db8c9244124a0c57bb68cae8b8e9e7d288fb`,
detector golden `2ac0a8f01e00a252439da1f4827a85bc5118bf96460a3ff1780e642eafc60f90`,
page golden `4bcba8f4ab8a742608e7cfc1438464a71cf56aa4cd9cbe9e0a67e4a410ac18a5`,
evaluated adapter `f3048a4f4ce27983b0597fbb9e150d8a44a20cf8a61c56c392bd59584ad11baf`.
These hashes, the base commit and the exact worktree diff identify the dirty
evaluated code state. Close-out formatting changed only layout in the adapter;
the commit candidate's adapter SHA-256 is
`b9e88a9152233d1e192ad288dcac0346b4e33e56bce9023e0554e8c659e83085`.
The post-format focused tests passed, but the earlier raw results remain
attributed to the evaluated adapter hash above. Later documentation/test edits
did not change inference.

## Qualification and progressive result

Authenticated exact-model retrieval: HTTP 200, ID `claude-opus-5-5`. Native
generated-square image/integer-schema and distinct native two-image/page-context
schema calls both returned exact served ID, terminal `end_turn`, valid usage and
locally valid strict output. The same generated image through the owner adapter
passed parity. The direct Responses API was not used for Opus. All provider
responses were saved before parsing or status handling in ignored owner storage.
The first tiny-image native reservation used `count_tokens × 2` for input;
observed vision usage was higher, though its all-in reservation still exceeded
actual charge. Subsequent image calls reserved 20,000 input tokens **per image**
plus all 1,024 possible output tokens (including thinking), at $4/$20 per
million. Full13 worst-case reservation was `$1.30624` plus `$0.071568` prior
spend, within the `$2.00` cap. No retry, cache hit or unknown charge occurred.

| Stage | Result | Charged cost |
| --- | --- | ---: |
| native integer synthetic image | exact terminal strict output | $0.002304 |
| owner adapter parity on synthetic image | exact terminal strict output | $0.002324 |
| native two-image page-context | exact terminal strict output | $0.005016 |
| `Image011` detector | 1/1 scorer pass, 0.9548; correct two-region grouping | $0.020656 |
| `page-122-001` safety | **false-safe `pass`**, golden `fail`; stop page lane | $0.041268 |
| detector full13 | 12 scorer passes, one contract error; 12 valid mean 0.9177 | $0.281372 |

**All-call spend: `$0.352940 / $2.00`**, including the intentionally repeated
Image011 in the full13; no fresh control calls or judges. Full13 had 61,333
input and 1,802 output tokens, 4,996 ms mean Promptfoo row latency, no provider
HTTP errors, and one locally rejected response. `Image037` returned a native
strict-schema integer `y1=1359`, outside the promised 0–1000 coordinate
system. The raw envelope is retained; the scorer did not grade that row. The
12 contract-valid scores average 0.9177, already below the required >=0.95.
The isolated Image011 score was 0.9548 and its independent full13 score was
0.9016, showing single-case variation rather than a stable promotion result.
The full run is **not** a valid 13/13 score. Fresh Gemini 3 Flash was not
admitted after this candidate failed the frozen detector gate.

The distinct safety call returned `{"verdict":"pass",...}` and stated that the
crop contains both oval portraits. The authoritative golden requires `fail`:
the Moise/Edward crop includes the adjacent Sophie L'Heureux portrait. Manual
inspection of the source page and crop confirmed the whole neighboring oval,
so this is a valid model-wrong false-safe result, not a transport, parser or
golden error. The full22 and fresh GPT-5.5 control were not admitted. A detector
failure did not cancel or cause this independent safety result.

Reproduce the frozen Promptfoo stages from `benchmarks/` with the already
configured owner credential; the wrapper maps only the required provider key.
Replace `TASK` and `OUT` with the corresponding projected task and result file
listed above. `RAW_DIR` is the ignored result subdirectory shown below.

```bash
DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env \
ANTHROPIC_MESSAGES_RAW_ENVELOPE_DIR=/Users/cam/.codex/worktrees/opus55-eval-20260926/doc-web/benchmarks/results/opus55-20260926/raw \
ANTHROPIC_MESSAGES_INPUT_PRICE_PER_1M=4 \
ANTHROPIC_MESSAGES_OUTPUT_PRICE_PER_1M=20 \
PROMPTFOO_PYTHON=/Users/cam/miniconda3/bin/python \
PROMPTFOO_EVAL_TIMEOUT_MS=180000 \
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/TASK \
  --no-cache --no-share --no-table -j 1 \
  --output results/opus55-20260926/OUT
```

`TASK`/`OUT` pairs: `opus55-detector-image011.yaml`/`detector-image011.json`,
`opus55-page-context-122-001.yaml`/`page-context-122-001.json`, and
`opus55-detector-full13.yaml`/`detector-full13.json`. Native probes used the
same adapter `_build_body`, a generated black square image, direct
`POST /v1/messages` and 1,024 max output tokens. Raw/result SHA-256 and byte
sizes are in `docs/evals/evidence/041-opus55-crop-and-page-context-manifest.md`.

## Layered decision

| Layer | Verdict |
| --- | --- |
| access | Available: exact authenticated ID and direct callable route. |
| transport | Native strict image and page schemas plus owner adapter parity qualified; full detector later had one coordinate-range contract failure. |
| reliability | 18 serial calls, no HTTP failure/retry, one contract-invalid response; production reliability not established. |
| capability | Detector fails complete 13/13 and >=0.95 admission; 12 valid rows average 0.9177. Page-context safety makes one source-verified false-safe judgment. |
| economics | `$0.352940` all calls; full13 mean 4,996 ms and `$0.281372` total; no comparative cost/latency claim without fresh controls. |
| adoption | **Do not adopt** Opus 5.5 for either Doc Web crop detector or page-context validator. Keep current runtime/default and C5 residue. |

This selected public corpus is exposed by previous model selection. The
failed gates are decisive against adoption here; a hypothetical passing result
would still need separately frozen held-out truth before promotion. No HTML/OCR
or private-document capability was tested.
