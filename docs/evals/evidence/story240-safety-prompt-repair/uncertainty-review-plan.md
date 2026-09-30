# Story240 — Uncertainty review before any Sol safety promotion

**Offline policy/qualification preparation, September30,2026.** Story240's measured evaluation stays Done. This document proposes a NEW opt-in, reviewed safety step; it does not implement it, authorize paid calls, adopt canonical goldens, change a prompt/schema/default, or qualify production behavior. Preserve the measured Attempt048 evidence: Sol medium4096/high source-adjudicated22/22 and physical5/5; S3 policy0/1. Original primary21/22 and both source-correction timelines remain visible.

## Recommended policy: every candidate requires an explicit source-reviewed decision

Use Sol's existing strict pass/fail response as a **proposal**, followed by human review of **every candidate, passes AND fails**, in a bounded opt-in pilot. Cam is the initial review authority; another named human can act only after explicit delegation. An agent can prepare the source/crop display, record Cam's decisions and check hashes; neither a subject model nor an AI-written run assessment grants publication authority. Missing or stale review means **hold publication**, preserving both source and candidate. Rejecting a candidate never authorizes source deletion or silent omission of the illustration.

The enforceable boundary is universal review, not the model's claimed confidence or whether its reason includes an uncertainty word. An apparently confident pass like S3 still waits. Review all source pages in the pilot for missed illustrations as well as existing candidate crops; a reviewed queue cannot establish detector completeness by itself. Every intended source visual must be accounted for by an approved crop or remain explicitly unresolved; no default “omit illustration” disposition.

| Option | Decision |
|---|---|
| Route only model-declared uncertainty or confidence below a threshold | Do not use for initial release. Pass-only ownership mistakes can look confident; no independent ambiguity detector was qualified. |
| Add another LLM or agreement check as the release authority | Defer. Agreement/confidence is not independent proof of source ownership; this adds paid work without a measured routing guarantee. |
| Review all candidate proposals, including failures, before publication | **Recommended bounded pilot.** Covers silent passes and protects valid illustrations from false rejection; adds explicit operator work rather than an unproven trigger. |

This manual compromise moves toward Fidelity to Source and Traceability while automatic uncertainty routing is unproven. A later narrower trigger must independently demonstrate missed-ambiguity recall and safe release behavior before reducing review coverage.

## S3 and the meaning of uncertainty

S3's mirrored fragments and faint central strokes plausibly form one coherent illustration. Multiple components, absent captions, weak contrast or similarity alone do not prove separate visuals or indeterminate ownership. Never require a model to recover hidden fixture-author intent. Source-visible composition/boundaries/grouping and actual caption relationships determine whether a crop is valid. If independent reviewers cannot establish one supported boundary, that is a **review-policy case**, not a source-confirmed physically unsafe crop.

Do not rewrite Attempt048's declared S3 policy miss. For future qualification, separate (a) physically determinate good/bad crops from (b) reviewer-unresolved ownership cases with explicitly recorded permissible interpretations. On ambiguous cases, pass/fail model proposals are reported descriptively; the release requirement is that neither proposal bypasses explicit review. A reviewer may approve a coherent interpretation when supported by source evidence, documenting the chosen boundary. If ownership remains unresolved, the default action is hold. No forced fail-label merely to reward agreement with the fixture designer.

## Actual owner substrate and the missing enforcement

Source trace verified September30 in this worktree:

