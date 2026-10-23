"""Source-located formula/merge inventory over stored SpreadsheetML records.

This is an acceptance check, not a worksheet renderer or formula evaluator.
Never expand the worksheet's declared rectangular dimensions into cells.
"""

from __future__ import annotations

import hashlib
import io
import xml.etree.ElementTree as ET
from xml.parsers import expat
from pathlib import Path
from typing import Any
from zipfile import ZipFile


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _reject_dtd(*args) -> None:
    raise ValueError("XLSX source inspection does not accept XML DTDs")


def _validate_sheet_xml(archive: ZipFile, part: str) -> None:
    # iterparse cannot use a custom TreeBuilder on supported Python3.11.
    # Validate without building a tree before the streaming inventory pass.
    parser = expat.ParserCreate()
    parser.StartDoctypeDeclHandler = _reject_dtd
    with archive.open(part) as stream:
        while chunk := stream.read(65536):
            parser.Parse(chunk, False)
    parser.Parse(b"", True)


def _scan_sheet(archive: ZipFile, part: str, sheet: str, report: dict[str, Any]) -> None:
    if archive.namelist().count(part) != 1:
        raise ValueError(f"Missing or ambiguous XLSX worksheet part: {part}")
    _validate_sheet_xml(archive, part)
    stack = []
    with archive.open(part) as stream:
        for event, node in ET.iterparse(stream, events=("start", "end")):
            if event == "start":
                if not stack and node.tag != f"{{{MAIN_NS}}}worksheet":
                    raise ValueError("Unrecognized XLSX worksheet namespace")
                stack.append(node)
                continue
            parent = stack[-2] if len(stack) > 1 else None
            if node.tag == f"{{{MAIN_NS}}}c" and parent is not None and parent.tag == f"{{{MAIN_NS}}}row":
                report["stored_cells_scanned"] += 1
                formula = node.find(f"{{{MAIN_NS}}}f")
                if formula is not None:
                    coordinate = node.attrib.get("r")
                    if not coordinate:
                        raise ValueError("Formula cell lacks a source coordinate")
                    cached = node.find(f"{{{MAIN_NS}}}v")
                    raw_cached = cached.text if cached is not None else None
                    report["formula_cells"].append({
                        "sheet": sheet,
                        "cell": coordinate,
                        "expression": "=" + formula.text if formula.text is not None else None,
                        "formula_kind": formula.attrib.get("t", "normal"),
                        "formula_range": formula.attrib.get("ref"),
                        "formula_xml_attributes": dict(formula.attrib),
                        "cached_xml_value": raw_cached,
                        "cached_xml_type": node.attrib.get("t", "n"),
                        "cache_element_present": cached is not None,
                        "cache_observation": "text_observed" if raw_cached is not None else "none_observed",
                    })
            elif node.tag == f"{{{MAIN_NS}}}mergeCell":
                reference = node.attrib.get("ref")
                if not reference:
                    raise ValueError("Merged cells lack a source range")
                report["merged_ranges"].append({"sheet": sheet, "range": reference})
            # Keep f/v children until the cell ends; release completed cells and
            # rows so memory follows stored records, not declared coordinates.
            if node.tag in {f"{{{MAIN_NS}}}c", f"{{{MAIN_NS}}}row", f"{{{MAIN_NS}}}mergeCell"}:
                node.clear()
                if parent is not None:
                    parent.remove(node)
            stack.pop()


def inspect_xlsx_features(xlsx_path: str | Path) -> dict[str, Any]:
    import openpyxl

    source = Path(xlsx_path).resolve()
    source_bytes = source.read_bytes()
    report: dict[str, Any] = {
        "schema_version": "xlsx_source_features_v1",
        "source_file": str(source),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "inspector": {"name": "SpreadsheetML stored-record inventory", "implementation": "stdlib XML iterparse", "part_authority": "openpyxl read-only worksheet identity", "reader_version": openpyxl.__version__},
        "scope": "Formula and merged-range acceptance only; not whole-workbook fidelity qualification",
        "cache_policy": "Cached XML text/type retained verbatim; no decoding, calculation or freshness verification. Empty and absent values are distinct from observed text.",
        "sheets": [],
        "source_parts": [],
        "stored_cells_scanned": 0,
        "formula_cells": [],
        "merged_ranges": [],
    }
    with ZipFile(io.BytesIO(source_bytes)) as archive:
        # Reject DTDs before either reader parses ordinary package XML. The
        # selected worksheet is checked again regardless of its file suffix.
        for part in archive.namelist():
            if part.lower().endswith((".xml", ".rels")):
                if archive.namelist().count(part) != 1:
                    raise ValueError(f"Ambiguous XLSX XML package part: {part}")
                _validate_sheet_xml(archive, part)
        # Use the exact consumer's metadata parser. Independent OPC resolution
        # can disagree about content-type authority or encoded target names.
        # Read-only mode does not expand merge geometry or cell rectangles.
        book = openpyxl.load_workbook(
            io.BytesIO(source_bytes), read_only=True, data_only=False, keep_links=False,
        )
        try:
            if not book.worksheets:
                raise ValueError("No native XLSX worksheet is available for inspection")
            for sheet in book.worksheets:
                # openpyxl has no public physical-part accessor. This narrow
                # read-only seam is qualified against the installed consumer;
                # an unavailable/changed seam fails rather than falling back.
                part = getattr(sheet, "_worksheet_path", None)
                if not isinstance(part, str) or not part:
                    raise ValueError("Native XLSX worksheet part identity unavailable")
                report["sheets"].append(sheet.title)
                report["source_parts"].append({"sheet": sheet.title, "part": part})
                _scan_sheet(archive, part, sheet.title, report)
        finally:
            book.close()
    report["disposition"] = (
        "blocked_unsupported_features" if report["formula_cells"] or report["merged_ranges"]
        else "native_feature_gate_clear"
    )
    return report
