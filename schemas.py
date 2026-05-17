import hashlib
import json
import re
from pathlib import PurePosixPath
from typing import Any, Dict, List, Optional, Literal, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Choice(BaseModel):
    target: str
    text: Optional[str] = None


class CombatEnemy(BaseModel):
    enemy: Optional[str] = None
    skill: Optional[int] = None
    stamina: Optional[int] = None
    armour: Optional[int] = None
    firepower: Optional[int] = None
    speed: Optional[str] = None


class Vehicle(BaseModel):
    """Player vehicle/robot with secondary stats (ARMOUR, FIREPOWER, SPEED, COMBAT BONUS)"""

    name: str
    type: Optional[str] = None  # "robot", "vehicle", "mech", etc.
    armour: Optional[int] = None
    firepower: Optional[int] = None
    speed: Optional[str] = None  # "Slow", "Medium", "Fast", "Very Fast", etc.
    combat_bonus: Optional[int] = None  # May be positive or negative
    special_abilities: Optional[str] = None  # Full text description
    rules: Optional[List[Dict[str, Any]]] = (
        None  # Parsed structured rules (similar to combat.rules)
    )
    modifiers: Optional[List[Dict[str, Any]]] = (
        None  # Parsed stat modifiers (similar to combat.modifiers)
    )
    confidence: float = 1.0


class Combat(BaseModel):
    enemies: List[CombatEnemy] = Field(default_factory=list)
    outcomes: Optional[Dict[str, Any]] = None
    mode: Optional[str] = None
    style: Optional[str] = None
    rules: Optional[List[Dict[str, Any]]] = None
    modifiers: Optional[List[Dict[str, Any]]] = None
    triggers: Optional[List[Dict[str, Any]]] = None
    confidence: float = 1.0


class ItemEffect(BaseModel):
    description: Optional[str] = None
    delta_gold: Optional[int] = None
    delta_provisions: Optional[int] = None
    add_item: Optional[str] = None
    use_item: Optional[str] = None

    @model_validator(mode="after")
    def default_desc(self):
        if self.description:
            return self
        parts = []
        for key in ("delta_gold", "delta_provisions", "add_item", "use_item"):
            val = getattr(self, key)
            if val is not None:
                parts.append(f"{key}:{val}")
        self.description = "; ".join(parts) if parts else "effect"
        return self


class InventoryItem(BaseModel):
    item: str
    quantity: Union[int, str] = 1
    confidence: float = 1.0


class InventoryState(BaseModel):
    action: Literal["lose_all", "restore_all"]
    scope: str = "possessions"
    confidence: float = 1.0


class StateValue(BaseModel):
    key: str
    value: str
    confidence: float = 1.0
    source_text: Optional[str] = None


class StateCheck(BaseModel):
    key: Optional[str] = None
    condition_text: Optional[str] = None
    template_target: Optional[str] = None
    template_op: Optional[str] = None
    template_value: Optional[str] = None
    choice_text: Optional[str] = None
    has_target: Optional[str] = None
    missing_target: Optional[str] = None
    confidence: float = 1.0


class InventoryCheck(BaseModel):
    item: str
    condition: str = "if you have"  # "if you have", "if you possess", etc.
    target_section: Optional[str] = None
    confidence: float = 1.0


class InventoryEnrichment(BaseModel):
    items_gained: List[InventoryItem] = Field(default_factory=list)
    items_lost: List[InventoryItem] = Field(default_factory=list)
    items_used: List[InventoryItem] = Field(default_factory=list)
    inventory_checks: List[InventoryCheck] = Field(default_factory=list)
    inventory_states: List[InventoryState] = Field(default_factory=list)


class StatCheck(BaseModel):
    stat: Optional[Union[str, List[str]]] = None  # SKILL, LUCK, STAMINA, or list
    dice_roll: str = "2d6"
    dice_count: int = 2
    dice_sides: int = 6
    pass_condition: str = "success"  # e.g., "total <= stat" or "1-3"
    pass_section: str
    fail_condition: Optional[str] = None
    fail_section: Optional[str] = None
    confidence: float = 1.0


class TestLuck(BaseModel):
    lucky_section: str
    unlucky_section: str
    confidence: float = 1.0


class StatModification(BaseModel):
    stat: str  # skill, stamina, luck (lowercase normalized)
    amount: Union[int, str]
    scope: str = "section"
    reason: Optional[str] = None
    confidence: float = 1.0


class Paragraph(BaseModel):
    id: str
    page: int = 0
    text: str
    choices: List[Choice] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    combat: List[Combat] = Field(default_factory=list)
    test_luck: List[TestLuck] = Field(default_factory=list)
    stat_checks: List[StatCheck] = Field(default_factory=list)
    stat_modifications: List[StatModification] = Field(default_factory=list)
    item_effects: List[ItemEffect] = Field(default_factory=list)
    inventory: Optional[InventoryEnrichment] = None

    @field_validator("id")
    def id_is_numeric(cls, v):
        if not v.isdigit():
            raise ValueError("id must be numeric string")
        return v

    @field_validator("combat", mode="before")
    def combat_default(cls, v):
        if v is None:
            return []
        if isinstance(v, dict):
            return [v]
        return v

    @field_validator("item_effects", mode="before")
    def item_effects_default(cls, v):
        if v is None:
            return []
        if isinstance(v, dict):
            return [v]
        return v


class PageResult(BaseModel):
    paragraphs: List[Paragraph]


class PageDoc(BaseModel):
    schema_version: str = "page_doc_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    source: Optional[List[str]] = None
    created_at: Optional[str] = None
    page: int
    page_number: Optional[int] = None
    original_page_number: Optional[int] = None
    image: Optional[str] = None
    text: str
    source_path: Optional[str] = None


class PageImage(BaseModel):
    schema_version: str = "page_image_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    source: Optional[List[str]] = None
    created_at: Optional[str] = None
    page: int
    page_number: Optional[int] = None
    original_page_number: Optional[int] = None
    image: str
    spread_side: Optional[str] = None


class PageHtml(BaseModel):
    schema_version: str = "page_html_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    source: Optional[List[str]] = None
    created_at: Optional[str] = None
    page: int
    page_number: Optional[int] = None
    original_page_number: Optional[int] = None
    image: Optional[str] = None
    spread_side: Optional[str] = None
    # OCR diagnostics (optional; populated by AI OCR stage)
    ocr_quality: Optional[float] = None
    ocr_integrity: Optional[float] = None
    continuation_risk: Optional[float] = None
    ocr_metadata_warning: Optional[str] = None
    ocr_metadata_tag: Optional[str] = None
    ocr_metadata_missing: Optional[bool] = None
    ocr_empty: Optional[bool] = None
    ocr_empty_reason: Optional[str] = None
    raw_html: Optional[str] = None
    html: str
    printed_page_number: Optional[int] = None
    printed_page_number_text: Optional[str] = None
    printed_page_number_inferred: Optional[bool] = None
    images: Optional[List[Dict[str, Any]]] = None


class HtmlBlock(BaseModel):
    block_type: str
    text: str
    order: int
    attrs: Optional[Dict[str, Any]] = None
    element_id: Optional[str] = None


class PageHtmlBlocks(BaseModel):
    schema_version: str = "page_html_blocks_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    source: Optional[List[str]] = None
    created_at: Optional[str] = None
    page: int
    page_number: Optional[int] = None
    original_page_number: Optional[int] = None
    image: Optional[str] = None
    spread_side: Optional[str] = None
    is_blank: bool = False
    blocks: List[HtmlBlock] = Field(default_factory=list)


class PipelineIssues(BaseModel):
    schema_version: str = "pipeline_issues_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None
    summary: Dict[str, Any]
    issues: List[Dict[str, Any]]


class EdgecaseScanReport(BaseModel):
    schema_version: str = "edgecase_scan_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None
    summary: Dict[str, Any]
    issues: List[Dict[str, Any]]


class EdgecasePatchRecord(BaseModel):
    schema_version: str = "edgecase_patch_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None
    section_id: str
    reason_code: str
    path: str
    op: str
    value: Optional[Any] = None
    ai_rationale: Optional[str] = None


