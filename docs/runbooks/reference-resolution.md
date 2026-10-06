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

## Explicit identifier and document scope grammar

Existing links may use complete source-authored prefixed heading identifiers
such as Q42 or APP7. Identity comparison folds identifier case, retains prefixes,
and requires unique evidence; stripped numeric or dotted partial matches do not
authorize links. Optional prose discovery additionally requires navigational
cues (see/read/consult/refer/turn/return/go to), parenthesized/bracketed citations,
or a source-authored contents/index context. Arbitrary code-like prose is not
converted just because a similar heading exists.

Spelled-out kinds require whitespace: `note D` is explicit; `noted` is prose.
Compact symbol/dotted abbreviation forms such as `§3`, `¶9`, `p.12`, `fig.2`
remain supported. Concatenated spelled-out forms such as `noteD` are excluded.

Explicit attached foreign-document qualifiers, before or after a citation,
prevent local binding and emit `external_document_scope`. This applies to
existing chapter links as well as optional discovery. Complete foreign document
resolution still requires a separately identified document and is not provided
by this single-document pass. Actual external URLs and included resources retain
their existing URI/media checks. Named-title inference, pronouns and broad
natural-language coreference remain unsupported; these controls do not claim
universal document-scope comprehension.

An explicit document-source qualifier such as “According to the installation
guide, see section3” cannot establish that the named guide is this supplied
document. It stays visible with `unestablished_document_scope`; explicit
foreign modifiers use `external_document_scope`. Demonstratives naming this,
current or present document preserve local eligibility. Ownership words alone
do not identify a document.

A single navigation cue may cover directly coordinated complete identifiers
(“See Q42 and APP7”), with each target independently source-supported. Compact
condition/outcome mappings (“1,2-Q42;3-APP7”) remain outside this citation
grammar and are not evidence of complete reference recall.
