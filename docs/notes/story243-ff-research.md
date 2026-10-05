# Story 243: Fighting Fantasy corpus research

Read-only discovery, 2026-10-05. No API calls or source/run edits. Existing
records are navigation evidence candidates, not a newly source-verified golden.

## Corpus split and provenance

All paths below are relative to `/Users/cam/Documents/Projects/codex-forge/`.

Development: Deathtrap Dungeon.

- Source: `input/06 deathtrap dungeon.pdf`.
- OCR: `output/runs/ff-deathtrap-dungeon-small/03_ocr_ai_gpt51_v1/pages_html.jsonl`.
- Sections: `output/runs/ff-deathtrap-dungeon-small/13_portionize_html_extract_v1/portions_enriched.jsonl`.
- Final: `output/runs/ff-deathtrap-dungeon-small/gamebook.json`.
- `output/run_manifest.jsonl` records recipe `recipe-ff.yaml`, creation
  `2026-01-07T05:50:38.577572Z`, and recipe/plan/registry snapshots in the run.
- Fresh aggregation: 401 sections (400 numbered plus background), 627
  `turn_to_links` entries; 365 sections contain presentation anchors.
- Final SHA-256: `6173c7060ce4debf89729dee3bbf6e3637357a150dafb60c71f35c22fe714014`.
- Five development samples inspected: section 1 has links 270/66 and explicit
  `turn to 270`/`turn to 66` anchors; sections 2–4 have no anchors/turn-to list;
  section 5 has targets 185/395 but only bare-number anchor labels. Therefore
  retain surrounding prose when testing detection, not only anchor text.

Held out: Freeway Fighter. Its answer contents were not opened during this
research; only paths, metadata, byte hashes and run registration were checked.
Do not tune from its discrepancies after the implementation is frozen.

- Source: `input/FF13 Freeway Fighter.pdf`.
- OCR: `output/runs/ff-freeway-fighter/03_ocr_ai_gpt51_v1/pages_html.jsonl`.
- Sections: `output/runs/ff-freeway-fighter/12_portionize_html_extract_v1/portions_enriched.jsonl`.
- Final: `output/runs/ff-freeway-fighter/gamebook.json`.
- Registered creation `2026-01-07T14:08:16.553336Z`, recipe `recipe-ff.yaml`.
- OCR SHA-256: `44ce34c3ce74ad58b9bda8d6f0bc4974e4fad0aef6d4f7d94ff96aedc1c689bf`.
- Sections SHA-256: `681a864098a94ce876e75c2a5c34e62702f38f54697a2422da48beecb66d77f4`.
- Final SHA-256: `101d7141614f8cbf87405b648ff3643f5b14be0bd0733ff5f1b69f70cc1b1c6b`.

Secondary stress corpus: `input/FF22 Robot Commando.pdf`, OCR
`output/runs/ff-robot-commando/03_ocr_ai_gpt51_v1/pages_html.jsonl`, sections
`output/runs/ff-robot-commando/13_portionize_html_extract_v1/portions_enriched.jsonl`.
The historically reported `output/runs/ff-robot-commando/gamebook.json` is
currently missing. Story 117 exposed some computed-target/repair answers during
discovery, so Robot Commando is unsuitable as an independent holdout here.

## Goldens and established local method

- `testdata/ff-20-pages/README.md` identifies reviewed Deathtrap OCR/line/boundary
  fixtures from `ff-canonical-full-20-test`. These are OCR goldens, not a complete
  navigation truth table.
- `/Users/cam/Documents/Projects/fighting-fantasy-engine/engine/test-scenarios/gamebooks/deathtrap-dungeon.json`
  contains 401 sections. Its neighboring `deathtrap-dungeon/golden-path-quick.json`
  and `golden-path-long.json` are gameplay routes, only partial link coverage.
- `/Users/cam/Documents/Projects/Fighting Fantasty Player/Deathtrap Dungeon/`
  contains original PDF, raw HTML/text and solution/map PDFs. The directory is
  spelled `Fantasty`. These are additional source evidence, not verified goldens.
- Local production pattern: `modules/extract/extract_choices_relaxed_v1/main.py`
  combines source HTML anchors with text candidates, then deduplicates and emits
  claims. `modules/common/turn_to_claims.py` preserves claim identity by target,
  claim type, module and evidence path.
- `modules/adapter/turn_to_link_reconciler_v1/main.py` builds a set of
  `(section_id, target)` claims and reports unclaimed references. Reuse its audit
  principle, not its game mechanics. Set membership alone loses occurrence
  recall and cannot verify a wrong but valid destination.
- `docs/runbooks/golden-build.md` requires source verification and a manifest
  tied to a scope and run. A model-produced final artifact is a comparison
  baseline until source review establishes the relevant truth.

## Recommendation and limits

Fresh scoped reuse checks (`.venv/bin/python tools/run_registry.py check-reuse
--run-id <id> --scope reference-extraction --output-root
/Users/cam/Documents/Projects/codex-forge/output`) return **unsafe** for both
Deathtrap and Freeway, with no scoped assessment and the fatal signal
`empty_html_between_nonempty_pages`. Deathtrap has 226 page rows and six empty
HTML pages; its run status is failed at Node validation. Freeway has 206 page
rows and five empty HTML pages; status is done but retains a historical failed
Node reason. These health checks inspected aggregate health only for Freeway,
not its reference answers. Neither run is trusted whole-document truth. Using
existing artifacts as a performance/comparison workload must retain these
caveats; source-backed review is required for scored truth.

Adapt only the input in a benchmark harness: construct headings from preserved
section labels, retain raw/presentation HTML and source page provenance, unwrap
source reference anchors to exercise plain-text discovery, and preserve the
original href separately as comparison evidence. Also exercise untouched
anchors for repair/preservation. This transformation must be explicitly named;
it does not demonstrate raw-PDF OCR or full FF pipeline quality.

Score occurrence detection, exact final target, wrong-target count, unresolved
and ambiguous abstention, text/markup/provenance preservation, default-off
behavior, and measured latency/memory on the full development document. Compare
at the occurrence level; 627 set entries are not necessarily 627 occurrences.
Use source images to review a bounded development truth slice independently
before calling it a golden. Keep synthetic tests for duplicate labels, missing
labels and outside-document scope; a naturally clean corpus cannot prove those.

Freeze implementation before running Freeway Fighter. Avoid presenting agreement
with historical gamebook output as independently verified correctness. Computed
targets, state templates and orphan reachability in Robot Commando belong outside
the explicit printed-reference binding contract; report abstention rather than
restoring game-specific production code.

Loop review after discovery/code/artifact rounds: corpus found; independent
holdout reserved; no complete navigation golden found; obsolete artifact path
identified. Further broad scans have diminishing value. Next experiment is a
bounded development harness and independent source review, not more searches.
