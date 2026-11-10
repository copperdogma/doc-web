# Attempt087 — Fable5.2 source fidelity capability panel

2026-11-09. **Prioritize native Fable5.2 for broader safety qualification; retain current runtime models.** Fable correctly classified all six safety cases with zero false-safe, versus fresh GPT5.5 three correct and one false-safe. It identified the missing bottom fifth of page012001’s seal. Tables tie fresh Astra; crop and handwriting still lose source content. No default, deployment, commit, push or architecture deletion.

Owner Story265 / Conductor Scout107 revision2 item2. Fresh `origin/main` base `5bd3ba777d70347eb8dd84b9aa18a6b3ba025193`, branch `codex/fable52-20261109-doc-web`, retained uncommitted worktree `/Users/cam/.codex/worktrees/fable52-20261109/doc-web`. Primary checkout unchanged. [Summary](../evidence/087-fable52/summary.json), [plan](../evidence/087-fable52/execution-plan.json), [source review](../evidence/087-fable52/source-review.json), [manifest](../evidence/087-fable52/manifest.json).

## Complete selected panel

| Independent task | Fable xhigh32768 | Fresh maintained control | Decision |
|---|---|---|---|
| Safety six source/crop pairs | 6/6, zero false-safe; USD.536464 /10.077s mean HTTP | GPT5.5 3/6, one false-safe; .350083 /3.689s | Strong bounded quality lead; prioritize broader qualification |
| Three synthetic literal tables | 36/36 clear cells, both genuine ambiguity cells held; .296712 /17.589s mean | Astra same quality; .2309025 /6.997s | Quality tie, retain faster/cheaper Astra |
| Image011/Image001 crops | .9478/.7702 original scorer; strict source preservation0/2; .09968 /6.889s mean | Gemini .9839/.9829, source preservation1/2; .012685 /9.225s | Retain detector and manual/source holds; no crop replacement |
| Actual public LOC Barney OCR | .981295 versus maintained.99; .075648 /15.234s | Exact Gemini3.7 requested,3.8 served; .01614675 /28.979s quarantined | Tested Fable fails gate; no fresh relative OCR claim |

This is the complete twelve heterogeneous candidate cases, not13detector/22safety or400page qualification. One fresh response per case, independent sessions, serial dispatch, no cache or paid judge. The conditional max65536 arm was **not triggered**: the hard glyph discriminator and clean table control both passed, and genuine ambiguity holds are correct behavior. No effort sweep, favorable-repeat selection or prompt/golden weakening. Original ambiguity text comparison is7/8 for both arms; both uncertainty holds prevent accepted wrong edits. Clear cells and ownership are36/36 exact for each model.

Source inspection overrides tolerant crop scores. Image001 Fable omits the complete `1887–1987` date; Gemini retains it. Image011 Fable preserves lettering/date/seal rim but clips12dark pixels at two integral signature baseline endpoints; Gemini clips16seal-rim pixels across rows1374,1375,1790. Both fail strict full-source preservation there. Overlays, original pixels, unchanged normalized boxes and pixel-count regions are retained. The maintained scorer uses a golden-assisted axis oracle for both arms; these results do not qualify raw runtime coordinates.

Barney’s original640x502 source and actual driver HTML were inspected. Fable replaces `comrads` with `comrade` and omits `it` after `least expected`; it does not fabricate the broad guardpost passage seen in Hy4. Some small spelling/token discrepancies remain optically ambiguous, including the golden’s bracketed token; no golden change or invented corrected score. Original .981295 remains separately reported. Exact source fidelity and the maintained.99 gate are uncleared.

## Route recovery, strict contracts and evidence

Selected OpenRouter exact `anthropic/claude-fable-5.2`, Anthropic standard only, was rejected402 under both existing owner and isolated centrally custodied eval credentials:32768 requested,5785 affordable. Full responses retained; no source answer or OR transport qualification. The coordinator then explicitly authorized the existing owner native Anthropic route as operational recovery within the sameUSD30, preserving the exact model/provider/effort/output/payload gates. Final subject route is **native `claude-fable-5-2`**, response model exact, service tier/speed `standard`; do not label these OpenRouter results.

