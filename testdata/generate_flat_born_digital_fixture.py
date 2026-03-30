#!/usr/bin/env python3
"""Generate the repo-owned flat born-digital PDF fixture from checked-in source text."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "flat-born-digital-mini.md"
DEFAULT_OUTPUT = ROOT / "flat-born-digital-mini.pdf"

sys.path.insert(0, str((ROOT / "vendor").resolve()))
from fpdf import FPDF  # noqa: E402


def _paragraphs(text: str) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                paragraphs.append(" ".join(current).strip())
                current.clear()
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current).strip())
    return paragraphs


def build_fixture(source_path: Path, output_path: Path) -> int:
    paragraphs = _paragraphs(source_path.read_text(encoding="utf-8"))
    pdf = FPDF(format="letter")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_title("Flat Born-Digital Mini")
    pdf.set_author("doc-forge")
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    for paragraph in paragraphs:
        pdf.multi_cell(0, 6, text=paragraph)
        pdf.ln(3)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return pdf.page_no()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Checked-in source text")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output PDF path")
    args = parser.parse_args()

    page_count = build_fixture(args.source, args.output)
    print(f"Wrote {args.output} ({page_count} pages)")


if __name__ == "__main__":
    main()
