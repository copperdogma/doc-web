# Story234 offline integration verification

Runtime remains default-off, unconfigured and undeployed. Zero paid/live-provider
calls. These are mocked provider integration outputs, not new model-quality or
provider-cost observations. Usage/cost fields in sidecars are synthetic test values.

Final command:

```sh
/Users/cam/Documents/Projects/doc-web/.venv/bin/python scripts/verify_jev_shadow.py --output-dir output/runs/story234-jev-shadow-verification-r4
pytest tests/test_jev_consistency_shadow.py tests/test_plan_onward_document_consistency_v1.py -q
ruff check modules/validate/plan_onward_document_consistency_v1/main.py modules/validate/plan_onward_document_consistency_v1/jev_shadow.py tests/test_jev_consistency_shadow.py scripts/verify_jev_shadow.py tests/fixtures/jev_shadow/mock_provider
```

26affected tests passed. Real driver disabled/enabled/provider-failure runs passed;
all primary JSONL report rows and three authoritative sidecars are equal after
removing run ID/timestamps. Enabled uncertain with low confidence stays review;
provider failure keeps authoritative classification and unknown cost reservation.

Safe copies of the enabled/failure shadow and authoritative artifacts are here.
Full synthetic pipeline outputs remain under the recorded `output/runs` paths.
The verifier creates synthetic sources itself and blocks network through explicit
mock providers, with inherited provider credentials excluded.

Prior Story233 evaluation evidence is frozen and unchanged. This integration uses
actual compact extracted-HTML profiles and already-derived conventions, so prior
synthetic source-prose accuracy is not asserted for runtime inputs. Existing full
planner always runs; fallback is its already-computed result, not a new serial
GPT call. This shadow implementation measures added JEV behavior/cost only and
makes no production savings claim.
