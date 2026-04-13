"""
Shared HTML stitching helpers for the Onward scanned-genealogy seam.

This keeps the late chapter-build repair focused on chapter-local table
continuity while giving rerun/build one explicit owner for the shared HTML
normalization behavior.
"""

from copy import deepcopy
import re
from typing import Any, List, Optional

from bs4 import BeautifulSoup

try:
    from modules.adapter.table_rescue_onward_tables_v1.main import (
        _normalize_rescue_html_for_chapter_merge as _normalize_genealogy_rescue_html,
    )
except Exception:  # pragma: no cover - optional adapter reuse
    _normalize_genealogy_rescue_html = None


_GENEALOGY_EXPECTED_HEADERS = ["name", "born", "married", "spouse", "boy", "girl", "died"]
_GENEALOGY_HEADER_TOKEN_SETS = {
    tuple(_GENEALOGY_EXPECTED_HEADERS),
    ("name", "born", "married", "spouse", "boygirl", "died"),
}
_GENEALOGY_FAMILY_HEADING_RE = re.compile(r"\b[A-Z][A-Z'’\-]+(?:\s+[A-Z][A-Z'’\-]+)*\s+FAMILY\b")
_GENEALOGY_GENERATION_CONTEXT_RE = re.compile(
    r"\b(?:great\s+grandchildren|grandchildren|children)\b",
    re.IGNORECASE,
)
_GENEALOGY_CONTEXT_LINE_RE = re.compile(
    r"(?:[A-Z][\w.\-]*\s+)*[A-Z][\w.\-]*['’](?:s)?\s+"
    r"(?:Great\s+Great\s+Grandchildren|Great\s+Grandchildren|Grandchildren|Children)\b"
)
_GENEALOGY_SUMMARY_LABELS = ("TOTAL DESCENDANTS", "LIVING", "DECEASED")
_GENEALOGY_CHILD_NOTE_RE = re.compile(
    r"\b(?:born|boys?|girls?|child(?:ren)?|was born|to\b|infants?\s+died|\d+\s+(?:months?|years?)\s+old|infant)\b",
    re.IGNORECASE,
)


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _normalize_genealogy_token(text: str) -> str:
    return re.sub(r"[^a-z]", "", (text or "").lower())


def _genealogy_heading_lines(tag: Any) -> List[str]:
    if tag is None:
        return []
    return _genealogy_heading_lines_from_text(tag.get_text("\n", strip=True))


def _genealogy_heading_lines_from_text(text: str) -> List[str]:
    raw_lines = [
        line.strip()
        for line in (text or "").split("\n")
        if line.strip()
    ]
    lines: List[str] = []
    for line in raw_lines:
        lines.extend(_split_flattened_genealogy_heading_line(line))
    return lines


def _split_flattened_genealogy_heading_line(line: str) -> List[str]:
    normalized = _normalize_ws(line)
    if not normalized:
        return []

    family_line = None
    prefix = normalized
    family_matches = list(_GENEALOGY_FAMILY_HEADING_RE.finditer(normalized))
    if family_matches and family_matches[-1].end() == len(normalized):
        family_line = family_matches[-1].group(0).strip()
        prefix = normalized[:family_matches[-1].start()].strip()

    parts: List[str] = []
    if prefix:
        pos = 0
        for match in _GENEALOGY_CONTEXT_LINE_RE.finditer(prefix):
            if prefix[pos:match.start()].strip():
                parts = []
                break
            parts.append(match.group(0).strip())
            pos = match.end()
        if parts and prefix[pos:].strip():
            parts = []
    if family_line:
        parts.append(family_line)

    if parts and all(
        _extract_genealogy_family_labels(part) or _is_genealogy_generation_context(part)
        for part in parts
    ):
        return parts
    return [normalized]


def _extract_genealogy_family_labels(text: str) -> List[str]:
    normalized = _normalize_ws(text).replace("’", "'").upper()
    return list(dict.fromkeys(_GENEALOGY_FAMILY_HEADING_RE.findall(normalized)))


