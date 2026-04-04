---
title: Audit model lineup vs latest OpenAI sheets
status: Obsolete
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

# Story: Audit model lineup vs latest OpenAI sheets

**Status**: Obsolete

---

## Acceptance Criteria
- Inventory every OpenAI model currently relevant to codex-forge (GPT-5.1 family, GPT-5 mini/nano/pro, GPT-5.1-Codex-Max, GPT-4.1 family, legacy baseline) with pricing, context, and capability notes pulled from official model sheets.
- Compare our default model choices in settings/recipes to the current best value (quality per $) and flag any recommended swaps or optional upgrades.
- Document evidence (links or citations) dated within the last 7 days to confirm recency.
- Produce a concise recommendation table and next steps for updating settings/recipes.

## Tasks
- [x] Gather latest official model sheets and release notes (pricing, context, modalities, tool support, variants).
- [ ] Compare codex-forge defaults (currently `gpt-4.1-mini` primary; `gpt-5` optional boost) against current catalog.
- [ ] Propose configuration changes (per stage) balancing quality, latency, and cost; include long-context vs standard.
- [ ] Update AGENTS/settings examples if we swap defaults; validate driver/recipes still runnable.

## Findings (Nov 26, 2025, source: openai.com)
- **GPT-5.1** flagship: $1.25 / $0.125 cached / $10 per 1M input/output; supports web/file search and structured outputs; snapshots available (gpt-5.1-2025-11-13). citeturn0search0turn0search6
- **GPT-5 mini / nano / pro**: cheaper tiers at $0.25 / $0.05 / $15 input per 1M with proportional output; mini/nano attractive for high-volume light steps. citeturn0search0
- **GPT-5.1-Codex-Max** (Nov 19, 2025): frontier coding/agentic model, same rates as GPT-5.1-Codex; optimized for long tasks with multi-context compaction. citeturn0search1turn0search7
- **GPT-4.1 family** pricing: $2.00 / $0.50 / $8.00 (base), $0.40 / $0.10 / $1.60 (mini), $0.10 / $0.025 / $0.40 (nano); still viable where tool parity is sufficient. citeturn0search3
- **Priority processing** option exists with higher SLAs; GPT-5.1 priced at $2.50 / $0.25 / $20 per 1M for priority lanes. citeturn0search5
- **Legacy catalog** (4o/3.5/etc.) remains but offers worse $/quality versus 4.1/5.x lines. citeturn0search8

## Early Recommendations (draft)
- Swap default generation model to **gpt-5 mini** for cost-effective stages (cleaning/portionization/enrich) and keep **gpt-5.1** or **gpt-5.1-Codex-Max** as an opt-in “boost” for alignment-sensitive steps (resolution, enrichment once built).
- Keep **gpt-4.1-nano** as fallback for bulk heuristic passes or unit tests to control spend.
- Evaluate **priority processing** only for latency-sensitive interactive tools; otherwise stay on standard pricing.
- Add model aliases/snapshots in settings to lock behavior (`gpt-5.1-2025-11-13`) for reproducibility.

## Work Log
### 20251221-1600 — Marked obsolete
- **Result:** Success.
- **Notes:** Superseded by story-076 (AI vision engine evaluation) and subsequent GPT‑5.1 pipeline work; no further action planned here.
- **Next:** None.
### 20251126-1230 — Source collection
- **Result:** Compiled current model/pricing info from OpenAI pricing pages, model docs, and release notes; noted new GPT-5.1-Codex-Max and priority processing tier.
- **Next:** Audit repo configs to see where `gpt-4.1-mini`/`gpt-5` are set; draft swap matrix and cost deltas per stage.
