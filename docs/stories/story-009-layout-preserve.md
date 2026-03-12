# Story: Spatial Layout Understanding for Content Linearization

**Status**: To Do
**Priority**: High

---

## Problem

When converting multi-column, image-rich, or complex-layout documents to single-column HTML, we need to make conscious, defensible decisions about where every non-text element (images, tables, figures, sidebars) appears in the linearized output. Currently, the pipeline extracts text and images separately without preserving their spatial relationships on the source page.

A three-column document with an image spanning columns 1-2, a table in column 3, and a figure at the bottom of the page must become a single HTML stream where each element is inserted at the most semantically correct position. Sometimes the placement is obvious (image between paragraphs that reference it). Sometimes it requires reasoning (image floated in a margin — does it belong before or after the adjacent paragraph?). Either way, the decision must be explicit and traceable.

## Goal

Build a spatial layout representation that captures the geometric relationships between content blocks on a page, and use it to drive intelligent content placement when linearizing to HTML. Every placement decision should be documented in the output provenance.

## Acceptance Criteria

- [ ] **Layout map per page**: Each page produces a spatial map of content blocks (text regions, images, tables, figures, captions, headers, sidebars) with bounding boxes and reading-order relationships.
- [ ] **Content-type classification**: Each block is classified (paragraph, heading, image, table, caption, page-number, marginalia, etc.) so downstream placement logic can reason about it.
- [ ] **Reading-order linearization**: The layout map is linearized into a content sequence that preserves semantic proximity — images appear near the text that references them, tables appear where they interrupt the reading flow, captions stay with their figures.
- [ ] **Placement reasoning**: When placement is ambiguous (e.g., a margin image could belong to either adjacent paragraph), the system records the decision and rationale in provenance metadata.
- [ ] **Multi-column handling**: Documents with 2-3 column layouts are correctly linearized — text flows in reading order, cross-column elements (spanning images, full-width tables) are placed at the appropriate break point.
- [ ] **Integration with existing pipeline**: The layout map feeds into `build_chapter_html_v1` (or equivalent) so that `<img>`, `<table>`, and `<figure>` tags are inserted at layout-informed positions rather than appended at the end or placed arbitrarily.
- [ ] **Eval**: A benchmark of 10+ pages with mixed layouts (multi-column, images, tables) where human-judged placement accuracy is ≥90%.

## Approach (to be refined)

1. **VLM-based layout analysis**: Send each page image to a VLM and ask for a structured layout map (block types, bounding boxes, reading order). This aligns with the Ideal — AI understands layout from content alone.
2. **Geometric reasoning**: Use bounding box overlap, proximity, and column detection to establish which blocks are spatially associated.
3. **Linearization rules**: Convert the 2D layout into a 1D content stream using reading order + placement heuristics (e.g., images placed before the first paragraph that overlaps their vertical extent).
4. **Fallback**: When VLM layout confidence is low, fall back to source-order insertion with a provenance note.

## Spec Connections

- **Compromise C3** (Heuristic + AI Layout Detection): This story directly works toward eliminating C3. If the VLM-based approach achieves high accuracy, heuristic fallbacks can be reduced.
- **Compromise C5** (Layout Text Trim Heuristics for Crops): A reliable layout map would also improve crop detection by providing spatial context for what's text vs. illustration.
- **Ideal Requirement #5** (Structure): "Decompose the document into semantic parts with provenance. Every piece of output knows where it came from."

## Dependencies

- Story 026 (Onward) provides the first test corpus with complex layouts (genealogy tables, images, multi-section pages).
- Story 125/126 (image crop extraction + validation) provides the image detection pipeline that this story's placement logic would consume.

## Tasks

- [ ] Design the layout map schema (block types, bounding boxes, reading order, confidence)
- [ ] Prototype VLM-based layout extraction on 5 representative pages (multi-column, image-heavy, table-heavy)
- [ ] Implement linearization logic (2D layout → 1D content stream with placement decisions)
- [ ] Build placement provenance (each non-text element records why it was placed where it was)
- [ ] Create eval benchmark (10+ pages, human-judged placement accuracy)
- [ ] Integrate layout map into chapter HTML builder
- [ ] Test on Onward corpus (genealogy pages with tables + images)
- [ ] Test on FF corpus (single-column with inline illustrations — should be trivial/baseline)

## Notes

- Story 026 built **table content fidelity** (correctly transcribing table data). This story addresses the orthogonal problem of **where** tables, images, and other elements belong in the linearized output.
- The Onward book is a good first test case: it has genealogy tables interspersed with narrative text and photos, requiring layout-aware placement.
- For simple single-column documents (most FF gamebooks), this should be a no-op — content is already in reading order.

## Work Log

### 20260312 — Reframed story from original "layout-preserving extractor"
- **Result:** Rewrote story with sharper framing around spatial layout understanding and content linearization.
- **Notes:** Original story was vague ("capture bounding boxes, export layout-aware JSON"). Real need is intelligent placement of non-text elements when linearizing complex layouts to single-column HTML. Story 026 built table fidelity but not spatial layout reasoning.
- **Next:** Prototype VLM-based layout extraction on representative pages.
