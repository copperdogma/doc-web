# Native runtime observation — 2026-09-21

One native JEV 1.13.0 request through the landed runtime seam, using the dedicated
Doc Web runtime key and retained synthetic r4 input. The existing planner output
was mock-authored; no GPT call or private document was sent.

Observed conformant at confidence0.70, below the configured0.80 threshold:
planner_fallback / low_confidence. Latency303.043ms;1054 input and64 output tokens;
usage-priced costUS$0.000044268; no unknown reservation. All five authoritative
JSON files retained their exact hashes. The per-call exposure cap wasUS$0.002688.

This establishes runtime access, native contract parsing and fallback behavior
on one synthetic input. It does not establish representative quality, confidence
calibration or savings. Persistent shadow remains disabled. The retained run_id
identifies the source planner run; this observation is identified by this directory
and its sidecar created_at. No retries or additional model calls occurred.
