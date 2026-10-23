# Related-document references — Story 250

## Decision and evidence

The general problem is scoped symbol resolution across separately published
artifacts, followed by portable publication. [Sphinx intersphinx](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html)
uses explicit external inventories; [RFC 3986 section 5](https://www.rfc-editor.org/rfc/rfc3986#section-5)
defines relative URI resolution. Adopt explicit inventories and relative path
construction; do not infer relatedness from folders or matching labels.

Local baseline: resolve_navigation is explicitly single_document_build and
ReferenceIndex only sees the supplied document entries. Ordinary bundles expose
manifest entries plus source-located provenance text_quote. This enables a
post-conversion operation without paid OCR. Code enumerates exact candidates and
applies caller authority. A decision model or language model may handle broader
prose in future, but cannot replace absent source evidence, identity or edition
permission. No model quality conclusion or provider call is made here.

New declaration lists each member bundle and optional edition evidence. Known
edition disagreement is an explicit hold; unknown evidence is not inferred.
Caller relationship assertion remains distinct from proven physical equivalence.
Source-backed heading labels may be leading or terminal parenthesized symbols;
full heading text must agree with its heading provenance. Reuse DOM range and
scope helpers. Ambiguity remains visible and is never broken by member order.

Inputs are immutable; output is a derivative set with a new receipt and report.
Existing local bundle manifests/provenance and local hrefs survive. The set adds
member directories and relative links. Copy proof and fresh driver artifacts
must establish applicability; external standards are design advice, not proof.

Remaining uncertainty: broad natural-language citations and incomplete/truncated
heading provenance may need richer upstream evidence. No fuzzy fallback is
included. Exact supported grammar and validation results are documented with
the candidate before handoff.

## Strategic review — first checkpoint

Current runtime exposes gpt-6-astra with ultra as its maximum effort; this chat
was created with that requested configuration (tool evidence in originating
chat). Independently served model identity is unavailable. Root review used the
existing configuration; implementation workers used Sol high/medium, factual
inventory Luna high, and independent API/security review Sol xhigh.

1. Follow-through: first checkpoint; no prior review recommendation. Authorized
   plan is implemented at public CLI and driver level. New direct owner preference
   permits bare exact identifiers; consumer feedback established repeated default
   document IDs as valid, so explicit member_id owns the namespace.
2. Utility: a caller can now build a fresh derivative set offline. Initial
   67 focused tests passed; driver run story250-related-offline-02 completed.
   Consumer has a source-hashed v1 candidate for independent real-data testing.
3. Alternative/opportunity cost: reuse the source-backed Sphinx-inventory/RFC3986
   comparison above. An explicit user-authored link map would be simpler runtime
   code but transfers interpretation/maintenance to callers and misses the task.
   A model-based whole-document rewrite adds paid inference and fidelity risk
   without supplying missing identity authority. Current exact binding remains
   the smallest justified mechanism for the supported class. No paid comparison
   is authorized or useful to this plumbing acceptance boundary.
4. Disposition: continue with bounded independent review, broader affected-local
   regressions and real consumer results, then stop when candidate acceptance is
   concrete. Do not expand into semantic citation inference or source repair.
   Next strategic check after another three substantive rounds/30 active minutes
   if needed.

Driver integration initially exposed existing line-oriented envelope behavior:
its stamp_artifact reads JSONL and adds run/module/time fields. The adapter now
uses the generic transform stage and a one-record JSON result with explicit
metadata fields, leaving the declaration unmodified. No driver-wide workaround
or gate relaxation was required.

## Static portability review

A confirmed missing-srcset probe showed that only checking img.src does not
cover responsive assets. This is a generic static dependency-inventory problem.
The [HTML srcset algorithm](https://html.spec.whatwg.org/multipage/images.html#parse-a-srcset-attribute)
separates URL tokens from descriptors without splitting data-URL commas. Adapt
that split. [tinycss2 API](https://doc.courtbouillon.org/tinycss2/stable/api_reference.html)
provides CSS syntax tokens including URL/function/import forms; use its existing
parser rather than a regex CSS reimplementation. Declare >=1.3,<2 in the driver
extra and requirements (1.3.0 already available locally); no package download
or provider call required. Verify missing/valid CSS, imports, image-set and
srcset with local controls. Dynamic script behavior and remote availability
remain outside static validation.

Legacy manifests without file classifications use an explicit core/asset-root
allowlist, not full-directory publication. Preserve existing audit metadata and
document its privacy limitation; no privacy-sanitized snapshot claim is made.
A second read of the manifest must equal the parsed authority before any receipt
is emitted; subsequent readback detects later source mutation.
