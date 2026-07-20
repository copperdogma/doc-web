from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from schemas import PageHtml
from scripts.spikes.unlimited_ocr_benchmark import (
    MAX_GROUNDING_BOXES,
    _generation_cap_assessment,
    _select_best_candidate,
    build_page_html_rows,
    decide_adoption,
    markdown_to_html,
    parse_grounded_output,
    run_space,
    validate_transport,
)


def _valid_two_page_output() -> str:
    return """<PAGE>
| Name | Year |
| --- | --- |
| <|ref|>Lessard<|/ref|><|det|>[10, 20, 300, 80]<|/det|> | 19O1 |
<PAGE>
<|ref|>Second family<|/ref|><|det|>[[15, 25, 350, 90], [20, 100, 360, 180]]<|/det|>
"""


def _parse_two_pages() -> dict:
    return parse_grounded_output(
        _valid_two_page_output(),
        expected_pages=2,
        source_pages=[79, 80],
    )


def _onward_case(
    case_id: str,
    *,
    incumbent_score: float,
    candidate_score: float,
    routing_signal: str = "flagged_genealogy_table_group",
    transport_ok: bool = True,
    material_page_fidelity_loss: bool = False,
) -> dict:
    return {
        "case_id": case_id,
        "incumbent_score": incumbent_score,
        "candidate_score": candidate_score,
        "routing_signal": routing_signal,
        "transport_ok": transport_ok,
        "material_page_loss": material_page_fidelity_loss,
    }


def _error_text(report: dict) -> str:
    return " ".join(str(error) for error in report["errors"]).casefold()


def _complete_failing_handwriting_pair() -> list[dict]:
    return [
        {
            "case_id": case_id,
            "overall_ratio": 0.5,
            "page_min_ratio": 0.5,
            "pass_rate": 0.0,
        }
        for case_id in ("barney", "alverson")
    ]


def test_parse_grounded_output_preserves_page_order_and_grounding() -> None:
    parsed = _parse_two_pages()

    assert parsed["page_count"] == 2
    assert parsed["preamble"].strip() == ""
    assert parsed["raw"] == _valid_two_page_output()
    assert [page["page"] for page in parsed["pages"]] == [1, 2]
    assert [page["source_page"] for page in parsed["pages"]] == [79, 80]

    first, second = parsed["pages"]
    assert "<|ref|>Lessard<|/ref|>" in first["raw_markdown"]
    assert "<|det|>[10, 20, 300, 80]<|/det|>" in first["raw_markdown"]
    assert first["blocks"] == [
        {
            "label": "Lessard",
            "raw_coordinates": "[10, 20, 300, 80]",
            "boxes": [[10, 20, 300, 80]],
        }
    ]
    assert first["clean_markdown"].count("Lessard") == 1
    assert "<|ref|>" not in first["clean_markdown"]
    assert "<|det|>" not in first["clean_markdown"]

    assert second["blocks"] == [
        {
            "label": "Second family",
            "raw_coordinates": "[[15, 25, 350, 90], [20, 100, 360, 180]]",
            "boxes": [[15, 25, 350, 90], [20, 100, 360, 180]],
        }
    ]
    assert parsed["malformed_coordinates"] == []
    assert parsed["out_of_range_coordinates"] == []


@pytest.mark.parametrize(
    ("raw", "expected_pages", "source_pages", "failure_word"),
    [
        ("<PAGE>only one", 2, [79, 80], "missing"),
        ("<PAGE>one<PAGE>two<PAGE>three", 2, [79, 80], "extra"),
    ],
)
def test_validate_transport_rejects_missing_and_extra_pages(
    raw: str,
    expected_pages: int,
    source_pages: list[int],
    failure_word: str,
) -> None:
    parsed = parse_grounded_output(
        raw,
        expected_pages=expected_pages,
        source_pages=source_pages,
    )

    report = validate_transport(parsed, expected_pages=expected_pages)

    assert report["ok"] is False
    assert failure_word in _error_text(report) or "page" in _error_text(report)


