"""Controls on the evaluator, not implementation-mirroring resolver tests."""

import copy
import importlib.util
from pathlib import Path
import pytest
from bs4 import BeautifulSoup

PATH = (
    Path(__file__).resolve().parents[1]
    / "benchmarks/scripts/reference_resolution_benchmark.py"
)
spec = importlib.util.spec_from_file_location("reference_benchmark", PATH)
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


def test_reserved_holdout_requires_candidate_freeze():
    with pytest.raises(ValueError, match="candidate-freeze"):
        bench.load_corpus("heldout")


def test_wrong_existing_destination_is_not_mistaken_for_valid_resolution():
    corpus, _ = bench.load_corpus("development")
    result = bench.score(corpus, copy.deepcopy(corpus["entries"]))
    wrong = next(r for r in result["cases"] if r["id"] == "wrong-existing")
    assert not wrong["pass"]
    assert wrong["actual_hrefs"] == ["orchard-targets.html#wrong"]
    assert result["wrong_targets"] >= 1
    # The wrong target exists, which demonstrates why link-validity is insufficient.
    assert not any(
        r["href"] == "orchard-targets.html#wrong"
        for r in result["invalid_final_targets"]
    )


def test_missed_reference_counts_against_recall():
    corpus, _ = bench.load_corpus("development")
    result = bench.score(corpus, copy.deepcopy(corpus["entries"]))
    assert result["exact_target_recall"] < 1
    assert not next(r for r in result["cases"] if r["id"] == "printed-offset")["pass"]


def test_inline_markup_loss_fails_even_when_visible_words_unchanged():
    corpus, _ = bench.load_corpus("development")
    entries = copy.deepcopy(corpus["entries"])
    entry = entries[0]
    soup = BeautifulSoup(entry["body_html"], "html.parser")
    node = soup.select_one('[data-eval-case="section-inline"]')
    for tag in list(node.find_all(["em", "strong"])):
        tag.unwrap()
    entry["body_html"] = str(soup)
    result = bench.score(corpus, entries)
    row = next(r for r in result["cases"] if r["id"] == "section-inline")
    assert row["visible_text_preserved"]
    assert not row["inline_markup_preserved"]


def test_uri_equivalent_same_file_target_has_same_identity():
    assert bench.canonical_href(
        "#section-16", "section-16.html"
    ) == bench.canonical_href("section-16.html#section-16", "section-16.html")
    assert bench.canonical_href(
        "other.html#section-16", "section-16.html"
    ) != bench.canonical_href("#section-16", "section-16.html")


def test_truthy_receipt_does_not_unlock_holdout(tmp_path):
    path = tmp_path / "fake-freeze.json"
    path.write_text('{"candidate_frozen": true}')
    with pytest.raises(ValueError, match="incomplete"):
        bench.load_corpus("heldout", path)


def test_missing_audit_rows_fail_completeness():
    corpus, _ = bench.load_corpus("development")

    def no_audit(entries, **kwargs):
        return {"references": []}

    result = bench.evaluate(corpus, no_audit, 1)
    assert not result["report_occurrences_complete"]
    assert not result["report_statuses_correct"]


def test_deleted_resolved_occurrence_stays_in_recall_denominator():
    corpus, _ = bench.load_corpus("development")
    entries = copy.deepcopy(corpus["entries"])
    bench.resolver()(
        entries,
        resolve_references=True,
        source_pages=corpus["source_pages"],
        provenance_rows=corpus["provenance_rows"],
    )
    entry = entries[0]
    soup = BeautifulSoup(entry["body_html"], "html.parser")
    soup.select_one('[data-eval-case="printed-offset"]').decompose()
    entry["body_html"] = str(soup)
    result = bench.score(corpus, entries)
    assert result["exact_target_recall"] < 1.0
    assert not result["pass"]


@pytest.mark.parametrize(
    "removed", ["target", "candidates", "reason", "original_text", "source"]
)
def test_removed_audit_evidence_fails_contract(removed):
    corpus, _ = bench.load_corpus("development")
    candidate = bench.resolver()

    def corrupted(
        entries, *, resolve_references=False, source_pages=(), provenance_rows=()
    ):
        report = candidate(
            entries,
            resolve_references=resolve_references,
            source_pages=source_pages,
            provenance_rows=provenance_rows,
        )
        for row in report["references"]:
            row.pop(removed, None)
        return report

    result = bench.evaluate(corpus, corrupted, 1)
    assert not result["report_audit_contract_correct"]
    assert not result["pass"]


@pytest.mark.parametrize("field", ["provenance", "location"])
def test_missing_source_evidence_fails_contract(field):
    corpus, _ = bench.load_corpus("development")
    candidate = bench.resolver()

    def corrupted(
        entries, *, resolve_references=False, source_pages=(), provenance_rows=()
    ):
        report = candidate(
            entries,
            resolve_references=resolve_references,
            source_pages=source_pages,
            provenance_rows=provenance_rows,
        )
        for row in report["references"]:
            row["source"].pop(field, None)
        return report

    result = bench.evaluate(corpus, corrupted, 1)
    assert not result["report_audit_contract_correct"]
    assert not result["pass"]


def test_wrong_report_destination_fails_even_when_dom_is_correct():
    corpus, _ = bench.load_corpus("development")
    candidate = bench.resolver()

    def corrupted(
        entries, *, resolve_references=False, source_pages=(), provenance_rows=()
    ):
        report = candidate(
            entries,
            resolve_references=resolve_references,
            source_pages=source_pages,
            provenance_rows=provenance_rows,
        )
        for row in report["references"]:
            if row.get("target"):
                row["target"]["href"] = "orchard-targets.html#wrong"
        return report

    result = bench.evaluate(corpus, corrupted, 1)
    assert result["passed_cases"] == result["case_count"]
    assert not result["report_audit_contract_correct"]
    assert not result["pass"]


def test_every_warm_latency_sample_is_retained():
    corpus, _ = bench.load_corpus("development")
    result = bench.evaluate(corpus, bench.resolver(), 3)
    assert len(result["timing"]["warm_resolver_samples_ms"]) == 3
    assert all(value >= 0 for value in result["timing"]["warm_resolver_samples_ms"])


@pytest.mark.parametrize(
    "corruption", ["source_quote", "printed_label", "anchor_ordinal", "source_offsets"]
)
def test_populated_but_incorrect_audit_evidence_fails(corruption):
    corpus, _ = bench.load_corpus("development")
    candidate = bench.resolver()

    def corrupted(
        entries, *, resolve_references=False, source_pages=(), provenance_rows=()
    ):
        report = candidate(
            entries,
            resolve_references=resolve_references,
            source_pages=source_pages,
            provenance_rows=provenance_rows,
        )
        for row in report["references"]:
            if corruption == "anchor_ordinal" and "anchor_ordinal" in row:
                row["anchor_ordinal"] = 999
            if corruption == "source_offsets" and row["source"].get("location"):
                row["source"]["location"] = {"start": 0, "end": 1}
            for target in row.get("candidates", []) + (
                [row["target"]] if row.get("target") else []
            ):
                evidence = target.get("evidence", {})
                if corruption == "source_quote" and "source_text" in evidence:
                    evidence["source_text"] = "Fabricated source statement"
                if corruption == "printed_label" and "printed_label" in evidence:
                    evidence["printed_label"] = "876"
        return report

    result = bench.evaluate(corpus, corrupted, 1)
    assert not result["report_audit_contract_correct"]
    assert not result["pass"]