def _is_genealogy_generation_context(text: str) -> bool:
    normalized = _normalize_ws(text).replace("’", "'")
    if not normalized or len(normalized) > 120:
        return False
    if _extract_genealogy_family_labels(normalized):
        return False
    return bool(_GENEALOGY_GENERATION_CONTEXT_RE.search(normalized))


def _is_genealogy_heading_tag(tag: Any) -> bool:
    if getattr(tag, "name", None) not in {"h1", "h2", "h3", "p"}:
        return False
    lines = _genealogy_heading_lines(tag)
    if not lines:
        return False
    return all(
        _extract_genealogy_family_labels(line) or _is_genealogy_generation_context(line)
        for line in lines
    )


def _genealogy_table_header_tokens(table: Any) -> List[str]:
    thead = table.find("thead", recursive=False)
    header_row = None
    if thead is not None:
        for row in thead.find_all("tr", recursive=False):
            tokens = _genealogy_row_header_tokens(row)
            if tuple(tokens) in _GENEALOGY_HEADER_TOKEN_SETS:
                header_row = row
                break
    if header_row is None and thead is not None:
        header_row = thead.find("tr", recursive=False)
    if header_row is None:
        header_row = table.find("tr", recursive=False)
    if header_row is None:
        return []
    return _genealogy_row_header_tokens(header_row)


def _genealogy_row_header_tokens(row: Any) -> List[str]:
    if row is None:
        return []
    tokens = [
        _normalize_genealogy_token(cell.get_text(" ", strip=True))
        for cell in row.find_all(["th", "td"], recursive=False)
    ]
    while tokens and not tokens[-1]:
        tokens.pop()
    return tokens


def _is_genealogy_header_row(row: Any) -> bool:
    return tuple(_genealogy_row_header_tokens(row)) in _GENEALOGY_HEADER_TOKEN_SETS


def _is_genealogy_table_header(table: Any) -> bool:
    return tuple(_genealogy_table_header_tokens(table)) in _GENEALOGY_HEADER_TOKEN_SETS


def _genealogy_table_column_count(table: Any) -> int:
    counts = [len(_genealogy_table_header_tokens(table))]
    tbody = table.find("tbody", recursive=False)
    rows = tbody.find_all("tr", recursive=False) if tbody is not None else table.find_all("tr", recursive=False)
    for row in rows:
        cells = row.find_all(["th", "td"], recursive=False)
        if cells:
            counts.append(len(cells))
    return max(counts) if counts else len(_GENEALOGY_EXPECTED_HEADERS)


def _is_compatible_genealogy_table(table: Any, expected_cols: int) -> bool:
    if _is_genealogy_table_header(table):
        return True
    if table.find("thead", recursive=False) is not None:
        return False

    tbody = table.find("tbody", recursive=False)
    rows = tbody.find_all("tr", recursive=False) if tbody is not None else table.find_all("tr", recursive=False)
    if not rows:
        return False

    saw_cells = False
    for row in rows:
        cells = row.find_all(["th", "td"], recursive=False)
        if not cells:
            continue
        saw_cells = True
        if len(cells) > expected_cols:
            return False
    return saw_cells


def _looks_like_genealogy_continuation_table(table: Any) -> bool:
    if _is_genealogy_table_header(table):
        return True

    tbody = table.find("tbody", recursive=False)
    rows = tbody.find_all("tr", recursive=False) if tbody is not None else table.find_all("tr", recursive=False)
    for row in rows:
        cells = row.find_all(["th", "td"], recursive=False)
        if not cells:
            continue
        texts = [_normalize_ws(cell.get_text(" ", strip=True)) for cell in cells]
        non_empty = [text for text in texts if text]
        if not non_empty:
            continue
        if len(cells) == 1:
            text = non_empty[0]
            if _extract_genealogy_family_labels(text) or _is_genealogy_generation_context(text):
                return True
            continue
        if any(label in non_empty[0].upper() for label in _GENEALOGY_SUMMARY_LABELS):
            continue
        return True
    return False


