# Related-document references

`resolve-set` is an opt-in, offline operation over **already converted, final
Doc-web bundles**. It groups only documents explicitly supplied by the caller,
links exact source-supported heading identifiers, and writes a new portable
set. It makes no model/network calls and never runs OCR. Ordinary conversions
and their document-local `--resolve-references` behavior are unchanged.

## Public interface

From a checkout with project requirements installed, or an installation made with
`pip install .[driver]`, create a UTF-8 JSON declaration:

```json
{
  "schema_version": "doc_web_related_set_declaration_v1",
  "set_id": "field-guides",
  "documents": [
    {"member_id": "guide", "bundle": "converted/guide", "edition": null},
    {"member_id": "reference", "bundle": "converted/reference", "edition": null}
  ]
}
```

```bash
python -m doc_web resolve-set --manifest related.json --out-dir linked-set --json
```

Python callers use
`doc_web.related_documents.resolve_document_set(manifest_path, out_dir)`.
The CLI returns a JSON summary and exit code 0 on successful publication; code 1
and a JSON error on invalid inputs. Unresolved references are reported data,
not a publication error. Malformed bundles, existing broken local resources,
unsafe paths, changing inputs and preservation failures prevent publication.

Bundle paths may be absolute or relative to the declaration file. `member_id`
uses lowercase ASCII letters/digits/underscore/hyphen, starts with a letter,
and is at most 64 characters. It is the **set namespace**, not a claim about the
source document's title or edition. Ordinary bundle `document_id`, entry IDs and
block IDs may overlap across different members. Duplicate member IDs, repeated
or overlapping roots, and byte-identical supplied bundles are rejected. The
output directory must not exist or overlap any input bundle.

The caller declares that these exact documents belong together. Doc-web does
not discover relationships from filenames, common folders, titles or labels.
Unlisted files outside the declared bundles never become reference targets.

## Evidence and supported references

Every member needs its ordinary `manifest.json`, listed entry HTML, index,
assets and `provenance/blocks.jsonl`. Each eligible target is a heading with a
unique DOM ID and exactly one corresponding `entry_id`/`block_id` provenance row,
`block_kind: heading`, nonempty `source_element_ids`, and full matching
`text_quote`. HTML entity spelling may differ while decoded text agrees.
The operation trusts the converter's source provenance; it does not independently
re-OCR or certify that the converter transcribed a source image correctly.

Supported heading forms include `x501b Supply checks`, `Section 4.2 Safety`,
`Equipment (x519)`, and `Equipment (x519):`. Identifier prefixes are unrestricted;
no document-specific dictionary exists. Matching follows the shared exact-label
case policy (prefixed and Roman labels case-insensitive). No fuzzy title match,
prefix stripping, parent-section fallback or invented subsection is used.

Within the explicitly declared set, **bare exact heading identifiers are
eligible**, as are citations such as `see x501b`, `(x501b)` and `section 4.2`.
This broad set policy is intentional and separate from local conversion defaults.
Explicit kinds must agree: a table citation cannot bind a chapter just because
its number agrees. An untyped prefixed heading may satisfy a section/paragraph
citation. All plausible matching headings participate in ambiguity checks,
including rejected candidates with missing/stale evidence; member order does
not break ties. Existing valid local links are kept, even when new matching
headings would make an unlinked occurrence ambiguous.

Source occurrences also need a unique source block/provenance join and a
matching quote. Full quotes support the entire block. A producer's exact
400-character truncated quote supports occurrences only inside that prefix;
later occurrences remain `insufficient_source_evidence`. Missing, stale or
ambiguous provenance remains inspectable. Previously generated unresolved spans
from the local resolver can be reconsidered without losing their text or IDs.

Code/preformatted/script/style/hidden/generated-navigation content, existing
anchors, and heading definitions are excluded. Explicit ranges, page references,
named/foreign-document qualifiers and literal edition mentions abstain; this
operation does not establish printed-page or prose scope across documents.
Unlinked code-shaped tokens without a target appear as missing in the report.
Unresolved text remains readable; no guessed anchor is added.

## Edition policy