def test_validate_transport_rejects_reordered_parsed_pages() -> None:
    parsed = _parse_two_pages()
    parsed["pages"] = [parsed["pages"][1], parsed["pages"][0]]

    report = validate_transport(
        parsed,
        expected_pages=2,
        expected_source_pages=[79, 80],
    )

    assert report["ok"] is False
    assert "order" in _error_text(report)


def test_validate_transport_rejects_non_whitespace_preamble() -> None:
    parsed = parse_grounded_output(
        "unexpected prose<PAGE>page one<PAGE>page two",
        expected_pages=2,
        source_pages=[79, 80],
    )

    report = validate_transport(parsed, expected_pages=2)

    assert report["ok"] is False
    assert "before the first <page>" in _error_text(report)


@pytest.mark.parametrize(
    "coordinates",
    [
        "[-1, 20, 30, 40]",
        "[0, 20, 1001, 40]",
        "[[10, 20, 30, 40], [50, 60, 70, 1001]]",
    ],
)
def test_out_of_range_coordinates_are_diagnostic_transport_failures(
    coordinates: str,
) -> None:
    parsed = parse_grounded_output(
        f"<PAGE><|ref|>bad box<|/ref|><|det|>{coordinates}<|/det|>",
        expected_pages=1,
        source_pages=[79],
    )

    assert parsed["out_of_range_coordinates"]
    report = validate_transport(parsed, expected_pages=1)
    assert report["ok"] is False
    assert "coordinate" in _error_text(report)


@pytest.mark.parametrize(
    "coordinates",
    [
        "not-json",
        "[10, 20, 30]",
        '{"x": 10, "y": 20}',
        "[[10, 20, 30, 40], [broken]]",
    ],
)
def test_malformed_coordinate_text_is_rejected_safely(coordinates: str) -> None:
    parsed = parse_grounded_output(
        f"<PAGE><|ref|>bad box<|/ref|><|det|>{coordinates}<|/det|>",
        expected_pages=1,
        source_pages=[79],
    )

    assert parsed["malformed_coordinates"]
    report = validate_transport(parsed, expected_pages=1)
    assert report["ok"] is False
    assert "coordinate" in _error_text(report)


def test_hostile_coordinate_text_is_not_executed(tmp_path: Path) -> None:
    sentinel = tmp_path / "parser-must-not-create-this"
    hostile = f"__import__('pathlib').Path({str(sentinel)!r}).touch()"

    parsed = parse_grounded_output(
        f"<PAGE><|ref|>hostile<|/ref|><|det|>{hostile}<|/det|>",
        expected_pages=1,
        source_pages=[79],
    )

    assert parsed["malformed_coordinates"]
    assert not sentinel.exists()
    assert validate_transport(parsed, expected_pages=1)["ok"] is False


def test_oversized_coordinate_literal_is_rejected_before_literal_eval() -> None:
    oversized = "[" + ",".join("0" for _ in range(20_000)) + "]"

    parsed = parse_grounded_output(
        f"<PAGE><|ref|>oversized<|/ref|><|det|>{oversized}<|/det|>",
        expected_pages=1,
        source_pages=[79],
    )

    assert len(parsed["malformed_coordinates"]) == 1
    assert "safety limit" in parsed["malformed_coordinates"][0]["reason"]
    assert validate_transport(parsed, expected_pages=1)["ok"] is False


def test_excessively_nested_coordinate_literal_is_rejected_before_literal_eval() -> (
    None
):
    coordinates = "[[[[[[0, 0, 10, 10]]]]]]"

    parsed = parse_grounded_output(
        f"<PAGE><|ref|>nested<|/ref|><|det|>{coordinates}<|/det|>",
        expected_pages=1,
        source_pages=[79],
    )

    assert len(parsed["malformed_coordinates"]) == 1
    assert "nesting safety limit" in parsed["malformed_coordinates"][0]["reason"]


