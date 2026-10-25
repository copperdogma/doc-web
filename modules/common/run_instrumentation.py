"""Rebuild recorded run usage from its append-only ledger, without reinference."""

import json
import math
from pathlib import Path


def read_report(path, run_id):
    try:
        report = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return report if isinstance(report, dict) and report.get("run_id") == run_id else {}


def retained_stage_metadata(previous, state):
    """Keep known timing, never resurrect an invalidated artifact or status."""
    stages = []
    for old in previous.get("stages", []):
        stage = dict(old)
        current = state.get("stages", {}).get(stage["id"], {})
        stage.update(status=current.get("status", "not_run"), artifact=current.get("artifact"))
        stage["extra"] = {**stage.get("extra", {}), "timing_scope": "latest_recorded_execution"}
        stages.append(stage)
    return stages


def _read_calls(path, run_id):
    groups = {}
    issues = []
    try:
        data = Path(path).read_bytes()
    except FileNotFoundError:
        return groups, issues
    # Re-read the small local ledger on each refresh. An unfinished final line
    # is never consumed, so a later read can admit it when the writer finishes.
    for number, line in enumerate(data.splitlines(keepends=True), 1):
        if not line.endswith(b"\n"):
            issues.append(f"line {number}: incomplete trailing usage record")
            continue
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if not isinstance(event, dict) or not isinstance(event.get("model"), str) or not event["model"]:
                raise ValueError("invalid model")
            if any(type(event.get(key)) is not int or event[key] < 0
                   for key in ("prompt_tokens", "completion_tokens")):
                raise ValueError("invalid tokens")
            cost = event.get("cost")
            if cost is not None and (type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0):
                raise ValueError("invalid cost")
            stage_id = event.get("stage_id")
            if stage_id is not None and not isinstance(stage_id, str):
                raise ValueError("invalid stage identity")
        except (ValueError, TypeError, UnicodeDecodeError):
            issues.append(f"line {number}: invalid usage record")
            continue
        if event.get("run_id") not in (None, run_id):
            issues.append(f"line {number}: conflicting run identity")
            continue
        groups.setdefault(stage_id or "unattributed", []).append(event)
    return groups, issues


def _usage_totals(calls, pricing):
    totals = {"calls": len(calls), "prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0}
    models = {}
    for event in calls:
        model = event["model"]
        cost = event.get("cost")
        if cost is None:
            rate = pricing.get("models", {}).get(model) or pricing.get("default", {})
            cost = round((event["prompt_tokens"] * rate.get("prompt_per_1k", 0)
                          + event["completion_tokens"] * rate.get("completion_per_1k", 0)) / 1000, 6)
        values = {"prompt_tokens": event["prompt_tokens"], "completion_tokens": event["completion_tokens"], "cost": cost}
        entry = models.setdefault(model, {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0})
        entry["calls"] += 1
        for key, value in values.items():
            totals[key] += value
            entry[key] += value
        entry["cost"] = round(entry["cost"], 6)
    totals["cost"] = round(totals["cost"], 6)
    return totals, models


def reconcile_usage(report, ledger_path, nodes, state, invocation_wall_seconds):
    """Project each valid ledger row once; prior summary totals are never added."""
    groups, issues = _read_calls(ledger_path, report["run_id"])
    stages = {stage["id"]: stage for stage in report.get("stages", [])}
    # Retain the existing old-OCR attribution only when it has one unambiguous
    # owner. Otherwise its recorded spend remains visible as a separate stage.
    ocr_ids = [sid for sid, node in nodes.items() if node.get("module") == "ocr_ai_gpt51_v1"]
    if "extract" in groups and "extract" not in nodes and len(ocr_ids) == 1:
        groups.setdefault(ocr_ids[0], []).extend(groups.pop("extract"))
    for sid in groups:
        if sid not in stages:
            node = nodes.get(sid, {})
            current = state.get("stages", {}).get(sid, {})
            stages[sid] = {
                "schema_version": "instrumentation_stage_v1", "id": sid,
                "stage": node.get("stage", "unknown"), "module_id": node.get("module"),
                "status": current.get("status", "not_run"), "artifact": current.get("artifact"),
                "wall_seconds": None, "cpu_user_seconds": None, "cpu_system_seconds": None,
                "extra": {"timing_scope": "unknown"},
            }
    for sid, stage in stages.items():
        calls = groups.get(sid, [])
        totals, models = _usage_totals(calls, report.get("pricing", {}))
        stage.update(llm_calls=calls, llm_totals=totals)
        stage["extra"] = {**stage.get("extra", {}), "per_model": models,
                          "usage_scope": "recorded_run_history"}
    all_calls = [event for calls in groups.values() for event in calls]
    prior_totals = report.get("totals", {})
    minimum_calls = max(prior_totals.get("calls", 0), prior_totals.get("minimum_recorded_calls", 0))
    if len(all_calls) < minimum_calls:
        issues.append("usage ledger contains fewer valid records than a prior summary; history is incomplete")
    totals, models = _usage_totals(all_calls, report.get("pricing", {}))
    totals.update(
        per_model=models, wall_seconds=round(invocation_wall_seconds, 6),
        usage_scope="recorded_run_history", timing_scope="current_invocation",
        cost_basis="explicit event costs; otherwise estimate under this report's price sheet",
        ledger_complete=not issues, ledger_issues=issues,
        minimum_recorded_calls=max(minimum_calls, len(all_calls)),
    )
    report.update(stages=list(stages.values()), totals=totals)
