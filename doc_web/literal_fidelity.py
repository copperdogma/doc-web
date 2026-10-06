"""Typed source-only table review and qualification contracts."""
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class UncertainCell(StrictRecord):
    row: int = Field(ge=0)
    cell: int = Field(ge=0)
    reason: str = Field(min_length=1)
    alternatives: list[str]


class SourceTableReview(StrictRecord):
    bbox: list[float] = Field(min_length=4, max_length=4)
    html: str
    uncertain_cells: list[UncertainCell]


class SourcePageReview(StrictRecord):
    source_table_count: int = Field(ge=0)
    tables: list[SourceTableReview]

    @model_validator(mode="after")
    def inventory_matches(self):
        if self.source_table_count != len(self.tables):
            raise ValueError("Incomplete source table inventory")
        return self


class SourceFileIdentity(StrictRecord):
    name: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class TableResolution(StrictRecord):
    table: int = Field(ge=0)
    bbox: list[float] = Field(min_length=4, max_length=4)
    initial_html: str
    review: SourceTableReview
    comparison: dict[str, Any]
    decision: Literal["initial_agrees_B", "unresolved"]
    reason: str


class LiteralFidelityReport(StrictRecord):
    schema_version: Literal["literal_fidelity_report_v1"] = "literal_fidelity_report_v1"
    policy_version: str = "source-only-table-review-v1"
    run_id: str
    upstream_run_id: str | None = None
    logical_page_number: int = Field(ge=1)
    original_page_number: int = Field(ge=1)
    source_pdf: SourceFileIdentity | None
    image_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    image_dimensions: list[int] = Field(min_length=2, max_length=2)
    initial_raw_html_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    reviewed_table_sequence_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    status: Literal["verified", "unresolved"]
    table_count: int = Field(ge=0)
    unresolved_count: int = Field(ge=0)
    tables: list[TableResolution]
    errors: list[str]
    requests: list[dict[str, Any]]


class LiteralFidelityReceipt(StrictRecord):
    schema_version: Literal["literal_fidelity_receipt_v1"] = "literal_fidelity_receipt_v1"
    policy_version: str = "source-only-table-review-v1"
    run_id: str
    status: Literal["verified", "unresolved"]
    logical_page_number: int = Field(ge=1)
    original_page_number: int = Field(ge=1)
    image_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_pdf_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    reviewed_table_sequence_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    report_path: str
    report_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    table_count: int = Field(ge=0)
    unresolved_count: int = Field(ge=0)

    @model_validator(mode="after")
    def verified_is_complete(self):
        if self.status == "verified" and self.unresolved_count:
            raise ValueError("Verified table receipt has unresolved items")
        return self
