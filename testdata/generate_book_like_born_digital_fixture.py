#!/usr/bin/env python3
"""Generate a repo-owned book-like born-digital PDF fixture from checked-in markdown."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "born-digital-handbook-mini.md"
DEFAULT_OUTPUT = ROOT / "born-digital-handbook-mini.pdf"

sys.path.insert(0, str((ROOT / "vendor").resolve()))
from fpdf import FPDF, XPos, YPos  # noqa: E402


TITLE_RE = re.compile(r"^# (.+)$")
SECTION_RE = re.compile(r"^## (.+)$")
NUMBERED_RE = re.compile(r"^\d+[.)]\s+")
PAGE_BREAK_RE = re.compile(r"^<<<PAGEBREAK>>>$")


def split_title_and_body(text: str) -> tuple[str, list[str]]:
    title = DEFAULT_SOURCE.stem.replace("-", " ").title()
    body: list[str] = []
    for raw_line in text.splitlines():
        match = TITLE_RE.match(raw_line.strip())
        if match and not body:
            title = match.group(1).strip()
            continue
        body.append(raw_line.rstrip())
    return title, body


def render_lines(pdf: FPDF, lines: list[str]) -> None:
    pdf.set_font("Helvetica", size=11)
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            pdf.ln(3)
            continue

        if PAGE_BREAK_RE.match(line):
            pdf.add_page()
            pdf.set_font("Helvetica", size=11)
            continue

        section_match = SECTION_RE.match(line)
        if section_match:
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.multi_cell(
                0,
                8,
                text=section_match.group(1).strip(),
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            pdf.ln(1)
            pdf.set_font("Helvetica", size=11)
            continue

        if line.startswith("- "):
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 6, text=line[2:].strip(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            continue

        if NUMBERED_RE.match(line):
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 6, text=line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            continue

        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, text=line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_fixture(source_path: Path, output_path: Path) -> int:
    title, body = split_title_and_body(source_path.read_text(encoding="utf-8"))

    pdf = FPDF(format="letter")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_title(title)
    pdf.set_author("doc-forge")
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.multi_cell(0, 10, text=title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    render_lines(pdf, body)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return pdf.page_no()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Checked-in markdown source")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output PDF path")
    args = parser.parse_args()

    page_count = build_fixture(args.source, args.output)
    print(f"Wrote {args.output} ({page_count} pages)")


if __name__ == "__main__":
    main()
