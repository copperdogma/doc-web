/**
 * Page-context crop validation prompt.
 * Image 1 is the full source page. Image 2 is the extracted crop.
 */

const { buildMessages } = require("./_image-helpers");

const PROMPT_TEXT = `You will receive TWO images in this order:
1. The full scanned book page.
2. The extracted crop from that page.

Judge whether the extracted crop is acceptable as an illustration crop when compared against the full page context.
This gate primarily checks whether page text or neighboring page visuals were left in the crop. It is not a fine-art composition scorer.

Return JSON: {"verdict": "pass" or "fail", "has_page_text": true or false, "excessive_blank": true or false, "reason": "brief explanation"}

PASS when:
- The crop contains only the illustration or visual element from the page.
- Any visible text is integral to the image itself (for example: engraved plaque text, logo text, seal text, handwriting on a photo, or monument inscriptions).
- The crop is not excessively blank. Large light regions inside a photograph, such as sky, snow, wall, halftone background, or studio backdrop, count as image content rather than empty page space.

FAIL when:
- The crop includes page-level caption text, paragraph text, headers, page-layout text, or other surrounding document text that should have stayed outside the crop.
- Any surrounding page text from an adjacent plaque, neighboring figure, or page layout is still visible at the crop edge, even if the main subject is correct.
- The crop is obviously incomplete because the full page shows a large, unmistakable part of the same intended visual outside the crop, or it is so loose that surrounding page content is part of the crop.
- More than 40% of the crop is empty page margin, scanner background, or blank paper with no real image content.

Important:
- Use the FULL PAGE only as context for whether visible text belongs to the page or to the image.
- Do not fail just because the image itself contains meaningful text.
- Be strict about external text leakage: if text belongs to the page or to a neighboring visual element outside the intended crop, that is a FAIL even when the leakage is small.
- Do not fail tight framing merely because artwork or a photograph reaches the crop edge, or because there is minor edge clipping on line art. Fail incompleteness only when the full-page context clearly shows a large missing part of the intended visual.
- Do not count sky, snow, wall, studio backdrop, faded photo background, or other natural light areas inside the image as excessive blank space.
- When uncertain, PASS.

Return ONLY valid JSON.`;

module.exports = function (context) {
  const { vars, provider } = context;
  return buildMessages(
    PROMPT_TEXT,
    [vars.page_image, vars.crop_image],
    provider?.id || ""
  );
};
