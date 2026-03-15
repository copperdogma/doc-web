---
type: external-research-stub
provider: anthropic
model: "Claude Opus"
adr: "ADR-001"
topic: "Source-aware consistency alignment and re-extraction strategy"
status: "COMPLETED_UNREVIEWED"
created: "2026-03-14"
source-prompt: "research-prompt.md"
---

# Architecture decision: cross-page consistency for codex-forge

**The strongest strategy for eliminating representation drift is a two-pass "discover-then-constrain" pipeline — not post-extraction HTML normalization.** Research across wrapper induction, schema matching, LLM prompting, and document AI converges on a clear conclusion: when a better source-aware model is available, going back to source with schema context outperforms any amount of deterministic cleanup on weaker first-pass output. The most important finding is that OpenAI Structured Outputs and equivalent constrained-decoding modes now achieve **100% schema adherence**, meaning a frozen schema from Pass 1 can eliminate structural drift in Pass 2 by construction. Deterministic detection (fingerprinting, clustering) cheaply identifies which pages need reruns, and light canonicalization handles only the cosmetic residue. This architecture is reusable across recipes, preserves provenance, and keeps AI costs selective.

---

## 1. The landscape favors schema-guided re-extraction over post-hoc repair

The most directly relevant system in the literature is **TWIX** (UC Berkeley, May 2025), which clusters phrase spatial locations across multi-page templatized documents to discover consistent field templates, then uses an ILP solver to assemble a global template and an LLM for semantic verification. After template inference, extraction runs **520× faster and 3,700× cheaper** than vision-LLM baselines while outperforming Amazon Textract, Azure Form Recognizer, and GPT-4 Vision by 25% F1. TWIX validates the core architectural hypothesis: discover structure first, then enforce it.

Two other systems anchor the pattern. **EVAPORATE** (Stanford, 2023) uses LLMs to infer schemas from heterogeneous document collections and then synthesizes reusable Python extraction functions, achieving a **110× cost reduction** versus direct LLM inference through weak-supervision aggregation of multiple candidate functions. **LMDX** (Google, ACL Findings 2024) adapts LLMs for document information extraction by encoding layout via coordinate tokens in prompts containing the target schema, enabling zero-shot extraction of singular, repeated, and hierarchical entities with grounding guarantees.

Classic wrapper induction systems (ROADRUNNER, DEPTA, MDR, FiVaTech) are research-only with no maintained implementations and are designed for templated web pages rather than AI-extracted HTML. They are not viable for direct adoption, though the underlying principle — detect repeated structure, infer a template, enforce it — is exactly the codex-forge pattern.

**Recommended choice**: Adopt the TWIX/EVAPORATE/LMDX pattern — schema discovery from initial extraction, followed by schema-constrained re-extraction. This is the only approach with strong published evidence of cross-page consistency improvement.

**Runner-up**: MinerU (54.6K GitHub stars) has built-in cross-page table merging and could serve as a preprocessing step for table continuations. Docling (37K stars) offers the strongest provenance support (DoclingDocument preserves page assignment, bounding boxes, reading order) and would be a good base pipeline if codex-forge ever needs one.

**Avoid**: Pure post-extraction schema alignment using only Valentine or similar schema matchers. While Valentine is production-ready (pip-installable, implements Cupid, COMA, SimilarityFlooding), schema matching between extracted DataFrames cannot recover structural information that was never extracted correctly. It is valuable for *detection* but not sufficient for *correction*.

Among document AI models, **Granite-Docling-258M** (IBM, early 2026) is notable as a production VLM using DocTags markup for single-pass extraction under Apache 2.0. For specialized schema-guided extraction at scale, **Schematron-8B/3B** (Inference.net) processes messy HTML into schema-compliant JSON at 1–2% of frontier-model cost. Neither solves cross-page consistency natively, but both reduce the cost of targeted reruns.

---

## 2. Cheap detection tiers make selective reruns practical

The core question for gating is: how cheaply can we detect that pages share the same underlying structure and flag the ones that drifted? The answer is a tiered pipeline that moves from cheap exact checks to progressively more expensive fuzzy matching, and completes in under two minutes for a 500-page document.

