# Story 243 bounded performance and quality hillclimb

2026-10-05. Worker GPT-6.1 Sol, medium, user-requested. Parent GO followed
accepted core/evaluator/integration audits. No provider calls; synthetic
24-case development and the historical 627-occurrence Deathtrap adapter are
only tuning inputs. Heldout and Freeway remain unopened.

## Frozen experiment

`output/story243-performance-r1/baseline-freeze.json` freezes accepted resolver
helpers, actual imported package initializer/utilities, complete pipeline source
inventory, frozen evaluator, smoke recipe/inputs, and materialized development
corpora. Isolated baseline/candidate subprocess trees record every loaded project
module path/hash and parser/dependency module hashes. Ambient helper imports are
fatal. Natural-source hash remains the documented Deathtrap hash. The first
preparation failed before measurement because the package initializer requires
`common.utils`; retained under `output/story243-performance/`. The complete r1
snapshot includes that dependency.

Resolver boundary: `resolve_navigation` only, with corpus loading/deepcopy outside
the timer. Twenty pairs alternate AB then BA (ABBA sequence); one untimed worker
warmup precedes pairing. Retain every sample; compare median per-pair relative
gain, >=16/20 winning pairs, and no p95 regression. Speed adoption requires >=10%
median paired gain on each development corpus and unchanged on/off emitted DOM,
report evidence (excluding elapsed time), upstream inputs/provenance, recall and
wrong-target gates. Reports and serialized states are retained for parity.
Bounds: three revisions/two strategies, 60 active minutes, zero provider calls,
stop after two misses or negligible practical overhead. Full-driver smoke wall
time is a separate single-run boundary, never added to resolver speed gains.

## Profile and candidate 1

Accepted baseline passes synthetic24/24 and Deathtrap627/627. Five preliminary
warm samples: synthetic approximately8.2ms; Deathtrap approximately350ms.
Deathtrap profile: 1203BeautifulSoup constructions (401final bodies,401source
inventory,401ReferenceIndex source reads), cumulative0.310s of instrumented
0.986s resolver. This selects invocation-local, read-only parsed source reuse.
It retains parser, document scope and exact source bytes; no cross-call cache.

Candidate1 retains exact on/off output/report/provenance parity. Synthetic
median paired gain12.33%,17/20wins,p50 8.152→7.156ms,p95 9.279→8.469ms.
Deathtrap9.08%,20/20wins,p50 359.748→323.237ms,p95 369.605→342.590ms.
Rejected as a speed adoption because Deathtrap misses the10%gate.
Full raw samples/loaded paths: `candidate1-comparison.json` under the r1directory.
Baseline driver: `baseline-driver.json`,2087.782ms,exit0; source-only smoke,
no OCR/providers. Artifact root `output/runs/story243-perf-baseline-r1/`.

## Loop review after three substantive rounds

Aligned but correctness remains the priority. No prior performance recommendation
was pending; parent authorized freeze/profile then one small measured candidate.
Repeated parsing is demonstrated, but initial gain misses the predeclared gate.
A new parent adversarial probe shows accepted baseline repairs “See page3” to
heading “3Equipment” and “Return to section10” to “Return policy”. Baseline failures
are retained in `supplemental-baseline-failures.json`; these are runtime-wrong,
not golden changes. Do not use historical passing controls as universal proof.

