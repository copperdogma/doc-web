# Story 226 Page Catalog Golden - Robo Rally Rulebook

Date: 2026-04-28

Input: `/Users/cam/Documents/Projects/doc-web/input/f5-robo-rally-rulebook.pdf`

Review artifact root: `output/runs/story226-page-catalog-r1/`

Purpose: establish a human-reviewed semantic golden before building or prompting against this graphics-heavy, print-imposed manual. This catalog is intentionally about content roles, page order, essential graphics, and conversion risks. It is not a transcript of the rulebook.

## Review Evidence

- Rendered logical page images: `output/runs/story226-page-catalog-r1/logical-pages/page-001.jpg` through `page-032.jpg`
- Contact sheets: `output/runs/story226-page-catalog-r1/contact-sheets/logical-pages-01-08.jpg`, `09-16.jpg`, `17-24.jpg`, `25-32.jpg`
- Text aids: `output/runs/story226-page-catalog-r1/page-text/page-001.txt` through `page-032.txt`
- Logical manifest: `output/runs/story226-page-catalog-r1/logical_page_manifest.json`
- Text extraction errors: `output/runs/story226-page-catalog-r1/text_extraction_errors.json` is an empty array
- Parallel shard notes:
  - `output/runs/story226-page-catalog-r1/agent-notes/pages-01-08.md`
  - `output/runs/story226-page-catalog-r1/agent-notes/pages-09-16.md`
  - `output/runs/story226-page-catalog-r1/agent-notes/pages-17-24.md`
  - `output/runs/story226-page-catalog-r1/agent-notes/pages-25-32.md`

All four shard reviews returned `RESULT: no-issue` against the materiality gate: page-order mistakes, missing essential graphics, wrong page role/topic, or catalog gaps that would mislead implementation.

## Logical Page Order Golden

The PDF is print-imposed, not reader-ordered. Physical sheet 1 contains the back page on the left and the front page on the right. Reader order is:

- logical page 1: physical sheet 01R
- logical pages 2-31: physical sheets 02L, 02R, 03L, 03R, ..., 16L, 16R
- logical page 32: physical sheet 01L

The page-order implementation must infer this through printed labels, spread geometry, and consistency checks. It must not hard-code "move first left half to end" as Robo Rally-specific behavior.

## Global Semantic Policy

- Treat hazard borders, yellow side tabs, rivets, grey texture backgrounds, page-number gears, crop marks, and print timestamps as layout chrome unless they separate major content regions.
- Preserve side-tab labels only as section-navigation metadata when useful; do not let them become primary headings in the reading order.
- Preserve content as semantic structures: headings, ordered procedures, bullets, term/definition lists, course entries, card entries, notes, callouts, and figures.
- Every essential graphic must become a figure-like artifact with source physical sheet, split side, logical page, crop or source bbox where available, role, caption/context, and confidence or review status.
- Decorative robot/action art can be omitted from the plain rules flow unless retained as front/back matter identity. It must not pollute rule extraction or figure inventories.
- Card thumbnails and course maps are not decorative: they are reference content and must remain bound to the correct title, metadata, and effect/setup text.

## Figure Role Taxonomy

- `cover_identity`: title/logo/product metadata on page 1; decorative art is secondary.
- `setup_diagram`: setup table diagram and start-board placement on page 3.
- `rule_example_diagram`: priority, programming, activation, board-element, pushing, reboot, and damage examples on pages 4, 6-15.
- `board_element_icon`: board symbol examples on pages 8 and 12-13.
- `course_map`: racing-course layouts on pages 16-23; these are primary setup content.
- `card_face_reference`: programming, special programming, and upgrade card images on pages 24-31.
- `round_summary_panel`: phase-summary panels on pages 11 and 32.
- `decorative_chrome`: borders, side rails, textures, rivets, crop marks, page-number ornaments, and non-rule action art.

## Per-Page Catalog