**Tier 0 — Table schema fingerprinting** (O(n), <1 second for 500 pages). For each extracted table, compute a fingerprint: `(column_count, normalized_header_texts, has_thead, colspan_pattern)`. Exact fingerprint matches identify pages that already agree structurally. This alone catches the easy cases — pages where the vision model produced identical column headers in the same order. The key implementation detail is normalizing header text (lowercase, strip whitespace, sort for order-invariant matching) and expanding colspan/rowspan to effective column counts before fingerprinting.

**Tier 1 — MinHash/LSH screening** (O(n), ~5 seconds). Using the `datasketch` library, generate k-gram shingles (k=3) from the DOM tag sequence of each page's table region, compute MinHash signatures (128 permutations, ~512 bytes per page), and index into an LSH structure with a Jaccard threshold of 0.5. This identifies structurally similar candidate pairs sub-linearly. At 128 permutations, Jaccard estimation error is ±0.08 — sufficient for screening. The datasketch library supports Redis backends for persistent indexes across pipeline runs.

**Tier 2 — Tag-sequence similarity scoring** (O(n²) on candidates, ~60 seconds). For candidate pairs from Tier 1, serialize each table's DOM to a tag-name sequence using `lxml` and compute similarity via Python's built-in `difflib.SequenceMatcher` (Ratcliff/Obershelp algorithm). This returns a 0.0–1.0 ratio that captures structural similarity while ignoring content. Prior work (page-compare, TeamHG-Memex) found optimal **F1 of 0.944 at a threshold of 0.35** on page identity detection using this exact approach. The html-similarity library wraps this in a one-liner but is unmaintainable; the same logic is ~20 lines of custom code.

**Tier 3 — HDBSCAN clustering** (~1 second). Feed the pairwise distance matrix from Tier 2 into `sklearn.cluster.HDBSCAN` with `min_cluster_size=2` and `metric='precomputed'`. HDBSCAN automatically discovers the number of structural clusters and labels noise points (structurally unique pages) as -1. Each cluster represents a "structural run" — pages sharing the same underlying table schema. The membership probability returned by HDBSCAN serves directly as a confidence gate.

**Tier 4 — APTED edit mapping for provenance** (O(k) on cluster centroids, seconds). For each cluster, compute APTED (All Path Tree Edit Distance) between the cluster centroid and each member. APTED returns the actual node-to-node edit mapping, enabling provenance reporting: "cell X in page A maps to cell Y in page B, with these specific edits." The `apted` Python library (MIT) supports custom insert/delete/rename costs and per-edit-operation configuration.

**Tier 5 — Schema inference** (per cluster). Apply header-inference heuristics: check for `<th>` elements, compare first-row content types against subsequent rows, compute frequency of row-0 cell values across the cluster (>50% frequency = header text, not data). Take majority vote per column position for the canonical header. Report per-column confidence based on cluster agreement ratio.

**Recommended choice**: The full five-tier pipeline. Tiers 0–3 constitute the minimum viable detection system. Total cost for a 500-page document: **under two minutes on a single core, zero API calls**.

**Runner-up**: PQ-Gram distance (O(n log n) per comparison) as a substitute for tag-sequence LCS at Tier 2. PQ-Gram is a proven lower bound on tree edit distance with tunable ancestor/sibling context parameters (default p=2, q=3). It's marginally more principled than sequence-based similarity but requires importing the `pqgrams` library from GitHub rather than using stdlib.

**Avoid**: Running APTED or Zhang-Shasha across all page pairs (O(n²) × O(n³) per pair). Tree edit distance is too expensive for screening — reserve it for provenance on final cluster assignments. Also avoid pure DOM-hash exact matching as the sole detector; semantically identical tables that differ by a single wrapper element will hash differently.

The critical failure mode for all deterministic methods is **semantic hierarchy ambiguity**: a heading embedded inside a table header on one page but emitted as a separate `<h3>` on the next page looks structurally different to every metric above. This is precisely the class of problem that requires source-aware re-extraction rather than post-hoc detection alone. The detection tiers identify *which* pages drifted; re-extraction fixes *why* they drifted.

---

## 3. Two-pass schema-constrained re-extraction is the strongest strategy

