"""Author synthetic source/extraction artifacts. Review gold stays outside payloads."""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "corpus"
STRATA = [
    ["conformant", "format_only", "row_semantic"],
    ["mixed", "missing_source", "ambiguous_attachment"],
    ["format_only", "row_semantic", "mixed"],
    ["missing_source", "ambiguous_attachment", "conformant"],
    ["row_semantic", "mixed", "missing_source"],
    ["ambiguous_attachment", "conformant", "format_only"],
]
NAMES = [
    ("Ada Brook", "Eli Brook"),
    ("Ruth Moss", "Oren Moss"),
    ("Nora Pine", "Ira Pine"),
    ("Lina Reed", "Tomas Reed"),
    ("Enid Ford", "Hugo Ford"),
    ("Cora Lake", "Arlen Lake"),
]
HEADERS = ["Name", "Born", "Married", "Spouse", "Boy", "Girl", "Died"]


def table(headers, rows, pagebreak=False):
    return (
        "<table"
        + (' data-page-break-before="true"' if pagebreak else "")
        + "><thead><tr>"
        + "".join("<th>" + html.escape(v) + "</th>" for v in headers)
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>" + "".join("<td>" + html.escape(v) + "</td>" for v in row) + "</tr>"
            for row in rows
        )
        + "</tbody></table>"
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    gold = []
    for d, strata in enumerate(STRATA, 1):
        directory = OUT / f"doc-{d:02d}"
        directory.mkdir(exist_ok=True)
        pages = []
        chapters = []
        for j, stratum in enumerate(strata, 1):
            a, b = NAMES[d - 1]
            a = a.split()[0] + f" {j} " + a.split()[1]
            b = b.split()[0] + f" {j} " + b.split()[1]
            born = 1870 + d * 3 + j
            other = born - 2
            married = born + 23
            died = born + 74
            headers = HEADERS.copy()
            rows = [
                [a, str(born), str(married), b, "2", "1", str(died)],
                [b, str(other), str(married), a, "2", "1", str(died - 2)],
            ]
            # Genuine source layouts vary: source documents2/5 use one fused count column.
            if d in (2, 5):
                headers = ["Name", "Born", "Married", "Spouse", "Boy/Girl", "Died"]
                rows = [r[:4] + ["2 / 1"] + r[6:] for r in rows]
            elif d == 6:
                headers = [h.upper() for h in headers]
            source_table = table(headers, rows)
            note = f"A daughter, Vale {j}, was born in {born + 26}."
            aside = (
                "<aside"
                + (
                    ""
                    if stratum == "ambiguous_attachment"
                    else f' data-person="{html.escape(a)}"'
                )
                + ">"
                + note
                + "</aside>"
            )
            source_html = (
                "<!doctype html><html><body><h1>Family register "
                + str(j)
                + "</h1>"
                + source_table
                + aside
                + "</body></html>"
            )
            changed = [r.copy() for r in rows]
            outheaders = headers.copy()
            if stratum in ("row_semantic", "mixed"):
                changed[0][1] = str(born + 5)
            if stratum in ("format_only", "mixed"):
                if "Boy/Girl" in headers:
                    outheaders = HEADERS.copy()
                    changed = [r[:4] + ["2", "1"] + r[5:] for r in changed]
                else:
                    outheaders = [
                        "Name",
                        "Born",
                        "Married",
                        "Spouse",
                        "Boy/Girl",
                        "Died",
                    ]
                    changed = [r[:4] + ["2 / 1"] + r[6:] for r in changed]
            extracted_table = table(outheaders, changed)
            # One conformant chapter intentionally continues at a real page break.
            if d == 4 and stratum == "conformant":
                extracted_table = table(outheaders, changed[:1]) + table(
                    outheaders, changed[1:], True
                )
                source_html = (
                    "<!doctype html><html><body><h1>Family register "
                    + str(j)
                    + "</h1>"
                    + table(headers, rows[:1])
                    + table(headers, rows[1:], True)
                    + aside
                    + "</body></html>"
                )
            chapter_html = (
                "<!doctype html><html><body><h1>Family register "
                + str(j)
                + "</h1>"
                + extracted_table
                + f'<aside data-person="{html.escape(a)}">'
                + note
                + "</aside></body></html>"
            )
            filename = f"chapter-{j:03d}.html"
            (directory / filename).write_text(chapter_html)
            (directory / f"source-{j:03d}.html").write_text(source_html)
            if stratum != "missing_source":
                pages.append(
                    {
                        "page": j,
                        "page_number": j,
                        "printed_page_number": j,
                        "html": source_html,
                    }
                )
            chapters.append(
                {
                    "kind": "chapter",
                    "file": str((directory / filename).resolve()),
                    "title": f"Family register {j}",
                    "source_pages": [j],
                    "source_printed_pages": [str(j)],
                }
            )
            label = {
                "format_only": "format_drift",
                "row_semantic": "row_semantic_issue",
                "missing_source": "uncertain",
                "ambiguous_attachment": "uncertain",
            }.get(stratum, stratum)
            gold.append(
                {
                    "document": f"doc-{d:02d}",
                    "chapter": filename,
                    "stratum": stratum,
                    "gold": label,
                    "source_html": str(
                        (directory / f"source-{j:03d}.html").relative_to(ROOT)
                    ),
                    "extracted_html": str((directory / filename).relative_to(ROOT)),
                    "oracle_conventions": {
                        "canonical_headers": headers,
                        "layout": "Preserve source table field separation; one continuous table unless source has real page break",
                        "notes": "Only named/anchored source notes establish ownership; absent source page or unanchored note remains unknown",
                    },
                    "source_reason": {
                        "conformant": "Source cells and actual permitted table layout preserved.",
                        "format_only": "Extracted count-column separation differs from source while facts and associations remain intact.",
                        "row_semantic": "Extracted first person birth year is five years later than actual source; table layout preserved.",
                        "mixed": "Count-column separation differs and first person birth year is five years later than source.",
                        "missing_source": "Expected page absent from actual source-pages JSONL; extracted facts cannot be verified. Source file retained for reviewer only and not loaded.",
                        "ambiguous_attachment": "Source aside has no person anchor or linking marker; extraction attaches it to first person without source support.",
                    }[stratum],
                }
            )
        for name, records in [("pages.jsonl", pages), ("chapters.jsonl", chapters)]:
            (directory / name).write_text(
                "".join(json.dumps(x) + "\n" for x in records)
            )
    (OUT / "reviewer-gold.json").write_text(json.dumps(gold, indent=2) + "\n")
    print("6syntheticdocs/18chapters/3perstratum authored; no provider outputs")


if __name__ == "__main__":
    main()
