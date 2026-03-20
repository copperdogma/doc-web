# ADR-003: Whether `DoclingDocument` Should Replace the `doc-web` Bundle Boundary

**Status:** DISCUSSING — stock tuning and a thin local hybrid proof now exist; `hybrid` currently leads, native replacement is not yet justified

<!-- Status lifecycle: PENDING → RESEARCHING → DISCUSSING → ACCEPTED -->
<!-- Alternatives: REJECTED / DEFERRED / SUPERSEDED -->
<!-- Process: docs/runbooks/adr-creation.md -->

## Context

ADR-002 accepted `doc-web` as the standalone runtime boundary that Dossier should consume via a versioned structural-website contract. Story 156 then made that boundary executable inside this repo: installable runtime package, machine-readable contract preflight, fixture-backed smoke lane, and published Dossier handoff docs. That makes `doc-web` a real incumbent, not just an idea.

Scout 011, however, found that `Docling` is the strongest external system currently known to overlap the repo's active intake seams while also exposing a native typed document representation (`DoclingDocument`) with layout, provenance, and confidence signals. The user explicitly said the goal is to give Storybook and Dossier the strongest possible ingestion engine and that they are willing to trash `doc-web` if native `DoclingDocument` support is the better answer.

This ADR exists because that is a hard-to-reverse architecture question:

- should Dossier keep consuming the current `doc-web` bundle contract;
- should `Docling` become an upstream substrate behind a thinner adapter or handoff layer;
- or should Dossier ingest native `DoclingDocument` output directly and let `doc-web` be retired or sharply narrowed?

The decision is not about taste. It is about which boundary deletes the most custom code while preserving provenance, hard-document quality, and Dossier/Storybook usability.

## Ideal Alignment

In the Ideal, the user hands the system any document and gets structured, provenance-rich, Dossier-ready output with zero configuration. The system detects format, handles OCR/layout/table complexity, preserves traceability, and graduates solved capability into Dossier instead of maintaining parallel runtime layers forever.

This ADR moves the project toward that Ideal if it:

- prefers the strongest reusable ingestion substrate over sunk-cost loyalty to `doc-web`;
- keeps traceability first instead of collapsing provenance while simplifying the runtime surface;
- treats `doc-web` as a means, not an end, and is willing to delete or narrow it if native `DoclingDocument` support is better;
- preserves an explicit, inspectable Dossier-facing contract rather than hiding the boundary inside ad hoc glue code.

The wrong move would be either:

- preserving `doc-web` because it already exists, even if `DoclingDocument` is materially better; or
- adopting `Docling` on enthusiasm alone without proving it on the repo's hard-document cases and provenance requirements.

The ideal migration discipline is also explicit now: if `Docling` is going to
win, it should win through the thinnest, most upgrade-friendly path first.
Using official `Docling` config, built-in pipelines, and documented extension
seams is preferable to owning patches, maintaining a fork, or rebuilding
another thick runtime layer. Deeper ownership only becomes justified when the
lower-ownership path is explicitly falsified by artifact evidence or operational
blockers.

## Options

### Option A: Keep `doc-web` as the Dossier-Facing Boundary; Use `Docling` Only as a Benchmark or Pattern Source

`doc-web` remains the accepted runtime contract. `Docling` is evaluated as a benchmark, research source, or optional upstream experiment, but Dossier does not ingest `DoclingDocument` directly.

Pros:

- preserves the current accepted boundary, tests, and fixture-backed runtime surface;
- keeps Dossier's contract stable while still learning from `Docling`;
- avoids a potentially expensive contract migration if `Docling` under-delivers on hard scans or provenance.

Cons:

- may preserve custom runtime code that could otherwise be deleted;
- keeps the repo on the hook for maintaining a bespoke handoff surface even if a stronger native format already exists;
- risks underweighting `Docling` because the decision is biased toward the incumbent.

### Option B: Hybrid — Use `Docling` as the Intake Substrate but Keep a Thin Adapter or Handoff Layer

`Docling` becomes the upstream intake engine for some or all documents, but Dossier still consumes a thin repo-owned contract derived from `DoclingDocument` rather than the native format directly.

Pros:

