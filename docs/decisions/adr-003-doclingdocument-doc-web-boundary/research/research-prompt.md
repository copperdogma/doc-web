---
type: research-prompt
topic: "doclingdocument-doc-web-boundary"
created: "2026-03-20"
---

# Research Prompt

## Context

This repo currently treats `doc-web` as the accepted Dossier-facing intake runtime boundary.

Relevant incumbent context:

- ADR-002 (`docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`) says `doc-web` is the standalone runtime for structural website output and that Dossier should consume it through a versioned contract.
- Story 156 (`docs/stories/story-156-pinned-doc-web-runtime-adoption-and-dossier-readiness.md`) made that boundary executable in-repo: installable `doc_web` package, `doc-web contract --json`, fixture-backed smoke recipe, published handoff docs, and validated bundle/provenance artifacts.
- The current public runtime contract is documented in `docs/doc-web-bundle-contract.md` and `docs/dossier-doc-web-handoff.md`.

Relevant challenger context:

- Scout 011 (`docs/scout/scout-011-external-document-ingestion-systems.md`) found that `Docling` is the strongest external candidate because it spans OCR/layout/structure/provenance and exposes a native typed document representation (`DoclingDocument`) with confidence signals.
- The user explicitly prefers the strongest ingestion engine for Storybook/Dossier over preserving `doc-web` for sunk-cost reasons, and is willing to retire `doc-web` if native `DoclingDocument` support is better.

What has not been proven yet:

- whether stock `Docling` on representative local documents actually meets or beats the incumbent `doc-web` acceptance bar;
- whether Dossier should ingest native `DoclingDocument` directly, use a thin adapter, or keep `doc-web` as the stable boundary;
- which current docs/tests/runtime surfaces would become redundant in each case.

## What I Need

1. **Replacement framing**
   Compare these three end states:
   - keep `doc-web` as the incumbent Dossier-facing boundary and use `Docling` only as a benchmark or internal substrate;
   - hybrid: use `Docling` upstream, but keep a thin repo-owned adapter or handoff layer;
   - native: let Dossier ingest `DoclingDocument` directly and retire or supersede `doc-web`.
   For each, explain when it is the right answer and what would falsify it.

2. **Technical fit against real repo needs**
   Focus on the requirements that matter here, not generic document-AI enthusiasm:
   - provenance and citation/open-original behavior;
   - reading order and semantic structure;
   - tables and repeated structures;
   - scanned PDFs, image-directory intake, and at least one likely future format gap such as born-digital PDF or DOCX;
   - whether `DoclingDocument` is already close to a Dossier-native intake contract or still needs significant custom wrapping.

3. **Operational and architecture fit**
   Assess what matters if this becomes the real Storybook/Dossier ingestion engine:
   - install/pin/upgrade model;
   - runtime dependencies and optional integrations;
   - licensing or packaging constraints that materially change the decision;
   - whether the replacement reduces total system complexity or just moves it.

4. **Migration and deletion plan**
   If native `DoclingDocument` wins, what should be retired, superseded, or retained from the current `doc-web` surface?
   If the hybrid path wins, what is the thinnest acceptable adapter and what should explicitly not survive as a second long-lived runtime?
   If `doc-web` stays incumbent, what is the most honest way to record `Docling` so the question is considered answered for now?

5. **Proof plan**
   Define the minimum local pilot and artifact inspection needed to make this decision credibly in this repo.
   Be explicit about:
   - which document categories should be tested first;
   - what outputs must be inspected manually;
   - what evidence would be enough to recommend keep / hybrid / replace.

## Output Format

For each section, provide:
1. **Recommended choice** with reasoning
2. **Runner-up** and when to choose it instead
3. **Avoid** — options that look attractive but have meaningful downsides
4. **Evidence** — sources, benchmarks, adoption signals, or concrete examples
