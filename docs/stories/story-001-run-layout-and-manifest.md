---
title: Establish run layout & manifests
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

# Story: Establish run layout & manifests

**Status**: Done

---

## Acceptance Criteria
- Create standard run root output/runs/<run_id>/ with artifacts isolated per run
- Add run_manifest.jsonl to track runs
- Git-ignore outputs/venv/caches
- Move existing outputs into run folders

## Tasks
- [ ] Design run directory schema
- [ ] Implement manifest writer/import
- [ ] Move legacy outputs
- [ ] Update README/docs

## Notes
- 

## Work Log
- 20251121-0000 — Established run layout, manifests, moved legacy outputs to output/runs/ and added run_manifest.jsonl
- Pending