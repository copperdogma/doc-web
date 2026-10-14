from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

from doc_web.literal_fidelity import SourcePageReview
from modules.common.literal_table_review import review_literal_tables
from schemas import PageHtml


HTML = '<table><tr><td>r2l3</td><td>1+</td></tr></table>'
BBOX = [5.0, 5.0, 95.0, 55.0]


def _row(tmp_path, html=HTML, *, source=True):
    tmp_path.mkdir(parents=True, exist_ok=True)
    image = tmp_path / "page.png"
    Image.new("RGB", (100, 60), "white").save(image)
    sources = []
    if source:
        pdf = tmp_path / "source.pdf"
        pdf.write_bytes(b"pdf-source-identity")
        sources = [str(pdf)]
    return {
        "schema_version": "page_html_v1",
        "run_id": "upstream-run",
        "page": 19,
        "page_number": 1,
        "original_page_number": 19,
        "image": str(image),
        "source": sources,
        "raw_html": html,
        "html": html,
    }


def _review(html=HTML, *, bbox=BBOX, uncertain=None):
    return SourcePageReview.model_validate({
        "source_table_count": 1,
        "tables": [{"bbox": bbox, "html": html, "uncertain_cells": uncertain or []}],
    })


def _load_report(row):
    receipt = row["literal_fidelity"]
    payload = Path(receipt["report_path"]).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == receipt["report_sha256"]
    return json.loads(payload)


def test_exact_source_review_seals_report_and_preserves_initial_html(tmp_path):
    row = _row(tmp_path)
    original_html = row["html"]
    original_raw = row["raw_html"]

    def reader(image_path, requests):
        assert Path(image_path) == Path(row["image"])
        requests.append({"status": "completed", "raw_response": "source B JSON"})
        return _review()

    output_path = tmp_path / "reviewed.jsonl"
    result = review_literal_tables([row], out_path=output_path, run_id="current-run", reader=reader)
    receipt = result[0]["literal_fidelity"]
    PageHtml.model_validate(result[0])
    report = _load_report(result[0])

    assert result[0]["html"] == original_html
    assert result[0]["raw_html"] == original_raw
    assert result[0]["run_id"] == "current-run"
    assert report["upstream_run_id"] == "upstream-run"
    assert receipt["status"] == report["status"] == "verified"
    assert report["source_pdf"]["name"] == "source.pdf"
    assert report["tables"][0]["review"]["html"] == HTML
    assert report["tables"][0]["comparison"]["pass"] is True
    assert report["requests"][0]["raw_response"] == "source B JSON"
    assert str(Path(row["image"]).parent) not in json.dumps(report)
    assert json.loads(output_path.read_text())["literal_fidelity"] == receipt


def test_source_disagreement_holds_page_and_preserves_complete_mismatches(tmp_path):
    row = _row(tmp_path)
    corrected = HTML.replace("r2l3", "r213")

    result = review_literal_tables(
        [row], out_path=tmp_path / "held.jsonl", run_id="current-run",
        reader=lambda *_: _review(corrected),
    )

    report = _load_report(result[0])
    assert result[0]["html"] == HTML
    assert result[0]["literal_fidelity"]["status"] == "unresolved"
    comparison = report["tables"][0]["comparison"]
    assert comparison["pass"] is False
    assert comparison["text_mismatches"] == [
        {"table": 0, "actual_table": 0, "row": 0, "cell": 0,
         "kind": "cell_text", "expected": "r2l3", "actual": "r213"}
    ]


def test_source_uncertainty_and_bad_bbox_both_fail_closed(tmp_path):
    rows = [_row(tmp_path / "a"), _row(tmp_path / "b")]

    def reader_factory(review):
        return lambda *_: review

    output = review_literal_tables(
        rows,
        out_path=tmp_path / "uncertain.jsonl",
        run_id="current-run",
        reader=lambda *_: _review(uncertain=[{"row": 0, "cell": 0, "reason": "ambiguous glyph", "alternatives": ["l", "1"]}]),
    )
    assert all(row["literal_fidelity"]["status"] == "unresolved" for row in output)

    other = _row(tmp_path / "other")
    result = review_literal_tables(
        [other],
        out_path=tmp_path / "bbox.jsonl",
        run_id="current-run",
        reader=reader_factory(_review(bbox=[-1.0, 5.0, 95.0, 55.0])),
    )
    assert result[0]["literal_fidelity"]["status"] == "unresolved"
    assert any("bbox" in error for error in _load_report(result[0])["errors"])


def test_no_table_page_requires_and_can_pass_complete_zero_inventory(tmp_path):
    row = _row(tmp_path, "<p>No table here.</p>", source=False)

    result = review_literal_tables(
        [row],
        out_path=tmp_path / "no-tables.jsonl",
        run_id="current-run",
        reader=lambda *_: SourcePageReview(source_table_count=0, tables=[]),
    )

    assert result[0]["literal_fidelity"]["status"] == "verified"
    assert _load_report(result[0])["table_count"] == 0


