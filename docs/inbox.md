# Doc Forge Inbox

This file captures ideas, insights, and potential architectural improvements discovered during development and manual tasks.

## Untriaged

- 2026-05-06 - From Conductor inbox: OpenAI's 2026-05-05 GPT-5.5
  Instant release says the ChatGPT default now uses GPT-5.5 Instant, the API
  exposure is `chat-latest`, and the model improved photo/image analysis,
  factuality, and concise answers. Treat it as a bounded challenger only if
  `chat-latest` is callable through the eval harness with image inputs.
  Candidate surfaces are the maintained `image-crop-extraction` /
  page-level crop deletion gate and the cheap content-hint preview pass.
  Compare against current Gemini/OpenAI winners, including the existing
  `openai:responses:gpt-5.5` page-context winner; do not alter maintained
  providers unless quality, latency, and cost beat current evidence. Source:
  https://openai.com/index/gpt-5-5-instant/

- 2026-05-01 — From Conductor Scout 028: Grok 4.3 is now documented for xAI API
  use and public snapshots describe text+image input, 1M context, and low
  output price. Evaluate it only as a bounded challenger if xAI credentials and
  provider wiring are cheap: candidate surfaces are the maintained
  `image-crop-extraction` / page-level crop deletion gate and any stronger-OCR
  blocker where text+image reasoning is actually relevant. Compare against the
  current Gemini/OpenAI winners; do not alter maintained providers unless the
  promptfoo/eval evidence wins on quality, latency, and cost. Source:
  `/Users/cam/.codex/worktrees/414d/conductor/docs/scout/scout-028-grok-4-3-api-eval-opportunities.md`
