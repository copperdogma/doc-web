# Scout 014 — degraded-handwriting-eval-sources

**Source:** Public historical-handwriting eval sources: [DiEm HTR](https://huggingface.co/datasets/RA-Data-Science/DiEm_HTR), [Digital Peter](https://huggingface.co/datasets/ai-forever/Peter), [Saint Gall Database](https://fki.tic.heia-fr.ch/databases/saint-gall-database), [Washington Database](https://fki.tic.heia-fr.ch/databases/washington-database), and [HTR-United](https://github.com/HTR-United/htr-united)
**Scouted:** 2026-04-11
**Scope:** Identify reusable degraded-handwriting / historical-script corpora that can pressure doc-forge's blocked handwritten OCR line without immediately reopening Story 191 on the same narrow Barney/Alverson evidence
**Previous:** Scout 011 (`external ingestion systems`, 2026-03-20)
**Status:** Complete

## Findings

1. **`DiEm HTR` is the strongest first benchmark source for the blocked handwritten line** — HIGH value
   What: The Danish National Archives publish `DiEm HTR` on Hugging Face as a historical handwriting ground-truth dataset with `975` scanned images, PAGE XML, ALTO XML, and explicit transcription provenance. The dataset card says it covers 17th- and 18th-century parish registers, includes pages chosen to represent handwriting and layout variance, and is licensed `CC BY 4.0`.
   Us: This is the closest match to the repo's current missing evidence surface: page-level historical handwriting with inspectable XML/transcript structure, public download, and permissive reuse. It is not the same document family as the LOC letters, but it is a much stronger benchmark seed than adding another synthetic handwritten fixture.
   Recommendation: Create story.
   Transfusion:
   Exemplar: Dataset cards that ship image data plus PAGE/ALTO transcription structure and explicit license metadata.
   Invariant: Any external benchmark we adopt must stay inspectable at the page level, not collapse into opaque aggregate scores.
   Adaptation: Start with a comparison-only bounded slice instead of importing the full corpus; use exact dataset row IDs and attribution so the benchmark can become durable without committing a large third-party dataset on the first pass.
   Proof target: A bounded DiEm slice can be fetched reproducibly, run through the existing OCR lane, and scored/inspected in `output/runs/` without widening the handwritten support claim by inertia.

2. **`Digital Peter` is the best permissive secondary corpus, but it is not the first local move** — MEDIUM value
   What: `Digital Peter` is published on Hugging Face with an `MIT` license and a linked GitHub repo. Its card describes `662` full-page images with end-to-end COCO-style annotations and translated line text for Peter the Great manuscripts.
   Us: The license posture is excellent, and the dataset is genuinely historical. The main drawback is fit: it is Russian/Cyrillic and annotation-heavy, so it is less directly comparable to the current English historical-handwriting blocker than DiEm. It is still a strong second benchmark if script diversity becomes the point rather than language comparability.
   Recommendation: Skip for now as the first follow-up; keep as the next permissive secondary candidate after DiEm.

3. **`Washington Database` is the best English longhand comparison source, but only as comparison-only evidence** — MEDIUM value
   What: The official IAM-HistDB page describes the Washington Database as 18th-century English longhand from the Library of Congress with `20` pages, `656` text lines, and `4,894` word instances, with line- and word-level transcriptions available after registration.
   Us: This is the closest language/time-period match to the LOC blocker pair. The limits are equally clear: it requires registration, carries non-commercial research/teaching-only terms, and exposes normalized line/word images rather than a large page-level public benchmark surface. That makes it useful for comparison-only evidence, not as the first durable repo-owned eval substrate.
   Recommendation: Keep as a comparison-only external benchmark candidate after a permissive page-level source is in place.

4. **`Saint Gall Database` is a real historical-script stressor, but weaker than DiEm for the first benchmark slice** — MEDIUM value
   What: The official IAM-HistDB page describes Saint Gall as a 9th-century Latin manuscript in Carolingian script with `60` page images, page-level text edition, exact line-level transcriptions, and non-commercial research/teaching terms after registration.
   Us: This is valuable as an old-script stressor, especially because the official page explicitly warns that page-level text edition differs from the image while line-level transcription matches exactly. For doc-forge's immediate blocker, though, Saint Gall is less compelling than DiEm: it is less degraded, less cursive, and less operationally simple because the terms are non-commercial and the benchmark would still be comparison-only.
   Recommendation: Keep as a later comparison-only historical-script benchmark if DiEm proves too clean or too domain-specific.

5. **`HTR-United` is a discovery and metadata pattern, not a benchmark corpus by itself** — MEDIUM value
   What: `HTR-United` is an open catalog and GitHub organization for patrimonial HTR ground truth. Its README says datasets should expose images, PAGE/ALTO XML, documentation, and visible license metadata, while its catalog site provides searchable discovery across many projects.
   Us: This is the strongest process pattern from the scout. It does not solve Story 191 directly, but it gives doc-forge a better sourcing rubric: when assessing future handwriting corpora, require explicit license, image/XML linkage, and transcription-guideline visibility instead of saving anonymous links.
   Recommendation: Adopt inline as a sourcing rule inside this scout and Story 211; do not treat `HTR-United` itself as the benchmark.
   Transfusion:
   Exemplar: HTR-United's requirement that shared corpora expose images, PAGE/ALTO linkage, and license/transcription-guideline metadata.
   Invariant: Benchmark sources must stay inspectable and attributable enough that later sessions do not have to rediscover what they are allowed to use.
   Adaptation: Record the rubric in the scout/story decision, then apply it to each candidate rather than creating a new local metadata system now.
   Proof target: The selected follow-up story is justified with explicit license, format, and transcript-granularity evidence rather than "historical handwriting dataset" hand-waving.

## Recommendation

1. Use `DiEm HTR` as the first bounded external historical-handwriting benchmark source.
2. Package the next move as a comparison-only benchmark story, not a corpus-import story.
3. Keep `Digital Peter` as the next permissive secondary source if script diversity becomes worth measuring.
4. Treat `Washington` and `Saint Gall` as comparison-only references because their terms and granularity do not make them good first durable repo-owned substrates.
5. Use the `HTR-United` metadata rubric for future source triage, but do not count the catalog itself as a benchmark pass.

## Approved

- [x] 1. Package the `DiEm HTR` follow-up as one concrete next story — landed as [Story 212](/Users/cam/.codex/worktrees/e813/doc-web/docs/stories/story-212-diem-htr-historical-handwriting-benchmark-slice.md)

## Skipped / Rejected

- `Digital Peter` as the first follow-up — skipped because the script/language mismatch makes it a weaker first benchmark than DiEm despite the strong `MIT` license.
- `Washington Database` as the first durable eval substrate — rejected because registration and non-commercial terms make it comparison-only for this repo.
- `Saint Gall Database` as the first follow-up — rejected because it is a useful historical-script comparator, but less representative of the current blocked degraded-handwriting pressure than DiEm.
- Repo-owned fixture acquisition inside Story 211 — rejected in this pass; the first honest move is to prove value with a bounded comparison-only benchmark before deciding whether any external corpus subset deserves to live in-repo.
- Treating `HTR-United` as a benchmark corpus — rejected; it is a catalog and metadata pattern, not a single pressure surface.

## Verification

- Reviewed local methodology and blocker context: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, [Story 191](/Users/cam/.codex/worktrees/e813/doc-web/docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md), [Story 208](/Users/cam/.codex/worktrees/e813/doc-web/docs/stories/story-208-glm-ocr-benchmark-for-handwritten-and-table-heavy-seams.md), and [Story 211](/Users/cam/.codex/worktrees/e813/doc-web/docs/stories/story-211-scout-degraded-handwriting-and-historical-script-eval-sources.md)
- Reviewed primary-source dataset or catalog docs for all five candidates
- Packaged the selected next move as [Story 212](/Users/cam/.codex/worktrees/e813/doc-web/docs/stories/story-212-diem-htr-historical-handwriting-benchmark-slice.md)

## Evidence

- `DiEm HTR`: [dataset card](https://huggingface.co/datasets/RA-Data-Science/DiEm_HTR)
- `Digital Peter`: [dataset card](https://huggingface.co/datasets/ai-forever/Peter), [GitHub repo](https://github.com/MarkPotanin/DigitalPeter)
- `Saint Gall Database`: [official IAM-HistDB page](https://fki.tic.heia-fr.ch/databases/saint-gall-database)
- `Washington Database`: [official IAM-HistDB page](https://fki.tic.heia-fr.ch/databases/washington-database)
- `HTR-United`: [catalog](https://htr-united.github.io/catalog.html), [GitHub repo](https://github.com/HTR-United/htr-united)
