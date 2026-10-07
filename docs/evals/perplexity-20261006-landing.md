# Perplexity campaign landing and historical custody

Decision: stop this evaluation campaign and retain the current model defaults.
The Perplexity sidecar and evidence hooks remain disabled unless their explicit
evaluation environment switches are enabled. Attempt067 is an experimental
warning integration, not evidence of adoption quality or a planner replacement.

## Historical attempts

The four independent attempt commits are ancestors of the combined landing.
Their paid receipts, source snapshots, manifests, and original verdicts are
unchanged. Historical final manifests describe those original commit trees;
the combined registry, graph, changelog and later sidecar intentionally differ.
Do not regenerate a historical manifest to imply that later code produced its
paid answers.

- Attempt064 native comparison: `3dbef2e8f7a1b7d5062627470f492e5b0e36f844`.
- Attempt065 early-stop runtime shadow: `a28a7385e6587d959aab0874d2d9870e446b9c97`.
- Attempt066 offline policy: `2b6321e9a4c5e5f16a16e7ed64c82da8833b4d32`.
- Attempt067 disabled warning integration: `8736d639c46232049ce1538349f025784c2580ea`.

The Attempt065 replay checks its frozen seventy source hashes and original
guard semantics. Run it from its original commit, not the combined landing:

```sh
git worktree add --detach /tmp/doc-web-attempt065 a28a7385e6587d959aab0874d2d9870e446b9c97
cd /tmp/doc-web-attempt065
/usr/local/bin/python3 docs/evals/evidence/065-pplx-shadow/replay.py
```

The retained campaign worktree is also at this exact commit. Its replay passed
at close-out: seventy source hashes, ten receipt hashes, two candidate guard
replays and exact canonical hashes; zero network calls. All 188, 33 and 99
entries in Attempt065/066/067 final manifests were verified directly against
those historical committed Git objects. Attempt064 replay in the combined
checkout reconciled 209 calls and 418 receipts, USD0.097180996, unknown zero.

## Combined validation

Focused pytest: 83 passed across Perplexity shadow/transport, Jev shadow,
evidence contract, planner, offline disagreement and initial campaign adapter.
Scoped Ruff and methodology graph check passed. The default-disabled test and
exact original dossier/prompt test passed. The integrated sidecar, hooks,
mock provider, warning verifier and driver campaign are byte-identical to
Attempt067, so its saved-response and real-driver offline artifact proof is
reused without overwriting frozen outputs or making another provider call.
Only the combined registry, changelog sequences and generated graph changed
at integration. Existing datetime.utcnow deprecation warnings remain.

No new inference, spend, credential copies, activation or default-model changes
were made during landing. Paid evidence remains synthetic; fresh independent
model-quality and broader pipeline adoption evidence remain unmeasured.
