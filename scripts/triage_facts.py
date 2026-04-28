#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.fromisoformat(
    os.environ.get("TRIAGE_FACTS_TODAY", date.today().isoformat())
)

LANE_SKILLS = [
    "triage-stories",
    "triage-inbox",
    "triage-evals",
    "triage-architecture",
    "triage-health",
    "codebase-improvement-scout",
    "discover-models",
    "loop-verify",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize cheap doc-web triage facts."
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON"
    )
    args = parser.parse_args()

    facts = collect_facts()
    if args.json:
        print(json.dumps(facts, indent=2, sort_keys=True))
    else:
        print_text(facts)
    return 0


def collect_facts() -> dict[str, Any]:
    graph = read_json("docs/methodology/graph.json", {})
    state = read_json("docs/methodology/state.yaml", {})
    coverage = read_json("tests/fixtures/formats/_coverage-matrix.json", {})
    return {
        "generated_for_date": TODAY.isoformat(),
        "repo": "doc-web",
        "git": git_facts(),
        "lanes": lane_presence(),
        "methodology_tooling": methodology_tooling_facts(),
        "graph": graph_facts(graph),
        "state": state_facts(state, graph),
        "coverage": coverage_facts(coverage),
        "inbox": inbox_facts(),
        "architecture": architecture_facts(state),
        "ui_scout": {"status": "absent"},
        "codebase_improvement": codebase_improvement_facts(),
        "recent_churn": recent_churn_facts(),
    }


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_json(relative_path: str, fallback: Any) -> Any:
    text = read_text(relative_path)
    if not text:
        return fallback
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return fallback


def git(args: list[str], *, strip: bool = True) -> str:
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            encoding="utf-8",
            env=env,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if completed.returncode != 0:
        return ""
    output = completed.stdout
    return output.strip() if strip else re.sub(r"(?:\r?\n)+$", "", output)


def git_facts() -> dict[str, Any]:
    status = git(["status", "--short"], strip=False)
    return {
        "branch": git(["branch", "--show-current"]) or None,
        "head": git(["rev-parse", "--short", "HEAD"]) or None,
        "upstream": git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
        or None,
        "dirty": bool(status),
        "status_short": [line for line in status.splitlines() if line][:30],
    }


def lane_presence() -> dict[str, str]:
    return {
        name: "present"
        if (ROOT / ".agents" / "skills" / name / "SKILL.md").exists()
        else "absent"
        for name in LANE_SKILLS
    }


def methodology_tooling_facts() -> dict[str, Any]:
    skill_root = ROOT / ".agents" / "skills"
    wrapper_root = ROOT / ".gemini" / "commands"
    invocable = []
    if skill_root.exists():
        for skill_file in sorted(skill_root.glob("*/SKILL.md")):
            skill_text = read_text(str(skill_file.relative_to(ROOT)))
            if re.search(r"^user-invocable:\s*true\s*$", skill_text, re.M):
                invocable.append(skill_file.parent.name)
    wrappers = (
        sorted(path.stem for path in wrapper_root.glob("*.toml"))
        if wrapper_root.exists()
        else []
    )
    return {
        "invocable_skill_count": len(invocable),
        "gemini_wrapper_count": len(wrappers),
        "missing_gemini_wrappers": sorted(set(invocable) - set(wrappers)),
        "extra_gemini_wrappers": sorted(set(wrappers) - set(invocable)),
    }


