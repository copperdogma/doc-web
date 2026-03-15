---
type: research-report
provider: openai
model: gpt-5-2025-08-07
adr: "ADR-001"
topic: "Source-aware consistency alignment and re-extraction strategy"
status: "COMPLETED_UNREVIEWED"
created: "2026-03-14T23:22:24.991658+00:00"
source-prompt: "research-prompt.md"
response_id: "resp_01988ed8e4e25fd00069b5ece0336c81959616eff16f604181"
---

# OpenAI Research Report

## Run Metadata

- Provider: `openai`
- Model: `gpt-5-2025-08-07`
- Response ID: `resp_01988ed8e4e25fd00069b5ece0336c81959616eff16f604181`
- Status: `completed`
- Tooling: `web_search_preview`
- Input tokens: `50285`
- Output tokens: `7430`
- Total tokens: `57715`

## Raw Output

Below is a decision brief aligned to your sections, with concrete, source-backed recommendations. I call out maturity (mature/reusable vs academic-only) and where recommendations are based on inference. Direct URLs are provided in code blocks under “Evidence”.

1) Existing landscape

- Recommended choice
  - Combine mature layout/table detectors with provenance-friendly outputs, then add schema-matching/record-linkage for consistency alignment:
    - Table/layout detection: Microsoft Table Transformer (TATR, DETR-based) with PubTables‑1M and GriTS metric; IBM DocLayNet models; LayoutParser as wrapper to Detectron2/YOLO models. These are production-reused and actively maintained. ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))
    - Cloud OCR + table parsers when you want managed scale and extra table semantics: AWS Textract Tables (including table titles/footers/types), Google Document AI Form/Layout parsers, Azure Form Recognizer. All have explicit table APIs and stable SLAs. ([docs.aws.amazon.com](https://docs.aws.amazon.com/textract/latest/dg/how-it-works-tables.html?utm_source=openai))
    - Open-source extract/ETL glue with provenance fields: unstructured.io (elements carry source filename/page/coords); pdfplumber for deterministic geometry; LayoutParser for consistent region objects. These are modular and easy to slot into a traceability-first pipeline. ([github.com](https://github.com/Unstructured-IO/unstructured?utm_source=openai))
    - Schema alignment and repeated-structure recognition: classical schema/ontology matching (COMA/COMA++), modern entity/record matching (Ditto), plus table-representation learning (TURL, TaBERT/TAPAS) when column semantics are fuzzy. These are the strongest options for aligning similar structures across runs. (Academic to applied: COMA is academic tool but long-lived; Ditto is research-backed with open code widely adopted in data matching; TURL/TaBERT/TAPAS are academic with growing applied use.) ([dbs.uni-leipzig.de](https://dbs.uni-leipzig.de/research/projects/coma?utm_source=openai))
  - Why: Each piece preserves or enriches structure and can emit coordinates/blocks needed for provenance and reruns. GriTS and cTDaR give objective checks on table structure gains. ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))

- Runner-up
  - OCR-first, OCR-free hybrids (Nougat/Marker/Donut variants) for whole-page Markdown/HTML, then post-hoc normalization. Strong on scientific books but less predictable on genealogical layouts and mixed heading/table blends; better as a complementary pass or cheap pre-screener. (Academic-to-applied.) ([github.com](https://github.com/facebookresearch/nougat?utm_source=openai))

- Avoid
  - HTML-only “normalization-first” strategies as the primary consistency layer. They lack reliable signals to unify semantically identical but visually different structures (e.g., BOY/GIRL vs BOY / GIRL), and you’ll fight drift without source re-reads. Use them only as light canonicalization after source-aware alignment. (Inference based on limitations of HTML sanitizers/canonicalizers vs true schema alignment.) ([en.wikipedia.org](https://en.wikipedia.org/wiki/HTML_Tidy?utm_source=openai))

- Evidence (URLs)
  ```
  Microsoft Table Transformer (TATR) + PubTables‑1M + GriTS: https://github.com/microsoft/table-transformer
  PubTables‑1M paper: https://openaccess.thecvf.com/content/CVPR2022/papers/Smock_PubTables-1M_Towards_Comprehensive_Table_Extraction_From_Unstructured_Documents_CVPR_2022_paper.pdf
  DocLayNet dataset: https://arxiv.org/abs/2206.01062
  LayoutParser: https://layout-parser.github.io/
  AWS Textract tables: https://docs.aws.amazon.com/textract/latest/dg/how-it-works-tables.html
  Google Document AI Form/Layout parsers: https://docs.cloud.google.com/document-ai/docs/form-parser
  Azure Form Recognizer (tables): https://docs.rinkt.com/activities/cognitiveServices/documentAnalysis
  unstructured (open-source): https://github.com/Unstructured-IO/unstructured
  pdfplumber: https://github.com/jsvine/pdfplumber
  COMA/COMA++: https://dbs.uni-leipzig.de/research/projects/coma
  Ditto (entity matching): https://github.com/megagonlabs/ditto
  TURL: https://arxiv.org/abs/2006.14806
  TaBERT: https://aclanthology.org/2020.acl-main.745/
  TAPAS: https://arxiv.org/abs/2004.02349
  ICDAR cTDaR results: https://cndplab-founder.github.io/cTDaR2019/results.html
  ```

2) Deterministic and statistical detection/gating

- Recommended choice
  - Fast, selective “same-structure” detection for gating reruns using cheap, provenance-friendly features:
    - Table-level signatures: column count; header string set and order; header normalization (tokenize, lowercase, strip punctuation and gendered splits BOY/GIRL -> BOY | GIRL); span patterns; average cell density; gridline presence. Cluster with MinHash/Jaccard or SimHash over header n‑grams to group compatible runs across pages/chapters. Mature, deterministic, and cheap. ([cs.princeton.edu](https://www.cs.princeton.edu/courses/archive/spr05/cos598E/bib/broder97resemblance.pdf?utm_source=openai))
    - Tree similarity between HTML table DOMs via tree-edit distance (Zhang–Shasha) for acceptance checks or tie-breaks. Use only after cheap hashing to keep costs down. Mature theory with multiple libs. ([arxiv.org](https://arxiv.org/abs/1805.06869?utm_source=openai))
    - Record linkage on rows (if person names/dates appear repeatedly): blocking on surname/year-of-birth + fuzzy match to detect near-duplicates; use Ditto or classical dedupe to verify a run spans the same family schema. Mature/open-source. ([github.com](https://github.com/megagonlabs/ditto?utm_source=openai))
  - Where it fails
    - Semantic hierarchy shifts (heading “ownership” moves into table header vs preceding H3) and headerless fragments: header-string similarity alone may miss compatible fragments; need visual/positional cues or learned table embeddings (TURL/TaBERT) for robustness. (Academic but useful augmentation.) ([arxiv.org](https://arxiv.org/abs/2006.14806?utm_source=openai))

- Runner-up
  - Sequence alignment for headers/records (Smith–Waterman local alignment) to match column sequences when minor drifts occur; best as a precision tool after hashing/clustering, not primary. (Mature algorithm; heavier CPU.) ([en.wikipedia.org](https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm?utm_source=openai))

- Avoid
  - Pixel-only similarity for runs (SSIM/feature matching) without text/layout cues. It’s brittle across scans and layout reflows and can mis-gate reruns. (Inference based on domain; no reliable structure semantics.)

- Evidence (URLs)
  ```
  Broder MinHash (document resemblance): https://www.cs.princeton.edu/courses/archive/spr05/cos598E/bib/broder97resemblance.pdf
  SimHash (Charikar 2002): https://www.cs.princeton.edu/courses/archive/spring05/cos598E/bib/p380-charikar.pdf
  Zhang–Shasha tree edit distance tutorial: https://arxiv.org/abs/1805.06869
  Python Zhang–Shasha lib: https://zhang-shasha.readthedocs.io/
  Ditto (entity/record matching): https://github.com/megagonlabs/ditto
  Smith–Waterman overview: https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm
  ```

3) Source-aware rerun strategies

- Recommended choice
  - Two-stage, source-aware reruns gated by the detectors above:
    1) Freeze a schema hypothesis per run: derive column headers, spans, and example rows from the highest-confidence instance; persist as a structured hint object (e.g., JSON schema with header list, allowed variants like BOY/GIRL vs BOY|GIRL; examples; acceptance constraints). Use this hint to drive targeted re-extractions on flagged pages to enforce consistency. (Inference pattern; mirrors “prompt freezing” and schema conditioning used in modern table pipelines and TATR’s structure targets.) ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))
    2) Rerun with broader context window: feed adjacent pages (±N) or full chapter when a high ratio of fragments/headerless mini-tables is detected. Cloud parsers can benefit from multi-page context; learned detectors (TATR/DocLayNet-based) benefit from batched inference and consistent thresholds. Use acceptance metrics (below) to keep only improvements. (Tooling mature; approach is practice-driven.)
  - Acceptance/rejection
    - Structure fidelity: GriTS increase vs baseline; cTDaR-style precision/recall on detected cells/rows if you maintain eval labels. ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))
    - Content preservation: row/field coverage must not drop beyond tolerance (e.g., ≤1% tokens or ≤1 row difference) measured by string overlap or record-matching. (Deterministic.)
    - Provenance: every rerun artifact keeps page-level bbox and a W3C PROV record linking it to source page(s) and the schema-hint version used. Mature standards. ([w3.org](https://www.w3.org/TR/prov-overview/?utm_source=openai))
  - When is selective rerun better than starting broader?
    - If runs are mostly consistent with a few drift pages and OCR is costly; when table headers are stable but placements vary (genealogy books often match this). Start with page-level extraction plus selective reruns. When drift rate crosses thresholds (see Section 5), switch to chapter-scope extraction.

- Runner-up
  - Self-consistency style multi-decoding for LLM extractors (sample N, vote) to stabilize header decisions without new OCR. Useful when cost forbids source re-read but you still need semantic stability. Academic-to-applied; good gains shown in LLM literature, but ensure provenance and acceptance checks. ([arxiv.org](https://arxiv.org/abs/2203.11171?utm_source=openai))

- Avoid
  - Blind second passes without frozen schema hints. They often reintroduce drift and erode traceability. (Inference; aligns with observed drift in page-by-page prompting.)

- Evidence (URLs)
  ```
  TATR + GriTS metric: https://github.com/microsoft/table-transformer
  cTDaR competition/evaluations: https://cndplab-founder.github.io/cTDaR2019/results.html
  W3C PROV Overview: https://www.w3.org/TR/prov-overview/
  Self-consistency (LLMs): https://arxiv.org/abs/2203.11171
  ```

4) Role of normalization after reruns

- Recommended choice
  - Keep normalization minimal and deterministic after a source-aware rerun:
    - Deterministic render cleanup: HTML Tidy and safe HTML sanitization (bleach/nh3), normalize whitespace, canonicalize list/table markup, and attach data- attributes for provenance (page, bbox, run-id). Mature and reversible. ([en.wikipedia.org](https://en.wikipedia.org/wiki/HTML_Tidy?utm_source=openai))
    - Canonical XML/DOM diff for change audits: serialize structure in a canonical form (XML C14N for structural snapshots; or consistent HTML serialization) to enable clean diffs and reversions. Mature standard. ([w3.org](https://www.w3.org/TR/xml-c14n/?utm_source=openai))
  - What to avoid
    - Semantic rewriting (e.g., renaming headers) in normalization. That belongs in the rerun phase under a frozen schema. Limit normalization to formatting/canonicalization.
  - When HTML-only normalization is justified
    - As a fallback for trivial heterogeneity (e.g., th vs td in header row, extra wrapper spans) when structure is already aligned by the rerun; or when a page is low value and the gating says “likely same schema” but confidence is just below the rerun threshold.

- Evidence (URLs)
  ```
  HTML Tidy: https://github.com/htacg/tidy-html5
  bleach (sanitization): https://github.com/marksweb/django-bleach
  Canonical XML (C14N): https://www.w3.org/TR/xml-c14n/
  ```

5) Recommended architecture for codex-forge

- Recommended choice (best value now)
  - A “detect → freeze → selective rerun → minimal normalize” architecture:
    1) First pass (AI-first extraction): use your current page-scope extractor; concurrently run cheap detectors to build per-table signatures (headers, spans, column count, density, simple embeddings via SimHash/MinHash). ([cs.princeton.edu](https://www.cs.princeton.edu/courses/archive/spring05/cos598E/bib/p380-charikar.pdf?utm_source=openai))
    2) Group pages into candidate runs via clustering on signatures; elect a canonical representative; freeze a schema-hint object (header set, span rules, examples). (Deterministic + light ML.)
    3) Source-aware selective reruns on flagged pages/regions using the frozen schema hint and broader context (±N pages). For implementation, reuse TATR/DocLayNet models locally, or call Textract/DocAI if managed services fit cost/latency. Keep provenance with W3C PROV records referencing the source page(s), schema-hint version, and acceptance checks. ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))
    4) Acceptance gate: require GriTS/structure-F1 improvement and no loss in row/field coverage vs baseline; otherwise keep the original. ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))
    5) Minimal deterministic normalization: tidy/sanitize, ensure consistent HTML tags, attach provenance data-*. ([en.wikipedia.org](https://en.wikipedia.org/wiki/HTML_Tidy?utm_source=openai))
  - Why: This maximizes fidelity and traceability while keeping OCR re-reads selective.

- Runner-up (highest quality if cost is secondary)
  - Start with run-/chapter-scope extraction for all chapters, with learned detectors (TATR/DocLayNet) and LLM-based schema conditioning from the outset. Accept higher compute and context windows to minimize later reruns, and still keep acceptance gates and provenance. (Tooling mature; higher infra cost.) ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))

- Avoid
  - Relying primarily on HTML normalization or on LLM-only rewriters to “standardize” tables post hoc. It undermines provenance and often drops subtle cells/footers. Use normalization only after structure is consistent from source. (Inference; supported by need for structural metrics like GriTS.)

- What should be AI-driven vs deterministic
  - AI-driven: table/layout detection (TATR/DocLayNet or managed APIs), context-aware re-extraction with frozen schema hints, optional table-embedding similarity (TURL/TaBERT) when header text is weak. ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))
  - Deterministic: gating features (header tokens, counts), clustering (MinHash/SimHash), acceptance checks (GriTS/row coverage deltas), canonical HTML/XML serialization, provenance (W3C PROV). ([cs.princeton.edu](https://www.cs.princeton.edu/courses/archive/spr05/cos598E/bib/broder97resemblance.pdf?utm_source=openai))

- First implementation slice
  - Add a “Run Detector” module after first-pass extraction:
    - Compute per-table signatures and cluster pages into candidate runs.
    - Elect a canonical schema; generate a schema-hint JSON.
    - Selectively rerun only the lowest-consistency pages with ±1 page context using your preferred source extractor; log PROV.
    - Gate on GriTS increase and row/field coverage; fall back if no gain.
    - Apply minimal normalization and emit Dossier artifacts + provenance bundle. ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))

- Metrics to gate rollout
  - Structure accuracy: GriTS vs baseline; cTDaR cell/row precision/recall where possible. ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))
  - Consistency: header-consistency rate within a run; column-count variance; proportion of pages adopting the canonical header.
  - Content preservation: record/field coverage deltas vs baseline.
  - Selectivity: rerun rate (% pages rerun) and OCR cost saved vs chapter-wide reruns.

- Threshold to move to broader extraction granularity
  - If, over a representative corpus:
    - ≥25–30% of pages in a chapter require rerun, or
    - ≥15% of pages still fail acceptance checks after one selective rerun, or
    - header-consistency within a detected run is <90%,
    then switch that recipe to run-/chapter-scope extraction by default. (Heuristics informed by rerun selectivity/cost; inference based on typical operational break-even.)

- Evidence (URLs)
  ```
  TATR & GriTS: https://github.com/microsoft/table-transformer
  DocLayNet: https://arxiv.org/abs/2206.01062
  AWS Textract tables: https://docs.aws.amazon.com/textract/latest/dg/how-it-works-tables.html
  Google Document AI form/layout parsers: https://docs.cloud.google.com/document-ai/docs/form-parser
  MinHash: https://www.cs.princeton.edu/courses/archive/spr05/cos598E/bib/broder97resemblance.pdf
  SimHash: https://www.cs.princeton.edu/courses/archive/spring05/cos598E/bib/p380-charikar.pdf
  W3C PROV: https://www.w3.org/TR/prov-overview/
  ```

Overall recommendation

- Adopt a source-aware consistency strategy: detect repeated structures cheaply, freeze a schema per run, do selective context-aware reruns from source, then perform minimal, deterministic normalization. Start with page-scope + selective reruns for genealogy-style documents; escalate to chapter-scope for recipes crossing the rerun thresholds. Tooling is mature (TATR/DocLayNet, Textract/DocAI, LayoutParser, unstructured/pdfplumber), and provenance can be enforced via W3C PROV and per-cell/page coordinates. ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))

Phased rollout

- Phase 1 (2–3 sprints)
  - Implement Run Detector and schema-hint generation; integrate MinHash/SimHash clustering; add GriTS evaluation; wire PROV records to every artifact. Keep selective reruns limited to ±1 page. ([cs.princeton.edu](https://www.cs.princeton.edu/courses/archive/spr05/cos598E/bib/broder97resemblance.pdf?utm_source=openai))
- Phase 2
  - Add table-embedding assist (TURL/TaBERT) for weak headers; expand context to chapter when drift persists; introduce record-linkage checks for entity-heavy tables (e.g., genealogies). ([arxiv.org](https://arxiv.org/abs/2006.14806?utm_source=openai))
- Phase 3
  - For high-drift recipes, default to run-/chapter-scope extraction; add optional self-consistency decoding for LLM extractors where source re-reads are constrained; standardize canonical HTML/XML serialization and diff-based auditing. ([arxiv.org](https://arxiv.org/abs/2203.11171?utm_source=openai))

Open risks

- OCR variance across reruns (font/layout noise) can still alter cell boundaries; acceptance gates (GriTS + coverage) mitigate but don’t eliminate this. ([zenodo.org](https://zenodo.org/records/2649217?utm_source=openai))
- Table detectors trained on scientific PDFs (PubTables‑1M) may need domain adaptation for genealogy books; expect some fine-tuning or thresholds tuning. ([microsoft.com](https://www.microsoft.com/en-us/research/publication/pubtables-1m/?utm_source=openai))
- Cloud API model/version drift; lock versions and monitor regression via acceptance metrics. ([docs.aws.amazon.com](https://docs.aws.amazon.com/textract/latest/dg/how-it-works-tables.html?utm_source=openai))
- Provenance overhead: PROV graph volume and coordination across modules; requires careful schema for run-id/page/bbox versioning. ([w3.org](https://www.w3.org/TR/prov-overview/?utm_source=openai))

Research gaps

- Robust heading ownership disambiguation (heading-as-header vs separate heading) still benefits from learned multimodal cues; limited off-the-shelf metrics beyond GriTS for this semantic edge case. (Academic gap; inference.)
- Systematic thresholds for switching from selective reruns to chapter-scope are operational heuristics; longitudinal cost/quality studies on your corpus would refine them.
- Comprehensive, domain-specific benchmarks for genealogy-style tables are scarce; you may need an internal labeled set for GriTS/cell-F1 and consistency measures. (Academic gap.)

Notes on maturity vs academic
- Mature/reusable now: TATR/DocLayNet models and repos, AWS Textract/Google DocAI/Azure Form Recognizer, LayoutParser, unstructured/pdfplumber, W3C PROV, MinHash/SimHash gating, Zhang–Shasha for DOM tree distance. ([github.com](https://github.com/microsoft/table-transformer?utm_source=openai))
- Academic/primarily research signals: TURL/TaBERT/TAPAS for table semantics; Nougat/Donut variants for OCR-free page-to-markup on diverse books; conformal/abstention policies for LLMs. Use selectively. ([arxiv.org](https://arxiv.org/abs/2006.14806?utm_source=openai))

Direct source URLs (consolidated)
```
TATR + PubTables‑1M + GriTS: https://github.com/microsoft/table-transformer
PubTables‑1M paper: https://openaccess.thecvf.com/content/CVPR2022/papers/Smock_PubTables-1M_Towards_Comprehensive_Table_Extraction_From_Unstructured_Documents_CVPR_2022_paper.pdf
DocLayNet: https://arxiv.org/abs/2206.01062
LayoutParser: https://layout-parser.github.io/
AWS Textract tables: https://docs.aws.amazon.com/textract/latest/dg/how-it-works-tables.html
Google Document AI form parser: https://docs.cloud.google.com/document-ai/docs/form-parser
Azure Form Recognizer (tables via Cognitive Services): https://docs.rinkt.com/activities/cognitiveServices/documentAnalysis
unstructured (open-source): https://github.com/Unstructured-IO/unstructured
pdfplumber: https://github.com/jsvine/pdfplumber
COMA/COMA++: https://dbs.uni-leipzig.de/research/projects/coma
Ditto (entity matching): https://github.com/megagonlabs/ditto
TURL: https://arxiv.org/abs/2006.14806
TaBERT: https://aclanthology.org/2020.acl-main.745/
TAPAS: https://arxiv.org/abs/2004.02349
MinHash (Broder): https://www.cs.princeton.edu/courses/archive/spr05/cos598E/bib/broder97resemblance.pdf
SimHash (Charikar): https://www.cs.princeton.edu/courses/archive/spring05/cos598E/bib/p380-charikar.pdf
Tree edit distance (tutorial): https://arxiv.org/abs/1805.06869
Zhang–Shasha Python lib: https://zhang-shasha.readthedocs.io/
cTDaR results: https://cndplab-founder.github.io/cTDaR2019/results.html
W3C PROV Overview: https://www.w3.org/TR/prov-overview/
HTML Tidy: https://github.com/htacg/tidy-html5
bleach (sanitization): https://github.com/marksweb/django-bleach
Canonical XML (C14N): https://www.w3.org/TR/xml-c14n/
Self-consistency (LLMs): https://arxiv.org/abs/2203.11171
Nougat OCR: https://github.com/facebookresearch/nougat
```
