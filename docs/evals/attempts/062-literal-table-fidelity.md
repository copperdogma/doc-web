# Attempt 062 — Literal table fidelity

Date: 2026-10-06. Story 245. Worker: Codex root; mechanical scorer/corpus workers Sol6.1 medium. Base HEAD ba4c84a; dirty evaluated-file identities are retained with outputs.

## Decision contract (frozen before calls)

Hypothesis: explicit literal transcription instructions or a stronger single-call reader can preserve source characters without document-specific repairs. Compare current gpt-5.1, identical model plus literal policy, then gpt-6-astra medium reasoning at the same 2048px preparation. Each case must pass exact case-sensitive cells and separate table/row/span ownership; all admitted cases must pass, zero substitutions or harmful control changes. No averaged score can conceal a failed case. Production fix only adopted after frozen-policy unseen confirmation and final driver export proof.

Development identities: output/story244-eval/development.json (Star equipment table slice plus lab and transit synthetic source documents). Native and image-only synthetic PDFs share visible pixels; sources and hashes live in metadata.json. Goldens never enter model requests. Onward is existing context, not an admitted new source golden. Confirmation reserved independently before tuning: output/story244-confirmation-sealed/source.json SHA256 7bdfa1dda5fa4f3d7e1fb907d9611d36da7fa6444ce0e35180d7f5a240a82f36. Do not inspect before candidate freeze; no tuning after opening.

Initial phase cap: 24 subject calls, eight final semantic judge calls, estimated USD10 conservative envelope; 8192 subject output tokens, 180-second timeout, SDK retries disabled. Reserve costs before dispatch; transport/incomplete/model-identity failure is not a quality observation. Stop this phase at its cap or two non-improving strategies; revisit source/input diagnosis rather than add prompt special cases. User authorized completing this story; any later experiment phase must have its own recorded bounded decision contract.

## Alignment and reuse

Ideal fidelity/provenance and ADR001/002 permit source-aware extraction and source-linked bundles. Current C1/C3/C6 remain active; this small panel cannot eliminate them. Existing table scorers use normalization inappropriate for exact glyph grading; new stricter scorer has 40 negative/positive controls. No decision-model lane can independently establish an image glyph. Exact identities, comparison and mutation stay deterministic; source interpretation belongs to visual reading. Native text is admissible only with visible-source qualification, never blind overwrite.

## Provisional observations

Baseline gpt-5.1 and literal-policy gpt-5.1: all three development cases fail. Star has two text errors, no scored equipment structure errors: LSU l-to-1 and blank CU replaced by dash. Lab/transit have character substitutions and missing span ownership. All raw and sanitized outputs retained. Offline golden-to-sanitizer controls independently prove span loss even with perfect OCR; narrow generic span preservation is required whatever model is chosen. These are pipeline/model failures, not grounds to loosen goldens. Visually ambiguous synthetic glyphs remain a separate uncertainty to adjudicate before adoption.

Results and receipts: output/story244-eval/{baseline,literal,strong}/; global call-ledger.json. Requests retain source/submitted image and prompt hashes, served model, response status, token usage and elapsed time. No whole-book or ingester speed claim.

## Research

Current primary source model docs: https://developers.openai.com/api/docs/models/gpt-6-astra (image input, strongest practical reader, medium reasoning supported; USD10/M input and USD50/M output). Vision guidance: https://developers.openai.com/api/docs/guides/images-vision (small text can require enlargement/original detail). Authenticated model-list lookup confirmed aliases locally; served identity verified per receipt. Image preparation and glyph visibility may still dominate model choice, so a miss is not proof of impossibility.

## Final adoption and limits

Adopt the opt-in uncertainty-aware B-only gate described in the final result below. Single-call full transcription adoption is rejected; exact extraction target remains unmet on ambiguous sources. Earlier sections retain the chronological hypotheses and rejected strategies.

## Input-preparation comparison (before dispatch)

