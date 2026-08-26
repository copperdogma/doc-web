#!/usr/bin/env python3
"""Regrade an existing PromptFoo crop result against authoritative goldens."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROVENANCE = ROOT / "benchmarks/golden/crop-eval-provenance.json"
SELECTION_ELIGIBLE_STATUS = "eligible_authoritative_golden"


def _validated_partition(surface: dict[str, Any], field: str) -> list[str]:
    keys = surface.get(field)
    if not isinstance(keys, list) or any(not isinstance(key, str) or not key for key in keys):
        raise ValueError(f"{field} must be a list of non-empty crop keys")

    duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)
    if duplicates:
        raise ValueError(f"Duplicate {field}: {duplicates}")
    return keys


def _result_rows_by_key(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    try:
        rows = payload["results"]["results"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Result payload must contain results.results rows") from exc
    if not isinstance(rows, list):
        raise ValueError("Result payload results.results must be a list")

    by_key: dict[str, dict[str, Any]] = {}
    duplicates: set[str] = set()
    for index, row in enumerate(rows):
        try:
            key = row["vars"]["crop_key"]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Result row {index} is missing vars.crop_key") from exc
        if not isinstance(key, str) or not key:
            raise ValueError(f"Result row {index} has an invalid vars.crop_key")
        if not isinstance(row.get("success"), bool):
            raise ValueError(f"Result row {index} ({key}) must have a boolean success value")
        if key in by_key:
            duplicates.add(key)
        else:
            by_key[key] = row

    if duplicates:
        raise ValueError(f"Duplicate result crop_key rows: {sorted(duplicates)}")
    return by_key


def regrade(payload: dict[str, Any], surface: dict[str, Any]) -> dict[str, Any]:
    by_key = _result_rows_by_key(payload)

    def summarize(keys: list[str]) -> dict[str, Any]:
        selected = [by_key[key] for key in keys]
        passed = sum(bool(row["success"]) for row in selected)
        return {
            "cases": len(selected),
            "passed": passed,
            "failed": len(selected) - passed,
            "pass_rate": round(passed / len(selected), 6) if selected else None,
            "failures": [row["vars"]["crop_key"] for row in selected if not row["success"]],
        }

    authoritative = _validated_partition(surface, "authoritative_golden_keys")
    expected = set(authoritative)
    actual = set(by_key)
    if expected != actual:
        raise ValueError(
            f"Result/provenance key mismatch: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )

    authoritative_summary = summarize(authoritative)
    model_selection_status = surface.get("model_selection_status")
    selection_claim_allowed = model_selection_status == SELECTION_ELIGIBLE_STATUS and authoritative_summary["cases"] > 0
    promotion_claim_allowed = selection_claim_allowed and authoritative_summary["failed"] == 0

    return {
        "contract_role": surface["contract_role"],
        "model_selection_status": model_selection_status,
        "all_cases": summarize(sorted(actual)),
        "authoritative_goldens": authoritative_summary,
        "selection_claim_allowed": selection_claim_allowed,
        "promotion_claim_allowed": promotion_claim_allowed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--surface", required=True)
    parser.add_argument("--provenance", type=Path, default=DEFAULT_PROVENANCE)
    args = parser.parse_args()

    provenance = json.loads(args.provenance.read_text(encoding="utf-8"))
    payload = json.loads(args.result.read_text(encoding="utf-8"))
    print(json.dumps(regrade(payload, provenance["surfaces"][args.surface]), indent=2))


if __name__ == "__main__":
    main()
