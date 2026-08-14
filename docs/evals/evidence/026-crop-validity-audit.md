# Attempt 026 crop-validity visual and provenance packet

## Target

- Full source page: `benchmarks/input/source-pages-b64/Image125.b64.txt`
  (`1545x2000`, SHA-256 `16e63507...17db`).
- Extracted crop: `benchmarks/input/crop-validation-b64/page-126-000.b64.txt`
  (`2933x2116`, SHA-256 `290cd36d...7b0e`).
- Goldens: `benchmarks/golden/crop-validation.json` and
  `benchmarks/golden/crop-page-level-deletion-gate.json`.
- Selection provenance: `benchmarks/golden/crop-eval-provenance.json`.

## Visual inspection

The source page contains two distinct memorial photographs. In the upper
photograph, the intended central veterans plaque is bordered on the left by a
separate narrow text-bearing plaque. The extracted `page-126-000` crop retains
that separate plaque as a conspicuous partial strip along its left edge. The
strip is not text engraved on the intended central plaque and is not required
to preserve the central photograph's meaning.

The fail label therefore remains source-backed for both crop-only safety review
and page-context review. Relabeling it would weaken fidelity and conceal a real
production crop defect.

## Validity classification

- **Golden truth:** valid `fail`; no golden edit.
- **Production safety regression:** valid hard regression case. A proposed
  runtime/default may still be vetoed for reproducing this leakage.
- **Model selection:** not an untouched discriminator. The crop-only prompt was
  selected on the full 40-case set, and the page-context prompt was explicitly
  tightened after this case failed.
- **Tuning parity:** historical challengers were generally run with the frozen
  incumbent-selected prompt and did not receive an equivalent declared
  calibration budget.
- **Current prompt/adapter parity:** Gemini 3.7 received strict structured
  output and the same crop-only semantic prompt, but semantic configuration
  selection was not symmetric.
- **Incumbent freshness:** the recorded crop-only `40/40` is from April 2026
  and predates the current GA provider ID; it is not a fresh current comparison.
- **Capability versus adoption:** Gemini 3.7's `39/40` is valid regression-set
  capability evidence and a valid safety-policy block on changing the default.
  It is not unbiased evidence that the incumbent model is intrinsically better.

## Remedy

Keep every current label and retain both existing corpora as calibration plus
production-regression surfaces. Block new winner/promotion claims until a new
source-backed held-out confirmation slice is frozen before provider calls.
Future comparisons may tune each model only on the declared calibration slice
with the same arm budget, then evaluate the frozen configurations once on the
held-out slice. A held-out win cannot override a failure on the production
safety regression gate.

## Frozen-output regrade

The retained Gemini 3.7 crop-only output regrades as `39/40` on calibration /
production regression, with sole failure `page-126-000`; held-out confirmation
contains `0` cases, so `selection_claim_allowed = false`. No paid rerun was
performed because identical incumbent/candidate calls on the already-exposed
corpus could not produce decision-bearing model-selection evidence.

## Held-out feasibility audit

The bounded search of existing Onward output history found only three logical
crop keys outside the maintained 40-case crop-only corpus:

| Candidate | Source/crop SHA-256 | Visual finding | Selection value |
|---|---|---|---|
| `page-012-002` | source `055f8314...516d`; crop `162d28b7...66f8` | Clean crop of the Gordon MacMurchy signature block on a certificate. | Pass-style only; source page 12 is already represented in calibration. |
| `page-122-002` | source `0a0d55a6...bfad`; crop `f2a4a8f9...b859` | Clean oval Sophie L'Heureux portrait with its integral name card. | Pass-style only; source page 122 is already represented in calibration. |
| `page-002-000` | source `ae9c7705...825`; crop `9e8bd1eb...fb1e` | Clean crop of the title treatment and dates. | Previously unused source page, but pass-style only. |

This inventory cannot honestly be frozen as a decision-bearing held-out slice:
it contains no natural production failure, only one source page not already
exposed during calibration, and only three cases total. Adding those cases as
"held out" would manufacture the appearance of independence without testing
the safety boundary that caused the disputed veto. The cases therefore remain
outside the benchmark and the held-out arrays remain empty.

### Executable next confirmation recipe

Before any validator call, prepare and freeze **12 natural production crops**
from at least **8 source pages that have no page overlap with either current
calibration corpus**:

1. Predeclare an unused page slice, run the maintained crop driver once, and
   retain every crop from those pages. Do not inspect validator output.
2. Review each source page beside each crop. Record the source and crop hashes,
   a source-backed verdict, and one of the existing failure categories. Obtain
   an independent second visual review.
3. Freeze a balanced `6 pass / 6 fail` confirmation task and its provenance. If
   the page slice yields fewer than six natural failures, expand by fixed
   increments of four unused source pages and review all crops from them; do
   not synthesize bad crops or cherry-pick cases based on model behavior.
4. Freeze both models' prompt, adapter, schema, reasoning, and equal
   calibration-arm budget. Run the current incumbent and challenger once on
   the held-out task, then separately run the full production-safety regression
   gate. A held-out pass does not waive a regression veto.

The preparation step is currently blocked by the absence of a predeclared
unused-page production run with enough naturally failing crops, not by missing
provider access. Creating that run is intentionally outside this bounded audit
and its no-broad-sweep authority.

## Candidate-close integrity repair

The first regrader implementation keyed result rows into a dictionary before
validating them and treated any nonempty held-out list as selection-eligible.
That could silently collapse duplicate `crop_key` rows, accept overlapping
partitions, and permit a blocked or failing held-out result to support a winner
claim. The repaired regrader now fails closed on malformed/duplicate rows,
duplicate partition keys, calibration/held-out overlap, and missing or extra
coverage. `selection_claim_allowed` is true only when
`model_selection_status == eligible_held_out_confirmation` and the held-out
partition is both nonempty and entirely passing.

Adversarial regression tests reproduce duplicate-row, overlap,
blocked-with-passing-held-out, and eligible-with-failed-held-out cases. The
retained Gemini 3.7 artifact still regrades `39/40`, with no held-out cases and
`selection_claim_allowed = false`; no provider call or golden change was
needed.
