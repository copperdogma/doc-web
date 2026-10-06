"""Literal table fidelity: positional comparison, never fuzzy row alignment.

HTML entities are decoded by the parser. Cell text is case-sensitive and only
whitespace is collapsed/trimmed; punctuation and Unicode remain unchanged.
Nested tables are separate tables and never contribute text/cells to a parent.
Rendered line/block boundaries become whitespace; inline markup stays adjacent.
Captions and table-owned text outside cells are compared without double counting.
Hidden, script, and style content fail structure rather than pretending visibility.
Indices in mismatch records are zero-based. Span values must be positive decimal
integers within HTML's limits; invalid geometry fails even if both inputs agree.
"""

import hashlib
from itertools import zip_longest
import json
import re

from bs4 import BeautifulSoup, Comment, NavigableString


# HTML's normal block boundaries separate adjacent words; inline markup does not.
_BLOCK_TAGS = {
    "address", "article", "aside", "blockquote", "caption", "dd", "div", "dl", "dt",
    "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4",
    "h5", "h6", "header", "hr", "li", "main", "nav", "ol", "p", "pre", "section", "ul",
    "tr", "thead", "tbody", "tfoot",
}


def _rendered_text(node, skip_tags=()):
    """Collect table-owned text with explicit rendered whitespace boundaries."""
    if isinstance(node, Comment):
        return ""
    if isinstance(node, NavigableString):
        return str(node)
    if node.name in {"table", "script", "style"}:
        return ""
    if node.name in skip_tags:
        return " "
    if node.name == "br":
        return " "
    contents = "".join(_rendered_text(child, skip_tags) for child in node.children)
    return " " + contents + " " if node.name in _BLOCK_TAGS else contents


def _normalized_text(node, skip_tags=()):
    # Start from children so a table root itself can supply outside-cell text.
    return re.sub(r"\s+", " ", "".join(
        _rendered_text(child, skip_tags) for child in node.children
    )).strip()


def _unsupported_visibility(node):
    style = node.get("style", "")
    return (node.has_attr("hidden") or node.get("aria-hidden", "").lower() == "true"
            or bool(re.search(r"(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse))",
                              style, re.IGNORECASE)))


