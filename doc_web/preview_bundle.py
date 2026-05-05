from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from doc_web.preview_support import (
    INDEX_PATH,
    MODULE_ID,
    PROVENANCE_PATH,
    PreviewBlock,
    PreviewEntry,
    collapse_text,
    save_json,
    save_jsonl,
)
from schemas import DocWebBundleManifest, DocWebProvenanceBlock


def _block_tag(block: PreviewBlock) -> str:
    if block.kind == "heading":
        return "h2"
    if block.kind == "table":
        return "table"
    if block.kind == "list_item":
        return "li"
    return "p"


def _render_block(block: PreviewBlock, block_id: str) -> str:
    if block.kind == "table":
        return (
            block.html_text
            or f'<table id="{html.escape(block_id)}"><tbody></tbody></table>'
        )
    tag = _block_tag(block)
    return f'<{tag} id="{html.escape(block_id)}">{html.escape(block.text)}</{tag}>'


def _wrap_html(
    *, title: str, body_html: str, prev_entry_id: str | None, next_entry_id: str | None
) -> str:
    nav = ['<nav class="doc-nav">', '<a href="index.html">Contents</a>']
    if prev_entry_id:
        nav.append(f'<a href="{html.escape(prev_entry_id)}.html">Previous</a>')
    if next_entry_id:
        nav.append(f'<a href="{html.escape(next_entry_id)}.html">Next</a>')
    nav.append("</nav>")
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
</head>
<body>
{"".join(nav)}
{body_html}
</body>
</html>
"""


def _index_html(document_title: str, entries: list[dict[str, Any]]) -> str:
    items = "\n".join(
        f'  <li><a href="{html.escape(entry["path"])}">{html.escape(entry["title"])}</a></li>'
        for entry in entries
    )
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(document_title)} Preview</title>
</head>
<body>
  <h1>{html.escape(document_title)} Preview</h1>
  <p>This is a non-final doc-web preview bundle.</p>
  <ul>
{items}
  </ul>
</body>
</html>
"""


def write_bundle(
    *,
    out_dir: Path,
    entries: list[PreviewEntry],
    document_title: str,
    source_path: Path,
    created_at: str,
    run_id: str | None,
) -> tuple[
    dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    (out_dir / "provenance").mkdir(parents=True, exist_ok=True)

    manifest_entries: list[dict[str, Any]] = []
    provenance_rows: list[dict[str, Any]] = []
    selector_mappings: list[dict[str, Any]] = []
    parsed_units: list[dict[str, Any]] = []

    for index, entry in enumerate(entries, start=1):
        prev_entry_id = entries[index - 2].entry_id if index > 1 else None
        next_entry_id = entries[index].entry_id if index < len(entries) else None
        body_parts: list[str] = []
        if entry.status_message:
            body_parts.append(
                f'<p class="doc-web-preview-status">{html.escape(entry.status_message)}</p>'
            )

        for block_index, block in enumerate(entry.blocks, start=1):
            block_id = f"blk-{entry.entry_id}-{block_index:04d}"
            body_parts.append(_render_block(block, block_id))
            row = DocWebProvenanceBlock(
                schema_version="doc_web_provenance_block_v1",
                module_id=MODULE_ID,
                run_id=run_id,
                created_at=created_at,
                block_id=block_id,
                entry_id=entry.entry_id,
                block_kind=block.kind,
                source_page_number=block.source_page_number,
                source_element_ids=block.source_element_ids,
                confidence=block.confidence,
                text_quote=collapse_text(block.text)[:400] or None,
            ).model_dump(exclude_none=True)
            provenance_rows.append(row)
            parsed_units.append(
                {
                    "entry_id": entry.entry_id,
                    "block_id": block_id,
                    "block_kind": block.kind,
                    "source_page_number": block.source_page_number,
                    "source_element_ids": block.source_element_ids,
                    "confidence": block.confidence,
                    "text": collapse_text(block.text),
                }
            )
            selector_mappings.append(
                {
                    "preview_entry_id": entry.entry_id,
                    "preview_block_id": block_id,
                    "full_entry_id": entry.entry_id,
                    "full_block_id": block_id,
                    "mapping_kind": "preserved",
                    "source_element_ids": block.source_element_ids,
                    "reason": "Preview block id is deterministic for unchanged content.",
                }
            )

        filename = f"{entry.entry_id}.html"
        (out_dir / filename).write_text(
            _wrap_html(
                title=f"{entry.title} Preview",
                body_html="\n".join(body_parts),
                prev_entry_id=prev_entry_id,
                next_entry_id=next_entry_id,
            ),
            encoding="utf-8",
        )
        manifest_entries.append(
            {
                "entry_id": entry.entry_id,
                "kind": entry.kind,
                "title": entry.title,
                "path": filename,
                "order": index,
                "prev_entry_id": prev_entry_id,
                "next_entry_id": next_entry_id,
                "source_pages": entry.source_pages,
                "printed_pages": [],
            }
        )

    manifest = DocWebBundleManifest(
        schema_version="doc_web_bundle_manifest_v1",
        module_id=MODULE_ID,
        run_id=run_id,
        created_at=created_at,
        document_id=source_path.stem,
        title=document_title,
        source_artifact=str(source_path.resolve()),
        entries=manifest_entries,
        reading_order=[entry["entry_id"] for entry in manifest_entries],
        asset_roots=[],
        provenance_path=PROVENANCE_PATH,
    ).model_dump(exclude_none=True)

    (out_dir / INDEX_PATH).write_text(
        _index_html(document_title, manifest_entries), encoding="utf-8"
    )
    save_json(out_dir / "manifest.json", manifest)
    save_jsonl(out_dir / PROVENANCE_PATH, provenance_rows)
    return manifest, provenance_rows, selector_mappings, parsed_units