class EdgecasePatchReport(BaseModel):
    schema_version: str = "edgecase_patch_report_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None
    summary: Dict[str, Any]
    patches: List[Dict[str, Any]]


class TurnToLinksRecord(BaseModel):
    schema_version: str = "turn_to_links_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None
    section_id: str
    portion_id: Optional[str] = None
    pageStart: Optional[int] = None
    pageEnd: Optional[int] = None
    links: List[Dict[str, Any]]


class TurnToLinkClaim(BaseModel):
    schema_version: str = "turn_to_link_claims_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None
    section_id: str
    portion_id: Optional[str] = None
    target: str
    claim_type: str
    evidence_path: Optional[str] = None


class TurnToLinkClaimInline(BaseModel):
    target: str
    claim_type: str
    module_id: Optional[str] = None
    evidence_path: Optional[str] = None


class TurnToUnclaimedReport(BaseModel):
    schema_version: str = "turn_to_unclaimed_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None
    summary: Dict[str, Any]
    issues: List[Dict[str, Any]]


class PageLine(BaseModel):
    text: str
    source: Optional[str] = None  # e.g., "betterocr", "gpt4v", "llm_reconcile"
    meta: Optional[Dict[str, Any]] = (
        None  # engine-level details, confidences, alignment notes
    )
    bbox: Optional[List[float]] = (
        None  # Optional normalized bbox [x0,y0,x1,y1] when available (0-1)
    )


class PageLines(BaseModel):
    schema_version: str = "pagelines_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    source: Optional[List[str]] = None
    created_at: Optional[str] = None
    page: int
    page_number: Optional[int] = None
    original_page_number: Optional[int] = None
    image: Optional[str] = None
    lines: List[PageLine]
    disagreement_score: Optional[float] = None
    needs_escalation: bool = False
    # Optional provenance/quality fields (kept during driver stamping).
    # Many OCR modules emit these, and downstream adapters/guards rely on them.
    engines_raw: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    column_spans: Optional[List[List[float]]] = None
    column_confidence: Optional[Dict[str, Any]] = None
    ivr: Optional[float] = None
    inline_escalated: Optional[bool] = None
    spread_side: Optional[str] = None  # "L", "R", or None
    meta: Optional[Dict[str, Any]] = None
    escalation_reasons: Optional[List[str]] = None


class BoundingBox(BaseModel):
    x0: int
    y0: int
    x1: int
    y1: int
    section_id: Optional[str] = None


_DOC_WEB_ENTRY_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DOC_WEB_BLOCK_ID_RE = re.compile(r"^blk-[a-z0-9]+(?:-[a-z0-9]+)*-[0-9]{4}$")
_DOC_WEB_PREVIEW_MODULE_ID = "doc_web_preview_v1"
_DOC_WEB_SOURCE_ARTIFACT_EXTENSIONS = {
    ".csv",
    ".doc",
    ".docx",
    ".epub",
    ".heic",
    ".htm",
    ".html",
    ".jpeg",
    ".jpg",
    ".json",
    ".jsonl",
    ".md",
    ".pdf",
    ".png",
    ".rtf",
    ".tif",
    ".tiff",
    ".txt",
    ".webp",
    ".xls",
    ".xlsx",
    ".xml",
    ".zip",
}


def _validate_doc_web_entry_id(value: str, field_name: str) -> str:
    if not _DOC_WEB_ENTRY_ID_RE.fullmatch(value):
        raise ValueError(
            f"{field_name} must be lowercase kebab-case (example: chapter-010, page-002)"
        )
    return value


def _validate_doc_web_source_ref(value: str, field_name: str) -> str:
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise ValueError(
            f"{field_name} must be a privacy-safe sha256:<hex> source reference"
        )
    return value


def _validate_doc_web_sha256_ref(value: str, field_name: str) -> str:
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise ValueError(f"{field_name} must be a sha256:<hex> digest")
    return value


def _contains_doc_web_source_artifact_filename(value: str) -> bool:
    extensions = "|".join(
        re.escape(ext.lstrip(".")) for ext in sorted(_DOC_WEB_SOURCE_ARTIFACT_EXTENSIONS)
    )
    return bool(
        re.search(
            rf"(?i)(?<![A-Za-z0-9._-])[A-Za-z0-9][A-Za-z0-9._-]*"
            rf"\.(?:{extensions})(?![A-Za-z0-9])",
            value,
        )
    )


def _validate_doc_web_run_id(value: Optional[str]) -> Optional[str]:
    if value is None:
        return value
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value):
        raise ValueError("run_id must be a portable identifier")
    if _contains_doc_web_source_artifact_filename(value):
        raise ValueError("run_id must be a portable identifier")
    return value


class ChapterHtmlManifestEntry(BaseModel):
    """
    Transitional row schema for the current codex-forge chapter/page manifest.

    Story 152 formalizes this existing surface so current reviewed artifacts can be
    validated explicitly while the future `doc-web` bundle contract moves to a
    document-level manifest plus block-level provenance sidecars.
    """

    schema_version: str = "chapter_html_manifest_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None

    chapter_index: Optional[int] = None
    title: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    file: str
    kind: Literal["chapter", "page"]
    source_pages: Optional[List[int]] = None
    source_printed_pages: Optional[List[int]] = None
    source_portion_title: Optional[str] = None
    source_portion_page_start: Optional[int] = None
    source_portion_titles: Optional[List[str]] = None
    source_portion_page_starts: Optional[List[int]] = None

    @model_validator(mode="after")
    def validate_page_bounds(self):
        if (
            self.page_start is not None
            and self.page_end is not None
            and self.page_start > self.page_end
        ):
            raise ValueError("page_start cannot be greater than page_end")
        return self


class DocWebBundleEntry(BaseModel):
    """Single content document in the first formal `doc-web` bundle contract."""

    model_config = ConfigDict(extra="forbid")

    entry_id: str
    kind: Literal["chapter", "page"]
    title: str
    path: str
    order: int
    prev_entry_id: Optional[str] = None
    next_entry_id: Optional[str] = None
    source_pages: List[int] = Field(default_factory=list)
    printed_pages: List[int] = Field(default_factory=list)
    printed_page_start: Optional[int] = None
    printed_page_end: Optional[int] = None

    @field_validator("entry_id")
    @classmethod
    def validate_entry_id(cls, value: str) -> str:
        return _validate_doc_web_entry_id(value, "entry_id")

    @field_validator("prev_entry_id", "next_entry_id")
    @classmethod
    def validate_neighbor_entry_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _validate_doc_web_entry_id(value, "neighbor entry id")

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if not value.endswith(".html"):
            raise ValueError("doc-web bundle entry paths must point to .html files")
        return value

    @field_validator("order")
    @classmethod
    def validate_order(cls, value: int) -> int:
        if value < 1:
            raise ValueError("order must be >= 1")
        return value

    @model_validator(mode="after")
    def validate_entry_shape(self):
        expected_path = f"{self.entry_id}.html"
        if self.path != expected_path:
            raise ValueError(
                f"path must be the bundle-root HTML file '{expected_path}' for entry_id '{self.entry_id}'"
            )
        if self.printed_pages:
            start = min(self.printed_pages)
            end = max(self.printed_pages)
            if self.printed_page_start is None:
                self.printed_page_start = start
            if self.printed_page_end is None:
                self.printed_page_end = end
        if (
            self.printed_page_start is not None
            and self.printed_page_end is not None
            and self.printed_page_start > self.printed_page_end
        ):
            raise ValueError(
                "printed_page_start cannot be greater than printed_page_end"
            )
        return self


def _validate_bundle_relative_path(value: str, label: str) -> str:
    if not value:
        raise ValueError(f"{label} cannot be empty")
    if "\\" in value:
        raise ValueError(f"{label} must use POSIX '/' separators")
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
        raise ValueError(
            f"{label} cannot be URI, storage-key, or drive-prefixed paths"
        )
    path = PurePosixPath(value)
    if path.is_absolute():
        raise ValueError(f"{label} must be relative to the bundle root")
    if path.as_posix() == "." or any(
        part in {"", ".", ".."} for part in value.split("/")
    ):
        raise ValueError(f"{label} cannot contain empty, '.', or '..' parts")
    return value