Strong-model 2048px raw output passes Star and lab but substitutes one character in transit; spans otherwise correct. Third strategy: preserve original PNG bytes and request documented original image detail with unchanged literal prompt/model. Run development transit first, then entire development if exact gate passes. Same initial24-call/USD10 ledger; no expected text supplied, no document-specific crop or correction. This tests small-text visibility loss from downsampling/JPEG. Adopt only if all development and frozen independent confirmation pass; otherwise revisit evidence rather than repeat favorable calls.

Original200dpi transit probe remains one text error (a different cell). No favorable rerun. The remaining visibility uncertainty justifies one composited300dpi PNG experiment at unchanged prompt/model. This is a generic raster-quality change: if all development/confirmation succeeds, prefer lossless composited rendering rather than a witness/repair framework. If it fails, stop single-call strategies and use explicit disagreement/uncertainty gating; do not keep nudging prompts. The exact200dpi miss remains recorded and prevents claiming model-only adoption.

## Candidate selection and integration contract

All three development cases pass raw and sanitized exact text/ownership under the unchanged literal prompt, Astra medium and300dpi PNG original detail. No repair or native text insertion is selected; ADR001/002 remain sufficient because no new evidence authority or publication semantics are introduced. Policy SHA256 b2560dfe4e5a031b7eea50523d8b3cfe7d2299a70f9d7e0b24809858f865c473. Candidate runtime/schema/scorer/input hashes will be frozen before confirmation is opened. Unseen confirmation gets one full driver invocation, with no tuning afterward. Full driver runs also cover original page19 and development native lab; transit's already measured raw output is reused for export verification. This reserves three additional Astra calls (one attempt each, SDKretry0) and four standard Opus4.6 final rubric calls, within the same24subject/eightjudge/USD10 envelope. Direct experiments used13subjectcalls andUSD6.85 conservative reservations; integration reservesUSD2.55 and rubricUSD0.60. Actual token-estimated charges remain separate from reservations. Stop on failed confirmation rather than qualify from the familiar example alone.

Pipeline bootstrap observation: monitored wrapper creates log/PID files before driver fresh-directory validation. First Star invocation stopped before any stage/provider call. Verified directory contains only wrapper logs/events/PID; rerun the same reserved dispatch with explicit --allow-run-id-reuse, preserving failure evidence. This is wrapper initialization/reuse-guard interaction, not a source quality result or favorable OCR rerun.

## Independent confirmation rejection

Frozen candidate passes Star raw/final19rows57cells, and development native labdriver. Unseen image-only workshop confirmation fails one exact cell (LIl-00 -> LlI-00) while structure passes8rows28cells. Source truth is retained; no model/config/golden change and no favorable rerun. Candidate rejected for full source-fidelity adoption. The3single-call preparation comparisons cannot establish exactness on arbitrary fonts. Helvetica I/l ambiguity may be observationally unrecoverable from the raster; source-authored text is not proof of glyph disambiguability. Root will classify visibility independently, keep confirmation exposed as diagnostic only, and create a new bounded decision contract for a generic disagreement/uncertainty gate. No token-specific correction permitted.

## Phase2 decision contract (before calls)

