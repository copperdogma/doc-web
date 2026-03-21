from __future__ import annotations

from functools import lru_cache
import re
from typing import Any, ClassVar

SUMMARY_LABELS = ("TOTAL DESCENDANTS", "LIVING", "DECEASED")
FAMILY_HEADING_RE = re.compile(r"\b[A-Z][A-Z'’\-]+(?:\s+[A-Z][A-Z'’\-]+)*\s+FAMILY\b")
GENERATION_CONTEXT_RE = re.compile(
    r"\b(?:great\s+grandchildren|grandchildren|children)\b",
    re.IGNORECASE,
)
CONTEXT_LINE_RE = re.compile(
    r"(?:[A-Z][\w.\-]*\s+)*[A-Z][\w.\-]*['’](?:s)?\s+"
    r"(?:Great\s+Great\s+Grandchildren|Great\s+Grandchildren|Grandchildren|Children)\b"
)
COMBINED_BOY_GIRL_RE = re.compile(r"\bBOY\s*/?\s*GIRL\b", re.IGNORECASE)


def normalize_text(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("’", "'")).strip()


def extract_family_labels(text: str) -> list[str]:
    normalized = normalize_text(text).upper()
    return list(dict.fromkeys(FAMILY_HEADING_RE.findall(normalized)))


def is_generation_context_text(text: str) -> bool:
    normalized = normalize_text(text)
    if not normalized or len(normalized) > 160:
        return False
    if extract_family_labels(normalized):
        return False
    if any(label in normalized.upper() for label in SUMMARY_LABELS):
        return False
    return bool(GENERATION_CONTEXT_RE.search(normalized))


def extract_terminal_family_heading(text: str) -> str | None:
    normalized = normalize_text(text)
    if not normalized:
        return None

    words = normalized.upper().split()
    if not words or words[-1] != "FAMILY":
        return None

    stop_tokens = {"CHILDREN", "GRANDCHILDREN", "DESCENDANTS", "LIVING", "DECEASED"}
    start = len(words) - 1
    saw_possessive = False
    while start > 0:
        prev = words[start - 1]
        token = prev.replace("'", "").replace("-", "")
        if token == "GREAT" or token in stop_tokens:
            break
        start -= 1
        if "'" in prev:
            saw_possessive = True

    candidate = " ".join(words[start:])
    if saw_possessive and FAMILY_HEADING_RE.fullmatch(candidate):
        return candidate
    return None


def canonical_family_heading(text: str) -> str:
    normalized = normalize_text(text)
    family = extract_terminal_family_heading(normalized)
    if family:
        return family
    families = extract_family_labels(normalized)
    if families:
        return families[-1]
    return normalized


def has_combined_boy_girl_header(text: str) -> bool:
    return bool(COMBINED_BOY_GIRL_RE.search(normalize_text(text)))


def should_promote_heading_cell(
    *,
    text: str,
    start_col_offset_idx: int,
    end_col_offset_idx: int,
    row_cell_count: int,
    num_cols: int,
    row_section: bool,
) -> bool:
    normalized = normalize_text(text)
    if not normalized:
        return False
    if row_section:
        return True
    if not (extract_family_labels(normalized) or is_generation_context_text(normalized)):
        return False
    if row_cell_count == 1:
        return True
    span = end_col_offset_idx - start_col_offset_idx
    return span >= max(4, num_cols - 1)