The core of the architecture is a two-pass pipeline where Pass 1 discovers structure and Pass 2 enforces it. The strongest evidence for this comes from three independent findings: (1) LangExtract (Google) explicitly documents that "a multi-extraction pass of 2 or more ensures that the output schema is on par with the schema and attributes you provided"; (2) **OpenAI Structured Outputs achieve 100% schema adherence** via constrained decoding, compared to <40% for unconstrained JSON mode; (3) prompt caching reduces the marginal cost of Pass 2 to **15–30% of Pass 1** with Anthropic (90% cached-read discount) or 40–60% with OpenAI (50% automatic discount).

The recommended extraction flow is:

**Pass 1 — Page-scope extraction + schema discovery.** Extract all pages independently at page scope (current approach). Then run the Tier 0–5 detection pipeline to cluster pages by structural similarity, infer canonical schemas per cluster, and flag pages whose structure diverges from their cluster's canonical form. This pass produces the raw extraction artifacts that are preserved as provenance.

**Pass 2 — Schema-constrained selective re-extraction.** For flagged pages only, re-extract using the frozen canonical schema. The prompt includes: (a) the target schema as a JSON Schema or HTML template, (b) 1–2 exemplar pages from the same cluster that already conform to the canonical form, and (c) explicit instructions to match the schema exactly. Use Structured Outputs (OpenAI) or tool-use mode (Anthropic) for constrained decoding. Anthropic's documentation recommends 3–5 examples wrapped in `<example>` tags; practitioner testing confirms Claude 3.5 Sonnet "captures subtle writing patterns and maintains them reliably across multiple outputs" while GPT-4o "often drifts from the established style." For cost optimization, structure prompts with static content (system prompt, schema, examples) as a prefix to maximize cache hits.

**Schema freeze timing** matters. The recommended pattern is: infer from the first 3–5 pages of a detected structural run, freeze the schema, and apply it to remaining pages. If detection finds that >15% of a run's pages fail schema conformance after re-extraction, this is the threshold signal that the recipe should switch to broader extraction granularity (section or chapter scope) rather than continuing page-level reruns.

**Acceptance testing for reruns** combines four checks: (1) schema conformance — does the output validate against the frozen JSON Schema? (2) row-count preservation — does the re-extracted table have at least as many data rows as the original? (3) content preservation — is the Jaccard similarity of flattened text content between original and re-extracted >0.95? (4) structural similarity — is the tag-sequence similarity between re-extracted output and canonical form >0.85? Only accept re-extractions that pass all four checks; otherwise retain the original and flag for manual review.

**Recommended choice**: Two-pass with page-scope extraction in Pass 1 and schema-constrained selective re-extraction in Pass 2, gated by the deterministic detection tiers. This is the best-value architecture because it adds minimal cost (~7.5% over first pass at a 15% rerun rate with prompt caching) while solving the consistency problem at its source.

**Runner-up**: Run-aware extraction from the start — process multi-page structural runs as single extraction units using long-context models (128K+ tokens). A 50-page run at ~2K tokens/page fits in a single context window. This produces inherently consistent output because the model sees all pages together. The trade-offs are: higher per-page cost (long-context pricing), degraded accuracy in the middle of long contexts ("lost in the middle" effect), larger error blast radius (a bad extraction corrupts the entire run), and harder provenance tracking. Choose this when >30% of pages in a recipe consistently need re-extraction — at that point, the two-pass overhead exceeds the cost of broader initial extraction.

**Avoid**: Self-consistency extraction (extracting each page 3–5 times and voting). This multiplies cost by 3–5× with marginal improvement over schema-constrained single extraction. Also avoid using cheap models (GPT-4o-mini, Haiku) for Pass 2 re-extraction; the schema constraint handles structural consistency, but content accuracy requires a capable model. Use cheap models only for structural triage (classifying pages as "needs re-extraction" vs. "already consistent").

**Cost model for a 100-page document** (using Claude Sonnet-class pricing at $3/M input, $15/M output, with 90% cache discount):

