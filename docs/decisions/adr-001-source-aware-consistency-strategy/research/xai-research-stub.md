---
type: external-research-stub
provider: xai
model: ""
adr: "ADR-001"
topic: "Source-aware consistency alignment and re-extraction strategy"
status: "COMPLETED_UNREVIEWED"
created: "2026-03-14"
source-prompt: "research-prompt.md"
---

**1. Existing landscape**  
**Recommended choice**: Hybrid reuse of mature open-source parsing (Docling or LlamaParse) + LLM schema-guided extraction (inspired by TASER-style agents) + post-processing heuristics from commercial tools like AWS Textract. This directly supports selective re-extraction, repeated-structure clustering, and traceability via JSON outputs with geometry/spans.  

**Runner-up**: Pure academic wrapper induction + tree-edit-distance matching (e.g., zss library on DOM trees). Choose this for fully deterministic, non-AI recipes or when LLM cost is prohibitive.  

**Avoid**: Heavy reliance on page-level commercial black-box services (e.g., raw Textract/Azure without custom postproc) or purely heuristic table extractors (Camelot/Tabula alone) — they lack inspectable provenance or easy schema freezing for drift-prone genealogy schemas.  

**Evidence**: Docling aggregates page-level layout + TableFormer recognition into traceable JSON/Markdown with cell spans and reading-order correction; it processes multi-page documents natively and integrates with RAG pipelines. LlamaExtract uses PER_TABLE_ROW entity segmentation + pattern recognition for repeating tables/lists, applying one schema per entity for consistency without re-extraction. Textract’s amazon-textract-response-parser merges/links multi-page tables via column/header/margin checks while preserving LINK provenance. TASER demonstrates agentic schema-guided extraction + iterative refinement for heterogeneous multi-page tables (directly analogous to genealogy family records). Wrapper induction and tree-edit-distance approaches (classic Kushmerick, modern zss/RTED) provide the structural clustering foundation; clustering papers add line/text DBSCAN/K-means patterns. All are provenance-compatible via block IDs, geometry, or custom attributes.

**2. Deterministic and statistical detection/gating**  
**Recommended choice**: Hybrid structural + embedding clustering: (1) tree-edit-distance (zss) or DOM similarity on extracted HTML for run detection, (2) header/column-signature matching + scikit-learn (DBSCAN/K-means on embeddings or spatial features) for schema hints, (3) record-linkage stats (dedupe lib) for acceptance. Threshold on variance or edit-distance to gate reruns.  

**Runner-up**: Pure deterministic heuristics (column count + exact header match + margin tolerance, as in Textract pipeline). Use when scans are clean and AI overhead is undesirable.  

**Avoid**: Pure semantic LLM clustering per page (too expensive/slow for gating) or simple string Jaccard on raw text (fails on layout variations).  

**Evidence**: Textract validation sequence (column count, identical headers, margin tolerance) catches repeated structures cheaply and rejects noisy fragments. Clustering papers achieve 97% column recognition via line/text DBSCAN on spatial features; reusable with NumPy/SciPy. zss (Zhang-Shasha) and dnted libraries compute normalized tree-edit distance on DOM/HTML trees for exact structural similarity; TEDS metric used in table benchmarks. LlamaExtract pattern recognition (visual separators, row consistency) and header-inference in modern table parsers provide schema hints. Failures on semantic hierarchy (heading ownership) are acknowledged in clustering papers and require AI augmentation.

**3. Source-aware rerun strategies**  
**Recommended choice**: First-pass page extraction → cluster similar structures → freeze schema hypothesis from majority cluster → selective re-extract flagged regions (or adjacent pages) with frozen schema + broader context prompt. Acceptance via post-rerun similarity score + coverage check.  

**Runner-up**: Broader run/chapter-level extraction from the start (LlamaExtract PER_TABLE_ROW or Agentar-style cross-page consolidation) for known repeating recipes.  

**Avoid**: Unconditional page-by-page LLM prompts (source of drift) or full-document re-extraction (OCR cost explosion).  

