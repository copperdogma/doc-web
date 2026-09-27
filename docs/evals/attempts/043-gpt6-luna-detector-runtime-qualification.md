# Attempt 043 — GPT-6 Luna detector-only runtime qualification

Date: 2026-09-26. Owner: Doc Web, Story 236. Base: `92f341e169f7e81775a7f006ae39757303a8e88f` (`origin/main`), isolated uncommitted branch `codex/gpt6-sol-luna-eval-20260926`. This continues Attempt 042's **single US$3 campaign**, without repeating its failed page-safety screens. [The evidence manifest](../evidence/043-gpt6-luna-runtime-manifest.md) identifies the source, recipes, seven owner driver runs, 42 new raw responses and usage ledger.

## Decision and owner contract

**Keep Gemini 3 Flash as the runtime crop detector.** Exact `gpt-6-luna` at medium remains the bounded full13 detector benchmark leader (13/13, `0.987554` versus fresh Gemini `0.961238`), but the same-input production crop seam does not qualify a detector switch. Keep Gemini caption assist and deterministic layout trimming. Keep GPT-5.5 Responses as the page-context regression provider: Attempt 042's Luna and Sol page screens made source-confirmed false-safe judgments, and no full22 page matrix was admitted. No maintained recipe/default, scorer, golden, prompt, private corpus or provider account setting was changed; no commit or push.

Story 231's adoption gate requires source-backed inspection of cover, seal/signatures, multi-photo page and caption-bearing line art, with no missing crop, material clipping, printed-caption contamination or broken provenance hidden by a green driver exit. Story 232's 13 human goldens are sufficient for **bounded detector ranking**, but do not transfer a benchmark score to production artifacts. The established public four-page runtime gate is sufficient for this owner adoption decision: the observed crop failure retains the incumbent. This attempt does not add a held-out corpus or discharge C5.

The projected recipes copy the maintained Onward parameters, including cover page 1's deterministic bypass, high-resolution source mapping, caption second pass and layout-text trim. The challenger splits only the detector to exact `gpt-6-luna` medium while retaining `gemini-3-flash-preview` for captions. The control keeps Gemini for both roles. The source fixture retains upstream counts `{1:1, 12:4, 122:3, 125:1}` and the same public images. The page-12 detector prompt explicitly groups adjacent seal and signatures into **one** image box; therefore a two-box Luna response is not by count alone a model-contract failure. The final crop still has to meet the owner's source-fidelity gate.

## Runs and source adjudication

| Driver run | Detector / caption | Context | Crops by page 1/12/122/125 | Disposition |
| --- | --- | --- | --- | --- |
| `story236-gpt6-luna-r1` | Luna / Gemini | broken shared layout cache | 1/2/3/1 | diagnostic, layout unavailable |
| `story236-gemini-r1` | Gemini / Gemini | broken shared layout cache, old array parser | 1/4/3/1 | diagnostic, page-12 text strips |
| `story236-gemini-coordinate-fixed-r2` | Gemini / Gemini | no layout; initial orientation repair | 1/4/3/1 | diagnostic, page-122 neighboring portrait |
| `story236-gpt6-luna-layout-parity-r3` | Luna / Gemini | isolated official layout model, maintained caption cap 400 | 1/2/3/1 | production-parameter challenger; page-12 composite rejected |
| `story236-gemini-layout-parity-r4` | Gemini / Gemini | same layout/cap, fail-closed generic array parser | 1/3/3/1 | production-parameter control; page-12 signatures combined |
| `story236-gpt6-luna-caption2048-r5` | Luna / Gemini | same layout; diagnostic caption cap 2048 | 1/2/3/1 | rejected; page-12 caption response `MAX_TOKENS` and raw detector crop flawed |
| `story236-gemini-caption2048-r6` | Gemini / Gemini | same layout/cap and parser as r5 | 1/4/3/1 | diagnostic control; all six Gemini responses `STOP`, but printed officer labels remain |

The shared user's `PP-DocLayout_plus-L` model cache had a broken parameter-file link. Before r3, the exact official model was restored in an isolated ignored `output/model-cache-story236`; the shared cache and primary checkout were untouched. Early r1/r2 outputs are preserved as diagnostics, never scored as production-parity. Gemini's raw `image_box` arrays were ambiguous between x/y and y/x; the generic orientation repair uses an overlapping caption above or below to disambiguate and falls back to CV on no-caption or ambiguous arrays. It was frozen before the later fresh control and has focused ambiguous/no-caption tests. It is a tooling repair on selection-exposed pages, not held-out quality proof.

