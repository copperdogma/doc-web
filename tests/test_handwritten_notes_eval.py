import json
from pathlib import Path

from benchmarks.scripts import run_handwritten_notes_eval as handwritten_eval
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
    assert build_run_id("handwritten-notes-barney-real", "image-handwritten-rescue") == "handwritten-handwritten-notes-barney-real-image-handwritten-rescue"


def test_handwritten_notes_eval_corpus_json_is_well_formed():
    corpus_path = Path("benchmarks/golden/handwritten-notes/corpus.json")
    payload = json.loads(corpus_path.read_text(encoding="utf-8"))

    assert "fixtures" in payload
    assert len(payload["fixtures"]) >= 4


def test_handwritten_notes_eval_loads_case_instrumentation(monkeypatch, tmp_path):
    run_id = "handwritten-demo-image-handwritten-rescue"
    run_dir = tmp_path / "output" / "runs" / run_id
    run_dir.mkdir(parents=True)
    instrumentation_path = run_dir / "instrumentation.json"
    instrumentation_path.write_text(
        json.dumps(
            {
                "schema_version": "instrumentation_run_v1",
                "run_id": run_id,
                "totals": {"calls": 1, "prompt_tokens": 10, "completion_tokens": 20, "cost": 0.123},
                "stages": [
                    {
                        "id": "ocr_ai",
                        "wall_seconds": 4.5,
                        "llm_totals": {"calls": 1, "prompt_tokens": 10, "completion_tokens": 20, "cost": 0.123},
                        "extra": {
                            "per_model": {
                                "gemini-2.5-pro": {
                                    "calls": 1,
                                    "prompt_tokens": 10,
                                    "completion_tokens": 20,
                                    "cost": 0.123,
                                }
                            }
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(handwritten_eval, "ROOT", tmp_path)

    payload = handwritten_eval.load_case_instrumentation(run_id)

    assert payload == {
        "path": str(instrumentation_path),
        "run_totals": {"calls": 1, "prompt_tokens": 10, "completion_tokens": 20, "cost": 0.123},
        "ocr_stage": {
            "wall_seconds": 4.5,
            "llm_totals": {"calls": 1, "prompt_tokens": 10, "completion_tokens": 20, "cost": 0.123},
            "per_model": {
                "gemini-2.5-pro": {
                    "calls": 1,
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "cost": 0.123,
                }
            },
        },
    }


def test_handwritten_notes_eval_returns_none_when_instrumentation_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(handwritten_eval, "ROOT", tmp_path)

    assert handwritten_eval.load_case_instrumentation("missing-run") is None
