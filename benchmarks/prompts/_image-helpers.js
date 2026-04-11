/**
 * Shared helpers for building provider-specific image content blocks.
 *
 * OpenAI:    { type: "image_url", image_url: { url: "data:..." } }
 * Anthropic: { type: "image", source: { type: "base64", media_type: "...", data: "..." } }
 * Google:    { inlineData: { mimeType: "...", data: "..." } }
 */

function extractBase64(dataUri) {
  const base64Data = dataUri.replace(/^data:image\/[^;]+;base64,/, "");
  const mediaType =
    dataUri.match(/^data:(image\/[^;]+);/)?.[1] || "image/jpeg";
  return { base64Data, mediaType };
}

/**
 * Build the image content block appropriate for the given provider.
 */
function buildImageContent(dataUri, providerId) {
  const { base64Data, mediaType } = extractBase64(dataUri);

  if (providerId.startsWith("anthropic:")) {
    return {
      type: "image",
      source: { type: "base64", media_type: mediaType, data: base64Data },
    };
  }

  if (providerId.startsWith("google:")) {
    return {
      inlineData: { mimeType: mediaType, data: base64Data },
    };
  }

  // OpenAI (default)
  return {
    type: "image_url",
    image_url: { url: dataUri },
  };
}

function normalizeDataUris(dataUriOrList) {
  return Array.isArray(dataUriOrList) ? dataUriOrList : [dataUriOrList];
}

/**
 * Build a complete message array for a vision prompt.
 * Google uses { parts: [...] }, OpenAI/Anthropic use { content: [...] }.
 */
function buildMessages(promptText, dataUriOrList, providerId) {
  const imageContents = normalizeDataUris(dataUriOrList).map((dataUri) =>
    buildImageContent(dataUri, providerId)
  );

  if (providerId.startsWith("google:")) {
    return [
      {
        role: "user",
        parts: [
          { text: promptText },
          ...imageContents,
        ],
      },
    ];
  }

  return [
    {
      role: "user",
      content: [
        { type: "text", text: promptText },
        ...imageContents,
      ],
    },
  ];
}

module.exports = { buildImageContent, buildMessages };