- captures most of `Docling`'s format/OCR/layout strengths without forcing Dossier to ingest a new native format immediately;
- allows the existing `doc-web` contract or a narrowed successor to remain the Dossier-facing boundary;
- creates a lower-risk migration path if native `DoclingDocument` is close but not quite sufficient.

Cons:

- risks carrying both `DoclingDocument` and a custom adapter as long-lived public surfaces;
- can become the worst of both worlds if the adapter grows into a second runtime instead of staying thin;
- still requires proving that the adapter preserves provenance and does not recreate `doc-web` under a new name.

### Option C: Let Dossier Ingest Native `DoclingDocument` Output and Retire or Supersede `doc-web`

`DoclingDocument` becomes the accepted Dossier-facing intake format. `doc-web` is retired, superseded, or reduced to a disposable migration tool if any residual conversion is needed temporarily.

Pros:

- maximizes deletion if `Docling` already solves the problem well enough;
- aligns directly with the user's "best ingestion engine wins" rule;
- avoids maintaining a custom runtime contract when a stronger native document IR may already exist.

Cons:

- only works if `DoclingDocument` satisfies real Dossier/Storybook provenance and hard-document needs;
- may shift more ingestion-format ownership into Dossier than the current `doc-web` model assumed;
- would supersede accepted direction in ADR-002 and require careful cleanup of docs, stories, and contract tests.

## Research Needed

- [ ] Can stock `Docling` on representative local documents meet or beat the current `doc-web` contract on provenance, reading order, table fidelity, repeated-structure consistency, and artifact inspectability?
- [ ] Which Dossier/Storybook features require a Dossier-facing intake contract beyond what `DoclingDocument` already exposes natively?
- [ ] If `Docling` wins technically, is native `DoclingDocument` ingestion actually lower total complexity than a thin adapter or the current `doc-web` bundle boundary?
- [ ] What operational constraints matter in practice: installation model, version pinning, runtime dependencies, optional integrations, licensing, and upgrade risk?
- [ ] Which current docs, tests, and runtime surfaces become redundant if the answer is keep / hybrid / replace?

## Repo Constraints / Existing Context

- `docs/ideal.md` says the system should accept any document with zero configuration and emit provenance-rich, Dossier-ready output.
- `docs/spec.md` and `docs/build-map.md` currently say `doc-web` is the accepted graduation target under `spec:7`, while `C1`, `C2`, `C3`, and `C7` remain active `climb` seams that a broader external substrate could pressure.
- ADR-002 is the accepted incumbent. This ADR does not erase it; it evaluates whether ADR-002 should stand, narrow, or be superseded.
- Story 156 provides a real executable incumbent baseline: installable `doc_web` package surface, `doc-web contract --json`, repo-owned smoke fixtures, and published handoff docs.
- Scout 011 is the current external-research baseline and ranks `Docling` as the strongest first replacement candidate.
- Local `Docling` pilot outputs now live under `output/runs/story157-docling-pilot-r1/docling/`. The replacement case is no longer hypothetical, but the final keep / hybrid / replace decision is still open.

## Dependencies

- ADR-002 (`docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`) — current accepted runtime-boundary decision
- Story 156 (`docs/stories/story-156-pinned-doc-web-runtime-adoption-and-dossier-readiness.md`) — incumbent executable `doc-web` baseline
- Story 158 (`docs/stories/story-158-docling-doc-web-replacement-evaluation.md`) — evaluation story for the local pilot and decision package
- Scout 011 (`docs/scout/scout-011-external-document-ingestion-systems.md`) — external `Docling` research baseline
- `docs/doc-web-bundle-contract.md` and `docs/dossier-doc-web-handoff.md` — incumbent Dossier-facing contract surfaces

## Research Summary

