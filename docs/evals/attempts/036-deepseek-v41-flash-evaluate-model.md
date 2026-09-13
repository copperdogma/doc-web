# Attempt 036 — DeepSeek V4.1 Flash detector access screen

Date: 2026-09-12. Owner: Story207, spec:4/spec:8, C4.
Base: `5e2de62842f3e15313bdb74d9d41b84b40abec96` (fresh origin/main).
Branch: `codex/deepseek-v41-flash-eval-20260912`.
Worktree: `/Users/cam/.codex/worktrees/deepseek-v41-flash-20260912/doc-web`.

## Decision

**Defer: upstream capacity prevented native qualification.** The one approved
native synthetic strict-vision request returned HTTP429 in 737ms, with
`engine_overloaded` and `limit_source=upstream_provider_shared_pool` from
DeepInfra. No valid model output or usage was returned. This is provider shared
capacity evidence, not client overload, schema incompatibility or semantic failure.
No retry, route fallback, schema relaxation, parity or maintained fixture call
was made. The predeclared access-failure stop ended the bounded attempt.

Provider spend: **US$0.00 / $0.50**, based on one pre-inference HTTP429 without
usage; this is not a provider billing reconciliation. Reserved ceiling for that
request was $0.0106144; conservatively retain that amount as unreconciled
possible charge exposure. No judge or incumbent calls occurred.

## Contract and approval

User selected Scout070 item1. The pre-spend plan is appended to Story207.
Requested model `deepseek/deepseek-v4.1-flash`, canonical catalog identity
`deepseek/deepseek-v4.1-flash-20260910`, pinned `deepinfra/fp8`, no fallback,
strict `crop_regions`, require_parameters=true, low reasoning hidden, 1024
synthetic/16384 real output ceiling. Low is one frozen documented reasoning arm;
actual parameter acceptance remains unverified because the route was overloaded.
The existing owner adapter has a separate served-provider check (`DeepInfra`);
the campaign guard changes only routing order to the exact endpoint slug before
hashing/sending. Expected served ID was the requested public ID; no served ID
was returned, so exact served checkpoint identity remains unproven.

Current public endpoint evidence was saved from
https://openrouter.ai/api/v1/models/deepseek/deepseek-v4.1-flash/endpoints.
DeepInfra fp8 status -2; advertised $0.20/M input and $0.60/M output, strict
outputs and image input. Metadata alone does not qualify the request.
DeepInfra privacy https://docs.deepinfra.com/account/data-privacy disclaims
training and allows limited debugging/security logging; residual retention
uncertainty was approved for public/synthetic inputs only. A generated 128px
black square was the only payload. No source page, private or licensed input
was sent. No ZDR/data-collection filter was imposed.

The owner wrapper loaded only the temporary DOC_WEB_OPENROUTER_API_KEY from
ignored .env. Conductor's helper removed it immediately after the stop; presence
verification confirms absent. No other owner key was present or copied.

## Frozen owner lane and unmeasured scope

Maintained conservative-count prompt, crop_regions schema, image_crop_scorer.py,
user-authored image-crops goldens and 13 canonical b64 fixtures were unchanged.
Planned progression: strict synthetic native then owner parity, offline resolved
13-case matrix before any multi-case spend, Image011 grouping screen, full
13/13 >=.95 with zero errors, then conditional fresh Gemini control under cap.
The matrix and Promptfoo were not executed because qualification stopped first.
Campaign-only task retains the maintained 13 independent cases, one prompt,
Python assertions, no implicit paid judge and concurrency one. Manual source
review would supplement structural scoring. No semantic result exists to review.

Runtime incumbent remains Gemini 3 Flash; historical 13/13 .9703 is not a fresh
control. Astra's .980392 bounded result is current quality evidence but lacks
runtime safety eligibility. Separate GPT-5.5 page-context and C5 safety were
unselected. This attempt supports no model ranking or runtime change.

## Layered verdict

