"""Cold and future pricing must include thought tokens and expose cache benefit."""

from benchmarks.scripts.argon_levels_summary import charges


def test_cold_normalization_and_december_include_thinking():
    result = charges(
        {
            "promptTokenCount": 1000,
            "candidatesTokenCount": 100,
            "thoughtsTokenCount": 200,
            "cachedContentTokenCount": 500,
        }
    )
    assert result["actual_usd"] == 0.00405
    assert result["cold_usd"] == 0.005
    assert result["december_actual_same_usage_usd"] == 0.0081
    assert result["december_cold_same_usage_usd"] == 0.01