def _parse(html):
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.find_all("table")
    tables = []
    for table_index, tag in enumerate(tags):
        rows = []
        issues = []
        row_tags = []
        groups = []
        owned_tags = [node for node in tag.find_all(True)
                      if node.find_parent("table") is tag]
        for node in [tag, *owned_tags]:
            if node.name in {"script", "style"} or _unsupported_visibility(node):
                issues.append({"kind": "unsupported_visibility", "tag": node.name})
        # A hidden wrapper outside the table also makes this transcription unsafe.
        if any(_unsupported_visibility(node) for node in tag.parents if getattr(node, "attrs", None)):
            issues.append({"kind": "unsupported_visibility", "tag": "ancestor"})
        captions = [_normalized_text(node) for node in owned_tags if node.name == "caption"]
        outside_text = _normalized_text(tag, skip_tags={"td", "th", "caption"})
        for child in tag.children:
            if getattr(child, "name", None) == "tr":
                row_tags.append(child)
                groups.append("direct")
            elif getattr(child, "name", None) in {"thead", "tbody", "tfoot"}:
                group_id = len(groups)
                section_rows = child.find_all("tr", recursive=False)
                row_tags.extend(section_rows)
                groups.extend([group_id] * len(section_rows))
        owned_rows = [tr for tr in tag.find_all("tr") if tr.find_parent("table") is tag]
        if {id(tr) for tr in owned_rows} != {id(tr) for tr in row_tags}:
            issues.append({"kind": "invalid_row_parent"})
        seen_cells = set()
        for row_index, tr in enumerate(row_tags):
            cells = []
            for cell_index, cell in enumerate(tr.find_all(["td", "th"], recursive=False)):
                seen_cells.add(id(cell))
                text = _normalized_text(cell)
                spans = {}
                for attr, maximum in (("rowspan", 65534), ("colspan", 1000)):
                    raw = cell.get(attr, "1")
                    if not isinstance(raw, str) or not re.fullmatch(r"[0-9]+", raw):
                        value = None
                    else:
                        # Avoid huge integer conversion on malformed model output.
                        value = int(raw) if len(raw) <= 5 else None
                    if value is None or not 1 <= value <= maximum:
                        issues.append({"kind": "invalid_span", "row": row_index,
                                       "cell": cell_index, "attribute": attr, "value": raw})
                        value = 1  # Only for diagnostic geometry; issue is fatal.
                    spans[attr] = value
                cells.append({"text": re.sub(r"\s+", " ", text).strip(),
                              "tag": cell.name, **spans})
            rows.append(cells)
        owned_cells = [c for c in tag.find_all(["td", "th"])
                       if c.find_parent("table") is tag]
        if {id(c) for c in owned_cells} != seen_cells:
            issues.append({"kind": "invalid_cell_parent"})
        # Intervals preserve slot ownership without allocating huge span grids.
        occupied = [[] for _ in rows]
        for row_index, cells in enumerate(rows):
            column = 0
            for cell_index, cell in enumerate(cells):
                while True:
                    covering = [(start, end) for start, end in occupied[row_index]
                                if start <= column < end]
                    if not covering:
                        break
                    column = max(end for _, end in covering)
                cell["column"] = column
                end = column + cell["colspan"]
                row_end = row_index + cell["rowspan"]
                if row_end > len(rows):
                    issues.append({"kind": "span_past_table", "row": row_index,
                                   "cell": cell_index, "row_end": row_end})
                elif any(groups[r] != groups[row_index] for r in range(row_index, row_end)):
                    issues.append({"kind": "span_crosses_row_group", "row": row_index,
                                   "cell": cell_index})
                for target_row in range(row_index, min(row_end, len(rows))):
                    if any(column < right and end > left for left, right in occupied[target_row]):
                        issues.append({"kind": "overlapping_span", "row": row_index,
                                       "cell": cell_index, "target_row": target_row})
                    occupied[target_row].append((column, end))
                column = end
        parent = tag.find_parent("table")
        parent_index = next((i for i, candidate in enumerate(tags) if candidate is parent), None)
        parent_cell = tag.find_parent(["td", "th"])
        parent_owner = None
        if parent is not None and parent_cell is not None:
            owner_row = parent_cell.find_parent("tr")
            parent_rows = [tr for tr in parent.find_all("tr")
                           if tr.find_parent("table") is parent]
            for ri, tr in enumerate(parent_rows):
                if tr is owner_row:
                    for ci, cell in enumerate(tr.find_all(["td", "th"], recursive=False)):
                        if cell is parent_cell:
                            parent_owner = [ri, ci]
        tables.append({"rows": rows, "issues": issues, "parent_table": parent_index,
                       "parent_owner": parent_owner, "captions": captions,
                       "outside_text": outside_text})
    return tables