**Evidence**: TASER’s iterative agent loop freezes/refines schema then re-extracts unmatched holdings until convergence; logs schema versions for provenance. Agentar-Fin-OCR cross-page consolidation + DHR reconstructs hierarchy across fragments using structural alignment and adaptive header splicing. LlamaExtract shows entity-level granularity beats monolithic extraction for exhaustive, consistent repeating records. Textract-style heuristics provide cheap acceptance gating; selective is justified when only 10–30% pages drift (OCR expense rule). Schema freezing via JSON in prompt prevents page-by-page drift.

**4. Role of normalization after reruns**  
**Recommended choice**: Light deterministic HTML canonicalization (BeautifulSoup/lxml tidy: standardize tags, attributes, whitespace) + schema-mapping cleanup (units, repeated headers). Reserve semantic AI rewriting only for unresolvable heading-ownership cases.  

**Runner-up**: Full HTML-only normalization as always-on fallback when rerun coverage exceeds cost threshold.  

**Avoid**: Heavy post-extraction LLM rewriting (loses traceability and introduces new drift).  

**Evidence**: Docling’s assembly stage performs deterministic reading-order correction, header/footer suppression, and span-aware Markdown/JSON normalization after aggregation. Textract LINK mode + custom attributes preserve geometry while allowing deterministic merge. html-similarity and lxml canonicalization patterns are standard for post-cleanup; they are cheap, reversible, and inspectable. Semantic normalization only justified as fallback per project constraints on fidelity/provenance.

**5. Recommended architecture for codex-forge**  
**Recommended choice (best-value)**: Modular recipe-driven pipeline: (1) AI-first page extraction, (2) deterministic/statistical detection & clustering (zss + DBSCAN + header inference), (3) selective schema-frozen re-extraction for high-variance clusters, (4) deterministic HTML canonicalization fallback. Provenance via versioned artifacts (original blocks + rerun logs).  

**Runner-up (highest-quality, cost secondary)**: Broader chapter/run-aware extraction with frozen schema from the start (LlamaExtract-style entity granularity) for recipes known to have repeats.  

**AI-driven vs deterministic**: AI for initial extraction + schema hypothesis; deterministic for detection/gating/acceptance/normalization.  

**First implementation slice**: Detection + gating layer (cluster runs, compute similarity metrics, log schema drift) on existing genealogy recipe — no re-extraction yet.  

**Metrics to gate rollout**: Inter-page structural similarity (tree-edit-distance or schema Jaccard > 0.95), fidelity lift vs ground-truth subsets (>10% consistency gain), rerun coverage (<25% pages), provenance auditability (100% reversible).  

**Rerun-coverage threshold for broader extraction**: >30% pages flagged per recipe → migrate that recipe to chapter-level extraction instead of repeated targeted reruns.  

**Overall recommendation**  
Adopt the hybrid source-aware strategy: page-level first pass → cheap detection/clustering → selective schema-frozen re-extraction → deterministic normalization. This beats pure HTML normalization (too narrow) while respecting OCR cost, traceability, and modularity. It reuses Docling/LlamaParse + Textract heuristics + zss clustering with minimal new code.  

**Phased rollout**  
1. Detection/gating + metrics dashboard (1–2 stories).  
2. Schema freezing + selective re-extract for flagged regions (next 2 stories).  
3. Broader extraction migration for high-rerun recipes + full provenance UI.  
4. Production monitoring + fallback normalization tuning.  

**Open risks**  
- False-positive clusters trigger unnecessary reruns (cost creep).  
- Schema-freezing misses genuine variations (e.g., heading ownership drift).  
- OCR quality variance across scans makes gating noisy.  
- Over-reliance on embeddings for noisy genealogy fonts.  

**Research gaps**  
No public benchmarks specifically measure “representation drift” across pages for genealogy-style repeated records; cost-benefit studies of selective vs. broader re-extraction in OCR-heavy pipelines are sparse; open-source genealogy-specific pattern libraries are absent (general table tools must be adapted).