Native Messages uses `output_config.effort=xhigh`, max32768, no sampling override. First source-review schema rejected400 for unsupported array bounds. [Anthropic’s documented SDK transformation](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) moves unsupported bounds into descriptions; `anthropic.transform_schema`0.79.0 was used, and original `SourcePageReview`, crop and safety schemas validate the saved native outputs. This is API-enforced structure plus host enforcement of original bounds, not a claim every bound was API-enforced. Frozen policy/prompt/source/golden/scorer remains unchanged. [Current native model documentation](https://platform.claude.com/docs/en/models/fable-5-2/overview) confirms xhigh/max support and USD8/M input,40/M output.

The first actual table response doubled as native contract and maintained-adapter qualification; subsequent independent crop/safety schemas and actual OCR driver paths were qualified separately. Twelve native subject responses are terminal and contract-valid. Actual OCR uses an eval-only Gemini-client dispatch shim; Google-compatible adapter metadata is not provider attribution or production integration. A subprocess import defect was repaired before any OCR POST, retaining failed driver logs; no subject answer was rerun. Gemini3.7→3.8 identity mismatch is quarantined before semantic scoring, with charge retained.

Full HTTP response bytes and complete lossless outgoing JSON objects/source bytes are durable before parsing. Requests are reserialized JSON, not original lexical wire bytes; authorization headers are excluded. Base plus producing/final source snapshots and epoch notes distinguish the native adapter, import repair and accounting-only guard change. Complete driver artifacts and raw reports are retained. No saved output was semantically rescued.

## Spend, custody and validation

**27POSTs: known usage-priced spend USD1.61832125; conservative unresolved rejection exposure USD4.76416; accounted maximum USD6.38248125/30.** The two402 and one400 originally assumed zero are preserved as superseded records; lack of usage alone does not prove nonbilling, so all three full reservations remain held in the closed corrected ledger. No invoice reconciliation claim. Successful native/controls total1.61832125, including quarantined OCR control. Judges0. No further calls.

All calls checked512MiB minimum free space and durable write admission. Existing owner wrapper credentials remained unchanged. The helper injected exactly OpenRouter into verified ignored isolated `.env`; after failure it removed only `DOC_WEB_OPENROUTER_API_KEY`, with name-only absence verified. Direct native uses the existing owner key through the normal wrapper, never copied or changed. Only owner-cleared public Onward/public LOC/authored synthetic data; standard30day retention and router uncertainty were disclosed. No account setting changes.

`python -m pytest tests/test_fable52_campaign.py -q`:5passed. Offline audit verifies27complete request/response receipts and hashes, exact native identity/terminal state/standard tier, original schemas, billing math and full unknown reservations. Methodology graph/build checks and compile validation are recorded in validation.json. Primary venv lacks pytest/Anthropic; the existing Conda Python with Anthropic0.79.0 ran native subjects and final tests. Unused OR scaffolding is not claimed qualified.

Access: directavailable/ORblocked. Transport: bounded native qualified with disclosed schema enforcement split; OR/production integration unqualified. Reliability:12/12native subjects successful, limited exposed panel. Capability: safetybetter, tabletie, cropsnotqualified, OCRgatefail. Economics: safety53%more costly and2.73×slower by mean than GPT5.5, trading overhead for zero false-safe on these six cases. Adoption: prioritize safety qualification, retain existing defaults everywhere.

The practical gain is a stronger safety reader that caught a dangerous seal-loss acceptance before publication. Reply `yes` to proceed with a separately bounded full22safety/current-caller qualification; no implementation or additional spend is authorized by this recommendation.


2026-11-10 close-out: The historical full22/caller recommendation above was executed separately as Attempt088/Story266 and is closed. Cam stopped further evaluations and authorized check-in/push. No additional provider calls are planned. Original producer evidence remains unchanged; custody packaging and later closure metadata are separate.
