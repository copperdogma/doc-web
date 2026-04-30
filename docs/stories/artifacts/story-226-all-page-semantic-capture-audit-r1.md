# Story 226 All-Page Semantic Capture Audit R1

## Target

- Source: `output/runs/story226-page-catalog-r1/logical-pages/page-001.jpg` through `page-032.jpg`
- Output: `output/runs/story226-driver-build-r1/output/html/`
- QA packet: `output/runs/story226-driver-build-r1/manual-inspection-r10/all-pages/`
- Conformance report: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json`
- Provenance sidecar: `output/runs/story226-driver-build-r1/output/html/provenance/blocks.jsonl`

## What Looks Right

- All 32 logical booklet pages are represented in reader order, not physical print-imposition order.
- The output stays plain semantic HTML rather than a visual replica: headings, procedures, lists, catalog entries, figures, notes, and card/course reference material are readable without the designed PDF layout.
- Source-pixel figures are kept where the visual is rule-bearing: setup diagrams, priority examples, board element diagrams, robot interaction diagrams, damage/reboot references, course maps, programming cards, and upgrade/damage cards.
- Decorative chrome is suppressed or reduced to source context. Highlighted text callouts are generally represented as semantic text unless the callout is spatially tied to a diagram.

## Problems Found

- Course-map figures that were split or repositioned could retain the correct image pixels while losing the crop source page in provenance. Generic class: moved/split figure nodes need source-page metadata carried on both the figure and image node.
- Definition-list catalog metadata could move into semantic catalog entries as bare inline text, so cost/effect values appeared in the rendered HTML but were not proper paragraph blocks for block-level provenance. Generic class: inline metadata moved out of a source `<dd>` needs paragraph wrapping.
- Provenance matching was too dependent on tag kind after semantic normalization. When source `dt`/`dd` or compact paragraphs became final headings and paragraphs, later catalog entries could be assigned to the wrong page. Generic class: provenance matching must use strong text matching across tag-kind changes, with numeric conflict checks for repeated cost/effect patterns.

## Fix Attempt

- `build_chapter_html_v1` now annotates figures and images with crop source page and source crop filename, and `_tag_entry_body` honors those overrides in provenance rows.
- Catalog `<dd>` metadata moved into semantic entry sections is wrapped into paragraph blocks when it is inline content.
- Source descriptor matching now tries text-first matching across semantic tag-kind changes before falling back to kind/position matching, and avoids matching cost/effect rows whose numeric values conflict.

## Rerun Evidence

- Driver rerun from `build_chapters` completed on the real local PDF and `validate_manual_html` reported `Semantic manual conformance: pass`.
- Conformance summary after the rerun: `22/22` checks passed, `0` warnings, `0` failures, `32` logical pages, `126` crops, `113` HTML figures, `490` provenance rows.
- Focused regression slice passed: `python -m pytest tests/test_build_chapter_html.py::test_normalize_catalog_entries_groups_definition_list_entries_with_embedded_figures tests/test_build_chapter_html.py::test_catalog_entry_provenance_survives_dt_dd_to_heading_paragraph_normalization tests/test_build_chapter_html.py::TestFigureWrapping::test_crop_figure_provenance_uses_crop_source_page_not_chapter_fallback -q`.
- Post-fix spot checks showed card entries such as `ADMIN PRIVILEGE`, `MEMORY STICK`, `TELEPORTER`, and `REBOOT` mapped to pages `26`, `28`, `29`, and `30` respectively, with source-pixel card figures plus paragraph-wrapped cost/effect text.

## Page-Level Judgments

| Page | Source Role | Judgment | Notes |
| --- | --- | --- | --- |
| 1 | Front cover and contents | Pass | Cover image retained; contents text extracted semantically. |
| 2 | Intro, TOC, first-time setup | Pass | Cover/intro visual retained; TOC and first-time setup are readable plain text. |
| 3 | Setup | Pass | Setup prose, bullets, component/setup figures, and two-player setup note are captured. |
| 4 | How to play and priority | Pass | Round phases and priority examples are text plus source-pixel diagrams. |
| 5 | Playing a round, upgrade phase | Pass | Upgrade shop/procedure text is captured; example graphic retained. |
| 6 | Programming phase | Pass | Register/player mat examples and the contextual programming graphic are retained. |
| 7 | Programming/activation transition | Pass | Programming example, timer note, and activation procedure are captured. |
| 8 | Board elements activation order | Pass | Eight board-element visuals are preserved; pure text notes are semantic text. |
| 9 | Activation example | Pass | Multi-step programming/board examples are retained in source-pixel figures with explanatory text. |
| 10 | Activation example continuation | Pass | Spatial callout diagram is retained; end-of-register note is semantic text. |
| 11 | Summary of a round | Pass with tradeoff | The summary panel is represented as semantic phase text; redundant panel art is not required as a final figure. |
| 12 | More on racing through the factory | Pass | Board element prose and conveyor/push-panel examples are captured. |
| 13 | Factory elements continuation | Pass | Gear, laser, pit, energy, checkpoint, wall, and antenna rules are captured with figures. |
| 14 | Robot interactions | Pass | Robot laser and pushing examples are retained with semantic rule prose. |
| 15 | Damage and reboots | Pass | Damage card faces, reboot examples, and procedure text are captured. |
| 16 | Racing courses intro/starter | Pass | Racing-course parent section, difficulty notes, setup instructions, and starter course map are captured. |
| 17 | Beginner course catalog | Pass | Four course entries are grouped with map figures and metadata. |
| 18 | Beginner/intermediate course catalog | Pass | Course maps and section transition are captured. |
| 19 | Beginner course catalog continuation | Fixed | Course figures were present before, but provenance was suspect; post-fix entries map to page 19. |
| 20 | Advanced course catalog | Pass | Course maps and metadata are grouped under the racing-courses parent section. |
| 21 | Advanced course catalog continuation | Fixed | Three course maps and metadata now carry correct page provenance. |
| 22 | Robots Must Die courses | Pass | The `ROBOTS. MUST. DIE. COURSES` section remains one catalog subsection with maps and setup rules. |
| 23 | Robots Must Die continuation | Pass | Continuation entries remain under the same catalog section rather than becoming a separate chapter. |
| 24 | Card index programming cards | Pass | Programming card faces and movement text are paired in plain HTML. |
| 25 | Special programming cards | Pass | Special card faces and rules are paired; no visual-text-only dependency remains. |
| 26 | Upgrade card intro/permanent upgrades | Fixed | Inline definition-list metadata is now paragraph-wrapped; card figures and cost/effect text align. |
| 27 | Permanent upgrades continuation | Fixed | Card entries now show source-pixel cards with their own cost/effect text and page provenance. |
| 28 | Permanent upgrades continuation | Fixed | Card entries and text are grouped by source page rather than leaking into page 24 fallback provenance. |
| 29 | Temporary upgrades | Fixed | Teleporter through Repeat Routine entries now show correct page 29 figures and cost/effect text. |
| 30 | Temporary upgrades continuation | Fixed | Reboot through Speed Routine entries now show correct page 30 figures and cost/effect text. |
| 31 | Temporary upgrades and variants | Fixed | Weasel Routine, Zoop, lighter game, and advanced game text are captured with correct page provenance. |
| 32 | Back page / summary | Pass with tradeoff | Back-page summary and legal/contact text are captured; visual back-cover design is not reproduced. |

## Reinspection Result

- The final all-page QA packet was regenerated after the driver rerun and manually inspected from the contact sheets plus focused full-page checks for the card-index and course-catalog pages.
- The material defects found by the all-page pass were generic provenance/semantic-structure defects and were fixed in code, not by manually editing generated HTML.
- No page-level semantic-capture defect remains in the current inspected output. Residual differences are plain-HTML tradeoffs: the output is intentionally not a print replica, and redundant designed panels may become semantic text rather than source-pixel figures.

## Remaining Caveats

- This remains a local hard-case proof for graphics-heavy/imposed manuals, not a broadened canonical coverage claim for every born-digital PDF.
- The audit packet is for human QA and uses generated screenshots/contact sheets; the authoritative output remains the final HTML plus provenance and manifest artifacts under `output/runs/story226-driver-build-r1/output/html/`.
- Full `make test` was not part of this audit note; the story closeout should still run the maintained check set before marking Done.
