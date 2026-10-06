# Agent staffing and event waits — Alignment 055 adoption

Date: 2026-10-06 (America/Edmonton)
Status: policy landed on owner remote main; final receipt landing is recorded
by the coordinator in Conductor Alignment 055.

## Source and isolated owner candidate

- Approved source: Conductor [Alignment 055](/Users/cam/Documents/Projects/conductor-align-055/docs/alignments/align-055-agent-staffing-and-event-waits.md).
- Source candidate: `/Users/cam/Documents/Projects/conductor-align-055`, branch
  `codex/align-055-conductor`, base `511655e8efdaba459427fb90b4f2815b7335bb34`.
- Source alignment SHA-256: `a26a407977c23f229cc85c81398191baddb14fed8e6deba36a5c39d2d6c2777a`.
- Owner base: `bb9d7c7accb68bdf309a9c26a98c7447640ff142`.
- Owner branch: `codex/align-055-doc-web`.
- Worktree: `/Users/cam/.codex/worktrees/align-055/doc-web`.

## Changed scope and local adaptation

Changed the short [AGENTS policy](../AGENTS.md), existing installed leaves
`loop-review, loop-verify, build-story, validate, finish-and-push, evaluate-model, triage, ideation, create-adr, setup-methodology`, [setup runbook](runbooks/setup-methodology.md),
[dated changelog](../CHANGELOG.md), and this receipt. Only missing decisions
were inserted into existing owner variants; whole skill files were not replaced.
The installer explicitly preserves approved owner variants instead of overwriting
their authority boundaries.

Strategic loop reviews resolve the strongest eligible runtime model and its
highest supported thinking level, distinguish requested from verified served
identity, and dispatch one bounded read-only reviewer when needed. Full-history
forks inherit configuration; explicit overrides use a supported compact no- or
partial-history packet. Ordinary staffing is proportional to risk and net
coordination benefit. Collection uses native completion events/message-aware
waits, preserving hard stops, failed/late-result handling, chat authorization
and continuation limits. Tiny-lane batching retains coverage and express fan-out.
Existing authorization covers the same bounded ideation/ADR packet.

Preserved the main thread's final score and closure authority, artifact/driver
verification for pipeline changes, lane/shard risk sizing, repo-local evaluation
protocol and progressive evidence gates. The operational staffing table changed;
product model guidelines, historical evidence and frozen subject/judge settings
were retained. Close-out uses a dated CalVer changelog entry, added for this scope.

The adaptation worker changed no product/model configuration, eval data, prompts,
judges, provider calls, story/state or primary-checkout files and performed no
staging, commits or pushes; Git close-out belongs to the coordinator.
No cost savings, idle-parent wake-up, provider identity or product-quality claim
is inferred from this documentation change.

## Validation and unchanged generated records

- `make skills-check`: exit 0; 29 canonical skills, compatibility links valid;
  Gemini command aliases are optional and absent in this checkout; no alias
  generation or check is applicable to these canonical body edits.
- `git diff --check`: exit 0.
- Scoped local Markdown-link/added-content inspection: source and local receipt
  targets resolve; dispatch, wait, authorization and preserved owner gates reviewed.
- Generated-record inspection: graph parses as JSON, and state/graph/story
  projection remain identical to the owner base. No compile is applicable
  because no story or methodology source/state changed.
- `docs/methodology/state.yaml`: SHA-256 `89d220fae3e2c3aa25a1fc86c6f784a3ff8d4c0fa9dd77e92aacc8df46075448`.
- `docs/methodology/graph.json`: SHA-256 `8c7a723a5e59119c8b29d2ddcedaea4b127a02c5d03507c890e9c0be61d68704`.
- `docs/stories.md`: SHA-256 `81ecaf4743368e3d118a16490e0c919f4dc58931a13ac04068335846adfeeea1`.

Checks cover this prose/skill candidate. Product suites, live pipelines and paid
evaluations were not applicable under the owner's proportional close-out policy.
Git integration and remote proof remain with the coordinator.

## Verified policy landing

Cam's 2026-10-06 approval covered this scoped commit and push. After the global
Conductor/11-owner preflight cleared, policy commit
`581e68dffa21d15eff80d70488e00fcf61e1cfd4` was pushed to
`origin/codex/align-055-doc-web` and fast-forwarded onto `origin/main`.
`git ls-remote origin refs/heads/main` verified that exact policy SHA after
landing. The primary checkout and its unrelated work were preserved.

This section records the observed policy landing. Its subsequent receipt-only
commit is recorded with final remote-main proof in Conductor Alignment 055's
consolidated owner ledger. Policy validation is reused because the checked leaf,
AGENTS and workflow inputs are unchanged; the receipt update receives scoped
content review and `git diff --check`. No product rerun is required.
