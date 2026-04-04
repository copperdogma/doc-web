---
title: Widen Born-Digital PDF Native-Text Validation and Routing Decision
status: Done
priority: High
ideal_refs:
- 'Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #6 (Validate), Zero
  configuration, Any format, any condition, Traceability is the Product'
spec_refs:
- spec:1
- spec:1.1
- spec:3
- spec:3.1
- spec:6
- spec:7
- spec:8
adr_refs: []
depends_on:
- '157'
- '165'
- '166'
- '168'
- '169'
category_refs:
- spec:1
- spec:3
- spec:6
- spec:7
- spec:8
compromise_refs:
- B1
- C2
- C3
input_coverage_refs:
- born-digital-pdf
architecture_domains: []
roadmap_tags: []
legacy_system: ''
---

# Story 170 — Widen Born-Digital PDF Native-Text Validation and Routing Decision

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #6 (Validate), Zero configuration, Any format, any condition, Traceability is the Product
**Spec Refs**: spec:1 (spec:1.1, C2), spec:3 (spec:3.1, C3), spec:6, spec:7, spec:8 (B1)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 3 Layout & Structure Understanding (`exists`, C3 `climb`); Category 7 Graduation & Dossier Handoff (`partial`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`); Input Coverage row `born-digital-pdf` (`has fixture`); Gap 2 — Born-digital PDF native text extraction
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`, `docs/stories/story-165-marker-breadth-comparator-born-digital-pdf.md`, `docs/stories/story-166-marker-internals-born-digital-pdf-substrate.md`, `docs/stories/story-168-marker-lite-maintained-born-digital-pdf-path.md`, `docs/stories/story-169-restore-contact-sheet-intake-and-benchmark-auto-book-type-detection.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/build-map.md`, `None found after search in docs/decisions/ for born-digital default-routing-specific ADRs`
**Depends On**: Story 157, Story 165, Story 166, Story 168, Story 169

## Goal

Widen the maintained born-digital PDF native-text lane beyond `testdata/tbotb-mini.pdf`, measure it honestly against the maintained OCR PDF baseline on a broader fixture set, and turn that evidence into a consistent routing decision. This story should either earn a stronger maintained recommendation for the Marker-lite path on defined born-digital cases or explicitly keep OCR as the general PDF default and Marker as an optional explicit lane, but it must stop leaving the repo in the current one-fixture limbo where code, docs, and operator guidance do not fully agree.

## Acceptance Criteria

- [x] A widened born-digital validation corpus exists beyond `testdata/tbotb-mini.pdf`, with at least two additional fixtures or explicitly documented validation assets covering more than one born-digital pattern family (for example simple prose plus a more structured or illustrated case), and the intended routing / review dimensions for each fixture are recorded.
- [x] The maintained Marker-lite native-text path and the maintained OCR PDF baseline are both run through `driver.py` on the widened corpus, and manual artifact inspection is recorded for representative `page_html_v1`, `doc_web_bundle/manifest.json`, `doc_web_bundle/provenance/blocks.jsonl`, and final HTML outputs. Any fixture claimed as acceptable shows no inspected silent text-loss or provenance regression.
- [x] The routing rule becomes consistent and honest across code and docs: either Marker-lite earns a broader maintained recommendation/default for defined born-digital cases, or the repo explicitly keeps OCR as the default general PDF lane and Marker as an optional explicit path. No surface silently claims broader support than the evidence earns.
- [x] Repeatable proof remains after the story: repo-owned smoke/comparison coverage or a maintained harness exists for the widened lane, and `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, and any affected intake/operator docs reflect the new reality honestly.

## Out of Scope

- Claiming `docx`, `xlsx`, `pptx`, `epub`, or other office-format support from the Marker stack
- Replacing the explicit-recipe compromise (`C2`) with hidden dispatch or silent auto-routing
- Reopening the negative `Docling` or `Surya` boundary decisions
- Hiding Docker, cached runtime, GPL/model-license, or cold-start constraints behind a default path
- Solving every born-digital layout edge case in one pass if widened evidence says the path should stay optional

## Approach Evaluation

- **Simplification baseline**: first rerun the current Marker-lite and OCR paths unchanged on a widened corpus. A single LLM call cannot answer runtime, fixture, or routing honesty here, and if OCR already wins on widened evidence, the right answer may be narrowing claims rather than adding code.
- **AI-only**: low-value as the primary path. A multimodal classifier could guess which route to use per PDF, but that would hide the routing question inside a prompt before the repo has enough evidence to support the choice.
- **Hybrid**: leading candidate. Use deterministic fixture selection, runtime metrics, provenance checks, and structural comparisons, with AI only where semantic review or benchmark scoring needs help interpreting HTML/structure differences.
- **Pure code**: appropriate for fixture plumbing, harnesses, docs, and explicit recipe-mapping changes once the comparison evidence exists. It is not sufficient by itself to settle quality.
- **Repo constraints / prior decisions**: ADR-002 keeps the `doc-web` boundary explicit; Story 157 restored the OCR-backed PDF lane as the maintained baseline; Stories 165, 166, and 168 proved the bounded Marker-lite seam but stopped short of broad adoption; Scout 011 explicitly says to widen beyond the single tiny fixture before any default-routing claim.
- **Existing patterns to reuse**: `modules/extract/extract_pdf_marker_lite_html_v1`, `modules/common/marker_page_html.py`, `modules/common/marker_lite_runtime.py`, `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml`, `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`, `tests/test_extract_pdf_marker_lite_html_v1.py`, `tests/test_pdf_intake_recipe.py`, `modules/intake/intake_plan_utils.py`, and Story 169's repo-owned benchmark-harness pattern.
- **Eval**: the deciding proof is a widened born-digital corpus comparison measuring text fidelity, structure preservation, provenance completeness, runtime/cold-start burden, and operator honesty. No dedicated born-digital routing/native-text eval exists today, so this story may need to add the smallest honest repeatable harness or benchmark surface.

## Tasks

- [x] Freeze the widened evaluation surface:
  - [x] Reuse the accessible Story 169 corpus first (`tbotb-mini`, `rfp`, `release-forms`) and decide whether any additional validation asset is still required
  - [x] Record expected routing outcomes and review dimensions per fixture
  - [x] Decide whether a repo-owned harness or a disciplined manual comparison surface is the smallest honest proof
- [x] Re-run the current maintained Marker-lite and OCR PDF lanes on the widened corpus before changing routing code or docs, and record exact failure modes / wins:
  - [x] runtime and cold-start cost
  - [x] text preservation or loss differences
  - [x] heading, order, table, or block-structure differences
  - [x] bundle / provenance completeness
- [x] Implement only the smallest behavior changes the widened evidence justifies:
  - [x] No generic Marker-lite normalization or runtime fixes were needed after the widened reruns; keep the seam stable and narrow recommendation honesty instead
  - [x] intake / recommendation / operator-doc routing changes only if the widened evidence supports them
  - [x] if the widened evidence is negative, narrow or remove over-claiming routes/docs instead of forcing adoption
- [x] Add or extend repeatable proof:
  - [x] repo-owned fixture(s), smoke tests, or a maintained comparison harness
  - [x] explicit artifact-inspection notes for the accepted slice
  - [x] refresh the affected benchmark corpus / score recording surface in `docs/evals/registry.yaml`
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL/HTML data
  - [ ] If agent tooling changed: `make skills-check` (not expected)
- [x] If evals or goldens changed: rerun the affected harness and update `docs/evals/registry.yaml`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every routing claim and accepted artifact still traces to source page, source block, confidence, and processing step
  - [x] T1 — AI-First: use AI only where it beats deterministic routing or semantic review; do not hide uncertainty in prompts
  - [x] T2 — Eval Before Build: widen and measure the current path before inventing more routing logic
  - [x] T3 — Fidelity: preserve born-digital text and structure faithfully; no silent losses while improving routing claims
  - [x] T4 — Modular: keep explicit recipes and thin adapters; avoid book-specific branches
  - [x] T5 — Inspect Artifacts: manually inspect emitted JSON/JSONL/HTML artifacts, not just scores and logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: born-digital extract/routing surfaces, comparison harnesses/fixtures, intake recommendation helpers, and the docs that define format-coverage truth.
- **Build-map reality**: Category 1 owns the routing question and is `exists` / `climb`; Category 3 may own any generic normalization defects exposed by widened fixtures; Category 7 still blocks stronger adoption/graduation claims because fixture breadth is tiny; Category 8 can host a new comparison surface. Input Coverage still keeps `born-digital-pdf` at `has fixture`, and Gap 2 explicitly says this is validation + widening work rather than first-path invention.
- **Substrate evidence**: `modules/extract/extract_pdf_marker_lite_html_v1/module.yaml` exists and emits `page_html_v1`; `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml` and `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` provide maintained comparison lanes; `tests/test_extract_pdf_marker_lite_html_v1.py` and `tests/test_pdf_intake_recipe.py` already cover the seams; `modules/intake/intake_plan_utils.py` currently routes `born_digital_pdf` to the Marker-lite recipe, so the docs/code consistency question is real rather than hypothetical. Story 168 documents historical artifact proof under `output/runs/story168-marker-lite-proof-r4/` and `story168-ocr-baseline-r1`, but widened proof is still missing.
- **Data contracts / schemas**: the primary surfaces are `page_html_v1`, `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, and `intake_plan_v1` if recommendation logic changes. Avoid schema churn unless widened evidence reveals a real missing field for comparison/reporting.
- **File sizes**: already-large likely touch points are `modules/common/marker_lite_runtime.py` (763 lines), `modules/common/marker_page_html.py` (780), `docs/build-map.md` (584), and `docs/evals/registry.yaml` (509). Prefer a small harness, new fixture file, or focused helper over expanding those further unless the change truly belongs there. Moderate likely touch points include `modules/extract/extract_pdf_marker_lite_html_v1/main.py` (168), `modules/intake/intake_plan_utils.py` (133), `modules/intake/contact_sheet_overview_v1/main.py` (192), `modules/intake/zoom_refine_v1/main.py` (123), `tests/test_extract_pdf_marker_lite_html_v1.py` (138), and `tests/test_pdf_intake_recipe.py` (62).
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, ADR-002, Stories 157/165/166/168/169, Scout 011, and the current born-digital recipe/module/test substrate. No separate ADR currently governs born-digital default-routing beyond the accepted `doc-web` boundary.

## Files to Modify

- `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml` — widen validation recipe or runtime params if the native-text lane needs honest generic adjustments (42 lines)
- `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` — keep the OCR baseline comparison lane honest and reproducible (88 lines)
- `modules/extract/extract_pdf_marker_lite_html_v1/main.py` — generic extract-stage fixes or comparison metrics if widened fixtures expose new defects (168 lines)
- `modules/common/marker_page_html.py` — generic normalization fixes for widened born-digital cases if required (780 lines)
- `modules/common/marker_lite_runtime.py` — runtime/bootstrap metrics or operator-surface fixes if the routing decision depends on them (763 lines)
- `modules/intake/intake_plan_utils.py` — reconcile explicit maintained recipe recommendation with the widened evidence (133 lines)
- `modules/intake/contact_sheet_overview_v1/main.py` — only if recommendation wording or plan fields need to change for honesty (192 lines)
- `modules/intake/zoom_refine_v1/main.py` — only if recommendation output or warnings need to change for honesty (123 lines)
- `tests/test_extract_pdf_marker_lite_html_v1.py` — add widened regression coverage (138 lines)
- `tests/test_pdf_intake_recipe.py` — add comparison or smoke coverage for widened born-digital fixtures (62 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — update the `born-digital-pdf` row honestly (325 lines)
- `docs/build-map.md` — reconcile Gap 2, Input Coverage, and next-action truth after the widened evidence lands (584 lines)
- `docs/evals/registry.yaml` — add/update the comparison surface only if this story creates a real repeatable eval or benchmark (509 lines)
- `docs/scout/scout-011-external-document-ingestion-systems.md` — update the Marker standing once the widened routing decision is real (176 lines)
- `README.md` and `docs/RUNBOOK.md` — only if the operator-facing default/optional guidance changes
- New repo-owned born-digital fixture(s) under `testdata/` or a new maintained comparison harness under `benchmarks/scripts/` or `tests/`

## Redundancy / Removal Targets

- Any docs or intake surfaces that imply Marker-lite is already the honest default for all `born-digital-pdf` inputs if widened evidence does not support that
- Any stale born-digital notes that still describe the path as OCR-only after Story 168 if widened evidence supports a stronger maintained claim
- One-off comparison scratch scripts if the story lands a maintained harness

## Notes

- Fresh Story 170 reruns showed that the main ambiguity was not text-layer probing alone. The current maintained full PDF recipes are still book-contract-shaped: `tbotb-mini` succeeds, but `rfp`, `release-forms`, and the scanned-prose control all reach `page_html_v1` and then fail later at `portionize_toc`. The routing surface therefore needed narrowing, not promotion.
- Prefer repo-owned fixtures where licensing allows. If wider validation relies on shared local PDFs, they can support manual evidence but should not be the only repeatable proof surface.
- Keep the story honest about operator cost. A path that wins structurally but still requires Docker, cached weights, and much slower cold starts may deserve an explicit niche lane rather than a default recommendation.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes a real active gap in the current mission path: the repo can recommend a born-digital recipe and can run a bounded native-text lane, but it still does not have enough evidence to say whether that lane should stay niche, become the honest maintained default for born-digital inputs, or be narrowed back.
- **Relevant build-map state:** Category 1 is `exists` / `climb`; Category 7 is still `partial`; Input Coverage keeps `born-digital-pdf` at `has fixture`; Gap 2 explicitly calls for validation + widening work on the new lane, not more invention.
- **Critical substrate verified in code:** the maintained Marker-lite recipe exists, the maintained OCR PDF baseline exists, the extract module and bundle/provenance surfaces exist, and intake recommendation helpers still own the explicit recipe recommendation seam. This is buildable reality, not paper substrate.
- **Fresh baseline evidence gathered in this pass:** `python -m pytest tests/test_extract_pdf_marker_lite_html_v1.py tests/test_pdf_intake_recipe.py -q` passed (`3 passed, 2 warnings`). A local audit of `benchmarks/golden/auto-book-type-detection/corpus.json` found all 10 corpus PDFs present on this machine. Fresh `driver.py` reruns then established the real widened story: `tbotb-mini` succeeds through both maintained lanes, while `rfp`, `release-forms`, and the scanned-prose control all produce `page_html_v1` and then fail at `portionize_toc`. The open gap is therefore recommendation honesty for flat/non-book PDFs, not merely native-text quality on a wider slice.
- **Critical missing slice:** the repo still has only one repo-owned born-digital fixture plus historical story-local proof notes. This checkout has no retained `output/runs/story168-*` or `output/runs/auto-book-type-detection/*` artifact directories, so fresh `driver.py` reruns are required for honest comparison evidence.
- **Scope adjustment folded in automatically:** the story no longer needs to invent a validation corpus from zero. It should reuse the accessible Story 169 local corpus first, then decide whether a new repo-owned born-digital fixture or a maintained comparison harness is still needed for repeatability. The story must also treat routing-surface narrowing as a valid success outcome if widened evidence is negative.

### Eval-First Gate

- **Baseline first:** run the current Marker-lite and OCR PDF lanes unchanged on the widened corpus before changing routing code or docs.
- **What the baseline must score:** text fidelity, structure preservation, provenance completeness, runtime/cold-start/operator burden, and whether the current routing surfaces over- or under-claim support.
- **Current baseline number:** current seam substrate checks are green (`3 passed` on the Marker-lite extract + PDF-entry smoke tests), and the refreshed `auto-book-type-detection` harness still scores `accuracy = 1.0`, `overall = 1.0`, `pass_rate = 1.0` after the routing surface is narrowed. The open baseline gap is no longer simple classification drift; it is that the maintained full PDF HTML recipes still only cover the book-like slice honestly.
- **Chosen proof surface:** first use a disciplined multi-fixture manual comparison over the accessible Story 169 born-digital subset (`tbotb-mini`, `rfp`, `release-forms`) plus one or more OCR-routed control PDFs from the same corpus. If that proves stable and useful, extract the comparison into the smallest maintained harness or smoke surface. Prompt-only eval is insufficient because the core question is end-to-end artifact and operator truth, not prompt quality in isolation.

### Implementation Tasks

#### Task 1 — Widen fixtures and freeze the comparison surface (`M`)

- Files: likely `benchmarks/golden/auto-book-type-detection/corpus.json` (read-only reference), a new story-local comparison note or harness under `benchmarks/scripts/` or `tests/`, and this story file.
- Change: start with the already accessible Story 169 corpus instead of sourcing random new inputs. Freeze the first widened born-digital slice around `tbotb-mini`, `rfp`, and `release-forms`, and keep one or two OCR-routed control PDFs from the same corpus nearby so the routing story stays honest.
- Impact / risk: the risk is overfitting the story to three convenience PDFs. If those three are too similar, the story must either add a broader local asset or explicitly stop short of a default-routing claim.
- Done when: the fixture list, routing expectations, and review dimensions are explicit, and the story names whether the first proof is manual-only or also lands a repeatable harness.

#### Task 2 — Run unchanged baseline comparisons (`S-M`)

- Files: likely no code changes if current recipes run cleanly; evidence should land under fresh `output/runs/story170-*`.
- Change: re-run `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml` and `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` unchanged on the widened slice.
- Impact / risk: this is the main truth-discovery task. The likely failure modes are runtime heaviness, provenance regressions on richer PDFs, or cases where OCR stays more robust despite being structurally cruder.
- Done when: fresh `driver.py` evidence exists for both lanes on the widened slice and manual inspection records where Marker-lite truly wins, where OCR wins, and where cold-start/operator cost changes the routing answer.

#### Task 3 — Land only evidence-backed behavior changes (`M`)

- Files: `modules/intake/intake_plan_utils.py`, `benchmarks/golden/auto-book-type-detection/corpus.json`, and the truth-surface docs/tests that describe the maintained recommendation seam.
- Change: if the widened runs show the full recipes stay book-contract-shaped, keep the extraction code stable and narrow intake guidance instead of inventing rescue logic. Update the explicit recipe-selection surfaces conservatively so flat/non-book PDFs surface `no-recipe-needed` rather than over-recommending a maintained lane that fails later.
- Impact / risk: the main risk is turning this into an adoption-defense story. Do not invent rescue logic purely to preserve a preferred routing outcome.
- Done when: any code changes are directly tied to widened evidence and the recommendation surfaces say exactly what the evidence supports.

#### Task 4 — Leave repeatable proof and honest docs behind (`S-M`)

- Files: `tests/test_pdf_intake_recipe.py`, possibly a new comparison harness under `tests/` or `benchmarks/scripts/`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/build-map.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, and optionally `README.md` / `docs/RUNBOOK.md`.
- Change: leave the repo with a repeatable comparison or smoke lane for whatever the story proves, and update the truth surfaces together.
- Impact / risk: if widened evidence still depends on local non-repo-owned PDFs, the docs must keep that explicit and avoid overpromoting the format family to `passing`.
- Done when: the build map, coverage matrix, scout, and operator guidance all tell one coherent story, and the repeatable proof surface is named.

### Impact Analysis

- **Primary blast radius:** born-digital recipes, Marker-lite extract/runtime helpers, intake recommendation helpers, and format-coverage truth docs.
- **Secondary blast radius:** coverage matrix, eval registry if a new comparison surface is added, and any README/runbook guidance that currently over- or under-claims born-digital support.
- **Main risk:** conflating "works on one tiny fixture" with "deserves default routing." The story should optimize for honest maintained behavior, not for forcing a win for either path.

### Structural Health Notes

- Reuse the existing Story 165/166/168 seam instead of creating another external-tool adapter path.
- Avoid expanding already-large files (`modules/common/marker_lite_runtime.py`, `modules/common/marker_page_html.py`, `docs/build-map.md`, `docs/evals/registry.yaml`) unless the widened evidence clearly belongs there.
- Historical proof directories from Story 168 are not present in this checkout, so this story cannot rely on prior artifact inspection as current evidence.

### Human-Approval Blockers / Risks

- If the story cannot source enough wider fixtures legally or operationally, stop and propose the smallest honest fallback instead of pretending the family is now passing.
- If widened evidence says Marker-lite should not be the default, accept that result and narrow the routing surfaces rather than spending the story protecting a preferred outcome.

### What Done Looks Like

- Multiple born-digital fixtures exist in the comparison surface.
- Both maintained lanes run through `driver.py` and produce inspected artifacts.
- The routing rule is consistent across code and docs.
- The build map and coverage matrix reflect the evidence honestly, whether the answer is promotion, explicit optionality, or rollback of over-claiming.

## Work Log

20260328-2300 — story created: triage identified born-digital PDF widening as the highest-leverage next action because `docs/build-map.md` still lists Gap 2 as the top non-passing format-family problem after the maintained Marker-lite lane landed. Evidence: Input Coverage still keeps `born-digital-pdf` at `has fixture`; Scout 011 says to widen beyond the single tiny fixture before any broader routing claim; and `modules/intake/intake_plan_utils.py` already maps `born_digital_pdf` to the Marker-lite recipe, so code/doc/operator truth is currently ahead of the evidence. Next step: `/build-story` should verify candidate fixtures, choose the smallest honest comparison surface, and decide whether the likely outcome is promotion, explicit optionality, or rollback of over-claiming routing surfaces.
20260328-2313 — explored substrate and refined plan: reviewed `docs/ideal.md`, `docs/spec.md` (`spec:1`, `spec:3`, `spec:6`, `spec:7`, `spec:8`), the relevant `docs/build-map.md` categories plus Input Coverage / Gap 2, ADR-002, Stories 157/165/166/168/169, Scout 011, `modules/extract/extract_pdf_marker_lite_html_v1/main.py`, `modules/common/marker_page_html.py`, `modules/common/marker_lite_runtime.py`, `modules/intake/contact_sheet_builder_v1/main.py`, `modules/intake/contact_sheet_overview_v1/main.py`, `modules/intake/zoom_refine_v1/main.py`, `modules/intake/intake_plan_utils.py`, `scripts/spikes/marker_breadth_benchmark.py`, and the current recipe/test surfaces. Fresh baseline checks passed: `python -m pytest tests/test_extract_pdf_marker_lite_html_v1.py tests/test_pdf_intake_recipe.py -q` => `3 passed, 2 warnings`. Fresh routing audit on `benchmarks/golden/auto-book-type-detection/corpus.json` found all 10 local PDFs accessible here; the current `probe_pdf_text_layer(...)` plus `choose_maintained_recipe(...)` pipeline matches the expected Story 169 routing `10/10`, with three current Marker-routed born-digital candidates already available (`tbotb-mini`, `rfp`, `release-forms`). Critical substrate verified: maintained Marker-lite and OCR recipes exist; extract/runtime helpers exist; intake recommendation surfaces already route born-digital cases explicitly. Critical missing slice: this checkout has no retained `output/runs/story168-*` or `output/runs/auto-book-type-detection/*` artifact trees, so widened proof must be rerun fresh through `driver.py`. Files likely to change: the born-digital recipes, Marker-lite runtime/normalization helpers if widened runs expose generic defects, intake recommendation helpers only if the widened evidence changes routing honesty, `tests/test_pdf_intake_recipe.py` or a new comparison harness, and the build-map / coverage / scout truth surfaces. Files at risk: the large Marker helper files and build-map/eval docs if the story spreads unnecessarily. Surprise found: fixture sourcing is not the main blocker after all; the Story 169 corpus already supplies a buildable widened comparison slice, so the real problem is evidence freshness and repeatability, not basic input availability. Next step: present the refined plan and wait for approval before implementation.
20260328-2318 — implementation started after approval: moved Story 170 to `In Progress` in the story file and story index so the fresh widened comparison slice can be executed against the approved plan. Next step: rerun the Marker-lite and OCR PDF lanes on the first widened born-digital slice (`tbotb-mini`, `rfp`, `release-forms`) plus OCR-routed controls and inspect the emitted artifacts before changing code or docs.
20260328-2332 — widened reruns changed the story direction from promotion to narrowing: fresh `driver.py` proofs under `output/runs/story170-marker-tbotb-r1/`, `output/runs/story170-marker-rfp-r1/`, `output/runs/story170-marker-release-forms-r1/`, `output/runs/story170-ocr-tbotb-r1/`, `output/runs/story170-ocr-rfp-r1/`, `output/runs/story170-ocr-release-forms-r1/`, `output/runs/story170-ocr-scanned-prose-r1/`, and `output/runs/story170-ocr-astrosmash-r1/` show that both maintained lanes still succeed on `tbotb-mini` but `rfp`, `release-forms`, and the scanned-prose control all fail later at `portionize_toc` after producing `page_html_v1`. Manual inspection confirms the reviewed positive slice is still honest: `output/runs/story170-marker-tbotb-r1/output/html/manifest.json` and `output/runs/story170-marker-tbotb-r1/output/html/provenance/blocks.jsonl` preserve the expected bundle/provenance contract, and `output/runs/story170-marker-tbotb-r1/output/html/page-001.html` keeps the TOC, headings, and choice-book structure without inspected text loss. Manual inspection also confirms the widened negative slice is a routing honesty problem, not an extract-stage crash: `output/runs/story170-marker-rfp-r1/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl` and `output/runs/story170-marker-release-forms-r1/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl` contain sensible source-linked HTML, but both runs stop at `portionize_toc`; OCR does the same on `output/runs/story170-ocr-rfp-r1/` and `output/runs/story170-ocr-release-forms-r1/`. Impact: this falsifies the idea that born-digital widening should broaden Marker recommendations today. The honest next step became narrowing the recommendation surface so flat/non-book PDFs stop receiving maintained full-recipe guidance they cannot complete.
20260328-2340 — narrowed the maintained PDF recommendation surface and refreshed the scored proof: updated `modules/intake/intake_plan_utils.py` to recommend the maintained PDF HTML recipes only for book-like / structured multi-page cases, added `tests/test_intake_plan_utils.py`, and refreshed `benchmarks/golden/auto-book-type-detection/corpus.json` so short flat PDFs now expect `no-recipe-needed`. Mismatch classification: both **pipeline-wrong** and **test-wrong** were present. The deterministic routing helper was too coarse relative to the current full-recipe contract, and Story 169's corpus expectations for `rfp` / `release-forms` encoded that same over-broad assumption. Fresh rerun evidence now converges: `benchmarks/results/auto-book-type-detection-story170.json` scored `accuracy = 1.0`, `overall = 1.0`, `pass_rate = 1.0`; representative final plans include `output/runs/auto-book-type-detection/tbotb-mini/overview_plan_final.jsonl` (`cyoa` -> Marker-lite), `output/runs/auto-book-type-detection/scanned-prose-mini/overview_plan_final.jsonl` (`novel` -> `no-recipe-needed`), `output/runs/auto-book-type-detection/rfp/overview_plan_final.jsonl` (`other` -> `no-recipe-needed`), and `output/runs/auto-book-type-detection/astrosmash-manual/overview_plan_final.jsonl` (`other` + `tables/images` -> OCR). Repo verification also passed fresh: `python -m pytest tests/test_extract_pdf_marker_lite_html_v1.py tests/test_pdf_intake_recipe.py tests/test_intake_plan_utils.py -q` => `8 passed, 2 warnings`; `make lint` => pass; `make test` => `384 passed, 12 warnings`. Impact: Story 170 now leaves the repo in an honest state instead of a one-fixture limbo. The bounded Marker lane remains available for the proven book-like slice, while flat/non-book PDFs explicitly surface `no-recipe-needed` until a maintained non-TOC PDF lane exists.
20260328-2357 — validation follow-up closed the remaining doc drift: updated `docs/build-map.md` so `Next Actions` no longer says to create Story 170, and updated the `Marker` row in `docs/scout/scout-011-external-document-ingestion-systems.md` so the portfolio view reflects the widened Story 170 result rather than pointing back to pre-widening proof work. Fresh follow-up verification kept the implementation surface stable and rechecked the story close-out slice: `python -m pytest tests/test_extract_pdf_marker_lite_html_v1.py tests/test_pdf_intake_recipe.py tests/test_intake_plan_utils.py -q` => `8 passed, 2 warnings`; manual re-read of `docs/build-map.md` and `docs/scout/scout-011-external-document-ingestion-systems.md` confirmed the stale guidance is gone. Impact: AC4 is now fully honest across the build map, scout, story, and implementation evidence. The story is ready for `/mark-story-done`; no additional pipeline rerun was needed because this follow-up only corrected documentation drift uncovered during validation.
20260329-0000 — story closed via `/mark-story-done`: fresh close-out verification passed in this pass with `python -m pytest tests/` => `384 passed, 12 warnings` and `python -m ruff check modules/ tests/` => `All checks passed!`. Closure evidence remains anchored in the previously inspected Story 170 artifacts and score surfaces, including `output/runs/story170-marker-tbotb-r1/output/html/manifest.json`, `output/runs/story170-marker-rfp-r1/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl`, and `benchmarks/results/auto-book-type-detection-story170.json`. Updated the story status/workflow gates, synchronized `docs/stories.md`, and added the completion changelog entry so the lifecycle record matches the shipped slice. Next step: `/check-in-diff`.
