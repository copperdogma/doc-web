---
title: Final assembly (portions_final_raw.json)
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

# Story: Final assembly (portions_final_raw.json)

**Status**: Done

---

## Acceptance Criteria
- Build per-portion JSON with spans, source_images, raw_text (prefers clean_text)
- Handles duplicate IDs via suffix
- Traceability to pages preserved

## Tasks
- [ ] Use clean_text fallback chain
- [ ] Assemble images list
- [ ] Suffix duplicates in build
- [ ] Emit JSON with spans/confidence

## Notes
- 

## Work Log
- 20251121-0004 — Build step prefers clean_text with fallback, suffixes duplicates, assembles source_images and spans into portions_final_raw.json
- Pending