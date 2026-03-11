"""Tests for benchmarks/lib/ranking.py — three-part model ranking."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "benchmarks"))

from lib.ranking import rank_results


def _make_summary(model, score, latency_ms=None, cost_usd=None, disqualified=False):
    return {
        "model": model,
        "mean_score": score,
        "mean_latency_ms": latency_ms,
        "mean_cost_usd": cost_usd,
        "disqualified": disqualified,
    }


def test_quality_winner_is_highest_score():
    summaries = [
        _make_summary("A", 0.95, 120000, 0.30),
        _make_summary("B", 0.94, 110000, 0.18),
    ]
    result = rank_results(summaries)
    assert result["quality_winner"] == "A"


def test_balanced_winner_considers_cost_and_speed():
    summaries = [
        _make_summary("Expensive", 0.952, 123000, 0.31),
        _make_summary("Cheap", 0.946, 110000, 0.18),
    ]
    result = rank_results(summaries)
    assert result["quality_winner"] == "Expensive"
    assert result["balanced_winner"] == "Cheap"


def test_value_winner_requires_2x_cost_advantage():
    summaries = [
        _make_summary("Baseline", 0.95, 120000, 0.30),
        _make_summary("Cheap", 0.92, 100000, 0.10),  # 3x cheaper, within 5%
    ]
    result = rank_results(summaries)
    assert result["value_winner"] == "Cheap"


def test_no_value_winner_when_not_cheap_enough():
    summaries = [
        _make_summary("A", 0.95, 120000, 0.30),
        _make_summary("B", 0.94, 110000, 0.20),  # only 1.5x cheaper
    ]
    result = rank_results(summaries)
    assert result["value_winner"] is None


def test_disqualified_models_excluded():
    summaries = [
        _make_summary("Good", 0.95, 120000, 0.30),
        _make_summary("Bad", 0.40, 50000, 0.05, disqualified=True),
    ]
    result = rank_results(summaries)
    assert "Bad" in result["disqualified"]
    assert "Bad" not in result["default_candidates"]


def test_empty_input():
    result = rank_results([])
    assert result["quality_winner"] is None
    assert result["balanced_winner"] is None


def test_rankings_include_three_part_scores():
    summaries = [
        _make_summary("A", 0.95, 120000, 0.30),
        _make_summary("B", 0.94, 110000, 0.18),
    ]
    result = rank_results(summaries)
    assert len(result["rankings"]) == 2
    for r in result["rankings"]:
        assert "three_part_score" in r
        assert r["three_part_score"] > 0


def test_real_onward_data():
    """Reproduce actual story-131 ranking."""
    summaries = [
        _make_summary("Claude Opus 4.6", 0.952, 123200, 0.3125),
        _make_summary("Claude Sonnet 4.6", 0.946, 110100, 0.1841),
        _make_summary("GPT-5.1", 0.847, 91200, 0.1155),
        _make_summary("GPT-4o", 0.855, 688500, 0.1104),
        _make_summary("Gemini 2.5 Pro", 0.577, 97000, 0.1480),
    ]
    result = rank_results(summaries)
    assert result["quality_winner"] == "Claude Opus 4.6"
    assert result["balanced_winner"] == "Claude Sonnet 4.6"