- Scout 011 concluded that `Docling` is the strongest external benchmark because it pressures active `C1`, `C2`, `C3`, `C7`, and `spec:7` at once while exposing a typed document IR with provenance and confidence signals.
- Local incumbent evidence now exists for `doc-web` through Story 156, so this decision can be made as a real kill test instead of a conceptual debate.
- The local pilot corpus is now pinned. Story 158 located the real Onward source corpus under `/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/`, extracted the exact incumbent hard-case source-page slice (`28-47`, `78-85`, `108-119`) into `output/runs/story157-docling-pilot-r1/input/onward-hardcase-slice-imageonly.pdf`, and recorded the corpus plus baseline references in `output/runs/story157-docling-pilot-r1/input/source_manifest.json`.
- The explicit local scoring rubric now lives in `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/local-pilot-scorecard.md`, which fixes the pass/fail bar before native `Docling` outputs are interpreted.
- Story 158 now has inspected native `Docling` outputs on the pinned corpus in `output/runs/story157-docling-pilot-r1/docling/`, and the first-pass findings are recorded in `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/local-pilot-findings.md`.
- The current missing piece is the final decision posture: whether the observed gaps justify keeping `doc-web`, recommending a thin hybrid adapter, or scheduling a second pilot to prove that the adapter/upstream-improvement path is genuinely thinner than the current boundary.
- Story 159 now adds a bounded Onward stock-tuning sweep under `output/runs/story158-docling-tuning-r1/`. That sweep proves image export is largely a stock configuration issue, but also shows that realistic OCR/table tuning still does not eliminate the decisive Onward genealogy-structure failure.
- Story 159 also now has a real hybrid proof under `output/runs/story158-docling-hybrid-proof-r1/`. That proof starts from the stock `baseline-images` artifact, rescues only pages 3 and 4 of the Arthur onset, and demonstrates that the remaining failure class can be repaired locally without rebuilding the whole boundary.

## Discussion

- 20260320-1016 — ADR created after the user explicitly stated that the real goal is a first-class ingestion engine for Storybook/Dossier and that `doc-web` can be trashed if `DoclingDocument` is the better answer. Current repo posture: ADR-002 remains the incumbent accepted direction until this ADR produces enough evidence to keep, hybridize, or supersede it.
- 20260320-1016 — The timing is now correct for this question because the repo finally has a real incumbent boundary to compare against. Before Story 156, the discussion would have been abstract. Now `doc-web` has a contract, package surface, smoke lane, and handoff docs, which means `Docling` can be judged against something concrete.
- 20260320-1058 — The local pilot is now anchored to a concrete source corpus instead of stale path references. The extracted 40-page image-only Onward slice matches the current Dossier handoff pack's hard-case chapters, which means `Docling` can be tested against the same source problem area rather than against derived HTML only. The install story also surfaced a real operational consideration: `Docling` is easy to install on this machine only when using an arm-native Python with the available `docling-parse` wheel; the x86_64 path falls into a slow local source build and is a bad default.
- 20260320-1058 — The first local pilot results are strong enough to narrow the architecture question. `Docling` clearly clears the "serious contender" bar: on the image-only hard-case slice it produced a native page-aware JSON document with `20` recovered tables, `7` detected pictures, and readable Arthur / Marie-Louise / Pierre / Antoine narrative sections without any repo-specific tuning. But the native consumer surface still misses concrete `doc-web` contract features. The built-in exports do not emit stable block anchors, do not export bundle-local images in HTML, and still leak repeated-structure subgroup headings into ordinary table cells. The current evidence therefore pressures the repo toward `hybrid` much more than immediate native `replace`.
- 20260320-1235 — Story 159's stock-tuning sweep narrowed the remaining uncertainty. The image/export concern is no longer the main blocker: enabling `generate_page_images=True`, `generate_picture_images=True`, and referenced-image HTML output produces inspectable `<img>` tags plus saved page/picture/table images on the real Onward hard-case slice. But the same sweep also shows that realistic stock tuning does not solve the core Onward fidelity problem. `OcrMacOptions(force_full_page_ocr=True)` leaves the failure region essentially unchanged, `table_structure_options.do_cell_matching=False` regresses header/cell integrity, and `TesseractCliOcrOptions(force_full_page_ocr=True)` only partially improves some later rows while leaving the first genealogy-table onset flattened and operationally noisy. This strengthens the case for `hybrid`, but it also narrows what the hybrid layer actually needs to do: repair explicit repeated-structure/table-onset failures rather than recreate all export/provenance behavior from scratch.
- 20260320-1308 — The thin hybrid path is now locally demonstrated instead of hypothetical. `scripts/spikes/docling_onward_hybrid_repair_proof.py` starts from the stock `baseline-images` chapter HTML, rescues page 3 and page 4 with targeted `gpt-4.1` OCR, splices those two repaired fragments back into the chapter, and reruns the shared genealogy merger. The repaired Arthur excerpt in `output/runs/story158-docling-hybrid-proof-r1/summary.json` moves from `8` pre-table paragraphs and `0` subgroup rows to `0` pre-table paragraphs and `46` subgroup rows, and the specific page-4 leak `ALICE'S FAMILY Barbara Hodges` is removed from the repaired excerpt. This materially strengthens `hybrid`, but it does not yet settle the ADR because the proof remains local to the Arthur two-page slice and later Onward defects still survive outside that repaired window.
- 20260320-1604 — The desired decision discipline is now clearer than it was at ADR creation time. The user explicitly wants a tiered path to `100%` Onward parity that optimizes for cheap future `Docling` upgrades: first exhaust official config, built-in pipelines, and documented extension seams; only then accept upstream-compatible deeper work such as a thin repair layer or upstream PRs; and only then consider long-lived source divergence like a fork. This means the ADR is not just deciding keep / hybrid / replace. It is also deciding what level of ownership is justified for getting `Docling` over the bar.
- 20260320-1742 — Story 159's Tier 1 closure pass tightened the current read rather than reopening it. Direct source-image input is a real official seam in this install through `ImageFormatOption`, but it does not help on the Arthur lane. `image-default` and `image-ocrmac` both fail immediately on the raw Onward page images because Pillow rejects the `302940000`-pixel source pages as decompression-bomb scale. The only surviving source-image official candidate, `image-smoldocling-transformers`, completed in `88.894s` but scored only `15.0 / 100` on the Arthur parity surface, worse than the already-poor `16.9 / 100` stock PDF baseline and far below the `89.0 / 100` hybrid proof. This materially weakens the remaining Tier 1 case in the current local environment unless a new documented extension seam is found.