def test_page_table_and_request_caps_emit_held_receipts_without_extra_calls(tmp_path):
    rows = [_row(tmp_path / str(index)) for index in range(2)]
    calls = []

    def reader(*args):
        calls.append(args[0])
        return _review()

    result = review_literal_tables(
        rows,
        out_path=tmp_path / "capped.jsonl",
        run_id="current-run",
        reader=reader,
        max_pages=1,
    )

    assert len(calls) == 1
    assert result[0]["literal_fidelity"]["status"] == "verified"
    assert result[1]["literal_fidelity"]["status"] == "unresolved"
    assert "page review cap" in " ".join(_load_report(result[1])["errors"])


def test_fresh_output_guard_prevents_overwrite_and_source_call(tmp_path):
    out = tmp_path / "existing.jsonl"
    out.write_text("prior artifact\n")
    calls = []

    with pytest.raises(FileExistsError, match="fresh output"):
        review_literal_tables(
            [_row(tmp_path / "input")],
            out_path=out,
            run_id="current-run",
            reader=lambda *args: calls.append(args),
        )

    assert out.read_text() == "prior artifact\n"
    assert calls == []


def test_fresh_report_directory_guard_and_declared_missing_pdf_hold_without_call(tmp_path):
    existing_report_dir = tmp_path / "fresh_reports"
    existing_report_dir.mkdir()
    calls = []
    with pytest.raises(FileExistsError, match="fresh output"):
        review_literal_tables(
            [_row(tmp_path / "guard")],
            out_path=tmp_path / "fresh.jsonl",
            run_id="current-run",
            reader=lambda *args: calls.append(args),
        )
    assert calls == []

    row = _row(tmp_path / "missing-pdf")
    Path(row["source"][0]).unlink()
    result = review_literal_tables(
        [row],
        out_path=tmp_path / "missing-source.jsonl",
        run_id="current-run",
        reader=lambda *args: calls.append(args),
    )
    report = _load_report(result[0])
    assert result[0]["literal_fidelity"]["status"] == "unresolved"
    assert any("source PDF is missing" in error for error in report["errors"])
    assert calls == []


def test_driver_build_command_routes_one_page_input_and_run_identity(tmp_path):
    from driver import build_command

    artifact, command, _ = build_command(
        entrypoint="modules/adapter/literal_table_review_v1/main.py",
        params={"model": "gpt-6-astra", "max_pages": 3, "max_tables": 8},
        stage_conf={
            "id": "literal_table_review",
            "stage": "adapter",
            "module": "literal_table_review_v1",
            "artifact_name": "pages_reviewed.jsonl",
        },
        run_dir=str(tmp_path / "run"),
        recipe_input={},
        state_path=str(tmp_path / "state.json"),
        progress_path=str(tmp_path / "events.jsonl"),
        run_id="current-run",
        artifact_inputs={"inputs": [str(tmp_path / "pages.jsonl")]},
        artifact_index={},
        stage_ordinal_map={"literal_table_review": 4},
    )

    assert artifact.endswith("04_literal_table_review_v1/pages_reviewed.jsonl")
    assert "--inputs" in command
    assert str(tmp_path / "pages.jsonl") in command
    assert command[command.index("--run-id") + 1] == "current-run"
    assert "--state-file" in command and "--progress-file" in command
    assert "--max-pages" in command and "3" in command


def test_adapter_saves_held_artifacts_before_nonzero_exit(tmp_path, monkeypatch):
    import sys

    from modules.adapter.literal_table_review_v1 import main as adapter
    from modules.common import literal_table_review

    row = _row(tmp_path / "cli")
    source_pages = tmp_path / "pages.jsonl"
    source_pages.write_text(json.dumps(row) + "\n")
    output_path = tmp_path / "adapter_out" / "pages_reviewed.jsonl"

    class FakeReader:
        def __init__(self, **kwargs):
            pass

        def __call__(self, image_path, requests):
            requests.append({"status": "completed", "raw_response": "table differs"})
            return _review(HTML.replace("r2l3", "r213"))

    monkeypatch.setattr(literal_table_review, "SourceOnlyReader", FakeReader)
    monkeypatch.setattr(
        sys,
        "argv",
        ["literal_table_review_v1", "--pages", str(source_pages), "--out", str(output_path),
         "--run-id", "current-run"],
    )

    with pytest.raises(SystemExit) as exc:
        adapter.main()

    assert exc.value.code == 2
    emitted = json.loads(output_path.read_text())
    assert emitted["html"] == HTML
    assert emitted["literal_fidelity"]["status"] == "unresolved"
    assert Path(emitted["literal_fidelity"]["report_path"]).is_file()