def test_excessive_grounding_box_count_is_rejected() -> None:
    coordinates = (
        "[" + ",".join("[0, 0, 10, 10]" for _ in range(MAX_GROUNDING_BOXES + 1)) + "]"
    )

    parsed = parse_grounded_output(
        f"<PAGE><|ref|>boxes<|/ref|><|det|>{coordinates}<|/det|>",
        expected_pages=1,
        source_pages=[79],
    )

    assert len(parsed["malformed_coordinates"]) == 1
    assert "box safety limit" in parsed["malformed_coordinates"][0]["reason"]


def test_adjacent_ref_det_pair_is_not_duplicated_as_det_only_block() -> None:
    parsed = parse_grounded_output(
        "<PAGE><|ref|>Lessard<|/ref|><|det|>[10, 20, 300, 80]<|/det|>",
        expected_pages=1,
        source_pages=[79],
    )

    assert len(parsed["pages"][0]["blocks"]) == 1
    assert parsed["pages"][0]["blocks"][0]["label"] == "Lessard"


def test_det_only_grounding_form_is_retained_and_removed_from_clean_text() -> None:
    raw = "<PAGE><|det|>title [9, 7, 904, 121]<|/det|>A Powdery Surface"

    parsed = parse_grounded_output(raw, expected_pages=1, source_pages=[1])

    assert parsed["pages"][0]["blocks"] == [
        {
            "label": "title",
            "raw_coordinates": "[9, 7, 904, 121]",
            "boxes": [[9, 7, 904, 121]],
        }
    ]
    assert parsed["pages"][0]["clean_markdown"] == "A Powdery Surface"
    assert validate_transport(parsed, expected_pages=1)["ok"] is True


def test_markdown_to_html_converts_pipe_table_without_repairing_cells() -> None:
    markdown = """Introduction

| Name | Year | Note |
| --- | ---: | --- |
| Le ssard | 19O1 | A & B |
"""

    html = markdown_to_html(markdown)

    assert "<table" in html
    assert "<th>Name</th>" in html
    assert "<th>Year</th>" in html
    assert "<td>Le ssard</td>" in html
    assert "<td>19O1</td>" in html
    assert "1901" not in html
    assert "Lessard" not in html
    assert "A &amp; B" in html


def test_build_page_html_rows_emits_schema_valid_source_mapped_rows() -> None:
    parsed = _parse_two_pages()
    source_paths = ["/fixtures/Image079.jpg", "/fixtures/Image080.jpg"]

    rows = build_page_html_rows(
        parsed,
        source_paths=source_paths,
        run_id="story230-test",
        module_id="unlimited_ocr_benchmark",
    )

    assert [row["page"] for row in rows] == [79, 80]
    assert [row["page_number"] for row in rows] == [79, 80]
    assert [row["original_page_number"] for row in rows] == [79, 80]
    assert [row["source"] for row in rows] == [[source_paths[0]], [source_paths[1]]]
    assert all(row["schema_version"] == "page_html_v1" for row in rows)
    assert all(row["run_id"] == "story230-test" for row in rows)
    assert all(row["module_id"] == "unlimited_ocr_benchmark" for row in rows)
    assert "<table" in rows[0]["html"]
    assert "19O1" in rows[0]["html"]
    assert [PageHtml.model_validate(row).page for row in rows] == [79, 80]


@pytest.mark.parametrize(
    ("finish_reason", "truncated"),
    [
        ("stop", True),
        ("length", False),
    ],
)
def test_truncation_is_a_hard_transport_failure(
    finish_reason: str, truncated: bool
) -> None:
    report = validate_transport(
        _parse_two_pages(),
        expected_pages=2,
        finish_reason=finish_reason,
        truncated=truncated,
    )

    assert report["ok"] is False
    assert "truncat" in _error_text(report) or "length" in _error_text(report)


def test_transport_accepts_exact_complete_output() -> None:
    report = validate_transport(
        _parse_two_pages(),
        expected_pages=2,
        finish_reason="stop",
        truncated=False,
    )

    assert report == {"ok": True, "errors": [], "warnings": []}


