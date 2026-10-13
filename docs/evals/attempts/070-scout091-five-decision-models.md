# Attempt 070 — Five decision models: text tradeoffs and a visual safety stop

Date: 2026-10-13. Approved Scout 091 items 2 and 3. Text cap USD4; visual cap
USD8; owner cap USD12. Worktree `codex/scout091-docweb-20261013` starts at current
remote main `5917251340e9c39fbfa69f62d6d31fa8eb8e7d56`. The clean primary
Story 245 checkout at `19b30b1` was read only. No runtime defaults, account
settings, commits, pushes or deployment changed.

**Text decision:** Solar is the strongest bounded quality/cost signal for a
future source-aware batch qualification. Its real cascade scores 33/40 versus
fresh GPT-4.1's 30/40, with fewer dangerous clean judgments overall and 81% lower
cost, but p95 is 15.6 times higher and one insufficient-evidence case is called
clean. Keep the full planner, source reasons and manual review; automatic
promotion is unqualified.

**Visual decision:** no safety winner. Clef and the fresh GPT-5.5 control both
accepted a substantially clipped seal. Clef stopped at the declared safety
gate. ScaleDown blocked the required two-image transport; Liquid direct access
was absent. The remaining 20 cases were not measured.

## Frozen decision contract

Story 233 / C7 (climb): five exact dated OpenRouter Decisions identities,
`cloudflare/clef-omni-20261009`, `nace-ai/drex-v2.0-20261009`,
`liquid/d1-20260930`, `scaledown/classify-1-20260928`, and
`upstage/solar-decide-20260928`, versus fresh pinned `gpt-4.1-2025-04-14`.
The maintained five-class projection has 20 independently reviewed synthetic
cases from two documents, repeated twice. Explicit `uncertain` stays review;
otherwise confidence below .8 invokes a fresh serial GPT-4.1 fallback for that
candidate. This rule, prompt, gold, class definitions and scorer stayed fixed.
No paid judge, threshold tuning or full-planner replacement was evaluated.

Story 240 / C5 (climb): finite page-context crop verdict, using all 22 exact
owner-public source/crop bindings from Decisions 063 and the source-adjudicated
Attempt 048 prompt/gold. Clef and ScaleDown router image routes were selected;
Liquid direct vision required an existing configured key. The first intact
small image pair qualified transport, then the clipped-seal differentiator
triggered the unsafe-accept stop. Fresh GPT-5.5 used the maintained Responses
configuration: `none`, 2048 output tokens, `auto`, strict full object.
Candidate reasons and generated geometry remain unqualified. Source bytes and
pixel geometry stayed exact; no downsample, collage, source omission or OCR
transport rescue was permitted. This selected finite safety projection does not
claim detector replacement or bypass a geometry qualification gate.

The full extraction/planner/rationale/repair path and runtime shadow promotion
remain separate boundaries under Story 220 / ADR-001. Historical 048/063/064
results are references, not fresh paid arms. No input-format coverage or
compromise deletion is claimed.

Requests were independent and serial, without session chaining or output
caches. There were no automatic or semantic retries. Up to two evidence-led
operational recoveries per lane were permitted within the hard caps. Conservative
full reservations were USD2.3113084 text and USD6.6792 visual, leaving finite
qualification/recovery headroom. Both ledgers reserve before dispatch and retain
unknown exposure. Catalog identity/provider mappings and prices were refreshed;
provider fallback was disabled. Model echoes do not attest immutable weights.
Drex stayed within its short-state limits. ScaleDown received every structured
state field through lossless stable JSON in `state.text`.

All text is synthetic; images are explicitly owner-classified public, rather
than assumed public because they are tracked. All 44 source/crop URI hashes
and five retained authorization-reference hashes matched. Provider retention
and training remain unresolved/disclosed for these approved public/synthetic
payloads; no ZDR claim is made. Existing owner OpenAI/OpenRouter keys were read
through `scripts/run_with_doc_web_env.py` with `DOC_WEB_ENV_FILE` pointing to the
primary owner `.env`. No key injection, copying, account provisioning or search
for credentials in another repository occurred. The direct Liquid variables
were absent; only its visual lane was deferred.

