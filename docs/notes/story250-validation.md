# Story 250 validation — related-document reference resolution

Validation snapshot: 2026-10-07, before repository landing. Candidate worktree:
`/Users/cam/.codex/worktrees/related-document-references/doc-web`, based on
`3a7bc2c01543c6c2f96cf3febe3dc8234331427b`. Public runtime/package identity is
recorded in `output/story250-handoff/candidate-v2.json` (12 SHA-256 pins).
Driver adapter/recipe identity is recorded separately in
`output/story250-handoff/driver-final-pins.json`. No commit or push had occurred
at validation time. No paid inference, OCR, or downstream production integration
was performed.

## Findings and disposition

No unresolved material finding remains for the declared offline capability.
Root inspected modified and untracked code, fixtures, schemas, docs and generated
records. A bounded independent semantic/security reviewer and two
`codex review --uncommitted` passes supplied additional findings. The final
driver-only review confirmed the resume correction. Review logs are retained in
`output/story250-handoff/codex-review.txt`, `codex-review-final.txt` and
`codex-review-resume.txt`.

| Accepted finding | Correction and applicable proof |
| --- | --- |
| Legacy bundles could publish unclassified files | Explicit core/declared-asset allowlist; file-inventory/private-extra regressions |
| Existing anchor text hid scope evidence; postfix named qualifiers and URI tokens needed coverage | Separate semantic scope text from mutation ranges; qualifier, edition, URI/email and inline-markup controls |
| Static portability missed responsive/CSS resources | Standard HTML URL-token split and tinycss2 parsing; missing/valid srcset, import, url and image-set controls |
| Parsed manifest could disagree with later snapshot | Require parsed authority bytes to match the snapshot, then reread inputs before publication; injected race test |
| Installed CLI imported an unshipped helper; benchmark snapshots assumed the old path | Move shared helper into doc_web, update all callers and isolated benchmark imports; installed-wheel CLI and fresh freeze/worker proofs |
| Typed prefixed identifiers and turn-to paragraph wording lost qualifier/kind checks | Extend the shared occurrence hook with unchanged local defaults; explicit kind, postfix/list and local resolver regression controls |
| Driver resume reused an existing output directory | Retain old derivatives, create a new sibling and update the result locator; real resume, byte-preservation test and focused review |

Historical failed attempts are retained rather than treated as passes. Initial
driver run `story250-related-offline-01` exposed the driver's line-oriented
envelope behavior; the generic transform adapter and one-record result fixed
that integration. An exploratory broader CLI environment sweep was interrupted
after 597 passes and two stale-import failures; both imports were corrected and
covered by the final affected suite. That interrupted sweep and full `make test`
are **not** claimed green. No unrelated package-environment installations are
required for the final proportional validation claim.

## Acceptance criteria

| Requirement | Result and evidence |
| --- | --- |
| Explicit opt-in public CLI/Python contract, unchanged local defaults | Met: public CLI/JSON, installed-wheel invocation outside checkout, runtime discovery and local resolver regression tests |
| Exact source-backed heading/subsection binding and inline citations | Met: leading/terminal-parenthesized headings, arbitrary prefixes, lettered labels and inline boundaries; direct owner preference permits bare exact identifiers |
| Refuse ambiguity, missing evidence, unsupported scope and edition conflict | Met: exhaustive bounded grammar/safety tests, retained rejected targets, synthetic refusal reports and 18 independent consumer refusal checks |
| Preserve original inputs, text, IDs, provenance, assets and existing links | Met: runtime preservation checks and receipts; independent consumer verifies 60 original files, 44 article texts/ID sets, 295 existing hrefs and eight figures |
| Portable copy resolves exact intended targets | Met: independently walked synthetic copied set and real consumer copy; 1,152 existing/generated local hrefs and eight image references checked in consumer output |
| Real driver, manual data inspection, rendered inspection and regressions | Met: fresh driver plus resume, six positive and two refusal sample rows read with target HTML/provenance; consumer clicked all six relocated destinations and inspected rendered heading/body |
| Public operational docs and practical limits | Met: `docs/related-document-references.md`, linked bundle contract, declared schemas and runtime metadata |
| Concrete candidate handoff, feedback and consumer acceptance | Met: all 12 v2 pins independently matched; signed-off consumer receipt and report retained at the path below |