def test_adoption_rejects_an_isolated_win_even_when_aggregate_gain_is_large() -> None:
    onward_cases = [
        _onward_case("marie_louise", incumbent_score=0.90, candidate_score=0.96),
        _onward_case("alma", incumbent_score=0.95, candidate_score=0.95),
        _onward_case("arthur", incumbent_score=0.95, candidate_score=0.95),
    ]

    decision = decide_adoption(onward_cases)

    assert decision["decision"] == "do_not_adopt"
    assert decision["meaningful_wins"] == 1
    assert any("1/3" in reason for reason in decision["reasons"])


def test_adoption_rejects_broad_but_sub_point_zero_one_gain() -> None:
    onward_cases = [
        _onward_case("marie_louise", incumbent_score=0.90, candidate_score=0.905),
        _onward_case("alma", incumbent_score=0.91, candidate_score=0.915),
        _onward_case("arthur", incumbent_score=0.92, candidate_score=0.925),
    ]

    decision = decide_adoption(onward_cases)

    assert decision["decision"] == "do_not_adopt"
    assert decision["meaningful_wins"] == 3
    assert any("0.01" in reason for reason in decision["reasons"])


def test_adoption_is_conditional_after_two_meaningful_routeable_wins() -> None:
    onward_cases = [
        _onward_case("marie_louise", incumbent_score=0.90, candidate_score=0.93),
        _onward_case("alma", incumbent_score=0.90, candidate_score=0.92),
        _onward_case("arthur", incumbent_score=0.95, candidate_score=0.94),
    ]

    decision = decide_adoption(
        onward_cases,
        handwriting_results=_complete_failing_handwriting_pair(),
    )

    assert decision["decision"] == "conditional_adopt"
    assert decision["meaningful_wins"] == 2
    assert "genealogy" in decision["winning_surface"]
    assert decision["oracle_hybrid_score"] == pytest.approx((0.93 + 0.92 + 0.95) / 3)
    assert decision["candidate_selection_share"] == pytest.approx(2 / 3)


def test_adoption_requires_all_three_unique_onward_cases() -> None:
    incomplete_cases = [
        _onward_case("marie_louise", incumbent_score=0.90, candidate_score=0.95),
        _onward_case("alma", incumbent_score=0.90, candidate_score=0.95),
    ]

    decision = decide_adoption(incomplete_cases)

    assert decision["decision"] == "do_not_adopt"
    assert any("exactly one result" in reason for reason in decision["reasons"])


def test_onward_win_still_requires_complete_handwriting_evidence() -> None:
    onward_cases = [
        _onward_case("marie_louise", incumbent_score=0.90, candidate_score=0.95),
        _onward_case("alma", incumbent_score=0.90, candidate_score=0.95),
        _onward_case("arthur", incumbent_score=0.90, candidate_score=0.89),
    ]

    decision = decide_adoption(onward_cases)

    assert decision["decision"] == "do_not_adopt"
    assert decision["complete_onward_evidence"] is True
    assert decision["complete_handwriting_evidence"] is False
    assert any("Barney and Alverson" in reason for reason in decision["reasons"])


def test_adoption_rejects_material_page_fidelity_loss() -> None:
    onward_cases = [
        _onward_case(
            "marie_louise",
            incumbent_score=0.90,
            candidate_score=0.95,
            material_page_fidelity_loss=True,
        ),
        _onward_case("alma", incumbent_score=0.90, candidate_score=0.94),
        _onward_case("arthur", incumbent_score=0.95, candidate_score=0.95),
    ]

    decision = decide_adoption(onward_cases)

    assert decision["decision"] == "do_not_adopt"
    assert any(
        "fidelity" in reason.casefold() or "page" in reason.casefold()
        for reason in decision["reasons"]
    )


