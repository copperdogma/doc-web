---
title: "Benchmark Unlimited-OCR as a Whole-Document Challenger"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #6 (Validate), Any format, any condition, Fidelity to the source, Traceability is the product"
spec_refs:
  - "spec:2"
  - "spec:2.1"
  - "spec:2.2"
  - "spec:3"
  - "spec:3.1"
adr_refs:
  - "ADR-001"
depends_on:
  - "208"
category_refs:
  - "spec:2"
  - "spec:3"
compromise_refs:
  - "C1"
  - "C3"
  - "C6"
input_coverage_refs:
  - "scanned-pdf-tables"
  - "handwritten-notes"
architecture_domains:
  - "ocr_and_extraction"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 230 — Benchmark Unlimited-OCR as a Whole-Document Challenger

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`,
`docs/methodology/state.yaml`, `docs/methodology/graph.json`,
`docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`,
`docs/runbooks/golden-build.md`,
`docs/runbooks/document-consistency-planning.md`,
`docs/evals/README.md`, `docs/evals/registry.yaml`,
`docs/scout/scout-016-vaibhav-sisinty-ai-agent-product-manager.md`,
`docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`,
`docs/stories/story-208-glm-ocr-benchmark-for-handwritten-and-table-heavy-seams.md`,
`benchmarks/tasks/onward-table-fidelity.yaml`, and Baidu's official
Unlimited-OCR [paper](https://arxiv.org/abs/2606.23050),
[model card](https://huggingface.co/baidu/Unlimited-OCR),
[repository](https://github.com/baidu/Unlimited-OCR), and
[vLLM recipe](https://recipes.vllm.ai/baidu/Unlimited-OCR)
**Depends On**: Story `208`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Determine whether Baidu Unlimited-OCR's one-shot multi-page parsing is a
meaningful, repeatable improvement over doc-forge's current OCR on the
table-heavy genealogy lane or the blocked historical-handwriting lane. The
story must measure four fair Onward arms, preserve raw page/grounding evidence,
classify every scored mismatch, and make one operational decision: reject the
extra runtime, adopt it conditionally for a clearly identifiable surface while
keeping the incumbent elsewhere, or recommend a later maintained integration
story. A tiny or isolated improvement is explicitly insufficient to justify a
second OCR model.

## Eval Ladder Context

- **Root Ideal eval**: faithful, provenance-rich extraction of the complete
  127-page Onward book and the real handwritten fixture pair. A full-book
  challenger run is deferred until a bounded slice establishes a credible win.
- **Parent evals**: `onward-table-fidelity` currently records `0.969` for the
  applied Gemini 3.1 Pro path and `0.9714` for the GPT-5.5 score-only leader,
  with residual cell errors; `handwritten-notes-transcription` remains at a
  maintained floor of `0.677267` and `pass_rate = 0.6`.
- **Measured failure mode**: page-scoped OCR remains vulnerable to cross-page
  table continuity and exact-cell drift, while the real Barney/Alverson pair is
  still below the `0.99` fidelity bar. Story 208 showed that launch claims are
  not evidence: GLM-OCR scored only `0.318375` on Marie-Louise and `0.097473`
  on the handwritten floor.
- **Child eval**: four-arm Unlimited-OCR comparison on the existing Onward
  goldens—incumbent, single-page Gundam, single-page Base, and multi-page
  Base—plus a bounded Barney/Alverson screen. Only a bounded win can justify a
  later full-book or maintained-integration story.

## Acceptance Criteria

- [x] The benchmark runtime and generation contract are pinned before quality is judged:
  - [x] exact model revision, weight precision, runtime/device, dependency versions, source-code patch status, prompt, decoding parameters, context/output cap, and license are recorded
  - [x] any community MPS/MLX code is reviewed before execution and clearly separated from Baidu's official CUDA/BF16 reference path
  - [x] the benchmark logs page/image count, wall time, output length/tokens where available, finish reason, and truncation/error state
- [x] A provenance-preserving benchmark harness writes inspectable artifacts under `output/runs/`:
  - [x] verbatim raw model output is retained before normalization
  - [x] `<PAGE>` coverage/order and `<|ref|>` / `<|det|>` grounding tokens are parsed with a bounded safe parser rather than `eval()`
  - [x] parsed page/block/box sidecars retain source path, source page, coordinates, model/runtime configuration, and processing step without inventing confidence values
  - [x] missing/extra/reordered pages, malformed coordinates, empty output, or truncation are explicit hard failures
- [x] The fair four-arm Onward comparison is run on the existing truth surface:
  - [x] Marie-Louise pages `079`–`083` pass the transport gate first, followed by Alma `022`–`025` and Arthur `029`–`034` unless transport hard-fails
  - [x] Unlimited-OCR single-page Gundam, single-page Base, and multi-page Base use the same source rasters; the current incumbent remains the fourth comparison arm
  - [x] every joined case is scored against its independently reviewed whole-case golden as the primary adoption truth; the Story 134 per-page references are used only for omission/regression diagnostics unless each cited page is freshly checked against source
  - [x] mismatches are classified as model/runtime-wrong, golden/scorer-wrong, or ambiguous before any scorer/golden change
- [x] The low-incremental-cost handwriting screen is run after transport succeeds:
  - [x] Barney and corrected-scope Alverson use the existing checked-in transcripts and scorer
  - [x] Story 191 remains blocked unless both real fixtures clear `overall_min_ratio >= 0.99`, `page_min_ratio >= 0.99`, and `pass_rate = 1.0`
- [x] The final recommendation applies the precommitted project-value gate:
  - [x] **reject** dual-model complexity if the candidate improves fewer than two Onward cases, improves aggregate structure by less than `0.01` without turning a failing case into an exact pass, loses page coverage/order, or only produces an unrouteable one-off win
  - [x] **conditional adoption** is allowed only if it wins on at least two Onward cases across distinct error instances with no material page-level fidelity loss, or if it clears the full Barney/Alverson blocker; the recommendation must name a simple, reliable routing signal and keep the incumbent on losing surfaces
  - [x] the decision report distinguishes the historical applied multi-page benchmark (`0.969`) from the maintained per-page-plus-rescue pipeline, reports an oracle-hybrid score and candidate selection share, and does not call old registry scores a fresh current-runtime baseline
  - [x] latency, local disk/model size, setup/runtime burden, marginal cost, provenance gaps, and operational failure modes are weighed against quality rather than reported as afterthoughts
  - [x] no maintained runtime integration occurs in this story; a genuine win names the exact follow-on integration/removal boundary

## Out of Scope

- Replacing the maintained OCR model or adding a production router in the same story
- Running the full 127-page Onward book before the bounded gate passes
- Treating a community quantization, popularity metric, or published benchmark as local adoption proof
- Changing hand-verified Onward or handwriting goldens to improve the candidate score without source-backed mismatch classification and approval
- Reopening Story 191 from multilingual/document-OCR claims rather than the existing fixture thresholds
- Hiding multi-page loss behind an aggregate score or silently dropping grounding/page tokens for clean Markdown

## Approach Evaluation

- **Simplification baseline**: Run the model unchanged with Baidu's exact
  prompts and generation contract before building any repair or routing logic.
  The four-arm design separates model quality from Base-mode compression and
  long-context effects.
- **AI-only**: Unlimited-OCR itself performs the OCR and structure judgment.
  The preferred reference is official BF16 on NVIDIA; an exact-weight,
  device-only MPS patch may supply the bounded local result if its code changes
  are reviewed and its deviation is recorded. Community quantizations are
  transport preflights, not decisive quality evidence.
- **Hybrid**: Code owns source selection, safe grounding/page parsing, Markdown
  normalization, scoring, instrumentation, and decision reporting. A future
  conditional-adoption router is warranted only if this benchmark discovers a
  reliable winning surface.
- **Pure code**: Appropriate only for orchestration and deterministic
  comparison. It cannot repair OCR text, infer missing table cells, or turn
  coordinates into confidence scores.
- **Repo constraints / prior decisions**: ADR-001 favors document-wide,
  source-aware understanding but still requires explicit policy and provenance
  artifacts. `C1` and `C3` are in `climb`; `C6` remains in `hold`, so recurring
  expense and extra escalation must earn their complexity. Scout 016 says
  evaluate rather than adopt. Story 191's unblock thresholds remain unchanged.
- **Existing patterns to reuse**: Story 208's bounded benchmark harness and
  artifact layout, `benchmarks/scorers/html_table_diff.py`,
  `benchmarks/scorers/handwritten_notes_transcription.py`, the independently
  reviewed whole-case Onward goldens, the diagnostic Story 134 per-page
  references, and the existing eval-registry attempt protocol.
- **Eval**: Quality is decided by the existing `onward-table-fidelity` and
  `handwritten-notes-transcription` truth surfaces plus explicit page/order,
  provenance, runtime, and complexity metrics. No new golden is needed.

## Tasks

- [x] Verify and pin the smallest trustworthy runtime path:
  - [x] inspect any community device patch/custom code before execution
  - [x] establish an exact-weight device runtime with an official BF16 parity control; prefer MPS/CUDA, but permit sandboxed FP32 CPU when trust-boundary constraints block custom-code MPS execution and parity is exact
  - [x] record the trustworthy raw-special-token path or an explicit hard stop
- [x] Implement the smallest story-local benchmark harness:
  - [x] reuse Story 208 scoring and artifact patterns without changing maintained modules/recipes
  - [x] implement safe `<PAGE>` / grounding parsing, Markdown-table normalization, per-page and whole-case scoring, and run instrumentation
  - [x] add focused tests for page coverage/order, coordinate validation, safe parsing, truncation/error handling, and the project-value decision rule
- [x] Run the four-arm Onward ladder, classify mismatches, and manually inspect the source/output artifacts
- [x] Run the bounded Barney/Alverson screen and keep Story 191's decision boundary honest
- [x] Publish one final adopt / conditional-adopt / do-not-adopt recommendation using the precommitted breadth-and-complexity gate
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Focused benchmark-harness tests
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If a candidate earns downstream integration consideration: run the narrowest real `driver.py` continuation that proves its emitted artifact can be consumed, then inspect the resulting `output/runs/` artifacts
  - [x] If agent tooling changed: `make skills-check`
- [x] Run `/improve-eval`, classify all mismatches, and update `docs/evals/registry.yaml` with the verified result
- [x] Search all docs and update any related to what was touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: raw response, page order, grounding, runtime, source page, and processing step remain inspectable; absent confidence is not fabricated
  - [x] T1 — AI-First: the model performs recognition/structure work while code only orchestrates and validates
  - [x] T2 — Eval Before Build: the bounded four-arm comparison precedes any maintained runtime or routing change
  - [x] T3 — Fidelity: every source page is represented exactly once and page/cell losses remain explicit
  - [x] T4 — Modular: the benchmark stays story-local and any later adoption has a named narrow routing boundary
  - [x] T5 — Inspect Artifacts: raw output, parsed sidecars, scored Markdown/HTML, and source images are manually reviewed

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via /mark-story-done

## Blocker Summary

N/A

## Blocker Evidence

N/A

## Unblock Condition

N/A

## Architectural Fit

- **Owning module / area**: story-local OCR challenger harness under
  `scripts/spikes/`, focused tests, existing eval registry, and Scout 016. No
  maintained module or recipe changes are justified before a measured win.
- **Methodology reality**: `spec:2` and `spec:3` own this work. `C1` and `C3`
  are in `climb`; `C6` is in `hold`. `scanned-pdf-tables` is currently
  `passing` with `structure_preservation = 0.95`, while `handwritten-notes`
  remains `has-fixture` and blocked by real-fixture OCR quality.
- **Substrate evidence**: source images exist under
  `input/onward-to-the-unknown-images/`; whole-case and per-page goldens exist
  under `benchmarks/golden/onward/`; Story 208's harness demonstrates bounded
  external OCR comparison and artifact packaging; both required scorers exist.
  The current Apple-Silicon machine has 48 GB unified memory and can fit the
  6.7 GB weights. Code-only comparison found the community Universal fork uses
  the exact official weight object and changes only `34` added / `21` removed
  lines in `modeling_unlimitedocr.py` for device placement, MPS
  `masked_scatter_`, and dtype/autocast handling while retaining the original
  R-SWA path. Baidu's public BF16 ZeroGPU Space supplied a single-page parity
  control, but its API deliberately explodes PDFs page-by-page and cannot supply
  the decisive multi-page arm. Configured AWS identities are Storybook-scoped
  and lack a safe doc-web EC2 path. Executing third-party custom code on MPS
  outside the sandbox was not approved, so the measured path used exact-weight
  FP32 CPU inside the sandbox. Its cleaned public-sample output matched the
  official BF16 Space exactly (`2263` characters; ratio `1.0`), and the large
  negative margins made a rented official-CUDA confirmation immaterial.
- **Data contracts / schemas**: no shared schema change is planned. The harness
  emits story-local JSON/JSONL and Markdown/HTML comparison artifacts under
  `output/runs/`. Any normalized `page_html_v1` diagnostic row must include the
  required `page` field and pass `validate_artifact.py`; any later maintained
  integration belongs to a separate adoption story.
- **File sizes**: `scripts/spikes/glm_ocr_benchmark.py` is 395 lines,
  `benchmarks/scorers/html_table_diff.py` is 212,
  `benchmarks/scorers/handwritten_notes_transcription.py` is 119,
  `docs/evals/registry.yaml` is 3817, and Scout 016 is 228. Keep registry edits
  surgical and put new behavior in focused story-local files.
- **Decision context**: reviewed the Ideal, `spec:2`, `spec:3`, current
  methodology state/graph, ADR-001, both relevant runbooks, Scout 016, Stories
  191/208, eval registry entries, coverage rows, and Baidu's primary sources.
  No new ADR is required because this story measures rather than changes the
  maintained architecture.

## Files to Modify

- `docs/stories/story-230-benchmark-unlimited-ocr-whole-document-challenger.md` — story contract, work log, evidence, and final decision (new)
- `scripts/spikes/unlimited_ocr_benchmark.py` — bounded runtime adapter, provenance parser, scorer orchestration, and decision report (new)
- `tests/test_unlimited_ocr_benchmark.py` — focused deterministic harness/provenance/decision tests (new)
- `docs/evals/attempts/017-unlimited-ocr-whole-document-challenger.md` — portable verified attempt record (new)
- `docs/evals/registry.yaml` — surgical Story 230 score/attempt lineage update (3817 lines)
- `docs/scout/scout-016-vaibhav-sisinty-ai-agent-product-manager.md` — approved/result evidence and final status (228 lines)
- `docs/scout.md` — generated-by-hand scout expedition index after verified completion
- `docs/stories.md` and `docs/methodology/graph.json` — generated story/methodology views
- `CHANGELOG.md` — close-out note if the story is validated and marked done

## Redundancy / Removal Targets

- Do not add a maintained Unlimited-OCR provider, module, recipe, or router if
  the breadth-and-complexity gate fails.
- Keep Story 208's GLM harness as historical negative evidence; reuse its
  pattern rather than expanding it into a multi-model abstraction prematurely.
- If Unlimited-OCR earns a later maintained lane, that follow-on must name the
  incumbent path it replaces or the narrow escalation trigger it adds so the
  project does not accumulate an unbounded model matrix.
- The lowest-complexity likely follow-on is a sibling backend at the existing
  `validate_onward_genealogy_consistency_v1` →
  `rerun_onward_genealogy_consistency_v1` flagged-group seam, retaining the
  incumbent fallback, rather than a new up-front router over every page.

## Notes

- **New story justification**: Story 208 owns a completed GLM-OCR direct
  single-page challenger. Story 230 owns a materially different whole-document
  runtime, raw grounding/page contract, four-arm single-versus-multi-page
  validation boundary, and dual-model complexity decision. Reopening Story 208
  would blur completed negative evidence and the new cross-page hypothesis.
- **Human gate**: Cam explicitly approved Scout 016's bounded benchmark on
  2026-07-20 with the added requirement that isolated wins must not justify
  dual-model complexity. This plan stays inside that approved scope; any
  maintained adoption or materially broader/full-book run remains a separate
  decision.
- **Reference reproduction contract**: exact prompts are
  `<image>document parsing.` for single-page and
  `<image>Multi page parsing.` for multi-page; use deterministic decoding,
  preserve special tokens, and log the no-repeat processor/window settings.

## Plan

1. **Runtime and transport proof (S)**
   - Review the exact-weight device patch or official CUDA image before running
     custom code, pin revisions and dependency versions, and record deviations
     from Baidu's reference runtime.
   - Run one Marie-Louise page in Base and Gundam modes. Stop on empty output,
     stripped special tokens, malformed grounding, or unbounded setup risk.
2. **Harness and tests (M)**
   - Add `scripts/spikes/unlimited_ocr_benchmark.py` by adapting Story 208's
     story-local packaging, not its GLM-specific transport.
   - Persist raw responses first; safely parse page/ref/det tokens; normalize
     model Markdown to scoreable HTML; emit page/whole-case quality,
     provenance, runtime, and decision summaries.
   - Add deterministic tests for hostile coordinate text, page-count/order
     failures, Markdown tables, score aggregation, and the precommitted
     breadth/complexity rule.
3. **Bounded quality ladder (M)**
   - Run Marie-Louise `079`–`083` across Gundam, Base, and multi-page Base,
     compare to the independently reviewed whole-case golden and historical
     baselines, and inspect all source/output pairs. Use per-page references as
     diagnostics only unless freshly source-revalidated.
   - Continue to Alma and Arthur unless transport hard-fails. Run Barney and
     Alverson as a separate low-incremental-cost screen.
4. **Eval record and decision (S)**
   - Classify mismatches before touching any scorer/golden; normally expect no
     golden changes.
   - Record verified quality, latency, disk/runtime burden, provenance gaps,
     and the exact conditional-adoption or rejection boundary in the attempt,
     registry, story, and Scout 016.
5. **Verification and closure (M)**
   - Run focused tests, `make lint`, `make test`, artifact inspection, and the
     narrowest driver continuation only if the candidate earns integration
     consideration.
   - Run `/validate`; if complete, run `/mark-story-done`. Do not commit or push
     without separate explicit instruction.

## Result

**Decision: do not adopt Unlimited-OCR. Keep the current OCR approach on every
tested surface and do not add a second-model router.**

Best transport-valid Unlimited-OCR scores were Alma `0.6797`, Arthur `0.5384`,
and Marie-Louise `0.5966`, versus historical applied records `0.923`, `0.989`,
and `0.995`. The candidate mean was `0.6049` versus `0.969`, for a `-0.3641`
delta, `0/3` meaningful wins, oracle-hybrid `0.969`, and candidate selection
share `0.0`. Multi-page mode lost to the best single-page mode on every case;
Arthur multi-page additionally emitted seven page segments for six inputs.

The handwriting screen was also decisive: Barney scored `0.200382`; Alverson
scored `0.022946` and ran away to `30939` output tokens near the `32768` cap.
Story 191 remains blocked. Manual source/output review classified the material
differences as model/runtime-wrong; no golden/scorer defect or outcome-changing
ambiguity was found.

Portable evidence is in
`docs/evals/attempts/017-unlimited-ocr-whole-document-challenger.md`. Run-local
evidence is under
`output/runs/story230-unlimited-ocr-benchmark-r1/local-cpu/`, especially
`decision.json`, `onward_results.json`, `handwriting_results.json`, and each
arm's raw/parsed/transport/runtime/clean/HTML/score bundle.

## Work Log

20260720-1018 — create-story + approved build plan: created Story 230 as the
next honest story ID after verifying that this is not another model permutation
inside Story 208. The new candidate changes the runtime, raw artifact contract,
and validation boundary by testing one-shot multi-page output against both
whole-case and page-level goldens. Reviewed the Ideal, relevant spec/state/graph
slices, ADR-001, consistency/golden runbooks, Scout 016, Stories 191/208, the
coverage matrix, current eval registry, source images, goldens, scorers, and
Baidu's primary reproduction sources. Critical substrate exists: all three
Onward source/golden cases are local, Story 208 supplies the bounded benchmark
pattern, the machine has enough unified memory for full weights, and configured
AWS access exists as an NVIDIA fallback. Cam's explicit approval covers this
written plan and adds the precommitted rule that a tiny or isolated win does not
justify two OCR models. Next: promote to `In Progress`, prove the exact runtime,
then implement only the story-local harness and tests.

20260720-1021 — build-story runtime exploration + promotion: promoted Story 230
to `In Progress` after verifying a bounded exact-weight path rather than
pretending the CUDA-only official snippet runs on this Mac. Official model
revision `ee63731b6461c8afcdcc7b15352e7d2ffecc2ead` and community Universal
revision `bc00ae36def7fe8d23980adf5a901125fe0040a2` point to the same 6.67 GB
safetensors object (`sha256:2bc48a7a110061ea58fff65d3169367eebe3aee371ca6968dc2219c1b2855fc6`).
The code diff is bounded to device/dtype handling in
`modeling_unlimitedocr.py` (`34` insertions / `21` deletions), preserving the
official multi-page/R-SWA generation logic and exact prompts. The fork runs
FP32 on MPS because BF16 drifts there. Baidu's own public ZeroGPU Space is
official BF16 and useful for a single-page parity control, but current Space
code intentionally runs each PDF page separately at `max_length=8192`; it
cannot answer the one-shot hypothesis. AWS access was also checked: available
profiles are Storybook-scoped and not an honest doc-web GPU substrate. Decision:
run exact-weight FP32 MPS, verify representative single-page parity against the
official BF16 Space, and require rented official CUDA confirmation only if the
candidate is close enough to affect the adoption call. This keeps the approved
benchmark moving without treating community MLX/GGUF quantizations as evidence.

20260720-1058 — runtime proof superseding the initial MPS plan: executing the
reviewed third-party custom model code outside the sandbox on MPS required a
broader trust approval, so the measured path stayed inside the sandbox on native
arm64 FP32 CPU. This was not a quantized substitute: the runtime verified
community revision `bc00ae36def7fe8d23980adf5a901125fe0040a2`, exact weight
size `6672547120`, and SHA-256
`2bc48a7a110061ea58fff65d3169367eebe3aee371ca6968dc2219c1b2855fc6`
before custom-code execution. Baidu's official BF16 Space and the local CPU path
then produced an exact `2263`-character match on Baidu's public sample after
removing only the Space's grounding metadata (`sequence_ratio = 1.0`). No
repo-owned image was uploaded. Evidence:
`output/runs/story230-unlimited-ocr-benchmark-r1/runtime-verification.json` and
`output/runs/story230-unlimited-ocr-benchmark-r1/parity-public-sample-gundam-clean.json`.

20260720-1124 — benchmark + manual inspection: ran all nine candidate arms on
the same Onward rasters and the separate corrected Barney/Alverson screen. Best
transport-valid results were Alma single Base `0.6797`, Arthur single Gundam
`0.5384`, and Marie-Louise single Base `0.5966`; the historical applied scores
are `0.923`, `0.989`, and `0.995`, not fresh current-runtime baselines. The
precommitted decision artifact reports candidate mean `0.6049`, historical mean
`0.969`, delta `-0.3641`, `0/3` meaningful wins, oracle-hybrid `0.969`, and
candidate selection share `0.0`. Arthur multi-page emitted seven `<PAGE>`
segments for six images and hard-failed transport. Barney scored `0.200382`;
Alverson scored `0.022946` and emitted `30939` tokens near the total
`max_length = 32768` cap. Because the helper omitted input length and stop
reason, truncation remains indeterminate; the fabricated, repetitive content
is independently a decisive model/runtime failure.

Manual source review opened Marie-Louise pages `079`–`083`, Alma `022` and
`025`, Arthur `029`, `032`, and `034`, plus both handwritten images. The matching
raw/clean/score artifacts showed substantive candidate failures: collapsed
`BOY/GIRL` columns, family headings merged into data rows, omissions, `George`
rendered as `Eorge`, an extra Arthur page segment, Barney's missing second-page
content, and Alverson's fabricated formula/repetition. Re-running the existing
scorer reproduced all nine stored scores. Classification: model/runtime-wrong
for every material mismatch; golden/scorer-wrong none; only minor pale-glyph
ambiguity, with no decision impact. No golden changed.

20260720-1146 — harness hardening + eval record: implemented story-local raw
first packaging, bounded `ast.literal_eval` grounding parsing, coordinate/page
hard failures, schema-validated `page_html_v1` diagnostics, exact-case-set
positive-decision gates, eligibility-aware arm selection, conservative cap-state
assessment, pinned checkout/weight verification, resume fingerprint checks, and
an explicit public-upload acknowledgement for the official Space command. A
parallel findings-first review found no conclusion-threatening issue; its
positive-decision, parser-bound, truncation, privacy, and selection findings were
accepted and fixed. Focused evidence is `37 passed` plus clean focused Ruff.
The per-arm bundle collectively owns the provenance contract: `raw.txt` is
verbatim, `parsed.json` maps pages/blocks/boxes to source paths, `runtime.json`
pins model/environment/generation, and `pages_html.jsonl` records the processing
module and source page. All `11` emitted page artifacts passed
`validate_artifact.py --schema page_html_v1`. No maintained module, recipe,
router, coverage claim, scorer, or golden changed; therefore no driver
continuation, coverage-matrix edit, or skills check was triggered. Registry,
Scout 016, and methodology state now carry the negative result. Next: run the
fresh full-suite and methodology checks, validate, and close via
`/mark-story-done`.

20260720-1218 — validate: findings-first review found no remaining material
Story 230 defect after the accepted harness hardening. Two independent review
packets rechecked code/decision logic and rescored every stored Onward artifact;
all nine scores reproduced exactly and neither review found a conclusion threat.
Residual limits are explicit rather than hidden: the incumbent is historical,
official BF16/FP32 parity uses one public sample, and bare multi-page markers
make semantic order partly manual. Those limits cannot plausibly reverse case
deficits of `0.2433`–`0.4506`, the Arthur page-count hard failure, or the
handwriting misses. ADR-001 remains aligned and no new ADR is warranted because
the maintained architecture did not change.

Fresh checks: focused harness `37 passed`; focused Ruff clean; `make lint`
clean; `make test` initially exposed `11` sandbox-network failures in clean-env
package installs and one API-backed OCR smoke, then the required network-enabled
rerun passed all `869` tests with four existing Pydantic deprecation warnings;
all `11` `page_html_v1` artifacts validated; `make methodology-compile && make
methodology-check` passed; and `git diff --check` passed. The implementation is
graded **A (96/100)**: every acceptance criterion and task is met, no maintained
integration was earned, and only `/mark-story-done` bookkeeping remains.
Closure recommendation: **Close now**.

20260720-1222 — mark-story-done: closed Story 230 with all top-level tasks and
acceptance groups complete, all nested runtime/provenance/comparison/value
gates satisfied, all six Central Tenets verified, eval registry lineage updated,
and no outstanding implementation gap. The result is deliberately negative but
operationally complete: current OCR remains the only maintained lane,
Unlimited-OCR adds no router/runtime burden, and Story 191 remains honestly
blocked. Final evidence: the portable attempt, `decision.json`, all nine Onward
arm bundles, both handwritten bundles, exact public-sample parity, pinned
runtime verification, `869` passing full tests, clean lint, and current
methodology graph. Recommended next step: `/check-in-diff`.
