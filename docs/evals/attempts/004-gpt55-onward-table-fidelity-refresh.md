# GPT-5.5 Onward Table Fidelity Refresh

Date: 2026-04-24
Repo HEAD at measurement: `aa5b577`

## Trigger

After the maintained crop surfaces were rerun with `gpt-5.5`, the highest-signal
non-crop promptfoo benchmark with recent GPT-5.4 history was also screened:
`onward-table-fidelity`.

## Command

```bash
cd benchmarks && promptfoo eval -c tasks/onward-table-fidelity.yaml \
  --no-cache --filter-providers 'openai:chat:gpt-5.5' \
  --output results/gpt55-onward-table-fidelity-20260424.json -j 1
```

Promptfoo version warning during the run: installed `0.121.1`, latest available
reported by promptfoo as `0.121.7`.

## Result

`gpt-5.5` produced the strongest aggregate score recorded so far on this
surface, but it did not produce exact table matches.

| Case | Score | Promptfoo Pass | Main Error Class |
| --- | ---: | --- | --- |
| `golden/onward/alma.html` | `0.9333` | fail | child-count and continuation placement drift |
| `golden/onward/arthur.html` | `0.9918` | fail | name/date transcription mismatches |
| `golden/onward/marie_louise.html` | `0.9890` | fail | total-row cell placement and date drift |

Aggregate:

- `structure_preservation = 0.9714`
- `promptfoo_pass_rate = 0/3`
- average latency: `162210 ms`
- total tokens: `192778`
- estimated current API cost: `$1.9268` total (`$0.6423` per chapter call)
- provider errors: `0`

The prior best aggregate score was Gemini 3.1 Pro at `0.969`. GPT-5.5 is a
score-and-cost challenger, but the residual exact-cell errors still need source
review before any recipe switch.

## Decision

Do not switch the applied Onward table recipe in this pass. Record GPT-5.5 as
the current aggregate-score leader, keep GPT-5.4 as the value winner with known
cost, and leave the applied Gemini 3.1 Pro recipe unchanged until value and
failure-class review are complete.
