# Scout 015 — photon-image-processing

**Source:** `https://github.com/silvia-odwyer/photon`
**Scouted:** 2026-05-25
**Scope:** Evaluate whether `silvia-odwyer/photon` should replace any current
doc-forge image-processing tools in the scanned/image intake, OCR handoff, and
illustration-crop lanes.
**Previous:** None
**Status:** Complete

## Summary

Photon is a healthy Rust/WebAssembly image-manipulation library, but it is not a
good replacement for any current doc-forge image-processing dependency. It is
best treated as a parked reference for a future browser-side crop/preview UI or
for a narrow CPU-bound Rust benchmark if pixel transforms become a measured
bottleneck.

## Findings

1. **Do not replace `Pillow` with Photon in the Python pipeline** — LOW value, story-sized if attempted
   What: Photon provides Rust-native and WASM image loading, saving, crop,
   resize, rotate, filters, channel operations, thresholding, and convolution
   helpers. It wraps the Rust `image` / `imageproc` ecosystem and exposes
   `PhotonImage` as raw RGBA pixels.
   Us: Current pipeline modules are Python-first and already use `Pillow` as
   glue for page-image manifests, source crops, base64 VLM payloads, Tesseract
   OCR calls, and artifact writes. `Pillow` also fits the existing `pyproject`
   and `requirements.txt` boundary; Photon has no Python binding in the source
   tree reviewed here.
   Recommendation: Skip. A replacement would add Rust/WASM/Node subprocess or
   FFI ownership without removing the OCR/VLM/provenance work that actually
   dominates the pipeline.

2. **Do not replace `OpenCV` crop/runtime heuristics with Photon** — LOW value, story-sized if attempted
   What: Photon includes thresholding, line-detection convolutions, color-space
   transforms, and simple crop/resize/rotate operations.
   Us: The maintained crop runtime uses `cv2` for morphology, connected
   components, contours, Canny edges, HSV masks, dilation/closing/opening, and
   document-specific geometry cleanup around VLM detector boxes. Photon does
   not provide a drop-in equivalent for that OpenCV-shaped surface, and it does
   not know about the repo's `image_crop_v1` / `page_image_v1` artifact
   contracts.
   Recommendation: Skip. If the OpenCV dependency is a packaging problem, solve
   that directly; Photon would not simplify the current crop code.

3. **Do not replace PDF/page extraction or OCR tools with Photon** — LOW value
   What: Photon supports common raster image formats and pixel transforms.
   Us: `extract_pdf_images_fast_v1` owns PDF XObject extraction, DPI/source
   metadata, and `pdf2image` fallback rendering; `modules/common/ocr.py` owns
   Tesseract handoff and confidence data. Photon has no PDF extraction, OCR,
   Tesseract confidence, or page-provenance model.
   Recommendation: Skip.

4. **Park Photon as a possible browser-side preview/edit dependency** — MEDIUM value later, story-sized only when a UI exists
   What: Photon's strongest differentiator is cross-platform Rust/WASM use,
   especially browser or Node-side manipulation at near-native speed.
   Us: doc-forge currently runs the image pipeline server-side through
   `driver.py`; there is no active browser crop-editor surface in this checkout.
   A future operator UI could use Photon for non-authoritative preview actions
   like rotate, crop, resize, threshold, or visual comparison without round
   trips.
   Recommendation: Defer. Create a story only if an operator crop-review UI
   becomes active or if browser-local image transforms become a real workflow
   requirement.
   Transfusion:
   Exemplar: Photon exposes the same image operations natively and as WASM.
   Invariant: Browser previews must stay non-authoritative unless the final
   crop/provenance artifact is regenerated through the pipeline.
   Adaptation: Use Photon only on the UI side; keep `driver.py` as the source
   of truth for emitted artifacts.
   Proof target: A future UI story can rotate/crop/threshold a page image
   client-side, then regenerate the accepted `image_crop_v1` artifact through
   the normal pipeline path.

