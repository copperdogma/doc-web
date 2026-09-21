# Story234 evidence-contract fixes and bounded recheck

**The workflow now contains the two observed failures safely.** Unknown event
notes remain visible, missing source context remains uncertain, and conflicting
canonical policy is diagnosed instead of passed to JEV. This does **not** mean
the model stopped generating contradictory policy: it still did so in this recheck.
Keep JEV opt-in and advisory; no threshold tuning or additional rerun followed.

## What changed

- Planner instructions distinguish observed anomalies from desired conventions.
  A narrow structural check diagnoses canonical fused child headers when the raw
  finding itself calls the same header a defect. Raw policy stays inspectable;
  shadow skips it with `conflicting_conventions`, retaining current planner output.
- A genuinely accepted-looking fused policy versus the sole deterministic fused
  warning becomes explicit uncertain review, with empty repair issues and retained
  detector evidence. This avoids blanket normalization or automatic variant repair.
- Otherwise unclassified non-date DIED prose survives in bounded raw examples,
  separately from proven child-note signals. Missing source pages and compacted
  profile counts remain explicit. Ordinary dates/deaths/placeholders are excluded.
- Explicit planner uncertainty survives normalization. Missing-source/unclassified
  context and omitted unresolved findings cannot silently become conformant.
  Dependent JEV output cannot clear authoritative uncertainty, but raw JEV labels
  and confidence remain available for comparison. Default repair excludes uncertain.

## Same-sample recheck

Original six HTML samples and original gold are unchanged. They retain one real
48-row DOM structure with regenerated fictional text and five injected mutations;
this is not production traffic. Revised dossier, prompt, code and policies are
separately identified by `freeze.json`. The original five conditional cases remain
the direct before/after metric. Case6's historical exclusion flag is untouched;
its newly visible ambiguity is evaluated separately, plus descriptive all-six
pipeline results. No gold is sent to either provider.

| Case | Gold | Raw planner / normalized | Raw JEV | Routed shadow |
|---|---|---|---|---|
| 1 base | conformant | conformant / conformant | conformant (.89) | conformant, direct |
| 2 fragmented | format_drift | format_drift / format_drift | conformant (.32) | uncertain, layout review |
| 3 joined headings | format_drift | format_drift / format_drift | format_drift (.60) | format_drift, confidence fallback |
| 4 fused header | format_drift | format_drift / format_drift | not called | format_drift, convention conflict fallback |
| 5 explicit child birth | row_semantic_issue | row_semantic_issue / row_semantic_issue | row_semantic_issue (.92) | row_semantic_issue, direct |
| 6 ambiguous event | uncertain | uncertain / uncertain | row_semantic_issue (.42) | uncertain, authoritative review |

Original five: raw planner and normalized pipeline5/5; raw JEV3correct,1wrong,
1skipped (3/4 conditional among called;4/5 coverage); routed shadow4/5 exact plus
one appropriate review. Prior raw JEV was4/5 with5/5 call coverage. On the four
mutually called cases, raw JEV changed4/4→3/4; **no raw-model improvement claim**.
Case4 previously clean under inconsistent policy is now skipped, not magically
corrected by JEV. Raw JEV still called case2 clean; unchanged layout guard caught it.

Case6: model/pipeline now recognize insufficient evidence; JEV overcalls a semantic
defect, but authoritative uncertainty wins the routed decision. Descriptive allsix:
planner6/6 exact, shadow5/6 exact+one safe review; rawJEV3/5 among called,1skip.
Allsix clear-versus-review actions match the predeclared intent. DirectJEV2/6;
one low-confidence fallback,one conflict fallback,two reviews. No known defect is
routed clean. Prior compaction had routed case6 clean; that specific failure is gone.

The unchanged binary detector still only flags case4: on clean1+format2–4,2/4
correct and1/3format defects detected. Semantic5/unknown6 are outside its intended
structural scope. The added guards are not described as improved base-detector
recall.

## Source-reviewed remaining limitations

The revised full planner still creates a fused-header pattern while assigning its
chapter format_drift. The exact contradiction guard now records it and prevents
that inconsistent policy from reaching JEV; prompt-only correction did not suffice.
The main family's allowed multiple tables versus fragment evidence can still be
ambiguous. JEV's fragmented clean proposal and semantic overcall on the ambiguous
note are retained as misses. Do not tune against this tiny sample.

This remains dependent checking: the planner authors conventions and sees detector
hints; JEV sees sanitized compact evidence plus those conventions, whose canonical
signals can carry inferred descriptions. Results measure workflow behavior, not
independent verification or controlled model superiority. Source context is
extracted HTML, not original-image verification. No private text was transmitted.

## Cost, latency and custody

Six calls:1 exact`gpt-4.1-2025-04-14`,5 exact`jev-1.13.0`; zero retries, transport
or strict-parser failures, unknown usage$0. Full reservation bound$0.115796;
actually dispatched reservation$0.113108 within$0.15cap.

- Planner$0.029740;29,176.34ms.
- JEV$0.000289128; median262.92ms, five serial calls1,319.72ms.
- **Total$0.030029128**; shadow added0.97% to planner cost, not savings.

Allfour authoritative artifacts stayed byte-for-byte unchanged during shadow.
`run/` contains all six raw requests/responses, reservations, normalized output and
shadow sidecars. Historical222Story233 and38prior-observation artifacts verified
unchanged. The historical code identities belong to their recorded commit; this
recheck explicitly tests changed runtime/prompt identities.

## Validation and status

Independent review CLEAR after two finite review fixes. Runtime/evidence tests32
passed; affected repair-consumer tests34passed; targeted Ruff and whitespace clean.
Driver `output/runs/story234-evidence-contract-cohort-r5` ran disabled/enabled with
network blocked and mock providers. Inspection verifies case6notecount1/missingpage6,
uncertain status/no repair issues survives stamped report; conflicting policy has
zero dispatch; authoritative outputs are invariant. Safe copies are in `offline/`.
Original clean disabled/enabled/failure driver path also passed earlier in this
follow-through. No provider test was repeated after these frozen results.

Implemented and validated; runtime remains default-off/advisory. This closes the
approved fixes as failure containment and evidence visibility, not perfect planner
policy generation. Further expansion should require broader independently reviewed
policy/evidence coverage, not lowering the current guards.
