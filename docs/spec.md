# Codex-Forge — Spec (Active Compromises)

> Every entry here exists because of a named limitation. When the limitation
> resolves, the compromise gets deleted and the system simplifies.
> See `docs/ideal.md` for what this system should be with zero limitations.

## Non-Negotiable Design Principles

These are not compromises — they are permanent architectural commitments:

1. **Traceability end-to-end** — Every output traces to source page, OCR engine, confidence score, and processing step.
2. **Modular pipeline** — YAML recipes compose modules. New document types = new recipes, not new code.
3. **Append-only artifacts** — Intermediate outputs preserved for audit. No silent overwrites.
4. **Validation is mandatory** — Every run ends with structural and semantic validation.
5. **Graduate to Dossier** — Proven converters migrate to Dossier. Codex-forge stays lean.

---

## Active Compromises

### C1: Multi-Stage OCR Pipeline
**Ideal:** One AI call reads any page and returns perfect text with layout preserved.
**Compromise:** Multi-engine OCR pipeline with escalation (fast engine → stronger model on failures).
**Limitation:** AI capability — no single model reliably handles all page types (scanned, tables, multi-column, degraded) at acceptable cost.
**Detection:** Single-model OCR of a 400-page mixed-format book produces ≥99% character accuracy with layout preserved, at <$2 total cost.
**When it resolves:** Delete OCR ensemble logic, escalation loops, engine voting. Collapse to single extract call.

### C2: Format-Specific Conversion Recipes
**Ideal:** System auto-detects document format and configures itself. Zero user input.
**Compromise:** User selects a YAML recipe matching their document type.
**Limitation:** AI capability — reliable format detection and pipeline selection from raw input alone hasn't been proven across diverse document types.
**Detection:** Given 10 diverse documents with no metadata hints, system correctly identifies format and selects appropriate pipeline for all 10.
**When it resolves:** Delete recipe selection. Auto-detect replaces manual choice.

### C3: Heuristic + AI Layout Detection
**Ideal:** System understands document structure from content alone — sections, columns, tables, headers, illustrations.
**Compromise:** Code-first pattern matching with AI escalation for ambiguous layouts.
**Limitation:** AI capability — VLMs handle most cases but struggle with unusual layouts. Code heuristics are faster and cheaper for well-structured documents.
**Detection:** VLM-only layout detection achieves 100% accuracy on a diverse 5-document benchmark without any heuristic fallbacks.
**When it resolves:** Delete pattern-matching heuristics. Collapse to single VLM call per page.

### C4: Two-Stage Image Crop Detection
**Ideal:** One call detects and crops every illustration perfectly.
**Compromise:** Detector model (Gemini 3 Pro) proposes bounding boxes → Validator model (Gemini 2.5 Flash) checks for text contamination → Auto-retry on count mismatch.
**Limitation:** AI capability — no single model reliably detects all illustrations AND avoids text contamination in one pass.
**Detection:** Single-model crop detection scores ≥0.95 on the image-crop-extraction eval with zero text contamination false positives.
**Current score:** 0.856 (77% pass rate).
**When it resolves:** Delete validator stage, retry logic. Single detect call.

### C5: Layout Text Trim Heuristics for Crops
**Ideal:** Crop detection understands page layout and excludes text automatically.
**Compromise:** Post-detection heuristic trimming using OCR text coordinates.
**Limitation:** AI capability — VLM bounding boxes frequently absorb nearby text.
**Detection:** VLM crop detection produces bounding boxes that exclude all non-illustration content on a 50-page benchmark.
**When it resolves:** Delete `_trim_box_by_layout_text` and related heuristics.

### C6: Expensive OCR for Quality
**Ideal:** OCR is instant and free with perfect quality.
**Compromise:** GPT-5.1 AI OCR at ~$0.01/page. Cost-conscious workflows reuse OCR artifacts rather than re-running.
**Limitation:** Economics — API calls cost money and take time.
**Evolution path:** Cost decreases as models commoditize. When <$0.001/page at current quality, remove cost-conservation workflows.

---

## Retired Compromises (from v1 book processing era)

These compromises existed when codex-forge was a book processing pipeline. They're preserved for reference but no longer actively tracked. The capabilities they addressed (game mechanic extraction, patching system) were specific to Fighting Fantasy processing and aren't part of the current intake R&D mission.

- **C5-old: Per-Module Enrichment Passes** — Separate extraction for each game mechanic type (choices, combat, inventory, stats). FF-specific.
- **C7-old: Patching System for Exceptional Books** — `*.patch.json` overrides for books that defy conventions. FF-specific.

---

## Compromise-Level Preferences

These are engineering decisions tied to specific compromises. They die when their compromise is eliminated.

- **C1:** Prefer code-first extraction for speed/cost; use AI only for flagged pages.
- **C4:** Gemini 3 Pro is the current winning detector; Flash is the cheapest reliable validator.
- **C6:** Treat OCR as expensive and single-run. Iterate downstream by reusing artifacts.
