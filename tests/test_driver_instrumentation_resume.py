"""Persistent run usage accounting through real driver resume/rebuild commands.

The temporary producers emit synthetic usage receipts, never provider requests.
All artifacts and registry records stay under the test's isolated output root.
"""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL = "driver-instrumentation-fixture"


def _read_calls(run_dir):
    sink = run_dir / "instrumentation_calls.jsonl"
    return [json.loads(line) for line in sink.read_text().splitlines() if line.strip()] if sink.exists() else []


@pytest.fixture
def usage_probe(tmp_path):
    producer = tmp_path / "usage_producer.py"
    producer.write_text(textwrap.dedent("""\
        import argparse
        import json
        import uuid
        from pathlib import Path
        from modules.common.utils import log_llm_usage

        parser = argparse.ArgumentParser()
        parser.add_argument("--out", required=True)
        parser.add_argument("--input")
        parser.add_argument("--calls", type=int, default=0)
        parser.add_argument("--prompt-tokens", type=int, required=True)
        parser.add_argument("--completion-tokens", type=int, required=True)
        parser.add_argument("--cost", type=float, required=True)
        parser.add_argument("--fail", action="store_true")
        parser.add_argument("--state-file")
        parser.add_argument("--progress-file")
        parser.add_argument("--run-id")
        args = parser.parse_args()
        if args.input:
            assert json.loads(Path(args.input).read_text())["text"] == "Deterministic source content"
        for _ in range(args.calls):
            log_llm_usage(
                "driver-instrumentation-fixture", args.prompt_tokens, args.completion_tokens,
                provider="fixture", request_id="fixture-" + uuid.uuid4().hex, cost=args.cost,
            )
        if args.fail:
            raise SystemExit(7)
        Path(args.out).write_text(json.dumps({
            "page": 1, "text": "Deterministic source content",
        }) + "\\n")
        """))
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"modules": {
        "usage_probe_v1": {
            "stage": "transform", "entrypoint": str(producer),
            "input_schema": "page_doc_v1", "output_schema": "page_doc_v1",
        },
    }}))
    pricing = tmp_path / "pricing.json"
    pricing.write_text(json.dumps({"currency": "USD", "default": {
        "prompt_per_1k": 0, "completion_per_1k": 0,
    }}))
    source = tmp_path / "source.txt"
    source.write_text("Fixture source; never sent to a provider.")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")

    def run(*extra_args, upstream_calls=1, downstream_calls=0, downstream_fails=False,
            expected_returncode=0, run_id="usage-resume-probe"):
        recipe = tmp_path / "recipe.json"
        recipe.write_text(json.dumps({
            "name": "instrumentation-resume-fixture",
            "input": {"text_glob": str(source)},
            "stages": [
                {"id": "upstream", "stage": "transform", "module": "usage_probe_v1",
                 "out": "elements.jsonl", "params": {
                     "calls": upstream_calls, "prompt_tokens": 100, "completion_tokens": 10, "cost": 0.125,
                 }},
                {"id": "downstream", "stage": "transform", "module": "usage_probe_v1",
                 "needs": ["upstream"], "inputs": {"input": "upstream"}, "out": "elements.jsonl",
                 "params": {
                     "calls": downstream_calls, "prompt_tokens": 200, "completion_tokens": 20, "cost": 0.25,
                     "fail": downstream_fails,
                 }},
            ],
        }))
        run_dir = tmp_path / "output" / "runs" / run_id
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "driver.py"), "--recipe", str(recipe),
             "--registry", str(registry), "--price-table", str(pricing), "--instrument",
             "--run-id", run_id, "--output-dir", str(run_dir), *extra_args],
            cwd=REPO_ROOT, env=env, capture_output=True, text=True,
        )
        assert result.returncode == expected_returncode, result.stdout + result.stderr
        assert (tmp_path / "output" / "run_manifest.jsonl").exists()
        return run_dir, json.loads((run_dir / "instrumentation.json").read_text())

    return run