class DocWebBundleFile(BaseModel):
    """Bundle file classification for portable snapshot/replay consumers."""

    model_config = ConfigDict(extra="forbid")

    _UNSAFE_ROLE_PRIVACY_CLASS = {
        "debug": "debug",
        "private": "private",
        "cache_local": "cache_local",
    }

    path: str
    role: Literal[
        "manifest",
        "index",
        "entry",
        "asset",
        "provenance",
        "preview_metadata",
        "preview_status",
        "selector_map",
        "cache_identity",
        "parsed_units",
        "debug",
        "private",
        "cache_local",
    ]
    safe_to_persist: bool = False
    safe_to_replay: bool = False
    privacy_class: Literal["portable", "debug", "private", "cache_local"] = "private"
    required_for_replay: bool = False

    @field_validator("path")
    @classmethod
    def validate_bundle_relative_path(cls, value: str) -> str:
        return _validate_bundle_relative_path(value, "bundle file paths")

    @model_validator(mode="after")
    def validate_file_safety(self):
        unsafe_privacy_class = self._UNSAFE_ROLE_PRIVACY_CLASS.get(self.role)
        if unsafe_privacy_class is not None:
            if self.privacy_class != unsafe_privacy_class:
                raise ValueError(
                    f"{self.role} bundle files must use privacy_class='{unsafe_privacy_class}'"
                )
            if self.safe_to_persist or self.safe_to_replay or self.required_for_replay:
                raise ValueError(
                    f"{self.role} bundle files must be marked unsafe for persist/replay"
                )
        if self.safe_to_persist or self.safe_to_replay:
            if self.privacy_class != "portable":
                raise ValueError("safe bundle files must use privacy_class='portable'")
        if self.required_for_replay and not self.safe_to_replay:
            raise ValueError("required_for_replay files must be safe_to_replay")
        if self.required_for_replay and not self.safe_to_persist:
            raise ValueError("required_for_replay files must be safe_to_persist")
        return self


