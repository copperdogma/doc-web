# Story 243 core invariant audit

2026-10-05. Bounded systemic audit after two independent rounds found variants
of the same DOM visibility and page-binding failures. Stop instance-by-instance
verification repairs; establish one edit domain and one binding proof first.
Scope remains the existing resolver, focused controls and this audit record.
No goldens changed; no model/API calls.

## Evidence and established alternatives

- [Beautiful Soup special strings](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#special-strings)
  identifies comments and other specialized `NavigableString` subclasses.
  Installed version is **4.12.3**. Inspected `Tag._all_strings`: default text
  collection uses exact string classes, excluding comments and processing
  instructions; CData is included. A local parser probe produced ordinary
  `NavigableString`, `Comment`, `ProcessingInstruction`, `CData`,
  `TemplateString` and `Script`. `get_text()` yielded `AvisibleB` from
  ordinary A/B plus CData, excluding comment/PI/template/script contents.
- [DOM Text.splitText](https://dom.spec.whatwg.org/#dom-text-splittext)
  preserves a text node's parent context. Adopt this principle for ordinary
  leaf splitting rather than clone partial inline elements and their IDs.
- [DOM Range.surroundContents](https://dom.spec.whatwg.org/#dom-range-surroundcontents)
  rejects partial non-Text containment. Whole sibling units are moved only
  when the range includes every intervening sibling. Otherwise same-target
  text-leaf wrappers preserve original ancestor topology.
- Complete page-identity matching replaces the earlier existential agreement
  test. Agreeing on a physical scan number shared by L/R proves neither side.
  Enumerate raw identities first; provenance must match exactly one identity.

## Enforced invariants

1. Only **exact ordinary `NavigableString` nodes** enter the editable domain.
   Specialized strings remain original nodes; CData is conservatively left
   untouched even though this parser includes it in `get_text()`. Templates,
   scripts/styles, code, existing links, hidden content and navigation chrome
   are excluded. Opaque slots prevent reference tokens crossing exclusions,
   including empty excluded elements. Resolution does not make hidden strings
   visible, rewrite them as ordinary text, or change their ordering.
2. Each ordinary text node belongs to its nearest eligible block. Parent-owned
   text before/after nested blocks is discoverable; descendant blocks are
   barriers and resolve their own text once. TOC/index suffix matching works
   per parent-owned segment instead of requiring one leaf-only block.
3. Discovery and mutation use the same slot coordinates. Opaque barrier
   coordinates map back to original `get_text()` source offsets; comments,
   specialized invisible strings and synthetic empty-element barriers never
   shift reported source locations. Nested blocks report offsets relative to
   their actual ID-bearing ancestor. Candidate occurrences
   are nonoverlapping: URLs take precedence; longer explicit phrases own their
   interval. No mutation can revisit an already selected interval.
4. Whole-node moves require complete sibling coverage and DOM object identity.
   Leaf fallback retains comments, empty breaks/images, partial inline elements,
   original attributes and IDs. One logical record may describe several adjacent
   equivalent links. Final inspection independently flags nested anchors.
5. Raw identities include logical number, page ID, physical/original number,
   spread side, observed print label and inferred flag. All supplied provenance
   identity aliases and labels must agree. A provenance projection must match
   **exactly one raw identity** within the logical-page group. Shared evidence,
   contradictory aliases, unknown identities and insufficient evidence abstain.
6. Duplicate raw observed labels remain ambiguous even when a duplicate's body
   was never emitted. Inferred/unsupported labels do not become destinations.
   Exact source-block fallback is allowed only when no page provenance exists,
   the raw logical identity is unique, and its first source block matches one
   final block. Contradictory or nondiscriminating provenance never falls back.

## Generic control matrix

| Domain | Cases | Required result |
|---|---|---|
| Special strings | comment, PI, CData | Original node classes/content/order; no hidden links |
| Exclusions | script/style/template/code/hidden, empty excluded tags | Opaque token boundaries; no nested or excluded links |
| Structural nodes | intervening br/img, nested partial em/strong | Same original ordered topology and IDs after wrapper removal |
| Source coordinates | references after comment/PI/CData/template/empty-code and nested ID ancestor | Original block text slice exactly equals occurrence |
| Ownership | nested TOC li, parent text before/after child | Every parent/child occurrence discovered exactly once |
| Overlap | turn-to-paragraph and typed phrase, URL containing section token | One logical occurrence per interval; no nested anchor |
| Identity projections | shared original number; unique side, ID or observed label | Shared evidence abstains; unique consistent evidence binds |
| Contradictions | unknown ID, ID/side disagreement, conflicting identity aliases | Missing/unbound; no HTML fallback |
| Print policy | duplicate raw labels, inferred label, spread/range, no raw label | Explicit ambiguity/missing; no scan-index guesses |

## Loop review and disposition

Prior recommendation: retain safe whole-inline moves and text-leaf fallback,
with exact binding. Authorized and implemented; repeated verification showed
that the edit domain and binding proof needed strengthening, not more isolated
exceptions. The mechanism now follows exact node-class semantics and unique
identity projection. These changes directly prevent hidden-text exposure and
wrong spread destinations while recovering nested TOC parent entries.

Alternative: browser DOM Range extraction or cloning a partial subtree would
increase dependencies and risk duplicate IDs without solving absent source
identity. Retain the current bounded static HTML mechanism. Structural topology
controls supplement visible-text/tag-count metrics. Finish this bounded task,
then parent owns independent acceptance; do not restart an unbounded repair loop.

Remaining limits: static HTML does not evaluate external CSS, layout or arbitrary
JavaScript visibility. Specialized CData discovery is intentionally unsupported;
its source bytes/node remain intact. Printed-page mapping remains unavailable
where raw/provenance evidence cannot distinguish identities. No natural-book
OCR or all-format quality claim follows from the observed reference workload.

## Verification

Focused resolver tests and development/Deathtrap adapter checks are recorded in
`output/story243-core-audit-dev.json` and
`output/story243-core-audit-deathtrap.json`; final exact counts and candidate
verification are reported to the parent after the last code edit. These are
resolver-only measurements, not complete OCR/pipeline performance.

Final bounded audit verification: **78 focused tests passed**, Ruff and
`git diff --check` clean. Development **24/24**, observed Deathtrap adapter
**627/627**, zero wrong targets. Both reports retain source text/markup and
provenance, pass repeated-run idempotence and opt-out parity. Driver integration
and fresh independent acceptance remain parent-owned.

## Independent acceptance and structural traversal completion

Independent acceptance confirmed page-identity projections and special-node/source
offset invariants, but found that empty nested blocks lacked a barrier. That
snapshot was explicitly not ready. Parent completed the structural traversal:
enter and exit events delimit every supported structural container regardless
of whether it contains text. Sentinels occupy no original source coordinates.
Heading definitions are not inherited as parent reference prose. This replaces
text-presence-based segmentation; no additional ordinary repair loop was run.

Independent matrix controls cover empty/nonempty block types, both parent TOC
occurrences around empty list/table/div containers, unchanged ordered DOM, source
offsets, and refusal to synthesize a URL across a table. Fresh111focused tests
pass; `output/story243-accepted-development.json` passes24/24 and
`output/story243-accepted-deathtrap.json` passes627/627 with zero wrong targets.
The original reviewer performs a bounded confirmation of the specific finding.
The earlier loop remains recorded as systemic-audit-needed, not retroactively
renamed a clean round. Parent acceptance includes this structural correction.

## Final source-authority composition correction

Final inspection initially flattened source anchor evidence. That erased the
owning filename, allowing an unrelated same-label source anchor to lend alias
authority to a changed live href. Filename scoping alone was insufficient:
same-file same-label occurrences could still borrow each other's evidence.
This is the same source-identity proof class established above, not new grammar.

The bounded correction passes original entries to inspection and preserves an
alias-only occurrence receipt: original href, final href, label, and a unique
anchor receipt key. Resolver-owned per-entry receipts accompany the serialized
marker; markers alone never authorize. Initial unverified markers are removed.
Repeated calls retain only exact receipt/source matches, then recompute alias
authority. Final inspection checks the actual anchor's receipt, owning entry's
original href/label, original ID map and unique actual destination. Ordinary
wrong-target checks remain active. No flattened alias API remains.

Loop review: adopt this explicit source identity chain rather than another
same-label heuristic. Bounds are one implementation pass, affected controls and
one parent-owned independent confirmation of the reproduced cases. No heldout,
new discovery grammar, or ordinary repair loop. Alias metadata changes the timed
resolver state, so the parent must refresh the final performance lineage.

Fresh correction checks: 287 resolver/integration/chapter/Marker controls and
21 evaluator controls pass; Ruff and diff whitespace checks pass. Development
benchmark `output/story243-alias-occurrence-development.json` passes 24/24,
exact recall 1.0, abstention accuracy 1.0, zero wrong targets and zero API cost.
This is correctness confirmation, not a performance adoption measurement.

Parent's bounded confirmation demonstrated that source identity also needs a
stable occurrence position: moving the receipt to an earlier same-label anchor,
or changing the authorized href to a semantically plausible target, could evade
label checking. Structural completion now stores each alias receipt's anchor
ordinal after enrichment. Final inspection enumerates the caller-declared
content boundary and requires every expected receipt at that exact position,
with unchanged marker, original href, actual href and label. Missing, moved or
changed expected receipts fail explicitly before semantic fallback. Chapter
declares its article; Office declares body excluding only its first generated
navigation element; Marker and unit fragments use their entire source body.

A generated discovered anchor cannot acquire source-ID alias authority on a
later call: both alias branches require the owning original source anchor.
Controls cover discovery adding anchors before an alias, same-file receipt
movement/deletion, a semantically plausible changed destination and alias-key
collisions on repeated generated references. This completes the existing
authority/occurrence invariant; no additional grammar or ordinary review loop.

One nonfrozen Marker integration input was test-wrong: its stamped output
included an original source anchor that its supplied raw page omitted, while
expecting original-ID rebinding. With parent approval, the raw synthetic page
now includes that same anchor. A separate negative control proves absence of
the owning original source anchor still abstains. Runtime authority remains
strict; no frozen golden or outside-owned answer changed.