def test_handwriting_threshold_can_override_onward_rejection() -> None:
    onward_cases = [
        _onward_case("marie_louise", incumbent_score=0.95, candidate_score=0.90),
        _onward_case("alma", incumbent_score=0.95, candidate_score=0.90),
        _onward_case("arthur", incumbent_score=0.95, candidate_score=0.90),
    ]

    passing_fixture = {
        "overall_ratio": 0.99,
        "page_min_ratio": 0.99,
        "pass_rate": 1.0,
    }
    decision = decide_adoption(
        onward_cases,
        handwriting_results=[
            {"case_id": "barney", **passing_fixture},
            {"case_id": "alverson", **passing_fixture},
        ],
    )

    assert decision["decision"] == "conditional_adopt"
    assert "historical handwriting" in decision["winning_surface"].replace("_", " ")
    assert any("handwrit" in reason.casefold() for reason in decision["reasons"])


def test_handwriting_override_requires_every_story_191_threshold() -> None:
    onward_cases = [
        _onward_case("marie_louise", incumbent_score=0.95, candidate_score=0.90),
        _onward_case("alma", incumbent_score=0.95, candidate_score=0.90),
        _onward_case("arthur", incumbent_score=0.95, candidate_score=0.90),
    ]

    decision = decide_adoption(
        onward_cases,
        handwriting_results=[
            {
                "case_id": "barney",
                "overall_ratio": 0.99,
                "page_min_ratio": 0.99,
                "pass_rate": 1.0,
            },
            {
                "case_id": "alverson",
                "overall_ratio": 0.99,
                "page_min_ratio": 0.9899,
                "pass_rate": 1.0,
            },
        ],
    )

    assert decision["decision"] == "do_not_adopt"


def test_handwriting_override_requires_both_unique_real_fixtures() -> None:
    onward_cases = [
        _onward_case("marie_louise", incumbent_score=0.95, candidate_score=0.90),
        _onward_case("alma", incumbent_score=0.95, candidate_score=0.90),
        _onward_case("arthur", incumbent_score=0.95, candidate_score=0.90),
    ]
    passing_barney = {
        "case_id": "barney",
        "overall_ratio": 1.0,
        "page_min_ratio": 1.0,
        "pass_rate": 1.0,
    }

    decision = decide_adoption(
        onward_cases,
        handwriting_results=[passing_barney, passing_barney],
    )

    assert decision["decision"] == "do_not_adopt"


def test_candidate_selection_prefers_best_transport_valid_arm() -> None:
    selected = _select_best_candidate(
        [
            {
                "arm": "invalid_high",
                "candidate_score": 0.99,
                "transport_ok": False,
            },
            {
                "arm": "valid_lower",
                "candidate_score": 0.75,
                "transport_ok": True,
            },
        ]
    )

    assert selected is not None
    assert selected["arm"] == "valid_lower"


def test_candidate_selection_returns_none_when_every_arm_is_ineligible() -> None:
    selected = _select_best_candidate(
        [
            {
                "arm": "transport_failure",
                "candidate_score": 0.99,
                "transport_ok": False,
            },
            {
                "arm": "page_loss",
                "candidate_score": 0.75,
                "transport_ok": True,
                "material_page_loss": True,
            },
        ]
    )

    assert selected is None


def test_generation_near_cap_remains_indeterminate_without_stop_reason() -> None:
    assessment = _generation_cap_assessment(30_939, 32_768)

    assert assessment["truncated"] is None
    assert assessment["finish_reason"] == "not_exposed_by_transformers_helper"
    assert assessment["output_token_margin_to_total_max_length"] == 1_829


def test_generation_at_total_cap_is_a_hard_truncation_failure() -> None:
    assessment = _generation_cap_assessment(32_768, 32_768)

    assert assessment["truncated"] is True
    assert assessment["finish_reason"] == "length"


def test_public_space_upload_requires_explicit_acknowledgement() -> None:
    with pytest.raises(ValueError, match="public Hugging Face Space"):
        run_space(SimpleNamespace(allow_public_upload=False))
