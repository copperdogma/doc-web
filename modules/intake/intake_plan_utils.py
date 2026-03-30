import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from modules.common.utils import read_jsonl


VALID_BOOK_TYPES = {
    "novel",
    "cyoa",
    "genealogy",
    "textbook",
    "mixed",
    "other",
}

MAINTAINED_RECIPES = {
    "images_dir": "configs/recipes/recipe-images-ocr-html-mvp.yaml",
    "scanned_pdf": "configs/recipes/recipe-pdf-ocr-html-mvp.yaml",
    "born_digital_pdf": "configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml",
    "born_digital_pdf_non_toc": "configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml",
}

BOOK_TYPE_ALIASES = {
    "booklet": "other",
    "catalog": "other",
    "checklist": "other",
    "choose-your-own-adventure": "cyoa",
    "choose_your_own_adventure": "cyoa",
    "cyoa book": "cyoa",
    "fiction": "novel",
    "form": "other",
    "forms": "other",
    "gamebook": "cyoa",
    "genealogy book": "genealogy",
    "guide": "textbook",
    "instructions": "other",
    "invitation": "other",
    "letter": "other",
    "manual": "textbook",
    "memoir": "novel",
    "program": "other",
    "proposal": "other",
    "reference": "textbook",
    "report": "other",
}

PDF_RECIPE_BOOK_TYPES = {
    "cyoa",
    "genealogy",
    "textbook",
}

PDF_RECIPE_STRUCTURAL_SIGNALS = {
    "tables",
}


def normalize_book_type(raw_value: Any, fallback: str = "other") -> str:
    value = (str(raw_value or "")).strip().lower().replace("-", "_").replace(" ", "_")
    if value in VALID_BOOK_TYPES:
        return value
    if value in BOOK_TYPE_ALIASES:
        return BOOK_TYPE_ALIASES[value]
    return fallback


def normalize_signal_evidence(rows: Optional[Iterable[Dict[str, Any]]]) -> list[dict[str, Any]]:
    normalized = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        signal = str((row or {}).get("signal") or "").strip()
        if not signal:
            continue
        pages = [str(page) for page in (row or {}).get("pages", []) if str(page).strip()]
        normalized.append(
            {
                "signal": signal,
                "pages": sorted(dict.fromkeys(pages)),
                "reason": (row or {}).get("reason"),
            }
        )
    return normalized


def merge_unique_strings(*values: Iterable[str]) -> list[str]:
    merged = []
    seen = set()
    for value_list in values:
        for value in value_list or []:
            text = str(value).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            merged.append(text)
    return merged


def load_contact_sheet_build_meta(manifest_path: Path, sheets_dir: Optional[Path] = None) -> Dict[str, Any]:
    candidates = []
    if sheets_dir:
        candidates.append(Path(sheets_dir) / "contact_sheet_build_meta.json")
    try:
        first_row = next(read_jsonl(str(manifest_path)), None)
    except Exception:
        first_row = None
    if first_row and first_row.get("sheet_path"):
        candidates.append(Path(first_row["sheet_path"]).parent / "contact_sheet_build_meta.json")
    candidates.append(Path(manifest_path).parent / "contact_sheet_build_meta.json")

    seen = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.exists():
            with candidate.open("r", encoding="utf-8") as handle:
                return json.load(handle)
    return {}


def choose_maintained_recipe(plan: Dict[str, Any]) -> Optional[str]:
    source_input = ((plan or {}).get("meta") or {}).get("source_input") or {}
    input_kind = source_input.get("input_kind")
    if input_kind == "images_dir":
        return MAINTAINED_RECIPES["images_dir"]
    if input_kind == "pdf":
        book_type = normalize_book_type((plan or {}).get("book_type"), fallback="other")
        signals = {
            str(signal).strip().lower()
            for signal in (plan or {}).get("signals", [])
            if str(signal).strip()
        }
        tile_count = (((plan or {}).get("meta") or {}).get("summary") or {}).get("tile_count") or 0
        supports_html_recipe = (
            book_type in PDF_RECIPE_BOOK_TYPES
            or ("cyoa" in signals)
            or (int(tile_count) >= 5 and bool(signals & PDF_RECIPE_STRUCTURAL_SIGNALS))
        )
        if source_input.get("has_extractable_text") is True:
            if not supports_html_recipe:
                return MAINTAINED_RECIPES["born_digital_pdf_non_toc"]
            return MAINTAINED_RECIPES["born_digital_pdf"]
        if not supports_html_recipe:
            return None
        return MAINTAINED_RECIPES["scanned_pdf"]
    return None


def resolve_source_images_dir(plan: Dict[str, Any], explicit_dir: Optional[str]) -> Optional[Path]:
    if explicit_dir:
        return Path(explicit_dir)
    source_input = ((plan or {}).get("meta") or {}).get("source_input") or {}
    for key in ("source_images_dir", "rendered_pages_dir", "images_dir"):
        value = source_input.get(key)
        if value:
            return Path(value)
    return None