def graph_facts(graph: dict[str, Any]) -> dict[str, Any]:
    stories = graph.get("stories") or []
    evals = graph.get("evals") or []
    compromises = (graph.get("spec") or {}).get("compromises") or []
    return {
        "stories": {
            "total": len(stories),
            "by_status": count_by(
                stories, lambda item: item.get("status") or "Unknown"
            ),
            "recommended_now": [
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "status": item.get("status"),
                    "posture": (item.get("actionability") or {}).get("posture"),
                    "why_now": (item.get("actionability") or {}).get("whyNow") or "",
                }
                for item in stories
                if (item.get("actionability") or {}).get("recommendedNow")
            ],
            "blocked": [
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "path": item.get("path"),
                }
                for item in stories
                if item.get("status") == "Blocked"
            ],
            "in_progress": [
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "path": item.get("path"),
                }
                for item in stories
                if item.get("status") == "In Progress"
            ],
        },
        "evals": {
            "total": len(evals),
            "by_type": count_by(evals, lambda item: item.get("type") or "unknown"),
            "recommended_now": [
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "posture": (item.get("actionability") or {}).get("posture"),
                    "why_now": (item.get("actionability") or {}).get("whyNow") or "",
                    "retry_trigger_status": (item.get("actionability") or {}).get(
                        "retryTriggerStatus"
                    ),
                }
                for item in evals
                if (item.get("actionability") or {}).get("recommendedNow")
            ],
            "retry_ready": [
                {
                    "id": item.get("id"),
                    "ready_triggers": [
                        retry.get("condition")
                        for retry in item.get("retryState") or []
                        if retry.get("status") == "ready"
                    ],
                }
                for item in evals
                if any(
                    retry.get("status") == "ready"
                    for retry in item.get("retryState") or []
                )
            ],
            "stale_scores": [
                {
                    "id": item.get("id"),
                    "measured": (item.get("latestScore") or {}).get("measured"),
                    "days_since": days_since(
                        (item.get("latestScore") or {}).get("measured")
                    ),
                }
                for item in evals
                if not (item.get("latestScore") or {}).get("measured")
                or days_since((item.get("latestScore") or {}).get("measured")) > 30
            ][:20],
        },
        "compromises": {
            "total": len(compromises),
            "by_phase": count_by(
                compromises,
                lambda item: (item.get("state") or {}).get("phase") or "unknown",
            ),
            "recommended_now": [
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "phase": (item.get("state") or {}).get("phase"),
                    "posture": (item.get("actionability") or {}).get("posture"),
                    "why_now": (item.get("actionability") or {}).get("whyNow") or "",
                }
                for item in compromises
                if (item.get("actionability") or {}).get("recommendedNow")
            ],
        },
    }


