from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from doc_web.preview_support import PreviewBlock, PreviewEntry, collapse_text


def _table_html(table: Table, block_id: str) -> str:
    rows = []
    for row in table.rows:
        cells = "".join(
            f"<td>{html.escape(collapse_text(cell.text))}</td>" for cell in row.cells
        )
        rows.append(f"<tr>{cells}</tr>")
    return f'<table id="{html.escape(block_id)}"><tbody>{"".join(rows)}</tbody></table>'


def _docx_blocks(source_path: Path) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    document = Document(str(source_path))
    title = (
        collapse_text(document.core_properties.title or "")
        or source_path.stem.replace("-", " ").replace("_", " ").title()
    )
    blocks: list[dict[str, Any]] = []
    paragraph_count = 0
    table_count = 0

    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            paragraph = Paragraph(child, document)
            text = collapse_text(paragraph.text)
            if not text:
                continue
            paragraph_count += 1
            style_name = paragraph.style.name if paragraph.style is not None else ""
            blocks.append(
                {
                    "type": "paragraph",
                    "style": style_name,
                    "text": text,
                    "source_element_id": f"docx-paragraph-{paragraph_count:04d}",
                }
            )
        elif isinstance(child, CT_Tbl):
            table_count += 1
            table = Table(child, document)
            text = collapse_text(
                " ".join(cell.text for row in table.rows for cell in row.cells)
            )
            blocks.append(
                {
                    "type": "table",
                    "style": "Table",
                    "text": text,
                    "table": table,
                    "source_element_id": f"docx-table-{table_count:04d}",
                }
            )

    facts = {
        "format": "docx",
        "paragraph_count": paragraph_count,
        "table_count": table_count,
        "metadata_title": document.core_properties.title or None,
        "metadata_creator": document.core_properties.author or None,
        "pageless": True,
    }
    return title, blocks, facts


def docx_preview(
    *,
    source_path: Path,
    max_sample_units: int,
) -> tuple[
    list[PreviewEntry],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[str],
    str,
]:
    document_title, blocks, facts = _docx_blocks(source_path)
    entries: list[PreviewEntry] = []
    current: PreviewEntry | None = None
    skipped_units: list[dict[str, Any]] = []
    included_units: list[dict[str, Any]] = []

    def ensure_entry(title: str | None = None) -> PreviewEntry:
        nonlocal current
        if current is None:
            entry_id = f"chapter-{len(entries) + 1:03d}"
            current = PreviewEntry(
                entry_id=entry_id,
                kind="chapter",
                title=title or document_title,
            )
            entries.append(current)
        return current

    for block in blocks:
        style = str(block.get("style") or "")
        text = str(block.get("text") or "")
        if style == "Title" and not entries and current is None:
            document_title = text or document_title
            facts["metadata_title"] = document_title
            continue
        if style.startswith("Heading 1"):
            if len(entries) >= max_sample_units:
                skipped_units.append(
                    {
                        "kind": "entry",
                        "identifier": text,
                        "included": False,
                        "reason": "outside_preview_sample",
                    }
                )
                current = None
                continue
            current = PreviewEntry(
                entry_id=f"chapter-{len(entries) + 1:03d}",
                kind="chapter",
                title=text or f"Section {len(entries) + 1}",
            )
            entries.append(current)
            current.blocks.append(
                PreviewBlock(
                    kind="heading",
                    text=text,
                    source_element_ids=[str(block["source_element_id"])],
                    confidence=1.0,
                )
            )
            included_units.append(
                {"kind": "entry", "identifier": current.entry_id, "included": True}
            )
            continue
        if len(entries) >= max_sample_units and current is None:
            continue
        entry = ensure_entry()
        if block["type"] == "table":
            block_id = f"blk-{entry.entry_id}-{len(entry.blocks) + 1:04d}"
            entry.blocks.append(
                PreviewBlock(
                    kind="table",
                    text=text,
                    source_element_ids=[str(block["source_element_id"])],
                    confidence=1.0,
                    html_text=_table_html(block["table"], block_id),
                )
            )
        elif style.startswith("Heading"):
            entry.blocks.append(
                PreviewBlock(
                    kind="heading",
                    text=text,
                    source_element_ids=[str(block["source_element_id"])],
                    confidence=1.0,
                )
            )
        elif style.startswith("List"):
            entry.blocks.append(
                PreviewBlock(
                    kind="list_item",
                    text=text,
                    source_element_ids=[str(block["source_element_id"])],
                    confidence=1.0,
                )
            )
        else:
            entry.blocks.append(
                PreviewBlock(
                    kind="paragraph",
                    text=text,
                    source_element_ids=[str(block["source_element_id"])],
                    confidence=1.0,
                )
            )

    if not entries:
        entries.append(
            PreviewEntry(
                entry_id="page-001",
                kind="page",
                title=document_title,
                status_message="No readable DOCX preview blocks were found.",
            )
        )
        coverage_state = "deferred"
    else:
        coverage_state = "sampled" if skipped_units else "complete"

    facts["entry_count"] = len(entries)
    facts["sampled_entry_limit"] = max_sample_units
    return entries, facts, included_units, skipped_units, [], coverage_state
