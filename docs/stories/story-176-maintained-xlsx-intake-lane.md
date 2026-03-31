# Story 176 — Establish a Maintained XLSX Intake Lane

**Priority**: High
**Status**: Draft
**Ideal Refs**: Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Any format, any condition, Traceability is the product
**Spec Refs**: spec:1, spec:6, spec:7
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 6 Validation, Provenance & Export (`exists`); Input Coverage row `xlsx` (`untested`); Gap 3 — Office document intake beyond the widened DOCX slice
**Depends On**: Story 175

## Goal

Turn the currently observed local spreadsheet seam into the first honest maintained `xlsx` lane for `doc-web`, starting with table-oriented workbooks and preserving reviewable provenance rather than inventing slide or document metaphors that do not fit spreadsheets.

## Acceptance Criteria

- [ ] A repo-owned or reproducibly generated `xlsx` fixture exists under `testdata/`
- [ ] The story measures the real local spreadsheet seams before choosing the maintained path
- [ ] A maintained explicit `xlsx` recipe runs through `driver.py` on the supported slice and leaves inspectable final bundle/provenance artifacts
- [ ] Truth surfaces move `xlsx` only as far as the fresh evidence earns

## Notes

- Story 175 verified that `openpyxl` and `unstructured.partition.xlsx` are importable in the current checkout and that a minimal workbook probe emits a `Table` element with `text_as_html`.
- Start with table-centric workbook intake. Do not assume charts, formulas, comments, or multi-sheet semantic reconstruction are in scope for the first maintained slice.

## Work Log

20260331-0000 — draft created from Story 175 sequencing decision: split `xlsx` from `pptx` because the spreadsheet seam is locally real today while the slide seam is blocked earlier by missing runtime substrate. Next step: triage/build this story separately when office-family work rises again.
