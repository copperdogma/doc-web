"""Three-part ranking policy for benchmark results.

Ported from Dossier's benchmarking_ranking.py. Selects quality, balanced,
and value winners from a set of model benchmark results.

Each input summary dict must have:
  - model: str
  - mean_score: float | None  (primary quality metric)
  - mean_latency_ms: float | None
  - mean_cost_usd: float | None
  - disqualified: bool
"""

from __future__ import annotations

from typing import Any

THREE_PART_WEIGHTS = {
    "quality": 0.60,
    "speed": 0.25,
    "cost": 0.15,
}
DEFAULT_QUALITY_FLOOR_RATIO = 0.95
VALUE_COST_ADVANTAGE_RATIO = 2.0
VALUE_SPEED_ADVANTAGE_RATIO = 1.5


def rank_results(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify models into quality/balanced/value winners.

    Returns dict with:
      quality_winner: str | None — highest score
      balanced_winner: str | None — best three-part score
      value_winner: str | None — best score among significantly cheaper/faster models
      default_candidates: list[str] — non-dominated models in quality window
      disqualified: list[str] — below floor or failed
      rankings: list[dict] — full ranked list with three_part_score
    """
    if not summaries:
        return _empty()

    quality_pool = [s for s in summaries if s.get("mean_score") is not None]
    if not quality_pool:
        return {**_empty(), "disqualified": [s["model"] for s in summaries]}

    quality_winner = max(quality_pool, key=lambda s: s["mean_score"])
    default_pool = [
        s for s in summaries
        if not s.get("disqualified") and s.get("mean_score") is not None
    ]
    disqualified = [s for s in summaries if s.get("disqualified")]

    for s in summaries:
        s["three_part_score"] = None

    if not default_pool:
        return {
            **_empty(),
            "quality_winner": quality_winner["model"],
            "disqualified": [s["model"] for s in disqualified],
        }

    baseline = max(default_pool, key=lambda s: s["mean_score"])
    floor = baseline["mean_score"] * DEFAULT_QUALITY_FLOOR_RATIO
    quality_window = [s for s in default_pool if s["mean_score"] >= floor]

    # Pareto filter: remove dominated candidates
    default_candidates = []
    for candidate in quality_window:
        if any(
            _dominates(other, candidate)
            for other in quality_window
            if other is not candidate
        ):
            continue
        default_candidates.append(candidate)

    if baseline not in default_candidates:
        default_candidates.append(baseline)

    # Compute three-part scores
    valid_latency = [
        s["mean_latency_ms"] for s in default_candidates
        if s.get("mean_latency_ms") and s["mean_latency_ms"] > 0
    ]
    valid_cost = [
        s["mean_cost_usd"] for s in default_candidates
        if s.get("mean_cost_usd") and s["mean_cost_usd"] > 0
    ]
    fastest = min(valid_latency) if valid_latency else None
    cheapest = min(valid_cost) if valid_cost else None

    for s in default_candidates:
        s["three_part_score"] = _three_part_score(s, fastest, cheapest)

    balanced_winner = max(
        default_candidates, key=lambda s: s["three_part_score"]
    )

    # Value winner: significantly cheaper or faster, within quality window
    value_candidates = []
    baseline_cost = baseline.get("mean_cost_usd")
    baseline_latency = baseline.get("mean_latency_ms")
    for s in default_candidates:
        if s is baseline:
            continue
        cost_adv = _advantage_ratio(baseline_cost, s.get("mean_cost_usd"))
        speed_adv = _advantage_ratio(baseline_latency, s.get("mean_latency_ms"))
        if (
            (cost_adv is not None and cost_adv >= VALUE_COST_ADVANTAGE_RATIO)
            or (speed_adv is not None and speed_adv >= VALUE_SPEED_ADVANTAGE_RATIO)
        ):
            value_candidates.append(s)

    value_winner = (
        max(value_candidates, key=lambda s: s["three_part_score"])
        if value_candidates
        else None
    )

    default_candidates.sort(key=lambda s: s["three_part_score"], reverse=True)

    return {
        "quality_winner": quality_winner["model"],
        "balanced_winner": balanced_winner["model"],
        "value_winner": value_winner["model"] if value_winner else None,
        "default_candidates": [s["model"] for s in default_candidates],
        "disqualified": [s["model"] for s in disqualified],
        "rankings": [
            {
                "model": s["model"],
                "mean_score": s["mean_score"],
                "mean_latency_ms": s.get("mean_latency_ms"),
                "mean_cost_usd": s.get("mean_cost_usd"),
                "three_part_score": s["three_part_score"],
            }
            for s in default_candidates
        ],
    }


def _empty() -> dict[str, Any]:
    return {
        "quality_winner": None,
        "balanced_winner": None,
        "value_winner": None,
        "default_candidates": [],
        "disqualified": [],
        "rankings": [],
    }


def _dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    a_t = a.get("mean_latency_ms")
    b_t = b.get("mean_latency_ms")
    a_c = a.get("mean_cost_usd")
    b_c = b.get("mean_cost_usd")
    if not all(v and v > 0 for v in [a_t, b_t, a_c, b_c]):
        return False
    no_worse = a["mean_score"] >= b["mean_score"] and a_t <= b_t and a_c <= b_c
    strictly_better = a["mean_score"] > b["mean_score"] or a_t < b_t or a_c < b_c
    return no_worse and strictly_better


def _three_part_score(
    item: dict[str, Any],
    fastest: float | None,
    cheapest: float | None,
) -> float:
    quality = item.get("mean_score") or 0.0
    latency = item.get("mean_latency_ms")
    speed = (
        (fastest / latency)
        if fastest is not None and latency is not None and latency > 0
        else 0.0
    )
    cost = item.get("mean_cost_usd")
    cost_ratio = (
        (cheapest / cost)
        if cheapest is not None and cost is not None and cost > 0
        else 0.0
    )
    return round(
        THREE_PART_WEIGHTS["quality"] * quality
        + THREE_PART_WEIGHTS["speed"] * speed
        + THREE_PART_WEIGHTS["cost"] * cost_ratio,
        4,
    )


def _advantage_ratio(
    baseline_value: float | None,
    candidate_value: float | None,
) -> float | None:
    if not baseline_value or not candidate_value or baseline_value <= 0 or candidate_value <= 0:
        return None
    return baseline_value / candidate_value
