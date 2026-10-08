# Offline native manual source-fidelity replay

Use this opt-in path when a retained manual build has suppressed source catalog
illustrations or has existing crops that were not placed in a table. It does not
rerun OCR, alter planner decisions, or infer missing artwork. Preserve the parent
run and first verify its source identities and scoped reuse status. A separately
supplied immutable fixture may instead carry an explicit source/hash receipt.

The recovery stage needs the original PDF, full physical-page raster manifest,
logical page HTML with source-image/physical-page/split identity, and the existing
illustration manifest plus its sibling `images/` directory. It accepts a complete
page or an exact declared left/right slice with uniform PDF-to-raster scale.
Rotated PDF pages and nontrivial PDF crop boxes hold for review. Rotated embedded
artwork retains its printed orientation because crops use the rendered pixels.

Create a recipe with these stages, replacing each `/absolute/...` path:

```yaml
input:
  pdf: /absolute/source.pdf
stages:
  - id: physical
    stage: extract
    module: load_artifact_v1
    out: physical.jsonl
    params:
      path: /absolute/physical/pages_images_manifest.jsonl
      out: physical.jsonl
  - id: pages
    stage: extract
    module: load_artifact_v1
    out: pages.jsonl
    params:
      path: /absolute/normalized/pages_manual_normalized.jsonl
      out: pages.jsonl
  - id: portions
    stage: extract
    module: load_artifact_v1
    out: portions.jsonl
    params:
      path: /absolute/portions/portions_headings.jsonl
      out: portions.jsonl
  - id: recover
    stage: transform
    module: recover_native_graphics_v1
    needs: [physical, pages]
    inputs:
      physical_pages: physical
      pages: pages
    out: illustration_manifest.jsonl
    params:
      pdf: /absolute/source.pdf
      existing_crops: /absolute/crops/illustration_manifest.jsonl
      inclusion_policy: source-associated-catalog-illustrations-v1
  - id: build
    stage: build
    module: build_chapter_html_v1
    needs: [pages, portions, recover]
    inputs:
      pages: pages
      portions: portions
      illustration_manifest: recover
    out: chapters_manifest.jsonl
    params:
      book_title: Manual
      images_subdir: images
      resolve_references: true
```

Run in a fresh output directory:

```bash
python driver.py --recipe /absolute/replay.yaml --run-id unique-offline-replay
```

The loaders only stamp the copied run envelope; source files stay untouched.
Recovery keeps original crop records (including protected planner rectangles)
and original encoded assets exact. `native_graphics_inventory.json` records the
explicit policy, accepted/retained/held associations, PDF/raster/crop hashes,
source occurrence geometry and exact decoded-pixel validation. Missing titles,
duplicate labels, uncertain neighbors, conflicting image coordinates and partial
overlap with a protected crop all hold. Unassociated native images are listed;
there is no untargeted image-detection, OCR or model fallback.

The builder places uniquely labelled table illustrations in the label cell and
adds independent crop provenance. It preserves transcribed text beside native
supplements. Existing legacy crops marked `contains_text` can still use the
builder's prior local OCR deduplication path; inspect those flags before calling
any arbitrary replay zero-inference. The Story 251 retained fixture has none,
and the new native supplements explicitly bypass that path. Match the parent's
other normalization/navigation parameters to avoid unrelated output changes.

Inspect the new `output/html/`, inventory, crop manifest, provenance blocks and
navigation report. Check every added occurrence against its source, all existing
figure occurrences/bytes, ordered nonfigure wording and provenance, and the
original fixture hashes. Ordinal output block IDs can change when figures are
added; compare the complete ordered source joins and preserve an old-to-new ID
map. TOC resolution requires the complete source title, source-row provenance
and uniquely supported heading/page evidence; observed labels have authority,
inferred labels do not. Correct source-ID links retain their own authority.

This is a bounded source-associated catalog policy, not universal illustration
recovery or a semantic importance classifier. Its held inventory is evidence for
review, not permission to silently relax the policy.

## Continue a completed standard imposed-manual run

For a completed `recipe-graphics-heavy-imposed-pdf-html-mvp.yaml` run with all
standard stages, use the append-only preparation helper. It reads the parent's
exact `snapshots/recipe.yaml` (including `stage_params`) and `snapshots/plan.json`;
it refuses missing/different stages, incomplete artifacts, graph drift, existing
destinations, or overlapping parent/clone directories before copying anything.
The destination's final directory name must equal the new run ID so the driver
uses that exact clone directory.

```bash
python scripts/prepare_native_manual_continuation.py \
  --parent-run /absolute/immutable/completed-run \
  --destination /absolute/output/runs/new-offline-continuation \
  --run-id new-offline-continuation
```

Preparation prints an exact `driver.py` command. Run that printed command from
this checkout when ready. It includes `--start-from source_fidelity_recover`,
`--allow-run-id-reuse`, the new run ID, and the clone's explicit `--output-dir`.
Preparation itself executes no pipeline stages or provider calls. The reusable
`configs/recipes/overlays/native-manual-source-fidelity.yaml` is an append-only
overlay consumed by the helper, not a standalone recipe.

The original stage graph remains an exact prefix with unchanged ordinals,
parameters and overrides. Recovery waits for the original `validate_manual_html`
and consumes existing physical rasters, normalized pages and retained crops.
Only new recovery, build and semantic-validation stages execute. The old crop,
OCR and planner stages are skipped by the driver's start gate. New validation
uses the original logical-page and figure-planner artifacts plus new crops and
chapters. The new bundle is `CLONE/output/source-fidelity/html/`; the original
`CLONE/output/html/` remains available for comparison. The appended builder enables
reference resolution and disables reference/catalog normalization to preserve
prepared source wording; the original builder parameters remain unchanged.

`native_manual_continuation.json` pins the canonical parent graph and recipe
hashes, exact snapshot hashes, all original file hashes, and each state artifact
path before/after rebasing. `continuation_parent/` archives the original snapshots
and state because the driver replaces active snapshots. Preparation changes only
the copied state's artifact paths; original stage records, paid timestamps, IDs,
JSONL bytes and embedded image paths are retained. **Keep the immutable parent
and its PDF available:** embedded source-image paths intentionally still point
there. Inspect the new inventory, bundle and conformance report using the checks
above before accepting the continuation.

Before claiming restored detail, compare native embedded dimensions and placement
transforms with the retained raster's PDF-to-pixel scale. Record per-axis sampling
for each relevant layer, rotation, clipping/containment and exported pixel hashes.
Do not rerender or upsample when the retained grid already covers native placed
image density. Report rendered-pixel fidelity separately from original encoded
streams/channels/vector data. Existing protected crop boundaries still prevail.


## Transport identity and positive recovery checks

When transporting a retained run, its recipe PDF path and physical raster
`source` records must resolve to the same included file. A separately copied,
byte-identical PDF at another path does not satisfy that identity contract.
Preserve the original packet; produce a separately hashed coherent transport
view when rebasing paths. Do not repair pipeline artifacts in place.

A completed overlay with zero recovered occurrences proves neither recovery nor
successful adoption. Inspect the inventory's held reasons, require the intended
positive restoration, and compare every original crop/asset, ordered text and
source provenance before accepting the derivative. Conformance may pass for a
correctly held no-op; it is a separate check from positive restoration evidence.
