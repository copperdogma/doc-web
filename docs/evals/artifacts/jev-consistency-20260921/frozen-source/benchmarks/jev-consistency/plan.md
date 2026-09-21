# JEV document consistency comparison — frozen plan 2026-09-21

Owner: Doc Web. Evaluation only, $0.60 hard total. Synthetic inputs exclusively.
20 cases: seven-column genealogy tables and titled equipment maintenance cards; two cases per five-way class per structure. Ten paired mutation patterns across two independently worded synthetic source documents, not twenty independent sources.
Labels and evidence receive independent review before any inference.

Maintained seam: plan_onward_document_consistency_v1 assigns conformant,
format_drift, row_semantic_issue, mixed, uncertain. This new projection supplies
explicit conventions rather than measuring convention generation or full repair
planning. GPT-4.1 is Story220's configured planner; GPT-5 is older Story219's.
Fresh GPT-4.1 narrow strict-schema projection is the comparator, not a claim that
this is a complete unchanged planner benchmark. Existing deterministic genealogy
chapter detector is also measured, via rendered seven-column HTML, with unsupported equipment documents marked
out-of-domain. An explicit generic structural-only baseline is reported separately.

One arm each: native jev-1.13.0 Choice; native gpt-4.1-2025-04-14 Chat Completions,
strict JSON schema, temperature 0, max_completion_tokens 160. Same state/class
instructions. No tuning, cache, hidden judge, private source, runtime change.
Two repetitions; serial independent requests. First case qualifies native
contract and adapter parity, then remaining cohort proceeds despite semantic misses.
Stop only invalid contracts/access or spend. No automatic retry; unknown spend
reserved conservatively and halt. Request upper bound charged before dispatch
and actual usage settled after each response. Exact synthetic requests/responses retained.

Workflow arm: each explicit uncertain JEV decision remains uncertain and routes to review. Other JEV decisions accepted when confidence>=0.8; otherwise perform a real serial GPT-4.1 fallback on that case.
Report classification accuracy, per-class recall/macro-F1, defect falsely called
clean, unnecessary defect flags, review/uncertain routing, and workflow cost/latency.
No absolute perfection or 50%-saving gate: choose relative quality/economics;
residual dangerous misses and sample uncertainty guide scoped adoption.
The deterministic baseline is not ground truth. Independent reviewer checks source
and golden, then important subject misses are classified with source evidence.
No paid rubric judge: independent source-based semantic review plus exact typed
label scorer satisfies separate semantic/structural proof on this closed vocabulary.