| Existing file/seam | What it supports and what it does not |
|---|---|
| `modules/extract/crop_illustrations_guided_v1/main.py:5216` and `module.yaml` | Writes `illustration_v1` rows containing run/source/page/bbox/filename/caption and detector/caption identities. It writes image bytes before manifest. It has no maintained page-context pass/fail safety call or per-crop human approval. |
| `configs/recipes/recipe-onward-images-html-mvp.yaml:34`, `:65`, `:72`, `:75` | Existing detector/captionassist/layout-trim stage, Gemini3Flash rescue and retained C5 helpers. Keep all settings intact. A new Sol review step would follow cropping; it is **not replacement of an existing GPT5.5 runtime safety call**. |
| `benchmarks/prompts/validate-page-level-crop.js`, `benchmarks/providers/openai_responses_model.py`, `benchmarks/tasks/crop-page-level-deletion-gate.yaml` | Page-context classifier is a benchmark surface. Requested Sol configuration/native schema are measured there; these files do not enforce runtime publication. |
| `modules/build/build_chapter_html_v1/main.py:1241`, `:1306`, `:2523`, `:3240` | Builder groups supplied crop rows, copies named images, then attaches them to HTML. It does not inspect a review sidecar. Filtering a manifest alone is insufficient: it can silently omit source visuals and image placeholders. |
| `driver.py:1568`, `:2924`, `:3070`; maintained recipe `:157` | Existing `--end-at`/`--start-from`, failed-stage halt and DAG inputs provide pause/resume plumbing. Builder currently consumes cropping directly. These are stage boundaries, not a persisted crop review queue or an approval check. |
| `modules/common/run_registry.py:455`, `tools/run_registry.py:76` | Run-level assessments record scope/status/author/evidence (author defaults `ai`). Useful provenance summary; neither authenticated per-crop decisions nor enforcement. Do not treat `known_good` as crop-release authority. |
| `modules/extract/crop_illustrations_guided_v1/main.py:5906` and builder `:1306` | Crop refresh merges targeted rows or prunes stale images; builder also prunes published assets not in its supplied manifest. Preserve immutable original candidate/source custody before any future recrop/refresh; do not edit the raw manifest in place to reject a crop. |
| `driver.py:1266`, `validate_artifact.py:SCHEMA_MAP`, `schemas.py:ImageCrop` | Guided `illustration_v1` is not the same registered `image_crop_v1` model. A new release module must validate its sidecars and completeness itself; generic driver schema stamping does not already enforce this policy. |

Current C5 deletion condition in `docs/spec.md:110` is a50-page detector/text-exclusion bar, distinct from this22-case classifier comparison. This proposal preserves detector/caption/C5 defaults and does not remove heuristics. Current reviewed run/bundle scaffolding is reusable evidence plumbing, not a crop-review UI. No existing source-deletion permission is inferred from a benchmark fail.

## Proposed decision and artifact contract (new code required later)

For a pilot, snapshot the complete candidate manifest, each source page and crop bytes before review. Bind stable `candidate_id` to runID, source-page identity, source SHA256, crop SHA256, bbox/geometry and original manifest-row hash. Record source coordinate system/native dimensions and the source image actually used for cropping. Display the full source and full-resolution crop side by side with the proposed boundary and caption context. Changing source, crop, geometry or source coordinate transform invalidates prior decisions even when filenames stay the same.

Keep four separate artifacts under the pilot run, rather than adding a third verdict to the model schema:

1. **`crop_safety_proposals.jsonl`:** candidate bindings; requested/served model, effort/output/detail; prompt/schema/scorer identities; raw request/response hashes and existing pass/fail/observed flags/reason. A model error remains an operational issue. Every candidate remains in inventory regardless of model verdict.
2. **`crop_review_decisions.jsonl`:** append-only explicit reviewer event: candidate bindings, policy version, action, source-backed reason, chosen visual boundary if approved, reviewer identity, explicit authority/delegation reference, decision timestamp and direct reviewer-input evidence. Do not accept a model-written reviewer identity or confidence field as authority. Supersession identifies the previous event; contradictory decisions remain held until resolved. The initial pilot trusts the local operator/explicit Cam input path; this is not a claimed remote identity/signature service.
3. **`crop_review_release.json`:** deterministic coverage/missing/stale/conflicting/held counts; every expected candidate/source visual accounted for, hashes of proposals/decisions/source inventory and release result. Reviewer-unresolved source visuals or unavailable responses remain held; no release on partial inventory.
4. **`illustration_manifest.jsonl` plus `images/` in the new release-stage directory:** builder-compatible copies of explicitly approved current crop rows/bytes, emitted **only when the complete pilot source inventory is resolved**. Rejected/pending candidates and original source bytes stay in immutable upstream custody. The build recipe consumes this new stage, never the raw cropping stage in the opt-in pilot.

| Reviewer action | Meaning and release effect |
|---|---|
| `approve_current_crop` | Reviewer source-inspected this exact bound crop and explicitly accepts it. May agree with pass or override a false model fail. Counts toward complete release inventory. |
| `require_recrop` | Current crop is not accepted. Keep source/candidate, hold publication, record concrete boundary/text/completeness issue. A corrected crop becomes a new bound candidate requiring a new decision; old approval cannot transfer. |
| `unresolved_ownership` | Evidence cannot establish a supported boundary. Preserve artifacts and hold publication pending source/context review. No automatic deletion, omission or retries. |
| Missing, stale, unauthorized or conflicting decision | Same fail-closed hold. Never default to accept and never drop the source illustration to make the build succeed. |

