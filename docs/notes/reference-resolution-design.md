# Reference-resolution design and research (Story 243)

2026-10-05. Scope: bind explicit document references after structure and block IDs
are final, optionally discover unlinked text, and retain evidence for consumers.

## Decision

Reuse the unmerged `manual_navigation.py` from the Ingester worktree, whose
existing-link behavior has 22 focused controls. The source snapshot and SHA256
receipts are in `output/story243-baseline/donor/snapshot.json`. Its upstream
owner remains active; these are copied bytes, not a claim of a merged release.
No other worktree is edited. The new story extends this same resolver.

Callers opt into enrichment using `--resolve-references`; routine final link
inspection remains on. No model or network calls belong in this implementation.
This is exact binding against already extracted structure. No claim is made
that a model could not resolve broader language; semantic inference is outside
the current supported behavior and evaluation.

Resolve in a two-phase pass: index final destination identities and source
evidence, then inspect/transform references. Preserve exact text, element order,
inline markup and block IDs. Resolve before hashes and consumer manifests are
sealed. Sidecar reports expose candidates, chosen destination, source evidence,
abstention and metrics rather than just a broken-link total.

Printed page labels are identifiers, distinct from source scan indexes. An
observed Roman or Arabic label can locate an unambiguous final block/page marker.
Inferred offsets, missing labels, repeated labels and unsplit spreads do not
authorize a guessed destination. Raw page evidence is mandatory: existing
paragraph provenance can contain fallback printed numbers and lose the inferred
flag.

Contents/index entries are explicit references. Scope their unprefixed page
numbers to supported table/list/semantic containers or explicit headings.
Keep generated previous/next navigation out of discovery. Range parsing must
not turn an ambiguous interval into a guessed single page.

## Established methods and applicability

