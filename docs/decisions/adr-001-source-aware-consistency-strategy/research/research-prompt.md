---
type: research-prompt
topic: "Source-aware consistency alignment and re-extraction strategy"
created: "2026-03-14"
---

# Research Prompt

## Context

You are researching an architecture decision for `codex-forge`, an R&D pipeline that converts scanned PDFs and other difficult documents into traceable HTML and structured artifacts for a downstream product called Dossier.

The pipeline already uses AI-first extraction from source documents, often at page scope. That works well for raw extraction quality, but it creates representation drift: adjacent pages that contain the same underlying structure can produce inconsistent HTML or structure. The same source pattern may appear as different table shapes, heading placements, list styles, or repeated record layouts.

The immediate trigger is a genealogy-book workflow ("Onward to the Unknown"). In one reviewed run, the same genealogy schema appears as:
- a canonical table with columns like `NAME / BORN / MARRIED / SPOUSE / BOY / GIRL / DIED`;
- near-identical tables that still use a combined `BOY/GIRL` header;
- family/context headings embedded inside table headers on one page but emitted as separate headings on the next;
- multiple headerless mini-tables that are clearly fragments of the same conceptual structure.

An initial framing called this an HTML normalization problem. The current hypothesis is that this framing is too narrow. Local repo experience suggests a stronger rule: when a stronger source-aware model is available, going back to source with better context usually beats post-extraction cleanup of weaker results.

The architecture question is therefore:
- should consistency be achieved primarily by selective, context-aware re-extraction from source after first-pass analysis;
- should some recipes move to broader run-aware extraction from the start;
- what deterministic/statistical methods are best for detecting repeated structures, clustering compatible runs, inferring schema hints, and validating reruns;
- and what role should HTML-only normalization still play as a fallback or light canonicalization step?

Project constraints:
- Quality and fidelity matter most.
- Provenance matters. Original artifacts must remain available, and any consistency layer should be inspectable and reversible.
- AI-first is preferred where it clearly outperforms deterministic cleanup.
- OCR/source reads are expensive, so a second pass must be justified and selective by default.
- The system is modular and recipe-driven. The goal is a reusable strategy, not a one-off genealogy hack.

## What I Need

### 1. Existing landscape
Research open-source libraries, commercial systems, and academic work relevant to source-aware consistency, repeated-structure detection, document reranking/rerun strategies, and post-extraction canonicalization.

Questions:
- Are there established systems or research areas for selective re-extraction, wrapper induction, repeated-structure clustering, schema matching, or consistency alignment in document pipelines?
- Which options are mature enough to reuse or adapt, and which are mostly academic?
- Which options are compatible with a traceability-first pipeline?

### 2. Deterministic and statistical detection/gating
Compare deterministic or statistical methods for cheaply detecting when multiple pages or regions probably represent the same underlying structure.

Questions:
- What are the strongest methods for detecting same-schema tables or repeated structures across adjacent pages or chapters?
- How useful are DOM similarity, table schema matching, sequence alignment, clustering, record linkage, header inference, or tree edit distance for run detection and acceptance checks?
- Which libraries or implementation patterns are best value if we want deterministic run detection, schema hints, acceptance/rejection, or provenance reporting?
- Where do these methods fail, especially on semantic hierarchy problems such as heading ownership or mixed heading/table representations?

### 3. Source-aware rerun strategies
Compare approaches that go back to source with broader context instead of repairing extracted HTML.

Questions:
- What is current best practice for targeted reruns or context-aware re-extraction of flagged document regions?
- When is a second-pass selective rerun better than extracting at broader run/chapter scope from the start?
- What patterns exist for freezing a schema hypothesis for a run before rerunning, rather than letting prompts drift page by page?
- What acceptance/rejection strategies work best to ensure reruns improve consistency without dropping content?

### 4. Role of normalization after reruns
Assume the pipeline adopts a source-aware consistency strategy first.

Questions:
- What normalization or canonicalization still makes sense after a better source-aware rerun?
- What should be limited to deterministic render cleanup versus semantic AI rewriting?
- When is HTML-only normalization still a justified fallback?

### 5. Recommended architecture for codex-forge
Recommend the best architecture for codex-forge over the next few stories.

Questions:
- What is the best-value architecture right now?
- What is the highest-quality architecture if cost is secondary?
- What should be AI-driven versus deterministic?
- What should the first implementation slice be?
- What metrics should gate rollout?
- At what threshold of rerun coverage should the team conclude that a recipe needs broader extraction granularity instead of repeated targeted reruns?

## Output Format

For each section, provide:
1. **Recommended choice** with reasoning
2. **Runner-up** and when to choose it instead
3. **Avoid** — options that look attractive but have meaningful downsides
4. **Evidence** — sources, benchmarks, adoption signals, or concrete examples

Then finish with:
- **Overall recommendation** — a concrete architecture choice for codex-forge
- **Phased rollout** — what to build first, second, and later
- **Open risks** — the most important failure modes or unknowns
- **Research gaps** — what still could not be answered confidently
