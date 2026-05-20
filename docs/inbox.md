# Doc Forge Inbox

This file captures ideas, insights, and potential architectural improvements discovered during development and manual tasks.

## Untriaged

- 2026-05-19 — From Conductor Scout 035: Google's Gemini API `gemini-3.5-flash`
  is a strong doc-web challenger because it has image/PDF input, structured
  output, 1M context, and fresh media-resolution migration guidance. If Google
  credential/cost setup is cheap, run it as a bounded challenger on the
  maintained `image-crop-extraction` / page-context crop deletion gates and the
  parked stronger-OCR blocker. Compare against the current winners
  (`gpt-5.5` for page-context and Gemini 3.1 Flash Lite where it still wins);
  do not alter default providers unless registry evidence wins on quality,
  latency, and cost. Source:
  `/Users/cam/.codex/worktrees/dfe1/conductor/docs/scout/scout-035-google-gemini-35-flash-api-eval-opportunities.md`

- 2026-05-01 — From Conductor Scout 028: Grok 4.3 is now documented for xAI API
  use and public snapshots describe text+image input, 1M context, and low
  output price. Evaluate it only as a bounded challenger if xAI credentials and
  provider wiring are cheap: candidate surfaces are the maintained
  `image-crop-extraction` / page-level crop deletion gate and any stronger-OCR
  blocker where text+image reasoning is actually relevant. Compare against the
  current Gemini/OpenAI winners; do not alter maintained providers unless the
  promptfoo/eval evidence wins on quality, latency, and cost. Source:
  `/Users/cam/.codex/worktrees/414d/conductor/docs/scout/scout-028-grok-4-3-api-eval-opportunities.md`