General problem: visual OCR with ambiguous character identity, coupled with uncalibrated forced-choice certainty. Research: Tesseract documents character-choice alternatives and word/box confidence (https://tesseract-ocr.github.io/tessdoc/APIExample.html and https://tesseract-ocr.github.io/tessapi/5.x/a02458.html). PyMuPDF documents hidden/occluded-text hazards (https://pymupdf.readthedocs.io/en/latest/functions.html#Page.get_texttrace); independent local probe shows opaque white-on-white and covered text can still be type0/opacity1. Native painted status alone is insufficient; blind native replacement rejected. Installed PyMuPDF1.27.1 find_tables extracts source equipment row correctly, but no new native dependency/authority is adopted now.

Cheapest next hypothesis: a source-only structured table reread with explicit abstention can produce source-bound table HTML and uncertainties. It sees image pixels and dimensions only, never OCR/goldens/native text. Initial OCR and this independent source reading must agree, or one additional source-only read must confirm the candidate; any reported uncertainty or disagreement remains unresolved and stops qualified export. Reader agreement remains empirical evidence, never a universal correctness guarantee. If the structured reader fails to flag demonstrated ambiguity or introduces known substitutions, reject this simple path before building a native-witness framework.

Prototype policy fixed in benchmarks/scripts/probe_literal_table_review.py before dispatch. Development: existing original equipment image, transit300dpi image, exposed workshop confirmation now diagnostic only. The original confirmation failure remains immutable and is never reused as unseen evidence. Fresh reserved panel is independently authored under output/story244-phase2-confirmation-sealed: nativepositive5x3, clear image-onlypositive6x4, and image-onlynegative4x2 with proved identical glyph pixels. Accept positive cases only with exact cells/structure and zero harmful changes. Negative expected outcome is actionable source-located uncertainty and blocked export; refusal must be reported separately from extraction accuracy/coverage, never counted as successful literal extraction. Hidden/corrupt native layers must not enter model payloads. No blanket native-only scope substitution.

Phase2 cap16subject calls, four final standardOpus4.6 rubrics, USD15 conservative reservations;8192subject outputs,180stimeout, SDKretry0. Stop this phase at cap, transport/status failure, two non-improving strategies, or failed fresh independent confirmation. This phase replaces no first-phase result or golden. Contract and separate ledger fixed before calls. Any next strategy needs fresh source roles and explicit bounded decision contract; no prompt nudge based on expected tokens.

## Targeted source resolution contract (before dispatch)

Phase2 source review passes transit8rows30cells exactly, detects three workshop uncertainties including every actual misread, and flags three l/I source ambiguities on original equipment despite correct diagnostic table text. No native authority is introduced. Next smallest discriminator is one source-only reread of a complete table crop produced from the reader's bbox, padded by2percent of maximum table dimension and clamped to the image. Trigger is any table uncertainty or initial/review disagreement. No tokens, expected strings, goldens, prior OCR or desired uncertainty reduction enter the request. Same fixed literal/abstention policy. Resolve only if crop read has zero uncertainties and agrees exactly with initial OCR over the complete table (text and ownership); retain first review ambiguity, crop transform/hash/receipt. Otherwise hold before qualified export. This is empirical source resolution, never majority voting or universal consensus proof. Development probes: original equipment and exposed workshop. Unseen Phase2 panel remains sealed until production gate freeze; same16call/USD15 phase cap.

## Selected source-review gate

One crop reread did not resolve original ambiguities. Workshop crop raw response retains three correct uncertainty locations but has malformed JSON; retained as a failed structured-output observation, not repaired or favorably retried. Reject crop machinery and unsupported font authority (Star subset cmap is not Unicode; ToUnicode cannot validate itself). Select the simplest measured behavior: independent source-only fullpage inventory once; qualify only complete exact initial/source agreement with no uncertain cells; otherwise emit typed source-located hold and stop qualified export. No native text enters requests. No repairs, native fallback, voting, crop retries or all-panel OCR adoption are claimed. Native and image-only clear cases can pass; ambiguity remains explicitly actionable. Original correct final HTML will be independently inspected as unqualified evidence, with held production run separately demonstrated. This follows the story's pre-existing resolve-or-report-uncertainty branch; held cells are never scored correct.

Malformed JSON motivates documented Responses structured text.format JSONschema (https://developers.openai.com/api/docs/guides/structured-outputs), retaining exact source-only policy and unknown behavior. Schema validity is not a fidelity proof. Production driver rows/reports bind source/image/cellsequence/requestreceipts; finalbuilder verifies them beforeexport and again afterreference enrichment. Fresh Phase2 confirmations remain sealed until runtime/report/builder gate freeze. Same16subjectcall/fourjudge/USD15 phase cap; reserve current dispatched5sourceprobes separately, admit only bounded originalheld, transitclear, workshopheld and fresh clear/ambiguous confirmations. Reuse initialOCR where unchanged instead of paying again.

Integration reservation plan before dispatch: originalheld and exposed-workshopheld reuse immutable initialOCR and eachreceiveone strict source review (USD1.50 conservative reservation each). Fresh reserved nativepositive, imagepositive and ambiguitynegative eachgetoneOCR (USD0.85) plusone strictreview (USD1.50), followed byfourstandardOpus4.6 rubrics (USD0.15each). Combined withfiveexisting Phase2probes (USD4.25), projectedPhase2 reservesUSD14.90 and13subjectdispatches, withinUSD15/16subject/fourjudgecaps. Hidden-layer fixture is verified offline by equalvisiblepixel hashes and exactimage-only payload routing, not separately billed duplicatevisualrequests. Frozenheldouts cannot be tuned; an unexpectedheld clearcase is a coveragefailure, not a literalpass.

Current offlineunqualifieddriver proof `story244-star-unqualified-current` reusesrawOCR afterscope-specificregistryinspection. Final equipment passes19rows57cells exactly; rootmanuallyread10rows includingLSUr2l3, neighboringr211b/r213, 1+, andblankHyperchargeCU. Printedfooter now19(labelp.19/24), logical1, physicaloriginal19; tableprovenance recordsallthreeidentities. No literalqualification appears inthisdiagnosticmanifest. Finalreferenceenrichmentpreservesliteralstrings.

Realdriver source-gate outcomes: `story244-star-held-current` preserves initialOCR and independently matches every table's text/structure, but equipment cells(2,0),(9,2),(10,2) are explicitly uncertain. It exits beforeexport with complete sourceboundreport. `story244-workshop-held-current` reportsuncertainties(1,1),(4,1),(5,0), covering its knowninitialerror(5,0), and similarlyblocks export whilekeeping html/raw_html byteidentical. StrictJSONschema completedbothrequests; these are qualityholds, nottransportfailures. Rootopened the current original diagnosticHTML in a local in-appbrowser and visuallyverified the complete table:LSUr2l3,neighborrefs,1+,blankHyperchargeCU androwownership. Source/finalinspection andrawexactscoring remain separate from qualification.

Validationsofar: current160focused gate/reader/OCR/scorer/parser tests pass;147driver/reference regressions pass;232builder/bundle regressions pass;make lint,make check-size,methodologycompile/check anddiffcheck pass. Driver-onlyRuff has8pre-existing findings, reproducedfromHEAD viaRuffstdin;repo make lint excludesdriver and passes. Full make test and independentcodexreview run concurrently; no repeatedproviderqualityruns.

## Hourly loop-review — 2026-10-06T21:15Z (due21:13:36Z)

Verdict: aligned but at risk until fresh clear cases qualify. This is the first hourly review; the user authorized continuing within Story 245 and requested hourly review. Original single-call adoption and crop resolution were rejected using retained failures, not deferred. The current useful result is a real driver hold before export, covering the demonstrated workshop error and preserving source evidence; the original correct diagnostic HTML is visually verified but explicitly unqualified. Test counts alone do not close the story.

Would choose the B-only gate again: it adds a bounded abstention surface without asserting native text authority or silently replacing ambiguous glyphs. Reuse the source-backed Tesseract alternatives/confidence and PyMuPDF hidden/occluded-text comparison above: those assumptions still fit, and local subset-font inspection rules out treating native extraction as independently authoritative. A font reconstruction framework would displace the smaller consumer-visible result without demonstrated authority. No additional source research or crop retries are justified now.

The smallest discriminator remains the frozen, independently prepared native and image-only clear cases plus an identical-glyph ambiguity case: clear cases must qualify with exact source cells, ambiguity must hold, and held coverage stays separate from transcription accuracy. Independent review additionally found a literal-only builder publication path collision; apply the existing path-separation guard before freezing. The bounded CLI advisory timed out without a final report, but exposed erased line boundaries/captions and a receipt-only provider bypass; generic fixes have160 focused passing checks. Full-suite missing saved benchmark-response fixtures are being classified as baseline limitations, not repaired with invented evidence.

Disposition: finish the existing bounded task, no goal expansion, native authority or further strategies. Freeze after review fixes, run each fresh case once, inspect final artifacts, obtain independent rubrics, then close only against the existing uncertainty-aware ACs. No extra permission or handoff is required for this already-authorized work. Next hourly review remains22:13:36Z; the two-minute delayed checkpoint does not shift cadence.

## Frozen confirmation and final result

Candidate identity: `output/story244-phase2/candidate-freeze-v2.json` hashes72 runtime/scorer/recipe files plus the independent corpus seal. The corpus was opened only after freeze; each of native-positive, image-positive and ambiguity-negative received one initialOCR plus one strict source-only review. No desired text, initialOCR, native layer or golden entered the independent review request.

| Case | Literal outcome | Production disposition | Evidence |
| --- | --- | --- | --- |
| Fresh native library |13/13cells exact,5rows/span preserved |qualified |`output/runs/story244-native-positive-v2/output/html/chapter-001.html` |
| Fresh image-only bakery |23/23cells exact,6rows/span preserved |qualified |`output/runs/story244-image-positive-v2/output/html/chapter-001.html` |
| Fresh ambiguous warehouse |7/8initialcells exact; identicalglyph I/l cannot be disambiguated optically |held; both ambiguous source cells flagged; no bundle |`output/runs/story244-ambiguity-negative-v2/03_literal_table_review_v1/pages_html_reviewed_reports/row-00000-page-00001-original-00001.json` |
| Original equipment diagnostic |57/57cells exact,19rows; LSU `r2l3` |unqualified diagnostic; separate real gate run holds3uncertaincells |`output/runs/story244-star-unqualified-current/output/html/chapter-001.html` |
| Previously exposed workshop |one initial exacterror; independentreview flags its location and2others |held; initialHTML/raw unchanged; no bundle |`output/runs/story244-workshop-held-current/02_literal_table_review_v1/pages_html_reviewed_reports/row-00000-page-00001-original-00001.json` |

Fresh safe-disposition3/3 is distinct from exact-transcription2/3 and qualified-coverage2/3. Zero known wrong cells among36 accepted cells; held errors are not forgiven or scored correct. Across the five production diagnostic/confirmation pages above, only2/5qualify; this is a coverage limitation, not universal fidelity. Source review inventories all tables, including four on the originalpage; scoring that original equipment slice is explicit. No repair/nativeauthority is implemented. The pre-existing resolve-or-report-uncertainty branch is the completed behavior.

Four independently served ClaudeOpus4.6 rubrics pass: two clear literal finals, original unqualified equipment literal diagnostic, and negative safe-hold handling. Deterministic exact comparator remains authoritative and no judge can relax it. An independent Astra artifact audit revalidated current input authority, both qualification/report/entryhashes,36 finalcells and negative rejection; no contradiction to safehandling closure.

Root inspected all three sourcePNGs, both finalHTMLs in a real browser,11 positive table rows, both pageJSONL rows, typed reports, manifest/qualification records and four source-provenance records. Examples preserved: `cataloge`, `recieve`, `Il1-O0`, `o0-LI`, `aB-9`/`AB-9`, curlyquotes, blankversusdash, `1+`, colspan3/2. Original manuallyinspected10rows retain LSU `r2l3`, adjacent `r211b`/`r213`, `1+`, blank HyperchargeCU and CommercialVehicle inside ShipBoat notes. Original printed19/logical1/physical19 remain distinct in provenance. Portable manifest/schema validation and every qualified entry/report hash match.

Current-parser offline audit regrades36 retained observations; all27 recorded old verdicts persist, including the rejected workshop confirmation. Parser now checks captions, table-owned outside text and rendered line/block boundaries; hidden-content structures fail. Earlier held reports retain old candidate identities and cannot authorize new qualification. They are not manually patched. Fresh reports use current canonical hashes.

Synthetic fresh sources/goldens/PDFs/PNGs/proofs are retained unchanged at `testdata/literal-table-fidelity/confirmation-v2/`; they are now exposed regression material. Original game PDF remains external/read-only. Hidden-layer control proves byte-identical visiblepixels to image-only PDF and a conflicting native layer; production payload tests prove only imagebytes/dimensions enter review. No duplicate paid hidden-layer read was made. No format-wide matrix/state promotion or compromise deletion.

## Cost, latency and rejected paths

The offline audit `output/story244-phase2/cost-latency-summary.json` deduplicates33 providerIDs. Phase1:16subjects,USD9.40reserved,USD1.39517875tokenestimated. Phase2:13subjects+4judges,USD14.90reserved,USD1.822275tokenestimated (judges0.096805); combined3.21745375estimated,262322tokens. Reservations are not billed cost. Verified2026-10-06 uncached rates: GPT5.1 USD1.25/10 perM input/output (https://developers.openai.com/api/docs/models/gpt-5.1), Astra10/50 and Opus5/25 perM as sourced above. Existing run pricing snapshots omit Astra/Opus and are not used as authority.

Fresh initial+review request sums: native13.180s/USD0.23459; image19.738s/USD0.24984; ambiguity14.137s/USD0.23469. These are request sums, not full driver walltime or optimization gains. Five early Phase2 probes lack timings; token-cost coverage is33/33, timing28/33. Root/worker orchestration cost is not included. No speed claim about ingester snapshot checks.

Do not retry rejected prompt/raster/crop variants on exposed confirmation merely to obtain a favorable answer. Re-evaluate on fresh reserved evidence when a new subjectmodel, independently qualified visible/native authority or materially different approach can raise accepted coverage without weakening holds. Both policy and source uncertainty remain inspectable.

## Validation findings and resolution

The bounded `codex review` advisory timed out at300s without a final clean report. Its partial evidence exposed real caption/line-boundary comparison gaps and a receipt-only nonOpenAI provider bypass; generic fixes pass focused regression. Independent Astra review additionally found postvalidation output/state/progress collision; the existing path-separation guard now applies to literal-only builds, with four CLI collision regressions.236builder/bundle/gate tests pass.160focused reader/adapter/parser/OCR tests and147driver/reference regressions pass; lint for runtime/tests and changed benchmark/schema tooling passes.

Initial full-suite run exposed missing ignored historical `response-068.json` needed by unchanged cropfixture setup. Exact retained tracked fixture hash99ef270f399ae6075a33615cd2fd7b9f444eaef200a644f48b5c1b5672fdcae2 matches the original048 continuation manifest; restored only the ignored file, no fabricated response or trackedfixture edits. The rerun exposed three genuine new early-crop-prerequisite ordering regressions; move the existing requiredargument check before literal receipt discovery. This validation-only ordering fix changes no source-read policy/scorer/decision. Final builder-only driver resumes reused unchanged saved requests and reproduced byte-identical HTML for both qualified cases and the original unqualified diagnostic. Current portable qualification/entry/report hashes validate. No reading policy, scorer or model call changed; candidate-validation-addendum.json and current-builder-rebuild-proof.json retain this evidence. All120 crop and236 gate/build/bundle tests pass after the ordering fix.

## Conclusion

**Quality-eval result: failed.** The original all-case exact-transcription target
remains unmet, including the retained workshop failure and the one fresh
identical-glyph error. The registry keeps that failure status.

**Product decision: adopt the opt-in safe-handling gate.** Its separately frozen
contract passes all three fresh dispositions: two clear exact qualified outputs
and one actionable hold, with no known incorrect accepted cell. Story 245 already
permits resolving discrepancies or reporting uncertainty; no acceptance criterion
was relaxed to count a hold as correct text.

What worked: lossless source preparation, literal instructions, preservation of
safe spans/entities, an independent source-only inventory, exact comparison,
strict bound evidence and the final export gate. What failed: prompt-only baseline,
strong single-call universal adoption, and complete-table crop resolution.
Native-layer authority remains unproved and was not added. No favorable reruns.
Retry only with a materially new model/approach and fresh reserved confirmation;
retain all exposed cases as regression material and keep uncertainty visible.

Final validation: fresh applicable broad run1639passed/1skipped; separately
rerun2transport+3thinkingguard checks pass (1644currentpasses). Original full
suite is not green: classified fixture/transition failures are resolved by exact
restoration/current reruns;3unchanged HTTPX test-order failures pass alone, and
2unchanged pikepdf native installer failures remain. See graded validation note.
Story 245 closes on safe handling, while this quality attempt retains failed
exact-transcription status. No commits/pushes.
