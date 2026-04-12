import csv
import json
import zipfile
from pathlib import Path

from scripts.spikes.loc_gw_benchmark import (
    DATASET_ITEM_JSON_URL,
    DATASET_ZIP_URL,
    STORY214_SLICE,
    build_parser,
    load_loc_dataset_bundle,
    normalize_transcript,
    resolve_story214_slice_rows,
    should_retry_transient_eval_failure,
    summarize_case_failure,
)
from benchmarks.scorers.handwritten_notes_transcription import score_page_html_artifact


def _write_dataset_zip(path: Path) -> Path:
    rows = [
        {
            "Campaign": "Ordinary Lives",
            "Project": "Interrogations of British Deserters During the Revolutionary War, 1782-1783",
            "Item": "Interrogation item",
            "ItemId": "mgw6a00007",
            "Asset": "mgw6a00007-4",
            "AssetId": "367413",
            "AssetStatus": "completed",
            "DownloadUrl": "https://example.com/367413.jpg",
            "Transcription": "Joseph Rickers\nsecond line",
            "Tags": "Hessians",
        },
        {
            "Campaign": "Ordinary Lives",
            "Project": "Revolutionary War Receipts, 1776-1780",
            "Item": "Receipt item",
            "ItemId": "mgw500029",
            "Asset": "mgw500029-9",
            "AssetId": "367466",
            "AssetStatus": "completed",
            "DownloadUrl": "https://example.com/367466.jpg",
            "Transcription": "New York 16 Apr 1776",
            "Tags": "receipt",
        },
        {
            "Campaign": "Ordinary Lives",
            "Project": "Farm Reports, 1789-1798",
            "Item": "Farm item",
            "ItemId": "mgw438393",
            "Asset": "mgw438393-1",
            "AssetId": "780802",
            "AssetStatus": "completed",
            "DownloadUrl": "https://example.com/780802.jpg",
            "Transcription": "Jannari the 18t 1794",
            "Tags": "farm report",
        },
        {
            "Campaign": "Ordinary Lives",
            "Project": "Farm Reports, 1789-1798",
            "Item": "Blank item",
            "ItemId": "blank-item",
            "Asset": "blank-item-1",
            "AssetId": "999999",
            "AssetStatus": "completed",
            "DownloadUrl": "https://example.com/999999.jpg",
            "Transcription": "",
            "Tags": "nothing to transcribe",
        },
    ]
    header = [
        "Campaign",
        "Project",
        "Item",
        "ItemId",
        "Asset",
        "AssetId",
        "AssetStatus",
        "DownloadUrl",
        "Transcription",
        "Tags",
    ]
    from io import StringIO

    text_io = StringIO()
    writer = csv.DictWriter(text_io, fieldnames=header)
    writer.writeheader()
    writer.writerows(rows)
    readme_text = "The text in this dataset was created by volunteers and can be used in many different ways."
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("ordinary-lives.csv", text_io.getvalue())
        archive.writestr("README_ordinary-lives.txt", readme_text)
    return path


def test_load_loc_dataset_bundle_reads_csv_and_readme(tmp_path: Path):
    zip_path = _write_dataset_zip(tmp_path / "loc.zip")

    bundle = load_loc_dataset_bundle(zip_path)

    assert bundle["csv_name"] == "ordinary-lives.csv"
    assert bundle["readme_name"] == "README_ordinary-lives.txt"
    assert "volunteers" in bundle["readme_text"]
    assert bundle["summary"]["rows_total"] == 4
    assert bundle["summary"]["rows_with_transcription"] == 3
    assert bundle["summary"]["rows_without_transcription"] == 1
    assert bundle["summary"]["asset_status_counts"] == {"completed": 4}


def test_resolve_story214_slice_rows_returns_selected_rows_in_story_order(tmp_path: Path):
    bundle = load_loc_dataset_bundle(_write_dataset_zip(tmp_path / "loc.zip"))

    resolved = resolve_story214_slice_rows(bundle["rows"])

    assert [spec.asset_id for spec, _row in resolved] == [spec.asset_id for spec in STORY214_SLICE]
    assert [row["Project"] for _spec, row in resolved] == [spec.project for spec in STORY214_SLICE]


def test_normalize_transcript_preserves_text_and_adds_trailing_newline():
    assert normalize_transcript(" line one \nline two ") == "line one \nline two\n"
    assert normalize_transcript("   ") == ""


def test_build_parser_defaults_to_image_only_mode():
    parser = build_parser()

    args = parser.parse_args([])

    assert args.story_id == "214"
    assert args.include_pdf is False
    assert args.instrument is False
    assert args.max_attempts == 2
    assert args.retry_sleep_seconds == 20
    assert args.candidate_model is None
    assert args.candidate_retry_model is None
    assert args.zip_path is None


def test_story214_constants_point_at_official_loc_surface():
    assert DATASET_ITEM_JSON_URL.endswith("/?fo=json")
    assert DATASET_ZIP_URL.endswith("/2020446971.zip")


def test_should_retry_transient_eval_failure_handles_demand_spikes_and_skips_quota():
    assert should_retry_transient_eval_failure("", "503 UNAVAILABLE ... currently experiencing high demand")
    assert should_retry_transient_eval_failure("", "429 rate limit exceeded")
    assert not should_retry_transient_eval_failure("", "insufficient_quota")


def test_summarize_case_failure_detects_empty_html_and_partial_omission(tmp_path: Path):
    transcript_path = tmp_path / "transcript.txt"
    transcript_path.write_text("Line one\nLine two\n", encoding="utf-8")

    empty_artifact = tmp_path / "empty.jsonl"
    empty_artifact.write_text(
        json.dumps(
            {
                "page_number": 1,
                "html": "",
                "ocr_empty": True,
                "ocr_empty_reason": "Empty HTML output for page 1",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    empty_metrics = score_page_html_artifact(transcript_path, empty_artifact)
    empty_summary = summarize_case_failure(empty_artifact, empty_metrics)
    assert empty_summary["dominant_failure_mode"] == "empty_html"
    assert empty_summary["empty_reasons"] == ["Empty HTML output for page 1"]

    short_artifact = tmp_path / "short.jsonl"
    short_artifact.write_text(json.dumps({"page_number": 1, "html": "<p>Line one</p>"}) + "\n", encoding="utf-8")
    short_metrics = score_page_html_artifact(transcript_path, short_artifact)
    short_summary = summarize_case_failure(short_artifact, short_metrics)
    assert short_summary["dominant_failure_mode"] == "partial_omission"
