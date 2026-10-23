# Fresh manual source fidelity — Story 251

## Scope and source baseline

Work is confined to Doc-web and the self-contained fixture
`/tmp/doc-web-fresh-manual-review-20261008/`. Its retained conversion is immutable
paid OCR/planner evidence, not globally certified output. The initial receipt at
`output/story251-inspection/fixture-input-receipt.json` hashes all 303 files
(455,792,284 bytes), including the original PDF, page pixels, model responses,
planner manifests, crops, normalized pages and published HTML. The separate
`fresh-manual-source-fidelity/doc-web` worktree starts at
`2f0df93e4f0012e8a0eb031977ab273dc0318e48`. The prior runtime is not edited.

## Personal source/output inspection before repair

Logical page 25 visibly contains six small card faces next to transcribed
headings and descriptions. Its retained planner declares no targets. Page 26
retains an enlarged Brakes illustration, but suppresses the six small references.
Page 28 has eight correct source-pixel PNG crops but its final textual table
contains no figures. Page 29 contains eight source cards whose OCR placeholders
are lost after the empty target plan. Neighboring pages 27 and 30 each retain
eight figures and are preservation controls. Root opened source pages 25 and 28
and the initial chapter 010 in the browser before repairs. The graphics worker
also inspected pages 26 and 29 and native occurrence geometry.

The page 2 TOC contains complete titles in one cell and destination numbers in
the adjacent cell. All 16 links are unresolved or ambiguous because resolution
ignores the title cell. The source Australian URL on page 32 ends at a hard line
break; the old discovery stream drops that break, includes the next word `New`
in the URL and anchor, and thereby invents a destination suffix.

Generic failure classes: a semantic suppression decision erases source visual
occurrences; figure placement does not support table labels; text-stream
segmentation loses authored boundaries; numeric reference resolution loses
source-row context. Repairs must preserve both images and transcribed wording.

## Bounded research and chosen approach

