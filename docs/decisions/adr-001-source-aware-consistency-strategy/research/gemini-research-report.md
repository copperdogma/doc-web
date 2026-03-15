---
type: research-report
provider: google
model: gemini-2.5-pro
adr: "ADR-001"
topic: "Source-aware consistency alignment and re-extraction strategy"
status: "COMPLETED_UNREVIEWED"
created: "2026-03-14T23:20:25.102420+00:00"
source-prompt: "research-prompt.md"
response_id: "OO21aZ70OJDRz7IP65zX0A4"
---

# Gemini Research Report

## Run Metadata

- Provider: `google`
- Model: `gemini-2.5-pro`
- Response ID: `OO21aZ70OJDRz7IP65zX0A4`
- Tooling: `google_search`
- Prompt tokens: `1274`
- Candidate tokens: `3135`
- Thought tokens: `1215`
- Total tokens: `9354`

## Raw Output

## Source-Aware Consistency and Re-extraction: An Architectural Blueprint for `codex-forge`

This research brief outlines a recommended architecture for `codex-forge` to address representation drift in extracted documents. The core recommendation is a phased shift towards a source-aware consistency model, prioritizing selective, context-aware re-extraction over post-extraction HTML normalization. This approach promises higher fidelity and traceability, aligning with the project's core constraints.

### 1. Existing Landscape: From Layout Analysis to Wrapper Induction

The problem of creating consistent structured data from documents touches on several established fields in computer science.

**Mature Practical Tooling:**

*   **Document Layout Analysis (DLA):** This is a mature field with a wide range of open-source and commercial tools. DLA models, often based on CNNs, Transformers, and GNNs, are adept at segmenting document images into logical regions like text, tables, and images. These tools form the foundational layer for any source-aware processing, as they can identify candidate regions for further analysis. Open-source libraries like `LayoutParser` provide a good starting point for integrating DLA into a pipeline.
*   **Wrapper Induction:** Traditionally used for web scraping, wrapper induction is a technique for automatically generating "wrappers" or extraction rules from labeled examples. This concept is highly relevant to `codex-forge`'s challenge of handling repeated structures. A learned wrapper could represent a canonical form of a recurring table or record, which can then be used to guide re-extraction.

**Promising but Immature Research:**

*   **Selective Re-extraction Strategies:** The specific architectural pattern of a fast, first-pass extraction followed by selective, context-aware re-extraction is more of a strategic inference than a well-documented, off-the-shelf solution. While the components (detection, extraction) are mature, their combination into a formal, reusable pipeline strategy appears to be a leading-edge practice rather than a widely adopted, standardized methodology.
*   **Source-Aware Training for LLMs:** Recent research explores "source-aware training" for large language models, where the model learns to associate knowledge with specific source documents and can cite its sources. This is a promising long-term direction that aligns with `codex-forge`'s emphasis on provenance, but it is currently in the research phase and not a mature, practical tool for immediate implementation.

**Strategic Inference:**

*   The most effective approach for `codex-forge` will be to synthesize a solution by combining mature DLA techniques for region identification with principles from wrapper induction and schema matching to create a targeted re-extraction workflow. This represents a strategic bet on the "back-to-source" hypothesis.

### 2. Detecting and Gating Reruns: Deterministic and Statistical Methods

A crucial part of a selective re-extraction strategy is the ability to cheaply and reliably detect when different parts of a document likely represent the same underlying structure.

**Mature Practical Tooling:**

*   **Tree Edit Distance:** For comparing the structure of extracted HTML, tree edit distance is a powerful and well-established deterministic method. It calculates the minimum number of edits (insert, delete, relabel) needed to transform one tree into another, providing a quantitative measure of structural similarity. This is ideal for identifying tables or lists with slightly different HTML representations. Open-source libraries in various languages are available for implementation.
*   **Record Linkage:** This field provides a suite of techniques for identifying records that refer to the same entity, even with variations in data. For `codex-forge`, this is directly applicable to clustering records from different tables that are conceptually identical despite minor schema differences (e.g., `BOY/GIRL` vs. `BOY`, `GIRL`). Both deterministic (rule-based) and probabilistic ("fuzzy matching") methods are mature.
*   **Sequence Alignment:** Originally from bioinformatics, sequence alignment algorithms can be adapted to compare sequences of document elements (e.g., tags, styles). This can be a useful tool for detecting patterns in the reading order of extracted content.
*   **Clustering Algorithms:** Standard clustering algorithms (e.g., K-Means, hierarchical clustering) can be applied to feature vectors derived from document structures (e.g., from tree edit distances or table schema comparisons) to group similar structures together.

