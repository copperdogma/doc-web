# Decision models in Doc Web

Status note: 2026-10-01. This guide describes a bounded semantic decision
option. It does not change pipeline modules, model defaults, provider setup, or
runtime enablement.

## What the primitives mean

A decision model returns a typed judgment about supplied context. Consider it
when a question has a constrained answer space and the pipeline already owns the
relevant document text, candidates, and validation rules.

- **Choice** selects one value from explicit options, including `unknown` or
  `needs_review` when no safe answer is supported.
- **Noul** estimates the probability of a yes/no judgment; it has no separate
  confidence field and does not prove correctness for one item.
- **Score** rates a state along explicitly ordered rubric levels. It returns a
  probability-weighted mean of the level positions, the level distribution, and confidence.
  Define each level clearly; combine separate judgments or custom weights in
  code.

Example: after extraction, code could provide two policy passages and ask
whether they describe the same scope, a conflicting rule, or insufficient text.
The model sees only extracted text and its provenance. Deterministic code owns
date and arithmetic comparisons, source/page identity, candidate generation,
the explicit consistency policy, visual layout checks, artifact writes, and any
repair. A text decision cannot replace image geometry or validate a crop.

## Coverage, stale state, and fallback

Use a frozen, reviewed set of representative documents or synthetic excerpts.
Include clear agreement, true conflict, paraphrase, OCR noise, tabular and
multi-column extraction, qualified language, missing passages, ambiguous cases,
and deliberately stale evidence. Split by source document, not by excerpt,
before measuring. Hash source artifacts, normalized text, policy version,
candidates, and model request context.

Report candidate coverage separately from classification quality. Include
unknown/no-match choices, out-of-set responses, empty input, malformed output,
missing provenance, stale hashes, timeouts, provider failure, and budget caps.
These paths must retain the current authoritative planner result or route to
review. Never treat a timeout, omitted text, or disagreement as a clean result.
Calibrate thresholds on development data and report held-out per-class results,
abstention, false-clean and false-alarm rates, plus calibration. Confidence
concentration is not proof that a page is consistent.

## Compare the complete workflow

Run deterministic policy, the current language-model planner, and any decision
model candidate over identical frozen inputs. Compare document-level outcomes,
including extraction errors, layout guards, uncertainty handling, downstream
repairs, and operator review. Report class-level quality, false-clean defects,
coverage, fallback rate, latency distribution, total cost including fallback,
and whether the actual run remains safe. Price or speed per call alone does not
establish a better pipeline.

Preserve the existing [Story 233](stories/story-233-jev-consistency-classifier-evaluation.md)
and [Story 234](stories/story-234-jev-consistency-shadow-routing.md) verdicts.
Story 233 measured JEV 24/40 versus GPT-4.1 29/40; the predeclared cascade
reached 33/40 with 17 fallbacks, lower aggregate cost and median latency, but
three false-clean defects remained and p95 latency was worse. Story 234 kept the shadow opt-in:
layout guards and explicit uncertainty remain authoritative, and a JEV semantic
overcall was withheld from repair. The result is a conditional shadow candidate,
not planner replacement, broad production-quality proof, or default enablement.
Read those story reports and their frozen artifacts before proposing a change.

## Privacy and authority

Document images, scans, and extracted text may contain private material. Use
only existing owner-approved providers, source scopes, and credentials. Prefer
reviewed synthetic or public cases for new comparisons; do not send a private
document to a new provider without explicit owner permission. Preserve raw
requests, responses, hashes, and cost records under existing eval policies, and
avoid logging source payloads in routine runtime diagnostics. No decision model
may bypass deterministic geometry, layout safety, provenance, or review gates.

## Instructions and host setup

`AGENTS.md` is canonical. Claude Code 2.1.281+ loads it by default when the
built-in `agents-md` plugin is enabled. If a fresh session misses it, check
plugin state (`claude plugin enable
agents-md@builtin --json`) and the default `claude-md-or-agents-md` mode. After
the coordinated root-bridge removal, check that no private or ancestor
`CLAUDE.md` suppresses fallback. For a confirmed unsupported host, use a
temporary `@AGENTS.md` import.

## Provider status recorded on 2026-10-01

TypeSafe documents Choice, Noul, and Score in its [primitives guide](https://docs.typesafe.ai/primitives),
with typed judgments described in [System One](https://docs.typesafe.ai/concepts/system-one)
and answer concentration in its [confidence guide](https://docs.typesafe.ai/confidence).
Jev is text-only at this review date. OpenAI's [September 29 DevDay recap](https://openai.com/index/devday-2026-recap/)
announced the Decisions API, powered by Luna, for text and image input in
limited preview, with broader release planned in the coming days. This does
not verify Doc Web account access, API/SDK contracts, or pricing. Verify current
provider documentation before designing an integration; do not invent request
or response behavior from the announcement.
