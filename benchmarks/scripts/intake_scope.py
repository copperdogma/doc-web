from pathlib import Path
from typing import Iterable


OFFICE_DIRECT_ENTRY_INPUT_KINDS = frozenset({"docx", "pptx", "xlsx"})


def describe_scope_boundary(input_kind: str, *, surface_key: str, surface_label: str) -> dict[str, str]:
    kind = str(input_kind or "").strip()
    if kind in OFFICE_DIRECT_ENTRY_INPUT_KINDS:
        return {
            "scope_policy": "direct_explicit_recipe_only",
            "boundary_reason": f"outside_{surface_key}:{kind}:direct_explicit_recipe_only",
            "error": (
                f"Input kind '{kind}' is outside {surface_label} because maintained {kind.upper()} "
                "support is a direct explicit-recipe entry lane, not part of this automation surface."
            ),
        }
    return {
        "scope_policy": "unsupported_input_kind",
        "boundary_reason": f"outside_{surface_key}:{kind or 'missing'}:unsupported_input_kind",
        "error": f"Input kind '{kind or 'missing'}' is outside {surface_label}.",
    }


def build_scope_blocked_row(
    case: dict,
    input_path: Path,
    *,
    surface_key: str,
    surface_label: str,
    supported_input_kinds: Iterable[str],
) -> dict:
    details = describe_scope_boundary(
        str(case.get("input_kind") or ""),
        surface_key=surface_key,
        surface_label=surface_label,
    )
    return {
        "id": case["id"],
        "input_kind": case.get("input_kind"),
        "path": str(input_path),
        "status": "blocked",
        "failure_step": "scope",
        "supported_input_kinds": sorted(str(kind) for kind in supported_input_kinds),
        **details,
    }