- Access: constrained by shared upstream capacity; callability unverified.
- Transport: blocked before native strict vision qualification; schema support unproven.
- Reliability: one operational capacity failure, no successful response; sustained reliability unmeasured.
- Capability: not measured, including Image011 and all 13 detector cases.
- Economics: $0 recorded inference spend, 737ms failed request; useful-output cost/latency unmeasured.
- Adoption: defer for detector; page-context not advanced.

Retry only after dated owner evidence demonstrates exact pinned route native
availability, or an explicit fresh bounded retry authorization. Catalog, price
or status metadata alone cannot establish the failed callability gate. Do not
repeat unchanged calls or broaden providers based on this record.

## Evidence and validation

Manifest: `docs/evals/evidence/036-deepseek-v41-flash-manifest.json`.
Durable ignored raw directory: `benchmarks/results/deepseek-v41-20260912/`.
Complete raw envelope and exact request body were saved before HTTP status
handling, along with endpoint catalog and spend ledger. Raw account identifier
stays in ignored storage; tracked evidence contains hashes and safe summary only.
Executed command from repo root:

```bash
/Users/cam/miniconda3/bin/python scripts/run_with_doc_web_env.py /Users/cam/miniconda3/bin/python benchmarks/scripts/deepseek_v41_probe.py native
```

Reproduction requires restored owner-authorized access and a new run/ledger identity.
The saved helper points at this completed run and must not be invoked unchanged.
No runtime/pipeline changes or eligibility advance: driver.py and broad runtime
suites were not run. Narrow offline adapter/guard verification and methodology
compile/check results are recorded in the story closeout. No commit/push/default
or primary-checkout modifications were made.

## Post-run guard hardening

The reused guard originally treated an HTTP error with no usage as zero cost.
Review identified that this overstates billing certainty. No further live call
occurred. The exact executed guard and pre-hardening ledger are retained in the
ignored raw directory. The guard now keeps no-usage error cost unresolved with
its reservation, and rejects replay of a closed campaign. The current ledger
records unknown charge (null), $0 reported spend and $0.0106144 conservative
exposure. Separate executed/current hashes prevent retrospective attribution.
Offline tests cover no-usage429 and closed-campaign refusal in addition to the
existing budget, nonfinite-usage and timeout checks. All 20 adapter/guard tests
passed after hardening; methodology compile/check and git diff --check passed.

## 2026-09-12 23:56 UTC — Authorized heartbeat1 follow-through

**Final detector verdict: do not adopt this frozen low-reasoning arm.** The
user's explicit six-hour finite retry authorization reopened access testing,
not semantic tuning. New immutable run `deepseek-v41-20260912-heartbeat1`
preserved initial artifacts and carried $0.0106144 unresolved charge exposure.
Local remaining cap was $0.4893856, original cumulative cap $0.50. Retry helper
enforces the authorized hard deadline 2026-09-13 23:54:06 UTC. The explicit
fresh authorization, not metadata alone, permitted this retry.

Endpoint metadata now reported status0 with unchanged price and canonical
checkpoint. Native strict synthetic vision and identical owner-adapter parity
both returned exact public model ID/DeepInfra, terminal stop, valid schema and
correct square bbox [.25,.25,.75,.75]. Native/parity outgoing bodies were equal.
Three pre-send body hashes were reconstructed successfully offline. The router
reports the public alias; catalog maps it to 20260910, no independent weight hash.

| Stage | Latency | Reported cost | Outcome |
| --- | ---: | ---: | --- |
| Native square |12516ms|$0.000526|Qualified|
| Owner parity square |12460ms|$0.000358368|Qualified|
| Promptfoo Image011 |67804ms|$0.0018894|0/1, score0.5551, zero errors|

Fresh reported total **$0.002773768**, plus initial unresolved exposure
$0.0106144 gives conservative cumulative **$0.013388168 / $0.50**. Current
three response costs came from usage.cost; initial429 remains unreconciled.
Promptfoo0.121.1 used --no-cache and concurrency1, exit100 is assertion failure.