Alternative mechanism: switch to lxml for speed. Beautiful Soup's
[parser documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#differences-between-parsers)
warns different parsers can produce different trees for invalid HTML. Reject that
broader dependency/DOM-semantics change here; parsed-tree reuse is lower risk.
Opportunity cost: additional cache structures/parser changes would displace final
independent verification for approximately36ms saved on the natural development
workload. Finish the small quality correction, measure combined candidate2 once,
then remove cache if the threshold still misses; no tuning to favorable timings.

Candidate2 restricts typed references anywhere in existing anchor labels to exact
kind/label heading evidence. Ranges, plurals and multiple typed destinations abstain;
ordinary first words cannot authorize headings. Valid hrefs/unique original-ID
aliases retain authority. Resolver and independent inspector share that candidate
policy. Nine supplemental controls cover wrong targets, valid typed prefixes,
plural/range/multiple abstention, authoritative links, and printed-page paragraphs
that coexist with numbered headings.120focused controls pass. Candidate2
measurement/result and final disposition follow below.

## Final measured decision

Retain candidate2 (two revisions/two strategies) and stop. Parent approved this
bounded disposition pending independent review/heldout. Twenty final pairs:

| Development workload | Baseline p50 | Candidate p50 | Median paired gain | Winning pairs | Baseline/candidate p95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Synthetic24controls | 8.229ms | 7.148ms | 11.64% | 19/20 | 8.716/7.822ms |
| Deathtrap627occurrences | 361.863ms | 321.978ms | 10.80% | 19/20 | 374.047/341.384ms |

**Near-threshold uncertainty:** candidate1's earlier Deathtrap gain was9.08%.
Final measured10.80% meets the predeclared rule, but does not establish an exact
or universal gain. Do not add synthetic/natural gains or different timing
boundaries. No quality tradeoff: both versions pass24/24 and627/627 development
checks, have zero wrong destinations on those declared controls, and produce
identical exact on/off DOM/report-state hashes. Supplemental controls separately
close both known baseline wrong-link defects without changing frozen answers.
120focused tests and Ruff pass. Cost/calls remain0; no cheaper provider possible.
Quality ceiling is bounded to inspected controls, not universal references.

Profile mechanism confirmed: candidate2 uses802instead of1203BeautifulSoup
constructions on Deathtrap. This is401removed redundant parses, with no parser
change or cross-call retention. Paired evidence:
`output/story243-performance-r1/candidate2-comparison.json`, alongside individual
baseline/candidate quality reports and exact on/off state JSON.
Final complete helper/harness/input/driver lineage:
`output/story243-performance-r1/performance-final-receipt.json`.
Supplemental corrected report samples:
`output/story243-performance-r1/candidate2-supplemental-quality.json`.

Full smoke driver observation: baseline2087.782ms; candidate2098.312ms, both exit0.
This is **not** a full-driver speed improvement and is not a paired performance
claim. Both runs emit8resolved,1missing,1ambiguous records; source pages1–5 remain
accounted for, printed12 and Romaniv resolve to their correct different logical
pages, duplicate22 abstains, and source IDs rebind. Manually inspected seven report
rows and emitted anchors across first three entries. Fourteen provenance rows are
unchanged except run IDs/timestamps (see `driver-parity.json`). Artifact paths:

- `output/runs/story243-perf-baseline-r1/output/html/navigation_resolution_report.json`
- `output/runs/story243-perf-candidate2-r1/output/html/navigation_resolution_report.json`
- `output/runs/story243-perf-candidate2-r1/output/html/provenance/blocks.jsonl`

Stop rationale: approximately40ms natural resolver benefit, initial near-threshold
variation, supplemental defects closed, zero cost floor. Extra complexity or
another favorable timing search is unwarranted. Independent heldout remains for
parent only, after complete final freeze; no heldout contents or Freeway executed
or opened during this work. No commits. Runtime helper ownership returns to parent.

## Instrumentation lineage reconciliation

The initial freeze records performance script
`5541c449121409626447a46da2ed1fc3082806b54a8770c17fc635f776aa3495`.
Both candidate1 and candidate2 paired runs used
`ab46097ac1eb6c53cf6d9a803c740c3753aba9833d3df52cf10d41f14053d1f8`
for both baseline and candidate processes. Exact reconstruction reproduces the
initial hash byte-for-byte: the only changes removed unused `import copy` and
added evaluate-only on/off serialized-state hashes plus their quality parity gate.
These occur outside timing. Resolver invoke boundary,20pair ABBA order, raw sample
collection and aggregation source are unchanged. The accepted evaluator remains
`f7ea46219f14cd4b435c6143f9241a7a758ba7c772305acff03d3c54d4e8242c`.
Preserve initial receipt rather than overwriting it; exact source/diff/protocol
receipt live in `baseline-performance-instrumentation.py`,
`instrumentation-drift.diff` and `instrumentation-lineage-receipt.json` under r1.
This reconciles two instrumentation epochs, not a claim they had identical hashes.

Final reviewer identified an independent-validator disagreement: a unique original
ID alias is authoritative to resolver, but a conflicting text heading could make
serialized inspection reject that preserved link. The validator/emitters correction
is underway in parent ownership. No additional optimization is authorized. After
parent GO, freeze corrected complete graph and perform one same-protocol paired
confirmation, retaining all earlier measurements and explaining exactly what changed.
Heldout and Freeway remain unopened; no runtime/helper/test edits in this followup.

The first validator-correction snapshot (`final-validator`) is retained but rejected
**before measurement**. Independent alias review reproduced cross-entry authority
leakage from globally flattened source links: a source link from another entry
could authorize a corrupt final destination. Parent is replacing that context with
filename-scoped source entries/aliases. `final-validator-rejection.json` explicitly
records zero timing samples and no confirmation started. Previous candidate2
measurements remain unchanged; no favorable timing search occurred. Wait for parent
final targeted confirmation before the one authorized paired run.

### Lineage loop review after three substantive rounds

Aligned, with final validator evidence still at risk. Prior recommendation was one
confirmation after a validator-only correction; that confirmation remains pending,
not completed/retried. Exact hash reconciliation and rejected-before-measurement
snapshot improve provenance without claiming a new speed result. Established
alternative to global source-label evidence is filename-scoped explicit target
binding, already justified by the design note's Sphinx cross-reference principles;
its namespace assumptions fit this same-document multi-entry bundle. Reuse that
comparison rather than changing parser/performance techniques. Parent's independent
source1/source2 adversarial confirmation is the discriminating local test. Additional
profiling/tuning would displace correctness confirmation and is not authorized.
Disposition: wait for corrected source-entry authority acceptance; then one fixed
protocol run, preserve all observations, and hand back lineage. No budget extension,
heldout access or runtime edits from this worker.

## Final corrected-semantics confirmation

Parent's targeted independent alias confirmation passed54controls and all prior
corruption reproductions. Final corrected `manual_navigation.py` is
`5c584fe228578b1129bf972a9ab1742cfd69ebcc54492ead68a81a87673eb46b`;
`reference_resolution.py` remains
`445599ed222a9887e8414642c7448eda8d1cec6fe056761c5161a02ab24b580d`.
Later corrections bind source evidence to owning entries and actual post-enrichment
anchor occurrences; missing/moved/changed expected receipts fail before fallback.
These changes intentionally affect resolver trace markup/state, so historical
baseline state hashes are not silently reused for final semantic parity.

After final GO, one—and only one—confirmation compared this exact corrected
resolver with source parse reuse against identical corrected code with ONLY that
cache removed. Isolated complete module trees, unchanged materialized development
corpora, evaluator and performance script were frozen before measurement. Cache-only
diff and both full graphs are retained under
`output/story243-performance-final-confirmation/`. This is a new matched-semantics
baseline, not a replacement/overwrite of the original accepted baseline.

| Final workload | Corrected uncached p50 | Corrected cached p50 | Median paired gain | Wins | Uncached/cached p95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Synthetic24controls | 8.282ms | 7.149ms | 14.03% | 19/20 | 9.088/8.022ms |
| Deathtrap627occurrences | 364.482ms | 321.910ms | 11.52% | 20/20 | 372.005/336.136ms |

Both20pair workloads meet the same >=10%/consistent-pair/no-p95-regression gate.
Both variants pass24/24 and627/627 quality checks, zero wrong targets, exact on/off
DOM/report-state parity, unchanged upstream/provenance, idempotence and opt-out
controls. Every raw sample and loaded module path/hash persists in
`final-cached-comparison.json`; immutable pre-run lineage is in
`final-confirmation-freeze.json`, appended conclusion in
`final-confirmation-result-receipt.json`. Working helper bytes still match the
measured cached tree. No retries, new optimization, heldout/Freeway access, provider
calls or runtime/helper/test edits occurred in this lineage followup.

Decision: retain the bounded source parse reuse after this matched final confirmation.
Earlier9.08%natural gain still shows near-threshold variation; claim the measured
11.52%final result rather than guaranteed precision or universal speed. Original
candidate2 and final corrected-semantics measurements remain separate and
nonadditive. Full-driver wall-time observations remain historical single observations
from the earlier semantic epoch; final driver/heldout validation belongs to parent.
Final performance evidence is complete; parent owns final independent heldout.