| Phase | Pages | Input tokens/page | Output tokens/page | Cost |
|-------|-------|-------------------|-------------------|------|
| Pass 1 (all pages) | 100 | ~3,000 | ~2,000 | ~$3.90 |
| Detection (deterministic) | 100 | 0 | 0 | ~$0.00 |
| Pass 2 (15% rerun, cached) | 15 | ~4,000 | ~2,000 | ~$0.47 |
| **Total** | | | | **~$4.37** |

This represents a **12% cost increase** over extraction-only for a significant consistency improvement.

---

## 4. Light canonicalization still has a role — but a narrow one

After schema-constrained re-extraction, the remaining normalization work is strictly cosmetic. The boundary principle is: **"If a human could disagree about the right answer, it requires semantic understanding and belongs in the AI pass, not the normalization layer."**

Ten transformations should **always run** as a deterministic post-processing step, regardless of extraction quality:

- **Whitespace normalization**: collapse runs of whitespace to single spaces in non-`<pre>` content, trim cell text, remove whitespace-only text nodes in structural contexts. LLMs produce inconsistent whitespace across calls.
- **Attribute ordering**: sort HTML attributes alphabetically within each element. This is purely cosmetic but dramatically improves diffing, hashing, and deduplication downstream.
- **Unicode NFC normalization**: W3C-recommended. Prevents invisible mismatches between composed and decomposed Unicode in class names, IDs, and content.
- **Well-formedness repair**: parse through `lxml.html.fromstring()` and re-serialize. Catches any malformed output silently.
- **Inline CSS property sorting**: alphabetize properties within `style=""` attributes, normalize whitespace around colons and semicolons, add trailing semicolons.
- **Boolean attribute normalization**: standardize `checked="checked"` to `checked` (or vice versa — pick one).
- **Consistent quoting**: double quotes for all attribute values.
- **Void element normalization**: standardize `<br/>` vs `<br>` to one form.
- **Character entity normalization**: `&amp;amp;` → `&amp;` consistently.
- **Default attribute removal**: strip `colspan="1"` and `rowspan="1"` (these are implicit defaults).

This layer must be **idempotent** (`f(f(x)) == f(x)`) and must **never** touch heading levels, table header detection (`<td>` → `<th>`), list-vs-paragraph decisions, paragraph merging/splitting, or any transformation where the correct answer requires semantic understanding of the content.

**Recommended tool stack**: `lxml` as the core parser/serializer (C-based, fast, production-grade), `pytidylib` (Python bindings to HTML Tidy 5.8) for well-formedness repair, and `lxml.html.diff` for generating pre/post audit diffs. `nh3` (Rust-based, 20× faster than deprecated Bleach) for allowlist-based sanitization if needed. No additional libraries required — the normalization pipeline is ~100 lines of custom Python on top of lxml.

**Recommended choice**: A thin, deterministic normalization layer that runs on every extraction output (Pass 1 and Pass 2) and handles only the ten cosmetic transformations above. Store both raw and normalized versions with a diff artifact for auditability.

**Runner-up**: Adding `<thead>`/`<tbody>` wrapper insertion and empty-element removal to the deterministic layer. These are borderline — they change DOM structure and may affect downstream selectors, but they improve rendering consistency. Include them as opt-in per-recipe configuration rather than global defaults.

**Avoid**: Deterministic tag conversion (`<b>` → `<strong>`, `<i>` → `<em>`). These change semantic meaning (presentational vs. emphasis) and the correct choice depends on whether the source document used bold for emphasis or for visual weight. Also avoid deterministic table row/column removal based on "emptiness" heuristics — empty cells are structurally meaningful in many table schemas.

---

## 5. The recommended architecture for codex-forge

### Best-value architecture (recommended for next few stories)

The architecture has four layers, each with clear responsibilities:

**Layer 1 — Page-scope extraction** (existing). Extract each page independently using the current AI-first approach. Preserve all raw artifacts as provenance. No changes needed here.

**Layer 2 — Deterministic detection and clustering** (new, first build priority). Implement the five-tier detection pipeline: table schema fingerprinting → MinHash/LSH screening → tag-sequence similarity → HDBSCAN clustering → schema inference. This layer runs entirely on extracted HTML with no API calls. It produces: (a) a cluster assignment for each page, (b) a canonical schema per cluster, (c) a list of pages flagged for re-extraction, and (d) a confidence score per assignment. The output is a "consistency report" that is inspectable and drives Layer 3.