All 8 acceptance criteria and 14 task/tenet checkboxes are satisfied. Build and
validation gates may close. Grade: **A for the bounded story**. Recommendation:
**Close now**. No remaining story gap or user decision is needed.

## Checks and environment

Runtime: Python 3.11.5 (`/Users/cam/miniconda3/bin/python`), BeautifulSoup 4.12.3,
tinycss2 1.3.0, Pydantic 2.12.5, macOS. The installed CLI regression builds and
uses a wheel from the candidate outside the source checkout. No provider keys
or calls are needed.

The affected suite covers the set runtime, shared resolver and its local
consumer, package/CLI contracts, independent benchmark snapshots and real driver:

```bash
python -m pytest -q tests/test_related_documents.py \
  tests/test_related_navigation.py tests/test_manual_navigation.py \
  tests/test_reference_resolution.py tests/test_reference_integration.py \
  tests/test_reference_benchmark.py tests/test_doc_web_bundle_contract.py
```

Final consolidated result: **650 passed in 38.45s**, recorded in
`output/story250-handoff/focused-tests-final.txt`.
Full `make lint`, artifact schema validation, `git diff --check`, and methodology
compile/check pass. No skills changed. Earlier 592-test evidence and the later
416-test grammar/import checks were supplemented by the consolidated final run
after the resume correction. Final counts and completion are recorded in the
story work log.

## Driver and manually inspected samples

```bash
python driver.py --recipe configs/recipes/recipe-related-document-set.yaml \
  --run-id story250-related-final --output-dir output/runs
python driver.py --recipe configs/recipes/recipe-related-document-set.yaml \
  --run-id story250-related-final --output-dir output/runs \
  --start-from references --allow-run-id-reuse
```

Both pass; logs are `output/story250-handoff/driver-final.txt` and
`driver-resume-final.txt`. The authoritative result locator is
`output/runs/story250-related-final/02_resolve_document_set_v1/related_set_result.json`.
It now names
`output/runs/story250-related-final/02_resolve_document_set_v1/related-set-2d4e2cac48aa41c2a65a15f8d3483a89/`.
The first `related-set/` derivative remains intact. Both outputs contain the
portable `related_documents.json` receipt and `related_reference_report.json`.

Read the six positive occurrence records against source and target HTML plus
`provenance/blocks.jsonl`. All use physical source page 1 and the expected unique
`el-001-00N` source element; visible text, inline emphasis, original Contents
anchor and assets survive. The `x501b` and `x503e` occurrences have raw source
offsets 4:9; `x512`, `x528`, `x525` and `x519` use 4:8.

| Exact token | Target heading | Target fragment in companion/chapter-001.html |
| --- | --- | --- |
| x501b | x501b: Supply checks | blk-chapter-001-0001 |
| x512 | Movement rules (x512) | blk-chapter-001-0002 |
| x528 | Weather checks (x528): | blk-chapter-001-0003 |
| x503e | x503e Encounters | blk-chapter-001-0004 |
| x525 | Equipment (x525) | blk-chapter-001-0005 |
| x519 | x519: Final checks | blk-chapter-001-0006 |

The final report records six resolved references, four existing local links,
ten final local links and 12 checked static resources, with zero issues/calls/
cost. Independently followed all six links after copying the entire derivative
to `output/story250-safety-final/relocated-complete-set/`.

Also manually opened refusal rows in
`output/story250-safety-final/editions/related_reference_report.json` (all six
`edition_conflict`, null targets) and
`output/story250-safety-final/duplicate/related_reference_report.json` (`x501b`
ambiguous with `duplicate_exact_targets`, null target; other five resolve).
These are generated artifacts, never hand-edited pipeline results.