## Decisions

<!-- Final decisions with rationale. Use "Settled — DO NOT suggest alternatives" for key calls. -->
- Provisional — `hybrid` is the current leading option. Stock `Docling` appears strong enough to justify an upstream-substrate role, but its native export surface does not yet satisfy the accepted Dossier-facing `doc-web` contract requirements.
- Provisional — stock configuration is enough to recover usable image export, so the remaining justification for any adapter or repair layer is now primarily stable anchors plus repeated-structure fidelity, not basic image preservation.
- Provisional — the thinnest currently demonstrated hybrid shape is page-local OCR rescue plus shared HTML normalization, not a full new runtime. That shape is now proven on the Arthur onset / page-4 continuation slice.
- Provisional — adopt a tiered ownership ladder for this decision:
  1. Tier 1: official `Docling` surfaces only
     - stock configuration
     - built-in OCR / VLM / export options
     - documented plugin / serializer / extension seams
     - preferred because it preserves the ability to pull a new `Docling`
       release, run a narrow smoke/parity check, and promote with low friction
  2. Tier 2: upstream-compatible deeper ownership
     - thin repo-owned repair/adaptation layer
     - upstream PRs
     - replayable local patches that do not require permanent source divergence
     - only justified when Tier 1 is falsified by measured quality or
       operational evidence
  3. Tier 3: source-divergent ownership
     - maintained fork
     - invasive long-lived patch stack
     - only justified when lower tiers cannot honestly reach the bar
- Provisional — on the Arthur lane, the currently discoverable locally real
  Tier 1 seams are materially exhausted.
  - raw source-image input fails operationally on the actual Onward page scale
  - the surviving source-image VLM path performs worse than the stock PDF baseline
  - further Tier 1 work should only continue if a specific documented extension
    seam is surfaced, not by repeating broad stock probes
- Open — whether the proven thin hybrid shape can stay thin when generalized beyond the Arthur two-page slice, or whether the adapter starts growing back into most of `doc-web`.
- Open — whether any still-untried documented `Docling` extension seam can move the Arthur lane materially closer to `100%`; absent that, Tier 2 ownership is now the measured default path.

## Integration Checklist