def _convert_definition_lists_to_tables(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    changed = False
    for dl in list(soup.find_all("dl")):
        pairs = []
        current_term = None
        for child in dl.children:
            name = getattr(child, "name", None)
            if name == "dt":
                if current_term is not None:
                    pairs.append((current_term, ""))
                current_term = _normalize_ws(child.get_text(" ", strip=True))
            elif name == "dd":
                text = _normalize_ws(child.get_text(" ", strip=True))
                if current_term is None:
                    continue
                pairs.append((current_term, text))
                current_term = None
        if current_term is not None:
            pairs.append((current_term, ""))
        if not pairs:
            continue

        table = soup.new_tag("table")
        tbody = soup.new_tag("tbody")
        table.append(tbody)
        for term, value in pairs:
            row = soup.new_tag("tr")
            term_cell = soup.new_tag("td")
            term_cell.string = term
            row.append(term_cell)
            value_cell = soup.new_tag("td")
            value_cell.string = value
            row.append(value_cell)
            tbody.append(row)
        dl.replace_with(table)
        changed = True
    return str(soup) if changed else (html or "")


def _next_significant_sibling(node: Any) -> Any:
    sibling = node.next_sibling
    while sibling is not None:
        if getattr(sibling, "name", None) is not None:
            return sibling
        if str(sibling).strip():
            return sibling
        sibling = sibling.next_sibling
    return None


def _previous_significant_sibling(node: Any) -> Any:
    sibling = node.previous_sibling
    while sibling is not None:
        if getattr(sibling, "name", None) is not None:
            return sibling
        if str(sibling).strip():
            return sibling
        sibling = sibling.previous_sibling
    return None


def _genealogy_heading_lines_from_node(node: Any) -> List[str]:
    if node is None:
        return []
    tag_name = getattr(node, "name", None)
    if tag_name is not None:
        if not _is_genealogy_heading_tag(node):
            return []
        return _genealogy_heading_lines(node)

    lines = _genealogy_heading_lines_from_text(str(node))
    if not lines:
        return []
    if not all(
        _extract_genealogy_family_labels(line) or _is_genealogy_generation_context(line)
        for line in lines
    ):
        return []
    return lines


def _is_genealogy_name_list_paragraph(tag: Any) -> bool:
    if getattr(tag, "name", None) != "p" or tag.find_parent("table") is not None:
        return False
    if tag.find(["table", "img", "figure"]) is not None:
        return False

    lines = [
        line.strip()
        for line in tag.get_text("\n", strip=True).split("\n")
        if line.strip()
    ]
    if not lines or len(lines) > 8:
        return False

    for line in lines:
        normalized = _normalize_ws(line)
        if not normalized or any(ch.isdigit() for ch in normalized):
            return False
        if _extract_genealogy_family_labels(normalized) or _is_genealogy_generation_context(normalized):
            return False
        tokens = normalized.replace("’", "'").split()
        if len(tokens) > 3:
            return False
        if not all(re.fullmatch(r"[A-Za-z][A-Za-z'’.\-]*", token) for token in tokens):
            return False
    return True


def _convert_genealogy_name_list_paragraphs_to_tables(soup: BeautifulSoup) -> None:
    for heading in list(soup.find_all(["h1", "h2", "h3"])):
        heading_lines = _genealogy_heading_lines(heading)
        if not heading_lines or not _extract_genealogy_family_labels(heading_lines[-1]):
            continue

        paragraph = _next_significant_sibling(heading)
        if not _is_genealogy_name_list_paragraph(paragraph):
            continue

        follow = _next_significant_sibling(paragraph)
        if getattr(follow, "name", None) not in {"h1", "h2", "h3", "table"}:
            continue

        table = soup.new_tag("table")
        tbody = soup.new_tag("tbody")
        table.append(tbody)
        for line in [
            line.strip()
            for line in paragraph.get_text("\n", strip=True).split("\n")
            if line.strip()
        ]:
            row = soup.new_tag("tr")
            cell = soup.new_tag("td")
            cell.string = line
            row.append(cell)
            tbody.append(row)

        paragraph.replace_with(table)


def _row_genealogy_heading_lines(row: Any) -> List[str]:
    cells = row.find_all(["th", "td"], recursive=False)
    if not cells:
        return []

    non_empty_indices = [
        idx
        for idx, cell in enumerate(cells)
        if _normalize_ws(cell.get_text(" ", strip=True))
    ]
    if non_empty_indices != [0]:
        return []

    lines = _genealogy_heading_lines_from_text(cells[0].get_text("\n", strip=True))
    if not lines:
        return []
    if not all(
        _extract_genealogy_family_labels(line) or _is_genealogy_generation_context(line)
        for line in lines
    ):
        return []
    return lines


def _looks_like_death_value(text: str) -> bool:
    normalized = _normalize_ws(text)
    if not normalized:
        return False
    upper = normalized.upper()
    if upper == "DECEASED" or "MONTH" in upper or "YEAR" in upper:
        return True
    if re.search(r"\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|SEPT|OCT|NOV|DEC)[A-Z.]*\b", upper):
        return True
    if re.fullmatch(r",?\s*\d{4}", normalized):
        return True
    return bool(re.search(r"\d{4}", normalized) and not re.fullmatch(r"\d+", normalized))


def _looks_like_child_note_value(text: str) -> bool:
    normalized = _normalize_ws(text)
    if not normalized:
        return False
    return bool(_GENEALOGY_CHILD_NOTE_RE.search(normalized) or re.match(r"^\d+\s*[-A-Za-z]", normalized))


def _normalize_genealogy_body_rows(table: Any, soup: BeautifulSoup) -> None:
    tbody = table.find("tbody", recursive=False)
    rows = list(tbody.find_all("tr", recursive=False)) if tbody is not None else list(table.find_all("tr", recursive=False))
    if not rows:
        return

    col_count = _genealogy_table_column_count(table)
    header_tokens = _genealogy_table_header_tokens(table)
    canonical_seven_col = header_tokens[:7] == ["name", "born", "married", "spouse", "boy", "girl", "died"]

    for row in rows:
        if row.parent is None:
            continue

        if _is_genealogy_header_row(row):
            if table.find("thead", recursive=False) is not None or row is not rows[0]:
                row.decompose()
                continue

        heading_lines = _row_genealogy_heading_lines(row)
        if heading_lines:
            new_rows = [
                _build_genealogy_subgroup_row(line, col_count, soup)
                for line in heading_lines
            ]
            for new_row in new_rows[::-1]:
                row.insert_after(new_row)
            row.decompose()
            continue

        if "genealogy-subgroup-heading" in (row.get("class") or []):
            cells = row.find_all(["th", "td"], recursive=False)
            if len(cells) == 1:
                cells[0]["colspan"] = str(col_count)
            continue

        if not canonical_seven_col:
            continue

        cells = row.find_all(["td", "th"], recursive=False)
        if len(cells) < 7:
            continue

        boy_cell = cells[4]
        girl_cell = cells[5]
        died_cell = cells[6]
        boy_text = _normalize_ws(boy_cell.get_text(" ", strip=True))
        girl_text = _normalize_ws(girl_cell.get_text(" ", strip=True))
        died_text = _normalize_ws(died_cell.get_text(" ", strip=True))

        if boy_text and not girl_text and not died_text:
            nums = re.findall(r"\d+", boy_text)
            if len(nums) >= 2:
                boy_cell.clear()
                boy_cell.append(nums[0])
                girl_cell.clear()
                girl_cell.append(nums[1])
                girl_text = nums[1]
                died_text = ""

        if girl_text and not died_text and _looks_like_death_value(girl_text) and not _looks_like_child_note_value(girl_text):
            girl_cell.clear()
            died_cell.clear()
            died_cell.append(girl_text)


def _build_genealogy_subgroup_row(line: str, colspan: int, soup: BeautifulSoup) -> Any:
    row = soup.new_tag("tr")
    row["class"] = "genealogy-subgroup-heading"
    cell = soup.new_tag("th", colspan=str(colspan))
    cell.string = line
    row.append(cell)
    return row


def _clone_genealogy_row(row: Any, col_count: int, soup: BeautifulSoup) -> Any:
    cloned = deepcopy(row)
    cells = cloned.find_all(["td", "th"], recursive=False)
    if "genealogy-subgroup-heading" in (cloned.get("class") or []):
        if len(cells) == 1:
            cells[0]["colspan"] = str(col_count)
        return cloned

    while len(cells) < col_count:
        cell = soup.new_tag("td")
        cloned.append(cell)
        cells.append(cell)
    return cloned


def _prepend_genealogy_subgroup_rows(table: Any, lines: List[str], soup: BeautifulSoup) -> None:
    if not lines:
        return
    tbody = table.find("tbody", recursive=False)
    if tbody is None:
        tbody = soup.new_tag("tbody")
        table.append(tbody)
    first_row = tbody.find("tr", recursive=False)
    col_count = _genealogy_table_column_count(table)
    for line in lines:
        row = _build_genealogy_subgroup_row(line, col_count, soup)
        if first_row is not None:
            first_row.insert_before(row)
        else:
            tbody.append(row)


def _split_combined_boygirl_header(row: Any, soup: BeautifulSoup) -> None:
    cells = row.find_all(["th", "td"], recursive=False)
    if len(cells) != 6:
        return
    tokens = [_normalize_genealogy_token(cell.get_text(" ", strip=True)) for cell in cells]
    if tuple(tokens) != ("name", "born", "married", "spouse", "boygirl", "died"):
        return
    combined = cells[4]
    tag_name = getattr(combined, "name", None) or "th"
    boy = soup.new_tag(tag_name)
    boy.string = "BOY"
    girl = soup.new_tag(tag_name)
    girl.string = "GIRL"
    combined.insert_before(boy)
    combined.insert_before(girl)
    combined.decompose()


def _normalize_genealogy_table_head(table: Any, soup: BeautifulSoup) -> None:
    thead = table.find("thead", recursive=False)
    if thead is None:
        return

    rows = thead.find_all("tr", recursive=False)
    canonical_row = None
    canonical_index = None
    for idx, row in enumerate(rows):
        tokens = _genealogy_row_header_tokens(row)
        if tuple(tokens) in _GENEALOGY_HEADER_TOKEN_SETS:
            canonical_row = row
            canonical_index = idx
            break
    if canonical_row is None:
        return

    _split_combined_boygirl_header(canonical_row, soup)

    if canonical_index is None or canonical_index == 0:
        return

    heading_lines: List[str] = []
    for row in rows[:canonical_index]:
        lines = _row_genealogy_heading_lines(row)
        if not lines:
            continue
        heading_lines.extend(lines)
        row.decompose()
    _prepend_genealogy_subgroup_rows(table, heading_lines, soup)


def _absorb_leading_genealogy_headings(base_table: Any, soup: BeautifulSoup) -> None:
    nodes_and_lines: List[Any] = []
    cursor = base_table
    while True:
        prev = _previous_significant_sibling(cursor)
        if prev is None:
            break
        lines = _genealogy_heading_lines_from_node(prev)
        if not lines:
            break
        nodes_and_lines.append((prev, lines))
        cursor = prev

    if not nodes_and_lines:
        return

    all_lines: List[str] = []
    for node, lines in reversed(nodes_and_lines):
        all_lines.extend(lines)
        node.extract()
    _prepend_genealogy_subgroup_rows(base_table, all_lines, soup)


def _append_genealogy_heading_and_rows(base_table: Any, heading_tags: List[Any], source_table: Any,
                                       soup: BeautifulSoup) -> None:
    heading_lines: List[str] = []
    for tag in heading_tags:
        heading_lines.extend(_genealogy_heading_lines(tag))
    _append_genealogy_heading_lines_and_rows(base_table, heading_lines, source_table, soup)


def _append_genealogy_heading_lines_and_rows(base_table: Any, heading_lines: List[str], source_table: Any,
                                             soup: BeautifulSoup) -> None:
    base_tbody = base_table.find("tbody", recursive=False)
    if base_tbody is None:
        base_tbody = soup.new_tag("tbody")
        base_table.append(base_tbody)

    col_count = _genealogy_table_column_count(base_table)
    for line in heading_lines:
        base_tbody.append(_build_genealogy_subgroup_row(line, col_count, soup))

    source_tbody = source_table.find("tbody", recursive=False)
    rows = source_tbody.find_all("tr", recursive=False) if source_tbody is not None else source_table.find_all("tr", recursive=False)
    if source_table.find("thead", recursive=False) is None and _is_genealogy_table_header(source_table) and rows:
        rows = rows[1:]
    for row in rows:
        base_tbody.append(_clone_genealogy_row(row, col_count, soup))


def _preserve_figure_and_image_attrs(original_html: str, merged_html: str) -> str:
    original_soup = BeautifulSoup(original_html or "", "html.parser")
    merged_soup = BeautifulSoup(merged_html or "", "html.parser")

    original_imgs = original_soup.find_all("img")
    merged_imgs = merged_soup.find_all("img")
    if len(original_imgs) != len(merged_imgs):
        return merged_html

    for original_img, merged_img in zip(original_imgs, merged_imgs):
        merged_img.attrs = dict(original_img.attrs)

        original_parent = original_img.parent
        merged_parent = merged_img.parent
        if getattr(original_parent, "name", None) == "figure" and getattr(merged_parent, "name", None) == "figure":
            merged_parent.attrs = dict(original_parent.attrs)

    return merged_soup.decode_contents()


def merge_contiguous_genealogy_tables(html: str, *, rescue_normalizer: Optional[Any] = None) -> str:
    if "<table" not in (html or "").lower():
        return html or ""

    normalizer = rescue_normalizer
    if normalizer is None:
        normalizer = _normalize_genealogy_rescue_html

    normalized = html or ""
    if normalizer is not None:
        normalized = normalizer(normalized)

    soup = BeautifulSoup(normalized, "html.parser")
    _convert_genealogy_name_list_paragraphs_to_tables(soup)
    for table in list(soup.find_all("table")):
        _normalize_genealogy_table_head(table, soup)
    for base_table in list(soup.find_all("table")):
        if base_table.parent is None or not _is_genealogy_table_header(base_table):
            continue

        _absorb_leading_genealogy_headings(base_table, soup)
        expected_cols = _genealogy_table_column_count(base_table)
        cursor = base_table
        pending_heading_nodes: List[Any] = []
        pending_heading_lines: List[str] = []

        while True:
            next_node = _next_significant_sibling(cursor)
            if next_node is None:
                break
            lines = _genealogy_heading_lines_from_node(next_node)
            if lines:
                pending_heading_nodes.append(next_node)
                pending_heading_lines.extend(lines)
                cursor = next_node
                continue
            if (
                getattr(next_node, "name", None) == "table"
                and not pending_heading_lines
                and _is_compatible_genealogy_table(next_node, expected_cols)
                and _looks_like_genealogy_continuation_table(next_node)
            ):
                _append_genealogy_heading_and_rows(base_table, [], next_node, soup)
                next_node.decompose()
                cursor = base_table
                continue
            if getattr(next_node, "name", None) == "table" and pending_heading_lines and _is_compatible_genealogy_table(next_node, expected_cols):
                _append_genealogy_heading_lines_and_rows(base_table, pending_heading_lines, next_node, soup)
                for heading in pending_heading_nodes:
                    heading.extract()
                pending_heading_nodes = []
                pending_heading_lines = []
                next_node.decompose()
                cursor = base_table
                continue
            break

    for table in soup.find_all("table"):
        if _is_genealogy_table_header(table):
            _normalize_genealogy_body_rows(table, soup)

    return _preserve_figure_and_image_attrs(html, soup.decode_contents())


def merge_genealogy_tables_preserving_headings(html: str) -> str:
    """Merge fragmented genealogy tables after normalizing summary blocks.

    The older fragment-preserving behavior kept generic generation headings
    (`Grandchildren`, `Great Grandchildren`, `... FAMILY`) outside the merged
    table, which regressed the reviewed Onward goldens into many small tables.
    Keep the build entrypoint stable, but delegate to the contiguous merge so
    those headings become inspectable subgroup rows inside the final table.
    """
    if "<table" not in (html or "").lower() and "<dl" not in (html or "").lower():
        return html or ""

    normalized = _convert_definition_lists_to_tables(html or "")
    return merge_contiguous_genealogy_tables(normalized)
