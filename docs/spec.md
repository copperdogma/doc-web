# Codex-Forge — Spec (Active Compromises)

> Every entry here exists because of a named limitation. When the limitation
> resolves, the compromise gets deleted and the system simplifies.
> See `docs/ideal.md` for what this system should be with zero limitations.

## Non-Negotiable Design Principles

These are not compromises — they are permanent architectural commitments:

1. **Traceability end-to-end** — Every output traces to source page, OCR engine, confidence score, and processing step.
2. **Modular pipeline** — YAML recipes compose modules. New book types = new recipes, not new code.
3. **Append-only artifacts** — Intermediate outputs preserved for audit. No silent overwrites.
4. **Validation is mandatory** — Every run ends with structural and semantic validation.

---

## Active Compromises

### C1: Multi-Stage OCR Pipeline
**Ideal:** One AI call reads any page and returns perfect text with layout preserved.
**Compromise:** Multi-engine OCR pipeline with escalation (fast engine → stronger model on failures).
**Limitation:** AI capability — no single model reliably handles all page types (scanned, tables, multi-column, degraded) at acceptable cost.
**Detection:** Single-model OCR of a 400-page mixed-format book produces ≥99% character accuracy with layout preserved, at <$2 total cost.
**When it resolves:** Delete OCR ensemble logic, escalation loops, engine voting. Collapse to single extract call.

### C2: Recipe-Based Book Type Configuration
**Ideal:** System auto-detects book type and configures itself. Zero user input.
**Compromise:** User selects a YAML recipe matching their book type (Fighting Fantasy, genealogy, etc.).
**Limitation:** AI capability — reliable book-type detection from a PDF alone hasn't been built/proven yet.
**Detection:** Given 10 diverse PDFs with no metadata, system correctly identifies book type and selects appropriate pipeline for all 10.
**When it resolves:** Delete recipe selection UX. Auto-detect replaces manual choice. Recipes become internal implementation detail.

### C3: Heuristic + AI Section Detection
**Ideal:** System understands document structure from content alone — sections, chapters, front matter, appendices.
**Compromise:** Code-first pattern matching (regex for "Turn to X", section number patterns) with AI escalation for ambiguous boundaries.
**Limitation:** AI capability — VLMs handle most cases but struggle with unusual layouts. Code heuristics are faster and cheaper for well-structured books.
**Detection:** VLM-only section detection achieves 100% boundary accuracy on a diverse 5-book benchmark without any regex or heuristic fallbacks.
**When it resolves:** Delete pattern-matching heuristics. Collapse to single VLM call per page/spread.

### C4: Two-Stage Image Crop Detection
**Ideal:** One call detects and crops every illustration perfectly.
**Compromise:** Detector model (Gemini 3 Pro) proposes bounding boxes → Validator model (Gemini 2.5 Flash) checks for text contamination → Auto-retry on count mismatch.
**Limitation:** AI capability — no single model reliably detects all illustrations AND avoids text contamination in one pass. Non-determinism requires retry mechanism.
**Detection:** Single-model crop detection scores ≥0.95 on the image-crop-extraction eval with zero text contamination false positives.
**Current score:** Gemini 3 Pro detector + Flash validator = 0.856 (77% pass rate).
**When it resolves:** Delete validator stage, retry logic, count-mismatch handling. Single detect call.

### C5: Per-Module Enrichment Passes
**Ideal:** System extracts all game mechanics (choices, combat, inventory, stats) in one understanding pass.
**Compromise:** Separate extraction modules for each mechanic type (choices, combat, inventory, stat checks, stat modifications), each with its own code-first + AI-escalation pipeline.
**Limitation:** AI capability — a single extraction call for all mechanics produces unreliable results for complex sections. Separate focused passes are more accurate.
**Detection:** Single structured-output call extracts all mechanic types from a 400-section gamebook with ≥98% accuracy on each type.
**When it resolves:** Delete per-mechanic modules. Collapse to single extraction call per section.

### C6: Layout Text Trim Heuristics for Crops
**Ideal:** Crop detection understands page layout — text columns, captions, headers — and excludes them from illustration bounding boxes automatically.
**Compromise:** Post-detection heuristic trimming: check X-axis overlap before vertical trims, use OCR text coordinates to identify and exclude text regions from proposed crop boxes.
**Limitation:** AI capability — VLM bounding boxes frequently absorb nearby text (captions, headers, body text in adjacent columns).
**Detection:** VLM crop detection produces bounding boxes that exclude all non-illustration content on a 50-page benchmark with diverse layouts.
**When it resolves:** Delete `_trim_box_by_layout_text` and related heuristics.

### C7: Patching System for Exceptional Books
**Ideal:** Generic pipeline handles all books without manual corrections.
**Compromise:** `*.patch.json` files override specific outputs for books that defy conventions (Robot Commando vehicle stats, unusual section numbering).
**Limitation:** AI capability + book diversity — some books have truly unique structures that no generic model handles.
**Detection:** Pipeline produces correct output for Robot Commando and Freeway Fighter without any patch files.
**When it resolves:** Delete patching system. All corrections happen through improved generic modules.

### C8: Expensive OCR for Quality
**Ideal:** OCR is instant and free with perfect quality.
**Compromise:** GPT-5.1 AI OCR at ~$0.01/page. Cost-conscious workflows reuse OCR artifacts rather than re-running.
**Limitation:** Physics/economics — API calls cost money and take time. Better models = higher cost.
**Evolution path:** Cost decreases as models commoditize. OCR cost per page has dropped 10x in 12 months. Monitor pricing; when <$0.001/page at current quality, remove cost-conservation workflows.

---

## Compromise-Level Preferences

These are engineering decisions tied to specific compromises. They die when their compromise is eliminated.

- **C1:** Prefer code-first extraction for speed/cost; use AI only for flagged pages.
- **C3:** Pattern matching handles 90%+ of Fighting Fantasy sections; AI handles the rest.
- **C4:** Gemini 3 Pro is the current winning detector; Flash is the cheapest reliable validator.
- **C5:** Extract choices first (most critical for game engine), then combat, then inventory/stats.
- **C7:** Patches must be minimal, scoped, and documented in the story work log.
- **C8:** Treat OCR as expensive and single-run. Iterate downstream by reusing artifacts.
