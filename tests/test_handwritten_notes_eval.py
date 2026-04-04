import json
from pathlib import Path

from benchmarks.scripts.run_handwritten_notes_eval import build_run_id, load_fixture_specs


def test_handwritten_notes_eval_default_corpus_loads_unique_fixtures():
    fixtures = load_fixture_specs()

    ids = [fixture["id"] for fixture in fixtures]
    assert ids == [
        "handwritten-notes-mini",
        "handwritten-notes-faded",
        "handwritten-notes-rough",
        "handwritten-notes-barney-real",
    ]
    assert len(ids) == len(set(ids))
    assert all(fixture["transcript_path"].exists() for fixture in fixtures)
    assert all(fixture["images_path"].exists() for fixture in fixtures)
    assert all(fixture["pdf_path"].exists() for fixture in fixtures)


def test_handwritten_notes_eval_supports_single_fixture_override(tmp_path):
    transcript = tmp_path / "note.txt"
    transcript.write_text("Page one", encoding="utf-8")
    images = tmp_path / "images"
    images.mkdir()
    pdf = tmp_path / "note.pdf"
    pdf.write_bytes(b"%PDF-1.4")

    fixtures = load_fixture_specs(
        transcript=str(transcript),
        images=str(images),
        pdf=str(pdf),
    )

    assert len(fixtures) == 1
    assert fixtures[0]["id"] == "single-fixture"
    assert fixtures[0]["transcript_path"] == transcript
    assert fixtures[0]["images_path"] == images
    assert fixtures[0]["pdf_path"] == pdf


def test_handwritten_notes_eval_builds_fixture_specific_run_ids():
    assert build_run_id("handwritten-notes-mini", "image-generic") == "handwritten-handwritten-notes-mini-image-generic"
    assert build_run_id("handwritten-notes-faded", "image-generic") == "handwritten-handwritten-notes-faded-image-generic"
    assert build_run_id("handwritten-notes-rough", "pdf-generic") == "handwritten-handwritten-notes-rough-pdf-generic"
    assert build_run_id("handwritten-notes-barney-real", "pdf-generic") == "handwritten-handwritten-notes-barney-real-pdf-generic"


def test_handwritten_notes_eval_corpus_json_is_well_formed():
    corpus_path = Path("benchmarks/golden/handwritten-notes/corpus.json")
    payload = json.loads(corpus_path.read_text(encoding="utf-8"))

    assert "fixtures" in payload
    assert len(payload["fixtures"]) >= 4
