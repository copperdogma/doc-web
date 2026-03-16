# Codex Forge Inbox

This file captures ideas, insights, and potential architectural improvements discovered during development and manual tasks.

## Untriaged

- Row-structured fallback experiment for hard table pages: if the current HTML-first targeted rescue starts struggling again on reviewed genealogy-table pages, try a bounded experiment where the model emits row-oriented CSV/JSON with stable row ids first, then render HTML deterministically and compare row recall, ordering, and column fidelity against the current rescue path. Revisit trigger: repeated reviewed failures on Roseanna/Emilie-style pages or unstable model drift that the current acceptance checks cannot reliably control.
- External document-ingestion systems to evaluate for codex-forge: `Docling` (typed document IR, backend abstraction, serializer separation, optional enrichments), `OCRmyPDF` (deskew/rotation/cleanup/OCR-layer preprocessing), `Surya` plus `Marker` (layout, reading order, table/cell detection, OCR repair components), and `GROBID` (domain-specific converter pattern with coordinate-rich structured output and strong eval discipline). Goal: identify reusable components or architectural patterns that could reduce bespoke intake/OCR/layout work without weakening provenance, inspectability, or recipe modularity. Suggested evaluation order: Docling first, OCRmyPDF second, Surya/Marker third, GROBID fourth. Revisit trigger: the next story that reopens intake routing, OCR/layout architecture, or document-consistency planning (`C1`, `C2`, `C3`, `C7`).