## Complete text comparison

| Arm | Correct /40 | Defect clean / uncertainty clean | Review | Real fallbacks | Cohort USD | Median / p95 ms |
|---|---:|---:|---:|---:|---:|---:|
| Fresh GPT-4.1 |30|3 /0|6|0|.043392|681 /1111|
| Clef raw |18|6 /6|2|0|.00340470|348 /713|
| Clef cascade |28|3 /0|4|38|.04484070|1022 /1851|
| Drex raw |18|6 /8|0|0|.00116376|389 /477|
| Drex cascade |22|4 /8|0|12|.01438376|427 /1115|
| Liquid raw |28|4 /4|4|0|.00085384|398 /493|
| Liquid cascade |31|2 /2|6|6|.00727784|410 /1139|
| ScaleDown raw |12|2 /4|0|0|.00123592|518 /801|
| ScaleDown cascade |31|2 /0|6|38|.04250792|1182 /1682|
| Solar raw |31|0 /1|4|0|.00151180|13164 /17319|
| Solar cascade |33|0 /1|5|6|.00826380|13164 /17319|

Solar's cascade macro-F1 is .82087 versus GPT's .73725; uncertain recall is
62.5% versus 75%. Its one dangerous clean judgment is repeat 1 maintenance-09:
the source omits installation dates and work notes, so extracted-looking values
cannot establish conformity. Confidence .992957 bypassed fallback; repeat 2
correctly declined. GPT's three dangerous clean judgments cover two unique
cases, family-03/04. Fewer established-defect misses do not establish uncertainty
parity, and no new source guard or confidence threshold was tested. Solar's
latency/cost tradeoff suggests a separate batch qualification, not an automatic
interactive routing replacement.

ScaleDown's cascade removes one known-defect clean judgment at similar cost
(2% saving) but 51% higher p95; no useful overall improvement is demonstrated.
Liquid's cascade improves accuracy and cost but introduces two uncertainty-clean
judgments on family-09, making four dangerous clean judgments versus GPT's
three. Clef adds cost/latency at worse accuracy; Drex retains 12 dangerous clean
judgments. Do not adopt these tested automatic routes. No fresh Jev arm or
claim against its historical best evidence is included.

`text-summary.json` preserves every class recall, macro-F1, review count,
actual fallback cost/latency, mismatch, uncertainty-clean count and unique
case IDs. All 20 source-backed labels were reviewed without a golden change.
The two repeats are reliability evidence, not 40 independent samples.

## Visual qualification and stop

Clef passed safe logo `page-012-000`, then passed `page-012-001` despite the
source-confirmed seal clipping. Confidence was .0275; confidence routing was
not predeclared for this visual projection, so a new threshold cannot rescue
the result. The fresh GPT-5.5 control also passed both cases. Its full reason
noticed the absence of external text and neighboring visuals but omitted the
substantial loss of seal content. Both scored 1/2 with one false-safe and no
false-reject. Do not call GPT proven safe or Clef relatively worse on this
matched two-case diagnostic. The full 22-case gate remains unmeasured.

Attempt 048 registration has 439 inliers, mapping crop bottom 1701.98 versus
full-seal bottom 1790: roughly 21% of seal height is missing. Owner and root
independently inspected `source-review-contact.jpg`; the flat-cut crop bottom
corroborates the retained source-adjudicated fail gold. No source, golden,
prompt or scorer was changed after an outcome.

Clef's two verdict calls cost USD.00088050 versus GPT's two full objects at
USD.051778, with median 1467 versus 2762 ms. This failed safety diagnostic cannot
establish adoption or whole-workflow savings. Internal resized pixel dimensions
were not returned and remain unverified; Cloudflare documents 64–1024 image
tokens. Original submitted dimensions/bytes are preserved.

