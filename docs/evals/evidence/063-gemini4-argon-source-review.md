# Attempt063 source review

The canonical thirteen source-page b64 fixtures, user-created goldens and scorer
were frozen before calls. Their hashes, exact outputs and receipts are retained
in the manifest/summary. No golden, score, label or default was changed to fit
the candidate. All thirteen predicted region counts match the goldens.

Main-agent visual inspection covered original Image000/Image011 pixels and
candidate crops, then source/golden/candidate panels for Image001, Image003,
Image037 and Image124. A bounded independent semantic reviewer inspected the
remaining seven panels (twelve regions). These observations do not establish
every boundary pixel or publication safety.

| Source | Concrete observation | Disposition |
|---|---|---|
| Image000 | Inset `[65,42,956,943]` removes outer red cover margin. Title/year, lower names, landscape, and four gold frame sides appear retained. Top-left finial has very little clearance; no unambiguous amputated tip was identified. | Preserve `.8324` whole-cover score. **Model-wrong bounding undercoverage**, consistent with prior inset-cover classification; no golden/scorer fault. Exact cover-edge equivalence remains unresolved, so do not call it fully source-faithful. |
| Image011 | Full `CELEBRATE SASKATCHEWAN` wording arc, central emblem and `1905–1980` retained; second region groups seal/signatures as required by the detector golden. | `.9914`; no definite logo loss observed. Grouped detector region is not independent C5/publication qualification. |
| Image001 | Decorative title, full lettering and dates remain present. | No definite subject loss observed in panel. |
| Image003 | Wagon, animals, surrounding illustration lines and grass retained; separate printed credit remains outside. | No definite subject loss observed in panel. |
| Image037 | Group photo and oval portrait remain separate; visible clothing, faces and oval extent retained, with prose outside. | No definite subject loss/caption contamination observed. |
| Image124 | Covered wagon, occupants, oxen, wheel, ground and faint cloud lines remain visible; separate illustration credit excluded. | Preserve `.9756`; no definite subject amputation identified, without asserting every faint boundary pixel. |
| Image008/013 | Portraits retain visible heads/clothing/photo boundaries; adjacent prose/captions remain outside. | Independent reviewer found no definite subject loss. |
| Image020/021 | Farm/aerial landscapes/buildings and people/photo extents retained; page captions excluded. | Independent reviewer found no definite subject loss. |
| Image059 | Two photos retained, including standing couple's lower extent and second subject's hands; prose outside. | Independent reviewer found no definite subject loss. |
| Image121 | Group and two oval portraits remain distinct. A cutoff already exists at the source photo edge. | Do not misattribute the source-edge cutoff to the candidate. |
| Image126 | Monument/plaque boundaries and inscriptions retained. | Text within photographed plaques is source content, not surrounding page-caption contamination. |

The comparison panels are under
`output/triage-20261023-argon-eval/source-review/`; original model outputs and
canonical source pixels remain inspectable independently.

Conclusion: the detector passes its numeric gate and improves the fresh-control
mean, but **source-quality equivalence and production adoption remain
unqualified**. No page-context/crop-only safety or actual production-route test
was run. Higher observed latency/cost and the retained historical Sol leader
also prevent claiming a simplification or economics win. Preserve C5, current
defaults and all existing blocked OCR stories.
