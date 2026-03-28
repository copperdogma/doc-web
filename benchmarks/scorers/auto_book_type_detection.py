import json
from pathlib import Path


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
    expected_signals = list(expected.get("expected_major_signals", []))
    actual_signals = set(actual.get("signals", []))
    checks = {
        "book_type": actual.get("book_type") == expected.get("expected_book_type"),
        "recommended_recipe": actual.get("recommended_recipe") == expected.get("expected_recipe"),
    }
    if expected_signals:
        checks["major_signals"] = set(expected_signals).issubset(actual_signals)

    passed_checks = sum(1 for value in checks.values() if value)
    total_checks = len(checks) or 1
    return {
        "pass": passed_checks == total_checks,
        "score": passed_checks / total_checks,
        "checks": checks,
        "expected": {
            "book_type": expected.get("expected_book_type"),
            "recommended_recipe": expected.get("expected_recipe"),
            "major_signals": expected_signals,
        },
        "actual": {
            "book_type": actual.get("book_type"),
            "recommended_recipe": actual.get("recommended_recipe"),
            "signals": actual.get("signals", []),
        },
    }


def summarize_results(rows: list[dict]) -> dict:
    completed = [row for row in rows if row.get("status") == "ok"]
    accuracy = 0.0
    overall = 0.0
    if completed:
        accuracy = sum(1 for row in completed if row.get("score", {}).get("pass")) / len(completed)
        overall = sum(row.get("score", {}).get("score", 0.0) for row in completed) / len(completed)
    return {
        "docs": len(rows),
        "completed": len(completed),
        "failed_runs": len(rows) - len(completed),
        "accuracy": accuracy,
        "overall": overall,
        "pass_rate": accuracy,
    }


def get_assert(output: str, context: dict) -> dict:
    actual = _load_output(output)
    expected = {
        "expected_book_type": context["vars"]["expected_book_type"],
        "expected_recipe": context["vars"]["expected_recipe"],
        "expected_major_signals": context["vars"].get("expected_major_signals", []),
    }
    result = score_case(expected, actual)
    return {
        "pass": result["pass"],
        "score": result["score"],
        "reason": json.dumps(result["checks"], sort_keys=True),
    }
