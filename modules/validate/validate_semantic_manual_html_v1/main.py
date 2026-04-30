#!/usr/bin/env python3
"""Conformance checks for graphics-heavy manual semantic HTML runs."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from modules.common.utils import ProgressLogger, read_jsonl, save_json


MODULE_ID = "validate_semantic_manual_html_v1"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _status(ok: bool, *, warning: bool = False) -> str:
    if ok:
        return "pass"
    return "warn" if warning else "fail"


def _check(checks: list[dict[str, Any]], check_id: str, description: str, ok: bool, *, warning: bool = False, detail: Any = None) -> None:
    checks.append(
        {
            "id": check_id,
            "description": description,
            "status": _status(ok, warning=warning),
            "detail": detail,
        }
    )


def _count_figures(html_files: list[Path]) -> dict[str, int]:
    figure_count = 0
    img_with_src_count = 0
    for path in html_files:
        if not path.exists():
            continue
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        figure_count += len(soup.find_all("figure"))
        img_with_src_count += len([tag for tag in soup.find_all("img") if tag.get("src")])
    return {"figure_count": figure_count, "img_with_src_count": img_with_src_count}


_REQUIRED_SOURCE_PIXEL_CROP_ROLES = {
    "board_element",
    "card_face",
    "card_reference",
    "component_reference",
    "icon_reference",
    "map_or_board",
    "rule_example_diagram",
    "setup_diagram",
}


def _role_from_crop(crop: dict[str, Any]) -> str:
    return str(crop.get("critical_graphics_role") or crop.get("role") or "")


def _importance_from_crop(crop: dict[str, Any]) -> str:
    return str(crop.get("critical_graphics_importance") or crop.get("importance") or "").casefold()


def _used_crop_filenames(html_files: list[Path]) -> set[str]:
    used: set[str] = set()
    for path in html_files:
        if not path.exists():
            continue
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for img in soup.find_all("img"):
            filename = img.get("data-crop-filename")
            if filename:
                used.add(str(filename))
                continue
            src = img.get("src") or ""
            if src:
                used.add(Path(src).name)
    return used


def _html_crop_usage_checks(*, crops: list[dict[str, Any]], html_files: list[Path]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    used = _used_crop_filenames(html_files)
    required = []
    missing = []
    for crop in crops:
        filename = crop.get("filename")
        if not filename:
            continue
        role = _role_from_crop(crop)
        if _importance_from_crop(crop) != "essential" or role not in _REQUIRED_SOURCE_PIXEL_CROP_ROLES:
            continue
        detail = {
            "filename": filename,
            "page": crop.get("source_page"),
            "role": role,
            "description": crop.get("image_description") or crop.get("alt"),
        }
        required.append(detail)
        if filename not in used:
            missing.append(detail)

    _check(
        checks,
        "essential_source_pixel_crops_referenced_in_html",
        "Final HTML references essential source-pixel crops for roles that cannot be replaced by plain text.",
        not missing,
        detail={
            "required_count": len(required),
            "referenced_count": len(required) - len(missing),
            "missing": missing[:20],
        },
    )
    return checks


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _title_key(text: str) -> str:
    text = _normalize_ws(text).casefold()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", " ", text).strip()


_CATEGORY_WORDS = {
    "actions",
    "catalog",
    "card",
    "cards",
    "component",
    "components",
    "contents",
    "course",
    "courses",
    "element",
    "elements",
    "examples",
    "index",
    "overview",
    "phase",
    "phases",
    "reference",
    "references",
    "route",
    "routes",
    "rules",
    "setup",
    "summary",
    "upgrade",
    "upgrades",
    "variants",
}

_CATALOG_PARENT_CUES = (
    "following page",
    "following pages",
    "list of",
    "detailed look",
    "different types",
    "types of",
    "description of each",
    "descriptions will",
    "reference",
)

_CATALOG_TOKEN_STOPWORDS = {
    "and",
    "card",
    "cards",
    "course",
    "courses",
    "index",
    "section",
    "sections",
    "the",
}

_PROCEDURAL_PARENT_TITLE_CUES = (
    "how to",
    "how-to",
    "playing",
    "play",
    "round",
    "rules",
    "turn",
)

_PROCEDURAL_PARENT_TEXT_CUES = (
    "following page",
    "following pages",
    "next page",
    "description of each",
    "full round",
    "phase",
    "phases",
)

_PROCEDURAL_CHILD_TERMS = {
    "activation",
    "activating",
    "order",
    "phase",
    "playing",
    "programming",
    "register",
    "round",
    "summary",
    "turn",
    "upgrade",
}


def _looks_like_category_heading(text: str) -> bool:
    key = _title_key(text)
    if not key:
        return False
    tokens = key.split()
    if any(token in _CATEGORY_WORDS for token in tokens):
        return True
    return bool(":" in text and any(token.rstrip(":") in _CATEGORY_WORDS for token in tokens[:3]))


def _singular_token(token: str) -> str:
    token = token.strip().casefold()
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def _title_terms(text: str, *, include_category_terms: bool = False) -> set[str]:
    terms = set()
    for token in _title_key(text).split():
        singular = _singular_token(token)
        if include_category_terms and singular in {"card", "course"}:
            terms.add(singular)
            continue
        if len(singular) < 4 or singular in _CATALOG_TOKEN_STOPWORDS:
            continue
        terms.add(singular)
    return terms


def _page_text(row: dict[str, Any] | None) -> str:
    if not row:
        return ""
    soup = BeautifulSoup(row.get("html") or row.get("raw_html") or "", "html.parser")
    return _normalize_ws(soup.get_text(" ", strip=True))


def _looks_like_catalog_parent_page(title: str, row: dict[str, Any] | None) -> bool:
    if not _looks_like_category_heading(title):
        return False
    text = _page_text(row).casefold()
    return any(cue in text for cue in _CATALOG_PARENT_CUES)


def _looks_like_procedural_parent_page(title: str, row: dict[str, Any] | None) -> bool:
    key = _title_key(title)
    if not key or not any(cue in key for cue in _PROCEDURAL_PARENT_TITLE_CUES):
        return False
    text = _page_text(row).casefold()
    return any(cue in text for cue in _PROCEDURAL_PARENT_TEXT_CUES)


def _looks_like_procedural_subheading(
    *,
    parent_title: str,
    promoted: str,
    parent_row: dict[str, Any] | None,
    chapter_soup: BeautifulSoup | None,
) -> bool:
    if not _looks_like_procedural_parent_page(parent_title, parent_row):
        return False
    if not (_title_terms(promoted, include_category_terms=True) & _PROCEDURAL_CHILD_TERMS):
        return False
    return bool(
        chapter_soup
        and any(
            _title_key(tag.get_text(" ", strip=True)) == _title_key(promoted)
            for tag in chapter_soup.find_all(re.compile(r"^h[1-6]$"))
        )
    )


def _catalog_fragmentation_issues(
    *,
    pages: list[dict[str, Any]],
    chapters: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pages_by_number = {
        row.get("page_number") or row.get("page"): row
        for row in pages
        if isinstance(row.get("page_number") or row.get("page"), int)
    }
    issues = []
    for idx, chapter in enumerate(chapters[:-1]):
        source_pages = chapter.get("source_pages") or []
        if not source_pages:
            continue
        title = _normalize_ws(chapter.get("title") or "")
        if not _looks_like_catalog_parent_page(title, pages_by_number.get(source_pages[0])):
            continue
        parent_terms = _title_terms(title, include_category_terms=True)
        next_chapter = chapters[idx + 1]
        child_title = _normalize_ws(next_chapter.get("title") or "")
        child_terms = _title_terms(child_title, include_category_terms=True)
        if parent_terms and parent_terms & child_terms:
            issues.append(
                {
                    "chapter_title": title,
                    "chapter_source_pages": source_pages,
                    "next_chapter_title": child_title,
                    "next_chapter_source_pages": next_chapter.get("source_pages") or [],
                    "reason": "catalog_subsection_promoted_to_sibling_chapter",
                }
            )
    return issues


def _next_text_until_heading(tag, *, max_chars: int = 280) -> str:
    parts = []
    for sibling in tag.next_siblings:
        name = getattr(sibling, "name", None)
        if name and re.fullmatch(r"h[1-6]", name.lower()):
            break
        text = _normalize_ws(
            sibling.get_text(" ", strip=True) if hasattr(sibling, "get_text") else str(sibling)
        )
        if text:
            parts.append(text)
        if sum(len(part) for part in parts) >= max_chars:
            break
    return _normalize_ws(" ".join(parts))[:max_chars]


def _looks_like_label_value_entry(text: str) -> bool:
    labels = re.findall(r"\b[A-Z][A-Za-z0-9 /&-]{1,28}:", text or "")
    return len({label.casefold() for label in labels}) >= 2


def _item_heading_boundary_issues(*, pages: list[dict[str, Any]], chapters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pages_by_number = {
        row.get("page_number") or row.get("page"): row
        for row in pages
        if isinstance(row.get("page_number") or row.get("page"), int)
    }
    issues = []
    for chapter in chapters:
        source_pages = chapter.get("source_pages") or []
        if not source_pages:
            continue
        first_page = source_pages[0]
        page = pages_by_number.get(first_page)
        title = _normalize_ws(chapter.get("title") or "")
        if not page or not title:
            continue
        soup = BeautifulSoup(page.get("html") or "", "html.parser")
        title_key = _title_key(title)
        if any(_title_key(tag.get_text(" ", strip=True)) == title_key for tag in soup.find_all("h1")):
            continue
        for tag in soup.find_all(["h2", "h3", "h4", "h5", "h6"]):
            text = _normalize_ws(tag.get_text(" ", strip=True))
            if _title_key(text) != title_key:
                continue
            if not _looks_like_category_heading(text) and _looks_like_label_value_entry(_next_text_until_heading(tag)):
                issues.append(
                    {
                        "chapter_title": title,
                        "source_page": first_page,
                        "source_pages": source_pages,
                        "heading_tag": tag.name,
                        "reason": "lower_level_item_heading_started_chapter",
                    }
                )
            break
    return issues


def _significant_sibling(node, *, direction: str):
    from bs4 import NavigableString

    sibling = node.next_sibling if direction == "next" else node.previous_sibling
    while sibling is not None:
        if isinstance(sibling, NavigableString):
            if sibling.strip():
                return None
            sibling = sibling.next_sibling if direction == "next" else sibling.previous_sibling
            continue
        return sibling
    return None


def _leading_label_text(tag) -> str:
    if getattr(tag, "name", None) in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return _normalize_ws(tag.get_text(" ", strip=True))
    if getattr(tag, "name", None) == "p":
        strong = tag.find("strong")
        if strong:
            return _normalize_ws(strong.get_text(" ", strip=True))
        return _normalize_ws(tag.get_text(" ", strip=True)).split(".", 1)[0]
    return ""


def _reference_entry_candidate_count(html: str) -> int:
    soup = BeautifulSoup(html or "", "html.parser")
    count = 0
    for paragraph in soup.find_all("p"):
        children = list(paragraph.contents)
        first_strong_idx = None
        for idx, child in enumerate(children):
            name = getattr(child, "name", None)
            if name == "strong":
                first_strong_idx = idx
                break
            if name is None and not str(child).strip():
                continue
            first_strong_idx = None
            break
        if first_strong_idx is None:
            continue
        term = _normalize_ws(children[first_strong_idx].get_text(" ", strip=True))
        if not term or term.endswith(":") or len(term.split()) > 6:
            continue
        letters = [char for char in term if char.isalpha()]
        if letters and sum(1 for char in letters if char.isupper()) / len(letters) < 0.7:
            continue
        if len(_normalize_ws(paragraph.get_text(" ", strip=True))) < len(term) + 8:
            continue
        count += 1
    for figure in soup.find_all("figure"):
        sibling = _significant_sibling(figure, direction="next")
        if getattr(sibling, "name", None) != "p":
            continue
        label = _normalize_ws(sibling.get_text(" ", strip=True))
        key = _title_key(label)
        if not key or len(label) > 80 or len(key.split()) > 6:
            continue
        letters = [char for char in label if char.isalpha()]
        if not letters or sum(1 for char in letters if char.isupper()) / len(letters) < 0.7:
            continue
        desc = _significant_sibling(sibling, direction="next")
        if getattr(desc, "name", None) == "p" and len(_normalize_ws(desc.get_text(" ", strip=True))) >= 8:
            count += 1
    return count


_CATALOG_ENTRY_FIGURE_ROLES = {
    "card_face",
    "component_reference",
    "icon_reference",
    "map_or_board",
    "setup_diagram",
}


def _is_catalog_entry_figure(tag: Any) -> bool:
    if getattr(tag, "name", None) != "figure":
        return False
    role = str(tag.get("data-critical-graphics-role") or "")
    if role == "card_reference":
        return False
    if role in _CATALOG_ENTRY_FIGURE_ROLES:
        return True
    img = tag.find("img")
    alt = img.get("alt") if img else ""
    lowered = str(alt or "").casefold()
    return bool(
        _looks_like_label_value_entry(str(alt or ""))
        and any(word in lowered for word in ("card", "course", "map", "reference", "component"))
    )


def _compact_catalog_label(text: str) -> bool:
    text = _normalize_ws(text)
    if not text or len(text) > 90 or text.endswith(":"):
        return False
    if _looks_like_label_value_entry(text):
        return False
    if len(_title_key(text).split()) > 8:
        return False
    if re.search(r"[.!?]", text):
        return False
    letters = [char for char in text if char.isalpha()]
    return bool(letters and len(letters) / max(1, len(text)) >= 0.45)


def _catalog_label_from_node(tag: Any) -> str:
    name = getattr(tag, "name", None)
    if name == "dt":
        text = _normalize_ws(tag.get_text(" ", strip=True))
        return text if _compact_catalog_label(text) else ""
    if name in {"h3", "h4", "h5", "h6"}:
        text = _normalize_ws(tag.get_text(" ", strip=True))
        return text if _compact_catalog_label(text) else ""
    if name == "p":
        text = _normalize_ws(tag.get_text(" ", strip=True))
        strong = tag.find("strong", recursive=False)
        strong_text = _normalize_ws(strong.get_text(" ", strip=True)) if strong else ""
        if strong_text and _title_key(text) == _title_key(strong_text) and _compact_catalog_label(strong_text):
            return strong_text
        key = _title_key(text)
        letters = [char for char in text if char.isalpha()]
        if key and len(key.split()) <= 6 and letters and sum(1 for char in letters if char.isupper()) / len(letters) >= 0.7:
            return text
    if name == "dl" and "semantic-entry-list" in (tag.get("class") or []):
        dt = tag.find("dt", recursive=False)
        text = _normalize_ws(dt.get_text(" ", strip=True)) if dt else ""
        return text if _compact_catalog_label(text) else ""
    return ""


def _is_catalog_metadata_node(tag: Any) -> bool:
    name = getattr(tag, "name", None)
    if name in {"dd", "p"}:
        return _looks_like_label_value_entry(tag.get_text(" ", strip=True))
    if name == "dl" and "semantic-entry-list" in (tag.get("class") or []):
        dd = tag.find("dd", recursive=False)
        return bool(dd and _looks_like_label_value_entry(dd.get_text(" ", strip=True)))
    return False


def _catalog_figure_has_entry_neighbors(figure: Any) -> bool:
    prev_tag = _significant_sibling(figure, direction="previous")
    next_tag = _significant_sibling(figure, direction="next")
    if _catalog_label_from_node(prev_tag):
        return getattr(prev_tag, "name", None) == "dl" or _is_catalog_metadata_node(next_tag)
    if not _catalog_label_from_node(next_tag):
        return False
    return getattr(next_tag, "name", None) == "dl" or _is_catalog_metadata_node(_significant_sibling(next_tag, direction="next"))


def _dl_pairs(dl: Any) -> list[tuple[Any, Any]]:
    pairs = []
    children = [child for child in dl.children if getattr(child, "name", None)]
    idx = 0
    while idx < len(children):
        dt = children[idx]
        dd = children[idx + 1] if idx + 1 < len(children) else None
        if getattr(dt, "name", None) == "dt" and getattr(dd, "name", None) == "dd":
            pairs.append((dt, dd))
            idx += 2
            continue
        return []
    return pairs


def _catalog_entry_grouping_issues(*, pages: list[dict[str, Any]], chapters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pages_by_number = {
        row.get("page_number") or row.get("page"): row
        for row in pages
        if isinstance(row.get("page_number") or row.get("page"), int)
    }
    issues = []
    for chapter in chapters:
        source_pages = chapter.get("source_pages") or []
        if not source_pages:
            continue
        title = _normalize_ws(chapter.get("title") or "")
        if not _looks_like_catalog_parent_page(title, pages_by_number.get(source_pages[0])):
            continue
        file_path = chapter.get("file")
        if not file_path or not Path(file_path).exists():
            continue
        soup = BeautifulSoup(Path(file_path).read_text(encoding="utf-8"), "html.parser")
        for dl in soup.find_all("dl"):
            if dl.find_parent("section", class_="semantic-catalog-entry"):
                continue
            for dt, dd in _dl_pairs(dl):
                figure = next((fig for fig in dd.find_all("figure") if _is_catalog_entry_figure(fig)), None)
                if figure is None:
                    continue
                if not _catalog_label_from_node(dt) or not _is_catalog_metadata_node(dd):
                    continue
                img = figure.find("img")
                issues.append(
                    {
                        "chapter_title": title,
                        "file": file_path,
                        "source_pages": source_pages,
                        "crop": img.get("data-crop-filename") if img else None,
                        "reason": "catalog_entry_figure_embedded_in_definition_list",
                    }
                )
        for figure in soup.find_all("figure"):
            if figure.find_parent("section", class_="semantic-catalog-entry"):
                continue
            if not _is_catalog_entry_figure(figure) or not _catalog_figure_has_entry_neighbors(figure):
                continue
            img = figure.find("img")
            issues.append(
                {
                    "chapter_title": title,
                    "file": file_path,
                    "source_pages": source_pages,
                    "crop": img.get("data-crop-filename") if img else None,
                    "reason": "catalog_entry_figure_not_grouped_with_label_and_metadata",
                }
            )
    return issues


def _html_files_from_chapters(chapters: list[dict[str, Any]]) -> list[Path]:
    files = []
    for row in chapters:
        file_path = row.get("file")
        if file_path:
            files.append(Path(file_path))
    return files


def _chapter_for_source_page(chapters: list[dict[str, Any]], page: int) -> dict[str, Any] | None:
    for row in chapters:
        if page in (row.get("source_pages") or []):
            return row
    return None


def _semantic_fidelity_checks(
    *,
    pages: list[dict[str, Any]],
    chapters: list[dict[str, Any]],
    html_files: list[Path],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    nav_issues = []
    unresolved_imgs = []
    running_head_leaks = []
    duplicate_caption_labels = []
    reference_pages_needing_structure = []
    reference_pages_structured = []
    item_boundary_issues = _item_heading_boundary_issues(pages=pages, chapters=chapters)
    catalog_fragmentation_issues = _catalog_fragmentation_issues(pages=pages, chapters=chapters)
    catalog_entry_grouping_issues = _catalog_entry_grouping_issues(pages=pages, chapters=chapters)

    for path in html_files:
        if not path.exists():
            continue
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for nav in soup.select("nav.chapter-nav"):
            if nav.get("data-doc-web-ui-chrome") != "navigation":
                nav_issues.append({"file": str(path), "reason": "unmarked_navigation"})
                continue
            if nav.find_parent("article"):
                nav_issues.append({"file": str(path), "reason": "navigation_inside_article"})
        for tag in soup.find_all(class_="running-head"):
            running_head_leaks.append({"file": str(path), "text": tag.get_text(" ", strip=True)})
        for img in soup.find_all("img"):
            if not img.get("src"):
                unresolved_imgs.append({"file": str(path), "alt": img.get("alt")})
        for figure in soup.find_all("figure"):
            caption = figure.find("figcaption")
            caption_text = _normalize_ws(caption.get_text(" ", strip=True)) if caption else ""
            if not caption_text:
                continue
            caption_key = _title_key(caption_text)
            for sibling in (
                _significant_sibling(figure, direction="previous"),
                _significant_sibling(figure, direction="next"),
            ):
                label_key = _title_key(_leading_label_text(sibling))
                if caption_key and label_key and caption_key == label_key:
                    duplicate_caption_labels.append({"file": str(path), "caption": caption_text})
                    break

    chapter_soups: dict[str, BeautifulSoup] = {}
    for row in chapters:
        file_path = row.get("file")
        if file_path and Path(file_path).exists():
            chapter_soups[file_path] = BeautifulSoup(Path(file_path).read_text(encoding="utf-8"), "html.parser")
    pages_by_number = {
        row.get("page_number") or row.get("page"): row
        for row in pages
        if isinstance(row.get("page_number") or row.get("page"), int)
    }

    promoted_boundary_issues = []
    for row in pages:
        page_html = row.get("html") or ""
        page_soup = BeautifulSoup(page_html, "html.parser")
        promoted_tags = page_soup.find_all(attrs={"data-normalized-from": "running-head"})
        if not promoted_tags:
            continue
        promoted = _normalize_ws(promoted_tags[0].get_text(" ", strip=True))
        page = row.get("page_number") or row.get("page")
        if not promoted or not isinstance(page, int):
            continue
        chapter = _chapter_for_source_page(chapters, page)
        if not chapter:
            promoted_boundary_issues.append({"page": page, "heading": promoted, "reason": "no_chapter_for_source_page"})
            continue
        source_pages = chapter.get("source_pages") or []
        title = chapter.get("title") or ""
        is_matching_boundary = bool(source_pages and source_pages[0] == page and _title_key(title) == _title_key(promoted))
        chapter_soup = chapter_soups.get(chapter.get("file") or "")
        is_catalog_subheading = bool(
            source_pages
            and _looks_like_catalog_parent_page(title, pages_by_number.get(source_pages[0]))
            and chapter_soup
            and any(
                _title_key(tag.get_text(" ", strip=True)) == _title_key(promoted)
                for tag in chapter_soup.find_all(re.compile(r"^h[1-6]$"))
            )
        )
        is_procedural_subheading = bool(
            source_pages
            and _looks_like_procedural_subheading(
                parent_title=title,
                promoted=promoted,
                parent_row=pages_by_number.get(source_pages[0]),
                chapter_soup=chapter_soup,
            )
        )
        if not is_matching_boundary and not is_catalog_subheading and not is_procedural_subheading:
            promoted_boundary_issues.append(
                {
                    "page": page,
                    "heading": promoted,
                    "chapter_title": title,
                    "chapter_source_pages": source_pages,
                }
            )

    for row in pages:
        page = row.get("page_number") or row.get("page")
        if not isinstance(page, int):
            continue
        if _reference_entry_candidate_count(row.get("html") or "") < 3:
            continue
        chapter = _chapter_for_source_page(chapters, page)
        if not chapter:
            continue
        source_pages = chapter.get("source_pages") or []
        file_path = chapter.get("file")
        soup = chapter_soups.get(file_path or "")
        structured = bool(
            soup
            and (
                soup.find("dl", class_="semantic-entry-list")
                or soup.find("section", class_="semantic-catalog-entry")
                or soup.find("table")
            )
        )
        detail = {"page": page, "chapter": file_path, "source_pages": source_pages}
        if structured:
            reference_pages_structured.append(detail)
        else:
            reference_pages_needing_structure.append(detail)

    _check(
        checks,
        "generated_navigation_marked_ui_chrome",
        "Generated previous/index/next navigation is explicit UI chrome outside semantic article content.",
        not nav_issues,
        detail={"issues": nav_issues[:10], "count": len(nav_issues)},
    )
    _check(
        checks,
        "no_running_head_chrome_leaks",
        "Source running-head chrome is promoted to true headings or removed before final HTML.",
        not running_head_leaks,
        detail={"leaks": running_head_leaks[:10], "count": len(running_head_leaks)},
    )
    _check(
        checks,
        "no_unresolved_image_placeholders",
        "Final HTML contains no <img> placeholders without a resolved src.",
        not unresolved_imgs,
        detail={"unresolved": unresolved_imgs[:10], "count": len(unresolved_imgs)},
    )
    _check(
        checks,
        "promoted_running_heads_become_boundaries",
        "Promoted page-level section headings start matching chapter entries.",
        not promoted_boundary_issues,
        detail={"issues": promoted_boundary_issues[:10], "count": len(promoted_boundary_issues)},
    )
    _check(
        checks,
        "lower_item_headings_do_not_start_chapters",
        "Lower-level catalog/reference item headings with label/value metadata remain inside their parent section.",
        not item_boundary_issues,
        detail={"issues": item_boundary_issues[:10], "count": len(item_boundary_issues)},
    )
    _check(
        checks,
        "catalog_subsections_stay_with_parent",
        "Catalog/index subsection headings stay inside their source parent section instead of becoming sibling chapters.",
        not catalog_fragmentation_issues,
        detail={"issues": catalog_fragmentation_issues[:10], "count": len(catalog_fragmentation_issues)},
    )
    _check(
        checks,
        "catalog_entries_group_figures_labels_and_metadata",
        "Catalog/index entry figures with nearby labels and label/value metadata are grouped into semantic entry sections.",
        not catalog_entry_grouping_issues,
        detail={"issues": catalog_entry_grouping_issues[:10], "count": len(catalog_entry_grouping_issues)},
    )
    _check(
        checks,
        "no_adjacent_duplicate_figure_captions",
        "Figure captions do not duplicate adjacent headings or entry labels.",
        not duplicate_caption_labels,
        detail={"duplicates": duplicate_caption_labels[:10], "count": len(duplicate_caption_labels)},
    )
    _check(
        checks,
        "reference_entries_structured",
        "Dense card/reference entry pages use tables or definition lists instead of flat paragraphs.",
        not reference_pages_needing_structure,
        detail={
            "structured": reference_pages_structured[:10],
            "unstructured": reference_pages_needing_structure[:10],
            "structured_count": len(reference_pages_structured),
            "unstructured_count": len(reference_pages_needing_structure),
        },
    )
    return checks


def _role_sample_pages(plan: dict[str, Any]) -> dict[str, int | None]:
    roles = {
        "setup": None,
        "rule_example": None,
        "map_or_board": None,
        "card_or_reference": None,
        "summary": None,
    }

    def fill(role: str, page: int) -> None:
        if role == "setup_diagram" and roles["setup"] is None:
            roles["setup"] = page
        elif role == "rule_example_diagram" and roles["rule_example"] is None:
            roles["rule_example"] = page
        elif role == "map_or_board" and roles["map_or_board"] is None:
            roles["map_or_board"] = page
        elif role == "card_or_reference" and roles["card_or_reference"] is None:
            roles["card_or_reference"] = page
        elif role == "summary_reference" and roles["summary"] is None:
            roles["summary"] = page

    page_records = plan.get("pages", [])
    for require_figures in (True, False):
        for page_record in page_records:
            page = page_record.get("page_number")
            if not isinstance(page, int):
                continue
            figure_count = int(page_record.get("figure_placeholder_count") or 0)
            if require_figures and figure_count == 0:
                continue
            page_roles = set(page_record.get("page_roles") or [])
            for role in page_roles:
                fill(role, page)
    for item in plan.get("plan_items", []):
        role = item.get("role")
        page = item.get("source_page_number")
        if isinstance(page, int):
            fill(role, page)
    return roles


def _intersection_area(a: dict[str, Any], b: dict[str, Any]) -> int:
    try:
        ax0, ay0, ax1, ay1 = int(a["x0"]), int(a["y0"]), int(a["x1"]), int(a["y1"])
        bx0, by0, bx1, by1 = int(b["x0"]), int(b["y0"]), int(b["x1"]), int(b["y1"])
    except (KeyError, TypeError, ValueError):
        return 0
    ix0 = max(ax0, bx0)
    iy0 = max(ay0, by0)
    ix1 = min(ax1, bx1)
    iy1 = min(ay1, by1)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0
    return (ix1 - ix0) * (iy1 - iy0)


def _critical_graphics_checks(
    *,
    critical_manifest: dict[str, Any],
    crops: list[dict[str, Any]],
    min_target_crop_coverage: float,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    summary = critical_manifest.get("summary") or {}
    planned_targets = []
    for page in critical_manifest.get("pages", []):
        if not isinstance(page, dict):
            continue
        page_number = page.get("page_number")
        for target in page.get("targets", []):
            if not isinstance(target, dict):
                continue
            if target.get("importance") == "decorative":
                continue
            if not isinstance(target.get("bbox_pixels"), dict):
                continue
            if target.get("source_page_number") is None and isinstance(page_number, int):
                target = {**target, "source_page_number": page_number}
            planned_targets.append(target)

    manifest_target_count = int(summary.get("target_count") or 0)
    if manifest_target_count == 0:
        manifest_target_count = sum(
            len(page.get("targets") or [])
            for page in critical_manifest.get("pages", [])
            if isinstance(page, dict)
        )
    _check(
        checks,
        "critical_graphics_manifest_present",
        "SOTA visual-planner manifest exists and records non-decorative target decisions.",
        bool(critical_manifest) and manifest_target_count > 0,
        detail=summary,
    )

    crops_by_page: dict[int, list[dict[str, Any]]] = {}
    for crop in crops:
        page = crop.get("source_page")
        if isinstance(page, int):
            crops_by_page.setdefault(page, []).append(crop)

    misses = []
    matches = []
    for target in planned_targets:
        target_bbox = target.get("bbox_pixels") or {}
        target_area = int(target_bbox.get("width") or 0) * int(target_bbox.get("height") or 0)
        if target_area <= 0:
            continue
        page = target.get("source_page_number")
        target_id = str(target.get("target_id") or "")
        split_crops = [
            crop
            for crop in crops_by_page.get(page, [])
            if target_id and str(crop.get("critical_graphics_target_id") or "").startswith(f"{target_id}-")
        ]
        if split_crops and str(target.get("role") or "") in {
            "card_reference",
            "component_reference",
            "icon_reference",
            "rule_example_diagram",
        }:
            aggregate_coverage = sum(
                _intersection_area(target_bbox, crop.get("bbox") or {}) / float(target_area)
                for crop in split_crops
                if isinstance(crop.get("bbox"), dict)
            )
            detail = {
                "target_id": target.get("target_id"),
                "page": page,
                "role": target.get("role"),
                "description": target.get("description"),
                "split_crop_count": len(split_crops),
                "coverage": round(min(1.0, aggregate_coverage), 3),
                "coverage_mode": "split_reference_children",
            }
            if len(split_crops) >= 2 and aggregate_coverage >= 0.2:
                matches.append(detail)
                continue
        best = 0.0
        best_crop = None
        for crop in crops_by_page.get(page, []):
            crop_bbox = crop.get("bbox")
            if not isinstance(crop_bbox, dict):
                continue
            coverage = _intersection_area(target_bbox, crop_bbox) / float(target_area)
            if coverage > best:
                best = coverage
                best_crop = crop.get("filename")
        detail = {
            "target_id": target.get("target_id"),
            "page": page,
            "role": target.get("role"),
            "description": target.get("description"),
            "best_crop": best_crop,
            "coverage": round(best, 3),
        }
        if best >= min_target_crop_coverage:
            matches.append(detail)
        else:
            misses.append(detail)

    _check(
        checks,
        "critical_graphics_crop_coverage",
        "Non-decorative visual-planner targets with bboxes are covered by emitted source-pixel crops.",
        bool(planned_targets) and not misses,
        warning=True,
        detail={
            "non_decorative_targets_with_bbox": len(planned_targets),
            "matched": len(matches),
            "misses": misses[:10],
            "minimum_target_coverage": min_target_crop_coverage,
        },
    )
    return checks


def build_report(
    *,
    pages_path: Path,
    logical_pages_path: Path,
    figure_plan_path: Path,
    critical_graphics_manifest_path: Path | None,
    crops_path: Path,
    chapters_path: Path,
    run_id: str | None,
    min_figure_crop_ratio: float,
    min_critical_target_crop_coverage: float,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    pages = list(read_jsonl(str(pages_path))) if pages_path.exists() else []
    logical_pages = list(read_jsonl(str(logical_pages_path))) if logical_pages_path.exists() else []
    logical_map_path = logical_pages_path.parent / "logical_page_map.json"
    logical_map = _read_json(logical_map_path) if logical_map_path.exists() else {}
    plan = _read_json(figure_plan_path) if figure_plan_path.exists() else {}
    critical_manifest = (
        _read_json(critical_graphics_manifest_path)
        if critical_graphics_manifest_path and critical_graphics_manifest_path.exists()
        else {}
    )
    crops = list(read_jsonl(str(crops_path))) if crops_path.exists() else []
    chapters = list(read_jsonl(str(chapters_path))) if chapters_path.exists() else []
    html_files = _html_files_from_chapters(chapters)
    figure_counts = _count_figures(html_files)

    logical_summary = logical_map.get("summary") or {}
    _check(
        checks,
        "logical_page_map_complete",
        "Logical page map has no missing/duplicate pages or unresolved mapping issues.",
        bool(logical_summary.get("complete")) and int(logical_summary.get("issues_count") or 0) == 0,
        detail=logical_summary,
    )
    _check(
        checks,
        "ordered_manifest_matches_map",
        "Ordered page manifest row count matches logical page map count.",
        len(logical_pages) == int(logical_summary.get("inferred_logical_page_count") or -1),
        detail={"logical_manifest_rows": len(logical_pages), "map_count": logical_summary.get("inferred_logical_page_count")},
    )
    empty_html_pages = [row.get("page_number") for row in pages if not (row.get("html") or "").strip()]
    _check(
        checks,
        "page_html_coverage",
        "OCR HTML has one non-empty row per logical page.",
        len(pages) == len(logical_pages) and not empty_html_pages,
        detail={"page_html_rows": len(pages), "ordered_page_rows": len(logical_pages), "empty_html_pages": empty_html_pages},
    )

    plan_summary = plan.get("summary") or {}
    preserve_count = int(plan_summary.get("preserve_as_figure_count") or 0)
    crop_count = len(crops)
    crop_ratio = crop_count / preserve_count if preserve_count else 1.0
    _check(
        checks,
        "essential_graphics_plan_present",
        "Essential graphics plan exists and records preserve-as-figure decisions.",
        figure_plan_path.exists() and preserve_count > 0,
        detail=plan_summary,
    )
    _check(
        checks,
        "figure_crop_coverage",
        "Cropped/source-bbox assets cover enough preserve-as-figure decisions for this candidate run.",
        crop_ratio >= min_figure_crop_ratio,
        warning=True,
        detail={"crop_count": crop_count, "preserve_as_figure_count": preserve_count, "ratio": round(crop_ratio, 3), "minimum_ratio": min_figure_crop_ratio},
    )
    crops_with_bbox = [
        row.get("filename")
        for row in crops
        if row.get("bbox")
    ]
    _check(
        checks,
        "crop_bbox_presence",
        "Every emitted crop has a bbox/source location.",
        bool(crops) and len(crops_with_bbox) == len(crops),
        warning=True,
        detail={"crops": len(crops), "with_bbox": len(crops_with_bbox)},
    )

    manifest_path = html_files[0].parent / "manifest.json" if html_files else None
    provenance_path = html_files[0].parent / "provenance" / "blocks.jsonl" if html_files else None
    provenance_rows = list(read_jsonl(str(provenance_path))) if provenance_path and provenance_path.exists() else []
    _check(
        checks,
        "final_html_bundle_exists",
        "Final HTML bundle files and manifest exist.",
        bool(html_files) and all(path.exists() for path in html_files) and bool(manifest_path and manifest_path.exists()),
        detail={"html_files": [str(path) for path in html_files[:5]], "manifest": str(manifest_path) if manifest_path else None},
    )
    _check(
        checks,
        "html_figures_attached",
        "Final HTML contains figure tags with image sources when crops were emitted.",
        figure_counts["figure_count"] > 0 and figure_counts["img_with_src_count"] > 0,
        warning=True,
        detail=figure_counts,
    )
    _check(
        checks,
        "provenance_blocks_exist",
        "Block-level provenance exists for final HTML output.",
        bool(provenance_rows),
        detail={"provenance_path": str(provenance_path) if provenance_path else None, "rows": len(provenance_rows)},
    )

    checks.extend(
        _semantic_fidelity_checks(
            pages=pages,
            chapters=chapters,
            html_files=html_files,
        )
    )
    checks.extend(_html_crop_usage_checks(crops=crops, html_files=html_files))
    if critical_graphics_manifest_path is not None:
        checks.extend(
            _critical_graphics_checks(
                critical_manifest=critical_manifest,
                crops=crops,
                min_target_crop_coverage=min_critical_target_crop_coverage,
            )
        )

    role_samples = _role_sample_pages(plan)
    _check(
        checks,
        "manual_review_sample_roles",
        "The report selects representative pages for manual review by role.",
        any(value is not None for value in role_samples.values()),
        warning=True,
        detail=role_samples,
    )

    fail_count = sum(1 for check in checks if check["status"] == "fail")
    warn_count = sum(1 for check in checks if check["status"] == "warn")
    overall_status = "pass" if fail_count == 0 and warn_count == 0 else ("needs_review" if fail_count == 0 else "fail")
    return {
        "schema_version": "semantic_manual_html_conformance_report_v1",
        "module_id": MODULE_ID,
        "run_id": run_id,
        "created_at": _utc(),
        "scope": "graphics_heavy_manual_or_rulebook",
        "overall_status": overall_status,
        "summary": {
            "check_count": len(checks),
            "pass_count": sum(1 for check in checks if check["status"] == "pass"),
            "warn_count": warn_count,
            "fail_count": fail_count,
            "logical_pages": len(logical_pages),
            "page_html_rows": len(pages),
            "preserve_as_figure_count": preserve_count,
            "crop_count": crop_count,
            "html_figure_count": figure_counts["figure_count"],
            "provenance_rows": len(provenance_rows),
        },
        "checks": checks,
        "review_samples": {
            "front_or_first_page": 1 if logical_pages else None,
            "back_or_last_page": len(logical_pages) if logical_pages else None,
            **role_samples,
        },
        "artifacts": {
            "pages": str(pages_path),
            "logical_pages": str(logical_pages_path),
            "logical_page_map": str(logical_map_path),
            "figure_plan": str(figure_plan_path),
            "critical_graphics_manifest": str(critical_graphics_manifest_path) if critical_graphics_manifest_path else None,
            "crops": str(crops_path),
            "chapters": str(chapters_path),
            "html_manifest": str(manifest_path) if manifest_path else None,
        },
    }


def _write_markdown_report(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Semantic Manual HTML Conformance",
        "",
        f"- Overall status: `{report['overall_status']}`",
        f"- Checks: `{report['summary']['check_count']}`",
        f"- Pass: `{report['summary']['pass_count']}`",
        f"- Warn: `{report['summary']['warn_count']}`",
        f"- Fail: `{report['summary']['fail_count']}`",
        "",
        "## Checks",
    ]
    for check in report["checks"]:
        lines.append(f"- `{check['status']}` `{check['id']}`: {check['description']}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate semantic HTML output for graphics-heavy manuals.")
    parser.add_argument("--pages", required=True, help="Final page_html_v1 JSONL")
    parser.add_argument("--logical-pages", required=True, help="Ordered page_image_v1 manifest")
    parser.add_argument("--figure-plan", required=True, help="Essential graphics plan JSON")
    parser.add_argument("--critical-graphics-manifest", help="Optional critical_graphics_manifest_v1 JSON")
    parser.add_argument("--crops", required=True, help="Illustration crop manifest JSONL")
    parser.add_argument("--chapters", required=True, help="Chapter HTML manifest JSONL")
    parser.add_argument("--out", required=True, help="Output conformance report JSON")
    parser.add_argument("--min-figure-crop-ratio", type=float, default=0.75)
    parser.add_argument("--min-critical-target-crop-coverage", type=float, default=0.5)
    parser.add_argument("--fail-on-blocking", action="store_true", help="Exit nonzero when blocking checks fail")
    parser.add_argument("--progress-file")
    parser.add_argument("--state-file")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log("validate", "running", message="Validating semantic manual HTML", module_id=MODULE_ID)

    report = build_report(
        pages_path=Path(args.pages),
        logical_pages_path=Path(args.logical_pages),
        figure_plan_path=Path(args.figure_plan),
        critical_graphics_manifest_path=Path(args.critical_graphics_manifest) if args.critical_graphics_manifest else None,
        crops_path=Path(args.crops),
        chapters_path=Path(args.chapters),
        run_id=args.run_id,
        min_figure_crop_ratio=args.min_figure_crop_ratio,
        min_critical_target_crop_coverage=args.min_critical_target_crop_coverage,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(str(out_path), report)
    _write_markdown_report(out_path.with_suffix(".md"), report)

    logger.log(
        "validate",
        "done",
        current=report["summary"]["check_count"],
        total=report["summary"]["check_count"],
        message=f"Semantic manual conformance: {report['overall_status']}",
        artifact=str(out_path),
        module_id=MODULE_ID,
        extra={"summary": report["summary"]},
    )

    if args.fail_on_blocking and report["summary"]["fail_count"]:
        raise SystemExit(f"Semantic manual conformance failed; see {out_path}")


if __name__ == "__main__":
    main()