def _assert_usage(report, calls, *, count, prompt_tokens, completion_tokens, cost):
    """Compare declared fixture usage with both the report and its raw receipts."""
    expected = {
        "calls": count, "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens, "cost": cost,
    }
    assert len(calls) == count
    assert report["totals"]["usage_scope"] == "recorded_run_history"
    assert report["totals"]["timing_scope"] == "current_invocation"
    for key, value in expected.items():
        assert report["totals"][key] == pytest.approx(value), (key, report["totals"], expected)
    if count:
        assert set(report["totals"]["per_model"]) == {MODEL}
        for key, value in expected.items():
            assert report["totals"]["per_model"][MODEL][key] == pytest.approx(value)
    else:
        assert report["totals"]["per_model"] == {}
    reported_calls = [call for stage in report["stages"] for call in stage.get("llm_calls", [])]
    assert sorted(call["request_id"] for call in reported_calls) == sorted(call["request_id"] for call in calls)


def test_downstream_resume_keeps_retained_upstream_usage(usage_probe):
    run_dir, initial = usage_probe()
    original_calls = _read_calls(run_dir)
    _assert_usage(initial, original_calls, count=1, prompt_tokens=100, completion_tokens=10, cost=0.125)

    run_dir, resumed = usage_probe("--allow-run-id-reuse", "--start-from", "downstream")
    assert _read_calls(run_dir) == original_calls
    _assert_usage(resumed, original_calls, count=1, prompt_tokens=100, completion_tokens=10, cost=0.125)


def test_rerun_adds_new_usage_once(usage_probe):
    run_dir, initial = usage_probe(downstream_calls=1)
    _assert_usage(initial, _read_calls(run_dir), count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)

    run_dir, rerun = usage_probe("--allow-run-id-reuse", "--start-from", "downstream", downstream_calls=1)
    calls = _read_calls(run_dir)
    assert [call["stage_id"] for call in calls] == ["upstream", "downstream", "downstream"]
    _assert_usage(rerun, calls, count=3, prompt_tokens=500, completion_tokens=50, cost=0.625)


def test_zero_call_repeats_do_not_change_persistent_usage(usage_probe):
    run_dir, initial = usage_probe(downstream_calls=1)
    calls = _read_calls(run_dir)
    _assert_usage(initial, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)
    run_dir, first_repeat = usage_probe("--allow-run-id-reuse", "--start-from", "downstream", downstream_calls=0)
    run_dir, second_repeat = usage_probe("--allow-run-id-reuse", "--start-from", "downstream", downstream_calls=0)
    assert _read_calls(run_dir) == calls
    _assert_usage(first_repeat, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)
    _assert_usage(second_repeat, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)


def test_skip_done_preserves_latest_actual_stage_execution_timing(usage_probe):
    run_dir, initial = usage_probe(downstream_calls=1)
    calls = _read_calls(run_dir)
    timing_fields = ("started_at", "ended_at", "wall_seconds", "cpu_user_seconds", "cpu_system_seconds")
    timings = {
        stage["id"]: {field: stage[field] for field in timing_fields}
        for stage in initial["stages"]
    }
    assert all(values["wall_seconds"] > 0 for values in timings.values())

    run_dir, skipped = usage_probe("--allow-run-id-reuse", "--skip-done", downstream_calls=1)
    assert _read_calls(run_dir) == calls
    _assert_usage(skipped, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)
    assert {stage["id"] for stage in skipped["stages"]} == set(timings)
    for stage in skipped["stages"]:
        assert stage["status"] == "skipped"
        assert {field: stage[field] for field in timing_fields} == timings[stage["id"]]
        assert stage["extra"]["timing_scope"] == "latest_recorded_execution"


def test_repeated_skip_done_does_not_execute_previously_skipped_stages(usage_probe):
    run_dir, initial = usage_probe(downstream_calls=1)
    calls = _read_calls(run_dir)
    _assert_usage(initial, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)
    run_dir, first_skip = usage_probe("--allow-run-id-reuse", "--skip-done", downstream_calls=1)
    assert _read_calls(run_dir) == calls
    _assert_usage(first_skip, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)

    run_dir, second_skip = usage_probe("--allow-run-id-reuse", "--skip-done", downstream_calls=1)
    assert _read_calls(run_dir) == calls, "Repeated --skip-done must not execute the same completed artifacts"
    _assert_usage(second_skip, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)
    assert all(stage["status"] == "skipped" for stage in second_skip["stages"])


