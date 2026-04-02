import json


def _load_output(output: str) -> dict:
    text = (output or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        pass
    first_line = text.splitlines()[0]
    try:
        return json.loads(first_line)
    except Exception:
        return {}


def score_case(expected: dict, actual: dict) -> dict:
    expected_recipe = expected.get("expected_recipe")
    launch_expected = expected_recipe != "no-recipe-needed"
    checks = {
        "recommended_recipe": actual.get("recommended_recipe") == expected_recipe,
        "handoff_artifact": bool(actual.get("handoff_artifact")),
    }
    if launch_expected:
        checks.update(
            {
                "terminal_outcome": actual.get("terminal_outcome") == "launched",
                "downstream_run_id": bool(actual.get("downstream_run_id")),
                "first_downstream_artifact": bool(actual.get("first_downstream_artifact")),
            }
        )
    else:
        checks.update(
            {
                "terminal_outcome": actual.get("terminal_outcome") == "skipped",
                "terminal_reason": actual.get("terminal_reason") == "no_recipe_needed",
                "no_first_downstream_artifact": not actual.get("first_downstream_artifact"),
            }
        )

    passed_checks = sum(1 for value in checks.values() if value)
    total_checks = len(checks) or 1
    return {
        "pass": passed_checks == total_checks,
        "score": passed_checks / total_checks,
        "checks": checks,
        "expected": {
            "recommended_recipe": expected_recipe,
            "terminal_outcome": "launched" if launch_expected else "skipped",
            "terminal_reason": None if launch_expected else "no_recipe_needed",
        },
        "actual": {
            "recommended_recipe": actual.get("recommended_recipe"),
            "terminal_outcome": actual.get("terminal_outcome"),
            "terminal_reason": actual.get("terminal_reason"),
            "handoff_artifact": actual.get("handoff_artifact"),
            "first_downstream_artifact": actual.get("first_downstream_artifact"),
        },
    }


def summarize_results(rows: list[dict]) -> dict:
    docs = len(rows)
    completed = sum(1 for row in rows if row.get("status") == "ok")
    failed_runs = docs - completed
    passed = sum(1 for row in rows if row.get("score", {}).get("pass"))
    overall = 0.0
    if docs:
        overall = sum(row.get("score", {}).get("score", 0.0) for row in rows) / docs
    return {
        "docs": docs,
        "completed": completed,
        "failed_runs": failed_runs,
        "launched": sum(1 for row in rows if row.get("terminal_outcome") == "launched"),
        "skipped": sum(1 for row in rows if row.get("terminal_outcome") == "skipped"),
        "pass_rate": passed / docs if docs else 0.0,
        "accuracy": passed / docs if docs else 0.0,
        "overall": overall,
    }


def get_assert(output: str, context: dict) -> dict:
    actual = _load_output(output)
    expected = {
        "expected_recipe": context["vars"]["expected_recipe"],
    }
    result = score_case(expected, actual)
    return {
        "pass": result["pass"],
        "score": result["score"],
        "reason": json.dumps(result["checks"], sort_keys=True),
    }
