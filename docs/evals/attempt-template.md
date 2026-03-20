# Attempt NNN — {eval-id}: {short title}

**Eval:** {eval-id from registry}
**Date:** YYYY-MM-DD
**Worker Model:** {AI model doing the improvement work}
**Subject Model / Surface:** {model, prompt, or pipeline surface under test}
**Mission:** Improve {metric} from {current} to {target}

## Prior Attempts

{Summarize what previous attempts tried, what worked, and what should not be
retried without new evidence.}

## Plan

{What will be tried and why. Reference the improvement vector:
- prompt engineering
- scorer or assertion tuning
- model selection
- pipeline logic
- golden correction
- latency or cost optimization
}

## Work Log

{Dated entries: what was tried, what happened, measurements, and conclusions}

## Conclusion

**Result:** {succeeded | failed | inconclusive}

**Score before:** {metrics / latency / cost}
**Score after:** {metrics / latency / cost}

**What worked:**
- {list}

**What did not work:**
- {list}

**What not to retry without new evidence:**
- {dead ends or blocked repeats}

**Retry when:**
- {condition}: {why that condition might change the outcome}

## Definition of Done

- [ ] Read the target eval's prior attempts first
- [ ] Measured a before state or confirmed the current recorded baseline
- [ ] Recorded after-state metrics
- [ ] Updated `docs/evals/registry.yaml`
- [ ] Classified major mismatches when the eval used a golden or rubric
- [ ] Filled in the Conclusion section completely
- [ ] Documented retry conditions or dead ends if the attempt failed
