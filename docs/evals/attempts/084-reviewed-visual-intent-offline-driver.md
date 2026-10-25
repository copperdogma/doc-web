# Attempt084 — Reviewed visual intent through the actual offline driver

Story262, spec:4/spec:6. **Pass for bounded reviewed-intent execution; outputs
remain review_hold.** No model, provider call, credential, default change,
source deletion, commit or push. Spend USD0. Sealed082/083/plan unchanged.

## Result

The existing planner-owned path admits the title page despite historical OCR
`images:null`, and preserves the complete reviewed title/date unit. Five
authored targets yield five lossless PNG crops, all exact RGB source rectangles.
No detector prompt, schema or product algorithm change was needed. This avoids
paying models again before the grouping/admission ownership is explicit.

Actual run: `output/runs/reviewed-visual-intent-084-r5/`.
Manifest: `03_crop_illustrations_guided_v1/illustration_manifest.jsonl`.
Producing inputs/freeze/recipe/logs and proof-v1:
`benchmarks/results/reviewed-visual-intent-084-r5/`.
Corrected offline verification: `docs/evals/evidence/084-reviewed-visual-intent/proof-v2.json`.
Evidence index: `docs/evals/evidence/084-reviewed-visual-intent/manifest.json`.
The index hashes existing frozen inputs and driver assets; no duplicate large
archive was created during the host storage shortage.

| Original / source page | Reviewed rectangle (source pixels) | Inspection |
|---|---|---|
| Image001 / 2 | 960,1760–4370,2545 | Full ONWARD / TO THE UNKNOWN / 1887 - 1987; external author heading excluded. |
| Image003 / 4 | 280,1740–4820,3060 | Complete wagon/animals/ground; separate printed credits excluded. |
| Image008 / 9 | 1100,1700–4150,4440 | Portrait retained; external name/date and dedication prose excluded. |
| Image011 / 12 | 1890,450–3010,1550 | Complete logo/circular lettering/1905–1980. Seal/signatures outside selected target; no full-page coverage claim. |
| Image124 / 125 | 510,450–4600,4520 | Artwork/clouds/integral artist signature retained; separate printed credit excluded. |

Geometry is explicitly authored reviewed input, **not a native model prediction**.
Source001's independently measured dark support in a broad source ROI is
986,1786–4345,2518; the reviewed rectangle adds edge margin. The golden was
neither changed nor read by the runner. Two different synthetic title/date
layouts also verify generic ownership without document/page/string branching.
Nearby source text is empty where not supplied; editorial rationale is only in
reason, and expected_visual_contents is a list, matching the existing contract.

## Custody and actual consumer boundary

Run registry check-reuse reports historical onward-book-r1 unsafe globally
(later empty pages/portion failure). No override or original repair occurred.
The full 867231-byte early OCR artifact is frozen. Five complete selected early
rows are independently hash/schema/content/mapping checked as **quarantined
historical input**, not newly qualified OCR or a globally reusable run.

Historical extracted JPEGs and originals have distinct hashes, both5100×6600.
Independent source/edge review plus dark-mask registration IoU .99854–.99983
supports reviewed 1:1 coordinate applicability. The plan honestly names the
historical OCR coordinate frame. An explicit page-number highres manifest
selects each frozen original: Image001→page2. Attempt052's existing highres
coordinate guards are reused; no source identity is forged or guard weakened.
The sidecar coordinate-mapping.json binds both hashes, pages and target IDs.
Equal-sized frames do not emit bbox_transform in the existing helper; the
illustration manifest alone is not a 1:1 mapping receipt.

`load_artifact_v1` overwrites run_id/created_at; registered page_html_v1 stamping
also adds **literal_fidelity:null**. All original fields/content remain present
and exact, including html/raw_html, source PDF and historical image paths,
diagnostics and images:null. Native producer rows and full file remain frozen.
Page2 retains title/date/author/roman-page HTML. This proves content preservation
through the **loaded OCR boundary**, not final rendered HTML or deduplication.