| Logical page | Source | Page role | Core content structures | Essential graphics | Main conversion risks |
| --- | --- | --- | --- | --- | --- |
| 1 | 01R | Front cover and component inventory | Title/guide identity, player/age metadata, component list, publisher branding | Title/logo and metadata markers; cover illustration is decorative identity | Small bottom inventory can be missed; do not infer rules from cover art |
| 2 | 02L | Introduction, win condition, contents, first-time prep | Intro prose, win-condition subsection, table of contents, first-time setup list | No rules-critical diagram; contents/list structure is essential text | Dot leaders and page numbers can become noise; prep list must remain separate from contents |
| 3 | 02R | Main setup procedure | Setup heading, nine ordered setup steps, course/priority cross-references, figure callouts | Start-board placement inset; large labeled setup table diagram | Figure labels must stay attached to the diagram, not merge into setup steps; energy bank and player reserve are distinct |
| 4 | 03L | Round overview and priority rules | Three-phase overview, priority callout, two worked priority examples | Two priority board diagrams; antenna/tie-break visuals | The two examples are parallel examples with separate captions; side rail is chrome |
| 5 | 03R | Upgrade phase rules | Upgrade-shop bullets, purchase rules, permanent/temporary distinction, limits, transition to programming | Upgrade-card cost callout; player-mat upgrade placement figure; card-type examples | Card images belong to the phase explanation, not the later card index |
| 6 | 04L | Programming phase procedure and example start | Four programming steps, register/facedown note, example hand, movement plan | Example hand of programming cards; board-route figure with numbered action callouts | Note interrupts an ordered list; example hand and route must stay linked |
| 7 | 04R | Programming continuation and activation start | Register-placement figure, timer/timeout rules, activation phase intro, three activation steps | Five-register player-mat figure with facedown cards and related callout | Page starts mid-example and later changes phase; activation content must not be dropped |
| 8 | 05L | Activation-order reference | Ordered board-element and laser sequence, notes, upgrade reminder, end-of-round cleanup | Eight numbered element/laser graphics in activation order | Two-column layout must preserve numeric order 1-8; fifth-register energy condition must survive |
| 9 | 05R | Activating robots worked example | Three example units for first-register resolution in priority order | Three player-mat/card images plus three board-state diagrams | Each paragraph must stay bound to its matching player/board pair |
| 10 | 06L | Board-element activation example | Activation-order reminder, large board example, outcome notes, register-one close | Central board diagram with callouts; blue activation-order summary | Yellow callouts must attach to the correct robots/board positions; "no effect" outcomes are semantic |
| 11 | 06R | Summary of a round and end-game condition | Three phase panels, repeated register cycles, separate end-game subsection | Blue phase panels are semantic layout; robot art is decorative | Activation cycles must remain five repeated register cycles, not collapse into vague prose |
| 12 | 07L | Board elements, first page | Section intro, conveyor rules, rotating conveyor rules, push panel rules | Conveyor examples, rotation examples, push-panel tile | Several small examples need correct captions; movement source matters for rotating conveyors |
| 13 | 07R | Board elements, continuation | Icon-plus-rule blocks for gears, lasers, pits, energy spaces, checkpoints, walls, priority antenna | All board-element icons/tiles | Checkpoint marker numbers can become stray list items; priority antenna orientation is semantic |
| 14 | 08L | Robot interaction rules | Robot-laser rules, pushing rules, conveyor exception, falling-off-board rule | Laser line-of-sight diagram; four pushing examples with programming-card icons | Two-column example grid can merge captions; wall/pit outcomes must stay with examples |
| 15 | 08R | Damage and reboots | Damage-card resolution steps, damage-type reference, reboot procedure, notes | Four damage card images; reboot token/board example | Two numbered lists must not merge; damage-card grid must preserve label/card/effect associations |
| 16 | 09L | Racing-course catalog intro and starter course | Difficulty taxonomy, course metadata definitions, Dizzy Highway entry | Difficulty panel; Dizzy Highway course map | General taxonomy must not merge with the first course entry; map remains tied to setup steps |
| 17 | 09R | Beginner course catalog | Four course entries in a 2x2 grid | Four course maps: Risky Crossing, High Octane, Sprint Cramp, Corridor Blitz | OCR numbers can precede course names; preserve image/caption/metadata units |
| 18 | 10L | Beginner-to-intermediate course transition | Fractionation entry, intermediate heading, Burnout and Lost Bearings entries | Three course maps | Fractionation remains beginner; Burnout's special rule belongs only to Burnout |
| 19 | 10R | Intermediate course continuation | Passing Lane and Twister entries | Two course maps | Twister's longer special rule must remain attached to Twister; wide Passing Lane map is one figure |
| 20 | 11L | Advanced course start | Advanced heading, Dodge This and Chop Shop Challenge entries | Two course maps, including one wide multi-board map | Chop Shop Challenge must remain one course figure and one metadata set |
| 21 | 11R | Advanced course continuation | Undertow, Heavy Merge Area, Death Trap entries | Three course maps | Lower two-column entries can interleave; repeated reboot-token special rules are real duplicated course-specific content |
| 22 | 12L | Robots Must Die course start | Pilgrimage and Gear Stripper long-form entries | Two large multi-board course maps | Similar long special rules belong to two separate entries, not a shared detached note |
| 23 | 12R | Robots Must Die continuation | Extra Crispy and Burn Run entries | Two course maps, including Burn Run's large multi-board layout | Burn Run board list wraps; stray OCR control characters must be rejected |
| 24 | 13L | Card index: programming cards | Programming-card reference grid, grouped Move 1/2/3 entry, distinct turn/back/power/again entries | Programming card faces are essential reference images | OCR can interleave columns; "Move Back" image label and "Back Up" text label should be reconciled deliberately |
| 25 | 13R | Special programming card reference | Six special programming card entries; routine option lists | Six black programming-card thumbnails | Preserve card grid atomicity; Sandbox and Weasel options are lists, not comma-noise |
| 26 | 14L | Upgrade card intro and permanent upgrades | Upgrade-card anatomy, permanent-upgrade definition, first six entries | Cost/effect anatomy callout; six yellow permanent-upgrade card thumbnails | Anatomy callout precedes the card catalog; cost/effect/name/card associations must stay atomic |
| 27 | 14R | Permanent upgrade continuation | Eight upgrade entries plus rule-exception callout | Eight yellow card thumbnails; Rogue Code note | Rogue Code applies generally, not only to nearby cards; bottom-row entries remain separate |
| 28 | 15L | Permanent upgrade continuation | Eight upgrade entries | Eight yellow card thumbnails | Similar shooting/pushing effects need exact name/effect associations |
| 29 | 15R | Permanent-to-temporary transition | Teleporter and Virus Module permanent entries, temporary-upgrade definition, first six temporary entries | Two yellow card thumbnails, six red card thumbnails, category heading | Do not classify whole page as temporary; transition occurs after top two permanent cards |
| 30 | 16L | Temporary upgrade continuation | Eight temporary upgrade entries with longer effects and lists | Eight red card thumbnails | Long effects can merge across columns; routine upgrades add programming cards and must preserve that distinction |
| 31 | 16R | Temporary upgrade close and variant rules | Two temporary card entries, lighter-game variant, advanced-game variant | Two red card thumbnails; divider is structural but not content | Variant sections are independent optional rules and must not merge into card effects |
| 32 | 01L | Back cover summary and legal/footer | Summary of a round, three numbered phase panels, legal/contact/footer block | Phase summary panels are rule-summary layout; logos are footer/branding | Page 32 must be last despite source sheet 01L; footer is separate from rules summary |

