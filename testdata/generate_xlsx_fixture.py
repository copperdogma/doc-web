#!/usr/bin/env python3
"""Generate the repo-owned XLSX fixture from checked-in source data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "xlsx-mini.source.json"
DEFAULT_OUTPUT = ROOT / "xlsx-mini.xlsx"


def build_fixture(source_path: Path, output_path: Path) -> None:
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    workbook = Workbook()
    workbook.remove(workbook.active)

    for sheet in payload["sheets"]:
        worksheet = workbook.create_sheet(title=sheet["name"])
        for row in sheet["rows"]:
            worksheet.append(row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Checked-in source JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output XLSX path")
    args = parser.parse_args()

    build_fixture(args.source, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
