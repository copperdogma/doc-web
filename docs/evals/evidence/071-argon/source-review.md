# Independent source reviews — 2026-10-13

Reviewer: GPT-6.1 Sol high, chosen for semantic correctness risk. Read-only; no provider inference or file mutations. The owner retained these findings.

Before candidate inference, the reviewer confirmed Alverson's “a good prospect” against exact scan pixels, reusing the resolution already documented in Attempts061/068. Attempt046's concern remains historical. This was a targeted review, not certification of every faint handwritten glyph.

The two clear confirmation-v2 sources match their authored goldens: 13 cells/five rows and 23 cells/six rows, including spans, unusual literal tokens, blank/dash, and case differences. Negative I/l stamp glyphs are optically identical; both must be held. After inference, both reader arms preserved all 36 clear cells and flagged exactly row1/cell1 and row2/cell1 in the negative page. Matching provisional negative HTML does not establish optical glyph recovery.

Recovered Image011 candidate boxes contain the complete logo, seal, handwritten signatures, and horizontal rules. The control includes seal/signature ink but clips approximately 10–12 pixels from right rule tails. Full-control boxes match the recovered-control boxes. No page-safety claim follows.

Nine candidate detector pages were source-reviewed. Image000/008/011/013/021 are complete. Image003 ends at a grass ink edge; Image020 has roughly 1–2 pixel photo-border edges, without identifiable building/animal loss; these remain uncertain raster-edge findings. Image001 clips date ink reaching y762 with a box ending at y760: a confirmed small source-completeness failure. Image037's second `[.097,.642,.492,898]` bbox mixes units and is invalid; no repair was made. Remaining four pages were not run.

Barney's frozen .988117 output changes source/golden `comrads` to `comrades` and `mede` to `made`. These establish a literal fidelity miss. The golden's “least expected it were cut down” may contain an unsupported `it`; scan wording appears to match the candidate there. That is a separate golden concern, not candidate deletion. Faint names and `[soon]` are not decisive. No golden edits or rescoring occurred; Alverson remains unmeasured after the Barney stop.
