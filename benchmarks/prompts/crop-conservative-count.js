/**
 * Conservative-count prompt for image crop extraction.
 * Reduces over-detection by emphasizing grouping and major elements only.
 */

const { buildMessages } = require("./_image-helpers");

const PROMPT_PREFIX = `Analyze this scanned book page. Find distinct photographs, illustrations, or visual elements.

Rules:
- Only count MAJOR visual elements (photos, illustrations, logos, seals)
- Stylized title text, decorative logos, or text in artistic/display fonts that function as standalone artwork ARE visual elements — include them
- Do NOT count ordinary section headings, person-name headings, certificate/body title lines, or other display text that is part of the document's reading flow rather than a standalone visual
- Do NOT count small decorative elements, horizontal rules, or text formatting
- When in doubt whether something is a separate image, group it with the nearest image
- A cover page or title page with decorative art = ONE image covering the full visual area
- Signatures next to seals = ONE combined image

Return JSON: {"images": [{"description": "...", "bbox": [x0, y0, x1, y1]}]}`;

const PROMPT_SUFFIX = `If no images: {"images": []}
JSON only, no other text.`;

module.exports = function (context) {
  const { vars, provider } = context;
  const providerId = provider?.id || "";
  const coordinates = providerId.includes("gemini-3.5-flash-lite")
    ? "Coordinates: integers 0-1000, origin top-left, with x0 < x1 and y0 < y1."
    : "Coordinates: normalized 0.0-1.0, origin top-left.";
  const promptText = `${PROMPT_PREFIX}\n${coordinates}\n${PROMPT_SUFFIX}`;
  return buildMessages(promptText, vars.image, providerId);
};
