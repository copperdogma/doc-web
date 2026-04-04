---
title: Consensus/dedupe/normalize/resolve pipeline
status: Done
priority: Unknown
ideal_refs: []
spec_refs: []
adr_refs: []
depends_on: []
category_refs: []
compromise_refs: []
input_coverage_refs: []
architecture_domains: []
roadmap_tags: []
legacy_system: ''
---

# Story: Consensus/dedupe/normalize/resolve pipeline

**Status**: Done

---

## Acceptance Criteria
- Consensus selects non-overlapping spans with min_conf
- Force full page-range coverage
- Dedupe/normalize IDs (S###/P### + suffixes)
- Resolve overlaps & fill gaps

## Tasks
- [ ] Consensus min_conf + range
- [ ] Dedupe suffix handling
- [ ] ID normalize S/P
- [ ] Overlap resolver gap fill

## Notes
- 

## Work Log
- 20251121-0003 — Consensus min_conf+range, dedupe suffixing, ID normalization S/P, overlap resolution with gap filling
- Pending