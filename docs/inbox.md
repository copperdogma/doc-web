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

## Processed

- 2026-07-20 — Closed the older Conductor Scout 028 Grok item with a newer
  Grok 4.5 direct-xAI evaluation. The model was callable with image input and
  valid Responses output, but the maintained detector scored only `0.8026` and
  `12/13` versus Gemini 3 Flash's `0.9703` and `13/13`. A high-reasoning retry
  repeated the source-confirmed `Image011` bbox undercoverage, so the
  page-context gate remained ladder-gated and maintained providers did not
  change. Proof: `docs/evals/attempts/016-grok45-bounded-challenger.md`.

- 2026-06-09 — Closed the Conductor Scout 044 Claude Fable 5 item with direct
  Anthropic API eval evidence. Fable 5 is callable through the repo-local key
  and the existing Anthropic direct/no-sampling provider pattern, but did not
  beat maintained quality, latency, or cost on the bounded page-context crop
  deletion gate: it scored `0.9091` / `20/22` versus the GPT-5.5 Responses
  `1.0` / `22/22` winner, cost about `$2.1137` total, and repeated the same
  false negatives on `page-122-001` and `page-126-000` that Opus 4.8 missed.
  Decision: do not alter maintained providers. Proof:
  `docs/evals/attempts/013-fable5-bounded-challenger.md`.

- 2026-05-28 — Closed the Conductor Scout 043 Claude Opus 4.8 item with
  direct Anthropic API eval evidence. Added a bounded promptfoo provider because
  promptfoo's built-in Anthropic provider sends `temperature`, which
  `claude-opus-4-8` rejects, and updated the local Anthropic OCR client to omit
  sampling params for Opus 4.8. Opus 4.8 is callable with adaptive
  thinking/high effort, but did not beat maintained quality: detector scored
  `0.7669` / `10/13` versus the Gemini 3 Flash `0.9703` / `13/13` winner;
  page-context scored `0.9091` / `20/22` versus the GPT-5.5 Responses `1.0` /
  `22/22` winner; `xhigh` failed-case retries repaired `0` cases; and the
  corrected Barney/Alverson handwritten image-entry screen remained below bar
  with `0.711207` / `0.680902`. Decision: do not alter maintained providers.
  Proof: `docs/evals/attempts/012-opus48-bounded-challenger.md`.

- 2026-05-20 — Closed the Conductor Scout 038 Kimi K2.6 item with direct
  Moonshot API eval evidence. Added a bounded promptfoo provider and reran the
  maintained crop detector plus page-context deletion gate. Kimi K2.6 is
  callable and cheaper on the page-context gate, but did not beat maintained
  quality: `image-crop-extraction` scored `0.8981` / `12/13` versus the Gemini
  3 Flash `0.9703` / `13/13` winner, and `crop-page-level-deletion-gate`
  scored `0.9545` / `21/22` versus the GPT-5.5 Responses `1.0` / `22/22`
  winner. Thinking-mode retries of the failed cases did not repair the misses.
  Decision: do not alter maintained providers. Proof:
  `docs/evals/attempts/011-kimi-k26-bounded-challenger.md`.
