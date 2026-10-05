# Attempt 059 — reference-resolution: explicit final-HTML links

**Eval:** reference-resolution
**Date:** 2026-10-05
**Worker model:** GPT-6.1 Sol, medium (user request)
**Subject:** deterministic final HTML resolver; no pipeline model calls
**Lineage:** Story243; spec:3/6/7; no active compromise deletion
**Git base:** 3bba309f43cde45eaf0140bab45ecb1966176600

## Baseline and hypothesis

The donor resolver repairs source-authored anchors but discovers no plain
references. Fresh probe: “See page12”, “section3” and an HTTP URL emit zero
records/links. Extend the same final-ID seam with exact target indexing,
conservative source-supported discovery and explicit abstention.

Expected user benefit: follow explicit references/contents/index entries while
retaining source text and avoiding plausible wrong targets. Printed-page labels
must not be conflated with PDF/logical scan indexes.

## Frozen decision contract

Quality gates: no wrong destinations on supported explicit controls, exact
visible-text/markup/provenance preservation, no opt-out discovery/API calls,
correct abstention and full report coverage. A live target can still be wrong.

Two authored fixture splits and natural-document workloads. Development uses
Deathtrap Dungeon; Freeway Fighter reserved unopened until final candidate
freeze. Historical book runs have source health warnings and are comparison
workloads, not source-verified whole-book goldens.

Measure post-loop-verify baseline separately from pre-build functional probe.
Record all timing samples and corpus/code hashes. Resolver and driver timing
boundaries remain separate; report p50/p95, calls and known cost explicitly.

Hillclimb: maximum3revisions/two strategies,60 active minutes,zero paid pipeline
calls,one independent final confirmation. Adopt a speed candidate only at >=10%
paired median improvement with consistent samples and no quality regression;
otherwise retain simpler code. Stop after two non-improving attempts or
negligible remaining practical overhead. Never modify goldens for a better score.
Loop-review after3substantive rounds/30active minutes, earlier for obstacles.

## Work log

20261005 — Planning: inspected existing source-ID/provenance seams and donor
resolver;22donor controls independently pass. Copied immutable donor snapshot.
Created Story243 and frozen-fixture task before runtime implementation.
User added TOC/index and historical FF corpus; both included within this same
reference/validation boundary. Further model reasoning and whole OCR are excluded.

## Verification before optimization

SOL6.1 medium workers built the core, integration and evaluator with individual
goals. The ordinary strict loop-verify exposed material errors and stopped under
its systemic-audit rule. A bounded DOM/page-identity audit, structural traversal
completion and independent confirmation closed reported defects. An independent
evaluator review rejected corrupt-output probes and found no remaining issue.
Full history is retained in `docs/notes/reference-resolution-design.md` and
`docs/notes/story243-core-invariant-audit.md`.

Post-verification calibration:111focused core controls,23integration controls,
21evaluator controls; development24/24 and Deathtrap627/627 pass with zero wrong
targets and source/report/opt-out gates. These calibration timings are not the
paired performance result. Holdout remains unexecuted at this point.

Broader suite:1243passed,1skipped,10fresh-install packaging cases deselected;
three unrelated guard isolation failures pass alone. Full attempt also encounters
absent saved crop-review responses. Logs retain the limits; no full-suite green
claim. No fixtures are fabricated.

## Optimization record

Accepted-source freeze and complete import isolation are recorded under
`output/story243-performance-r1/`. An earlier isolated-tree preparation omitted
common.utils and failed before measurement; it is retained separately, not
counted as a baseline. Two strategies are in bounds: invocation-local parsed-page
reuse and stricter typed evidence for existing-link repairs. Supplemental semantic
probes expose baseline false repairs separately from unchanged frozen answers.
The original combined candidate met its paired gates, but final validation
review then exposed alias-authority composition defects. A bounded structural
audit bound authority to its owning entry and final anchor occurrence; independent
confirmation closed every reported repro. Rejected snapshots and their limits
remain in the design/performance notes. No heldout material was opened for repairs.

Final confirmation compares the same corrected semantics with and without only
the invocation-local source parse cache. Twenty alternating pairs, one batch:

| Workload | Uncached p50 | Cached p50 | Median paired gain | Winning pairs |
| --- | ---: | ---: | ---: | ---: |
| Synthetic development (24 cases) | 8.282 ms | 7.149 ms | 14.03% | 19/20 |
| Deathtrap (627 admitted occurrences) | 364.482 ms | 321.910 ms | 11.52% | 20/20 |

Both p95 values improve. Exact on/off DOM/report-state hashes match, and all
quality/source gates pass. Retain the cache and stop: roughly 43 ms saved on
the natural development workload, modest absolute overhead, zero provider cost,
and no justification for further complexity. Earlier epochs are not additive.
No full-driver improvement is claimed (earlier single smoke observations were
2087.782 ms uncached and 2098.312 ms cached). Final evidence is under
`output/story243-performance-final-confirmation/`; see
`docs/notes/story243-performance.md` for all samples, rejected attempts and lineage.

## Single independent confirmation

Final freeze `output/story243-candidate-freeze.json`, SHA256
`e89ebbfc5f738a7e6ed97f554a89fb5d4e11de3f38669bbd659ae38b6f5c3ad2`,
binds 273 runtime/configuration sources, evaluator, corpora and natural source.
The independently executed final reserved runs both pass without edits or tuning:

- Synthetic: 12/12 cases, exact recall 1.0, zero wrong targets, correct abstention.
  `output/story243-heldout-final.json`; descriptive warm mean 3.460279 ms.
- Freeway Fighter: 491/491 admitted literal occurrences over 380 observed sections,
  exact recall 1.0 and zero wrong targets within that scored set.
  `output/story243-freeway-final.json`; descriptive warm mean 248.460146 ms.
- Both: full text/markup, provenance, idempotence, opt-out and audit gates pass;
  no invalid final hrefs; zero API calls/$0 for the resolver only.

Freeway has 520 observed source anchors: 29 forms are excluded by the frozen
adapter, including some parenthesized phrases. Its report contains 557 resolved
discoveries; 66 are outside the admitted source-anchor oracle and are not silently
counted as correct. Natural abstention is unmeasured because no negative cases
were admitted. Existing OCR health warnings and adapter-supplied section metadata
prevent whole-book completeness, OCR or universal navigation-accuracy claims.
Ten actual final records were inspected, including offset31→source6, Romanvi,
section18 wrong-live-target repair, inferred32 missing, duplicate19 ambiguous,
and five Freeway section destinations. All bound hashes still match after execution.

## Conclusion

Succeeded within the declared explicit-reference scope. Optional enrichment
improves navigation without provider cost; uncertainty stays visible and source
identity is retained. Quality, speed and cost limits remain separate. Final real
driver on/off artifacts and parent inspection are recorded in
`docs/notes/story243-validation.md`. No format graduation, upstream OCR repair,
external URL availability check or provider-model promotion is claimed.
