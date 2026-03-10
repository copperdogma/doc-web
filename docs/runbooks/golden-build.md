# Golden Build Runbook

Operational guide for creating and maintaining golden reference files for evals.

## Golden File Locations

| Eval | Golden Path | Format |
|------|-------------|--------|
| Image crop extraction | `benchmarks/golden/` | JSON bounding boxes per page |

## Creating a New Golden

1. **Run the pipeline** on representative input pages.
2. **Manually verify** each output against the source material.
3. **Save as golden** in the appropriate directory with clear naming.
4. **Register the eval** in `docs/evals/registry.yaml` with target metrics.

## Eval-Driven Golden Improvement

When `/verify-eval` identifies golden-wrong mismatches:

1. **Review the mismatch table** — each item classified as golden-wrong needs fixing.
2. **Apply fixes**:
   - For < 5 changes: edit golden files directly
   - For > 5 changes: write a batch Python script for consistency
3. **Validate** that golden fixture tests still pass.
4. **Re-run the eval** to get verified scores.
5. **Document the delta** in the story work log.

## Quality Standards

- Every golden entry must be manually verified against source material
- Golden files should cover diverse cases (simple pages, multi-illustration, tables, edge cases)
- When adding new test cases, include at least one "tricky" case per category
- Golden changes that affect > 5% of test cases require user approval

## Pitfalls

- **Don't assume golden is always right** — models sometimes find real issues the golden missed
- **Version golden with the code** — golden files are tracked in git, not generated
- **Document golden conventions** — what counts as an illustration vs. decoration, how to handle partial crops, etc.
