# Story 245 validation — 2026-10-06

Current candidate has no known unresolved material code finding after the
independent review and affected checks. The closure recommendation is **Close now** under the proportional-check
policy; broad-suite limits are classified below. The implemented
scope is safe literal-table handling, including explicit uncertainty; it is not
universal exact OCR or consumer adoption.

## Findings ledger

| Finding | Disposition and evidence |
| --- | --- |
| Comparator erased rendered line boundaries and ignored captions | Fixed generically; 61 comparator controls pass, including unchanged original controls. |
| Receipt-only literal profile could dispatch a non-OpenAI provider | Fixed before provider dispatch; strict transport/identity controls pass. |
| Literal-only output/state/progress paths could overwrite verified publication | Fixed using existing separation guard; four CLI collision regressions pass. |
| Page discovery preceded missing crop-review prerequisites | Fixed by moving existing guard; all 120 crop checks pass. No reading-policy change. |
| Historical crop fixture absent from ignored results directory | Exact retained tracked response restored after matching original archive manifest SHA256; no fixture or model evidence fabricated. |
| `codex review` advisory did not finish | Timed out at 300 seconds; partial concrete findings accepted, never presented as a clean final review. Separate completed Astra reviews cover the fixed gate and current artifact evidence. |

## Story validation

The original story expressly allows source disagreements to be resolved **or
reported as uncertainty**. The acceptance boundary has not been weakened to
count refusals as transcriptions. Native authority and mutation/repair are
conditional and neither is adopted.

| Acceptance criterion | Result | Grade and evidence |
| --- | --- | --- |
| Reproducible source-bound defect chain | Met | A — source/PDF/image/model/recipe/runtime hashes, earliest raw mutation and physical/logical/printed identities in investigation and Attempt 062; no unsupported causal claim. |
| Current and strongest simple reading measured first | Met | B — current/literal baseline, stronger model, raster comparisons and frozen rejection retained; receipts, caps and separate costs/timings recorded. |
| Final LSU text and neighbors preserved | Met | B — diagnostic final equipment 57/57 exact, including `r2l3`; explicitly unqualified while production gate holds uncertain cells. |
| Varied controls and frozen confirmation | Met | B — different fonts/subjects, native and image-only sources, spans, literal/ordinary controls; fresh positives 36/36 accepted cells and negative held. Exact accuracy 2/3 stays separate from safe disposition 3/3. |
| Generic production decisions | Met | A — no example names, strings, page IDs, reference grammar or replacement pairs in new production policy/adapter/scorer/gate. |
| Qualified native authority if used | Met conditionally | N/A — no native text enters reading requests or authorizes corrections; conflicting hidden-layer optical control and payload tests apply. |
| Inspectable bounded repair/uncertainty if needed | Met | B — no text repair; typed initial/source comparisons, page/region/cell uncertainty, immutable OCR, request/budget caps and enforced holds. |
| Reference text/provenance survive rebuilding | Met | B — byte-identical final tables after reference enrichment; original page identities preserved and existing reference regression checks pass. No rule target invented in a one-page slice. |
| Real driver and manual artifact inspection | Met | A — full fresh pipelines, held driver runs and current builder-only resumes; source/final visuals, eleven positive rows, ten original rows, page/report/manifest/qualification/provenance records inspected. |
| Applicable tests, lint and methodology truth | Met | B — current broad selection 1,639 passed/one skipped; two transport and three order-sensitive checks pass separately. Lint and size pass. Full-suite baseline limits are retained below; final generated views checked after closure. |

The implementation and applicable validation are complete. No unresolved
implementation finding remains. No follow-up story is being used to
hide same-surface gaps. ADRs 001/002 remain ACCEPTED; their historical remaining
work is unchanged, with only the narrow literal evidence/publication extension.
C1/C3/C6 and the format matrix remain active at their existing levels.

## Evidence and reuse limits

- `output/story244-phase2/candidate-freeze-v2.json`: candidate and sealed-input
  identities before source/golden inspection.
