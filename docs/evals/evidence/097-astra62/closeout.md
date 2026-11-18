# Story 273 opt-in reader close-out

2026-11-17. Cam approved landing the Doc Web opt-in table reader. The source
comparison and separate handwriting and crop decisions are in [Attempt 097](../../attempts/097-gpt62-astra-source-fidelity.md).

The close-out changed how the SDK opens the native input-count endpoint. The
repository locks OpenAI SDK 1.109.1, which predates its typed counter. The
client's public POST method sends the same count body to the same endpoint.
The exact model, count endpoint, two-dollar reservation, and inference request
remain part of the same contract. The old profile still rejects unknown models.
[SDK request method](https://github.com/openai/openai-python/blob/main/README.md#making-customundocumented-requests)
and [OpenAI count endpoint](https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count).

The [locked SDK consumer replay](closeout-consumer.json) used saved native
responses and verified request equality. An input count of 68,929 crossed
the reservation and issued zero inference calls. The driver exported 20 exact
cells with a qualification receipt. Manual inspection found the two-row Port
span, B8-S5 and B6-S3, the empty count cell, Q2-Z7 versus q2-z7, and the footer
span. The ambiguity run stopped with two uncertain cells and no qualification.
Retained outputs are under `output/runs/scout116-closeout-sdk109/runs/` in the
evaluation worktree. The first OCR stage is represented by an authored artifact
in this replay. No additional provider inference was used.

Focused recheck with `python -m pytest -q tests/test_table_source_review.py
tests/test_google_table_source_review.py tests/test_literal_qualification_offline.py`
passed 124 tests. The broader check had 445 passes, three obsolete-message
assertions and three setup errors from a missing local output directory.
The focused recheck covers both repairs. Changed Python module lint,
methodology compilation/check and Git whitespace verification passed.

The locked-SDK replay used SHA-256
`a942f6a1ad89076b15a8b9f9760fcb73d80a09093f5eda601b824b771f284759`
for `modules/common/openai_client.py` and
`a5ed54165c02d4684bf7a4e75f1195efda11ee072f0705e0ef68fdea10c4909f`
for `modules/common/table_source_review.py`. The
[opt-in runbook](../../../runbooks/astra62-literal-table-reader.md) records
setup, the eligible source boundary and rollback.
