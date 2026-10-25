"""Recorded-event accounting: replay, incomplete writes, and attribution."""

import json

import pytest

from modules.common.run_instrumentation import reconcile_usage, retained_stage_metadata


def event(**overrides):
    return {"model": "fixture", "run_id": "probe", "stage_id": "ocr",
            "prompt_tokens": 100, "completion_tokens": 10, **overrides}


def report():
    return {"run_id": "probe", "stages": [], "pricing": {
        "models": {"fixture": {"prompt_per_1k": 1, "completion_per_1k": 2}},
    }}


def project(tmp_path, rows, summary=None):
    sink = tmp_path / "calls.jsonl"
    sink.write_text("".join(json.dumps(row) + "\n" for row in rows))
    summary = summary or report()
    reconcile_usage(summary, sink, {}, {}, 3)
    return summary, sink


def test_identical_distinct_calls_survive_repeated_projection(tmp_path):
    summary, sink = project(tmp_path, [event(), event()])
    assert summary["totals"]["calls"] == 2
    assert summary["totals"]["cost"] == 0.24
    before = sink.read_bytes()
    old_totals = summary["totals"].copy()
    reconcile_usage(summary, sink, {}, {}, 3)
    assert summary["totals"] == old_totals
    assert sink.read_bytes() == before
    assert summary["stages"][0]["wall_seconds"] is None
    assert summary["totals"]["timing_scope"] == "current_invocation"


def test_explicit_event_cost_survives_current_price_estimate(tmp_path):
    summary, _ = project(tmp_path, [event(cost=0.5), event()])
    assert summary["totals"]["cost"] == 0.62
    assert summary["totals"]["per_model"]["fixture"]["cost"] == 0.62


def test_missing_recorded_ledger_does_not_become_complete_zero_cost(tmp_path):
    summary, sink = project(tmp_path, [event()])
    sink.unlink()
    for _ in range(2):
        reconcile_usage(summary, sink, {}, {}, 3)
        assert summary["totals"]["calls"] == 0
        assert summary["totals"]["ledger_complete"] is False
        assert summary["totals"]["minimum_recorded_calls"] == 1


def test_partial_final_line_is_admitted_only_after_writer_finishes(tmp_path):
    summary, sink = project(tmp_path, [event()])
    with sink.open("a") as stream:
        stream.write(json.dumps(event())[:-1])
    reconcile_usage(summary, sink, {}, {}, 3)
    assert summary["totals"]["calls"] == 1
    assert summary["totals"]["ledger_complete"] is False
    assert summary["totals"]["ledger_issues"] == ["line 2: incomplete trailing usage record"]
    with sink.open("a") as stream:
        stream.write("}\n")
    reconcile_usage(summary, sink, {}, {}, 3)
    assert summary["totals"]["calls"] == 2
    assert summary["totals"]["ledger_complete"] is True


@pytest.mark.parametrize("bad", [None, [], event(prompt_tokens=-1), event(prompt_tokens=True),
                                      event(cost=float("nan")), event(run_id="another-run")])
def test_invalid_or_foreign_rows_are_visible_without_changing_raw_ledger(tmp_path, bad):
    summary, sink = project(tmp_path, [event(), bad])
    before = sink.read_bytes()
    assert summary["totals"]["calls"] == 1
    assert summary["totals"]["ledger_complete"] is False
    assert len(summary["totals"]["ledger_issues"]) == 1
    reconcile_usage(summary, sink, {}, {}, 3)
    assert sink.read_bytes() == before


def test_malformed_complete_line_is_not_hidden(tmp_path):
    summary, sink = project(tmp_path, [event()])
    with sink.open("a") as stream:
        stream.write("{malformed}\n")
    reconcile_usage(summary, sink, {}, {}, 3)
    assert summary["totals"]["calls"] == 1
    assert summary["totals"]["ledger_issues"] == ["line 2: invalid usage record"]


def test_retained_timing_does_not_restore_invalidated_artifact():
    previous = {"stages": [{"id": "ocr", "status": "done", "artifact": "stale.jsonl",
                            "wall_seconds": 5, "llm_totals": {"calls": 10}}]}
    stage, = retained_stage_metadata(previous, {"stages": {}})
    assert stage["status"] == "not_run"
    assert stage["artifact"] is None
    assert stage["wall_seconds"] == 5
    assert stage["extra"]["timing_scope"] == "latest_recorded_execution"


def test_unknown_stage_cost_is_retained_and_existing_ocr_alias_is_unambiguous(tmp_path):
    summary, sink = project(tmp_path, [event(stage_id="extract"), event(stage_id="retired")])
    summary["stages"] = []
    reconcile_usage(summary, sink, {"ocr": {"module": "ocr_ai_gpt51_v1", "stage": "extract"}}, {}, 3)
    assert {stage["id"] for stage in summary["stages"]} == {"ocr", "retired"}
    assert summary["totals"]["calls"] == 2