**Promising but Immature Research:**

*   The application of advanced, AI-driven visual similarity models for detecting structurally similar regions directly from images is a promising area but may be more computationally expensive and less interpretable than deterministic methods for initial gating.

**Strategic Inference:**

*   A combination of tree edit distance for structural comparison and record linkage for data-level comparison provides a robust and mature toolkit for detecting candidate regions for re-extraction. These methods are deterministic and computationally cheaper than running a full AI extraction, making them ideal for a "gating" mechanism. A known failure point for these methods is in understanding semantic hierarchies, such as when a heading's ownership of a subsequent table is ambiguous. This is where AI-driven re-extraction will provide the most value.

### 3. Going Back to Source: A Strategy for Reruns

Instead of attempting to repair inconsistent HTML, a source-aware rerun strategy uses the initial pass to build context and then re-extracts problematic regions with a more informed model.

**Mature Practical Tooling:**

*   **Targeted OCR Reruns:** Best practices for Optical Character Recognition (OCR) are well-established. If the initial extraction has low confidence scores or garbled text in a region identified for re-extraction, a targeted rerun of the OCR engine with optimized settings (e.g., higher DPI, different binarization) on just that image segment is a mature and effective technique.

**Promising but Immature Research:**

*   **Schema Hypothesis Stabilization:** The concept of "freezing" a schema hypothesis before rerunning is a strategic inference. The idea is to use the initial pass to infer a canonical schema for a group of similar structures (e.g., the most complete table schema in a cluster). This inferred schema is then provided as a strong hint or constraint to the AI model during the re-extraction of all similar structures. This ensures that the model's output conforms to a consistent structure across the entire run, rather than drifting from page to page.

**Strategic Inference:**

*   A second-pass selective rerun is preferable to a broad, run-scoped extraction from the start when the majority of a document is well-structured and only a minority of regions exhibit inconsistency. This avoids the high cost of re-processing the entire document.
*   The re-extraction process should be guided by a "consistency context" that includes the inferred canonical schema and potentially examples of well-extracted instances of the same structure.
*   **Acceptance/Rejection Strategy:** A re-extracted region should be accepted only if it meets a set of predefined criteria, such as:
    *   It successfully validates against the inferred canonical schema.
    *   It does not result in a significant loss of content compared to the initial extraction.
    *   It has a higher structural similarity (e.g., lower tree edit distance) to the canonical form than the original extraction.

### 4. The Limited Role of Post-Rerun Normalization

After a source-aware consistency pass, the need for a heavy-handed HTML normalization layer is significantly reduced.

**Mature Practical Tooling:**

*   **Deterministic Render Cleanup:** Some level of deterministic cleanup will always be necessary. This includes tasks like fixing malformed HTML, standardizing whitespace, and ensuring consistent styling for rendering purposes. These are low-level, predictable transformations that do not alter the semantic meaning of the content.

**Promising but Immature Research:**

*   The use of AI for semantic rewriting of HTML should be approached with caution. While powerful, it can introduce non-traceable changes and may be better suited for content summarization or re-purposing than for achieving canonical representation.

**Strategic Inference:**

*   After a source-aware rerun, normalization should be limited to deterministic, lightweight canonicalization. The goal is to trust the output of the more context-aware extraction and avoid a second layer of complex, potentially error-prone transformations.
*   HTML-only normalization remains a justified fallback for recipes where the cost of a second pass of OCR and AI extraction is prohibitive, or for documents with very little repeated structure.

### 5. Recommended Architecture for `codex-forge`

**Overall Recommendation:**

The recommended architecture for `codex-forge` is a **phased, dual-pass, source-aware re-extraction model**. This architecture explicitly favors fidelity and provenance by correcting inconsistencies at the source, rather than through post-processing.

**High-Level Workflow:**

