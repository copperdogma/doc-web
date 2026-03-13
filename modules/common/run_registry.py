import hashlib
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from modules.common.utils import append_jsonl, read_jsonl


RUN_MANIFEST_FILENAME = "run_manifest.jsonl"
RUN_HEALTH_FILENAME = "run_health.jsonl"
RUN_ASSESSMENTS_FILENAME = "run_assessments.jsonl"


def _utc() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _git_common_output_root(cwd: Path) -> Optional[Path]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None

    common_dir_raw = (result.stdout or "").strip()
    if not common_dir_raw:
        return None

    common_dir = Path(common_dir_raw)
    if not common_dir.is_absolute():
        common_dir = (cwd / common_dir).resolve(strict=False)
    else:
        common_dir = common_dir.resolve(strict=False)

    candidate = (common_dir.parent / "output").resolve(strict=False)
    if candidate.exists():
        return candidate
    return None


def resolve_output_root(run_dir: Optional[str] = None, cwd: Optional[str] = None) -> str:
    """
    Resolve the shared output root for a run.

    If the run directory lives under */output/runs/<run_id>, use that output root even when
    the current workspace is a worktree or reaches the real run dir through a symlink.
    Otherwise prefer the git common-dir output root, then fall back to <cwd>/output.
    """
    base_cwd = Path(cwd or os.getcwd()).resolve()
    default_root = (base_cwd / "output").resolve()
    if not run_dir:
        shared_root = _git_common_output_root(base_cwd)
        if shared_root:
            return str(shared_root)
        return str(default_root)

    resolved = Path(run_dir).resolve(strict=False)
    for candidate in (resolved,) + tuple(resolved.parents):
        if candidate.name == "runs":
            return str(candidate.parent)
    return str(default_root)


def registry_paths(output_root: str) -> Dict[str, str]:
    root = Path(output_root)
    return {
        "manifest": str(root / RUN_MANIFEST_FILENAME),
        "health": str(root / RUN_HEALTH_FILENAME),
        "assessments": str(root / RUN_ASSESSMENTS_FILENAME),
    }


def rel_to_output_root(path: Optional[str], output_root: str) -> Optional[str]:
    if not path:
        return None
    target = Path(path).resolve(strict=False)
    root = Path(output_root).resolve(strict=False)
    try:
        return os.path.relpath(str(target), str(root))
    except Exception:
        return str(target)


def manifest_entry_for_run(output_root: str, run_id: str) -> Optional[Dict[str, Any]]:
    manifest_path = registry_paths(output_root)["manifest"]
    if not os.path.exists(manifest_path):
        return None
    latest = None
    for row in read_jsonl(manifest_path):
        if row.get("run_id") == run_id:
            latest = row
    return latest