## Required Golden Checks For Future Runs

Any candidate pipeline or VLM baseline for this story should be checked against these observations:

- Logical page map contains 32 logical pages in reader order, with page 1 sourced from `01R` and page 32 sourced from `01L`.
- No logical pages are missing or duplicated.
- Page 3 includes both setup figures and nine setup steps.
- Page 4 preserves two separate priority examples and their diagram captions.
- Pages 8-10 preserve activation order and worked activation examples as rule examples, not loose images.
- Pages 12-15 preserve board-element, robot-interaction, damage, and reboot reference graphics as essential figures.
- Pages 16-23 produce course entries where each course map is an essential figure bound to title, game length, boards, and special rules.
- Pages 24-31 produce card entries where each card face is bound to card name, cost where applicable, category, and effect.
- Page 29 preserves the category transition from permanent upgrades to temporary upgrades.
- Page 31 separates variant rules from the temporary-upgrade card entries.
- Page 32 is a back-cover summary/footer page and does not appear before page 1 in final HTML.

## Implementation Implications

- Start with a logical-page-map artifact before semantic HTML. The most dangerous failure is a plausible-looking manual in physical print order.
- Treat figure classification as a first-class artifact. At minimum, produce a `graphic_role_inventory`, an `essential_graphics_plan`, and a `semantic_html_conformance_report`.
- Use generic signals: printed page labels, spread-side geometry, section/page-number consistency, card-grid/course-grid structure, nearby text, visual density, and role classification.
- Keep Robo Rally-specific names in goldens/evals only. Production code should not branch on title strings, course names, card names, or exact page IDs.
- Validate page types, not just text coverage: front matter, setup, worked rule examples, reference pages, course catalog, card catalog, variant rules, and back matter.
