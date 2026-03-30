#!/usr/bin/env python3
"""Build a doc-web bundle directly from DOCX Unstructured elements."""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from modules.common.utils import ProgressLogger, ensure_dir, read_jsonl, save_json, save_jsonl
from schemas import DocWebBundleManifest, DocWebProvenanceBlock


TAG_RE = re.compile(r"<[^>]+>")


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slugify(value: str) -> str:
    lowered = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return lowered or "document"


def _collapse_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _text_quote(value: str) -> Optional[str]:
    collapsed = _collapse_text(TAG_RE.sub(" ", value or ""))
    if not collapsed:
        return None
    return collapsed[:400]


def _tag_for_element_type(element_type: str, *, first_heading: bool) -> str:
    if element_type == "Title":
        return "h1" if first_heading else "h2"
    if element_type in {"ListItem", "BulletedText"}:
        return "li"
    if element_type == "Table":
        return "table"
    if element_type in {"FigureCaption", "Figure"}:
        return "figcaption"
    return "p"


def _block_kind_for_element_type(element_type: str) -> str:
    if element_type == "Title":
        return "heading"
    if element_type in {"ListItem", "BulletedText"}:
        return "list_item"
    if element_type == "Table":
        return "table"
    if element_type == "Figure":
        return "figure"
    if element_type == "FigureCaption":
        return "caption"
    return "paragraph"


