# Benchmark Input Fixtures

This directory holds tracked promptfoo image fixtures for the maintained crop
benchmark surfaces.

- `source-pages-b64/` contains the 13 downscaled page fixtures used by the
  crop detector benchmarks.
- `crop-validation-b64/` contains the 40 downscaled crop fixtures used by the
  dedicated crop text-exclusion / crop-quality validation surface.

These files are stored as `data:image/jpeg;base64,...` text payloads on
purpose. Promptfoo's `file://` loader is safe for text fixtures like these, but
it is not a safe substitute for raw binary JPEG interpolation in the
multi-provider vision prompts used here.

If you widen or replace these fixtures:

1. Keep the checked-in goldens in sync.
2. Update `tests/test_crop_benchmark_substrate.py`.
3. Record the new measured result in `docs/evals/registry.yaml`.
