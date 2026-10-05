# Optional reference resolution

Final HTML builders always inspect existing local links. Enable new links from
plain text only when useful for the caller:

```bash
python driver.py \
  --recipe configs/recipes/recipe-reference-resolution-smoke.yaml \
  --run-id references-on \
  --resolve-references
```

For a recipe, set `resolve_references: true` in the final emitter's `params`.
The corresponding module invocation accepts `--resolve-references`. The default
is false. Non-final preview does not expose this option. A recipe with no
supported final emitter must reject the driver flag instead of ignoring it.

The pass runs after structure and stable block IDs exist. It adds links for
supported explicit page/section/chapter/paragraph/figure/table/footnote labels,
HTTP(S) URLs, tables of contents and index entries. It preserves the exact
displayed wording and inline markup. Repeated, missing or unsupported references
remain visible and are reported. Broad semantic references such as “the paragraph
above” do not authorize a guessed link.

Printed page numbers are not PDF page indexes. Only explicit observed labels
authorize printed-page destinations. Inferred numbering, missing labels and
undifferentiated spreads remain unresolved. Report evidence keeps the available
logical page, original scan page and spread-side information separate.

Inspect:

- `output/runs/references-on/output/html/navigation_resolution_report.json`
  for policy, reference decisions, evidence and aggregate metrics.
- `output/runs/references-on/output/html/provenance/blocks.jsonl`
  for unchanged block/source mapping.
- Final chapter/page HTML to check actual destinations and retained wording.

Repeat the same recipe under a fresh run ID without `--resolve-references` to
compare opt-out behavior. Existing-link validation/repair is separate from
plain-text enrichment. The resolver performs zero provider/network calls;
reported zero cost covers this pass only, not upstream OCR or agent work.

Consumers should validate packaged file/fragment destinations independently
after copying/rebasing a bundle. They should also check source-supported target
semantics and unresolved reports: a reachable target alone is not proof that the
link points to the right section. External URL availability is not tested.

See [design and evidence policy](../notes/reference-resolution-design.md) and
[Story 243](../stories/story-243-optional-source-grounded-reference-resolution.md)
for the supported scope, benchmark boundaries and remaining uncertainty.