@lru_cache(maxsize=1)
def _load_docling_types() -> tuple[type[Any], type[Any], type[Any], type[Any]]:
    from typing import Sequence, Type

    from docling.datamodel.base_models import Page, Table, TableStructurePrediction
    from docling.datamodel.document import ConversionResult
    from docling.datamodel.pipeline_options import (
        BaseTableStructureOptions,
        TableFormerMode,
        TableStructureOptions,
    )
    from docling.models.base_table_model import BaseTableStructureModel
    from docling.models.stages.table_structure.table_structure_model import (
        TableStructureModel,
    )
    from docling_core.types.doc import TableCell

    class OnwardTableStructureOptions(BaseTableStructureOptions):
        kind: ClassVar[str] = "onward_table_structure_v1"
        delegate_do_cell_matching: bool = True
        delegate_mode: TableFormerMode = TableFormerMode.ACCURATE
        promote_heading_like_rows: bool = True
        split_combined_boy_girl_headers: bool = True

    def _full_width_heading_cell(
        *,
        row_idx: int,
        num_cols: int,
        text: str,
    ) -> TableCell:
        return TableCell(
            start_row_offset_idx=row_idx,
            end_row_offset_idx=row_idx + 1,
            start_col_offset_idx=0,
            end_col_offset_idx=num_cols,
            row_span=1,
            col_span=num_cols,
            text=text,
            column_header=False,
            row_header=False,
            row_section=True,
        )

    def _split_combined_header(cell: TableCell) -> list[TableCell]:
        span = cell.end_col_offset_idx - cell.start_col_offset_idx
        if span < 2:
            return [cell]
        split_at = cell.start_col_offset_idx + max(1, span // 2)
        left = cell.model_copy(
            update={
                "text": "BOY",
                "end_col_offset_idx": split_at,
                "col_span": split_at - cell.start_col_offset_idx,
            }
        )
        right = cell.model_copy(
            update={
                "text": "GIRL",
                "start_col_offset_idx": split_at,
                "col_span": cell.end_col_offset_idx - split_at,
            }
        )
        return [left, right]

    def _normalize_table(table: Table, options: OnwardTableStructureOptions) -> Table:
        rows: dict[int, list[TableCell]] = {}
        for cell in table.table_cells:
            rows.setdefault(cell.start_row_offset_idx, []).append(cell)

        normalized_cells: list[TableCell] = []
        for row_idx in sorted(rows):
            row_cells = sorted(
                rows[row_idx],
                key=lambda item: (item.start_col_offset_idx, item.end_col_offset_idx),
            )

            promoted_text: str | None = None
            if options.promote_heading_like_rows:
                for cell in row_cells:
                    if should_promote_heading_cell(
                        text=cell.text,
                        start_col_offset_idx=cell.start_col_offset_idx,
                        end_col_offset_idx=cell.end_col_offset_idx,
                        row_cell_count=len(row_cells),
                        num_cols=table.num_cols,
                        row_section=cell.row_section,
                    ):
                        promoted_text = canonical_family_heading(cell.text)
                        break

            if promoted_text:
                normalized_cells.append(
                    _full_width_heading_cell(
                        row_idx=row_idx,
                        num_cols=table.num_cols,
                        text=promoted_text,
                    )
                )
                continue

            for cell in row_cells:
                rewritten = cell.model_copy(
                    update={
                        "text": canonical_family_heading(cell.text)
                        if cell.row_section
                        else cell.text
                    }
                )
                if (
                    options.split_combined_boy_girl_headers
                    and rewritten.column_header
                    and has_combined_boy_girl_header(rewritten.text)
                ):
                    normalized_cells.extend(_split_combined_header(rewritten))
                else:
                    normalized_cells.append(rewritten)

        return table.model_copy(update={"table_cells": normalized_cells})

    def _normalize_prediction(
        prediction: TableStructurePrediction,
        options: OnwardTableStructureOptions,
    ) -> TableStructurePrediction:
        normalized_table_map = {
            table_id: _normalize_table(table, options)
            for table_id, table in prediction.table_map.items()
        }
        return prediction.model_copy(update={"table_map": normalized_table_map})

    class OnwardTableStructureModel(BaseTableStructureModel):
        def __init__(
            self,
            enabled: bool,
            artifacts_path,
            options: OnwardTableStructureOptions,
            accelerator_options,
            enable_remote_services: bool = False,
        ):
            self.enabled = enabled
            self.options = options
            delegate_options = TableStructureOptions(
                do_cell_matching=options.delegate_do_cell_matching,
                mode=options.delegate_mode,
            )
            self.delegate = TableStructureModel(
                enabled=enabled,
                artifacts_path=artifacts_path,
                options=delegate_options,
                accelerator_options=accelerator_options,
                enable_remote_services=enable_remote_services,
            )

        @classmethod
        def get_options_type(cls) -> Type[OnwardTableStructureOptions]:
            return OnwardTableStructureOptions

        def predict_tables(
            self,
            conv_res: ConversionResult,
            pages: Sequence[Page],
        ) -> Sequence[TableStructurePrediction]:
            predictions = self.delegate.predict_tables(conv_res, pages)
            if not self.enabled:
                return predictions
            return [
                _normalize_prediction(prediction, self.options)
                for prediction in predictions
            ]

    return OnwardTableStructureOptions, OnwardTableStructureModel, TableCell, Table


def build_table_structure_options(**overrides: Any) -> Any:
    options_cls, _, _, _ = _load_docling_types()
    return options_cls(**overrides)


def table_structure_engines() -> dict[str, list[type[Any]]]:
    _, model_cls, _, _ = _load_docling_types()
    return {"table_structure_engines": [model_cls]}
