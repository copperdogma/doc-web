# Anonymized structural observation — 2026-09-21

**Keep JEV shadow-only.** The layout guard
prevented a clean clearance on the fused-header case. The stronger finding is an
inconsistent planner policy: the full planner identified format drift but also
made that format a canonical/allowed variant in the conventions supplied to JEV.
Neither model can recover the deliberately ambiguous note lost by compaction.

## Frozen scope and results

One inherited real reviewed 48-row DOM structure, all fictional regenerated
content, six variants; five injected mutations. No original genealogy content,
private source excerpts or images sent. Case6 was excluded from conditional
classification **before calls** because the dossier drops its ambiguous note.
This is a small maintained-structure observation, not production traffic or six
independent documents. Full planner sees detector hints and authors conventions;
JEV sees sanitized compact evidence plus those conventions. This tests workflow
utility, not a controlled model-ranking claim. Planner-authored canonical_signals
can carry defect descriptions, so this is dependent checking, not independent
validation. It caught no additional defect versus the full planner in this sample.

| Case | Frozen expected | Full planner | Raw JEV | Actual shadow route/status |
|---|---|---|---|---|
| 1 generated base | conformant | conformant | conformant | JEV / conformant |
| 2 fragmented table | format_drift | format_drift | format_drift | low-confidence planner fallback / format_drift |
| 3 joined headings | format_drift | format_drift | format_drift | low-confidence planner fallback / format_drift |
| 4 fused child header | format_drift | format_drift | conformant | deterministic guard / uncertain review |
| 5 explicit child birth in DIED | row_semantic_issue | row_semantic_issue | row_semantic_issue | JEV / row_semantic_issue |
| 6 clipped ambiguous note | uncertain; compaction probe | conformant | conformant | JEV / conformant |

On the five visible-evidence cases: planner5/5 exact, raw JEV4/5 exact, shadow4/5
exact. Shadow's case4 abstention is an appropriate review action, not a repaired
classification. Binary clear-versus-review: planner5/5, rawJEV4/5, shadow5/5.
RawJEV called1/4 known defects clean; planner and guarded shadow called0/4 clean.
Across allsix, directJEV3/6, existing-planner fallback2/6, deterministic review1/6.
Within the five scored cases directJEV2/5. Allsix eligible/dispatched, no skips.

The unchanged detector flagged only case4. On its structural scope (clean1,
format2–4):2/4 binary correct,1/3 format defects detected; semantic case5 is outside
that detector's structural remit. This is a scoped binary comparison, not a
five-class detector score.

## Source-reviewed mismatches and limits

- Case4: planner's status is format_drift, but its emitted `pattern_4` canonical
  headers are fused and `allowed_variants` explicitly allows that fused header.
  JEV's clean result is consistent with this supplied policy, despite disagreeing
  with frozen gold. Root cause: contradictory upstream conventions versus desired
  document-wide format; not evidence of an isolated JEV reasoning failure. The
  unchanged deterministic layout guard catches it. Gold remains unchanged.
- Cases2–3: planner allows fragmentation/concatenated contexts in `allowed_variants`
  while prose conventions discourage them. Raw JEV classifications match gold but
  confidence .44/.77 triggers the frozen .8 fallback. No threshold tuning.
- Case6: fullHTML has an explicitly clipped/ambiguous DIED entry. Dossier carries
  neither that note nor a suspicious-row marker; source page profile is absent.
  Both outputs are clean; neither detects the missing context. This is one
  pipeline coverage failure (5/6 planner exact,4/6 raw/guarded shadow exact),
  excluded from conditional classifier accuracy. More capable routing alone
  cannot fix evidence the compact input removes.

## Cost, latency, custody

Seven calls:1 official OpenAI full planner,6 native TypeSafe JEV; zero retries,
transport failures, strict-contract failures or unknown usage. Observed exact
models: `gpt-4.1-2025-04-14` and `jev-1.13.0`. Allraw envelopes saved before parsing.
Fullplanner6000 output cap, SDK retries0, explicit official base URL; JEV unchanged
native2second deadline. Reserved upperbound$0.108506 within$0.15 cap.

- Fullplanner known cost$0.033562; latency31,396.23ms.
- JEV known cost$0.00030639; median233.84ms; six serial calls1,540.77ms total.
- Combined known cost **$0.03386839**, unknown reservation$0.
- Added shadow cost is0.91% of fullplanner cost; no savings claimed.

Allfour authoritative output JSON hashes remained byte-for-byte unchanged after
shadow. Raw requests/responses, ledger, plan/conformance and both sidecars reside
in `run/`. Frozen source/request/gold manifest is `freeze.json`; independent root
pre-call approval is `review.json`.

## Verdict and next evidence

Retain shadow default-off and deterministic layout guard. Before promoting this
routing path, address/measure the planner's contradictory convention export and
loss of ambiguous evidence; keep original source review available when compact
state is insufficient. Do not lower confidence thresholds based on this sample.
This observation supports safe advisory isolation, not production quality,
whole-document coverage or savings. No runtime policy edits, primary checkout
changes or private-document transmissions occurred.

Provider-free harness verification: `/usr/local/bin/pytest
benchmarks/jev-observation/test_run.py -q` →5passed; targeted Ruff clean. Existing
runtime26tests and realdriver r4 evidence reused because runtime code unchanged.
