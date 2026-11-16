# Opt-in reviewed handwriting OCR with Hydrogen

Attempt094 recommends `gemini-4-hydrogen`, HIGH, 32768 combined output/thinking
tokens for the bounded reviewed historical-handwriting job. It passes the
maintained .99 similarity target on two public LOC sources, with higher measured
cost and latency than the current Gemini3.8 reference. Defaults remain unchanged.
This is not exact transcription, general book qualification or publication approval.

The ordinary recipes select the actual native model; no evaluation dispatch shim
or startup injection is needed:

```bash
scripts/run_with_doc_web_env.py python driver.py \
  --recipe configs/recipes/hydrogen-ocr-candidate-barney.yaml \
  --run-id hydrogen-reviewed-barney-NEW --end-at ocr_ai --instrument
scripts/run_with_doc_web_env.py python driver.py \
  --recipe configs/recipes/hydrogen-ocr-candidate-alverson.yaml \
  --run-id hydrogen-reviewed-alverson-NEW --end-at ocr_ai --instrument
```

Commands make provider calls; the closed evaluation wallet does not authorize
another run. Use a fresh identity and the owner's authorized payload/spend scope.
Use the established Conda interpreter if the active Python lacks project packages.
For an isolated checkout, set `DOC_WEB_ENV_FILE` to that same owner's configured
environment; do not copy credentials or use another project’s key.

The exact model opts into HIGH using the SDK's documented native `extra_body`
request override. Installed google-genai1.63.0 forwards nested ThinkingConfig in
snake_case; network-denied SDK capture demonstrated that this would not preserve
the native `thinkingLevel` contract. No dependency upgrade is required. The
same normal client retains exact served-model/terminal checks and now bills
thinking tokens and actual implicit-cache rates explicitly. Existing models keep
their prior generation controls. The price sheet names Hydrogen's cold rates.

Inspect `02_ocr_ai_gpt51_v1/pages_html.jsonl`, both raw_html and stamped html,
against the original image before accepting a transcription. Keep uncertain names,
misspellings and damaged text under review. The tested similarity ratios are
.990641/.991716 versus matched Gemini .985632/.984090; native subject costs
.0639975/.0251835 versus .011088/.0062685, client latencies39.627/18.900s versus
21.408/10.472s. These are two-source observations, not a throughput guarantee.

Rollback: select the existing `gpt61-ocr-gemini-3.7-flash-*.yaml` owner recipes
or the maintained default recipe. The new candidate recipes are opt-in; no
existing default changes. The normal native-client consumer was verified with
both original native responses under network denial, yielding exact same raw
and stamped HTML; no extra subject inference was needed.

Evidence: [Attempt094](../evals/attempts/094-hydrogen-source-fidelity.md),
[summary](../evals/evidence/094-hydrogen/summary.json),
[manifest](../evals/evidence/094-hydrogen/manifest.json).

The [readable measured outputs](../evals/evidence/094-hydrogen/ocr-reviewed-outputs.json)
preserve candidate/control raw and stamped HTML from all four actual-driver
artifacts, with hashes binding the protected originals. This visible-content
projection contains no opaque provider state; native-envelope replay still
requires the separately retained protected archive described by the manifest.
