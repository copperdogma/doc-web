#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs/methodology/state.yaml"
GRAPH_PATH = ROOT / "docs/methodology/graph.json"
IDEAL_PATH = ROOT / "docs/ideal.md"
SPEC_PATH = ROOT / "docs/spec.md"
EVALS_PATH = ROOT / "docs/evals/registry.yaml"
STORIES_DIR = ROOT / "docs/stories"
STORIES_INDEX_PATH = ROOT / "docs/stories.md"
ADRS_DIR = ROOT / "docs/decisions"
COVERAGE_MATRIX_PATH = ROOT / "tests/fixtures/formats/_coverage-matrix.json"
ACTIVE_SURFACE_PATHS = [
    ROOT / "AGENTS.md",
    ROOT / "docs/methodology-ideal-spec-compromise.md",
    ROOT / "docs/decisions/README.md",
    ROOT / "docs/runbooks/codebase-improvement-scout.md",
    ROOT / "docs/runbooks/setup-methodology.md",
    ROOT / "docs/runbooks/adr-creation.md",
    ROOT / "docs/runbooks/triage-architecture.md",
    ROOT / "docs/setup-checklist.md",
    ROOT / ".agents/skills/align/SKILL.md",
    ROOT / ".agents/skills/build-story/SKILL.md",
    ROOT / ".agents/skills/codebase-improvement-scout/SKILL.md",
    ROOT / ".agents/skills/create-adr/SKILL.md",
    ROOT / ".agents/skills/create-adr/templates/adr.md",
    ROOT / ".agents/skills/create-story/SKILL.md",
    ROOT / ".agents/skills/create-story/templates/story.md",
    ROOT / ".agents/skills/finish-and-push/SKILL.md",
    ROOT / ".agents/skills/format-gap-analysis/SKILL.md",
    ROOT / ".agents/skills/mark-story-done/SKILL.md",
    ROOT / ".agents/skills/setup-methodology/SKILL.md",
    ROOT / ".agents/skills/setup-methodology/templates/setup-checklist.md",
    ROOT / ".agents/skills/triage/SKILL.md",
    ROOT / ".agents/skills/triage-evals/SKILL.md",
    ROOT / ".agents/skills/triage-inbox/SKILL.md",
    ROOT / ".agents/skills/triage-stories/SKILL.md",
    ROOT / ".agents/skills/validate/SKILL.md",
]
SPEC_REF_RE = re.compile(r"\bspec:\d+(?:\.\d+)*\b")
ADR_ID_RE = re.compile(r"\bADR-\d{3}\b")
COMPROMISE_ID_RE = re.compile(r"\b(?:C|B)\d+\b")
STORY_ID_INLINE_RE = re.compile(r"\b(?:Story\s+|story[- ])(\d{3})\b", re.IGNORECASE)
STORY_FILE_RE = re.compile(r"story-(\d{3})-")
CANONICAL_STORY_FILE_RE = re.compile(r"^story-(\d{3})-[a-z0-9-]+\.md$")
ALLOWED_LEGACY_CONTEXT_RE = re.compile(
    r"legacy|historical|archive|archived|retired|replaced|previous|stub|final hand-authored",
    re.IGNORECASE,
)
LIVE_BUILD_MAP_RE = re.compile(r"docs/build-map\.md|build-map-first|build-map-centered", re.IGNORECASE)
MANUAL_STORIES_INDEX_RE = re.compile(
    r"add a row to .*docs/stories\.md|update corresponding row in .*docs/stories\.md|edit .*docs/stories\.md",
    re.IGNORECASE,
)
ALLOWED_GENERATED_INDEX_CONTEXT_RE = re.compile(r"generated|compile|drift|archive|historical", re.IGNORECASE)
EMPTY_STORY_SECTION_RE = re.compile(
    r"^(?:n/?a|none|not blocked|not currently blocked)(?:[\s.:;-].*)?$",
    re.IGNORECASE | re.DOTALL,
)
PLACEHOLDER_SECTION_RE = re.compile(r"^\{.+\}$", re.DOTALL)
VALID_STORY_STATUSES = {
    "Draft",
    "Pending",
    "In Progress",
    "Done",
    "Blocked",
    "To Do",
    "Complete",
    "Won't Do",
    "Obsolete",
}
REQUIRED_STORY_FRONTMATTER_KEYS = {
    "title",
    "status",
    "priority",
    "ideal_refs",
    "spec_refs",
    "adr_refs",
    "depends_on",
    "category_refs",
    "compromise_refs",
    "input_coverage_refs",
    "architecture_domains",
    "roadmap_tags",
}
REQUIRED_ADR_FRONTMATTER_KEYS = {
    "title",
    "status",
    "ideal_refs",
    "spec_refs",
    "story_refs",
    "compromise_refs",
    "related_adrs",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def to_rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def unique_sorted(values: list[str] | set[str]) -> list[str]:
    return sorted({value for value in values if value}, key=lambda value: (value.lower(), value))


def first_non_empty_line(lines: list[str]) -> tuple[int, str] | None:
    for index, line in enumerate(lines):
        if line.strip():
            return index, line
    return None


def parse_frontmatter_document(text: str, path: Path) -> tuple[dict[str, Any], str, bool]:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return {}, text, False
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        raise ValueError(f"Unterminated frontmatter in {to_rel(path)}")
    frontmatter = yaml.safe_load(match.group(1)) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError(f"Frontmatter must parse to a mapping in {to_rel(path)}")
    return frontmatter, text[match.end() :], True


def frontmatter_list(frontmatter: dict[str, Any], key: str) -> list[str]:
    value = frontmatter.get(key)
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def parse_legacy_fields(body: str) -> dict[str, str]:
    lines = body.splitlines()
    heading = first_non_empty_line(lines)
    start = (heading[0] + 1) if heading else 0
    fields: dict[str, str] = {}
    current: str | None = None
    for line in lines[start:]:
        if line.startswith("## "):
            break
        match = re.match(r"^\*\*(.+?)\*\*:\s*(.*)$", line)
        if match:
            current = match.group(1)
            fields[current] = match.group(2).strip()
            continue
        if current and line.strip():
            fields[current] = f"{fields[current]} {line.strip()}".strip()
            continue
        current = None
    return fields


def split_loose_refs(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in re.split(r"\s*(?:\||;)\s*", value) if part.strip()]


def normalize_story_section(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return ""
    if EMPTY_STORY_SECTION_RE.match(cleaned):
        return ""
    if PLACEHOLDER_SECTION_RE.match(cleaned):
        return ""
    return cleaned


def extract_markdown_section(body: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(body)
    if not match:
        return ""
    return normalize_story_section(match.group(1))


def extract_story_ids(text: str) -> list[str]:
    return unique_sorted([match.group(1) for match in STORY_ID_INLINE_RE.finditer(text)])


def parse_ideal() -> dict[str, Any]:
    lines = read_text(IDEAL_PATH).splitlines()
    section = None
    preferences: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    for line in lines:
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if section == "Vision-Level Preferences":
            match = re.match(r"^- \*\*(.+?)\.\*\*\s*(.+)$", line)
            if match:
                preferences.append(
                    {"label": match.group(1).strip(), "description": match.group(2).strip()}
                )
        if section == "Requirements":
            match = re.match(r"^(\d+)\.\s+\*\*(.+?)\*\*\s+—\s+(.+)$", line)
            if match:
                requirements.append(
                    {
                        "id": f"req:{match.group(1)}",
                        "label": match.group(2).strip(),
                        "description": match.group(3).strip(),
                    }
                )
    return {
        "path": to_rel(IDEAL_PATH),
        "title": lines[0].removeprefix("# ").strip(),
        "preferences": preferences,
        "requirements": requirements,
    }


def parse_spec() -> dict[str, Any]:
    categories: list[dict[str, Any]] = []
    compromises: list[dict[str, Any]] = []
    current_category: str | None = None
    for line in read_text(SPEC_PATH).splitlines():
        category = re.match(r"^##\s+(spec:\d+)\s+—\s+(.+)$", line)
        if category:
            current_category = category.group(1)
            categories.append({"id": current_category, "title": category.group(2).strip(), "sections": []})
            continue
        section = re.match(r"^###\s+(spec:\d+(?:\.\d+)*)\s+—\s+(.+)$", line)
        if section and current_category:
            categories[-1]["sections"].append({"id": section.group(1), "title": section.group(2).strip()})
            continue
        bold_compromise = re.match(r"^\*\*((C\d+|B\d+):\s*([^*]+))\*\*", line)
        if bold_compromise and current_category:
            compromises.append(
                {
                    "id": bold_compromise.group(2),
                    "title": bold_compromise.group(3).strip(),
                    "category_id": current_category,
                    "source": "bold",
                }
            )
            continue
        table_compromise = re.match(r"^\|\s*(B\d+)\s*\|\s*([^|]+?)\s*\|", line)
        if table_compromise and current_category and not any(
            item["id"] == table_compromise.group(1) for item in compromises
        ):
            compromises.append(
                {
                    "id": table_compromise.group(1),
                    "title": table_compromise.group(2).strip(),
                    "category_id": current_category,
                    "source": "table",
                }
            )
    return {"path": to_rel(SPEC_PATH), "categories": categories, "compromises": compromises}


def parse_story(path: Path) -> dict[str, Any]:
    frontmatter, body, has_frontmatter = parse_frontmatter_document(read_text(path), path)
    fields = parse_legacy_fields(body)
    lines = body.splitlines()
    heading = first_non_empty_line(lines)
    file_match = CANONICAL_STORY_FILE_RE.match(path.name)
    if not file_match:
        raise ValueError(f"Unable to derive story id from {to_rel(path)}")
    spec_text = " ".join(
        part
        for part in [fields.get("Spec Refs", ""), fields.get("Build Map Refs", ""), fields.get("Decision Refs", "")]
        if part
    )
    legacy_decision_refs = split_loose_refs(fields.get("Decision Refs") or fields.get("ADR Refs"))
    frontmatter_adr_refs = unique_sorted(frontmatter_list(frontmatter, "adr_refs"))
    if has_frontmatter:
        status = str(frontmatter.get("status") or "Unknown")
        priority = str(frontmatter.get("priority") or "Unknown")
        ideal_refs = unique_sorted(frontmatter_list(frontmatter, "ideal_refs"))
        spec_refs = unique_sorted(frontmatter_list(frontmatter, "spec_refs"))
        adr_ids = unique_sorted(ADR_ID_RE.findall(" ".join(frontmatter_adr_refs)))
        depends_on = unique_sorted([re.sub(r"\D", "", value) for value in frontmatter_list(frontmatter, "depends_on")])
        compromise_refs = unique_sorted(frontmatter_list(frontmatter, "compromise_refs"))
    else:
        status = str(fields.get("Status") or "Unknown")
        priority = str(fields.get("Priority") or "Unknown")
        ideal_refs = unique_sorted(split_loose_refs(fields.get("Ideal Refs")))
        spec_refs = unique_sorted(SPEC_REF_RE.findall(spec_text))
        adr_ids = unique_sorted(
            ADR_ID_RE.findall(fields.get("Decision Refs", "")) or ADR_ID_RE.findall(fields.get("ADR Refs", ""))
        )
        depends_on = unique_sorted(re.findall(r"\b\d{3}\b", fields.get("Depends On", "")))
        compromise_refs = unique_sorted(COMPROMISE_ID_RE.findall(spec_text))
    title = str(frontmatter.get("title") or "")
    if not title and heading:
        title_match = re.match(r"^#+\s+Story(?:\s+\d+)?\s*[—:-]\s+(.+)$", heading[1])
        title = title_match.group(1).strip() if title_match else re.sub(r"^#+\s*", "", heading[1]).strip()
    missing = sorted(REQUIRED_STORY_FRONTMATTER_KEYS - set(frontmatter)) if has_frontmatter else []
    blocker_summary = extract_markdown_section(body, "Blocker Summary")
    blocker_evidence = extract_markdown_section(body, "Blocker Evidence")
    unblock_condition = extract_markdown_section(body, "Unblock Condition")
    return {
        "id": file_match.group(1),
        "title": title or path.stem,
        "path": to_rel(path),
        "status": status,
        "priority": priority,
        "ideal_refs": ideal_refs,
        "spec_refs": spec_refs,
        "decision_refs": unique_sorted(frontmatter_adr_refs + legacy_decision_refs),
        "adr_ids": adr_ids,
        "depends_on": depends_on,
        "category_refs": unique_sorted(frontmatter_list(frontmatter, "category_refs")),
        "compromise_refs": compromise_refs,
        "input_coverage_refs": unique_sorted(frontmatter_list(frontmatter, "input_coverage_refs")),
        "architecture_domains": unique_sorted(frontmatter_list(frontmatter, "architecture_domains")),
        "roadmap_tags": unique_sorted(frontmatter_list(frontmatter, "roadmap_tags")),
        "blocker_summary": blocker_summary,
        "blocker_evidence": blocker_evidence,
        "unblock_condition": unblock_condition,
        "legacy_build_map_refs": fields.get("Build Map Refs", ""),
        "metadata_source": "frontmatter" if has_frontmatter else "legacy",
        "missing_frontmatter_keys": missing,
    }


def parse_stories() -> list[dict[str, Any]]:
    return [parse_story(path) for path in sorted(STORIES_DIR.glob("story-*.md")) if CANONICAL_STORY_FILE_RE.match(path.name)]


def parse_adr(path: Path) -> dict[str, Any]:
    frontmatter, body, has_frontmatter = parse_frontmatter_document(read_text(path), path)
    lines = body.splitlines()
    heading = first_non_empty_line(lines)
    if not heading:
        raise ValueError(f"Unable to parse ADR heading in {to_rel(path)}")
    title_match = re.match(r"^#\s+(ADR-\d{3}):\s+(.+)$", heading[1])
    if not title_match:
        raise ValueError(f"Unable to parse ADR heading in {to_rel(path)}")
    text = body
    missing = sorted(REQUIRED_ADR_FRONTMATTER_KEYS - set(frontmatter)) if has_frontmatter else []
    if has_frontmatter:
        spec_refs = unique_sorted(frontmatter_list(frontmatter, "spec_refs"))
        story_refs = unique_sorted([re.sub(r"\D", "", value) for value in frontmatter_list(frontmatter, "story_refs")])
        compromise_refs = unique_sorted(frontmatter_list(frontmatter, "compromise_refs"))
        related_adrs = unique_sorted(frontmatter_list(frontmatter, "related_adrs"))
    else:
        spec_refs = unique_sorted(SPEC_REF_RE.findall(text))
        story_refs = unique_sorted(extract_story_ids(text))
        compromise_refs = unique_sorted(COMPROMISE_ID_RE.findall(text))
        related_adrs = unique_sorted(ADR_ID_RE.findall(text))
    return {
        "id": title_match.group(1),
        "title": str(frontmatter.get("title") or title_match.group(2).strip()),
        "path": to_rel(path),
        "status": str(frontmatter.get("status") or ""),
        "ideal_refs": unique_sorted(frontmatter_list(frontmatter, "ideal_refs")),
        "spec_refs": spec_refs,
        "story_refs": story_refs,
        "compromise_refs": compromise_refs,
        "related_adrs": related_adrs,
        "metadata_source": "frontmatter" if has_frontmatter else "legacy",
        "missing_frontmatter_keys": missing,
    }


def parse_adrs() -> list[dict[str, Any]]:
    return [parse_adr(path) for path in sorted(ADRS_DIR.glob("adr-*/adr.md"))]


def parse_eval_registry() -> list[dict[str, Any]]:
    payload = yaml.safe_load(read_text(EVALS_PATH)) or {}
    records = []
    for raw in payload.get("evals", []):
        blob = json.dumps(raw, default=str)
        spec_refs = unique_sorted([str(item) for item in raw.get("spec_refs", [])] + SPEC_REF_RE.findall(blob))
        compromise = raw.get("spec_compromise")
        compromise_refs = []
        if isinstance(compromise, str) and compromise.strip():
            compromise_refs.append(compromise.strip())
        compromise_refs.extend(COMPROMISE_ID_RE.findall(blob))
        records.append(
            {
                "id": str(raw["id"]),
                "name": str(raw.get("name") or raw["id"]),
                "type": str(raw.get("type") or "unknown"),
                "command": str(raw.get("command") or ""),
                "path": to_rel(EVALS_PATH),
                "spec_refs": spec_refs,
                "story_refs": extract_story_ids(blob),
                "compromise_refs": unique_sorted(compromise_refs),
            }
        )
    return records


def parse_state() -> dict[str, Any]:
    payload = yaml.safe_load(read_text(STATE_PATH)) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"{to_rel(STATE_PATH)} must parse to a mapping")
    return payload


def parse_coverage_matrix() -> dict[str, Any]:
    return json.loads(read_text(COVERAGE_MATRIX_PATH))


def category_for_spec_ref(spec_ref: str) -> str | None:
    match = re.match(r"^(spec:\d+)", spec_ref)
    return match.group(1) if match else None


def build_graph() -> dict[str, Any]:
    ideal = parse_ideal()
    spec = parse_spec()
    state = parse_state()
    coverage = parse_coverage_matrix()
    stories = parse_stories()
    adrs = parse_adrs()
    evals = parse_eval_registry()
    compromise_to_category = {entry["id"]: entry["category_id"] for entry in spec["compromises"]}
    coverage_ids = {entry["id"] for entry in coverage.get("formats", [])}
    story_overrides = state.get("story_overrides", {}).get("category_refs", {})
    for story in stories:
        category_refs = set(story["category_refs"])
        for spec_ref in story["spec_refs"]:
            category = category_for_spec_ref(spec_ref)
            if category:
                category_refs.add(category)
        for compromise in story["compromise_refs"]:
            category = compromise_to_category.get(compromise)
            if category:
                category_refs.add(category)
        for category in story_overrides.get(story["id"], []):
            category_refs.add(str(category))
        if not story["input_coverage_refs"] and story["legacy_build_map_refs"]:
            story["input_coverage_refs"] = unique_sorted(
                [coverage_id for coverage_id in coverage_ids if coverage_id in story["legacy_build_map_refs"]]
            )
        story["category_refs"] = sorted(category_refs)
        if story["metadata_source"] == "legacy":
            story["adr_ids"] = unique_sorted(
                story["adr_ids"] + [match for ref in story["decision_refs"] for match in ADR_ID_RE.findall(ref)]
            )
    story_map = {story["id"]: story for story in stories}
    for adr in adrs:
        category_refs = {category_for_spec_ref(ref) for ref in adr["spec_refs"] if category_for_spec_ref(ref)}
        for compromise in adr["compromise_refs"]:
            category = compromise_to_category.get(compromise)
            if category:
                category_refs.add(category)
        for story_id in adr["story_refs"]:
            category_refs.update(story_map.get(story_id, {}).get("category_refs", []))
        adr["category_refs"] = sorted(category_refs)
    for entry in evals:
        category_refs = {category_for_spec_ref(ref) for ref in entry["spec_refs"] if category_for_spec_ref(ref)}
        for compromise in entry["compromise_refs"]:
            category = compromise_to_category.get(compromise)
            if category:
                category_refs.add(category)
        for story_id in entry["story_refs"]:
            category_refs.update(story_map.get(story_id, {}).get("category_refs", []))
        entry["category_refs"] = sorted(category_refs)
    validation = validate_graph(state, spec, stories, adrs, evals, coverage)
    categories = []
    for category in spec["categories"]:
        category_id = category["id"]
        categories.append(
            {
                **category,
                "state": state.get("categories", {}).get(category_id),
                "story_ids": [story["id"] for story in stories if category_id in story["category_refs"]],
                "adr_ids": [adr["id"] for adr in adrs if category_id in adr.get("category_refs", [])],
                "eval_ids": [entry["id"] for entry in evals if category_id in entry.get("category_refs", [])],
            }
        )
    return {
        "version": 1,
        "paths": {
            "ideal": to_rel(IDEAL_PATH),
            "spec": to_rel(SPEC_PATH),
            "state": to_rel(STATE_PATH),
            "graph": to_rel(GRAPH_PATH),
            "stories_dir": to_rel(STORIES_DIR),
            "stories_index": to_rel(STORIES_INDEX_PATH),
            "evals": to_rel(EVALS_PATH),
            "coverage_matrix": to_rel(COVERAGE_MATRIX_PATH),
        },
        "ideal": ideal,
        "spec": {"path": spec["path"], "categories": categories, "compromises": spec["compromises"]},
        "stories": stories,
        "adrs": adrs,
        "evals": evals,
        "coverage": {
            "path": to_rel(COVERAGE_MATRIX_PATH),
            "generated": coverage.get("generated"),
            "formats": coverage.get("formats", []),
            "statuses": coverage.get("statuses", {}),
        },
        "state": state,
        "validation": validation,
    }


def validate_graph(
    state: dict[str, Any],
    spec: dict[str, Any],
    stories: list[dict[str, Any]],
    adrs: list[dict[str, Any]],
    evals: list[dict[str, Any]],
    coverage: dict[str, Any],
) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    category_ids = {entry["id"] for entry in spec["categories"]}
    spec_section_ids = {section["id"] for entry in spec["categories"] for section in entry["sections"]}
    compromise_ids = {entry["id"] for entry in spec["compromises"]}
    story_ids = {story["id"] for story in stories}
    adr_ids = {adr["id"] for adr in adrs}
    coverage_ids = {entry["id"] for entry in coverage.get("formats", [])}
    legacy_story_ids: list[str] = []
    nonstandard_statuses: list[str] = []
    legacy_adr_ids: list[str] = []
    for category_id in state.get("categories", {}):
        if category_id not in category_ids:
            errors.append(f"state.categories.{category_id} does not match any spec category")
    for compromise_id in state.get("compromises", {}):
        if compromise_id not in compromise_ids:
            errors.append(f"state.compromises.{compromise_id} does not match any spec compromise")
    for story in stories:
        if story["metadata_source"] == "frontmatter" and story["missing_frontmatter_keys"]:
            errors.append(f"story {story['id']} frontmatter missing keys: {', '.join(story['missing_frontmatter_keys'])}")
        if story["status"] not in VALID_STORY_STATUSES:
            nonstandard_statuses.append(f"{story['id']}:{story['status']}")
        if story["status"] == "Blocked":
            missing_blocker_fields = [
                label
                for key, label in [
                    ("blocker_summary", "Blocker Summary"),
                    ("blocker_evidence", "Blocker Evidence"),
                    ("unblock_condition", "Unblock Condition"),
                ]
                if not story.get(key)
            ]
            if missing_blocker_fields:
                errors.append(
                    f"story {story['id']} is Blocked but missing sections: {', '.join(missing_blocker_fields)}"
                )
        if story["metadata_source"] == "legacy":
            legacy_story_ids.append(story["id"])
        for spec_ref in story["spec_refs"]:
            if spec_ref.startswith("spec:") and spec_ref not in category_ids and spec_ref not in spec_section_ids:
                errors.append(f"story {story['id']} references missing spec ref {spec_ref}")
        for dependency in story["depends_on"]:
            if dependency not in story_ids:
                errors.append(f"story {story['id']} depends_on missing story {dependency}")
        for adr_id in story["adr_ids"]:
            if adr_id not in adr_ids:
                errors.append(f"story {story['id']} references ADR with no local adr.md: {adr_id}")
        for compromise in story["compromise_refs"]:
            if compromise not in compromise_ids:
                errors.append(f"story {story['id']} references missing compromise {compromise}")
        for category in story["category_refs"]:
            if category not in category_ids:
                errors.append(f"story {story['id']} references missing category {category}")
        for coverage_id in story["input_coverage_refs"]:
            if coverage_id not in coverage_ids:
                errors.append(f"story {story['id']} references missing coverage row {coverage_id}")
    for adr in adrs:
        if adr["metadata_source"] == "frontmatter" and adr["missing_frontmatter_keys"]:
            errors.append(f"ADR {adr['id']} frontmatter missing keys: {', '.join(adr['missing_frontmatter_keys'])}")
        if adr["metadata_source"] == "legacy":
            legacy_adr_ids.append(adr["id"])
        for spec_ref in adr["spec_refs"]:
            if spec_ref.startswith("spec:") and spec_ref not in category_ids and spec_ref not in spec_section_ids:
                errors.append(f"ADR {adr['id']} references missing spec ref {spec_ref}")
        for story_id in adr["story_refs"]:
            if story_id not in story_ids:
                errors.append(f"ADR {adr['id']} references missing story {story_id}")
        for compromise in adr["compromise_refs"]:
            if compromise not in compromise_ids:
                errors.append(f"ADR {adr['id']} references missing compromise {compromise}")
    for entry in evals:
        for story_id in entry["story_refs"]:
            if story_id not in story_ids:
                errors.append(f"eval {entry['id']} references missing story {story_id}")
        for compromise in entry["compromise_refs"]:
            if compromise not in compromise_ids:
                errors.append(f"eval {entry['id']} references missing compromise {compromise}")
    for campaign in state.get("roadmap", {}).get("campaigns", []):
        for story_ref in campaign.get("story_refs", []):
            if str(story_ref) not in story_ids:
                errors.append(f"state.roadmap.campaign {campaign.get('id')} references missing story {story_ref}")
    for domain_id, domain in state.get("architecture_audits", {}).get("domains", {}).items():
        for story_ref in domain.get("recent_story_refs", []):
            if str(story_ref) not in story_ids:
                errors.append(f"state.architecture_audits.domains.{domain_id} references missing story {story_ref}")
    for active_path in ACTIVE_SURFACE_PATHS:
        if not active_path.exists():
            continue
        for lineno, line in enumerate(read_text(active_path).splitlines(), start=1):
            if LIVE_BUILD_MAP_RE.search(line) and not ALLOWED_LEGACY_CONTEXT_RE.search(line):
                errors.append(f"{to_rel(active_path)}:{lineno} still treats build-map language as live")
            if MANUAL_STORIES_INDEX_RE.search(line) and not ALLOWED_GENERATED_INDEX_CONTEXT_RE.search(line):
                errors.append(f"{to_rel(active_path)}:{lineno} still treats docs/stories.md as hand-maintained")
    overdue = []
    cadence = state.get("architecture_audits", {}).get("cadence", {}).get("target_story_interval")
    for domain_id, domain in state.get("architecture_audits", {}).get("domains", {}).items():
        if domain.get("manual_priority") == "high" or domain.get("open_findings"):
            overdue.append(domain_id)
            continue
        if isinstance(cadence, int) and int(domain.get("stories_since_audit", 0)) >= cadence:
            overdue.append(domain_id)
    if overdue:
        warnings.append(f"architecture audit domains due: {', '.join(sorted(overdue))}")
    if legacy_story_ids:
        errors.append(
            f"stories still on legacy metadata: {len(legacy_story_ids)} ({', '.join(legacy_story_ids[:8])}{' ...' if len(legacy_story_ids) > 8 else ''})"
        )
    if nonstandard_statuses:
        warnings.append(
            f"stories with non-standard statuses: {len(nonstandard_statuses)} ({', '.join(nonstandard_statuses[:8])}{' ...' if len(nonstandard_statuses) > 8 else ''})"
        )
    if legacy_adr_ids:
        errors.append(
            f"ADRs still on legacy metadata only: {len(legacy_adr_ids)} ({', '.join(legacy_adr_ids)})"
        )
    return {"errors": errors, "warnings": warnings}


def status_rank(status: str) -> int:
    order = {
        "In Progress": 0,
        "Pending": 1,
        "Blocked": 2,
        "Draft": 3,
        "Done": 4,
        "Complete": 4,
        "To Do": 5,
        "Won't Do": 6,
        "Obsolete": 7,
    }
    return order.get(status, 99)


def render_stories_index(graph: dict[str, Any]) -> str:
    lines = [
        "# Stories",
        "",
        "> Generated from story metadata, `docs/methodology/state.yaml`, and `tests/fixtures/formats/_coverage-matrix.json`. Do not edit manually.",
        "",
    ]
    for section in graph["state"].get("stories_index", {}).get("sections", []):
        lines.extend([f"## {section['title']}", "", str(section["markdown"]).strip(), ""])
    roadmap = graph["state"].get("roadmap", {})
    if roadmap.get("active_focus") or roadmap.get("campaigns"):
        lines.extend(["## Active Focus", ""])
        if roadmap.get("active_focus"):
            lines.append(f"- Active categories: {', '.join(roadmap['active_focus'])}")
        for campaign in roadmap.get("campaigns", []):
            story_refs = ", ".join(str(ref) for ref in campaign.get("story_refs", [])) or "none"
            lines.append(f"- Campaign `{campaign['id']}` ({campaign['status']}; stories: {story_refs}) — {campaign['notes']}")
        lines.append("")
    lines.extend(
        [
            "## Index",
            "",
            "Grouped by primary `spec:N` category. Stories without category refs remain in an explicit historical bucket when no current category mapping is honest.",
            "",
        ]
    )
    grouped: dict[str, list[dict[str, Any]]] = {}
    uncategorized: list[dict[str, Any]] = []
    for story in graph["stories"]:
        if story["category_refs"]:
            grouped.setdefault(story["category_refs"][0], []).append(story)
        else:
            uncategorized.append(story)
    for stories in grouped.values():
        stories.sort(key=lambda story: (status_rank(story["status"]), story["priority"], int(story["id"])))
    uncategorized.sort(key=lambda story: (status_rank(story["status"]), story["priority"], int(story["id"])))
    for category in graph["spec"]["categories"]:
        stories = grouped.get(category["id"], [])
        if not stories:
            continue
        lines.extend([f"### {category['id']} — {category['title']}", "", "| ID | Title | Priority | Status | Depends On | Link |", "|---|---|---|---|---|---|"])
        for story in stories:
            depends_on = ", ".join(story["depends_on"]) if story["depends_on"] else "—"
            link = story["path"].replace("docs/", "")
            escaped_title = story["title"].replace("|", "\\|")
            lines.append(
                f"| {story['id']} | {escaped_title} | {story['priority']} | {story['status']} | {depends_on} | [story-{story['id']}]({link}) |"
            )
        lines.append("")
    if uncategorized:
        label = graph["state"].get("stories_index", {}).get("uncategorized_label", "Uncategorized")
        lines.extend([f"### {label}", "", "| ID | Title | Priority | Status | Link |", "|---|---|---|---|---|"])
        for story in uncategorized:
            link = story["path"].replace("docs/", "")
            escaped_title = story["title"].replace("|", "\\|")
            lines.append(
                f"| {story['id']} | {escaped_title} | {story['priority']} | {story['status']} | [story-{story['id']}]({link}) |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(graph: dict[str, Any]) -> None:
    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_PATH.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    STORIES_INDEX_PATH.write_text(render_stories_index(graph), encoding="utf-8")


def run_command(command: str) -> int:
    graph = build_graph()
    if graph["validation"]["errors"]:
        print("Methodology graph validation failed:", file=sys.stderr)
        for error in graph["validation"]["errors"]:
            print(f"- {error}", file=sys.stderr)
        return 1
    serialized = json.dumps(graph, indent=2) + "\n"
    rendered_index = render_stories_index(graph)
    if command == "print":
        print(serialized, end="")
        return 0
    if command == "check":
        if not GRAPH_PATH.exists():
            print(f"{to_rel(GRAPH_PATH)} does not exist. Run make methodology-compile.", file=sys.stderr)
            return 1
        if read_text(GRAPH_PATH) != serialized:
            print(f"{to_rel(GRAPH_PATH)} is out of date. Run make methodology-compile.", file=sys.stderr)
            return 1
        if read_text(STORIES_INDEX_PATH) != rendered_index:
            print(f"{to_rel(STORIES_INDEX_PATH)} is out of date. Run make methodology-compile.", file=sys.stderr)
            return 1
        print(f"Methodology graph is current: {to_rel(GRAPH_PATH)}")
        return 0
    write_outputs(graph)
    print(f"Wrote {to_rel(GRAPH_PATH)}")
    print(f"Wrote {to_rel(STORIES_INDEX_PATH)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "check", "print"], nargs="?", default="build")
    args = parser.parse_args()
    return run_command(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
