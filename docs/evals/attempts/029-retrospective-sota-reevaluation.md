# Attempt 029 — Authoritative-golden SOTA reevaluation

**Date:** 2026-08-14
**Story:** 232

## Decision

- **Detector measured quality and production-eligible leader:** GPT-5.6 Terra, fresh `13/13`, mean
  `0.9689`, `2915 ms/case`, estimated `$0.117188` total. It beats the fresh
  Gemini 3 Flash incumbent at `13/13`, `0.959477`, `6236 ms/case`, `$0.052618`.
- **Crop-only quality and production leader:** Gemini 3.1 Flash Lite, fresh
  `40/40`, mean `1.0`, `2627 ms/case`. Gemini 3.7 repeats `39/40`, `0.975`,
  `2694 ms/case`; its sole miss is again `page-126-000`.
- Page-context remains GPT-5.5 Responses at the retained `22/22`; Terra's
  retained `21/22` cannot outrank it. Handwriting remains unchanged because
  current Gemini 3.7 evidence is below Gemini 3.6 and the absolute target.

The detector result clears the maintained quality/pass-rate and transport
requirements, so it is eligible for promotion. No executable default was
changed without a separate explicit decision.

## Policy repair

The 40 crop-only cases and 22 page-context cases are user-created authoritative
ideal goldens. The invented 12-case held-out prerequisite was removed. A
complete valid authoritative set permits ranking; runtime promotion still
requires the surface's full hard target. The regrader remains fail-closed for
missing, extra, duplicate, overlapping, malformed, or mislabeled evidence.

## Evidence

| Result | SHA-256 |
|---|---|
| `retrospective-gpt56-terra-detector-20260814.json` | `9f359919548acc3cd1f7ad4ddc2e1ffacdbbd35066f5c999ffdfe89882f5a547` |
| `retrospective-gemini3-flash-detector-20260814.json` | `66438bc3b8e9a55ebebf23ad2bded9f33d90cde6281c05f50dc2c8c65f30a086` |
| `retrospective-gemini37-crop-validation-20260814.json` | `8f9507355e51174881575ba77c8b1d70bd596747b0fcfbd2b15e8fa20e1b98a7` |
| `retrospective-gemini31-crop-validation-20260814.json` | `4b03a07d2be213a6329e66e6b5fc5020a04443a9d4c72cb59e1c808f5957359c` |

Task/scorer hashes: detector `5b848f87...f9d` / `7fcf07e0...e7`;
crop-only `049443f5...19a` / `12eb6372...8fb`; authoritative provenance
`acb9101b...e071`.

Conservative estimated subject spend is `$0.29152` total, below the `$5` cap.
The estimate uses official GPT-5.6 Terra rates, recorded Gemini 3 Flash cost,
Gemini 3.7 introductory rates, and those same higher Flash rates as a
conservative proxy where Promptfoo did not know Gemini 3.1 Flash Lite pricing.

No golden label, scorer, private input, executable default, commit, or push was
changed.