The gate must exit nonzero before builder execution when anything remains held. Do not emit an empty “approved” manifest and let the builder treat it as success. Existing source originals are never pruned by this decision step. Resume verifies all bindings again and invalidates downstream build outputs through the existing driver mechanism; avoid `--keep-downstream` stale publication. A separate explicit user decision would be needed for intentional source omission; this pilot defines none.

## Concrete implementation slice to propose next — not performed here

Prepare an owner story before code. The immediately approvable slice is **offline only: review recording, deterministic release enforcement and replayed-fixture driver proof, zero API spend**. Proposed files are NEW unless identified as existing; they are a finite plan, not proof they exist:

- `tools/review_crop_candidates.py`: local source/crop review display and explicit operator-event recording, with trusted direct-human authority/delegation evidence. This creates a review tool; none is claimed present now.
- `modules/transform/release_reviewed_crops_v1/{main.py,module.yaml}`: deterministic fail-closed gate, sidecar validation, inventory reconciliation and builder-compatible approved copies. Keep model JSON schema unchanged; new review sidecar contracts require their own validation, not silent fields on current model outputs.
- Existing `modules/build/build_chapter_html_v1/{main.py,module.yaml}` would gain an **opt-in** required-review flag/release-receipt input, checked before image copying or HTML writing. Under that flag, direct builder invocation with a raw manifest, missing receipt or mismatched hashes fails closed. Merely adding a recipe dependency would not prevent this bypass. Existing unopted recipes keep their current behavior.
- `configs/recipes/story-<allocated-id>-reviewed-crop-offline.yaml`: isolated fixture/loader recipe with saved proposals, source/crop inventory, decisions, release gate and opted-in builder. No live detector or classifier is invoked. Maintained recipe/defaults remain intact; allocate storyID normally rather than inventing it here.
- `tests/test_crop_review_release.py` and `tests/test_reviewed_crop_driver_contract.py`: missing/stale/duplicate/conflicting/unresolved/unauthorized reviews, model-pass and model-fail bypass attempts, manifest/source-inventory coverage and recrop invalidation. Real offline partial-driver proof must show a held gate prevents chapter/asset publication; direct opted-in builder bypass is denied; approved exact bytes reach HTML.
- `docs/runbooks/crop-safety-review.md`: operator actions/custody/recrop/resume and rollback. Registry/source-golden adoption, if requested, is a separate source-reviewed decision; this plan does not adopt the two campaign corrections canonically.

An offline first implementation proof can reuse **saved** S3pass and known valid/invalid native outputs plus synthetic source/crops, with zero model calls. Use a fixture/loader recipe to enter after extraction and run actual release→build stages. Inspect `output/runs/<pilot-run>/` HTML/images/provenance and verify no asset is published before a valid decision. This proves deterministic routing, not live Sol classification or real-document detector completeness. A later live public-data pilot requires a separately reviewed `modules/validate/propose_crop_safety_v1/` and runtime page-context support in existing `modules/common/openai_crop_vision.py`; neither exists as a maintained safety stage. Its live recipe, explicit bounded call plan, spend reconciliation and native runtime parity qualification are deferred beyond the immediate offline slice. Benchmark import is not production plumbing.

## Later live qualification — fixtures still unbuilt, freeze before inference

Prepare24 genuinely fresh source/crop pairs before any future inference:18 physically determinate (9pass/9fail) and6 reviewer-unresolved ownership cases. Twelve pairs come from independently source-reviewed public scans and twelve from deterministic diagrams; never describe them as already built or measured. Use one separate parent source per pair and freeze allowed crop interpretations before outputs. Keep these out of calibration and preserve source/crop/coordinate/model/prompt/schema hashes and privacy provenance. Existing22 scans andS1–S6 stay exposed diagnostics, not held-out validation.