Illustration_v1 is unregistered in current SCHEMA_MAP: driver retains the
module-produced envelope without registered illustration stamping/validation.
The replay verifier separately checks page/source/dimensions, IDs/role/
importance/reason/contains_text/expected contents, exact rectangles/RGB and
absence of detector/caption request/provider fields. Authorship/policy/reviewer
and hold remain in the hash-bound input sidecar; no model receipt is fabricated.

Independent review found proof-v1's before.get/after.get comparison conflated
missing keys with null and failed to report the schema default. The producing
runner and proof-v1 were copied/hash-frozen **before** correction. Proof-v2
re-verifies unchanged r5 outputs with presence-aware comparison: only declared
run envelope changes and the actual added literal_fidelity=None default pass;
unknown null additions, original-key deletions and changed content fail. V2
links the original producing freeze/proof hashes and revised verifier hash.
No driver/crop rerun or historical proof rewrite occurred.

## Guard, research and retained failures

Only process essentials enter the guarded driver environment; no API key,
credential wrapper or env file is loaded. Four Python processes install the
inherited startup guard. Connect/DNS/send/bind and listen/accept are blocked;
unguarded/non-Python child execution fails. This protects the selected trusted
Python workflow, not arbitrary malicious native code.

General obstacle: dependency import-time capability probing under a no-network
test boundary. Installed urllib3 1.26.18 _has_ipv6('::1') attempts a port0 bind,
then treats failure as unavailable IPv6. Primary research:
[urllib3 connection source](https://github.com/urllib3/urllib3/blob/main/src/urllib3/util/connection.py),
[CPython audit events](https://docs.python.org/3/library/audit_events.html).
Final guard keeps **all binds blocked**. Only exact ::1/port0 with verified
_has_ipv6 callsite/path/frozen source SHA is classified
blocked-local-capability-probe, then raises. One such blocked probe is logged;
no bind succeeds. Every other denial fails verification. Direct ::1 bind cannot
masquerade as the import probe, as the focused regression establishes.

Retained zero-cost iterations:

* r1: loader filename mismatch stopped before crop; recipe output basename
  corrected to the existing loader protocol. No module patch.
* r2: produced crops but verifier rejected unclassified blocked urllib3 probe.
* r3: interim logged bind-allowance prototype; superseded by final stricter
  keep-all-binds-blocked guard. Inspected crops retained, not final safety proof.
* r4: ENOSPC during first original copy, before driver launch; never resumed.
* r5: one bounded recovery completed under final producing guard. No task or
  general disk cleanup occurred. Guard-suite startup/Ruff also once failed for
  ENOSPC; subsequent applicable checks passed. A draft report write later failed
  transiently; no evidence was silently removed to recover space.

## Verification and limits

New tooling suite26 pass, including wrong-page/dropped-role/altered-contains
rejection, stale source/path escape, authorship/hold, network/env/process guard,
inheritance/missing-sink and two synthetic layouts. Five additional presence-
aware mutation/default checks validate the v2-only correction. Existing affected
loader/driver/schema/recipe/planner tests30 pass; critical crop/zero/absent-plan/
metadata tests29 pass (36deselected). Focused Ruff passes. Full product suite
not selected for isolated opt-in tooling; product modules remain unchanged.

Opened r5 manifest and complete OCR sample and viewed r5 title/date. All five
r5 PNG hashes exactly match personally inspected r3 crops; full originals were
also inspected. Supervisor independently viewed all five final crops/sources.
No claim of every-pixel whole-page semantic fidelity follows from rectangle
equality. Output remains held for existing safety/manual publication authority.

Automatic heritage admission/semantic planning, Kimi installed provider stamps,
native caption custody, renderer/export and downstream text deletion remain
unqualified. Owned targets intentionally bypass detector/caption/layout trim;
ordinary untargeted controls/defaults are unchanged, C4/C5 remain. Image000
physical-cover extent uncertainty stays separate. No further paid comparison is
needed to repeat Attempt083's unchanged grouping conflict.
