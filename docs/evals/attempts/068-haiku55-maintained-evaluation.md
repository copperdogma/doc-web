# Attempt068 — Haiku 5.5 maintained task value sweep

Date 2026-10-07; Story249; Scout089 selected item3. Base cff6771a01ba202b8eb39e13a604a932708e2278, branch codex/haiku55-eval-20261007. USD10 hard inclusive cap. Existing owner keys accessed only via normal wrapper and explicit primary .env path. Public Onward/user-reviewed crops, public LOC handwriting, synthetic consistency only. No private sources, default changes, commits or pushes.

Predeclared arms: recommended medium/adaptive, low/disabled, high/adaptive. Adequate output cap4096 crop/safety,16384OCR,1024classification. Calibration: Image011 detector; page122001 and012001 safety; Barney handwriting; first five consistency cases. Every declared arm is tried on calibration regardless of another arm's semantic miss. Select the cheapest source-valid arm satisfying each gate, then freeze. Detector confirmation full13 plus repeated Image011; independent safety source-adjudicated22 with old labels separately; OCR Alverson plus repeated Barney if calibration>=.99. Consistency remaining15 then second repetition20 for frozen arm, compare fresh GPT4.1 and actual maintained Jev confidence<.8/nonuncertain fallback if owner eligibility allows. Calibration reuse is exploratory; confirmation separates selection. Semantic rejection stops that arm/lane, independent tasks continue.

Gates: detector average>=.95/pass>=.90 plus source-visible completeness; safety zero false-safe and22/22; handwriting>=.99 source fidelity; consistency compare five-class accuracy/macroF1/dangerous false-clean and full workflow cost/latency. No semantic tuning, source/golden/scorer changes. Frozen maintained prompts, native strict integer geometry and strict safety/classification schema; actualdriver OCR system/user/image/sanitizer. No paid rubric on closed source-backed tasks, independent source inspection supplements deterministic scoring, as maintained owner protocol permits.

Spend reservation: candidate image call oneimage26K input+4096out=.004648, twoimage46K+.002048=.006648; OCR26K+.008192=.010792. Fresh GPT safety46K*5+2048*30=.29144 up to22=$6.41168; Gemini detector13*.062152=$.808; OCRtwo*.08094=$.162. Classification controls40*(6K*2+160*8)/1M=$.5312 plus fallback≤same; candidate classification≤.001112 each. Full bound<USD9 with operational reserve>USD1. Cross-process lock surrounds dispatch/ledger; unknown charges remain reserved, two explicit operational recoveries, no automatic price/identity fallback; serial no-cache. A valid failure stops full confirmations so actual spend may be much lower.

Current provider source: https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost confirms medium default Haiku5.5, max_tokens includes thinking. Release https://www.anthropic.com/claude-haiku-5-5 identifies claude-haiku-5-5. Exact native call and parameter acceptance will qualify owner access, not documentation alone. Owner privacy retention uncertainty disclosed by selected proposal; public/synthetic only.

## Measured result and recommendation

**Retain current detector, safety, OCR and full consistency planner.** Low effort
is the cheapest measured Haiku classifier setting, but does not establish a
quality-preserving replacement. Thinking improves the detector's grouping yet
still leaves visible source clipping; higher effort does not solve the safety
false-safe or handwriting fidelity loss.

| Task | Haiku arms | Fresh maintained control | Decision |
|---|---|---|---|
| Image011 detector | medium .5435 (3 regions); low geometry invalid; high .9242 (2 regions) but logo/seal clipping | Gemini3Flash .9826, source-complete grouping | Reject tested arms; full13 unmeasured |
| Independent safety2 differentiators | medium/low/high1/2 each; all false-safe amputated seal | GPT5.5 2/2 | Reject tested arms; full22 unmeasured |
| Actualdriver Barney OCR | medium .959162/7.672s/$.0009911; low .945640/3.457s/$.000422; high .942693/9.642s/$.0012986 | Gemini3.7 .980617/7.482s/$.0073575 | All<.99; reject tested Haiku; Alverson unmeasured |
| Synthetic status classifier | frozenlow25/40,macroF1.58745,3false-clean,median1.1535s,p951.371s,$.0041735 | GPT4.1 29/40,macroF1.71169,4false-clean,median.8575s,p951.976s,$.043392 | 90.38% cheaper but lower accuracy/34.52% slower median; no quality-preserving adoption established |

