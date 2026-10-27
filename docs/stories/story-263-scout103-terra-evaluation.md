---
title: "Scout103 GPT-6.1 Terra source-fidelity evaluation"
status: "Done"
priority: "Medium"
ideal_refs: ["req:3", "req:4", "req:6"]
spec_refs: ["spec:2.1", "spec:3.1", "spec:4.1", "spec:4.2", "spec:6"]
adr_refs: ["ADR-001", "ADR-002"]
depends_on: ["258"]
category_refs: ["spec:2", "spec:3", "spec:4", "spec:6"]
compromise_refs: ["C1", "C3", "C4", "C5", "C6"]
input_coverage_refs: ["scanned-pdf-tables", "handwritten-notes"]
architecture_domains: ["ocr_and_extraction", "doc_web_runtime"]
roadmap_tags: []
legacy_system: ""
---

# Story 263 — GPT-6.1 Terra bounded source-fidelity evaluation

**Status:** Done
**Priority:** Medium
**Spec refs:** spec:2, spec:3, spec:4, spec:8
**Category refs:** spec:2, spec:3, spec:4, spec:8
**Eval refs:** literal-table-fidelity, image-crop-extraction, handwritten-notes-transcription
**Compromise refs:** C1, C4, C6

## Goal and approved plan

Conductor Scout103 item1 selected by Cam's yes on2026-10-26; hard inclusive USD12.
Evaluate exact native OpenAI gpt-6.1-terra through Responses Standard/storefalse.
Source-only table high32768 vs fresh Astra medium8192;13 benchmark crop cases
medium16384 vs fresh exact Gemini3Flash; actual image-entry Barney handwriting
high32768 vs exact Gemini3.7Flash. Public/authored synthetic sources only.
Original sources/prompts/goldens/scorers frozen, single independent call/case,
no subject cache, no paid judge, no semantic retry/effort sweep. First valid
source failure stops only its own task; operational recovery bounded by12USD.
All36clear cells and both I/l holds,13/13crop/mean>=.95/full source preservation,
OCR>=.99 and no invented words. No defaults or production grouping/safety claim.
The selected plan satisfies local plan approval; no material scope change.

## Eval ladder and truth

Root400page perfect intake is deferred: this is a bounded capability decision,
not corpus/physical/document acceptance. C1 OCR remains blocked on handwriting;
C4 detector threshold alone cannot delete C5 helpers. Current best eligible
source evidence and consumer holds: Attempts080/081/083/084; unchanged prompts,
receipts and native pixels preserved. Actual current Onward Gemini3Flash,
source-only Astra; no substitute central harness or runtime changes.

## Acceptance criteria

- [x] Qualify native contract and preserved adapter parity independently.
- [x] Preflight exact matrix, sources, schemas, prices and hard ledger.
- [x] Run progressive fresh comparisons and source-adjudicate findings.
- [x] Record layered task verdicts, raw manifests, registry and scoped validation.
- [x] Build complete.
- [x] Validation complete or explicitly skipped by user.
- [x] Story marked done via /mark-story-done.

## Work log

2026-10-26: fetched origin/main3a7efec9216c7d784700e464a98fc6de9b8a2e02;
isolated codex/scout103-terra-docweb-20261026 under approved worktree root.
Primary remains untouched. Read owner/portable protocols, Ideal/spec/state/graph,
registry, benchmark runbook and current source evidence. Reused Scout102 runner
pattern with explicit native Responses bridge and independent hard12USD ledger;
Google-shaped compatibility usage is eval adapter data, original OpenAI receipt
remains authoritative. Existing owner OpenAI/Google names present through normal
primary.env override, no copy/injection. No secret values stored.

2026-10-26 build complete:33POSTs,USD0.27373875/12,unknown0. Terra normalized
detector13/13/mean.978576923 vsGemini13/13/.958900;51.22%faster at38.69%
highercost.12integral-content clears plusImage000 undecoratedcloth extent
UNRESOLVED, no13/13fullsourceacceptance. Botharms scorer usesgold-axisoracle,
not rawcoordinate/runtimeparity. Bakery22/23+gratuitoushold vsAstra23/23;
Barney.965270<.99 with source substitutions. Exact3.7controlredirect3.8
quarantined,chargepreserved. No semanticretries/effortsweeps. Native/test
qualificationUSD.001752; no paidjudge. Existingprimarycredentials only,
no injection/cleanup. Attempt085/evidence085 contain fullmanifest/closedledger.
No defaults, source policies or goldens changed. Formalclosure/landing unperformed.

2026-10-26 validation complete:119 focused tests, compile, methodology and
whitespace pass;115 archive members independently read back byte/hash exact.
New score appended to retain selected coverage pointer; no golden/defaultchange.
Formal /mark-story-done and landing remain unperformed.

## Closure verification

- [x] Traceability: native request/response hashes, exact model identities,
  sources, producing snapshots and all115 archive members remain preserved.
- [x] Fidelity: table/OCR errors, unresolved cover extent, scorer axis oracle and
  consumer applicability gaps remain explicit; no golden or gate weakened.
- [x] Eval-first and artifact inspection:13 crop pairs and actual driver OCR
  inspected; registry, Attempt085 and evidence updated, runtime unchanged.
- [x] Documentation and dependency: Story258 is Done; accepted ADR001/002 are
  unchanged and no remaining architecture decision is claimed resolved.

2026-10-26 /mark-story-done under authorized finish-and-push: bounded evaluation
scope complete (all task/acceptance and workflow gates met); Story263 Done.
Reuse119focusedchecks; postcollection Ruff formatting/import cleanup preserves
normalized ASTs, with original producing tools retained and no paid calls.
Ruff/compile/methodology/whitespace and archive/source proof cover this closeout.
Remote-main preflight equals original3a7efec base; no integration conflict.
No model adoption, source-policy resolution or production qualification implied.
Return control to finish-and-push; retain worktree and primary unchanged.