- [EPUB 3.3 navigation](https://www.w3.org/TR/epub-33/#sec-nav-pagelist)
  distinguishes content hierarchy from print-page navigation; separate print
  labels from HTML target identity. Its pagebreak model is useful where source
  page boundaries survive. We do not add an EPUB dependency or invent breaks.
- [Sphinx cross-references](https://www.sphinx-doc.org/en/master/usage/referencing.html)
  bind unique explicit labels across document files. Adopt uniqueness and
  explicit scope; do not use fuzzy title similarity as authorization.
- [W3C Text Quote Selector](https://www.w3.org/TR/annotation-model/#text-quote-selector)
  supplies a standard pattern for identifying exact text with context. Report
  original wording and block-local occurrence location so repeats are auditable.
- [Python URL parsing security](https://docs.python.org/3/library/urllib.parse.html#url-parsing-security)
  warns that parsing is not validation. Constrain generated URLs to explicit
  HTTP(S), preserve displayed spelling, validate paths within bundle boundaries,
  and avoid any claim of network availability.

These sources guide design, not proof. The local probe shows existing donor
behavior detects zero plain references; fresh fixtures and driver output must
establish this implementation's behavior.

## Validation and economics

Use exact occurrence/destination goldens and deliberately wrong targets that
exist. Score recall, wrong-link count, abstention, text/markup preservation,
provenance and report coverage separately. Natural documents are stress evidence,
not automatically authoritative goldens. Historical FF engine references may
have been mechanically derived; audit their provenance before using them as an
oracle. Reserve an independent document before tuning.

Performance: freeze the post-verification resolver baseline, time identical
inputs with interleaved comparisons, record all samples and full-driver versus
resolver boundaries. Maximum three candidate revisions/two strategies and 60
active minutes, no paid pipeline calls. Require zero wrong links/content loss
and >=10% median speed improvement with consistent paired results for speed
adoption. One predeclared independent confirmation; stop two non-improving
attempts or negligible user-visible remaining overhead. No compounded or
cross-boundary speedup claims.

## Loop review — planning checkpoint

**Verdict:** aligned, with one important evidence limit: historical pagination and
golden navigation cannot be assumed authoritative.

1. Follow-through: first checkpoint; no earlier recommendation. User-authorized
   optional pass, Sol6.1 medium workers with goals, Conductor loop-review, final
   verification and optimization are all reflected in the story and assignments.
2. Utility/evidence: discovered existing source-ID overwrite and lost inferred
   label provenance; adapting the actual donor avoids a second resolver and
   prevents scan-index false links. Added user-requested TOC/index behavior.
3. Opportunity cost: a whole-document model rewrite would add cost and fidelity
   risk; restoring legacy gamebook logic would displace the generic final seam.
   Exact symbol binding plus explicit abstention is the smaller useful option.
4. Disposition: continue current bounded implementation. Compare frozen explicit
   controls first, then natural FF/manual workloads. Reassess after three
   substantive implementation rounds or30 active minutes; paid inference is
   deferred unless a measured supported-use gap changes the decision.

No scope or permission expansion required. Root goal remains active until
verification, baseline, bounded hillclimb and final artifact inspection finish.

## Loop review — partial inline references

Natural gamebook calibration exposes a generic DOM range problem: the phrase
can begin outside an inline element whose remaining text extends past the
reference. The [DOM Range standard](https://dom.spec.whatwg.org/#dom-range-surroundcontents)
rejects partially contained non-Text nodes for surroundContents;
[Text.splitText](https://dom.spec.whatwg.org/#dom-text-splittext) preserves their
parent structure. Adopt full-element wrapping where safe and a text-leaf wrapper
fallback for partial inline ranges, without cloning source IDs or rewriting
text. One logical occurrence may have multiple adjacent anchors. This is a
source-preserving generic fix, not a gamebook-specific substitution.

Continue implementation before performance freeze. Current synthetic development
cases pass, but the natural adapter showed material missed explicit references.
URI-equivalent same-file links must be normalized by the scorer without changing
the destination oracle. Printed-label ambiguity must use all raw observed pages,
including source pages the builder previously collapsed. Local tests and a fresh
driver build will decide applicability; held-out cases remain reserved.

## Loop-verify plan and finding ledger

Mode: strict-until-clean, because executable reference binding, output schemas
and scoring contracts are in scope. Three fresh Sol6.1 medium find-only shards
(core, integration, evaluator), one bounded pass each (about10 active minutes).
Material findings are wrong/unsafe targets, source loss, option leakage, schema
or final-hash mismatches, false evaluation proof, or missed stated acceptance.
Style/nits do not reset. Parent verifies findings and coordinates fixes; any
material fix resets the original three shards only while converging. Stop at a
clean round, scope expansion, blocker or the skill's nonconvergence threshold.

Local scope is the Story243 diff and its generated/evaluation outputs. Historical
Codex Forge extractions and Ingester are evidence-only; their OCR/packaging
defects cannot be fixed here. Source artifacts are immutable.

Round1 begins after core calibration:41focused tests,development24/24 and
Deathtrap627/627 known source-anchor occurrences with zero wrong links. These
are preverification calibration results, not the optimization baseline.

### Round1 — core and additional CLI review

Accepted material findings from fresh core reviewer (41existing tests passed):
1. Overlapping TURN/EXPLICIT/URL spans nest anchors; arbitrate candidates before
   mutation and reject nested output in final validation.
2. URL matching crosses excluded-code boundary placeholders; use token barriers
   and reject control characters.
3. Invalid source URLs raise during always-on inspection; report invalid targets.
4. Global heading text can authorize generated targets in another entry; scope
   evidence to owning entry.
5. Shared logical page numbers with distinct spread identity select the first
   side; bind complete observed identity or abstain.

Independent `codex review --uncommitted` (Sol6.1 medium) reproduced findings1/3
and added one accepted DOM-fidelity finding: zero-text inline nodes (br/img) can
move relative to words when wrappers gather only text-bearing siblings. Preserve
ordered DOM topology as well as visible text, IDs and tag counts. No findings
rejected so far. Core worker owns class fixes/regressions. Original shard scope
will reset after fixes; this round is not clean.

Manual driver inspection at `output/runs/story243-integration-verified-on/output/html/`
read all10decisions:8resolved,1missing(page99),1ambiguous(duplicate page22).
Off has one repaired existing link. Browser rendered the TOC/index and clicked
Section7 to its Equipment heading. Printed12 maps logical source2; Romaniv maps3.
These samples prove normal-case behavior, not absence of the adversarial issues.

### Round1 — integration and evaluator

Accepted integration issue: printed-first `_page_sort_key` still reverses
within-chapter reading order when numbering resets, despite final-entry ordering.
Real driver repro confirms source[1,2]/printed[12,1] becomes[2,1]. Fix the source
identity ordering class and validate the final manifest's numeric printed bounds.

Accepted evaluator issues: deleting report target/evidence/wording/provenance
still passes because only block/status counts were checked; removing a whole
expected DOM occurrence inflates recall denominator; raw timing samples were
discarded despite the experiment contract. Add independent corrupt-output
controls and retain all samples before measuring optimization. No heldout run.

Disposition: all three shards require material local fixes, no outside-owned
implementation expansion. Continue one fresh original-scope round after fixes.
The existing DOM/symbol-binding approach still fits; stronger selection and
identity invariants address these classes without adding heuristic guesses.

Broader pytest exposed absent saved crop-review fixture
`benchmarks/results/safety-repair-048-20260929-continuation1/response-068.json`,
also absent in original checkout. This is separate from reference correctness;
do not fabricate evidence to make those unrelated controls pass.

Broad-suite attempt: interrupted after440.68s at505passed/10failed/86errors.
All reported failures/errors trace to the absent saved crop-review response.
Fresh-environment packaging installs were progressing slowly and do not exercise
this diff's package metadata (unchanged). Run the available broad suite excluding
those three fixture-dependent files and ten fresh-install packaging tests; retain
full logs and do not call the full suite green. The reference, driver, schema,
CLI contract, native converter and chapter tests remain included.

### Round2 — systemic-audit stop

Core50tests pass, but fresh reviewer reproduced remaining same-class failures:
comments become ordinary visible text; a shared original scan number is treated
as distinguishing L/R identity; nested TOC parent direct-text references are
omitted. The ordinary loop stops **systemic-audit-needed** under loop-verify's
nonconvergence rule. Do not call this a converged round or keep patching examples.

The existing user-authorized completion goal covers a bounded audit of the same
DOM/page-identity boundary (no new capability/owner scope). Core owns one
15-minute invariant audit, recorded separately: visible node domain; exactly-once
nearest-block ownership; preserved ordered DOM after unwrapping generated tags;
and unique matching of observed page identities from available provenance.
[Beautiful Soup special strings](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#special-strings)
confirms that Comment and other nonvisible classes subclass NavigableString;
raw isinstance checks are not a visibility model. Reuse DOM Text.splitText
semantics, now with an explicit node eligibility contract.

After the bounded audit, perform independent acceptance of those invariants and
the original integration/evaluator seams. No additional ordinary iterative review
rounds are authorized by this checkpoint; unresolved class defects will be
reported explicitly rather than counted as success. Performance remains paused.

Available broad suite:1243passed/1skipped/10fresh-install cases deselected;
3failures in test_thinking_safety_guard arise from prior guard import retaining
a pointer to absent sonnet55-20260928/ledger.json. All3pass alone (0.10s);
test and provider files are unchanged. This is an existing isolation/fixture
limitation, not a clean full-suite claim. Preserve logs at
output/story243-{full-tests,available-suite}.log. Final reference changes receive
fresh focused regression and driver runs.

Round2 integration accepted one new metadata regression: newly strict chapter
param_schema omitted legitimate pages/portions params used by the existing
Story241 recipe. Fix complete parser surface and prove all relevant recipe
plans; keep global param validation strict.

Post-audit evaluator acceptance: no material issue; independent corruption
probes reject missing/false source/target evidence, lost or repeated occurrences
and changed hashes.21tests pass. Integration metadata correction freshly
passes23controls including existing recipe/parser flags. Core independent
acceptance found empty structural containers were missing boundaries; parent
completed enter/exit traversal and added a generic empty/nonempty matrix.111core
controls and both development workloads pass. Bounded confirmation is pending
before performance GO. Earlier loop status remains systemic-audit-needed.

Bounded core confirmation completed: all three original structural-boundary
reproductions now pass, original DOM/source offsets preserved,111focused tests
pass. No reported finding remains unresolved in that confirmation scope. Parent
accepted corrected baseline for performance, with prior systemic-audit history
retained. Performance worker received GO only after this confirmation; evaluator
and corpora remain frozen and independent material remains unopened.

Performance-phase quality hypothesis: parent independently found two donor
heading-token false repairs outside the original frozen fixtures: “See page3”
borrowed a numbered section3, and “Return to section10” borrowed a “Return policy”
heading from its first word. Preserve the already-frozen baseline, record these
supplemental adversarial failures separately, and constrain explicit typed labels
plus fallback full-heading/numeric-identifier evidence consistently in repair and
final inspection. This is the second (quality) strategy within the existing
three-revision/two-strategy cap; no golden answers or heldout material change.
The cache-only candidate remains provisional until the combined quality gate.

### Final validator authority audit

The final core review reproduced a composition defect: exact original-ID alias
authority overrode a conflicting visible section label in the resolver, while
the serialized validator rejected that same correct binding. A first correction
passed alias maps into the checker, but independent confirmation proved that a
flattened source-link inventory allowed another chapter's identical label to
authorize a corrupted destination. Filename scoping alone is also insufficient
for two same-label occurrences in one chapter. This is an occurrence-identity
defect, not a need for additional heading heuristics. Stop the ordinary patch/review
loop and correct the evidence boundary once, then confirm the original probes.

Bounded research revisited the W3C annotation model: [quote selectors](https://www.w3.org/TR/annotation-model/#text-quote-selector)
can match multiple occurrences; [position selectors](https://www.w3.org/TR/annotation-model/#text-position-selector)
identify occurrences but need representation context when content changes.
Adapt that distinction: source evidence belongs to its entry and exact anchor;
identical wording is not identity. Retain resolver-owned original-href evidence
on alias-authorized anchors, independently checked against owning source entries
and original ID maps. Incoming metadata cannot establish its own authority.
Regressions must cover same/cross-entry borrowing, forged initial metadata,
repeat invocation, missing/duplicate targets and altered serialized hrefs.
No discovery grammar or external API capability is added. Independent corpora
remain unopened. Final measurement must bind the corrected runtime, preserving
the earlier receipts rather than retroactively relabeling their code hashes.

The occurrence audit's confirmation rejected the first receipt implementation:
uniqueness did not bind a receipt to its anchor, and invalid/missing receipts
could fall through to label inference. Parent specifies the structural completion:
freeze each receipt's final anchor ordinal after enrichment, compare every expected
receipt at that exact serialized position within the emitter-owned content root,
and make any missing/moved/changed receipt fatal. This catches both receipt
transfer and a change to an otherwise plausible semantic target. Parent also
reproduced a related repeat-call failure: a newly generated `section 2` link to
`#b` acquired an unrelated original-ID alias `b→c` on the second pass. Alias
authority must require an actual original source anchor (or its proven retained
receipt), never merely a matching href on a generated link. These are completions
of the same source-occurrence invariant, not additional reference heuristics.
Keep all rejected snapshots; no final timing or independent-corpus run has yet
been consumed. Confirmation is bounded to this invariant and the original probes.

Bounded structural confirmation is complete at manual helper SHA
`5c584fe228578b1129bf972a9ab1742cfd69ebcc54492ead68a81a87673eb46b` and
reference helper SHA `445599ed222a9887e8414642c7448eda8d1cec6fe056761c5161a02ab24b580d`.
The independent reviewer ran 54 focused controls and directly replayed transferred,
duplicated, deleted and semantically altered receipts: all corruptions fail;
correct aliases and repeated resolution pass. Chapter/Office/Marker content
boundaries and missing/duplicate file/fragment guards were inspected. All
reported findings are closed in this bounded scope. Earlier nonconvergence and
rejected corrections remain recorded; this is not a claim that those rounds
were clean. Final performance confirmation now uses the same corrected semantics
with and without the parse cache, preserving exact on/off state parity and the
original timing gates. Independent material is still sealed at this checkpoint.