- [ ] **docs/spec.md / docs/ideal.md / docs/requirements.md** — update any project direction or compromise implications
- [ ] **Related stories** — update `Decision Refs` and add any new tasks or constraints
- [ ] **AGENTS.md** — update if this changes workflow, conventions, or agent guardrails
- [ ] **Runbooks / supporting docs** — update any operational docs affected by the decision
- [ ] **Other ADRs / decision docs** — add cross-references where relevant
- [ ] **Audit** — verify each decision is reflected in the right project artifact

## Remaining Work

- Convert the current pilot findings into a formal keep / hybrid / replace recommendation that also names the justified ownership tier
- Only reopen Tier 1 on the Arthur lane if a specific documented official extension seam is surfaced that is meaningfully different from the seams already tested
- Generalize or falsify the now-proven Tier 2 hybrid repair shape on a broader Onward slice without letting it regrow into most of `doc-web`; Story 160 now tracks that follow-up explicitly
- Decide whether the next local pilot should focus on generalized target selection / acceptance or on a broader multi-page repair lane
- Run `/align` after the ADR reaches `DISCUSSING` or `ACCEPTED` and changes project direction

## Work Log

- 20260320-1016 — ADR created: the repo now has both an executable incumbent (`doc-web`) and a plausible external challenger (`Docling`). Cross-linked ADR-002, Story 156, Story 158, and Scout 011 so the replacement question is tracked explicitly as a decision, not hidden in ad hoc notes. Next step: run the local pilot and convert the current research scaffold into a decision-ready keep / hybrid / replace synthesis.
- 20260320-1058 — Local pilot evidence now exists. Story 158 pinned the real Onward source corpus, extracted the exact incumbent hard-case source-page slice, installed `Docling 2.80.0` in an arm-native runtime, and produced inspectable native artifacts for three inputs: `testdata/tbotb-mini.pdf`, the image-only Onward hard-case slice, and the OCR-backed Arthur split chapter. Initial interpretation: `Docling` is clearly valuable as an upstream substrate, but the native export surface still misses concrete Dossier-facing requirements that `doc-web` already satisfies, especially stable anchors and usable image exports. Next step: convert that provisional read into a formal keep / hybrid / replace recommendation.
- 20260320-1235 — Story 159 added the first bounded stock-tuning sweep on the same image-only Onward hard-case slice. Results now separate configuration gaps from real model/layout gaps. Best stock result is `baseline-images`, which preserves the baseline structural quality while solving picture export via generated image assets and HTML `<img>` tags. The decisive remaining blocker is the genealogy-table onset and subgroup leakage, which survived realistic OCR/table tuning. Next step: create or execute the thinnest hybrid repair proof against that explicit failure class.
- 20260320-1308 — Story 159 now also has the first scripted thin hybrid proof. The new run under `output/runs/story158-docling-hybrid-proof-r1/` shows that a two-page targeted OCR rescue can convert the Arthur onset from flattened prose into a real genealogy table and remove the page-4 `ALICE'S FAMILY Barbara Hodges` leak, all while keeping the stock `baseline-images` Docling output as the substrate. That is the strongest evidence so far for `hybrid`. The open question is no longer "can a thin hybrid layer work at all?" but "does the proven two-page shape stay thin when generalized?"
- 20260320-1604 — The user clarified the preferred migration discipline: this ADR should optimize first for the path that keeps `Docling` easiest to upgrade. I recorded that as a tiered ownership ladder in the ADR itself. Tier 1 is official-only `Docling` usage, Tier 2 is upstream-compatible deeper ownership, and Tier 3 is source divergence. This does not change the current measured winner, which is still a thin hybrid path, but it raises the bar for when deeper ownership is acceptable: each lower tier now needs explicit falsification of the higher one.
- 20260320-1742 — Story 159 closed the remaining direct source-image Tier 1 question for the Arthur lane. The result did not rescue the official-only path. Standard source-image input and OcrMac both fail on the raw Onward page scale before producing usable artifacts, and the surviving source-image SmolDocling VLM path performs worse than the stock PDF baseline on the parity surface. This does not mathematically prove every possible future Tier 1 seam is impossible, but it is strong enough to change the default next move: unless a concrete documented extension seam appears, the measured path forward is now Tier 2 hybrid generalization rather than more broad Tier 1 probing.
