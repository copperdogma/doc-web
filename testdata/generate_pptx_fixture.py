#!/usr/bin/env python3
"""Generate the reproducible PPTX probe fixture from checked-in markdown."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "pptx-mini.md"
DEFAULT_OUTPUT = ROOT / "pptx-mini.pptx"


def build_fixture(source_path: Path, output_path: Path) -> None:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("pandoc is required to generate the PPTX probe fixture")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [pandoc, str(source_path), "-t", "pptx", "-o", str(output_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or "pandoc failed to generate PPTX fixture")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Checked-in markdown source")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output PPTX path")
    args = parser.parse_args()

    build_fixture(args.source, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