Before the semantic call, offline preflight rendered all13 unique independent
single-user cases, one unchanged conservative-count prompt, one explicit
subject adapter, no paid judge, Python assertions and images<=2048 pixels.
Original canonical image bytes and actual outgoing Image011 bytes matched.
No subject output cache was used; provider prompt-prefix cache on the parity
call is usage evidence, not reused model output. No prompt/golden/scorer tuning.

### Source-backed mismatch

Visually inspected decoded Image011 against user-authored goldens and output.
The model correctly grouped seal/signatures and returned two regions, but
mislocalized both. Its logo box [.35,.03,.65,.14] ends halfway through the
actual logo; golden [.376863,.075455,.58,.231061] includes the complete artwork.
The combined box [.12,.72,.82,.94] misses upper seal and right-hand extent,
while extending below the expected region; golden is
[.119804,.686061,.876863,.896667]. These are coordinate accuracy errors, not
a grouping-count failure or source/golden defect. Taxonomy:
**prompt/pipeline-wrong -> model-wrong**, blocking this detector arm.
Structural score: count1.0 (2/2), meanIoU.453, minIoU.255, coverage.595, total.5551.
This fails the maintained single-case .70 assertion; full13 cannot clear the
predeclared13/13 gate. No new reasoning/budget arm, full suite or control run.

### Final layers and scope

Access recovered; tested strict native/adapter transport qualified. Observed
reliability is3/3 terminal success this wake plus the initial429 (3/4 across
the campaign), not sustained production reliability proof. Capability fails
Image011 localization; full13 and separate page-context remain unmeasured.
Economics are measured for these three calls; no fresh incumbent superiority
claim. Keep Gemini runtime and all existing safety defaults. The detector lane
is complete as a rejection; scheduled wakes must not rerun this semantic loss.
A revised checkpoint or independently justified owner contract change could
warrant a new proposal; capacity recovery alone no longer justifies this arm.

Credential helper removed only the injected DOC_WEB_OPENROUTER_API_KEY, and
absence was verified.20 offline guard/adapter tests passed fresh; methodology
compile/check, body/hash verification and diff check passed. No runtime/driver
change or runtime eligibility advance, so no driver run or broad suite.
New manifest: docs/evals/evidence/036-deepseek-v41-flash-heartbeat1-manifest.json.
Exact commands:

```bash
/Users/cam/miniconda3/bin/python scripts/run_with_doc_web_env.py /Users/cam/miniconda3/bin/python benchmarks/scripts/deepseek_v41_retry_probe.py native --run deepseek-v41-20260912-heartbeat1
/Users/cam/miniconda3/bin/python scripts/run_with_doc_web_env.py /Users/cam/miniconda3/bin/python benchmarks/scripts/deepseek_v41_retry_probe.py parity --run deepseek-v41-20260912-heartbeat1
# From benchmarks, Node24 on PATH:
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-deepseek-v41-heartbeat1.yaml --no-cache --filter-pattern Image011 --output results/deepseek-v41-20260912-heartbeat1/image011.json -j 1
```

Closed ledger prevents replay. Initial manifest/evidence stay unchanged.

## Authorized check-in — 2026-09-13

Scoped evidence/support landing authorized. Registry now leads with the final
semantic rejection and uses a new-subject-model trigger; initial capacity
history remains intact. An import-only Ruff cleanup preserves the exact
executed retry helper separately in the heartbeat manifest. No provider calls.
Story207 was already Done; its historical closure is unchanged, and this
attempt is complete without claiming broader runtime proof.

20260913 — authorized check-in validation: full make test passed 968 tests with four existing Pydantic warnings in 865.18s; make lint, direct campaign-helper Ruff, methodology compile/check, manifest hashes and git diff --check passed. No paid provider calls. Scoped evidence commit b0bf188; current-base branch landing authorized. Primary checkout and unrelated dirt preserved.