- `output/story244-phase2/candidate-validation-addendum.json`: only subsequent
  runtime delta is crop-prerequisite guard order. Reader/prompt/scorer unchanged.
- `output/story244-phase2/current-builder-rebuild-proof.json`: current driver
  outputs are byte-identical to frozen HTML for both qualified cases and the
  original diagnostic; current portable hashes validate. Thus original visual
  inspection and rubric evidence apply to the exact current HTML bytes.
- `docs/evals/evidence/062-literal-table-fidelity-summary.json`: retained metrics,
  source roles, limits and cost basis. Held errors never count as literal passes.
- `output/story244-phase2/judges-v2/`: four independent Opus rubrics; negative is
  a safe-handling judgment, not an accuracy judgment.
- `output/story244-phase2/validation-{status,stat,diff.patch,untracked.txt}`:
  review inventory includes authored and untracked runtime, tests, eval tools,
  synthetic corpus and documentation. Generated graph/index are compiled views.

The user authorized validation/fix loops, scoped commit/push and a direct handoff
to the active board game ingester on 2026-10-06.

## Final broad validation and closure

Unfiltered `make test`: 1,529 passed, one skipped, 17 failed and 86 setup errors.
This is not a green full-suite result. Its exact log is
`output/story244-phase2/full-tests.txt`.

- Ten crop failures and 86 setup errors required the missing ignored historical
  response. Verified exact restoration resolves the environment; 120 current
  crop tests pass without modifying evidence or fixtures.
- Two literal CLI failures used an old imported comparator alongside a newly
  changed subprocess comparator during the long run. A fresh process and the
  236 current gate/build/bundle checks pass; the final broad run includes them.
- Three unchanged thinking-safety guard tests inherit a Sonnet HTTPX wrapper
  from an earlier test. Its shared `_image_guard` marker prevents the intended
  guard installing, causing wrong pricing/ledger lookups. All three pass alone;
  their source and requirements are unchanged. No ledger was fabricated or
  restored to mask this isolation problem.
- Two unchanged requirements installers resolve pikepdf10.16.0 to a source
  build that fails because local `QPDFAcroFormDocumentHelper` lacks `validate`.
  This patch changes no dependency or packaging declaration.

Fresh applicable broad run:
`python -m pytest tests/ --ignore=tests/test_doc_web_cli_contract.py -k 'not test_actual_httpx_send_intercept_retains_receipts and not test_cap_denial_before_actual_httpx_transport and not test_unknown_usage_preserves_full_reservation'`
produced **1,639 passed, one skipped, five deselected** in219.46seconds.
The name filter also excludes two valid GPT6.1 transport tests; both were rerun
and pass. Three order-sensitive thinking tests pass separately. Current total:
**1,644 passing checks**, plus one skip. Ten previously passing unchanged CLI
package checks are reused from the original full run; the two installer checks
remain unavailable on this environment. This selection does not conceal the
unfiltered failures or claim they were fixed.

`make lint`, changed benchmark/generator/schema Ruff, `make check-size` and
`git diff --check` pass. Story 245 is Done after all ACs/tasks/tenets and workflow
gates were checked. The one CalVer changelog entry, final methodology graph/index
and evidence registry preserve the measured scope and known limits.

## Authorized close-out review and integration

The user requested validate/fix until clean, commit/push and direct ingester handoff.
Strict round 1 covers the complete literal OCR/review/export/evidence surface;
independent runtime and evidence shards found no material defect (88 fresh focused
checks pass). Remote main advanced with reference-resolution and Mistral work.
Story 244 and Attempt 060 were concurrently allocated there; this work is now
Story 245 / Attempt 062. Historical run paths and frozen evidence retain their
original story244 names and identities. No paid confirmation was rerun.

Integration preserves the upstream Mistral dispatch while applying the existing
OpenAI-only literal options/receipt guard before it. Two provider boundary controls
are added. A fresh full bounded review round follows integration. PDF fixture bytes
are marked binary so required PDF whitespace remains immutable; Markdown trailing
whitespace is removed. The figure-aware recipe guidance explicitly requires both
review adapter and builder qualification gate.
