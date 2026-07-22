# Kimi K3 Launch-Day Challenger

Date: 2026-07-16
Repo HEAD at measurement: `ac574bf`

## Trigger and eval ladder

Moonshot released Kimi K3 on 2026-07-16. The bounded challenger ladder remains:

1. `image-crop-extraction` with `conservative-count` (13 cases; maintained
   Gemini 3 Flash baseline `0.9703`, `13/13`).
2. `crop-page-level-deletion-gate` (22 cases; hard `22/22` contract; maintained
   GPT-5.5 Responses winner).

This is aligned with the Ideal's fidelity and inspectable-artifact requirements
and with C4/C5: a new ceiling model must beat the maintained quality gates, not
merely offer a new provider or lower price.

## Live access and transport verification

Official Moonshot documentation and authenticated API checks confirmed:

- model ID `kimi-k3` is visible to the Dossier Moonshot account through
  `GET https://api.moonshot.ai/v1/models`;
- K3 uses Chat Completions with base URL `https://api.moonshot.ai/v1`;
- K3 always reasons and requires top-level `reasoning_effort: max`; the K2.x
  `thinking` field must not be sent;
- official prices are `$0.30/M` cached input, `$3.00/M` uncached input, and
  `$15.00/M` output.

The existing `benchmarks/providers/moonshot_kimi_chat.py` was generalized to
preserve the K2.6 request contract while emitting the K3 reasoning contract and
model-specific cost calculation. Focused provider/env tests pass (`6 passed`).
The Dossier credential was supplied directly to the child process without
printing or checking it into the repo.

## Launch-day availability result

K3 was not inference-callable during this pass despite being account-visible:

- a minimal authenticated text request reached Moonshot and returned HTTP 429
  `engine_overloaded_error`;
- a minimal base64 vision request returned the same 429 after about 19 seconds;
- a one-case `image-crop-extraction` promptfoo smoke remained in-flight for
  nearly six minutes across bounded retry attempts and was stopped without
  writing a result artifact;
- a second single-attempt smoke also failed to complete and was stopped.

Because no model output was produced, there is no provisional quality score and
no mismatch to classify as model-wrong, golden-wrong, or ambiguous. The
page-context gate was not run: proceeding to 22 cases before a one-case vision
smoke succeeds would waste cost and cannot answer the quality question.

## Decision

**Do not adopt yet; eval blocked on launch-day provider availability.** This is
not negative model-quality evidence. Retry the same maintained ladder once a
minimal K3 vision request and one-case promptfoo smoke both complete without
`engine_overloaded_error` or a transport stall. Do not change prompts, scorers,
goldens, or maintained providers before that retry.

Official references:

- <https://www.kimi.com/blog/kimi-k3>
- <https://platform.kimi.ai/docs/guide/kimi-k3-quickstart>
- <https://platform.kimi.ai/docs/api/models-overview>
- <https://platform.kimi.ai/docs/pricing/chat-k3>