def test_force_rebuild_preserves_recorded_usage_for_the_same_run(usage_probe):
    run_dir, initial = usage_probe()
    calls = _read_calls(run_dir)
    _assert_usage(initial, calls, count=1, prompt_tokens=100, completion_tokens=10, cost=0.125)
    obsolete_artifact = run_dir / "disposable-artifact.txt"
    obsolete_artifact.write_text("Full force must rebuild artifacts.")

    run_dir, rebuilt = usage_probe("--force", upstream_calls=0, downstream_calls=0)
    assert not obsolete_artifact.exists()
    assert _read_calls(run_dir) == calls, "Artifact rebuild must not erase already recorded usage"
    _assert_usage(rebuilt, calls, count=1, prompt_tokens=100, completion_tokens=10, cost=0.125)


def test_new_run_id_starts_with_separate_recorded_usage(usage_probe):
    old_run_dir, _ = usage_probe()
    original_calls = _read_calls(old_run_dir)
    new_run_dir, fresh = usage_probe(run_id="usage-independent-probe", upstream_calls=0, downstream_calls=0)
    assert _read_calls(old_run_dir) == original_calls
    assert new_run_dir != old_run_dir
    _assert_usage(fresh, _read_calls(new_run_dir), count=0, prompt_tokens=0, completion_tokens=0, cost=0)


def test_deleted_summary_reconstructs_usage_without_inventing_upstream_timing(usage_probe):
    run_dir, initial = usage_probe(downstream_calls=1)
    calls = _read_calls(run_dir)
    _assert_usage(initial, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)
    (run_dir / "instrumentation.json").unlink()

    run_dir, reconstructed = usage_probe("--allow-run-id-reuse", "--start-from", "downstream")
    assert _read_calls(run_dir) == calls
    _assert_usage(reconstructed, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)
    upstream = next(stage for stage in reconstructed["stages"] if stage["id"] == "upstream")
    assert upstream["status"] == "done"
    assert upstream["wall_seconds"] is None
    assert upstream["cpu_user_seconds"] is None
    assert upstream["extra"]["timing_scope"] == "unknown"


def test_failed_stage_usage_survives_successful_zero_call_resume(usage_probe):
    run_dir, failed = usage_probe(downstream_calls=1, downstream_fails=True, expected_returncode=1)
    calls = _read_calls(run_dir)
    _assert_usage(failed, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)
    downstream = next(stage for stage in failed["stages"] if stage["id"] == "downstream")
    assert downstream["status"] == "failed"
    assert not Path(downstream["artifact"]).exists()

    run_dir, resumed = usage_probe("--allow-run-id-reuse", "--start-from", "downstream")
    assert _read_calls(run_dir) == calls
    _assert_usage(resumed, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)
    downstream = next(stage for stage in resumed["stages"] if stage["id"] == "downstream")
    assert downstream["status"] == "done"
    assert Path(downstream["artifact"]).exists()


def test_partial_upstream_rerun_keeps_cost_without_resurrecting_invalidated_downstream(usage_probe):
    run_dir, initial = usage_probe(downstream_calls=1)
    calls = _read_calls(run_dir)
    downstream = next(stage for stage in initial["stages"] if stage["id"] == "downstream")
    artifact = Path(downstream["artifact"])
    assert artifact.exists()

    run_dir, partial = usage_probe(
        "--allow-run-id-reuse", "--start-from", "upstream", "--end-at", "upstream",
        upstream_calls=0, downstream_calls=0,
    )
    assert _read_calls(run_dir) == calls
    _assert_usage(partial, calls, count=2, prompt_tokens=300, completion_tokens=30, cost=0.375)
    state = json.loads((run_dir / "pipeline_state.json").read_text())
    assert "downstream" not in state["stages"]
    assert not artifact.exists()
    downstream = next(stage for stage in partial["stages"] if stage["id"] == "downstream")
    assert downstream["status"] == "not_run"
    assert downstream["artifact"] is None
    assert downstream["llm_totals"]["calls"] == 1
    assert downstream["llm_totals"]["cost"] == pytest.approx(0.25)