1.  **First Pass (Page Scope):** Run the existing AI-first extraction on a page-by-page basis to generate initial HTML and structured data.
2.  **Detection and Clustering:** Use deterministic methods to analyze the first-pass outputs.
    *   Calculate structural similarity scores (e.g., using tree edit distance on HTML structure) for all extracted regions.
    *   Use clustering algorithms to group structurally similar regions.
    *   Within each cluster, use record linkage techniques to identify conceptually similar data.
3.  **Schema Inference and Gating:** For each cluster of similar regions, infer a canonical schema (e.g., by selecting the most comprehensive table structure). If a significant number of regions deviate from this canonical schema, flag the entire cluster for re-extraction.
4.  **Second Pass (Selective Re-extraction):** For each flagged region:
    *   Go back to the original source document image.
    *   Perform a targeted re-extraction using an AI model that is provided with a "consistency context" (the canonical schema, and potentially few-shot examples of good extractions from the same cluster).
5.  **Validation and Integration:** The output of the re-extraction is validated against the canonical schema. If it passes, it replaces the original extraction. The original extraction is archived for provenance.
6.  **Lightweight Normalization:** A final, deterministic HTML cleanup pass ensures render-level consistency.

**AI-driven vs. Deterministic Components:**

*   **AI-driven:**
    *   Initial, page-scoped extraction.
    *   Context-aware, selective re-extraction.
*   **Deterministic:**
    *   Detection of similar structures (tree edit distance, etc.).
    *   Clustering of similar regions.
    *   Schema inference (e.g., rule-based selection of the "best" schema).
    *   Validation of re-extracted data against the inferred schema.
    *   Final HTML render cleanup.

**Phased Rollout:**

1.  **Slice 1: Detection and Analysis.**
    *   Implement the deterministic detection and clustering mechanisms as a purely analytical tool.
    *   **Goal:** To gather data on the prevalence of inconsistent structures and validate the effectiveness of the detection methods.
    *   **Metrics:**
        *   Number of clusters of repeated structures identified per document.
        *   Intra-cluster variance in structure (average tree edit distance).
        *   Precision and recall of the clustering algorithm based on manual review.
2.  **Slice 2: Manual Re-extraction Workflow.**
    *   Build the user interface and workflow for a human operator to review the flagged clusters and manually trigger a re-extraction with a refined context.
    *   **Goal:** To validate the "back-to-source" hypothesis and refine the prompting strategies for context-aware re-extraction.
    *   **Metrics:**
        *   Percentage of re-extractions that result in a more consistent structure.
        *   User feedback on the effectiveness of the refined context.
3.  **Slice 3: Automated Re-extraction and Validation.**
    *   Automate the re-extraction and validation steps.
    *   **Goal:** To create a fully automated, closed-loop system for source-aware consistency.
    *   **Metrics:**
        *   End-to-end reduction in structural inconsistency per document.
        *   Processing time and cost per document.
        *   Rate of acceptance/rejection of automated re-extractions.

**Threshold for Broader Extraction:**

The team should consider moving a recipe to a broader extraction granularity (e.g., chapter-level) instead of repeated targeted reruns when the percentage of pages flagged for re-extraction in a typical document exceeds a certain threshold (e.g., **30-40%**). This indicates that the overhead of the dual-pass approach may outweigh the cost of a single, more context-aware pass on a larger chunk of the document.

### Open Risks and Research Gaps

*   **Cost of Re-extraction:** The primary risk is that the cost of a second pass of OCR and AI model inference could be prohibitively high. The phased rollout is designed to mitigate this by validating the value of the approach before full automation.
*   **Prompt Engineering for Consistency:** Developing the optimal prompting strategy for the re-extraction step will require experimentation. The "consistency context" needs to be carefully designed to guide the AI model without being overly restrictive.
*   **Defining "Better":** The acceptance criteria for a re-extraction need to be robust enough to ensure that the new version is genuinely an improvement and does not introduce new errors or content loss.
*   **Research Gaps:** While the individual components of this architecture are well-understood, there is a lack of published research on the end-to-end implementation and performance of this specific type of dual-pass, source-aware re-extraction workflow for document consistency. `codex-forge` will be breaking new ground in this area.