**Layer 3 — Schema-constrained selective re-extraction** (new, second build priority). For flagged pages, re-extract using the frozen canonical schema from Layer 2, 1–2 exemplar pages from the same cluster, and constrained decoding (Structured Outputs or tool-use mode). Apply acceptance testing (schema conformance + row count + content preservation + structural similarity). If accepted, the re-extracted version becomes the primary artifact; the original remains available as provenance. If rejected, retain the original and flag for manual review.

**Layer 4 — Light canonicalization** (new, third build priority). The ten deterministic transformations described in Section 4, applied to all outputs (both original and re-extracted). Produces the final canonical HTML with a diff artifact against the pre-normalization version.

### Highest-quality architecture (if cost is secondary)

Add two enhancements to the base architecture:

**Enhancement A — Long-context schema discovery.** Instead of inferring schemas from per-page extractions, send 10–20 representative page images to a long-context model (Gemini 2.5 Pro with 1M context, or Claude with 200K) with the prompt: "Analyze these pages and describe every distinct table schema you observe, including column definitions, header patterns, and structural variants." This produces a higher-quality schema hypothesis than inference from extracted HTML alone, because it works from source rather than from potentially-drifted extractions.

**Enhancement B — Self-consistency validation on critical pages.** For pages where acceptance testing produces borderline scores, extract 3 times with temperature >0 and use majority voting per cell. Reserve this for high-value documents only — it triples the cost of flagged pages.

### What should be AI-driven versus deterministic

| Task | AI-driven | Deterministic | Rationale |
|------|-----------|---------------|-----------|
| Page-scope extraction | ✓ | | Core competency of vision models |
| Schema discovery | ✓ (highest quality) or deterministic (good enough) | ✓ (header heuristics, clustering) | Deterministic is cheaper and sufficient for well-structured tables; AI is better for ambiguous layouts |
| Drift detection | | ✓ | Fingerprinting and clustering are fast, reliable, and require no API calls |
| Re-extraction with schema | ✓ | | Must go back to source image with context |
| Acceptance testing | | ✓ | Schema validation, row counts, and similarity scores are deterministic |
| Light canonicalization | | ✓ | Cosmetic transformations must be deterministic and idempotent |
| Heading ownership resolution | ✓ | | Inherently semantic — requires understanding content |

### First implementation slice

Build Layer 2 (detection) first, as a read-only diagnostic tool that runs on existing extraction output and produces a consistency report. This has zero risk (no changes to extraction), provides immediate visibility into drift patterns across all recipes, and validates the detection approach before investing in re-extraction infrastructure. The minimum viable version is: table schema fingerprinting + tag-sequence similarity + HDBSCAN clustering. Libraries: `lxml`, `difflib` (stdlib), `scikit-learn` (HDBSCAN), `datasketch`. Estimated implementation: **2–3 days for a working prototype**.

### Metrics that should gate rollout

- **Structural consistency rate**: percentage of pages in a run whose table schema fingerprint matches the cluster canonical form. Target: **>95%** after full pipeline (Layer 1 + 2 + 3 + 4), up from the current estimated ~70–80%.
- **Content preservation rate**: percentage of re-extracted pages where flattened text Jaccard similarity to original is >0.95. Target: **>99%**. Below this suggests the rerun is dropping data.
- **Rerun acceptance rate**: percentage of re-extractions that pass acceptance testing. Target: **>85%**. Below 85% suggests the schema hypothesis is wrong or the source material genuinely varies.
- **Rerun coverage**: percentage of pages in a run that require re-extraction. Monitor this per recipe.

### When to switch from targeted reruns to broader extraction granularity

**If >30% of pages in a recipe consistently require re-extraction across multiple documents**, the recipe should move to section-scope or run-scope extraction from the start. At 30% rerun coverage with prompt caching, the cost of two-pass page-level extraction approaches the cost of single-pass section-level extraction, while the latter produces inherently consistent output. The 30% threshold should be computed over at least 5 documents per recipe to avoid reacting to single-document outliers.

---

## Overall recommendation