def state_facts(state: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    categories = state.get("categories") or {}
    compromises = state.get("compromises") or {}
    return {
        "categories_by_substrate": count_by(
            categories.values(), lambda item: item.get("substrate") or "unknown"
        ),
        "compromises_by_phase": count_by(
            compromises.values(), lambda item: item.get("phase") or "unknown"
        ),
        "graph_validation": graph.get("validation"),
    }


def coverage_facts(coverage: dict[str, Any]) -> dict[str, Any]:
    formats = coverage.get("formats") or []
    attention_rows = []
    for row in formats:
        status = row.get("status") or "unknown"
        if status != "passing" or row.get("known_gaps"):
            attention_rows.append(
                {
                    "id": row.get("id"),
                    "status": status,
                    "known_gap_count": len(row.get("known_gaps") or []),
                    "measured": (row.get("scores") or {}).get("measured")
                    if isinstance(row.get("scores"), dict)
                    else None,
                }
            )
    return {
        "path": "tests/fixtures/formats/_coverage-matrix.json",
        "generated": coverage.get("generated"),
        "total_formats": len(formats),
        "by_status": count_by(formats, lambda item: item.get("status") or "unknown"),
        "attention_count": len(attention_rows),
        "attention_rows": attention_rows[:20],
    }


def inbox_facts() -> dict[str, Any]:
    text = read_text("docs/inbox.md")
    untriaged = markdown_section(text, "## Untriaged")
    deferred = markdown_section(text, "## Deferred")
    return {
        "untriaged_count": sum(
            1 for line in untriaged.splitlines() if line.startswith("- ")
        ),
        "deferred_count": sum(
            1 for line in deferred.splitlines() if re.match(r"^- \[[ x]\]", line)
        ),
        "untriaged_preview": [
            line.removeprefix("- ").strip()
            for line in untriaged.splitlines()
            if line.startswith("- ")
        ][:5],
    }


def architecture_facts(state: dict[str, Any]) -> dict[str, Any]:
    audits = state.get("architecture_audits") or {}
    target_interval = ((audits.get("cadence") or {}).get("target_story_interval")) or 6
    domains = audits.get("domains") or {}
    due_domains = []
    for domain_id, domain in sorted(domains.items()):
        stories_since = domain.get("stories_since_audit") or 0
        open_findings = domain.get("open_findings") or []
        due = bool(open_findings) or stories_since >= target_interval
        if due:
            due_domains.append(
                {
                    "id": domain_id,
                    "label": domain.get("label") or domain_id,
                    "stories_since_audit": stories_since,
                    "open_findings": len(open_findings),
                    "last_audited_at": domain.get("last_audited_at"),
                }
            )
    return {
        "status": "present" if domains else "absent",
        "target_story_interval": target_interval,
        "domain_count": len(domains),
        "due_domains": due_domains,
    }


def codebase_improvement_facts() -> dict[str, Any]:
    report_root = ROOT / "docs" / "reports" / "codebase-improvement"
    reports = (
        sorted(path.name for path in report_root.glob("*.md"))
        if report_root.exists()
        else []
    )
    latest_report = reports[-1] if reports else None
    report_path = (
        f"docs/reports/codebase-improvement/{latest_report}" if latest_report else None
    )
    return {
        "status": "present" if latest_report else "no-report",
        "latest_report": report_path,
        "latest_report_days_since": (
            days_since_report_name(latest_report) if latest_report else None
        ),
        "state_file": None,
    }


def recent_churn_facts() -> dict[str, Any]:
    since = (TODAY - timedelta(days=30)).isoformat()
    output = git(
        [
            "log",
            f"--since={since}T00:00:00Z",
            "--max-count=200",
            "--name-only",
            "--format=",
        ]
    )
    counts: Counter[str] = Counter(
        line.strip()
        for line in output.splitlines()
        if line.strip() and not line.startswith(".git/")
    )
    return {
        "since": since,
        "top_paths": [
            {"path": path, "count": count}
            for path, count in sorted(
                counts.items(), key=lambda item: (-item[1], item[0])
            )[:25]
        ],
    }


def markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    try:
        start = next(
            index for index, line in enumerate(lines) if line.strip() == heading
        )
    except StopIteration:
        return ""
    end = next(
        (
            index
            for index, line in enumerate(lines[start + 1 :], start + 1)
            if line.startswith("## ")
        ),
        len(lines),
    )
    return "\n".join(lines[start + 1 : end])


def count_by(items: Any, fn: Any) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        counts[str(fn(item))] += 1
    return dict(counts)


def days_since(value: Any) -> int | None:
    if not value or not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value[:10])
    except ValueError:
        return 9999
    return (TODAY - parsed).days


def days_since_report_name(filename: str) -> int | None:
    match = re.match(r"^(\d{4})(\d{2})(\d{2})", filename) or re.match(
        r"^(\d{4})-(\d{2})-(\d{2})", filename
    )
    if not match:
        return None
    return days_since(f"{match.group(1)}-{match.group(2)}-{match.group(3)}")


def print_text(facts: dict[str, Any]) -> None:
    print("Triage Facts")
    print(
        f"- branch: {facts['git']['branch'] or 'unknown'} @ {facts['git']['head'] or 'unknown'}"
    )
    print(f"- dirty: {'yes' if facts['git']['dirty'] else 'no'}")
    print(
        f"- stories: {json.dumps(facts['graph']['stories']['by_status'], sort_keys=True)}"
    )
    print(f"- recommended stories: {len(facts['graph']['stories']['recommended_now'])}")
    print(f"- recommended evals: {len(facts['graph']['evals']['recommended_now'])}")
    phase_counts = json.dumps(facts["graph"]["compromises"]["by_phase"], sort_keys=True)
    print(f"- compromises by phase: {phase_counts}")
    print(f"- coverage: {json.dumps(facts['coverage']['by_status'], sort_keys=True)}")
    print(f"- coverage attention rows: {facts['coverage']['attention_count']}")
    print(f"- inbox untriaged: {facts['inbox']['untriaged_count']}")
    print(f"- architecture due domains: {len(facts['architecture']['due_domains'])}")
    print("- ui scout due: absent")
    print(f"- codebase improvement: {facts['codebase_improvement']['status']}")
    wrapper_drift = len(facts["methodology_tooling"]["missing_gemini_wrappers"]) + len(
        facts["methodology_tooling"]["extra_gemini_wrappers"]
    )
    print(f"- wrapper drift: {wrapper_drift}")


if __name__ == "__main__":
    raise SystemExit(main())
