# JEV Doc Web consistency classification — 2026-09-21

**Decision:** The predeclared JEV → GPT-4.1 confidence cascade is the best measured
candidate on this narrow synthetic classifier. Raw JEV is cheaper/faster but less
accurate than GPT-4.1; do not replace the full planner or deploy either change from
this evidence. Recommend a bounded integration/shadow comparison at the existing
status seam, preserving explicit uncertainty and deterministic layout checks.

## Relative results

20 frozen cases ×2 uncached serial repetitions. Seven-column genealogy tables and
maintenance cards; ten paired mutation patterns across two source documents.
These are forty decisions, not forty independent documents.

| Arm | Correct class | Macro F1 | Correct action* | Defects called clean | Cost /40 | Median | p95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| New structural-only baseline |16/40|.2333|24/40|8|$0|not timed|not timed|
| JEV1.13.0 |24/40|.5858|34/40|4|$0.0014196|261.6ms|587.5ms|
| GPT-4.1-2025-04-14 narrow projection |29/40|.7133|34/40|3|$0.043408|730.3ms|1135.7ms|
| JEV → GPT-4.1 real serial cascade |33/40|.8156|37/40|3|$0.0196916|495.3ms|1691.4ms|

*Action groups: conformant=no action, uncertain=review, other three=repair. This
additional deterministic descriptive projection was calculated after the run;
five-class results and false-clean counts were the predeclared primary metrics.

The cascade improves class accuracy by10 percentage points and costs54.64% less
than the fresh narrow GPT comparator. Its median is32.18% faster, while p95 is48.92%
slower due to serial fallback. These are workload observations on this balanced
fixture distribution, not savings forecasts for production traffic. Independent
fallback calls were actually made, not reconstructed by selecting outputs from
the standalone GPT run. GPT varied between repeat/fallback calls despite temperature0.

## Workflow and confidence

Every explicit JEV uncertain decision stays review-routed regardless of confidence.
Other labels with confidence<.8 invoke GPT-4.1. The threshold and policy were frozen
before inference;17/40 decisions invoked actual fallback. All eight uncertainty
cases were preserved/corrected by the cascade, versus5/8 direct GPT and6/8 rawJEV.
No clean case was incorrectly labelled a defect. Three real format defects were
incorrectly called conformant by both cascade and standalone GPT in aggregate.
Family exact-class totals: JEV10/20, GPT12/20, cascade13/20.
Maintenance exact-class totals: JEV14/20, GPT17/20, cascade20/20.

## Maintained deterministic detector

The actual `analyze_chapter_row` detector ran via losslessly rendered synthetic
HTML, using its unchanged flag_threshold25. It accepted9/10 family cases and
flagged the two fused-header cases; it did not flag the split-table or semantic
errors. Reordered columns fell outside its recognized genealogy signatures.
All10 maintenance-card cases are out-of-domain. This is a binary layout detector,
not a five-class semantic incumbent; no invented overall accuracy is assigned.
`maintained-detector.json` retains complete outputs. The structural-only comparator
in the table is newly authored, generic and separately identified; it does not read
source semantics. Neither deterministic baseline is the gold source.

## What this comparison does and does not establish

- Access and transport: qualified native TypeSafe and OpenAI calls, exact served
  checkpoint identity, native Choice distributions or strict JSON Schema output,
  terminal outputs and usage retained.97calls completed,0errors,0retries.
- Capability: raw JEV worse on exact labels; predeclared cascade better on these
  reviewed source cases. This is useful relative evidence despite imperfect scores.
- Economics: provider usage-priced total **$0.0630996 / $0.60**, including40JEV,
  40standaloneGPT and17fallbackGPT calls. No unknown reservations remain. Cascade
  cost overlaps the JEV and fallback spend; do not sum all arm costs as campaign spend.
- Adoption: **conditional shadow evaluation for the bounded status-routing approach; do not
  replace the full planner**. An integration must measure the real assembled
  planner/repair consumer before production defaults change. No runtime changes made.
