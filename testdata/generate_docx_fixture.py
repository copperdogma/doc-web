#!/usr/bin/env python3
"""Generate repo-owned DOCX fixtures from checked-in source data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from docx import Document
from docx.enum.text import WD_BREAK


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "docx-mini.source.json"
DEFAULT_OUTPUT = ROOT / "docx-mini.docx"


def _add_table(document: Document, table_payload: dict[str, Any]) -> None:
    headers = table_payload["headers"]
    rows = table_payload["rows"]
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for idx, header in enumerate(headers):
        table.cell(0, idx).text = header
    for row in rows:
        cells = table.add_row().cells
        for idx, value in enumerate(row):
            cells[idx].text = value


def _paragraph_specs(paragraphs: Iterable[Any]) -> Iterable[dict[str, Any]]:
    for paragraph in paragraphs:
        if isinstance(paragraph, str):
            yield {"text": paragraph}
            continue
        yield paragraph


def build_fixture(source_path: Path, output_path: Path) -> None:
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    document = Document()
    document.add_heading(payload["title"], level=0)

    for section in payload["sections"]:
        document.add_heading(section["heading"], level=1)
        for paragraph in _paragraph_specs(section.get("paragraphs", [])):
            doc_paragraph = document.add_paragraph(paragraph["text"])
            if paragraph.get("page_break_after"):
                doc_paragraph.add_run().add_break(WD_BREAK.PAGE)
        for bullet in section.get("bullets", []):
            document.add_paragraph(bullet, style="List Bullet")
        for numbered in section.get("numbered", []):
            document.add_paragraph(numbered, style="List Number")
        table_payloads = []
        if section.get("table"):
            table_payloads.append(section["table"])
        table_payloads.extend(section.get("tables", []))
        for table_payload in table_payloads:
            _add_table(document, table_payload)
        if section.get("page_break_after"):
            document.add_page_break()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Checked-in source JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output DOCX path")
    args = parser.parse_args()

    build_fixture(args.source, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