class DocWebBundleManifest(BaseModel):
    """Document-level manifest for the first formal `doc-web` bundle contract."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "doc_web_bundle_manifest_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None

    document_id: str
    title: str
    creator: Optional[str] = None
    source_artifact: str
    index_path: str = "index.html"
    entries: List[DocWebBundleEntry]
    reading_order: List[str]
    asset_roots: List[str] = Field(default_factory=list)
    provenance_path: str = "provenance/blocks.jsonl"
    files: List[DocWebBundleFile] = Field(default_factory=list)

    @field_validator("run_id")
    @classmethod
    def validate_run_id(cls, value: Optional[str]) -> Optional[str]:
        return _validate_doc_web_run_id(value)

    @field_validator("asset_roots")
    @classmethod
    def validate_asset_roots(cls, value: List[str]) -> List[str]:
        for asset_root in value:
            _validate_bundle_relative_path(asset_root, "asset_roots")
        return value

    @model_validator(mode="after")
    def validate_manifest(self):
        if not self.entries:
            raise ValueError("entries cannot be empty")

        if self.index_path != "index.html":
            raise ValueError("index_path must be the bundle-root file 'index.html'")
        if self.provenance_path != "provenance/blocks.jsonl":
            raise ValueError(
                "provenance_path must be the bundle-local sidecar 'provenance/blocks.jsonl'"
            )

        entry_ids = [entry.entry_id for entry in self.entries]
        if len(set(entry_ids)) != len(entry_ids):
            raise ValueError("entry_ids must be unique")

        expected_orders = list(range(1, len(self.entries) + 1))
        actual_orders = [entry.order for entry in self.entries]
        if actual_orders != expected_orders:
            raise ValueError("entries must appear in contiguous reading order 1..N")

        if self.reading_order != entry_ids:
            raise ValueError(
                "reading_order must list each entry exactly once in entry order"
            )

        id_set = set(entry_ids)
        for index, entry in enumerate(self.entries):
            if entry.prev_entry_id and entry.prev_entry_id not in id_set:
                raise ValueError(
                    f"prev_entry_id '{entry.prev_entry_id}' not found in entries"
                )
            if entry.next_entry_id and entry.next_entry_id not in id_set:
                raise ValueError(
                    f"next_entry_id '{entry.next_entry_id}' not found in entries"
                )

            expected_prev = entry_ids[index - 1] if index > 0 else None
            expected_next = entry_ids[index + 1] if index + 1 < len(entry_ids) else None
            if entry.prev_entry_id != expected_prev:
                raise ValueError(
                    f"prev_entry_id for '{entry.entry_id}' must match reading-order adjacency"
                )
            if entry.next_entry_id != expected_next:
                raise ValueError(
                    f"next_entry_id for '{entry.entry_id}' must match reading-order adjacency"
                )

        is_preview_bundle = self.module_id == _DOC_WEB_PREVIEW_MODULE_ID
        if is_preview_bundle and not self.files:
            raise ValueError(
                "preview bundle manifests must include files with required replay paths"
            )

        if self.files:
            _validate_doc_web_source_ref(self.source_artifact, "source_artifact")

            file_paths = [file.path for file in self.files]
            if len(set(file_paths)) != len(file_paths):
                raise ValueError("bundle file manifest paths must be unique")

            files_by_path = {file.path: file for file in self.files}
            required_replay_paths = {
                "manifest.json",
                self.index_path,
                self.provenance_path,
                *[entry.path for entry in self.entries],
            }
            missing_paths = sorted(
                path for path in required_replay_paths if path not in files_by_path
            )
            if missing_paths:
                raise ValueError(
                    "bundle file manifest is missing required replay paths: "
                    + ", ".join(missing_paths)
                )

            for path in sorted(required_replay_paths):
                file = files_by_path[path]
                if not (
                    file.safe_to_persist
                    and file.safe_to_replay
                    and file.privacy_class == "portable"
                    and file.required_for_replay
                ):
                    raise ValueError(
                        "required replay paths must be portable, safe to persist, "
                        f"safe to replay, and marked required_for_replay: {path}"
                    )

            expected_roles_by_path = {
                "manifest.json": "manifest",
                self.index_path: "index",
                self.provenance_path: "provenance",
            }
            expected_roles_by_path.update(
                {entry.path: "entry" for entry in self.entries}
            )
            for path, expected_role in sorted(expected_roles_by_path.items()):
                if files_by_path[path].role != expected_role:
                    raise ValueError(
                        "bundle file manifest role does not match required path: "
                        f"{path} must use role='{expected_role}'"
                    )

            entry_paths = {entry.path for entry in self.entries}
            singleton_paths_by_role = {
                "manifest": {"manifest.json"},
                "index": {self.index_path},
                "provenance": {self.provenance_path},
            }
            for file in self.files:
                allowed_paths = (
                    entry_paths
                    if file.role == "entry"
                    else singleton_paths_by_role.get(file.role)
                )
                if allowed_paths is not None and file.path not in allowed_paths:
                    allowed_rendered = ", ".join(sorted(allowed_paths))
                    raise ValueError(
                        "bundle file manifest role/path pairing is invalid: "
                        f"role='{file.role}' must use path {allowed_rendered}"
                    )

            preview_replay_paths = {
                "preview_metadata.json",
                "preview_to_full_selectors.json",
                "cache/cache_identity.json",
                "cache/parsed_units.jsonl",
            }
            preview_roles = {
                "preview_metadata",
                "preview_status",
                "selector_map",
                "cache_identity",
                "parsed_units",
            }
            has_preview_files = is_preview_bundle or any(
                file.role in preview_roles or file.path in preview_replay_paths
                for file in self.files
            )
            if has_preview_files:
                missing_preview_paths = sorted(
                    path for path in preview_replay_paths if path not in files_by_path
                )
                if missing_preview_paths:
                    raise ValueError(
                        "preview bundle file manifest is missing required replay paths: "
                        + ", ".join(missing_preview_paths)
                    )
                for path in sorted(preview_replay_paths):
                    file = files_by_path[path]
                    if not (
                        file.safe_to_persist
                        and file.safe_to_replay
                        and file.privacy_class == "portable"
                        and file.required_for_replay
                    ):
                        raise ValueError(
                            "preview replay paths must be portable, safe to persist, "
                            f"safe to replay, and marked required_for_replay: {path}"
                        )
                preview_expected_roles_by_path = {
                    "preview_metadata.json": "preview_metadata",
                    "preview_status.jsonl": "preview_status",
                    "preview_to_full_selectors.json": "selector_map",
                    "cache/cache_identity.json": "cache_identity",
                    "cache/parsed_units.jsonl": "parsed_units",
                }
                for path, expected_role in sorted(
                    preview_expected_roles_by_path.items()
                ):
                    if path not in files_by_path:
                        continue
                    if files_by_path[path].role != expected_role:
                        raise ValueError(
                            "preview bundle file manifest role does not match "
                            f"required path: {path} must use role='{expected_role}'"
                        )
                preview_singleton_paths_by_role = {
                    expected_role: {path}
                    for path, expected_role in preview_expected_roles_by_path.items()
                }
                for file in self.files:
                    allowed_paths = preview_singleton_paths_by_role.get(file.role)
                    if allowed_paths is not None and file.path not in allowed_paths:
                        allowed_rendered = ", ".join(sorted(allowed_paths))
                        raise ValueError(
                            "preview bundle file manifest role/path pairing is invalid: "
                            f"role='{file.role}' must use path {allowed_rendered}"
                        )
        return self


class DocWebProvenanceBlock(BaseModel):
    """
    Paragraph/block-level provenance sidecar row for the first `doc-web` contract.

    The block_id doubles as the DOM anchor id that later emitter work should place
    directly on the rendered HTML block.
    """

    schema_version: str = "doc_web_provenance_block_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None

    block_id: str
    entry_id: str
    block_kind: Literal[
        "paragraph",
        "heading",
        "list_item",
        "table",
        "figure",
        "caption",
        "page_marker",
        "other",
    ]
    source_page_number: Optional[int] = None
    source_element_ids: List[str]
    source_printed_page_number: Optional[int] = None
    source_printed_page_label: Optional[str] = None
    source_bbox: Optional[BoundingBox] = None
    confidence: Optional[float] = None
    text_quote: Optional[str] = None

    @field_validator("run_id")
    @classmethod
    def validate_run_id(cls, value: Optional[str]) -> Optional[str]:
        return _validate_doc_web_run_id(value)

    @field_validator("block_id")
    @classmethod
    def validate_block_id(cls, value: str) -> str:
        if not _DOC_WEB_BLOCK_ID_RE.fullmatch(value):
            raise ValueError(
                "block_id must match blk-<entry-id>-<4-digit ordinal> (example: blk-chapter-010-0001)"
            )
        return value

    @field_validator("entry_id")
    @classmethod
    def validate_entry_id(cls, value: str) -> str:
        return _validate_doc_web_entry_id(value, "entry_id")

    @field_validator("source_page_number")
    @classmethod
    def validate_source_page_number(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value < 1:
            raise ValueError("source_page_number must be >= 1")
        return value

    @field_validator("source_element_ids")
    @classmethod
    def validate_source_element_ids(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError(
                "source_element_ids must contain at least one upstream element id"
            )
        return value

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return value

    @model_validator(mode="after")
    def validate_block_alignment(self):
        prefix = f"blk-{self.entry_id}-"
        if not self.block_id.startswith(prefix):
            raise ValueError("block_id must embed the matching entry_id prefix")
        return self


class DocWebPreviewUnit(BaseModel):
    """Page, record, entry, or document unit represented in preview coverage."""

    kind: Literal["page", "record", "entry", "document"]
    identifier: str
    included: bool
    reason: Optional[str] = None


class DocWebPreviewStatusEvent(BaseModel):
    """Progress event emitted by the synchronous preview path."""

    stage: Literal[
        "accepted",
        "preparing_pages",
        "detecting_text_or_ocr_need",
        "reading_sample",
        "building_preview_html",
        "preview_ready",
        "continuing_full_processing",
        "ready",
        "failed",
    ]
    elapsed_ms: float
    message: str
    artifact: Optional[str] = None
    detail: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("elapsed_ms")
    @classmethod
    def validate_elapsed_ms(cls, value: float) -> float:
        if value < 0:
            raise ValueError("elapsed_ms must be >= 0")
        return value


class DocWebPreviewContentHint(BaseModel):
    """Non-final high-level content hint derived from preview metadata/text."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["available", "deferred", "low_quality"]
    title_guess: Optional[str] = None
    document_kind_hint: str = "unknown"
    high_level_summary: str
    basis: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    text_quality_score: Optional[float] = None
    coverage_state: Optional[str] = None
    summary_provider: Optional[str] = None
    summary_model: Optional[str] = None
    summary_ms: Optional[float] = None
    summary_prompt_version: Optional[str] = None
    sample_sha256: Optional[str] = None
    cache_key: Optional[str] = None
    fallback_reason: Optional[str] = None

    @field_validator("text_quality_score")
    @classmethod
    def validate_text_quality_score(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        if not 0.0 <= value <= 1.0:
            raise ValueError("text_quality_score must be between 0.0 and 1.0")
        return value

    @field_validator("summary_ms")
    @classmethod
    def validate_summary_ms(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        if value < 0:
            raise ValueError("summary_ms must be >= 0")
        return value

    @field_validator("sample_sha256")
    @classmethod
    def validate_sample_sha256(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("sample_sha256 must be a lowercase SHA-256 hex digest")
        return value

    @field_validator("cache_key")
    @classmethod
    def validate_cache_key(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _validate_doc_web_sha256_ref(value, "cache_key")


class DocWebPreviewCacheSourceIdentity(BaseModel):
    """Privacy-safe source identity used to decide preview cache reuse."""

    model_config = ConfigDict(extra="forbid")

    source_ref: str
    source_sha256: str
    source_hash_algorithm: Literal["sha256"]
    source_hash_origin: str
    page_count: Optional[int] = None
    source_unit_count: Optional[int] = None
    source_display_label: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    @field_validator("source_ref")
    @classmethod
    def validate_source_ref(cls, value: str) -> str:
        return _validate_doc_web_source_ref(value, "source_identity.source_ref")

    @field_validator("source_sha256")
    @classmethod
    def validate_source_sha256(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError(
                "source_identity.source_sha256 must be a lowercase SHA-256 hex digest"
            )
        return value

    @field_validator("page_count", "source_unit_count")
    @classmethod
    def validate_counts(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value < 0:
            raise ValueError("source identity counts must be >= 0")
        return value

    @model_validator(mode="after")
    def validate_source_ref_matches_hash(self):
        if self.source_ref != f"sha256:{self.source_sha256}":
            raise ValueError(
                "source_identity.source_ref must match source_identity.source_sha256"
            )
        return self


class DocWebPreviewReusableArtifacts(BaseModel):
    """Bundle-relative artifacts reusable after cache identity match."""

    model_config = ConfigDict(extra="forbid")

    parsed_units: str
    selector_map: str

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    @field_validator("parsed_units", "selector_map")
    @classmethod
    def validate_reusable_artifact_path(cls, value: str) -> str:
        return DocWebBundleFile.validate_bundle_relative_path(value)


class DocWebPreviewCacheContentHintIdentity(BaseModel):
    """Cache-relevant content-hint inputs and outputs."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["auto", "ai", "deterministic"]
    effective_mode: Literal["ai", "deterministic"]
    provider: Optional[str] = None
    model: Optional[str] = None
    prompt_version: Optional[str] = None
    sample_sha256: Optional[str] = None
    cache_key: Optional[str] = None
    fallback_reason: Optional[str] = None
    requested_timeout_seconds: float

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    @field_validator("sample_sha256")
    @classmethod
    def validate_sample_sha256(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError(
                "content_hint.sample_sha256 must be a lowercase SHA-256 hex digest"
            )
        return value

    @field_validator("cache_key")
    @classmethod
    def validate_cache_key(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
            raise ValueError("content_hint.cache_key must be a sha256:<hex> digest")
        return value

    @field_validator("requested_timeout_seconds")
    @classmethod
    def validate_requested_timeout_seconds(cls, value: float) -> float:
        if value < 0:
            raise ValueError("requested_timeout_seconds must be >= 0")
        return value


class DocWebPreviewCacheIdentity(BaseModel):
    """Replay gate for portable preview cache artifacts."""

    model_config = ConfigDict(extra="forbid")

    identity_schema_version: Literal["doc_web_cache_identity_v1"]
    source_identity: DocWebPreviewCacheSourceIdentity
    doc_web_version: str
    doc_web_ref: str
    parser_settings: Dict[str, Any]
    runtime_options: Dict[str, Any]
    preview_contract_fingerprint: str
    bundle_fingerprint: str
    reusable_artifacts: DocWebPreviewReusableArtifacts
    content_hint: DocWebPreviewCacheContentHintIdentity
    identity_fingerprint: str

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    @field_validator(
        "preview_contract_fingerprint", "bundle_fingerprint", "identity_fingerprint"
    )
    @classmethod
    def validate_fingerprint(cls, value: str) -> str:
        return _validate_doc_web_sha256_ref(value, "cache identity fingerprints")

    def _expected_identity_fingerprint(self) -> str:
        source_identity = self.source_identity.model_dump()
        source_identity.pop("source_display_label", None)
        payload = {
            "source_identity": source_identity,
            "doc_web_version": self.doc_web_version,
            "doc_web_ref": self.doc_web_ref,
            "parser_settings": self.parser_settings,
            "runtime_options": self.runtime_options,
            "preview_contract_fingerprint": self.preview_contract_fingerprint,
            "bundle_fingerprint": self.bundle_fingerprint,
            "content_hint": self.content_hint.model_dump(),
        }
        encoded = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return f"sha256:{hashlib.sha256(encoded).hexdigest()}"

    @model_validator(mode="after")
    def validate_privacy_safe_strings(self):
        allowed_display_paths = {("source_identity", "source_display_label")}
        allowed_bundle_paths = {
            ("reusable_artifacts", "parsed_units"),
            ("reusable_artifacts", "selector_map"),
        }
        allowed_model_ref_paths = {
            ("runtime_options", "content_hint_model"),
            ("content_hint", "model"),
        }
        def walk(value: Any, path: tuple[str, ...]) -> None:
            if isinstance(value, BaseModel):
                walk(value.model_dump(), path)
                return
            if isinstance(value, dict):
                for key, child in value.items():
                    walk(child, (*path, str(key)))
                return
            if isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, (*path, str(index)))
                return
            if not isinstance(value, str):
                return
            if path in allowed_display_paths:
                return
            if path in allowed_bundle_paths:
                DocWebBundleFile.validate_bundle_relative_path(value)
                return
            if path in allowed_model_ref_paths:
                return
            if re.fullmatch(r"sha256:[0-9a-f]{64}", value):
                return
            if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
                raise ValueError("cache identity must not contain URI/storage paths")
            if value.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", value):
                raise ValueError("cache identity must not contain local source paths")
            if "\\" in value:
                raise ValueError("cache identity must not contain local source paths")
            if "/" in value:
                raise ValueError("cache identity must not contain relative source paths")
            if re.fullmatch(r"[0-9a-f]{64}\.[A-Za-z0-9]+", value):
                raise ValueError(
                    "cache identity must not use source hashes as filenames"
                )
            if _contains_doc_web_source_artifact_filename(value):
                raise ValueError("cache identity must not contain donor filenames")

        walk(self, ())
        expected = self._expected_identity_fingerprint()
        if self.identity_fingerprint != expected:
            raise ValueError(
                "identity_fingerprint must match cache identity fields"
            )
        return self


class DocWebPreviewMetadata(BaseModel):
    """Preview-mode metadata sidecar for latency-bound `doc-web` bundles."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "doc_web_preview_metadata_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None

    preview_mode: Literal["preview"] = "preview"
    status: Literal["preview_ready", "failed"]
    coverage_state: Literal["complete", "sampled", "partial", "deferred"]
    source_artifact: str
    source_sha256: str
    doc_web_version: str
    preview_contract_fingerprint: str
    parser_settings: Dict[str, Any] = Field(default_factory=dict)
    runtime_options: Dict[str, Any] = Field(default_factory=dict)
    structural_facts: Dict[str, Any] = Field(default_factory=dict)
    content_hint: Optional[DocWebPreviewContentHint] = None
    included_units: List[DocWebPreviewUnit] = Field(default_factory=list)
    skipped_units: List[DocWebPreviewUnit] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    unsupported_inferences: List[str] = Field(default_factory=list)
    status_events: List[DocWebPreviewStatusEvent]
    timing_ms: Dict[str, float] = Field(default_factory=dict)
    cache_identity: DocWebPreviewCacheIdentity
    artifacts: Dict[str, str] = Field(default_factory=dict)

    @field_validator("run_id")
    @classmethod
    def validate_run_id(cls, value: Optional[str]) -> Optional[str]:
        return _validate_doc_web_run_id(value)

    @field_validator("source_sha256")
    @classmethod
    def validate_source_sha256(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("source_sha256 must be a lowercase SHA-256 hex digest")
        return value

    @field_validator("source_artifact")
    @classmethod
    def validate_source_artifact(cls, value: str) -> str:
        return _validate_doc_web_source_ref(value, "source_artifact")

    @field_validator("preview_contract_fingerprint")
    @classmethod
    def validate_preview_contract_fingerprint(cls, value: str) -> str:
        return _validate_doc_web_sha256_ref(value, "preview_contract_fingerprint")

    @field_validator("timing_ms")
    @classmethod
    def validate_timing_ms(cls, value: Dict[str, float]) -> Dict[str, float]:
        for key, elapsed in value.items():
            if elapsed < 0:
                raise ValueError(f"timing_ms.{key} must be >= 0")
        return value

    @model_validator(mode="after")
    def validate_status_events(self):
        if self.source_artifact != f"sha256:{self.source_sha256}":
            raise ValueError("source_artifact must match source_sha256")
        if (
            self.cache_identity.source_identity.source_sha256 != self.source_sha256
            or self.cache_identity.source_identity.source_ref != self.source_artifact
        ):
            raise ValueError("cache_identity source identity must match preview source")
        if not self.status_events:
            raise ValueError("status_events cannot be empty")
        if self.status_events[0].stage != "accepted":
            raise ValueError("first preview status event must be accepted")
        if self.status == "failed" and self.status_events[-1].stage != "failed":
            raise ValueError("failed previews must end with a failed status event")
        if (
            self.status == "preview_ready"
            and self.status_events[-1].stage != "preview_ready"
        ):
            raise ValueError(
                "ready previews must end with a preview_ready status event"
            )
        return self


class DocWebPreviewSelectorMapping(BaseModel):
    """Selector continuity row from a preview block to a full-output selector."""

    model_config = ConfigDict(extra="forbid")

    preview_entry_id: str
    preview_block_id: Optional[str] = None
    full_entry_id: Optional[str] = None
    full_block_id: Optional[str] = None
    mapping_kind: Literal["preserved", "mapped", "deferred"]
    source_element_ids: List[str] = Field(default_factory=list)
    reason: Optional[str] = None

    @field_validator("preview_entry_id", "full_entry_id")
    @classmethod
    def validate_optional_entry_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _validate_doc_web_entry_id(value, "entry_id")

    @field_validator("preview_block_id", "full_block_id")
    @classmethod
    def validate_optional_block_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not _DOC_WEB_BLOCK_ID_RE.fullmatch(value):
            raise ValueError("block ids must match blk-<entry-id>-<4-digit ordinal>")
        return value

    @model_validator(mode="after")
    def validate_mapping(self):
        if self.mapping_kind == "preserved":
            if self.preview_block_id != self.full_block_id:
                raise ValueError("preserved mappings must keep identical block ids")
            if self.preview_entry_id != self.full_entry_id:
                raise ValueError("preserved mappings must keep identical entry ids")
        if self.mapping_kind == "mapped" and not self.full_entry_id:
            raise ValueError("mapped selector rows require full_entry_id")
        if self.mapping_kind == "deferred" and not self.reason:
            raise ValueError("deferred selector rows require a reason")
        return self


class DocWebPreviewSelectorMap(BaseModel):
    """Machine-readable selector continuity sidecar for preview bundles."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "doc_web_preview_selector_map_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None

    source_artifact: str
    source_sha256: str
    preview_contract_fingerprint: str
    mappings: List[DocWebPreviewSelectorMapping] = Field(default_factory=list)

    @field_validator("run_id")
    @classmethod
    def validate_run_id(cls, value: Optional[str]) -> Optional[str]:
        return _validate_doc_web_run_id(value)

    @field_validator("source_sha256")
    @classmethod
    def validate_source_sha256(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("source_sha256 must be a lowercase SHA-256 hex digest")
        return value

    @field_validator("source_artifact")
    @classmethod
    def validate_source_artifact(cls, value: str) -> str:
        return _validate_doc_web_source_ref(value, "source_artifact")

    @field_validator("preview_contract_fingerprint")
    @classmethod
    def validate_preview_contract_fingerprint(cls, value: str) -> str:
        return _validate_doc_web_sha256_ref(value, "preview_contract_fingerprint")

    @model_validator(mode="after")
    def validate_source_ref_matches_hash(self):
        if self.source_artifact != f"sha256:{self.source_sha256}":
            raise ValueError("source_artifact must match source_sha256")
        return self


class ImageCrop(BaseModel):
    schema_version: str = "image_crop_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    source: Optional[List[str]] = None
    created_at: Optional[str] = None
    page: int
    page_number: Optional[int] = None
    original_page_number: Optional[int] = None
    image: str
    boxes: List[BoundingBox]
    crops: List[str]


class CleanPage(BaseModel):
    schema_version: str = "clean_page_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    source: Optional[List[str]] = None
    created_at: Optional[str] = None
    page: int
    page_number: Optional[int] = None
    original_page_number: Optional[int] = None
    image: Optional[str] = None
    raw_text: str
    clean_text: str
    confidence: float


class PortionHypothesis(BaseModel):
    schema_version: str = "portion_hyp_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    source: Optional[List[str]] = None
    created_at: Optional[str] = None
    portion_id: Optional[str] = None
    page_start: int
    page_end: int
    page_start_original: Optional[int] = None
    page_end_original: Optional[int] = None
    title: Optional[str] = None
    type: Optional[str] = None
    confidence: float = 0.5
    notes: Optional[str] = None
    source_window: List[int] = Field(default_factory=list)
    source_pages: List[int] = Field(default_factory=list)
    continuation_of: Optional[str] = None
    continuation_confidence: Optional[float] = None
    raw_text: Optional[str] = None  # Text extracted from elements/pages
    element_ids: Optional[List[str]] = None  # Source element IDs for provenance
    macro_section: Optional[str] = None  # frontmatter | gameplay | endmatter


class LockedPortion(BaseModel):
    schema_version: str = "locked_portion_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    source: Optional[List[str]] = None
    created_at: Optional[str] = None
    portion_id: str
    page_start: int
    page_end: int
    page_start_original: Optional[int] = None
    page_end_original: Optional[int] = None
    title: Optional[str] = None
    type: Optional[str] = None
    confidence: float
    source_images: List[str] = Field(default_factory=list)
    continuation_of: Optional[str] = None
    continuation_confidence: Optional[float] = None
    raw_text: Optional[str] = None  # Text extracted from elements/pages
    element_ids: Optional[List[str]] = None  # Source element IDs for provenance
    macro_section: Optional[str] = None  # frontmatter | gameplay | endmatter


class ResolvedPortion(BaseModel):
    schema_version: str = "resolved_portion_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    source: Optional[List[str]] = None
    created_at: Optional[str] = None
    portion_id: str
    page_start: int
    page_end: int
    page_start_original: Optional[int] = None
    page_end_original: Optional[int] = None
    title: Optional[str] = None
    type: Optional[str] = None
    confidence: float = 0.0
    source_images: List[str] = Field(default_factory=list)
    orig_portion_id: Optional[str] = None
    continuation_of: Optional[str] = None
    continuation_confidence: Optional[float] = None
    raw_text: Optional[str] = None  # Text extracted from elements/pages
    element_ids: Optional[List[str]] = None  # Source element IDs for provenance
    macro_section: Optional[str] = None  # frontmatter | gameplay | endmatter


class EnrichedPortion(BaseModel):
    schema_version: str = "enriched_portion_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    source: Optional[List[str]] = None
    created_at: Optional[str] = None
    portion_id: str
    section_id: Optional[str] = None
    page_start: int
    page_end: int
    page_start_original: Optional[int] = None
    page_end_original: Optional[int] = None
    title: Optional[str] = None
    type: Optional[str] = None
    confidence: float = 0.0
    source_images: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = None
    raw_text_original: Optional[str] = None
    clean_text: Optional[str] = None
    raw_html: Optional[str] = None
    continuation_of: Optional[str] = None
    continuation_confidence: Optional[float] = None
    choices: List[Choice] = Field(default_factory=list)
    combat: List[Combat] = Field(default_factory=list)
    vehicle: Optional[Vehicle] = None
    test_luck: List[TestLuck] = Field(default_factory=list)
    stat_checks: List[StatCheck] = Field(default_factory=list)
    stat_modifications: List[StatModification] = Field(default_factory=list)
    item_effects: List[ItemEffect] = Field(default_factory=list)
    inventory: Optional[InventoryEnrichment] = None
    state_values: List[StateValue] = Field(default_factory=list)
    state_checks: List[StateCheck] = Field(default_factory=list)
    targets: List[str] = Field(default_factory=list)
    turn_to_links: List[str] = Field(default_factory=list)
    turn_to_claims: List[TurnToLinkClaimInline] = Field(default_factory=list)
    element_ids: Optional[List[str]] = None  # Source element IDs for provenance
    repair: Optional[Dict[str, Any]] = None
    repair_hints: Optional[Dict[str, Any]] = None
    context_correction: Optional[Dict[str, Any]] = None
    macro_section: Optional[str] = None  # frontmatter | gameplay | endmatter
    is_gameplay: Optional[bool] = None
    end_game: Optional[bool] = None
    ending: Optional[str] = None
    sequence: Optional[List[Dict[str, Any]]] = None

    @field_validator("combat", mode="before")
    def combat_default(cls, v):
        if v is None:
            return []
        if isinstance(v, dict):
            return [v]
        return v


class LLMCallUsage(BaseModel):
    schema_version: str = "instrumentation_call_v1"
    model: str
    provider: str = "openai"
    prompt_tokens: int
    completion_tokens: int
    cached: bool = False
    request_ms: Optional[float] = None
    request_id: Optional[str] = None
    cost: Optional[float] = None
    stage_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None

    @field_validator("prompt_tokens", "completion_tokens")
    def non_negative_tokens(cls, v):
        if v < 0:
            raise ValueError("token counts must be non-negative")
        return v

    @field_validator("request_ms")
    def non_negative_latency(cls, v):
        if v is not None and v < 0:
            raise ValueError("request_ms must be non-negative")
        return v


class StageInstrumentation(BaseModel):
    schema_version: str = "instrumentation_stage_v1"
    id: str
    stage: str
    module_id: Optional[str] = None
    status: str
    artifact: Optional[str] = None
    schema_version_output: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    wall_seconds: Optional[float] = None
    cpu_user_seconds: Optional[float] = None
    cpu_system_seconds: Optional[float] = None
    llm_calls: List[LLMCallUsage] = Field(default_factory=list)
    llm_totals: Dict[str, Any] = Field(default_factory=dict)
    extra: Dict[str, Any] = Field(default_factory=dict)


class RunInstrumentation(BaseModel):
    schema_version: str = "instrumentation_run_v1"
    run_id: str
    recipe_name: Optional[str] = None
    recipe_path: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    wall_seconds: Optional[float] = None
    cpu_user_seconds: Optional[float] = None
    cpu_system_seconds: Optional[float] = None
    stages: List[StageInstrumentation] = Field(default_factory=list)
    totals: Dict[str, Any] = Field(default_factory=dict)
    pricing: Dict[str, Any] = Field(default_factory=dict)
    env: Dict[str, Any] = Field(default_factory=dict)


class ContactSheetBBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

    @model_validator(mode="after")
    def positive_dims(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        return self


class ContactSheetTile(BaseModel):
    schema_version: str = "contact_sheet_manifest_v1"
    sheet_id: str
    tile_index: int = Field(ge=0)
    source_image: str
    display_number: int = Field(ge=0)
    sheet_path: str
    tile_bbox: Optional[ContactSheetBBox] = None
    orig_size: Optional[Dict[str, int]] = None  # {"width": int, "height": int}


class PageSpan(BaseModel):
    start_image: str
    end_image: str


class SectionPlan(BaseModel):
    label: str
    type: str
    page_spans: List[PageSpan] = Field(default_factory=list)
    notes: Optional[str] = None


class CapabilityGap(BaseModel):
    capability: str
    severity: Literal["missing", "partial"] = "missing"
    suggested_action: Optional[str] = None
    notes: Optional[str] = None
    pages: List[str] = Field(default_factory=list)


class SignalEvidence(BaseModel):
    signal: str
    pages: List[str] = Field(default_factory=list)
    reason: Optional[str] = None


class IntakePlan(BaseModel):
    schema_version: str = "intake_plan_v1"
    book_type: Literal[
        "novel",
        "cyoa",
        "genealogy",
        "textbook",
        "mixed",
        "other",
    ]
    type_confidence: Optional[float] = None
    sections: List[SectionPlan] = Field(default_factory=list)
    zoom_requests: List[str] = Field(default_factory=list)
    recommended_recipe: Optional[str] = None
    sectioning_strategy: Optional[str] = None
    assumptions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    signals: List[str] = Field(default_factory=list)
    sheets: List[str] = Field(default_factory=list)
    manifest_path: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    capability_gaps: List[CapabilityGap] = Field(default_factory=list)
    recommended_recipe: Optional[str] = None
    signal_evidence: List[SignalEvidence] = Field(default_factory=list)

    @field_validator("type_confidence")
    def confidence_range(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError("type_confidence must be between 0 and 1")
        return v


class IntakeHandoff(BaseModel):
    schema_version: str = "intake_handoff_v1"
    plan_path: str
    plan_run_id: Optional[str] = None
    recommended_recipe: Optional[str] = None
    source_input: Dict[str, Any] = Field(default_factory=dict)
    launch_input_flag: Optional[str] = None
    launch_input_path: Optional[str] = None
    driver_command: List[str] = Field(default_factory=list)
    downstream_run_id: Optional[str] = None
    downstream_output_dir: Optional[str] = None
    terminal_outcome: Literal["launched", "skipped", "blocked", "failed"]
    terminal_reason: Optional[str] = None
    exit_code: Optional[int] = None
    run_id: Optional[str] = None
    module_id: Optional[str] = None
    created_at: Optional[str] = None


def _validate_archive_member_path(value: str) -> str:
    rendered = str(value or "").strip()
    normalized = PurePosixPath(rendered)
    if not rendered:
        raise ValueError("archive member path must not be empty")
    if normalized.is_absolute():
        raise ValueError("archive member path must be archive-relative")
    if any(part == ".." for part in normalized.parts):
        raise ValueError("archive member path must not escape the archive root")
    if "." in normalized.parts:
        raise ValueError("archive member path must be normalized")
    return str(normalized)


class ArchiveMemberManifest(BaseModel):
    schema_version: str = "archive_member_manifest_v1"
    archive_format: str = "zip"
    archive_path: str
    member_id: str
    member_index: int = Field(ge=1)
    member_path: str
    extracted_path: str
    filename: str
    file_extension: Optional[str] = None
    detected_input_kind: Optional[str] = None
    file_size_bytes: int = Field(ge=0)
    sha256: Optional[str] = None
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None

    _member_path_relative = field_validator("member_path")(
        _validate_archive_member_path
    )


class ArchiveMemberRoute(BaseModel):
    schema_version: str = "archive_member_route_v1"
    archive_format: str = "zip"
    archive_path: str
    member_id: str
    member_index: int = Field(ge=1)
    member_path: str
    extracted_path: str
    filename: str
    file_extension: Optional[str] = None
    detected_input_kind: Optional[str] = None
    recommended_recipe: Optional[str] = None
    launch_input_flag: Optional[str] = None
    launch_input_path: Optional[str] = None
    driver_command: List[str] = Field(default_factory=list)
    downstream_run_id: Optional[str] = None
    downstream_output_dir: Optional[str] = None
    first_downstream_artifact: Optional[str] = None
    approval_mode: Optional[str] = None
    handoff_artifact_path: Optional[str] = None
    group_id: Optional[str] = None
    group_key: Optional[str] = None
    group_role: Optional[str] = None
    group_size: Optional[int] = Field(default=None, ge=1)
    terminal_outcome: Literal["launched", "skipped", "blocked", "failed"]
    terminal_reason: Optional[str] = None
    exit_code: Optional[int] = None
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None

    _member_path_relative = field_validator("member_path")(
        _validate_archive_member_path
    )


# ────────────────────────────────────────────────────────────────
# Document IR – Unstructured-native element representation
# ────────────────────────────────────────────────────────────────


class CodexMetadata(BaseModel):
    """
    Doc-forge metadata namespace for provenance and internal tracking.

    This is added to each Unstructured element to track our pipeline metadata
    without polluting the Unstructured fields.

    Note: This is serialized as '_codex' in JSON (see UnstructuredElement.model_dump).
    """

    run_id: Optional[str] = None
    module_id: Optional[str] = None
    sequence: Optional[int] = None  # Order within document (for stable sorting)
    created_at: Optional[str] = None


class UnstructuredElement(BaseModel):
    """
    Wrapper for Unstructured element serialized to JSON.

    This is the core Document IR format for doc-forge. We preserve Unstructured's
    native element structure (type, text, metadata) and add a 'codex' namespace
    for our provenance tracking.

    Unstructured provides rich element types:
    - Title, NarrativeText, Text, ListItem, Table, Image
    - Header, Footer, FigureCaption, PageBreak, etc.

    We preserve these exactly as Unstructured provides them, keeping all metadata:
    - metadata.page_number (1-based)
    - metadata.coordinates (bbox points)
    - metadata.text_as_html (for tables)
    - metadata.parent_id (hierarchy)
    - metadata.emphasized_text_contents, emphasized_text_tags
    - metadata.detection_class_prob (confidence scores)
    - ... and any other fields Unstructured provides

    This approach:
    - Keeps the IR rich and future-proof as Unstructured evolves
    - Avoids normalization complexity
    - Preserves all provenance and layout information
    - Makes downstream code simpler (one source of truth)

    Note: When serializing to JSON, use model_dump(by_alias=True) to get '_codex'
    instead of 'codex' in the output.
    """

    # Core Unstructured fields
    id: str  # Element ID from Unstructured or generated UUID
    type: str  # Unstructured element type (Title, NarrativeText, Table, etc.)
    text: str = ""  # Plain text content

    # Unstructured metadata (preserve all fields as-is)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Doc-forge namespace for our tracking (aliased to '_codex' in JSON)
    codex: CodexMetadata = Field(default_factory=CodexMetadata, alias="_codex")
    model_config = ConfigDict(
        # Allow extra fields for forward compatibility
        extra="allow",
        # Support both 'codex' and '_codex' when parsing
        populate_by_name=True,
    )


# ────────────────────────────────────────────────────────────────
# Numbered Section Pipeline Schemas
# ────────────────────────────────────────────────────────────────


class SectionBoundary(BaseModel):
    """
    AI-detected section boundary in a numbered-section document.

    This schema represents a single gameplay section detected by AI analysis.
    The AI scans elements to find numbered section headers and identifies the
    start/end element IDs that bound each section's content.
    """

    schema_version: str = "section_boundary_v1"
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    created_at: Optional[str] = None

    section_id: str  # "1", "2", "3", etc. (numbered section headers)
    start_element_id: str  # ID of first element in this section
    end_element_id: Optional[str] = (
        None  # ID of last element (None if extends to next section)
    )
    # Optional provenance helpers (code-first + vision escalation modules may emit these)
    start_page: Optional[int] = None
    start_line_idx: Optional[int] = None
    end_page: Optional[int] = None
    macro_section: Optional[str] = None  # frontmatter | gameplay | endmatter
    method: Optional[str] = None  # "code_filter" | "vision_escalation" | ...
    source: Optional[str] = (
        None  # "content_type_classification" | "escalation_cache" | ...
    )
    header_position: Optional[str] = None  # "top" | "middle" | "bottom" | "unknown"
    confidence: float  # 0.0-1.0, AI's confidence this is a real section boundary
    evidence: Optional[str] = None  # Why AI thinks this is a section boundary
    model_config = ConfigDict(extra="allow")


class BoundaryIssue(BaseModel):
    """Single boundary issue discovered during verification."""

    section_id: str
    severity: Literal["error", "warning"]
    message: str
    start_element_id: Optional[str] = None
    page: Optional[int] = None
    evidence: Optional[str] = None


class BoundaryVerificationReport(BaseModel):
    """Report produced by verify_boundaries_v1."""

    schema_version: str = "boundary_verification_v1"
    run_id: Optional[str] = None
    checked: int
    errors: List[BoundaryIssue] = Field(default_factory=list)
    warnings: List[BoundaryIssue] = Field(default_factory=list)
    ai_samples: List[Dict[str, Any]] = Field(default_factory=list)
    is_valid: bool = True


class ValidationReport(BaseModel):
    """
    Validation report for final structured document output.

    This schema captures quality checks on the final artifact payload,
    including missing sections, duplicates, and structural issues.
    """

    schema_version: str = "validation_report_v1"
    run_id: Optional[str] = None
    created_at: Optional[str] = None

    total_sections: int
    missing_sections: List[str] = Field(
        default_factory=list
    )  # Section IDs that should exist but don't
    duplicate_sections: List[str] = Field(
        default_factory=list
    )  # Section IDs appearing multiple times
    sections_with_no_text: List[str] = Field(default_factory=list)
    sections_with_no_choices: List[str] = Field(default_factory=list)
    unreachable_sections: List[str] = Field(
        default_factory=list
    )  # Sections unreachable from startSection (from Node validator)
    unreachable_entry_points: List[str] = Field(
        default_factory=list
    )  # Entry points: unreachable sections not referenced by other unreachable sections
    manual_navigation_sections: List[str] = Field(
        default_factory=list
    )  # Sections reachable via manual "turn to X" instructions (not code-extractable)

    is_valid: bool  # True if no critical errors
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    forensics: Optional[Dict[str, Any]] = None


# ────────────────────────────────────────────────────────────────
# Pipeline Redesign v2: Minimal IR Schemas
# ────────────────────────────────────────────────────────────────


class ElementLayout(BaseModel):
    """Layout information for an element (simplified from Unstructured metadata)."""

    h_align: str = "unknown"  # "left" | "center" | "right" | "unknown"
    y: Optional[float] = None  # Normalized vertical position 0-1 on page


class ElementCore(BaseModel):
    """
    Minimal internal IR schema for all AI operations.

    This schema reduces Unstructured's verbose IR to only the essential fields
    needed for section detection and boundary identification. All subsequent
    AI work depends only on elements_core.jsonl plus derived artifacts.

    Per pipeline redesign spec: {id, seq, page, kind, text, layout}
    No metadata fields (schema_version, module_id, run_id, created_at) to minimize
    AI workload and improve readability. Metadata lives in pipeline state/manifests.

    Derived from UnstructuredElement by:
    - Preserving id, text, page
    - Adding seq (0-based reading order index, preserved from original)
    - Mapping Unstructured types to simple "kind" categories
    - Extracting layout hints (alignment, vertical position)
    - Filtering out empty elements (text.strip() == "")
    """

    id: str  # Original element ID from Unstructured
    seq: int  # Global reading-order index (0-based, preserved from original elements_full)
    page: int  # Page number as reported by Unstructured (1-based)
    page_number: Optional[int] = None
    original_page_number: Optional[int] = None
    kind: str  # "text" | "image" | "table" | "other"
    text: str  # Raw text, normalized whitespace only (non-empty after filtering)
    layout: Optional[ElementLayout] = None  # Layout hints if available
    layout_role: Optional[str] = (
        None  # Optional upstream-provided role hint (e.g., TITLE, HEADER, FOOTER)
    )
    content_type: Optional[str] = (
        None  # DocLayNet label (or compatible), when available
    )
    content_type_confidence: Optional[float] = None  # 0.0-1.0
    content_subtype: Optional[Dict[str, Any]] = (
        None  # Small optional subtype payload (e.g., heading_level)
    )


class HeaderCandidate(BaseModel):
    """
    AI-classified header candidate from element-level analysis.

    This schema represents the output of Stage 1 (Header Classification), where AI
    analyzes each element to identify if it's a macro section header or game section header.
    This stage labels candidates only - it does not decide final section mapping.

    Per pipeline redesign spec v2: header_candidates.jsonl contains all elements with
    their classification results, not just positives, for downstream context.
    """

    seq: int  # Element sequence number (from elements_core)
    page: int  # Page number (from elements_core)
    macro_header: str = (
        "none"  # "none" | "cover" | "title_page" | "rules" | "introduction" | ...
    )
    game_section_header: bool = (
        False  # True if this is a numbered gameplay section header
    )
    claimed_section_number: Optional[int] = (
        None  # Section number (1-400) if game_section_header is true
    )
    confidence: float  # 0.0-1.0, AI's confidence in this classification
    text: Optional[str] = None  # Text content from elements_core (for verification)


class MacroSection(BaseModel):
    """Macro section (front_matter, game_sections region, etc.)"""

    id: str  # "front_matter", "game_sections", etc.
    start_seq: int  # Starting sequence number
    end_seq: int  # Ending sequence number
    confidence: float  # 0.0-1.0


class GameSectionStructured(BaseModel):
    """Game section with structured metadata from global analysis"""

    id: int  # Section number (1-400)
    start_seq: Optional[int] = None  # Starting sequence number (null if uncertain)
    status: Literal["certain", "uncertain"] = "certain"  # Status of this section
    confidence: float  # 0.0-1.0
    text: Optional[str] = (
        None  # Full text content from start_seq until next section (for verification)
    )
    text_length: Optional[int] = None  # Length of text in characters


class SectionsStructured(BaseModel):
    """
    Global structured view of document sections from Stage 2.

    This schema represents the output of Stage 2 (Global Structuring), where a single
    AI call analyzes header candidates to create a coherent global structure with
    macro sections and game sections.

    Per pipeline redesign spec v2: sections_structured.json contains macro sections
    (front_matter, game_sections) and game sections with strict ordering constraints.
    """

    macro_sections: List[
        MacroSection
    ]  # Macro sections (front_matter, game_sections region)
    game_sections: List[
        GameSectionStructured
    ]  # Game sections with status (certain/uncertain)


# ────────────────────────────────────────────────────────────────
# Run Configuration Schemas
# ────────────────────────────────────────────────────────────────


class ExecutionConfig(BaseModel):
    start_from: Optional[str] = None
    end_at: Optional[str] = None
    skip_done: bool = False
    force: bool = False
    dry_run: bool = False


class OptionsConfig(BaseModel):
    mock: bool = False
    no_validate: bool = False
    allow_run_id_reuse: bool = False
    dump_plan: bool = False


class InstrumentationConfig(BaseModel):
    enabled: bool = False
    price_table: Optional[str] = None


class RunConfig(BaseModel):
    """
    Structured configuration for a pipeline run.
    Captures all parameters previously passed as CLI arguments to driver.py.
    """

    run_id: Optional[str] = None
    recipe: str
    registry: str = "modules"
    settings: Optional[str] = None
    input_pdf: Optional[str] = None
    input_images: Optional[str] = None
    input_docx: Optional[str] = None
    input_xlsx: Optional[str] = None
    input_pptx: Optional[str] = None
    input_epub: Optional[str] = None
    input_html: Optional[str] = None
    input_eml: Optional[str] = None
    input_mbox: Optional[str] = None
    input_folder: Optional[str] = None
    input_zip: Optional[str] = None
    output_dir: Optional[str] = None

    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    options: OptionsConfig = Field(default_factory=OptionsConfig)
    instrumentation: InstrumentationConfig = Field(
        default_factory=InstrumentationConfig
    )
