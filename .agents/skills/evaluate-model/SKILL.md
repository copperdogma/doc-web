---
name: evaluate-model
description: Evaluate one or more AI models end to end for doc-web. Use for natural-language requests ranging from a broad new-model evaluation to a narrow task comparison, with or without exact slugs, providers, eval IDs, settings, or constraints. Resolve missing details, choose or validate a decision-bearing lane, qualify transport, run a fair bounded comparison, debug invalid attempts, preserve evidence, and give a scoped adoption verdict.
user-invocable: true
---

# /evaluate-model [natural-language evaluation brief]

> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md`
> and relevant decision records in `docs/decisions/`. If this work touches a known
> compromise in `docs/spec.md`, respect its limitation type and evolution path.
> If none apply, say so explicitly.

Evaluate the requested candidate set through defensible production-relevant
call shapes, not by changing model names and accepting the first harness result.

## Invocation Contract

Treat everything after `/evaluate-model` as an evaluation brief, not positional
arguments. A model name alone is sufficient, but the brief may instead be long,
informal, tightly scoped, or contain several candidates and explicit settings.
Extract and preserve any supplied:

- candidate names, model families, exact slugs, providers, or access paths
- target task, runtime stage, eval ID, fixture slice, or product decision
- incumbent or requested head-to-head comparison
- reasoning, thinking, output, schema, tool, sampling, or modality requirements
- cost, latency, deadline, concurrency, privacy, safety, or data constraints
- requested breadth, repeats, artifacts, or adoption standard
- execution intent such as evaluate/run/test/compare versus plan/design/recommend
- freshness intent such as reuse, rerun from scratch, reproduce/variance-check,
  or exercise the evaluation workflow fresh
- explicit exclusions and any later correction that supersedes earlier wording

Resolve omitted details from current first-party documentation, authenticated
access evidence, and repo truth. Do not ask the user to supply an eval ID, exact
slug, provider, incumbent, or routine settings when those can be discovered.
Do not silently discard a supplied constraint or reinterpret a narrow request as
a general model tournament. In a long or self-correcting brief, the latest clear
instruction wins; state any consequential interpretation before spending.

Unless explicitly limited to planning or read-only work, a request to evaluate,
run, benchmark, test, or compare authorizes the smallest bounded execution under
this skill's caps using configured doc-web credentials and payload-eligible
fixtures. It also authorizes the normal
repo-local story, adapter, artifact, registry, and methodology updates required
to make that evaluation valid and durable. A request to plan, design, scope, or
recommend remains read-only. Neither form authorizes copying credentials,
overriding fixture privacy, redefining source-backed goldens to help a model,
changing runtime defaults, committing, pushing, or broadening rollout.

Treat a clear request to rerun from scratch, reproduce prior evidence, measure
variance, or exercise the workflow fresh as **force-fresh intent** even when the
user does not use that label. A request only to inspect or audit existing
evidence remains read-only unless it also asks for fresh execution. Force-fresh
overrides only duplicate avoidance: retain and cite prior evidence, state the
verification objective, use new artifact names and uncached subject calls, and
report whether the result reproduces, weakens, or contradicts the prior result.
It does not expand scope or relax credential, privacy, spend, fairness, tuning,
retry, source-truth, default-change, commit, or rollout controls.

When force-fresh intent leaves the comparison shape unstated, match it to the
verification objective before spending. A workflow-acceptance or fresh
adoption-comparison request reruns the relevant incumbent and candidate on the
same frozen inputs. A candidate-variance or transport-reproduction request may
run candidate-only, but cannot make a contemporaneous superiority claim. If
existing uncommitted eval work could be confused with the new run, use distinct
attempt and artifact identities and record the full dirty state; use an isolated
worktree when that evidence cannot otherwise be separated. Never overwrite the
earlier artifacts.

For a read-only audit, do not make authenticated provider calls, run the
harness, create artifacts, or mutate adapters, registry, stories, or methodology
surfaces. Later execution sections become an audit checklist: inspect whether
the recorded evidence satisfied them and report gaps. Browse current public
documentation only when the brief requests current verification; otherwise
preserve the dates and limitations of the evidence being audited.

If neither the brief nor a stricter repo contract supplies a total budget, cap
all provider spend for the invocation at **US$5**, including access/contract
probes, candidate and incumbent calls, retries, and judge calls. Estimate and
start a cost ledger before the first paid call. This is a ceiling, not a target.
If the smallest valid decision-bearing run could exceed it, or pricing is too
uncertain to bound conservatively, stop and request approval for an explicit
higher cap before spending.

When scope is omitted, choose the single smallest high-leverage maintained
doc-web lane whose result could change a real decision. For a narrow request,
honor that surface and verify it is still decision-bearing. For an explicitly
broad, portfolio, or across-doc-web request, choose the smallest set of
materially distinct maintained decision surfaces that answers it, not every
historical eval. For multiple candidates, qualify each independently and compare
each against the same maintained incumbent per surface rather than creating
pairwise tournaments. Use provider-appropriate call shapes rather than forcing
identical but invalid parameters, and screen progressively so candidate count
does not multiply an expensive full matrix.

When a brief is rambling, consolidate it into a bounded interpretation, state
material assumptions, and proceed. Ask only when work needs new credentials or
authority, unapproved private payloads, spend materially beyond the repo's
normal bounded eval, or a product preference between genuinely different paths
that repo evidence cannot resolve. Also ask when explicit constraints conflict
materially and no safe interpretation preserves the user's intent. If a named
model cannot be identified or called reproducibly, or no maintained lane could
change a decision, return an evidence-backed defer/no-eval result instead of
inventing a benchmark.

Apply the repo's model discovery, eval triage, story creation, and eval
improvement workflows inside this command when needed. Do not require the user
to issue separate slash commands before `/evaluate-model` can do its job.

## Non-Negotiable Rule

Do not call a model bad when access, provider transport, the harness adapter,
output contract, parser, cleanup, scorer, or judge failed before valid subject
evidence was produced. Preserve those failures as operational evidence and keep
them separate from semantic capability.

## 1. Resolve the Brief, Candidates, and Owning Decision

This is an **owning-repo workflow**: for execution, doc-web owns the runtime,
credentials, fixtures, benchmark artifacts, registry, and adoption decision.

First turn the brief into a working scope:

1. Identify the requested candidate set without assuming the user's wording is
   an exact API slug. Resolve colloquial or launch names only when the mapping is
   unambiguous; never silently substitute a different model.
2. Separate explicit constraints from inferred defaults and note any tension
   between the request and a production requirement.
3. Inspect the registry, current runtime choices, open methodology state, and
   prior attempts.
4. Before creating work or spending, check whether a current, source-backed
   attempt already answers the same candidate/configuration/surface question.
   If no relevant model, provider, harness, prompt, scorer, golden, or runtime
   fact has changed and force-fresh intent is absent, return the existing scoped
   verdict and its evidence limits rather than manufacturing a rerun. When
   force-fresh applies, preserve the earlier attempt as prior evidence rather
   than current proof; do not copy its subject outputs or duplicate valid
   ownership artifacts.
5. Rank plausible lanes by ability to change a maintained decision, coverage of
   the model's relevant capabilities, evidence gap, and evaluation cost. Select
   one primary lane when scope was omitted. When breadth was explicit, select
   the minimum bounded portfolio covering materially different runtime
   decisions and state what is out of scope.
6. For an execution request, create or select the minimum coherent owning story
   set and write the decision contract before provider spend or mutation.
   Candidates sharing one decision surface share ownership; split only when
   runtime ownership or validation boundaries genuinely differ. For a read-only
   request, identify the would-be owner without changing it. Do this inside the
   command rather than handing the user another workflow step.

Read before spending tokens or changing eval surfaces:

- `AGENTS.md`, `docs/ideal.md`, relevant `docs/spec.md` constraints,
  `docs/methodology/state.yaml`, and `docs/methodology/graph.json`
- `docs/evals/README.md`, `docs/evals/registry.yaml`, and prior attempt notes
- candidate-relevant tasks, prompts, scorers, goldens, provider adapters,
  result artifacts, and runbooks under `docs/runbooks/`
- the repo-local instructions for discovery, eval triage, story creation, and
  eval improvement that this command may need to perform internally

Ensure any registry entry has the explicit story/category/compromise lineage
required by the eval README. Reuse suitable existing ownership; do not create a
story per model or duplicate process artifacts.

Record a decision contract that scales to one or several candidates:

- exact candidate/provider set and maintained incumbent configuration
- named runtime stage and eval ID for every selected surface that could change
- maintained prompt, fixtures, scorer/golden, current winning evidence, and SHA
- quality threshold and any hard promotion gate
- latency, cost, reliability, privacy, and safety limits
- exact adoption question and the evidence that could answer it
- freshness objective, evidence that may be reused, and whether a fresh
  head-to-head or candidate-only reproduction is required
- progressive stop conditions, including which later gate runs only after an
  earlier gate passes

For crop challengers, discover the current detector and page-context ladder from
the registry and runbooks. Do not hard-code fixture counts, scores, thresholds,
or incumbents from this skill. If no result could change a maintained decision,
record what was inspected, why no lane qualifies, and the smallest condition
that would make evaluation worthwhile; then stop and recommend no eval.

## 2. Refresh External and Local Truth

For execution, use current first-party provider documentation plus live
owner-run evidence. Do not rely on announcement copy, model-family memory, a
router catalog entry, or a PromptFoo alias alone. For a read-only audit, assess
the recorded source dates and call evidence without turning this section into
permission for a fresh authenticated probe.

Build a dated call-contract sheet for every candidate on the selected surfaces:

- exact model slug, aliases/tiers, availability, region, and access path
- native endpoint/API family and current SDK or PromptFoo support
- actual served-model/provider metadata, router fallback policy, and whether an
  intermediary enforces every required parameter
- required text/image/file/tool input shape and supported roles
- strict JSON Schema or structured-output support and required API flags
- reasoning/thinking controls and supported values
- output-token control and whether reasoning consumes that budget
- rejected sampling, stop, seed, penalty, or tool-choice parameters
- pricing, rate/concurrency limits, service tier, and availability guidance
- retention, training, ZDR, and payload eligibility

Use `python scripts/discover-models.py --check-new` only as catalog evidence; it
does not prove callability and may not cover every custom provider. For xAI,
Moonshot, routers, or other custom paths, verify the exact provider and model
directly. Check OpenRouter when it is the best practical supported access path,
but verify the served model and privacy policy rather than trusting listing
availability.

A provider marketing name, preview label, dated snapshot, and API slug may
differ. Record the mapping and do not claim a model was tested unless response
metadata or other provider evidence supports that exact identity. If several
tiers or snapshots plausibly match the brief, choose the production-relevant
one from repo and provider evidence or ask only when the choice changes the
product question materially.

## 3. Qualify Transport Before Scoring

For execution, use repo-scoped credentials through
`scripts/run_with_doc_web_env.py`. Never print or commit a key, and do not copy
one from another repo without explicit user authorization for that scope;
prefer doc-web's own ignored credential. Decide fixture payload eligibility
explicitly; `store: false` is not proof of ZDR or privacy approval. Start with
public, synthetic, or otherwise approved inputs. For a read-only audit, inspect
whether the record proves each ladder rung below; do not advance the ladder.

Advance through this ladder and retain sanitized request, response, status,
latency, usage, finish/stop reason, served-model metadata, and error evidence:

1. **Access probe** — prove the exact model is authorized and callable. Catalog
   visibility alone yields `access: unverified`.
2. **Native probe** — make the smallest direct provider call outside PromptFoo
   when practical and confirm what model/provider was actually served.
3. **Contract probe** — exercise the production requirement: images/files,
   strict schema, tools, long context, or another mandatory feature.
4. **Harness-parity probe** — send the same small case through the doc-web
   provider adapter/task and compare it with the native result.

Qualify the contract separately for each materially distinct surface. A schema
or adapter proven for one prompt/task does not qualify a later gate with a
different output shape. Do not score until that surface's required contract and
harness-parity probe pass. If a built-in provider sends the wrong API family,
multimodal shape, or task schema, repair or add the narrow adapter under
`benchmarks/providers/`, test it, and rerun parity.

HTTP success alone is not a valid subject response. Require the provider's
terminal success state, no provider error or incomplete condition, expected
served-model attribution, and complete output before scoring. Preserve status,
incomplete/error details, usage, and cost as operational evidence when this gate
fails.

PromptFoo result JSON may omit HTTP status/headers, served-model metadata,
finish reason, or partial-response details. Capture a sanitized sidecar when
needed; otherwise mark those provenance fields unverified rather than inventing
them.

Never persist authorization headers, API keys, signed URLs, or equivalent
secrets. Keep approved private inputs/outputs in the repo's protected or ignored
artifact location; committable evidence uses redacted excerpts, hashes, or safe
pointers.

When JSON is required, use strict schema enforcement when supported. Prompt-only
JSON is not equivalent. If only a weaker documented JSON mode exists, test and
label that limit; if strict structure is mandatory, classify the candidate as
incompatible rather than scoring malformed output as semantic quality. Ensure
the output budget can hold reasoning plus the schema before judging malformed
or incomplete output. A passing adapter unit test or parseable harness smoke
proves execution, not contract parity: inspect the actual provider-native schema
request, raw output, and served-model/status metadata.

## 4. Predeclare a Fair Configuration Budget

Write the candidate and configuration matrix before looking at scores:

- rerun the incumbent on its maintained configuration when fresh comparison is
  needed
- for a force-fresh head-to-head claim, rerun the incumbent on the same frozen
  inputs; for candidate-only reproduction, omit it to control cost and make no
  contemporaneous superiority claim
- run every challenger first at explicitly requested compatible settings, or at
  provider-recommended settings when the brief leaves them open, always with
  the required production contract
- predeclare the exact candidate/arm count plus transport-debug retry/repair
  cap; by default, allow at most two justified diagnostic or configuration arms
  beyond the candidates' recommended configurations across the evaluation
- predeclare the aggregate cost cap and update the ledger after every paid
  stage; stop before the next stage could exceed it
- give incumbent and challengers comparable opportunity while using each
  provider's valid controls; do not tune only whichever model is losing
- use a predeclared calibration slice where possible, then freeze one
  configuration before the decision-bearing comparison
- if variants share decision fixtures, label selection exploratory and require
  a predeclared repeat or independent confirmation before promotion
- do not expand tuning/debug budgets after seeing scores without explicit owner
  approval for a separately declared experiment
- keep prompt, fixtures, scorer, golden, and downstream cleanup fixed during the
  model comparison
- bypass subject-output cache for model/config changes, or prove the key covers
  exact model, provider, reasoning, schema, and route policy
- reuse frozen subject artifacts when only a scorer/golden is being corrected
- start PromptFoo at `-j 1`; raise concurrency only after provider limits are
  verified, and do not exceed the repo's normal `-j 3` without a separate
  production-throughput experiment

Do not launch the broad historical provider × prompt matrix by default. Filter
to the maintained incumbent/prompt and the predeclared candidate arms. When
several models were requested, use a shared cheap qualification/screening stage
before any candidate advances to the full decision-bearing gate.

A request-shape or documented schema-flag fix needed to obtain any valid answer
is transport repair. A change that can affect answer content—including prompt,
reasoning level, or output budget—becomes a declared configuration arm and its
exploratory score is not promotion evidence.

## 5. Run Progressively and Inspect Artifacts

Use the smallest run that answers the current question:

1. one public/synthetic native and harness-parity smoke
2. one representative PromptFoo case (`--filter-first-n 1` when appropriate)
3. the known failing or differentiating slice
4. the bounded maintained task with a frozen configuration
5. the next hard gate and required repeats only if the promotion condition passes

Use `--no-cache` for changed subject model/configuration, every subject arm
declared force-fresh, and final confirmation. PromptFoo exit code `100` means
test failures, not a harness crash; inspect the results before classifying it.

Between stages, open raw subject outputs and generated failure artifacts. For
crop mismatches, inspect decoded source images/contact sheets before changing a
golden or scorer. Stop weak or incompatible candidates before expensive later
gates, but retain every attempt.

When a progressive prerequisite stops a later materially distinct surface,
report that later capability as **not measured** and adoption as **not
advanced/defer under the declared ladder**. The stop is valid spend/adoption
evidence, but it is not semantic-quality evidence for an unrun surface.

## 6. Classify and Respond to Failures

For each non-pass, identify the producing stage first: subject request,
provider/router, adapter, parser, cleanup, scorer, judge, or golden. Then record
one primary class:

| Failure class | Required response |
| --- | --- |
| transient provider capacity, timeout, `5xx`, or capacity-coded `429` | Respect provider guidance/`Retry-After`; retry within the declared cap; retain all attempts and retry latency/cost. Persistent instability affects reliability, not semantic quality. |
| auth, quota, region, tier, plan, or policy | Correct only within existing authorization; otherwise mark access blocked/constrained and capability unmeasured. |
| client concurrency or rate-limit `429` | Inspect error body/headers, advertised limits, and concurrency. Client overload is harness/config evidence; plan limits are access/economics evidence. |
| wrong endpoint, API family, multimodal shape, or unsupported parameter | Recheck current docs, correct one contract variable, rerun native, then harness parity. |
| structured output not enforced | Enable supported schema/JSON controls and verify schema support before judging compliance. |
| truncation or thinking-token exhaustion | Inspect finish reason and usage; correct documented output/thinking controls and rerun the affected slice. |
| native succeeds but PromptFoo fails | Treat as adapter/harness incompatibility until disproved; inspect cache and served-model metadata. |
| parser, cleanup, judge, scorer, rubric, or golden mismatch | Isolate the stage and apply the repo-local eval-improvement workflow internally with source verification; reuse valid frozen subject artifacts where honest. |
| valid output contradicts source-backed expectation | Count as model-quality evidence after transport/config validity is proven. |
| refusal, content filter, or safety behavior | Classify separately as policy/safety compatibility for the target use. |

Classify `429` from provider error details, headers, account limits, and tested
concurrency. Change one causal variable at a time and never experiment until a
desired score appears.

When retries/provider failures matter, report both:

- **conditional semantic quality** on valid subject responses
- **end-to-end production result** including every failure, retry, latency, and
  cost

Do not erase initial failures by reporting only successful retries. Do not
charge judge, scorer, cleanup, or collector failures to the subject model.

## 7. Verify, Record, and Decide

Before recommending adoption:

- classify important mismatches against source evidence
- reject empty, malformed, partial, stale, or wrongly attributed result bundles
- compare quality, latency, cost, variance, success rate, retry overhead, and
  privacy/safety eligibility
- confirm the frozen winner is supported on the intended runtime path
- record exact sanitized commands, checked docs/date, model/provider IDs,
  requested and served parameters, fixture scope, repeats, cache state,
  concurrency, and sanitized transport evidence
- record a reproducible code identity. For a clean run, use the exact code SHA.
  For a dirty run after provider/eval repair, record the base SHA plus hashes of
  every relevant changed file or patch and ignored raw artifact; never imply the
  base SHA alone produced the result. Link the eventual commit containing the
  evaluated code when one exists
- when raw artifacts are ignored, preserve a compact tracked manifest with
  hashes, aggregate/case evidence needed for the verdict, and safe regeneration
  commands rather than relying only on local paths
- after an authorized execution, always update `docs/evals/registry.yaml` when
  an eval runs or is materially verified, including failed/inconclusive
  attempts and explicit lineage; add a numbered attempt note when the
  non-trivial result warrants one. In a read-only audit, report any needed
  correction without writing it
- update the owning story work log and regenerate methodology surfaces

Apply the repo-local eval-improvement workflow internally only after a valid
baseline needs prompt/pipeline versus scorer/golden diagnosis. Do not assume
every task requires an LLM judge; use the actual maintained assertions and
attribute any judge separately when present.

Do not change defaults because a model is newer, faster, or cheaper. It must
clear the maintained quality and operational gates for the exact surface. A
small isolated win does not justify a second-model router without a predeclared
breadth/value gate.

## Required Output

Return a compact evaluation record. Present one comparison row per selected
`(surface, candidate, resolved configuration)` where that makes the result
clear, followed by an adoption decision for each surface:

1. **Interpreted brief** — candidates, explicit constraints, inferred
   assumptions, and any unresolved ambiguity
2. **Decision and owner** — story set, eval IDs, chosen target surfaces,
   incumbents, adoption questions, why these lanes outranked plausible
   alternatives, and what remained out of scope
3. **External evidence** — checked sources/date, exact models and access paths,
   freshness objective, and whether prior evidence was freshly inspectable or
   record-derived
4. **Configuration matrix** — candidates, arms, rationale,
   cache/concurrency, and fairness
5. **Access** — available, constrained, blocked, or unverified per candidate
6. **Transport** — qualified, blocked, or inconclusive per candidate
7. **Reliability** — acceptable, degraded, failed, or not measured
8. **Capability** — better, equivalent, worse, or not measured
9. **Economics** — latency/cost/retry overhead, or not measured
10. **Adoption** — adopt, conditional adopt, do not adopt, or defer for the exact
   surface
11. **Artifacts and records** — result, attempt, registry, story, and source
    inspection evidence
12. **Limits and next step** — what remains unproven and the smallest honest
    follow-up

An access/transport block normally yields `capability: not measured` and
`adoption: defer`, unless a missing mandatory production feature makes the
candidate ineligible. A valid source-backed semantic loss may support `do not
adopt`. State which happened.

## Guardrails

- Do not score pre-response infrastructure failures as semantic misses.
- Do not weaken required image/schema/tool contracts merely to make a candidate
  pass.
- Do not alter goldens or scorers to rescue a model without source-backed
  inspection and the repo's consultation rules.
- Do not send private fixtures through a provider path without explicit payload
  eligibility.
- Do not silently borrow another repo's credential or trust `store: false` as a
  privacy policy.
- Do not commit, push, change runtime defaults, or broaden rollout without
  explicit authorization.
