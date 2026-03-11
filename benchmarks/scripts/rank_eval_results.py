#!/usr/bin/env python3
"""Extract cost/latency from promptfoo results and rank models.

Usage:
    python benchmarks/scripts/rank_eval_results.py benchmarks/results/FILE.json

Reads a promptfoo result JSON, aggregates per-provider metrics, and prints
a three-part ranking (quality × speed × cost).
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

# Add parent to path for lib imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.ranking import rank_results


def _normalize_model_id(provider_id: str) -> str:
    """Extract model ID from promptfoo provider string."""
    # e.g. "anthropic:messages:claude-opus-4-6" -> "claude-opus-4-6"
    #      "openai:gpt-5.1" -> "gpt-5.1"
    #      "google:gemini-2.5-pro" -> "gemini-2.5-pro"
    parts = provider_id.split(":")
    return parts[-1]


def extract_summaries(result_path: str) -> list[dict]:
    """Parse promptfoo results into per-provider summaries."""
    with open(result_path) as f:
        data = json.load(f)

    results = data.get("results", {})
    if isinstance(results, dict):
        results = results.get("results", [])

    by_provider: dict[str, list] = defaultdict(list)
    for r in results:
        provider = r.get("provider", {})
        label = provider.get("label", provider.get("id", "unknown"))
        by_provider[label].append(r)

    summaries = []
    for label, runs in sorted(by_provider.items()):
        scores = []
        latencies = []
        costs = []

        for r in runs:
            # Score from assertion results
            grade = r.get("gradingResult", {})
            if grade and grade.get("score") is not None:
                scores.append(grade["score"])

            # Latency
            lat = r.get("latencyMs")
            if lat:
                latencies.append(lat)

            # Cost — check top-level first, then response
            cost = r.get("cost")
            if cost is None:
                cost = r.get("response", {}).get("cost")
            if cost:
                costs.append(cost)

        mean_score = sum(scores) / len(scores) if scores else None
        mean_latency = sum(latencies) / len(latencies) if latencies else None
        mean_cost = sum(costs) / len(costs) if costs else None

        # Extract model ID for pricing lookup
        provider_info = runs[0].get("provider", {})
        model_id = _normalize_model_id(provider_info.get("id", ""))

        summaries.append({
            "model": label,
            "model_id": model_id,
            "mean_score": round(mean_score, 4) if mean_score is not None else None,
            "mean_latency_ms": round(mean_latency) if mean_latency is not None else None,
            "mean_cost_usd": round(mean_cost, 4) if mean_cost is not None else None,
            "num_runs": len(runs),
            "disqualified": mean_score is not None and mean_score < 0.5,
        })

    return summaries


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <promptfoo-result.json>")
        sys.exit(1)

    result_path = sys.argv[1]
    summaries = extract_summaries(result_path)

    if not summaries:
        print("No results found.")
        sys.exit(1)

    # Print per-model summary
    print(f"\n{'Model':<25} {'Score':>8} {'Latency':>10} {'Cost/call':>10}")
    print("-" * 55)
    for s in sorted(summaries, key=lambda x: x.get("mean_score") or 0, reverse=True):
        score = f"{s['mean_score']:.4f}" if s["mean_score"] is not None else "N/A"
        lat = f"{s['mean_latency_ms']/1000:.1f}s" if s["mean_latency_ms"] else "N/A"
        cost = f"${s['mean_cost_usd']:.4f}" if s["mean_cost_usd"] else "N/A"
        print(f"{s['model']:<25} {score:>8} {lat:>10} {cost:>10}")

    # Run ranking
    ranking = rank_results(summaries)

    print(f"\n--- Three-Part Ranking (Q={60}% S={25}% C={15}%) ---")
    if ranking.get("rankings"):
        print(f"\n{'Model':<25} {'3-Part':>8} {'Score':>8} {'Latency':>10} {'Cost':>10}")
        print("-" * 63)
        for r in ranking["rankings"]:
            lat = f"{r['mean_latency_ms']/1000:.1f}s" if r["mean_latency_ms"] else "N/A"
            cost = f"${r['mean_cost_usd']:.4f}" if r["mean_cost_usd"] else "N/A"
            print(f"{r['model']:<25} {r['three_part_score']:>8.4f} {r['mean_score']:>8.4f} {lat:>10} {cost:>10}")

    print(f"\n  Quality winner:  {ranking['quality_winner']}")
    print(f"  Balanced winner: {ranking['balanced_winner']}")
    print(f"  Value winner:    {ranking['value_winner'] or '(none — no model is 2x cheaper/1.5x faster)'}")

    if ranking.get("disqualified"):
        print(f"  Disqualified:    {', '.join(ranking['disqualified'])}")


if __name__ == "__main__":
    main()
