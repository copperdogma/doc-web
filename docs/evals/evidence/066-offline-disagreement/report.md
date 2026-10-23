# Attempt066 — Offline disagreement-to-review routing

**Preserve the observed low-confidence disagreement as a review warning.** On
saved Attempt065 outputs, this removes one unsafe clean answer at the cost of
one review. It does not add a correct semantic classification or qualify adoption.

| Saved three-chapter screen | Original frozen policy | Proposed offline policy |
| --- | --- | --- |
| Exact five-way labels |2/3|2/3|
| Defect called clean |1|0|
| Review routes |0|1|
| Determinate chapter outputs |3/3|2/3|
| Candidate decisions accepted |1/3|1/3|

Only change: if a valid native candidate response falls below the unchanged.8
confidence threshold, disagrees with a valid authoritative label, and would
otherwise use the existing `low_confidence` planner fallback, preserve both
labels/confidence in a warning and set the **advisory** route to review/uncertain.
No gold, caseID, source mutation, confidence tuning or generated answer is used
by this rule. Same-label low-confidence answers and all other existing gates
remain unchanged. The authoritative verdict and canonical artifacts are retained.

For doc01/ch003, source Ada3birth1876 versus extracted1881 establishes the
semantic defect. Saved Decider row_semantic_issue/confidence.42031 disagrees
with saved GPT conformant. Originalpolicy fell back clean; proposedpolicy asks
for review, preserving the correct warning without accepting it as a high-confidence
model verdict. Ch001 remains acceptedclean. Ch002 retains format_drift via
planner fallback; candidate was not called due a convention conflict.

## Method and limits

Executed in isolated codex/pplx-disagreement-offline-20261006 from owner base
19b30b1d0db4a7f3b2e31614ba9846dfdb93355c. Copied22nonsecret synthetic saved files
with exact source/hash/size manifest; original Attempt065 artifacts unchanged.
Loaded the frozen paid adapter, injected the original native responses, verified
original output equality, then applied the proposed pure offline policy. Network
socket creation is explicitly blocked during replay; no credentials read/injected.
Ten native receipt hashes verified;2candidate request/response replays exact;
4canonical artifact hashes unchanged. Original dictionaries not mutated.

This is a post-hoc exploratory policy replay over one exposed document,3chapters,
2nativecandidateanswers. It cannot establish fresh safety, review burden or
improvement on remaining15uniquechapters/allsecondrepeats. In particular, this
rule does not repair high-confidence mistakes, source omissions, absent/malformed
native responses, or contradictory planner conventions. Tests of constructed
boundary rows check policy behavior, not model accuracy. No full-driver integration
is claimed: no runtime module, prompt, schema, sourcegold or defaults changed.

## Verification and outcome

16boundary tests cover preserved warning/inputimmutability, low-confidence
agreement, exactthreshold.8, highconfidence, invalidconfidence/labels, skipped
and failedcalls, existingreview/highconfidence routes, and reverse disagreement.
Scoped Ruff and methodology/whitespace checks recorded at closure. Replay outputs
results.json; source custody input-manifest.json; executable
benchmarks/pplx-disagreement-offline/replay.py.

New providercalls0; spendUSD0; judgecalls0. Original five paid calls and their
USD.02588316 belong only to Attempt065 and are not counted again.

Recommendation: this rule is worth integrating **only into the default-off
experimental sidecar**, with a separate fresh held-out safety/utility evaluation
before adoption. Current request authorized the offline test only; integration,
provider calls, activation, commits and pushes remain unapplied.
