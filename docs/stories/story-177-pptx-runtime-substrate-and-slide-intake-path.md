# Story 177 — Restore PPTX Runtime Substrate and Choose a Maintained Slide Intake Path

**Priority**: Medium
**Status**: Draft
**Ideal Refs**: Requirement #1 (Ingest), Requirement #4 (Illustrations), Requirement #5 (Structure), Requirement #6 (Validate), Any format, any condition, Traceability is the product
**Spec Refs**: spec:1, spec:4, spec:6, spec:7
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 4 Visual Content & Crops (`partial`, C4 `climb`); Category 6 Validation, Provenance & Export (`exists`); Input Coverage row `pptx` (`untested`); Gap 3 — Office document intake beyond the widened DOCX slice
**Depends On**: Story 175

## Goal

Restore or replace the missing local slide-parser substrate for `pptx`, then measure whether a maintained slide-intake path is realistic in this checkout before promising any PowerPoint support at the `doc-web` boundary.

## Acceptance Criteria

- [ ] The story documents the real local `pptx` substrate options and their runtime/dependency status
- [ ] If a viable local seam exists, the story measures it on a reproducible slide fixture before choosing a maintained path
- [ ] If no viable seam exists, the story leaves an explicit blocker instead of implying pending support
- [ ] Truth surfaces reflect the measured `pptx` reality honestly

## Notes

- Story 175 verified that `python-pptx` is missing in the current checkout and that `unstructured.partition.pptx` currently fails with `ModuleNotFoundError: No module named 'pptx'`.
- This is a substrate-and-benchmark story first, not a promise that maintained `pptx` support is one patch away.

## Work Log

20260331-0000 — draft created from Story 175 sequencing decision: keep `pptx` separate from `xlsx` because the current blocker is earlier and different in kind. Next step: restore or replace the slide runtime seam before planning a maintained bundle path.