For each source type, the9 determinate pairs comprise5pass/4fail on scans and4pass/5fail on diagrams: legitimate unified multi-object photograph, source-unified multipart/panels, integral writing/badge text, acceptable tight/minor-edge framing, and a caption-free single visual across the two sets; invalid independent-neighbor inclusion (with and without leaked captions), external text, obvious substantial missing visual and excessive blank. Choose distinct parents so agreement does not recycle one boundary. The remaining3 scans+3 diagrams are pre-reviewed cases where the available source supports multiple plausible groupings/boundaries or cannot resolve an occluded/degraded boundary; lack of caption or multiple parts alone is **not** the ambiguity label. Independent source reviewers must document unresolved evidence and permissible interpretations before freeze. Withdraw genuinely label-disputed determinate fixtures before calls; never tune after outputs.

Report three layers separately:

- **Physical classification:**18 determinate case scores, false-safe and false-reject counts, source-backed reasons, valid native completion/usage and unavailable calls. Zero source-confirmed false-safe and zero false-reject is the classifier gate; reasons cannot rely on incidental marks or hidden authorship intent.
- **Review policy enforcement:**24/24 proposals enter review regardless of verdict; zero unreviewed/stale/unauthorized crop releases; valid human decisions bind exact source/crop/geometry and source inventory. Ambiguous6 are reported separately, with no physical-failure denominator. Measure hold/decision/recrop rates and operator workload rather than treating ambiguous fail-label agreement as model insight.
- **Published fidelity:** actual driver/build output contains only approved exact crop bytes, every source visual accounted for, no source deletion/silent omission, and changed geometry/hash or unresolved review blocks downstream publication. Manual original/crop/finalHTML inspection is mandatory for future behavior completion.

**Immediate offline acceptance:** replay saved S3pass plus source-valid pass/fail proposals; verify every candidate (including a false model fail) stays pending without a human decision; missing/stale/duplicate/conflicting/unresolved decisions, raw-manifest bypass and incomplete source inventory cannot publish chapters/assets; accepted exact bytes and provenance survive real fixture-driver release→build; originals remain intact after rejection and recrop; no provider invocation.

**Acceptance gates before a later live opt-in pilot:** deterministic gate/tests and real offline driver artifact proof pass; all24 fixtures source-reviewed and frozen; runtime native/parity/spend plan separately approved; explicit human reviewer available and willing to review every candidate/source page. **Acceptance before autonomous promotion:** representative source coverage/C5 requirements plus a separately proved independent ambiguity-routing boundary; manual pilot success alone cannot authorize automatic review bypass or a default switch. Keep Sol's measured physical lead, while naming the unresolved policy/production proof honestly.

## Validation of this preparation

Source paths/functions and pilot wiring above were inspected locally; this is a policy plan only. No implementation, fixture generation, provider call, current schema/prompt/recipe/default change, canonical-golden adoption or driver behavior test occurred in this preparation. Story240 remains Done for its completed evaluation. The next reviewable action is the bounded offline review-gate implementation slice; any later live pilot/promotion is a separate decision.

Source identity at preparation (SHA256):

- `modules/extract/crop_illustrations_guided_v1/main.py`: `d5235ecfbc639e8850c4d227be1c01201ac49f886eba3dcd7d637de2f24b4dac`
- `modules/extract/crop_illustrations_guided_v1/module.yaml`: `22fdc7a8995807d0bc72e0244bd03774e14da216cdc29d796e8b5939fc16f1c0`
- `configs/recipes/recipe-onward-images-html-mvp.yaml`: `3d1acbc9e73d8fb7c5fc18e1301fe100fed8d17299833ca9a99a377c938e653a`
- `modules/build/build_chapter_html_v1/main.py`: `052eb74a1ba4422ca157c4ccc4be5da5dba6842b87ddfefc2931a2d3572bae58`
- `driver.py`: `86847f8c1a8be9a3b82fda011338191d39acbaada1493348cd13bd4562a95e72`
- `modules/common/run_registry.py`: `ce020078681870a0cfaa6b505ba7e586ce4865ce5b7fa7d1dc69eaa1da22088f`
- `tools/run_registry.py`: `be3eee603d6b28f9a80c4f53d40205e16a28b78c6a59cc40807529908f88855a`
- `schemas.py`: `836c64bdc88171d33fad740304c683169c47ccaececf70b4fb0c4ea95578703a`
- `validate_artifact.py`: `2a1760ece93f0dc5d418e40e7ebe756653c6532e8ce3b65a467e886d19838955`
- `docs/spec.md`: `30b2d307f999a742e9c5ded76fc3d72eb2dfdbafc114a20ae1db2ba591b97a74`
