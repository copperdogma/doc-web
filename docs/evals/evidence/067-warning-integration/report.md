# Attempt067 — Default-off sidecar warning integration

**Integrated the offline-validated disagreement-to-review rule into the
experimental Perplexity sidecar.** No runtime default was activated.

When a valid native answer is below the unchanged `.8` confidence threshold and
disagrees with the authoritative planner, the advisory sidecar emits
`shadow_status: uncertain`, `route: review`, `reason: low_confidence_disagreement`
and a warning containing both labels and confidence. It retains the authoritative
label. Low-confidence agreement retains the old planner fallback. Existing
source-completeness, uncertainty, layout, conflict, input and request limits keep
precedence. A high-confidence answer at or above.8 follows its previous path.

In the saved Ada3case, the warning is:

```json
{"candidate_status":"row_semantic_issue","authoritative_status":"conformant","confidence":0.4203098334772307}
```

The native answer and its probability/confidence/usage/cost are unchanged. Saved
chapter1 stays acceptedclean; chapter2 stays conflict-skip/plannerformat_drift;
chapter3 becomes review. This preserves the correct birthyear concern instead
of silently inheriting clean. It is not an accepted semantic correction.

## Scope and evidence

Isolated branch codex/pplx-warning-integration-20261006 at owner remote base
19b30b1d0db4a7f3b2e31614ba9846dfdb93355c. Carried only necessary nonsecret
experimental modules/tests and synthetic fixtures; original Attempt065/066
worktrees/manifests remain untouched. Copied prior native evidence has an input
hash/size manifest. Existing DOC_WEB_PPLX_SHADOW_EVAL and evidence switches stay
default-off; authoritative planner, repairs and Jev activation are unchanged.

62focused tests pass across candidate, transport, Jev, source evidence and full
planner. New integration regressions cover lowconfidence0/.42/.799999, agreement,
exactthreshold.8/highconfidence, reverse disagreement and input immutability;
existing tests cover missingkey/malformed/timeout and prior guard precedence.
Default-off dossier/prompt matches unmodified base exactly.

Saved native replay verifies10receipt hashes,2exactcandidate request/response
replays and4unchanged priorcanonical artifacts. Integrated sidecar produces the
expected warning with no new inference. A real `driver.py` recipe using fixed
mock native responses writes the warning sidecar while all4canonical hashes
match the sidecar-disabled run exactly. Authoritative conformance remains
conformant in that mock scenario. Operator artifact inspected at:

`output/runs/pplx-warning-integration-20261006/offline-warning-integration/03_plan_onward_document_consistency_v1/pplx_consistency_shadow_eval.json`

`integration-proof.json` retains exact commands/hashes and inspected warning.
Offline parent and driver subprocess explicitly block sockets. No credentials
loaded/copied/injected; no .env created, providercalls0/newspendUSD0. Scoped
Ruff, methodology build/check and whitespace checks pass at closure.

## Limits and recommendation

This verifies integration and preserves one observed warning on saved exposed
outputs. It supplies no fresh model-quality, calibration, privacy or production
safety evidence. The earlier exploratory replay changed falseclean1→0 and
reviews0→1, exactlabels2/3unchanged; those counts are not a new independent eval.
The rule does not cure highconfidence mistakes, missing/malformed candidate
answers or convention contradictions. Additional review is an intentional cost.

Keep this experimental integration disabled. A separately approved fresh held-out
safety/utility comparison is required before promotion; remaining15original
held-out chapters and allsecondrepeats are still unmeasured. No deployment,
commits or pushes. The full planner remains necessary; no whole-pipeline savings
claim or provider-retention approval follows from offline proof.