## Independent consumer and rendered evidence

Consumer acceptance is explicit and separate from implementation evidence:

`/Users/cam/.codex/worktrees/companion-reference-consumer/boardgame-ingester/output/companion-reference-consumer-20261007/consumer-acceptance.json`

Sibling `consumer-report.md`, `consumer-v2-result.json`,
`consumer-v2-refusals.json`, `consumer-v2-bare-boundaries.json`, and
`accepted-docweb-candidate-v2.json` retain the detailed proof. Candidate v2 passes
2,396 preservation/portability assertions, all six exact expected destinations,
all 18 missing-provenance/duplicate/edition holds and bare-identifier boundary
controls. A deliberately malformed synthetic block-ID fixture was correctly
refused; the corrected fixture passes and that history remains available.

The consumer clicked all six generated links in the actual in-app browser on
its localhost-served relocated set and observed the independently expected
heading each time. It also inspected the displayed destination screenshot/body.
The screenshot was displayed by the browser tool, not saved as a local file.
Our earlier file-URL navigation was blocked by browser policy and supplies no
visual evidence; closure reuses the explicitly reported consumer browser proof
against unchanged v2 pins. The later adapter-only resume change does not alter
that public candidate. No consumer source/grade/seal changes or production
caller integration are part of this acceptance.

## Boundaries and methodology

The operation trusts existing converter provenance and caller-declared
relatedness. It handles documented exact identifier forms, not broad prose,
fuzzy meaning, unknown physical editions, OCR repair or universal source
fidelity. Null editions remain unknown. Static dependency checking does not
execute JavaScript or verify remote availability. Member audit metadata is
preserved and can contain historical absolute source paths; this is not a
privacy-sanitized publication tool. New navigation and receipts are portable.

Story 243 is Done. ADR-002 is ACCEPTED; this work extends its standalone runtime
and source-provenance boundary without resolving or reopening its remaining
repository extraction/Dossier integration work. Relevant spec:3/6/7 state and
PDF/DOCX coverage claims remain unchanged: synthetic/consumer proofs here do not
graduate a new input format. No model benchmark was run, so eval registry score
updates are not applicable. Generated graph/index are refreshed by closure.

The default-off source/identity/preservation rules satisfy T0/T3; the bounded
symbol-binding baseline (`output/story250-baseline/baseline.json`, zero companion
links) and explicit no-inference comparison satisfy T1/T2; generic declaration,
module and fixture identifiers satisfy T4; manual and rendered evidence above
satisfy T5. No replacement OCR path or second document-local resolver remains.

Final strategic disposition: the exact-binding/inventory approach reached the
authorized outcome and independent acceptance. Stop implementation; broader
semantic inference and downstream adoption require separate work. Review
findings exercised existing checks and are not evidence of a missing workflow
rule; no learning candidate or memory update is warranted.

## Authorized repository landing

After consumer acceptance, the user explicitly requested finish-and-push.
The landing preflight fetched origin/main and confirmed it still equals the
tested base `3a7bc2c01543c6c2f96cf3febe3dc8234331427b`. All 41 candidate paths,
12 public pins and three driver pins matched their validation receipts before
this documentation-only landing note. The 650-test result, driver/resume proof,
lint and consumer acceptance are reused because their tested inputs are
unchanged. Methodology records and whitespace checks are refreshed after this
note. No implementation or dependency revalidation is needed for these prose
changes. The independent consumer worktree is clean with no linked changes to
commit; the primary Doc-web checkout and its inbox have no new changes and are
left untouched.

Landing target: origin/main via execution branch
`codex/related-document-references`. Preserve the earlier candidate/consumer
receipts as pre-landing snapshots. The completed commit and verified remote
state belong in `output/story250-handoff/landing-receipt.json` and the final
handoff, rather than rewriting the accepted validation evidence. Retain the
task worktree, branch and ignored artifacts; cleanup was not requested.
