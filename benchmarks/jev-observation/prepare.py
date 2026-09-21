"""Generate fictional content in inherited real chapter DOM; no provider calls."""

import copy
import hashlib
import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from modules.validate.plan_onward_document_consistency_v1 import main as planner  # noqa: E402

OUT = ROOT / "docs/evals/artifacts/story234-anonymized-observation"
SOURCE = (
    ROOT
    / "benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/chapter-023.html"
)


def generate():
    OUT.mkdir(parents=True, exist_ok=False)
    original = BeautifulSoup(SOURCE.read_text(), "html.parser")
    soup = BeautifulSoup("<html><body></body></html>", "html.parser")
    # Inherit complete table DOM, including row density and grouping. Remove all
    # source attributes and regenerate ALL content; no name/date substitutions.
    tables = original.find_all("table")
    for table in tables:
        table = copy.deepcopy(table)
        for tag in [table, *table.find_all(True)]:
            tag.attrs = {
                k: v for k, v in tag.attrs.items() if k in {"colspan", "rowspan"}
            }
        for row_index, row in enumerate(table.find_all("tr")):
            cells = row.find_all(["th", "td"], recursive=False)
            originals = [c.get_text(" ", strip=True).upper() for c in cells]
            if originals == [
                "NAME",
                "BORN",
                "MARRIED",
                "SPOUSE",
                "BOY",
                "GIRL",
                "DIED",
            ]:
                replacements = originals
            elif len(cells) == 1:
                cells[0]["colspan"] = "7"
                row["class"] = ["genealogy-subgroup-heading"]
                replacements = ["SYNTHETIC FAMILY"]
            elif len(cells) == 7:
                replacements = [
                    f"Person {row_index}",
                    "Jan 1 1801",
                    "Jan 1 1821",
                    f"Partner {row_index}",
                    "1",
                    "1",
                    "Jan 1 1871",
                ]
            else:
                replacements = ["TOTAL DESCENDANTS"] + ["12"] * (len(cells) - 1)
            for cell, text in zip(cells, replacements):
                cell.clear()
                cell.string = text
        soup.body.append(table)
    clean = str(soup)
    cases = []
    labels = [
        "conformant",
        "format_drift",
        "format_drift",
        "format_drift",
        "row_semantic_issue",
        "uncertain",
    ]
    reasons = [
        "One coherent seven-column table; generated dates and children in matching columns.",
        "Injected duplicate full-header table split within one logical genealogy chapter; cohort convention is contiguous tables.",
        "Injected concatenated generation and two family headings in one subgroup cell.",
        "Injected BOY/GIRL fused header and corresponding slash-separated child values preserving meaning.",
        "Injected explicit child-birth note into DIED without a death assertion; full source counterpart states child birth.",
        "Injected clipped note in DIED with no event type; source excerpt intentionally absent, so death versus child birth cannot be established.",
    ]
    for index, label in enumerate(labels):
        s = BeautifulSoup(clean, "html.parser")
        table = s.find("table")
        rows = table.find_all("tr")
        data = [r for r in rows if len(r.find_all("td", recursive=False)) == 7]
        if index == 1:
            other = copy.deepcopy(table)
            for r in list(table.find_all("tr"))[len(rows) // 2 :]:
                r.decompose()
            for r in list(other.find_all("tr"))[1 : len(rows) // 2]:
                r.decompose()
            table.insert_after(other)
        if index == 2:
            heading = table.find("tr", class_="genealogy-subgroup-heading")
            heading.find(
                ["th", "td"]
            ).string = "SYNTHETIC Great Great Grandchildren SYNTHETIC Grandchildren FIRST FAMILY SECOND FAMILY"
        if index == 3:
            for row in table.find_all("tr"):
                cells = row.find_all(["th", "td"], recursive=False)
                if len(cells) == 7:
                    cells[4].string = (
                        "BOY/GIRL" if cells[4].get_text().upper() == "BOY" else "1/1"
                    )
                    cells[5].decompose()
                elif len(cells) == 1:
                    cells[0]["colspan"] = "6"
        if index == 4:
            data[0].find_all("td", recursive=False)[
                6
            ].string = "Child Person Z was born Jan 1 1851 to Person A"
        if index == 5:
            data[0].find_all("td", recursive=False)[
                6
            ].string = "Person Z Jan 1 1851; event label and row attachment missing from excerpt"
        name = f"chapter-{index + 1:03d}.html"
        html = str(s)
        (OUT / name).write_text(html)
        cases.append(
            {
                "case_id": f"case-{index + 1:02d}",
                "chapter_basename": name,
                "expected": label,
                "reason": reasons[index],
                "mutation": index != 0,
                "source_evidence": "fully fictional generated table; original personal content discarded",
                "source_excerpt_available": index != 5,
            }
        )
    chapters = [
        {
            "kind": "chapter",
            "file": str(OUT / c["chapter_basename"]),
            "title": "Fictional structural sample",
            "source_pages": [i + 1],
        }
        for i, c in enumerate(cases)
    ]
    pages = {
        i + 1: {"page_number": i + 1, "html": (OUT / c["chapter_basename"]).read_text()}
        for i, c in enumerate(cases)
        if i != 5
    }
    dossier = planner.build_document_dossier(
        chapters,
        pages,
        chapters_path=str(OUT / "chapters.jsonl"),
        pages_path=str(OUT / "pages.jsonl"),
        flag_threshold=25,
    )
    for name, obj in [
        ("gold.json", cases),
        ("dossier.json", dossier),
        (
            "lineage.json",
            {
                "source_path": str(SOURCE.relative_to(ROOT)),
                "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                "source_table_count": len(tables),
                "source_rows": sum(len(t.find_all("tr")) for t in tables),
                "scope": "One real reviewed DOM structure, six fictional variants; five explicitly injected mutations. Not production traffic or source-fidelity evaluation.",
            },
        ),
    ]:
        (OUT / name).write_text(json.dumps(obj, indent=2) + "\n")
    for name, rows in [
        ("chapters.jsonl", chapters),
        ("pages.jsonl", list(pages.values())),
    ]:
        (OUT / name).write_text("".join(json.dumps(r) + "\n" for r in rows))
    payload = {
        "model": "gpt-4.1",
        "messages": [
            {"role": "system", "content": planner.SYSTEM_PROMPT},
            {"role": "user", "content": planner._build_prompt(dossier)},
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 6000,
        "temperature": 0.0,
    }
    (OUT / "planner.request.json").write_text(json.dumps(payload, indent=2) + "\n")
    bound = (
        (len(json.dumps(payload, ensure_ascii=False).encode()) + 2048) * 2 / 1e6
        + 6000 * 8 / 1e6
        + 6 * 0.002688
    )
    assert bound <= 0.15, bound
    print(
        json.dumps(
            {
                "dir": str(OUT),
                "max_cost_usd": bound,
                "chapters": len(dossier["chapter_profiles"]),
            }
        )
    )


if __name__ == "__main__":
    generate()