ScaleDown's exact two-image array returned HTTP400, requiring state as a string
or an object containing only text/document/document_mime_type. Its documented
single-document facade delegates OCR/text extraction and cannot preserve this
native source-plus-crop contract. No OCR/document repair was scored. Text
access is available; visual transport is blocked, capability unmeasured,
adoption deferred. Liquid direct vision has no eligible configured key;
transport/quality are unmeasured and adoption deferred. Both stops leave the
completed text comparison intact.

## Provenance, spend and validation

All five native text identities and custom-runner request parity qualified.
346/346 text HTTP calls completed. The initial parser wrongly required zero
accounting output tokens; Drex reported 95, ScaleDown/Solar one each while the
typed envelopes and output-free costs were valid. Saved raw responses were
reparsed without another call or prompt change. The exact initial single-line
source difference and paid source snapshots are retained. After ledgers closed,
formatting and removal of unrelated old helper dispatch paths preserved all
22 image bodies byte-for-byte; later code did not produce earlier scores.

The closed text ledger has 346 calls: six qualification, 200 typed subjects,
40 baselines and 100 real fallbacks. **USD.16196998 /4 settled; unknown zero.**
The closed visual ledger has five calls: two Clef, two GPT and one ScaleDown.
**USD.05265850 /8 settled plus .00256 unknown HTTP400 billing reserve.**
Owner total: **351 calls; USD.21462848 settled + .00256 unknown = .21718848
maximum exposure /12.** OpenRouter reports response costs; OpenAI costs use
validated actual usage and current unit rates, including cached input, not an
invoice. Unknown HTTP exposure is not assumed free. No active paid process or
temporary credential remains; existing owner credentials were unchanged.

`preflight.json`, source snapshots, rendered text matrix, image topology,
source-review/eligibility records and ledgers bind the current base and actual
dirty execution identity. `receipts.tar.gz` (60.9 KB), `receipt-manifest.json`
and `reconstruct.py` preserve all 702 exact request/response files through
original fixture URI references. Offline reconstruction verified every size and
SHA-256; saved-response parser replay reproduces all 350 valid outputs and
settled costs. Ignored original receipts remain under
`benchmarks/results/scout091-20261013/`.

Validation: 40 focused pytest tests passed; Ruff passed current new files;
methodology compile/check and whitespace checks passed. `validation.json`
records cap closure, identity/cost replay, eligibility hashes, no-auth receipt
checks and cleanup. No driver behavior changed; no driver/publication proof is
claimed. Official source URLs and checked catalog/endpoint evidence are retained
in `sources.json` and adjacent files, including successful official web reads
where generic HTTP GETs failed.

Cam now has actual fallback economics and a separately visible uncertainty risk,
so low token prices cannot silently displace source review. The recommended next
step is a separately specified, independent source-aware Solar batch
qualification with fresh held-out cases, full runtime shadow cost/latency,
rationale/repair ownership and explicit uncertainty/review acceptance criteria.
No further paid work on these exposed fixtures is recommended.


## Authorized landing preparation

Cam subsequently requested check-in and push. Closeout keeps the paid evidence
and closed ledgers unchanged. A fresh origin fetch still matches the execution
base; no incoming integration conflict exists. Current main is unprotected and
this repository has no CI workflows or active Git hooks. Stories 233/240 remain
already Done; this landing does not close broader runtime promotion work. The
reviewed inbox has no relevant Scout 091 capture or primary-checkout dirt.

A scoped portability repair makes regression tests read native responses from
the tracked lossless archive rather than ignored originals; all seven affected
tests (including the closed-preflight overwrite guard) and Ruff pass. The other
34 unchanged focused tests, raw replay and visual
source review remain applicable. The changelog now uses its CalVer header. Full
external documentation downloads are omitted from Git; concise contract facts,
URLs, retrieval hashes and exact native receipts retain the evidence needed.
No provider call is authorized by these closeout repairs. Candidate preparation
waits for the coordinator's all-repository preflight before any push.

The closed-preflight guard is a post-paid closeout change: a completed ledger
now rejects preflight before any source snapshots or rendered evidence can be
overwritten. Paid requests, scores and original execution snapshots stay exact.
There are 41 applicable focused tests after closeout; no new provider call ran.