The owner driver exits `done` for all seven runs, but crop files are the decision surface. In r5, Luna's raw page-12 detector box `[.120,.686,.718,.843]` maps to `(612,4528)–(3662,5564)` on the 5100×6600 high-resolution source and **exactly matches** the final crop. Source overlay inspection shows the lower seal and lower signature extend below that raw box, the upper signature extends beyond its right edge, and printed officer labels lie inside. The layout trim and incomplete Gemini caption response did **not** shrink this box. This is material clipping and printed-text contamination in the detector's own geometry. It does not become a pass if its 2048-token caption call is retried at a larger bound. The `MAX_TOKENS` response is retained as a separate, unscored caption-assist contract failure. No additional paid call was justified by it.

The r6 Gemini control preserves the page-12 logo, seal and two signatures as four crops; printed officer labels still enter signature crops, so it too does not prove full source-text exclusion or C5 removal. This is an existing shared cleanup residual, not evidence that the Luna composite is acceptable. Both final arms kept the page-122 reunion and the two separate oval portraits without neighboring-photo or printed-caption leakage, and preserved the page-125 line art with its printed caption excluded. The deterministic cover remained one crop. A count-mismatch fallback is not qualified: Luna's prompt permits the seal/signature grouping, and the fresh Gemini artifact still has officer-text contamination. No book-specific router or hybrid default was added.

## Transport, spend and reproduction boundary

The optional GPT-6 strict Responses route preserved `store:false`, exact served-model and terminal-state checks, native usage and local schema validation; the runtime split did not alter the default. Raw direct OpenAI and Gemini responses were saved in ignored owner storage **before parsing**. The Gemini client now rejects wrong served identity and non-`STOP` finish, preventing the 400/2048-token truncations from being silently treated as normal captions. The evaluation-only retry flag disables OpenAI SDK retries; no orchestrated retry or model-effort sweep occurred. The owner wrapper used its existing ignored `.env` by variable presence only; no secret value was printed or copied.

Attempt 043 has **42 unique response IDs**: 9 direct Luna Responses and 33 Gemini responses, including diagnostic runs. Usage-priced incremental spend is **$0.181080085**: Luna `$0.005302585`, Gemini `$0.175777500`. Attempt 042 had `$0.201644875`; the combined campaign is **$0.382724960 / $3.00**, leaving `$2.617275040`. OpenAI pricing separates ordinary input, cached reads and cache-write subsets; Gemini output includes thoughts. These are usage-based estimates at the 2026-09-26 official rates, not an account invoice. No unpriced paid response or pending reservation remains.

The executed driver shape, with run IDs and recipe paths in the table and manifest, was:

```bash
DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env \
PADDLE_PDX_CACHE_HOME=output/model-cache-story236 \
PADDLE_PDX_MODEL_SOURCE=bos PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True \
OPENAI_CROP_RAW_ENVELOPE_DIR=benchmarks/results/gpt6-sol-luna-20260926/runtime/raw-openai-ARM \
GEMINI_CROP_RAW_ENVELOPE_DIR=benchmarks/results/gpt6-sol-luna-20260926/runtime/raw-gemini-ARM \
CROP_EVAL_DISABLE_SDK_RETRIES=1 \
/Users/cam/miniconda3/bin/python scripts/run_with_doc_web_env.py \
  /Users/cam/miniconda3/bin/python driver.py \
  --recipe configs/recipes/RECIPE.yaml --run-id RUN_ID
```

This records the reproducible command shape, **not** a command to replay every arm: r1/r2 predate the isolated cache, r1–r4 used the maintained 400-token caption cap, and r5/r6 used the explicit `*-caption2048.yaml` diagnostic recipes. Their `output/runs/RUN_ID/snapshots/recipe.yaml` and plan snapshots record the resolved inputs. A repeat would be a new paid attempt with fresh gates and budget accounting. No stopped Sol/Luna page-safety screen should be rerun as part of this attempt.

Focused module/provider, parser and recipe tests, Ruff and methodology checks are recorded in the Story 236 closeout. This evaluation closes with a **model-selection win but a runtime adoption hold**. The useful next technical work is a source-backed, model-independent crop/text contract repair; only then would a newly frozen output gate make another detector comparison meaningful. C5 remains open.
