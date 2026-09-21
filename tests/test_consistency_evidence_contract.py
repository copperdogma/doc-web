"""Regressions from frozen Story234 evidence; no provider calls."""

import json
from pathlib import Path

from modules.validate.plan_onward_document_consistency_v1 import main as p
from modules.validate.plan_onward_document_consistency_v1 import jev_shadow as j

BASE = Path("docs/evals/artifacts/story234-anonymized-observation")


def cohort():
    chapters = [
        json.loads(line) for line in (BASE / "chapters.jsonl").read_text().splitlines()
    ]
    for row in chapters:
        row["file"] = str(BASE / Path(row["file"]).name)
    pages = {
        row["page_number"]: row
        for row in map(json.loads, (BASE / "pages.jsonl").read_text().splitlines())
    }
    dossier = p.build_document_dossier(
        chapters,
        pages,
        chapters_path=str(BASE / "chapters.jsonl"),
        pages_path=str(BASE / "pages.jsonl"),
        flag_threshold=25,
    )
    raw = json.loads((BASE / "run/planner.response.json").read_text())
    payload = json.loads(raw["choices"][0]["message"]["content"])
    return dossier, payload


def outputs(dossier, payload):
    return p.build_outputs(
        dossier, payload, chapters_path="fixture", pages_path="fixture", run_id="test"
    )


def test_unclassified_note_survives_without_becoming_child_defect():
    d, raw = cohort()
    compact = p._planner_input_from_dossier(d)["chapters"]
    c = compact[-1]
    assert c["signal_examples"]["unclassified_notes"][0]["died_cell"].startswith(
        "Person Z Jan"
    )
    assert c["source_context"]["missing_pages"] == [6]
    assert c["signals"]["suggested_issue_types"] == []
    out = outputs(d, raw)
    assert out[3]["chapters"][-1]["status"] == "uncertain"
    assert "chapter-006.html" in out[3]["summary"]["uncertain_chapters"]
    state = j.state_for(c, out[2])
    assert state["extracted_evidence"]["source_context"]["missing_pages"] == [6]
    assert state["extracted_evidence"]["signal_examples"]["unclassified_notes"]


def test_benign_dates_deaths_and_placeholders_are_not_unclassified():
    for value in [
        "",
        "-",
        "unknown",
        "n/a",
        "living",
        "alive",
        "Jan 1 1871",
        "Died Jan 1 1871",
        "Deceased in childhood",
    ]:
        assert not p._unclassified_died_note(["Person", "", "", "", "", "", value]), (
            value
        )
    assert p._unclassified_died_note(
        ["Person", "", "", "", "", "", "Unattached event: Person Q 1851"]
    )


def test_explicit_and_omitted_uncertainty_preserved():
    d, raw = cohort()
    raw["chapter_findings"][0]["status"] = "uncertain"
    raw["chapter_findings"] = [
        f
        for f in raw["chapter_findings"]
        if f["chapter_basename"] != "chapter-006.html"
    ]
    cs = outputs(d, raw)[3]["chapters"]
    assert cs[0]["status"] == "uncertain" and cs[-1]["status"] == "uncertain"
    assert cs[-1]["issue_types"] == []


def test_exact_contradiction_guard_preserves_policy_and_skips_request():
    d, raw = cohort()
    out = outputs(d, raw)
    compact = p._planner_input_from_dossier(d)["chapters"]
    c = compact[3]
    convention = next(
        x
        for x in out[2]["pattern_conventions"]
        if c["chapter_basename"] in x["member_chapters"]
    )
    assert convention["canonical_headers"] == [
        "NAME",
        "BORN",
        "MARRIED",
        "SPOUSE",
        "BOYGIRL",
        "DIED",
    ]
    assert convention["convention_conflicts"]

    def request(*args):
        raise AssertionError("must not dispatch conflicting policy")

    report = j.run_shadow(
        [c],
        out[2],
        out[3],
        env={
            "DOC_WEB_JEV_SHADOW": "enabled",
            "DOC_WEB_TYPESAFE_RUNTIME_API_KEY": "test",
        },
        request=request,
    )
    assert (
        report["dispatched"] == 0
        and report["chapters"][0]["reason"] == "conflicting_conventions"
    )
    assert report["chapters"][0]["shadow_status"] == "format_drift"
    # Legitimately supported fused policy without its own contradictory defect finding.
    raw["chapter_findings"][3]["status"] = "conformant"
    raw["chapter_findings"][3]["issue_types"] = []
    out = outputs(d, raw)
    accepted_variant = out[3]["chapters"][3]
    assert accepted_variant["status"] == "uncertain"
    assert accepted_variant["issue_types"] == []
    assert (
        accepted_variant["status_reason"]
        == "detector_vs_canonical_variant_disagreement"
    )
    assert accepted_variant["suggested_issue_types"] == ["fused_boygirl_headers"]
    assert not next(
        x
        for x in out[2]["pattern_conventions"]
        if c["chapter_basename"] in x["member_chapters"]
    )["convention_conflicts"]


def test_compact_page_coverage_matches_actual_retained_profiles():
    import copy

    d, _ = cohort()
    c = d["chapter_profiles"][0]
    c["page_profiles"] = [copy.deepcopy(c["page_profiles"][0]) for _ in range(4)]
    c["source_context"] = {
        "expected_page_count": 5,
        "available_page_count": 4,
        "missing_pages": [99],
        "retained_page_profiles": 4,
    }
    compact = p._planner_input_from_dossier(d)["chapters"][0]
    assert len(compact["page_profiles"]) == 2
    assert compact["source_context"]["retained_page_profiles"] == 2
    assert (
        compact["source_context"]["available_profiles_omitted_from_compact_input"] == 2
    )
    assert compact["source_context"]["missing_pages"] == [99]
    assert p._unclassified_died_note(["Person", "", "", "", "", "", "Person 1 1851"])


def test_dependent_shadow_cannot_clear_authoritative_uncertainty():
    d, raw = cohort()
    out = outputs(d, raw)
    chapter = p._planner_input_from_dossier(d)["chapters"][-1]

    def confident_clean(*args):
        return {
            "model": j.MODEL,
            "usage": {"input_tokens": 100, "output_tokens": 50},
            "answers": {
                "status": {
                    "type": "choice",
                    "choice": "conformant",
                    "confidence": 0.95,
                    "probabilities": {
                        label: (1.0 if label == "conformant" else 0.0)
                        for label in j.LABELS
                    },
                }
            },
        }

    report = j.run_shadow(
        [chapter],
        out[2],
        out[3],
        env={
            "DOC_WEB_JEV_SHADOW": "enabled",
            "DOC_WEB_TYPESAFE_RUNTIME_API_KEY": "test",
        },
        request=confident_clean,
    )
    row = report["chapters"][0]
    assert row["jev_status"] == "conformant" and row["confidence"] == 0.95
    assert row["shadow_status"] == "uncertain" and row["route"] == "review"
    assert row["reason"] == "authoritative_uncertainty"