`edition` is optional caller-supplied documentary evidence. Null means unknown,
not equivalent. Comparable known labels are normalized for whitespace/case;
more than one distinct known value holds every new cross-member link with
`edition_conflict`. Same-member unambiguous references may still resolve.
A literal edition/editions mention in a citation block holds its citations with
`textual_edition_scope`, because the current contract does not bind that prose
qualification. Existing anchors remain unchanged.

The declaration asserts relatedness of the supplied bytes; it does not certify
physical-copy equivalence. Doc-web neither extracts nor guesses missing edition
identity. Supply matching comparable labels only when supported, leave unknowns
null, and keep distinct incompatible editions out of a related set.

## Output and portability

```text
linked-set/
  related_documents.json
  related_reference_report.json
  guide/manifest.json
  guide/index.html
  guide/chapter-001.html
  guide/provenance/blocks.jsonl
  reference/...
```

Links use relative paths such as
`../reference/chapter-001.html#blk-chapter-001-0003`. Copy the **entire set** with
member directory names intact; no source checkout or absolute path is needed
for navigation. Do not move just one member after linking.

The member manifests and provenance bytes remain unchanged. Only entry HTML
with new links is serialized; visible body text, IDs, existing anchors and
assets are checked for preservation. Existing member navigation reports are
historical input records; `related_reference_report.json` is authoritative for
this derivative step. Re-seal any caller-owned checksum package after adopting
new output. Doc-web does not mutate caller seals.

`related_documents.json` (`doc_web_related_set_v1`) records declaration digest,
member identity/edition, input manifest/bundle digests, and every output file's
SHA-256 plus its input digest when applicable. It excludes itself from its own
hash inventory. The report (`doc_web_related_resolution_v1`) contains target
inventory, accepted/rejected evidence, each discovered occurrence's original
text/source block/raw-text offsets/provenance, candidates, chosen target or
reason for abstention, summary, zero calls/cost and final local-link validation.
These portable receipts use set-relative paths. Historical member metadata is
preserved verbatim and may contain nonportable audit-only source locations.

When the source manifest has a `files` inventory, only portable files marked
safe to persist **and** replay are copied; unsafe/private/debug/cache files are
excluded. Without that optional inventory, only the known legacy bundle surface is copied:
manifest/index/entries/provenance, files under declared asset roots, the existing
navigation report, and declared literal-fidelity reports. Unclassified extras
are excluded. Point the declaration at a final bundle directory, not an entire
run or working directory. Symlinks and nonregular files are rejected. Historical member metadata is not
privacy-sanitized; an old manifest can retain audit-only source filenames.
Generated hrefs and static local HTML/CSS/srcset dependencies are checked without
fetching or executing anything. Absolute file URIs and missing local assets are
refused. This is not a JavaScript execution or remote-resource availability check.

Repeat the same declaration into a fresh output directory for deterministic
results. Reprocessing a linked set is possible with the same member names;
existing links are preserved and a new report describes only the new operation.
Always retain the earlier receipt if its occurrence history matters.

## Offline verification and driver use

```bash
python driver.py --recipe configs/recipes/recipe-related-document-set.yaml \
  --run-id related-proof --output-dir output/runs
python validate_artifact.py --schema doc_web_related_set_v1 \
  --file output/runs/related-proof/02_resolve_document_set_v1/related-set/related_documents.json
```

The checked-in recipe uses synthetic converted bundles through `load_artifact_v1`
and `resolve_document_set_v1`. The loader copies one `bundles` sibling directory
so declaration-relative paths survive staging. The transform adapter uses the
same public Python function; its result artifact locates the portable set.
On driver resumption, earlier derivative directories are retained; the current
result artifact points to a fresh `related-set-<unique-id>` directory. The public
CLI itself always requires a fresh output directory. No paid stages are needed.
Real existing bundles can use the CLI directly.

Machine-readable schemas and discovery metadata are exposed by
`python -m doc_web contract --json` under `related_document_resolution` and by
`validate_artifact.py` for declaration/report/set/result schema names.

Limits: exact symbol forms only, final supported bundle/provenance contracts,
no OCR repair, no assertion of universal source accuracy or physical edition
identity, and no cross-set fetching. Missing heading evidence cannot be repaired
merely by declaring documents related; recover applicable existing provenance
or perform a separately authorized upstream conversion/review.