def _html_wrap(body_html: str, page_title: str, *, prev_href: Optional[str], next_href: Optional[str]) -> str:
    nav_bits = ['<nav class="doc-nav">', '<a href="index.html">Contents</a>']
    if prev_href:
        nav_bits.append(f'<a href="{html.escape(prev_href)}">Previous</a>')
    if next_href:
        nav_bits.append(f'<a href="{html.escape(next_href)}">Next</a>')
    nav_bits.append("</nav>")
    nav_html = "".join(nav_bits)
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(page_title)}</title>
  <style>
    body {{ font-family: Georgia, 'Times New Roman', serif; line-height: 1.6; margin: 2rem auto; max-width: 48rem; padding: 0 1rem 3rem; color: #1f1f1f; }}
    .doc-nav {{ display: flex; gap: 1rem; flex-wrap: wrap; margin: 0 0 2rem; font-size: 0.95rem; }}
    h1, h2 {{ line-height: 1.2; margin-top: 2rem; }}
    p, li {{ margin: 0.85rem 0; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 1.5rem; }}
    th, td {{ border: 1px solid #d9d9d9; padding: 0.45rem 0.6rem; text-align: left; }}
    thead th {{ background: #f4f4f4; }}
    ul {{ padding-left: 1.5rem; }}
  </style>
</head>
<body>
{nav_html}
{body_html}
</body>
</html>
"""


def _bundle_index_html(document_title: str, entries: List[Dict[str, Any]]) -> str:
    items = "\n".join(
        f'  <li><a href="{html.escape(entry["path"])}">{html.escape(entry["title"])}</a></li>'
        for entry in entries
    )
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(document_title)}</title>
</head>
<body>
  <h1>{html.escape(document_title)}</h1>
  <ul>
{items}
  </ul>
</body>
</html>
"""


def _source_artifact(elements: List[Dict[str, Any]], fallback: str) -> str:
    if not elements:
        return fallback
    metadata = elements[0].get("metadata", {}) or {}
    file_directory = metadata.get("file_directory")
    filename = metadata.get("filename")
    if file_directory and filename:
        return str((Path(file_directory) / filename).resolve())
    return fallback


def _top_level_title_indexes(elements: List[Dict[str, Any]]) -> List[int]:
    indexes = []
    for idx, element in enumerate(elements):
        metadata = element.get("metadata", {}) or {}
        if element.get("type") == "Title" and not metadata.get("parent_id"):
            if _collapse_text(element.get("text", "")):
                indexes.append(idx)
    return indexes


def _entry_slices(elements: List[Dict[str, Any]], fallback_title: str) -> tuple[str, List[dict[str, Any]]]:
    title_indexes = _top_level_title_indexes(elements)
    document_title = fallback_title
    entry_specs: List[dict[str, Any]] = []

    if title_indexes:
        document_title = _collapse_text(elements[title_indexes[0]].get("text", "")) or fallback_title

    if len(title_indexes) >= 2:
        section_indexes = title_indexes[1:]
        for ordinal, start in enumerate(section_indexes, start=1):
            end = section_indexes[ordinal] if ordinal < len(section_indexes) else len(elements)
            entry_elements = elements[start:end]
            entry_title = _collapse_text(entry_elements[0].get("text", "")) or f"Section {ordinal}"
            entry_specs.append(
                {
                    "entry_id": f"chapter-{ordinal:03d}",
                    "kind": "chapter",
                    "title": entry_title,
                    "elements": entry_elements,
                }
            )
    else:
        entry_specs.append(
            {
                "entry_id": "page-001",
                "kind": "page",
                "title": document_title,
                "elements": elements,
            }
        )

    return document_title, entry_specs


def _render_table_html(raw_table_html: str, block_id: str) -> str:
    soup = BeautifulSoup(raw_table_html, "html.parser")
    table = soup.find("table")
    if table is None:
        return f'<table id="{html.escape(block_id)}"><tbody><tr><td>{html.escape(_collapse_text(raw_table_html))}</td></tr></tbody></table>'
    table["id"] = block_id
    return str(table)


def _provenance_row(
    *,
    module_id: str,
    run_id: Optional[str],
    created_at: str,
    block_id: str,
    entry_id: str,
    block_kind: str,
    source_element_id: str,
    rendered_text: str,
) -> Dict[str, Any]:
    row = DocWebProvenanceBlock(
        schema_version="doc_web_provenance_block_v1",
        module_id=module_id,
        run_id=run_id,
        created_at=created_at,
        block_id=block_id,
        entry_id=entry_id,
        block_kind=block_kind,
        source_element_ids=[source_element_id],
        text_quote=_text_quote(rendered_text),
    )
    return row.model_dump(exclude_none=True)


def _render_entry(
    entry: Dict[str, Any],
    *,
    module_id: str,
    run_id: Optional[str],
    created_at: str,
) -> tuple[str, List[Dict[str, Any]]]:
    parts: List[str] = []
    provenance_rows: List[Dict[str, Any]] = []
    block_ordinal = 1
    first_heading = True
    elements = entry["elements"]
    idx = 0

    while idx < len(elements):
        element = elements[idx]
        element_type = element.get("type", "Unknown")
        text = element.get("text", "") or ""
        metadata = element.get("metadata", {}) or {}
        source_element_id = str(element.get("id") or f'{entry["entry_id"]}-source-{block_ordinal:04d}')

        if element_type in {"PageBreak", "Header", "Footer"} and not _collapse_text(text):
            idx += 1
            continue

        if element_type in {"ListItem", "BulletedText"}:
            list_items = []
            list_rows = []
            while idx < len(elements) and elements[idx].get("type") in {"ListItem", "BulletedText"}:
                list_element = elements[idx]
                list_text = list_element.get("text", "") or ""
                list_block_id = f'blk-{entry["entry_id"]}-{block_ordinal:04d}'
                list_element_id = str(list_element.get("id") or f'{entry["entry_id"]}-source-{block_ordinal:04d}')
                list_items.append(f'<li id="{html.escape(list_block_id)}">{html.escape(_collapse_text(list_text))}</li>')
                list_rows.append(
                    _provenance_row(
                        module_id=module_id,
                        run_id=run_id,
                        created_at=created_at,
                        block_id=list_block_id,
                        entry_id=entry["entry_id"],
                        block_kind="list_item",
                        source_element_id=list_element_id,
                        rendered_text=list_text,
                    )
                )
                block_ordinal += 1
                idx += 1
            parts.append("<ul>\n" + "\n".join(list_items) + "\n</ul>")
            provenance_rows.extend(list_rows)
            continue

        block_id = f'blk-{entry["entry_id"]}-{block_ordinal:04d}'
        tag_name = _tag_for_element_type(element_type, first_heading=first_heading)
        block_kind = _block_kind_for_element_type(element_type)
        rendered_html = ""
        rendered_text = text

        if element_type == "Title":
            rendered_html = f'<{tag_name} id="{html.escape(block_id)}">{html.escape(_collapse_text(text))}</{tag_name}>'
            first_heading = False
        elif element_type == "Table":
            rendered_html = _render_table_html(metadata.get("text_as_html") or text, block_id)
            first_heading = False
        elif element_type in {"FigureCaption", "Figure"}:
            rendered_html = f'<{tag_name} id="{html.escape(block_id)}">{html.escape(_collapse_text(text))}</{tag_name}>'
            first_heading = False
        else:
            rendered_html = f'<{tag_name} id="{html.escape(block_id)}">{html.escape(_collapse_text(text))}</{tag_name}>'
            first_heading = False

        if _collapse_text(text) or element_type == "Table":
            parts.append(rendered_html)
            provenance_rows.append(
                _provenance_row(
                    module_id=module_id,
                    run_id=run_id,
                    created_at=created_at,
                    block_id=block_id,
                    entry_id=entry["entry_id"],
                    block_kind=block_kind,
                    source_element_id=source_element_id,
                    rendered_text=rendered_text,
                )
            )

        block_ordinal += 1
        idx += 1

    return "\n".join(parts), provenance_rows


def _build_bundle(
    elements: List[Dict[str, Any]],
    *,
    out_path: Path,
    module_id: str,
    run_id: Optional[str],
    book_title: str,
    book_author: str,
) -> Dict[str, Any]:
    run_dir = out_path.resolve().parents[1]
    html_dir = run_dir / "output" / "html"
    provenance_dir = html_dir / "provenance"
    ensure_dir(str(html_dir))
    ensure_dir(str(provenance_dir))

    fallback_title = book_title.strip() or out_path.stem
    document_title, entry_specs = _entry_slices(elements, fallback_title)
    if book_title.strip():
        document_title = book_title.strip()
    created_at = _utc()
    source_artifact = _source_artifact(elements, fallback_title)

    manifest_entries: List[Dict[str, Any]] = []
    provenance_rows: List[Dict[str, Any]] = []
    entry_files: List[tuple[str, str]] = []

    for index, entry in enumerate(entry_specs, start=1):
        prev_entry_id = entry_specs[index - 2]["entry_id"] if index > 1 else None
        next_entry_id = entry_specs[index]["entry_id"] if index < len(entry_specs) else None
        body_html, entry_rows = _render_entry(
            entry,
            module_id=module_id,
            run_id=run_id,
            created_at=created_at,
        )
        provenance_rows.extend(entry_rows)
        filename = f'{entry["entry_id"]}.html'
        wrapped = _html_wrap(
            body_html,
            f'{entry["title"]} — {document_title}',
            prev_href=f"{prev_entry_id}.html" if prev_entry_id else None,
            next_href=f"{next_entry_id}.html" if next_entry_id else None,
        )
        (html_dir / filename).write_text(wrapped, encoding="utf-8")
        entry_files.append((entry["entry_id"], filename))
        manifest_entries.append(
            {
                "entry_id": entry["entry_id"],
                "kind": entry["kind"],
                "title": entry["title"],
                "path": filename,
                "order": index,
                "prev_entry_id": prev_entry_id,
                "next_entry_id": next_entry_id,
                "source_pages": [],
                "printed_pages": [],
            }
        )

    manifest = DocWebBundleManifest(
        schema_version="doc_web_bundle_manifest_v1",
        module_id=module_id,
        run_id=run_id,
        created_at=created_at,
        document_id=_slugify(document_title),
        title=document_title,
        creator=book_author or None,
        source_artifact=source_artifact,
        entries=manifest_entries,
        reading_order=[entry["entry_id"] for entry in manifest_entries],
        asset_roots=[],
        provenance_path="provenance/blocks.jsonl",
    ).model_dump(exclude_none=True)

    (html_dir / "index.html").write_text(
        _bundle_index_html(document_title, manifest_entries),
        encoding="utf-8",
    )
    save_json(html_dir / "manifest.json", manifest)
    save_jsonl(provenance_dir / "blocks.jsonl", provenance_rows)

    return {
        "manifest_path": str((html_dir / "manifest.json").resolve()),
        "provenance_path": str((provenance_dir / "blocks.jsonl").resolve()),
        "index_path": str((html_dir / "index.html").resolve()),
        "entry_count": len(manifest_entries),
        "provenance_row_count": len(provenance_rows),
        "reading_order": manifest["reading_order"],
        "document_title": document_title,
        "source_artifact": source_artifact,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input unstructured elements JSONL path")
    parser.add_argument("--out", required=True, help="Output report JSON path")
    parser.add_argument("--book-title", default="", help="Optional document title override")
    parser.add_argument("--book-author", default="", help="Optional document author override")
    parser.add_argument("--run-id", dest="run_id", default=None, help="Driver compatibility")
    parser.add_argument("--state-file", dest="state_file", default=None, help="Driver compatibility")
    parser.add_argument("--progress-file", dest="progress_file", default=None, help="Driver compatibility")
    args = parser.parse_args()

    module_id = "docx_elements_to_bundle_v1"
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )
    logger.log("docx_bundle", "running", message=f"Loading {args.input}", module_id=module_id)

    elements = list(read_jsonl(args.input))
    if not elements:
        raise SystemExit("No DOCX elements found; cannot build bundle")

    out_path = Path(args.out)
    ensure_dir(str(out_path.parent))
    report = _build_bundle(
        elements,
        out_path=out_path,
        module_id=module_id,
        run_id=args.run_id,
        book_title=args.book_title,
        book_author=args.book_author,
    )
    save_json(str(out_path), report)
    logger.log(
        "docx_bundle",
        "done",
        current=report["entry_count"],
        total=report["entry_count"],
        message=f'Built DOCX bundle with {report["entry_count"]} entries and {report["provenance_row_count"]} provenance rows',
        artifact=str(out_path),
        module_id=module_id,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