5. **Benchmark only if pixel operations become a measured bottleneck** — LOW value now, story-sized later
   What: Photon has performance work and benchmark scaffolding, including a
   recent upstream memory-copy optimization merge.
   Us: The active doc-forge cost and quality constraints are OCR/VLM calls,
   crop correctness, provenance, and artifact inspection. No current evidence
   says Python pixel transforms are the bottleneck.
   Recommendation: Skip now. If profiling later shows crop/resize/mask CPU time
   is material, benchmark a Rust-native helper against the exact
   `crop_illustrations_guided_v1` hot path before choosing Photon or a smaller
   custom Rust tool.

## Approved

- None. Research-only scout; no implementation was approved or recommended.

## Skipped / Rejected

- Replacing `Pillow` — rejected because current use is Python glue plus OCR/VLM
  artifact handling, not just pixel effects.
- Replacing `OpenCV` crop heuristics — rejected because current code uses
  morphology, contours, connected components, HSV/Canny masks, and geometry
  logic that Photon does not replace.
- Replacing `pdf2image`, `pypdf`, or Tesseract handoff — rejected because Photon
  does not own PDF extraction, page rendering, OCR, confidence data, or
  provenance.
- Creating a story now — rejected because there is no measured bottleneck or
  active browser image-editing surface.

## Verification

- Read current methodology context: `docs/methodology/state.yaml`, `docs/spec.md`
  `spec:4`, `tests/fixtures/formats/_coverage-matrix.json`, and
  `docs/scout/scout-011-external-document-ingestion-systems.md`.
- Inspected current local image-processing surfaces:
  `pyproject.toml`, `requirements.txt`, `modules/common/image_utils.py`,
  `modules/common/ocr.py`, `modules/extract/images_dir_to_manifest_v1/main.py`,
  `modules/extract/extract_pdf_images_fast_v1/main.py`, and
  `modules/extract/crop_illustrations_guided_v1/main.py`.
- Reviewed upstream Photon primary sources:
  GitHub README and repository metadata, docs.rs `photon-rs 0.3.3`, crates.io API
  metadata, npm registry metadata for `@silvia-odwyer/photon` and
  `@silvia-odwyer/photon-node`, plus a shallow clone of commit
  `c093eea4fed2edf2ba163e87d4c7c874808c7a27`.
- No code changes, benchmarks, or `driver.py` runs were executed because the
  recommendation is no adoption.

## Evidence

- Upstream Photon snapshot:
  - GitHub head: `c093eea4fed2edf2ba163e87d4c7c874808c7a27`, committed
    2026-05-14, "Merge pull request #219 from herosql/perf/optimize-memory-copies".
  - Latest crates.io version from API: `photon-rs 0.3.3`, updated
    2025-05-10, `77574` total downloads and `9523` recent downloads at scout time.
  - Latest npm registry versions at scout time: `@silvia-odwyer/photon 0.3.3`
    and `@silvia-odwyer/photon-node 0.3.4`, both published 2025-05-10.
- Photon fit evidence:
  - `crate/Cargo.toml` declares Rust/WASM library output (`cdylib`, `rlib`) and
    dependencies on `image`, `imageproc`, `wasm-bindgen`, `web-sys`, and
    `node-sys`.
  - `crate/src/native.rs` exposes filesystem image open/save helpers returning
    `PhotonImage` raw RGBA pixels.
  - `crate/src/transform.rs`, `crate/src/monochrome.rs`, and `crate/src/conv.rs`
    cover crop/resize/rotate/threshold/convolution operations, not document
    OCR or provenance.
- Local fit evidence:
  - `pyproject.toml` keeps `Pillow`, `pypdf`, and `pytesseract` in the Python
    package boundary; `requirements.txt` includes `pdf2image`.
  - `modules/extract/crop_illustrations_guided_v1/main.py` uses `cv2` for
    morphology, contours, connected components, HSV/Canny masks, and crop
    refinement around VLM results.
  - `docs/spec.md` `spec:4` says the active compromise is not generic image
    transforms; it is caption-aware VLM crop detection plus layout-text trim
    until the maintained truth surface supports deletion.
