import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, Optional

from modules.common.utils import read_jsonl, utc_now


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
DIRECT_ENTRY_ONLY_RECIPES = {
    "docx": "configs/recipes/recipe-docx-html-mvp.yaml",
    "epub": "configs/recipes/recipe-epub-html-mvp.yaml",
    "pptx": "configs/recipes/recipe-pptx-html-mvp.yaml",
    "web-page": "configs/recipes/recipe-web-page-html-mvp.yaml",
    "xlsx": "configs/recipes/recipe-xlsx-html-mvp.yaml",
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

REPO_ROOT = Path(__file__).resolve().parents[2]
MAINTAINED_RECIPE_PATHS = set(MAINTAINED_RECIPES.values())
DIRECT_ENTRY_ONLY_RECIPE_TO_KIND = {path: kind for kind, path in DIRECT_ENTRY_ONLY_RECIPES.items()}


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


def load_artifact_row(path: str | Path) -> Dict[str, Any]:
    artifact_path = Path(path)
    if artifact_path.suffix.lower() == ".json":
        with artifact_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            return payload[0] if payload else {}
        return payload if isinstance(payload, dict) else {}
    return next(read_jsonl(str(artifact_path)), {})


def resolve_repo_path(raw_path: str | Path | None) -> Optional[Path]:
    if not raw_path:
        return None
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve(strict=False)


def normalize_source_input(plan: Dict[str, Any]) -> Dict[str, Any]:
    source_input = ((plan or {}).get("meta") or {}).get("source_input") or {}
    return dict(source_input) if isinstance(source_input, dict) else {}


def default_downstream_run_id(recipe_path: str, upstream_run_id: Optional[str]) -> str:
    recipe_stem = Path(recipe_path).stem
    safe_recipe_stem = "".join(ch if ch.isalnum() else "-" for ch in recipe_stem).strip("-").lower()
    safe_upstream = "".join(ch if ch.isalnum() else "-" for ch in (upstream_run_id or "confirmed-handoff")).strip("-").lower()
    combined = f"{safe_upstream}-{safe_recipe_stem}".strip("-")
    return combined[:120] or "confirmed-handoff"


def resolve_confirmed_handoff_source_input(plan: Dict[str, Any]) -> tuple[Optional[str], Optional[Path], Optional[str]]:
    source_input = normalize_source_input(plan)
    input_kind = source_input.get("input_kind")
    if input_kind == "images_dir":
        source_dir = resolve_source_images_dir(plan, explicit_dir=None)
        if not source_dir:
            return None, None, "missing_source_images_dir"
        return "--input-images", resolve_repo_path(source_dir), None
    if input_kind == "pdf":
        source_pdf = resolve_repo_path(source_input.get("source_pdf"))
        if not source_pdf:
            return None, None, "missing_source_pdf"
        return "--input-pdf", source_pdf, None
    if not input_kind:
        return None, None, "missing_input_kind"
    return None, None, f"unsupported_input_kind:{input_kind}"


def prepare_confirmed_handoff(
    plan: Dict[str, Any],
    *,
    plan_path: str | Path,
    upstream_run_id: Optional[str] = None,
    downstream_run_id: Optional[str] = None,
    downstream_end_at: Optional[str] = None,
    dry_run: bool = False,
    allow_run_id_reuse: bool = False,
) -> tuple[Dict[str, Any], list[str], bool]:
    row: Dict[str, Any] = {
        "schema_version": "intake_handoff_v1",
        "plan_path": str(Path(plan_path)),
        "plan_run_id": plan.get("run_id"),
        "recommended_recipe": plan.get("recommended_recipe"),
        "source_input": normalize_source_input(plan),
        "launch_input_flag": None,
        "launch_input_path": None,
        "driver_command": [],
        "downstream_run_id": None,
        "downstream_output_dir": None,
        "terminal_outcome": "blocked",
        "terminal_reason": None,
        "exit_code": None,
        "run_id": upstream_run_id,
        "created_at": utc_now(),
    }

    recipe = str(plan.get("recommended_recipe") or "").strip()
    if not recipe:
        row["terminal_reason"] = "missing_recommended_recipe"
        return row, [], False
    if recipe == "no-recipe-needed":
        row["terminal_outcome"] = "skipped"
        row["terminal_reason"] = "no_recipe_needed"
        return row, [], False
    direct_entry_kind = DIRECT_ENTRY_ONLY_RECIPE_TO_KIND.get(recipe)
    if direct_entry_kind:
        row["terminal_reason"] = f"direct_entry_recipe_outside_confirmed_handoff_scope:{direct_entry_kind}"
        return row, [], False
    if recipe not in MAINTAINED_RECIPE_PATHS:
        row["terminal_reason"] = f"unsupported_recommended_recipe:{recipe}"
        return row, [], False

    recipe_path = resolve_repo_path(recipe)
    if not recipe_path or not recipe_path.exists():
        row["terminal_reason"] = f"recommended_recipe_not_found:{recipe}"
        return row, [], False

    launch_flag, launch_path, source_error = resolve_confirmed_handoff_source_input(plan)
    if source_error:
        row["terminal_reason"] = source_error
        return row, [], False
    if not launch_path or not launch_path.exists():
        row["terminal_reason"] = f"source_input_not_found:{launch_path}"
        return row, [], False

    resolved_downstream_run_id = downstream_run_id or default_downstream_run_id(recipe, upstream_run_id)
    driver_command = [
        sys.executable,
        str(REPO_ROOT / "driver.py"),
        "--recipe",
        recipe,
        launch_flag,
        str(launch_path),
        "--run-id",
        resolved_downstream_run_id,
    ]
    if allow_run_id_reuse:
        driver_command.append("--allow-run-id-reuse")
    if downstream_end_at:
        driver_command.extend(["--end-at", downstream_end_at])

    row["launch_input_flag"] = launch_flag
    row["launch_input_path"] = str(launch_path)
    row["driver_command"] = driver_command
    row["downstream_run_id"] = resolved_downstream_run_id
    row["downstream_output_dir"] = str(REPO_ROOT / "output" / "runs" / resolved_downstream_run_id)

    if dry_run:
        row["terminal_outcome"] = "skipped"
        row["terminal_reason"] = "dry_run"
        return row, driver_command, False

    return row, driver_command, True


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