- The maintained Story220 recipe uses GPT-4.1. This benchmark projects that model
  into a new narrow schema with explicit conventions; it does not rerun unchanged
  full planner prompts or measure convention discovery, rationale generation,
  page-context retrieval, OCR, source rereading, or repair outcomes/cost.
- Small source coverage, balanced mutation prevalence, two repeats, no throughput
  experiment, synthetic sources only. No private Onward source was sent.
- TypeSafe docs say no training on customer requests; enterprise ZDR is not asserted
  here. OpenAI `store:false` is not ZDR proof. Synthetic fixtures make retention
  acceptable within the approved scope.

## Provenance and verification

`review.json` is independent pre-call source/gold approval; `source-manifest.json`
freezes runner, prompts, scorer, fixtures, deterministic adapter, maintained detector,
base SHA and provider pricing sources. `rendered.json` exposes the complete harness
topology without gold leakage. Every actual request/response and usage/latency is
retained under this directory; `ledger.json` records all dispatches and reservations.
`results.json` and `summary.json` are reproducible from those retained outputs.

Native smoke used family-01, then continued unchanged on the rest and second
repetition. No cached subject output substituted for a new call. A shared raw
HTTP call function is both native adapter and harness transport, eliminating a
separate Promptfoo transformation. Inputs contain `input` only, not gold/rationale/IDs.
The runner refuses duplicate dispatch names and refuses changed source hashes.

Commands (credentials loaded through owner wrappers; no credential values printed):

```sh
python3 benchmarks/jev-consistency/run.py
python3 -m unittest discover -s benchmarks/jev-consistency -p 'test_*.py'
/Users/cam/Documents/Projects/doc-web/.venv/bin/python benchmarks/jev-consistency/detector.py
python3 /Users/cam/Documents/Projects/doc-web/scripts/run_with_doc_web_env.py python3 scripts/run_with_doc_web_env.py python3 benchmarks/jev-consistency/run.py --run --limit 1 --repeats 1
python3 /Users/cam/Documents/Projects/doc-web/scripts/run_with_doc_web_env.py python3 scripts/run_with_doc_web_env.py python3 benchmarks/jev-consistency/run.py --run --limit 20 --repeats 2
/Users/cam/Documents/Projects/doc-web/.venv/bin/python scripts/methodology_graph.py build
/Users/cam/Documents/Projects/doc-web/.venv/bin/python scripts/methodology_graph.py check
git diff --check
```

5focused tests passed, real maintained detector executed, methodology graph check
passed, whitespace clean. Runtime pipeline is untouched; driver.py was not run and
no pipeline integration claim is made. Paid run outputs manually inspected for
format-versus-semantic confusion, confidence/fallback, and correct row provenance.

Post-run lint formatting (imports/whitespace only) changed the working runner and
tests. Exact paid-run source snapshots are preserved under `frozen-source/`, mapped
by `source-manifest.json`; hashes validate each original. No paid output is attributed
to later formatting. The run guard refuses the changed working source for this old
run; a future paid attempt needs a new explicit identity and reviewed manifest.
Focused tests and Ruff pass on the formatted tooling.

Credential cleanup: coordinator removed the temporary DOC_WEB_TYPESAFE_API_KEY;
presence-only owner resolver verification returned false. Existing owner OpenAI
key was used only through the owner wrapper and was never copied or changed.

Independent post-output review (`mismatch-review.json`) accounts exactly for all
34 mismatches across ten unique cases: JEV16, GPT11, cascade7. All were
source-reviewed model-wrong; zero gold defects, ambiguities or label changes. The
review supports shadow use only with explicit deterministic layout checks: the
three cascade false-clean format misses equal the direct GPT aggregate count.

Focused pytest passed5/5 using `/usr/local/bin/pytest`; the owner venv lacks pytest
and Ruff, so available system executables were used. Ruff passed. No dependency
installation or runtime changes were needed.