**Build a four-layer pipeline: page-scope extraction → deterministic drift detection → schema-constrained selective re-extraction → light canonicalization.** This architecture solves representation drift at its source (re-extraction with context) rather than papering over it (HTML normalization), while keeping AI costs selective through cheap deterministic gating. It is recipe-agnostic, preserves full provenance (raw + re-extracted + normalized versions with diffs), and degrades gracefully — if detection finds no drift, Layers 3 and 4 are no-ops.

## Phased rollout

**Phase 1 (1–2 weeks)**: Build the deterministic detection layer as a diagnostic tool. Implement table schema fingerprinting, tag-sequence similarity, and HDBSCAN clustering. Run against existing "Onward to the Unknown" extraction output and at least two other recipes. Produce consistency reports. Validate that the detection correctly identifies the known drift patterns (headerless mini-tables, BOY/GIRL header variants, embedded vs. separate headings).

**Phase 2 (2–3 weeks)**: Build the schema-constrained re-extraction layer. Implement schema freezing from cluster centroids, few-shot prompt construction with 1–2 exemplar pages, and acceptance testing. Integrate with prompt caching. Run on "Onward to the Unknown" and measure structural consistency rate before and after. Target: move from ~75% to >95% consistency.

**Phase 3 (1 week)**: Build the light canonicalization layer. Implement the ten deterministic transformations on lxml. Add provenance storage (raw + normalized + diff). This is the lowest-risk, lowest-value layer and should be built last.

**Phase 4 (ongoing)**: Instrument rerun coverage per recipe. When a recipe exceeds 30% rerun rate, prototype section-scope extraction for that recipe. Evaluate whether long-context schema discovery (Enhancement A) is worth the cost for high-value recipes.

## Open risks

**Schema inference from drifted extractions may compound errors.** If Pass 1 extraction is bad enough, the canonical schema inferred from clustering may itself be wrong. Mitigation: Enhancement A (long-context schema discovery from source images) for high-value documents, and manual review of inferred schemas for the first few runs of each recipe.

**Heading ownership is unsolved by deterministic detection.** The specific case where a family heading is embedded in a table header on one page but separate on the next is a semantic problem that no fingerprinting or clustering method will reliably detect. This requires AI-driven resolution, either during re-extraction (by including heading-association instructions in the schema prompt) or as a separate heading-normalization step.

**Acceptance testing may be too conservative.** If the acceptance test rejects valid re-extractions (e.g., because the original had hallucinated extra rows that inflate the row-count baseline), the pipeline silently retains bad data. Mitigation: track rejection reasons and review a sample of rejected re-extractions to calibrate thresholds.

**Context window costs will shift.** The cost/quality trade-offs for page-scope vs. section-scope extraction are sensitive to model pricing and context-window capabilities, both of which change quarterly. The 30% rerun threshold should be recalibrated when major pricing changes occur.

## Research gaps

**No benchmark exists for cross-page structural consistency.** All table extraction benchmarks (PubTables-1M, FinTabNet, SciTSR) evaluate per-table accuracy. PubTables-v2 addresses multi-page tables but not schema consistency across independent tables. codex-forge could contribute a benchmark here.

**Optimal schema-freeze timing is not studied.** The recommendation to infer from 3–5 pages is based on practitioner heuristics, not published research. How many pages are needed for reliable schema inference? How should the system handle genuine mid-document schema changes (e.g., a genealogy book that switches from a 7-column to a 5-column format in a new chapter)?

**Heading-table association lacks reliable deterministic methods.** The question of whether an `<h3>` belongs to the preceding or following table is poorly addressed in the literature. Positional heuristics (the heading "owns" the next table sibling if no intervening block elements exist) work in simple cases but fail when LLM extraction inserts spurious wrapper elements.

**Constrained decoding for HTML is less mature than for JSON.** OpenAI Structured Outputs and guided-json achieve 100% schema adherence for JSON output. Equivalent guarantees for HTML output (where the "schema" is a DOM structure template) are not available from any current API. If codex-forge's output format is HTML rather than JSON, schema-constrained re-extraction requires either converting the problem to JSON extraction (extract data as JSON, then render to canonical HTML deterministically) or accepting that HTML-mode extraction will have residual cosmetic variation that the canonicalization layer handles.