def record_run_manifest(
    run_id: str,
    run_dir: str,
    recipe: Dict[str, Any],
    instrumentation: Optional[Dict[str, str]] = None,
    snapshots: Optional[Dict[str, str]] = None,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    if not run_id:
        return "", None

    output_root = resolve_output_root(run_dir=run_dir)
    manifest_path = registry_paths(output_root)["manifest"]
    existing = set()
    if os.path.exists(manifest_path):
        try:
            for row in read_jsonl(manifest_path):
                if row.get("run_id"):
                    existing.add(row["run_id"])
        except Exception:
            existing = set()
    if run_id in existing:
        return manifest_path, manifest_entry_for_run(output_root, run_id)

    entry = {
        "run_id": run_id,
        "path": rel_to_output_root(run_dir, output_root) or run_dir,
        "created_at": _utc(),
        "recipe": recipe.get("name") or os.path.basename(recipe.get("recipe_path", "")) or None,
        "input": recipe.get("input", {}),
    }
    if instrumentation:
        entry["instrumentation"] = {
            key: rel_to_output_root(value, output_root) or value
            for key, value in instrumentation.items()
        }
    if snapshots:
        entry["snapshots"] = {
            key: rel_to_output_root(value, output_root) or value
            for key, value in snapshots.items()
        }
    append_jsonl(manifest_path, entry)
    return manifest_path, entry


def _read_json(path: str) -> Dict[str, Any]:
    import json

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_html(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


def _jsonl_first_row(path: str) -> Optional[Dict[str, Any]]:
    try:
        for row in read_jsonl(path):
            if isinstance(row, dict):
                return row
    except Exception:
        return None
    return None


def _resolve_artifact_path(
    artifact: Optional[str],
    *,
    run_dir: str,
    output_root: str,
) -> Optional[str]:
    if not artifact:
        return None

    raw = Path(artifact)
    candidates = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.extend(
            [
                raw,
                Path(run_dir) / raw,
                Path(output_root) / raw,
                Path(output_root).parent / raw,
            ]
        )

    seen = set()
    for candidate in candidates:
        resolved = str(candidate.resolve(strict=False))
        if resolved in seen:
            continue
        seen.add(resolved)
        if os.path.exists(resolved):
            return resolved
    return None


def _looks_like_page_html_artifact(path: str, schema_version: Optional[str]) -> bool:
    if schema_version == "page_html_v1":
        return True
    if not path.endswith(".jsonl"):
        return False
    row = _jsonl_first_row(path)
    if not row:
        return False
    return "page_number" in row and "html" in row


def _looks_like_chapter_manifest(path: str) -> bool:
    if not path.endswith(".jsonl"):
        return False
    row = _jsonl_first_row(path)
    if not row:
        return False
    return "file" in row and "kind" in row and "title" in row


def _infer_document_label(input_conf: Dict[str, Any]) -> Optional[str]:
    if not isinstance(input_conf, dict):
        return None
    for key in ("pdf", "input_pdf", "images"):
        value = input_conf.get(key)
        if isinstance(value, str) and value.strip():
            path = value.rstrip("/").rstrip("\\")
            return Path(path).stem if key in {"pdf", "input_pdf"} else Path(path).name
    text_glob = input_conf.get("text_glob")
    if isinstance(text_glob, str) and text_glob.strip():
        parent = Path(text_glob).parent
        return parent.name or Path(text_glob).name
    return None


def _latest_page_html_stage(
    state: Dict[str, Any],
    *,
    run_dir: str,
    output_root: str,
) -> Optional[Tuple[str, Dict[str, Any], str]]:
    stages = state.get("stages") or {}
    latest = None
    for stage_id, stage_state in stages.items():
        status = stage_state.get("status")
        artifact = _resolve_artifact_path(
            stage_state.get("artifact"),
            run_dir=run_dir,
            output_root=output_root,
        )
        if status not in {"done", "skipped"} or not artifact:
            continue
        if _looks_like_page_html_artifact(artifact, stage_state.get("schema_version")):
            latest = (stage_id, stage_state, artifact)
    return latest


def _all_page_html_stages(state: Dict[str, Any], *, run_dir: str, output_root: str) -> List[str]:
    stages = state.get("stages") or {}
    out = []
    for stage_id, stage_state in stages.items():
        artifact = _resolve_artifact_path(
            stage_state.get("artifact"),
            run_dir=run_dir,
            output_root=output_root,
        )
        status = stage_state.get("status")
        if status not in {"done", "skipped"} or not artifact:
            continue
        if _looks_like_page_html_artifact(artifact, stage_state.get("schema_version")):
            out.append(stage_id)
    return out


def analyze_page_html_artifact(path: str) -> Dict[str, Any]:
    rows = [row for row in read_jsonl(path) if isinstance(row, dict) and "page_number" in row]
    rows.sort(key=lambda row: (row.get("page_number") is None, row.get("page_number")))
    page_count = len(rows)
    empty_rows = [row for row in rows if not _normalize_html(row.get("html"))]
    empty_html_page_numbers = [row.get("page_number") for row in empty_rows if row.get("page_number") is not None]
    empty_html_printed_pages = [
        row.get("printed_page_number")
        for row in empty_rows
        if row.get("printed_page_number") is not None
    ]
    empty_html_with_printed_number_pages = [
        row.get("page_number")
        for row in empty_rows
        if row.get("page_number") is not None and row.get("printed_page_number") is not None
    ]

    empty_html_between_nonempty_pages: List[int] = []
    for idx, row in enumerate(rows):
        if _normalize_html(row.get("html")):
            continue
        prev_nonempty = idx > 0 and bool(_normalize_html(rows[idx - 1].get("html")))
        next_nonempty = idx < len(rows) - 1 and bool(_normalize_html(rows[idx + 1].get("html")))
        page_number = row.get("page_number")
        if prev_nonempty and next_nonempty and page_number is not None:
            empty_html_between_nonempty_pages.append(page_number)

    fatal_signals: List[str] = []
    if page_count == 0:
        fatal_signals.append("no_page_html_rows")
    if empty_html_with_printed_number_pages:
        fatal_signals.append("empty_html_with_printed_number_pages")
    if empty_html_between_nonempty_pages:
        fatal_signals.append("empty_html_between_nonempty_pages")

    return {
        "page_count": page_count,
        "empty_html_pages": len(empty_rows),
        "empty_html_page_numbers": empty_html_page_numbers,
        "empty_html_printed_pages": empty_html_printed_pages,
        "empty_html_with_printed_number_pages": empty_html_with_printed_number_pages,
        "empty_html_between_nonempty_pages": empty_html_between_nonempty_pages,
        "fatal_signals": fatal_signals,
    }


def _chapter_manifest_summary(path: str) -> Dict[str, Any]:
    chapter_count = 0
    page_file_count = 0
    try:
        for row in read_jsonl(path):
            if not isinstance(row, dict):
                continue
            kind = row.get("kind")
            if kind == "chapter":
                chapter_count += 1
            elif kind == "page":
                page_file_count += 1
    except Exception:
        return {"chapter_count": None, "page_file_count": None}
    return {"chapter_count": chapter_count, "page_file_count": page_file_count}


def build_run_health_entry(
    run_id: str,
    run_dir: str,
    *,
    recipe: Optional[Dict[str, Any]] = None,
    state_path: Optional[str] = None,
) -> Dict[str, Any]:
    output_root = resolve_output_root(run_dir=run_dir)
    manifest_entry = manifest_entry_for_run(output_root, run_id)
    run_input = {}
    recipe_name = None
    if manifest_entry:
        run_input = manifest_entry.get("input") or {}
        recipe_name = manifest_entry.get("recipe")
    if recipe:
        run_input = recipe.get("input", {}) or run_input
        recipe_name = recipe.get("name") or os.path.basename(recipe.get("recipe_path", "")) or recipe_name

    state_file = state_path or os.path.join(run_dir, "pipeline_state.json")
    if not os.path.exists(state_file):
        raise FileNotFoundError(f"Run state not found: {state_file}")
    state = _read_json(state_file)

    page_html_stage = _latest_page_html_stage(state, run_dir=run_dir, output_root=output_root)
    page_html_summary = {
        "page_count": None,
        "empty_html_pages": None,
        "empty_html_page_numbers": [],
        "empty_html_printed_pages": [],
        "empty_html_with_printed_number_pages": [],
        "empty_html_between_nonempty_pages": [],
        "fatal_signals": [],
    }
    page_html_stage_id = None
    page_html_artifact = None
    if page_html_stage:
        page_html_stage_id, _, page_html_artifact = page_html_stage
        page_html_summary = analyze_page_html_artifact(page_html_artifact)

    chapter_manifest_artifact = None
    chapter_summary = {"chapter_count": None, "page_file_count": None}
    stages = state.get("stages") or {}
    for stage_state in stages.values():
        artifact = _resolve_artifact_path(
            stage_state.get("artifact"),
            run_dir=run_dir,
            output_root=output_root,
        )
        if stage_state.get("status") not in {"done", "skipped"} or not artifact:
            continue
        if _looks_like_chapter_manifest(artifact):
            chapter_manifest_artifact = artifact
    if chapter_manifest_artifact:
        chapter_summary = _chapter_manifest_summary(chapter_manifest_artifact)

    stage_ids = list(stages.keys())
    stage_graph_hash = hashlib.sha1("\n".join(stage_ids).encode("utf-8")).hexdigest()[:12]

    return {
        "schema_version": "run_health_v1",
        "run_id": run_id,
        "path": rel_to_output_root(run_dir, output_root) or run_dir,
        "document": _infer_document_label(run_input),
        "recipe": recipe_name,
        "measured_at": _utc(),
        "run_status": state.get("status"),
        "status_reason": state.get("status_reason"),
        "stage_ids": stage_ids,
        "stage_graph_hash": stage_graph_hash,
        "page_html_stage_ids": _all_page_html_stages(state, run_dir=run_dir, output_root=output_root),
        "page_html_stage_id": page_html_stage_id,
        "page_html_artifact": rel_to_output_root(page_html_artifact, output_root) or page_html_artifact,
        "page_count": page_html_summary["page_count"],
        "empty_html_pages": page_html_summary["empty_html_pages"],
        "empty_html_page_numbers": page_html_summary["empty_html_page_numbers"],
        "empty_html_printed_pages": page_html_summary["empty_html_printed_pages"],
        "empty_html_with_printed_number_pages": page_html_summary["empty_html_with_printed_number_pages"],
        "empty_html_between_nonempty_pages": page_html_summary["empty_html_between_nonempty_pages"],
        "fatal_signals": page_html_summary["fatal_signals"],
        "chapter_manifest_artifact": rel_to_output_root(chapter_manifest_artifact, output_root) or chapter_manifest_artifact,
        "chapter_count": chapter_summary["chapter_count"],
        "page_file_count": chapter_summary["page_file_count"],
    }


def record_run_health(
    run_id: str,
    run_dir: str,
    *,
    recipe: Optional[Dict[str, Any]] = None,
    state_path: Optional[str] = None,
) -> Tuple[str, Dict[str, Any]]:
    output_root = resolve_output_root(run_dir=run_dir)
    health_path = registry_paths(output_root)["health"]
    entry = build_run_health_entry(run_id, run_dir, recipe=recipe, state_path=state_path)
    append_jsonl(health_path, entry)
    return health_path, entry


def latest_run_health(output_root: str, run_id: str) -> Optional[Dict[str, Any]]:
    health_path = registry_paths(output_root)["health"]
    if not os.path.exists(health_path):
        return None
    latest = None
    for row in read_jsonl(health_path):
        if row.get("run_id") == run_id:
            latest = row
    return latest


def record_run_assessment(
    *,
    run_id: str,
    scope: str,
    status: str,
    summary: str,
    output_root: Optional[str] = None,
    run_dir: Optional[str] = None,
    findings: Optional[Sequence[str]] = None,
    evidence_paths: Optional[Sequence[str]] = None,
    document: Optional[str] = None,
    source_story: Optional[str] = None,
    source_issue: Optional[str] = None,
    supersedes: Optional[Sequence[str]] = None,
    author: str = "ai",
) -> Tuple[str, Dict[str, Any]]:
    if not output_root:
        output_root = resolve_output_root(run_dir=run_dir)
    assessments_path = registry_paths(output_root)["assessments"]
    manifest_entry = manifest_entry_for_run(output_root, run_id)
    health_entry = latest_run_health(output_root, run_id)
    document_name = document
    if not document_name and health_entry:
        document_name = health_entry.get("document")
    if not document_name and manifest_entry:
        document_name = _infer_document_label(manifest_entry.get("input") or {})

    rel_evidence = [
        rel_to_output_root(path, output_root) or path
        for path in (evidence_paths or [])
    ]
    entry = {
        "schema_version": "run_assessment_v1",
        "run_id": run_id,
        "path": rel_to_output_root(run_dir, output_root) if run_dir else (manifest_entry or {}).get("path"),
        "document": document_name,
        "scope": scope,
        "status": status,
        "summary": summary,
        "findings": list(findings or []),
        "evidence_paths": rel_evidence,
        "reviewed_at": _utc(),
        "source_story": source_story,
        "source_issue": source_issue,
        "supersedes": list(supersedes or []),
        "author": author,
    }
    append_jsonl(assessments_path, entry)
    return assessments_path, entry


def latest_run_assessment(output_root: str, run_id: str, scope: Optional[str] = None) -> Optional[Dict[str, Any]]:
    assessments_path = registry_paths(output_root)["assessments"]
    if not os.path.exists(assessments_path):
        return None
    latest_exact = None
    latest_global = None
    for row in read_jsonl(assessments_path):
        if row.get("run_id") != run_id:
            continue
        row_scope = row.get("scope")
        if scope and row_scope == scope:
            latest_exact = row
        elif row_scope in {"all", "*"}:
            latest_global = row
        elif not scope:
            latest_exact = row
    return latest_exact or latest_global


def check_run_reuse(
    *,
    run_id: str,
    scope: str,
    output_root: Optional[str] = None,
    run_dir: Optional[str] = None,
) -> Dict[str, Any]:
    if not output_root:
        output_root = resolve_output_root(run_dir=run_dir)

    manifest_entry = manifest_entry_for_run(output_root, run_id)
    resolved_run_dir = run_dir
    if not resolved_run_dir and manifest_entry:
        path = manifest_entry.get("path")
        if isinstance(path, str) and path:
            candidate = Path(output_root) / path
            resolved_run_dir = str(candidate.resolve(strict=False))
    if not resolved_run_dir:
        candidate = Path(output_root) / "runs" / run_id
        if candidate.exists():
            resolved_run_dir = str(candidate.resolve(strict=False))

    health_entry = latest_run_health(output_root, run_id)
    if not health_entry and resolved_run_dir:
        try:
            health_entry = build_run_health_entry(run_id, resolved_run_dir)
        except Exception:
            health_entry = None
    assessment_entry = latest_run_assessment(output_root, run_id, scope=scope)

    reasons: List[str] = []
    recommendation = "unknown"
    fatal_signals = list((health_entry or {}).get("fatal_signals") or [])
    if fatal_signals:
        reasons.append(f"health flags: {', '.join(fatal_signals)}")

    assessment_status = (assessment_entry or {}).get("status")
    if assessment_status == "unsafe":
        recommendation = "unsafe"
        reasons.append("latest assessment marks this scope unsafe")
    elif fatal_signals:
        recommendation = "unsafe"
    elif assessment_status == "known_good":
        recommendation = "safe"
        reasons.append("latest assessment marks this scope known_good")
    elif assessment_status in {"partial", "superseded"}:
        recommendation = "caution"
        reasons.append(f"latest assessment status is {assessment_status}")

    if recommendation == "unknown" and not assessment_entry and not health_entry:
        reasons.append("no manifest, health, or assessment data found")
    elif recommendation == "unknown" and not assessment_entry:
        reasons.append("no assessment recorded for requested scope")

    return {
        "run_id": run_id,
        "scope": scope,
        "output_root": output_root,
        "run_dir": resolved_run_dir,
        "manifest": manifest_entry,
        "health": health_entry,
        "assessment": assessment_entry,
        "recommendation": recommendation,
        "reasons": reasons,
    }