def compare_tables(golden_html, actual_html, table_index=None):
    """Return independent text/structure verdicts and complete mismatch records.

    Default scope compares all tables in document order, including nested tables.
    ``table_index`` declares an actual-document one-table slice; the golden must
    contain exactly one table. Other actual tables are reported as excluded, and
    nested tables remain in document scope unless that explicit slice is used.
    Missing cells/rows/tables fail text as well as structure; geometry-only
    changes can pass text while failing structure. No-table inputs fail closed.
    """
    if table_index is not None and (isinstance(table_index, bool)
                                   or not isinstance(table_index, int) or table_index < 0):
        raise ValueError("table_index must be a nonnegative integer or None")
    golden = _parse(golden_html)
    actual = _parse(actual_html)
    original_actual = actual
    text_errors = []
    structure_errors = []
    scope = {"mode": "all_tables" if table_index is None else "single_table_slice",
             "table_index": table_index, "golden_table_count": len(golden),
             "actual_table_count": len(actual), "excluded_actual_table_indices": []}
    if table_index is not None:
        if len(golden) != 1:
            structure_errors.append({"kind": "invalid_golden_slice", "expected": 1,
                                     "actual": len(golden)})
        scope["excluded_actual_table_indices"] = [i for i in range(len(actual)) if i != table_index]
        actual = actual[table_index:table_index + 1]
    if not golden or not actual:
        structure_errors.append({"kind": "no_tables", "golden": len(golden), "actual": len(actual)})
        text_errors.append({"kind": "no_tables", "golden": len(golden), "actual": len(actual)})
    if len(golden) != len(actual):
        structure_errors.append({"kind": "table_count", "expected": len(golden), "actual": len(actual)})
    for ti, (gt, at) in enumerate(zip_longest(golden, actual)):
        location = {"table": ti, "actual_table": table_index if table_index is not None else ti}
        for side, table in (("golden", gt), ("actual", at)):
            if table is not None:
                structure_errors.extend({**location, "side": side, **issue} for issue in table["issues"])
        if gt is None or at is None:
            text_errors.append({**location, "kind": "missing_table" if at is None else "extra_table"})
        if gt is not None and at is not None:
            for key in ("captions", "outside_text"):
                if gt[key] != at[key]:
                    text_errors.append({**location, "kind": key,
                                        "expected": gt[key], "actual": at[key]})
        if gt is not None and at is not None and table_index is None:
            for key in ("parent_table", "parent_owner"):
                if gt[key] != at[key]:
                    structure_errors.append({**location, "kind": key,
                                             "expected": gt[key], "actual": at[key]})
        gr, ar = gt["rows"] if gt else [], at["rows"] if at else []
        if len(gr) != len(ar):
            structure_errors.append({**location, "kind": "row_count", "expected": len(gr), "actual": len(ar)})
        for ri, (grow, arow) in enumerate(zip_longest(gr, ar)):
            row_location = {**location, "row": ri}
            if grow is None or arow is None:
                text_errors.append({**row_location, "kind": "missing_row" if arow is None else "extra_row"})
            grow, arow = grow or [], arow or []
            if len(grow) != len(arow):
                structure_errors.append({**row_location, "kind": "cell_count", "expected": len(grow), "actual": len(arow)})
            for ci, (gc, ac) in enumerate(zip_longest(grow, arow)):
                cell_location = {**row_location, "cell": ci}
                if gc is None or ac is None or gc["text"] != ac["text"]:
                    text_errors.append({**cell_location, "kind": "cell_text",
                                        "expected": gc["text"] if gc else None,
                                        "actual": ac["text"] if ac else None})
                if gc is not None and ac is not None:
                    for key in ("tag", "rowspan", "colspan", "column"):
                        if gc[key] != ac[key]:
                            structure_errors.append({**cell_location, "kind": key,
                                                     "expected": gc[key], "actual": ac[key]})
    counts = {}
    for side, tables in (("golden", golden), ("actual", actual)):
        counts[side] = {"tables": len(tables), "rows": sum(len(t["rows"]) for t in tables),
                        "cells": sum(len(r) for t in tables for r in t["rows"])}
    scope["compared_actual_table_count"] = len(actual)
    scope["document_actual_table_count"] = len(original_actual)
    return {"text_pass": not text_errors, "structure_pass": not structure_errors,
            "pass": not text_errors and not structure_errors,
            "text_mismatch_count": len(text_errors), "structure_mismatch_count": len(structure_errors),
            "text_mismatches": text_errors, "structure_mismatches": structure_errors,
            "counts": counts, "scope": scope}


def canonical_table_digest(html):
    """Hash the exact parsed table contract, including text and geometry issues."""
    canonical = json.dumps(_parse(html), sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
