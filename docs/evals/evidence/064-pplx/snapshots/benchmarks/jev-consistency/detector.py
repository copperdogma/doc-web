"""Lossless synthetic table HTML adapter for the maintained chapter detector."""

import dataclasses
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from modules.validate.validate_onward_genealogy_consistency_v1.main import (  # noqa: E402
    analyze_chapter_row,
)

OUT = ROOT / "docs/evals/artifacts/jev-consistency-20260921"


def render(state):
    parts = ["<!doctype html><html><body>"]
    for t in state.get("tables", []):
        parts.append(
            "<table><thead><tr>"
            + "".join("<th>" + html.escape(v) + "</th>" for v in t["headers"])
            + "</tr></thead><tbody>"
        )
        for row in t["rows"]:
            parts.append(
                "<tr>"
                + "".join("<td>" + html.escape(v) + "</td>" for v in row)
                + "</tr>"
            )
        parts.append("</tbody></table>")
    return "".join(parts) + "</body></html>"


def main():
    cases = json.loads((Path(__file__).parent / "fixtures.json").read_text())
    results = []
    for c in cases:
        if "tables" not in c["input"]:
            results.append(
                {
                    "id": c["id"],
                    "gold": c["gold"],
                    "status": "out_of_domain",
                    "reason": "maintenance cards have no genealogy table",
                }
            )
            continue
        path = OUT / (c["id"] + ".html")
        path.write_text(render(c["input"]))
        result = analyze_chapter_row(
            {"kind": "chapter", "file": str(path), "source_pages": [1]},
            flag_threshold=25,
        )
        results.append(
            {
                "id": c["id"],
                "gold": c["gold"],
                "status": "measured" if result else "out_of_domain",
                "result": dataclasses.asdict(result) if result else None,
            }
        )
    (OUT / "maintained-detector.json").write_text(json.dumps(results, indent=2) + "\n")
    print(
        {
            "measured": sum(x["status"] == "measured" for x in results),
            "out_of_domain": sum(x["status"] == "out_of_domain" for x in results),
        }
    )


if __name__ == "__main__":
    main()