Classifier allthree thinking arms4/5 on fixedfirstfivecalibration, low selected by
cost before35confirmation. Confirmation21/35, with matchedGPT26/35 (firstfive
excluded symmetrically);20unique cases from2source documents, two repetitions.
Firstfive omit mixed/uncertain, so this is a bounded exploratory configuration
screen, not a universal best-thinking claim. Low has one fewer false-clean
format defect but misses more layout/ambiguity distinctions overall. No semantic
row defect was falsely clean in either arm. No eligible runtime-observable
routing rule or calibrated Haiku confidence exists to support a mixed-model
replacement. Fullplanner convention generation, rationale and repair remain
unmeasured. FreshJev/cascade unmeasured under missingownerkey/custody boundary;
prior cascade evidence is contextual, not a fresh measured comparator.

## Contract, recovery, spend and evidence

Owner directAPI exact claude-haiku-5-5 is callable and image/text/strictschema
qualified with allthree thinking configurations accepted. Detector local bounds
reject low's out-of-range integer response despite grammarinteger acceptance; raw intact,
no semantic score. Strictnative schemas enforce supported types; local geometry
validates range/order/length. Safety and classifier schemas independently
qualified. ActualdriverOCR stamps page_html_v1; eval-only startup supplies native
Haiku envelope preserving actualowner system/user/image/sanitizer, no runtime
client change. FreshGoogle/OpenAI controls retain owner settings.

InitialOCR startup mistakenly imported AnthropicClient instead of actual
AnthropicVisionClient. Guard installed, but patch failed and unmodifiedclient
sent deprecatedtemperature; HTTP400 retained with conservativeunknown reserve
$.011442. Fixed eval-only startup and used newrepairidentity; initialbadrequest
is harness/adapter compatibility, not modelquality. No failed responsehidden,
no paidsemantic retry, no model/provider fallback. AllHTTP dispatches serialized
by the cross-process lock despite independent parent processes. Duplicate
protection and unknownreservation tested offline.

**110dispatches;109unique successfulresponseIDs;$.136542 settled usage-priced,
$.011442 conservative unknown exposure;$.147984 total maximum exposure under
USD10 cap.** One unsuccessful400 and one lowgeometryinvalidresponse retained.
No accountinvoice reconciliation claim. Subject costs separate bytask/arm in
manifest; no paidjudge. No keys copied/injected; primary.env unchanged.

[Source review](../evidence/068-source-review.md),
[manifest](../evidence/068-haiku55-manifest.json),
[lossless deduplicated archive](../evidence/068-haiku55-receipts.tar.gz),
[offline reconstructor](../evidence/068-reconstruct.py).
Rawprotected receipts remain benchmarks/results/haiku55-20261007; source
snapshots record exact paidcode before formatting. Hashes/bytecounts cover all
requests/responses, originalfailed400 anddriverartifacts. Reconstruct into an
emptydirectory with `python docs/evals/evidence/068-reconstruct.py /tmp/haiku55-evidence`.
Normalcommands failclosed on closedledger/repeatedrun; new paidrun needs fresh
identity/authorization, never deletefailedartifacts to rerun.

Officialmodeloverview retrieved directly20261007 from
https://platform.claude.com/docs/en/models/haiku-5-5/overview.md: directslug,
text+images,adaptive/defaultmedium,<=100K prices$.10/.50, omitdeprecatedsampling.
Currentsteeringdoc confirms reasoningconsumesmax_tokens. Public/synthetic only;
retention/ZDRunverified and no privatepayloadclaims. Neither totalworkflowshare
nor end-to-endproductionbenefit is measured; tiny percasecost savings do not
justify source/capabilityregressions.

Validation:13focusedguard/handwritingscorertests passed, changedPythonRuff passed,
methodologybuild/check and whitespacehygiene passed. Offlinearchive reconstruction
verifies every member independently; runtime/default/deployment unchanged.
No immediatepaidfollow-up justified: retain incumbents and record checkpoint
rejection; a materially revised source-grounding/checkpoint would reopen exact
failedgate, not replay everytask.

2026-10-07 closeout — After the user authorized finish-and-push, staged review
found that replaying an entrypoint could overwrite auxiliary prior results/logs
although the spend guard denied inference. Native, classifier and OCR entrypoints
now reject existing campaign outputs before writing or calling a provider. Three
offline refusal checks preserved all existing artifact hashes;13 focused tests
and Ruff pass. These changes occurred after measurement and are bound separately
in `068-closeout.json`; execution-time source snapshots and receipts remain intact.
No additional provider calls, source/golden changes or defaults changed.
