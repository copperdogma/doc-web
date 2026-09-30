# Offline all-candidate crop review

This is a **new opt-in publication gate**, not an existing runtime safety classifier replacement. All pass and fail proposals need explicit source review; absence of approval holds publication. Rejection applies to the current crop, never authorizes source deletion. Detector, caption helpers, C5 and standard recipes remain unchanged. There is no live model adapter or API spend in this slice.

The authority file is a trusted local operator assertion, not secure external authentication. Keep its `operators` and `decision_log` designation under operator control. Never let model outputs supply authority or human-input evidence. An operator explicitly asserts complete source page and visual inventory, including missed detections; candidate enumeration alone cannot establish completeness. Hashes establish identity rather than authenticating a person. The JSON/JSONL contract is implemented in `modules/common/crop_review.py`; release rejects any uncovered candidate, missing source page, unauthorized or stale event.

The source display tool embeds full-resolution source/crop bytes, native dimensions and a red source-pixel bbox, plus proposal and decision history:

```sh
PYTHONPATH=. python tools/crop_review.py show \
  --custody-root tests/fixtures/crop_review_offline/approved \
  --manifest tests/fixtures/crop_review_offline/approved/manifest.jsonl \
  --run-id story241-crop-review-approved --html-out /tmp/new-crop-source-review.html
```

Review boundaries, captions, completeness and intended grouping. Lack of captions or multiple components alone does not establish ambiguity. S3's grouping is plausible; its saved pass is a proposal, not a physically wrong crop. S4's integral lettering is allowed; its false-fail proposal is explicitly synthetic. **Every approval in these fixtures is synthetic; none represents Cam source approval.**

For a real local review, supply an explicit authority file, complete inventory, bound proposal receipts and an initially empty designated `decisions.jsonl`. Run `show`, then create a human-authored JSON file with `candidate_id`, authorized `operator_id`, `action` (`approve_current_crop`, `require_recrop`, or `unresolved_ownership`), and a source-grounded `reason`. Record it with:

```sh
PYTHONPATH=. python tools/crop_review.py record --custody-root CUSTODY \
  --manifest CUSTODY/manifest.jsonl --authority CUSTODY/authority.json \
  --decisions CUSTODY/decisions.jsonl --human-input CUSTODY/human-input.json \
  --run-id RUN
```

To supersede an event for the **same exact candidate**, provide new human input and `--supersedes PREVIOUS_DECISION_ID`. Conflicting/duplicate events without an explicit chain hold release. Geometry, row, source/crop bytes or run changes require a new active custody bundle and newly bound inventory/proposal/review; retain the old bundle and its events. The executable recrop regression demonstrates old approval rejection, a newly reviewed geometry binding, successful release and unchanged old originals.

Release consumes the five contract files (`manifest`, `inventory`, `proposals`, `decisions`, `authority`) under a custody root. It copies only a completely approved inventory to a new or empty stage and emits a bound receipt. A held CLI run emits only `crop_review_held.json` with reason and counts, never approved manifest/images. Builder opts in via `--require-crop-review --crop-review-release RECEIPT`; supplying a receipt also activates enforcement. It rehashes original contracts/source/crops and exact reviewed pages/portions, checks release copies and destination aliases, stages output, requires every approved image exactly once and rechecks custody before publication. A stale/missing receipt or lost approved visual fails before final publication. Metadata must be outside HTML, destinations disjoint, and image subdirectory a safe relative path.

The exact deterministic driver proof is:

```sh
PYTHONPATH=. python driver.py \
  --recipe configs/recipes/story-241-reviewed-crop-offline.yaml \
  --run-id story241-crop-review-approved \
  --output-dir output/runs/story241-crop-review-approved
```

Use a fresh destination; this fixture recipe deliberately binds that exact run ID and receipt path. Its `.ndjson` loaders preserve reviewed bytes, avoiding the standard loader's JSONL timestamp stamping; no loader behavior changed. A successful proof already exists locally. Do not overwrite historical proof directories to rerun. Prepare a separate custody/run/recipe if another proof is needed. `tools/prepare_crop_review_fixture.py` only creates synthetic mechanics fixtures; it is not a production source inventory tool.

Focused checks: `PYTHONPATH=. pytest -q tests/test_crop_review.py tests/test_crop_review_tool.py tests/test_build_chapter_html.py`, selected Ruff, graph validation and `git diff --check`. These qualify offline custody/enforcement, not model correctness or external human authentication. A separately proposed live Sol pilot and source-reviewed determinate/ambiguous heldout qualification remain future work; automatic promotion remains deferred.
