# Codex-Forge — The Ideal

> What the system should be if there were no limitations of any kind.
> Perfect AI, zero cost, instant everything. No configuration, no workarounds,
> no unnecessary complexity. Just the pure experience.

## The Ideal

You hand it a document — any document, any format — and it becomes structured data ready for Dossier.

A scanned PDF from 1985 with coffee stains and a crooked spine. A born-digital textbook with complex tables and footnotes. A genealogy reference with dense multi-column layouts. A folder of JPEG scans. A Word doc. A webpage. A collection of handwritten notes. It doesn't matter. You give it the source material, and it gives you back clean, structured, Dossier-ready output — faithful to every word in the original.

You never configure anything. The system looks at what you gave it and knows what to do. It detects the format, assesses quality, runs the right conversion pipeline, validates the output, and delivers structured data that Dossier can ingest directly. If something goes wrong — garbled OCR, a rotated page, a table that didn't parse — it fixes it. If it can't fix it, it tells you exactly what's wrong and where.

The output is perfect. Not "good enough" — perfect. Every word matches the source. Every table preserves its structure. Every illustration is cleanly extracted. Every piece of output traces back to its source page and processing step. You could diff the structured output against the original and find zero discrepancies.

And it's instant. A 400-page scanned book processes before you finish your coffee. Cost is negligible. You batch-convert an entire archive without thinking about budgets.

## The Execution Ideal

> What building this product should be like if there were no limitations.
> Perfect AI tools, unlimited context, flawless reasoning. No process overhead.

You describe what you want. The AI builds it. It presents options — sometimes
delighting you with approaches you hadn't considered. You have a conversation
about what you see, what you like, what to change. It iterates. You never make
a technical decision, manage a backlog, or think about architecture. You provide
the ideal, your preferences, and your reactions. Everything else is the AI's job.

Even with perfect AI, this is genuinely iterative — you don't fully know what
you want until you see options. The AI fills in blanks, proposes solutions, and
refines through conversation. That iteration is the ideal, not a compromise.

## Mission

Codex-forge is the **intake R&D lab for Dossier**. It solves the hard format conversion problems — scanned PDFs, images, weird document formats — one at a time. Each converter is perfected here, then graduated into Dossier when Dossier is ready to accept it. Codex-forge is where messy real-world inputs become clean structured data.

**Relationship to Dossier:** Dossier is the library that processes structured documents into knowledge. Codex-forge handles the step before — turning physical and unstructured media into the structured format Dossier expects. As converters mature, they migrate to Dossier. Codex-forge always has the next hard problem to solve.

**Relationship to Storybook:** Storybook users will provide documents in unpredictable formats. Codex-forge builds and proves the converters that handle those formats before they become Dossier capabilities.

## Vision-Level Preferences

These qualities persist regardless of implementation. They survive even when every compromise is eliminated.

- **Traceability is the product.** Every piece of output traces back to its source — page number, scan coordinates, OCR engine, confidence score, processing step. Data without provenance is noise.
- **Fidelity to the source.** The system preserves what the document contains, not what it thinks the document means. OCR errors are bugs. Formatting changes are bugs. Missing content is a catastrophic failure.
- **Any format, any condition.** Scanned PDFs, born-digital, images, mixed layouts, degraded quality. No format is unsupported. The system adapts to the input, not the other way around.
- **Zero configuration.** The user's job is to provide a document. Everything else — format detection, pipeline selection, quality validation — is the system's job.
- **Dossier-ready output.** The output format serves Dossier's ingestion requirements. Structure, provenance, and metadata are first-class. The converter's job ends when Dossier can consume the output without transformation.
- **Transparency over magic.** When something goes wrong, the system shows you exactly what happened: which page, which module, which decision, what confidence.
- **Graduate, don't accumulate.** Converters that are proven and stable should move to Dossier. Codex-forge stays lean — it's always working on the next unsolved problem, not maintaining solved ones.

## Requirements

1. **Ingest** — Accept documents in any common format (PDF, images, text, office documents) and produce a normalized internal representation.

2. **Detect** — Identify what the document is and what conversion strategy it needs. Format, quality, layout complexity, content type — all assessed automatically.

3. **Extract** — Produce clean, accurate text. OCR quality must match or exceed the best human transcription. Layout must be preserved where it carries meaning (tables, multi-column, structured data).

4. **Illustrate** — Detect, crop, and catalog every illustration with precision. Whitespace trimmed, captions preserved, overlapping text excluded.

5. **Structure** — Decompose the document into semantic parts with provenance. Every piece of output knows where it came from.

6. **Validate** — Prove the output is correct and Dossier-ready. Every page accounted for. Text accuracy verified. Structure validated against expectations.

7. **Export** — Produce output in Dossier's expected format with full provenance metadata.

## Minimum Viable Floor

The threshold below which the product doesn't solve anyone's problem:

- Given a scanned PDF gamebook, produce a structured JSON artifact with clean text, correct section boundaries, working cross-references, and extracted game mechanics (choices, combat, inventory).
- Illustrations extracted and linked to their sections.
- A human spot-checking the output should find zero errors in any random 10-section sample.
- Processing a 400-page book should complete in under 30 minutes at reasonable cost (< $5).