PyMuPDF's [image occurrence API](https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_image_info)
reports placements and transforms, including inline images. Its
[transformation documentation](https://pymupdf.readthedocs.io/en/latest/app3.html#image-transformation-matrix)
explains the geometry, and its
[image recipes](https://pymupdf.readthedocs.io/en/latest/recipes-images.html)
distinguish embedded-image extraction from rendering the complete page.

Use occurrence geometry to locate artwork, then crop retained rendered pixels.
Do not substitute extracted image objects: a printed card can comprise nested
artwork, background and shadow layers. The local test proved exact RGB equality
between the declared split pages and their physical-page raster slices. Native
PDF titles and immediately-left image groups support the 20 missing crops.
Eight page-28 crops already match their source raster rectangles exactly.

This is deterministic identity/geometry and execution over retained model
outputs. Another VLM could reconsider importance; a decision model could rank
associations. Neither is authorized or needed for this offline source-pixel
boundary, and spatial confidence is not semantic truth. The explicit opt-in
`source-associated-catalog-illustrations-v1` policy is recorded in the generated
inventory. Missing, duplicate, ambiguous, unregistered or partially overlapping
candidates hold rather than fall back to new detection or inference. Original
planner targets, rectangles and crop bytes remain authoritative and unchanged.

The logical-13 Checkpoints candidate illustrates the safeguard: its larger
native composite overlaps an existing protected crop but is not 90% covered.
Hold that association instead of adding a duplicate or expanding the old crop.
No document title or page number is encoded in this runtime rule.

## Implementation contracts

- Native recovery is a separate transform. It copies every retained crop and
  asset, adds only independently supported disjoint occurrences, and emits an
  accepted/retained/held inventory with geometry, registration and hashes.
- The builder can place a uniquely matched figure in a table's label cell.
  Native supplements preserve all source transcription, including text inside
  the image, without invoking crop OCR or deleting nearby prose.
- URL discovery treats a visible `br` as whitespace with zero raw-text width,
  preserving the DOM and source-offset mapping.
- TOC binding joins an authored row through block provenance to complete native
  headings. Observed printed labels disambiguate; inferred labels never acquire
  authority. Unique headings may resolve without observed page labels, unless
  known page evidence contradicts the row. Final inspection repeats the check.

## Validation and limitations

The final current real driver replay r4 and 110-check comparison pass. Exact
producer/proof files are under output/story251-inspection. Sampling is complete;
independent consumer review accepted r4, and the final cloned continuation is
byte-identical on rendered HTML and assets. Existing baseline coverage is not broadened by one
manual. C3/C4/C5 remain active, Story 226 remains independent, and this does not
claim full embedded-pixel extraction, universal catalog recognition or paid
model quality improvements. Consumer acceptance is independently reported and
must not be inferred from local passing checks.

## First strategic checkpoint

A bounded read-only `/loop-review` requested `gpt-6-astra` / `ultra`; served
identity is not independently exposed. Verdict: continue the existing approach
through one integrated derivative and source/result inspection. There was no
prior checkpoint for this story. Reused the native-occurrence versus embedded
object extraction comparison above because layered printed appearance and the
zero-inference boundary are unchanged. Further generalized detection or model
work would displace the requested inspected bundle. Stop technical iteration
once the actual preservation, image and navigation evidence is clean; acceptance
and any landing authorization remain separate.

Independent semantic review found two actionable edge cases before replay:
ordinary quantity tables could preempt correct original-ID links, and synthetic
`br` discovery whitespace could leak into a raw source quote. The corrections
preserve exact original-ID authority first and derive quotations from authored
text slots. New controls cover these failures, including final inspection.

Root additionally opened the full source images for logical pages 26, 29 and 32:
six small upgrades plus the distinct enlarged Brakes, eight upgrades split into
permanent/temporary groups, and separate Australia/New Zealand service lines
match the intended restoration and URL boundary. The first driver preflight
rejected a single-schema declaration on the mixed-input recovery module. Setting
its input schema to null (as for the mixed-input builder) retains helper-level
source/geometry validation and permits the declared physical/page manifests.
No pipeline stages ran in that failed preflight.

## Integrated result

The second startup attempt exposed the loader convention: declare `params.out`
as well as the stage output name. The public replay example now does so. The
first completed replay restored all28 occurrences and preserved all539 ordered
nonfigure provenance records, but held15 TOC rows. Prepared pages had lost
spread_side/page_id/inferred-label metadata; retaining it in both builder paths
fixed the raw-source join without relaxing identity. Final r4 comparison passes
110 checks, including full ordered article wording (HTML whitespace normalized),
all303 fixture hashes, all103 original crop records/bytes, and all95 existing
exported occurrences. It adds20 crops and places8 retained crops, yielding123.

Root personally inspected each recovered crop in four saved contact sheets,
confirmed their r4 bytes match, saw table-cell placement and preserved duplicate
transcription, clicked all16 TOC links, and saw the corrected separate service
links in the rendered final page. All16 reached the supported headings; observed
page11 disambiguates Summary of a Round from the back cover. Fifteen rows use
observed labels; the first uses only unique-heading authority. No annotations
or final navigation issues remain. This is inspected artifact evidence, not
just a green module run. See correction-report.md for paths, samples and limits.

## Native sampling and append-only continuation

The retained physical13/14/15 rasters are5425x3625 over1302x870 PDF points: exactly
300ppi. All100 placed native occurrences and56 layers comprising28 restored crops
are at or below that grid within0.01ppi tolerance (maximum300.0000184ppi). This
supports retaining existing rendered pixels; upsampling would add no source detail.
The eight existing p28 crops retain the complete inner art but trim outer shadow
bounds (86.66-87.92% containment). Their protected rectangles stay unchanged. Do
not equate rendered RGB fidelity with encoded-stream, CMYK, independent mask,
vector or arbitrary clip-path preservation. Detailed per-occurrence measurements
are in output/story251-inspection/sampling-proof.json.

For an exact completed standard graph, the public preparation helper preserves
the original recipe/stage_params and topo nodes, copies all parent bytes, rebases
only copied state artifact paths, archives snapshots/state, and appends three
stages behind the completed validator. Use the emitted --start-from command;
source-image paths intentionally continue to require the immutable parent/PDF.
All original paid stage records/timestamps stay intact. New HTML has a separate
output/source-fidelity/html root. The clone basename must equal its new run ID
because the driver's output-dir parameter otherwise means a containing folder.
Path containment and relative rebasing use consistently resolved paths, while
receipts retain the source metadata's original spelling (macOS /tmp aliases).

The real continuation passes116 independent checks. Its123 exported images and
12 HTML files are byte-identical to accepted r4, and native inventory is identical
except the run ID. Original12 stage metadata, paid timestamps, original artifact
bytes, graph prefix, initial output and event prefix are preserved. New semantic
validation reports23pass/1warn/0fail: two numeric-label cases are unmeasured by its
legacy call without source-row provenance. This is recorded separately from the
builder's clean provenance-aware report and the16 verified actual destinations.
No validator warning has been suppressed or treated as a wrong target.


## Fresh candidate navigation correction and overlay qualification

The separate 2026-10-08 navigation packet exposed a validator caller omission:
serialized chapter source-page ownership and bundle block provenance were not
passed to the existing TOC inspector. Restoring that context changes only the
navigation check from failure to pass; all23 other checks and candidate bytes
remain identical. Wrong targets, missing/duplicate fragments and ambiguous or
missing source evidence remain rejected. Standalone and validator-only driver
reports both pass24/24. This is a caller correction, not a new semantic policy.

A fresh offline public overlay on the same candidate is independently qualified
at output/runs/story251-navigation-overlay-20261008-r2/. Exact PDF path identity
was essential: a redacted path was refused at preparation, and a byte-identical
alias mismatching physical source records produced a correctly held no-op.
The consumer supplied a separate coherent transport; no runtime guard changed.
Positive proof now covers20 new crops,103 preserved old images,557 preserved
nonfigure provenance rows,11 unchanged ordered chapter texts and24/24 conformance.
All40 recovered native layers meet the retained300ppi sampling grid within the
existing0.01ppi tolerance. Encoded PDF streams, masks and arbitrary clipping
remain outside this rendered-pixel proof. Existing source low-resolution artwork
is preserved rather than reconstructed.

The overlay's explicit reference-resolution flag creates17 source-page links and
two literal URLs in addition to16 TOC links. Independent review corroborated the
page-label/target joins; the builder and final validator report no unresolved or
ambiguous navigation. Root inspected current source pixels, all20 crop images,
rendered table placement, and both previously misclassified numeric links.
The full current offline consumer suite passes711 tests; exact evidence is under
output/story251-navigation-validation-20261008/, including closeout-test-receipt.json
and overlay-producer-pin-r2.json. Earlier pins and failed/no-op artifacts remain
historical evidence, not claims about this new run.
