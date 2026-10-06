"""Semantic mutations must not disappear behind normalization or alignment."""

import pytest

from benchmarks.scorers.literal_table_diff import compare_tables


def table(*rows):
    return "<table>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows) + "</table>"


@pytest.mark.parametrize("expected,actual", [
    ("Nl", "N1"), ("O’Neil", "O'Neil"), ("“Name”", '"Name"'),
    ("NAME", "Name"), ("", "—"), ("-", "—"), ("a,b", "ab"),
])
def test_literal_mutations_fail(expected, actual):
    result = compare_tables(table([expected]), table([actual]))
    assert not result["text_pass"]
    assert result["structure_pass"]
    assert not result["pass"]
    assert result["text_mismatches"][0]["expected"] == expected
    assert result["text_mismatches"][0]["actual"] == actual


def test_whitespace_only_and_entities_pass():
    assert compare_tables(table(["  A\n  B &amp; C "]), table(["A B & C"]))["pass"]
    assert compare_tables(table(["a<b>b</b>c"]), table(["abc"]))["pass"]
    assert compare_tables(table(["\u00a0"]), table([""]))["pass"]


@pytest.mark.parametrize("actual", [
    table(["a"], ["b"], ["c"]), table(["a"]),
    table(["a", "extra"], ["b"]), table([], ["b"]),
    table(["a"], ["b"]) + table(["extra"]), "", table(["b"], ["a"]),
])
def test_extra_missing_and_reowned_content_fail(actual):
    result = compare_tables(table(["a"], ["b"]), actual)
    assert not result["pass"]
    assert not result["text_pass"]
    assert result["text_mismatch_count"] == len(result["text_mismatches"])
    assert result["structure_mismatch_count"] == len(result["structure_mismatches"])


def test_no_tables_fails_closed():
    assert not compare_tables("", "")["pass"]


def test_empty_rows_count():
    result = compare_tables(table([]), table([], []))
    assert not result["structure_pass"]
    assert not result["text_pass"]


def test_missing_empty_table_detected():
    result = compare_tables("<table></table>" * 2, "<table></table>")
    assert not result["pass"]
    assert any(e["kind"] == "missing_table" for e in result["text_mismatches"])


def test_geometry_separate_from_text():
    golden = '<table><tr><td rowspan="2">a</td><td>b</td></tr><tr><td>c</td></tr></table>'
    actual = golden.replace(' rowspan="2"', '')
    result = compare_tables(golden, actual)
    assert result["text_pass"]
    assert not result["structure_pass"]
    assert {e["kind"] for e in result["structure_mismatches"]} == {"rowspan", "column"}
    assert compare_tables(golden, golden)["pass"]


def test_colspan_mutation():
    golden = '<table><tr><td colspan="2">a</td><td>b</td></tr></table>'
    result = compare_tables(golden, golden.replace(' colspan="2"', ''))
    assert result["text_pass"]
    assert not result["structure_pass"]


@pytest.mark.parametrize("span", ["0", "-1", "2x", "", "1.0", "1001", "9" * 5000])
def test_invalid_colspan_fails_even_identical(span):
    html = f'<table><tr><td colspan="{span}">a</td></tr></table>'
    result = compare_tables(html, html)
    assert not result["pass"]
    assert any(e["kind"] == "invalid_span" for e in result["structure_mismatches"])


def test_rowspan_outside_table_fails():
    html = '<table><tr><td rowspan="2">a</td></tr></table>'
    assert any(e["kind"] == "span_past_table" for e in compare_tables(html, html)["structure_mismatches"])


def test_span_overlap_fails():
    html = '<table><tr><td>a</td><td rowspan="2">b</td></tr><tr><td colspan="2">c</td></tr></table>'
    assert any(e["kind"] == "overlapping_span" for e in compare_tables(html, html)["structure_mismatches"])


def test_row_groups_and_header_cell_type():
    html = '<table><thead><tr><th>a</th></tr></thead><tbody><tr><td>b</td></tr></tbody></table>'
    assert compare_tables(html, html)["pass"]
    assert not compare_tables(html, html.replace("th>", "td>"))["structure_pass"]
    bad = html.replace("<th>", '<th rowspan="2">')
    assert any(e["kind"] == "span_crosses_row_group" for e in compare_tables(bad, bad)["structure_mismatches"])


def test_declared_slice_reports_excluded_tables():
    golden = table(["target"])
    actual = table(["outside"]) + golden + table(["outside2"])
    assert not compare_tables(golden, actual)["pass"]
    result = compare_tables(golden, actual, table_index=1)
    assert result["pass"]
    assert result["scope"]["excluded_actual_table_indices"] == [0, 2]
    assert result["scope"]["actual_table_count"] == 3
    assert result["counts"]["actual"] == {"tables": 1, "rows": 1, "cells": 1}
    assert not compare_tables(golden, actual, table_index=3)["pass"]
    assert not compare_tables(golden + golden, actual, table_index=1)["pass"]


@pytest.mark.parametrize("index", [-1, True, 1.0, "1"])
def test_invalid_slice_selector(index):
    with pytest.raises(ValueError):
        compare_tables(table(["a"]), table(["a"]), table_index=index)


def test_nested_tables_are_separate_without_parent_contamination():
    nested = table(["inside"])
    golden = table(["before" + nested + "after"])
    actual = golden.replace("inside", "changed")
    result = compare_tables(golden, actual)
    assert result["counts"]["golden"] == {"tables": 2, "rows": 2, "cells": 2}
    assert result["text_mismatch_count"] == 1
    assert result["text_mismatches"][0]["table"] == 1
    assert not result["text_pass"]
    # Flattening identical cell texts loses the nesting relationship.
    flattened = table(["beforeafter"]) + nested
    assert compare_tables(golden, flattened)["text_pass"]
    assert not compare_tables(golden, flattened)["structure_pass"]


@pytest.mark.parametrize("html", [
    '<table><div><tr><td>a</td></tr></div></table>',
    '<table><tr><div><td>a</td></div></tr></table>',
    '<table><td>a</td></table>',
])
def test_misplaced_rows_cells_fail_closed(html):
    assert not compare_tables(html, html)["structure_pass"]


def test_nested_table_cannot_change_owning_cell_silently():
    nested = table(["inner"])
    golden = table([nested, ""])
    actual = table(["", nested])
    result = compare_tables(golden, actual)
    assert result["text_pass"]
    assert not result["structure_pass"]
    assert any(e["kind"] == "parent_owner" for e in result["structure_mismatches"])


def test_canonical_digest_matches_declared_parser_serialization():
    import hashlib
    import json

    from doc_web.literal_tables import _parse, canonical_table_digest

    html = table(["“O’Neil”", "Nl"])
    expected = hashlib.sha256(json.dumps(_parse(html), sort_keys=True,
                                        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    assert canonical_table_digest(html) == expected
    assert canonical_table_digest(html) == canonical_table_digest(html)


def test_canonical_digest_ignores_only_presentational_table_whitespace():
    from doc_web.literal_tables import canonical_table_digest

    original = table([" A  B ", "—"])
    assert canonical_table_digest(original) == canonical_table_digest(table(["A B", "—"]))
    for mutated in (table(["a B", "—"]), table(["A B", ""]),
                    table(["A B", "—"], []), original.replace("<td>", '<td colspan="2">', 1)):
        assert canonical_table_digest(original) != canonical_table_digest(mutated)


def test_benchmark_surface_reexports_production_parser_and_comparator():
    from benchmarks.scorers import literal_table_diff
    from doc_web import literal_tables

    assert literal_table_diff._parse is literal_tables._parse
    assert literal_table_diff.compare_tables is literal_tables.compare_tables


@pytest.mark.parametrize("rendered", ["1<br>2", "1<br/>2", "<p>1</p><p>2</p>",
                                      "<div>1</div><div>2</div>", "1<div>2</div>"])
def test_rendered_boundaries_cannot_merge_tokens(rendered):
    assert compare_tables(table([rendered]), table(["1 2"]))["pass"]
    result = compare_tables(table([rendered]), table(["12"]))
    assert not result["text_pass"]
    assert result["structure_pass"]
    assert result["text_mismatches"][0]["expected"] == "1 2"


def test_inline_markup_does_not_invent_spaces():
    assert compare_tables(table(["N<span>l</span>"]), table(["Nl"]))["pass"]
    assert compare_tables(table(["<strong>1</strong><em>2</em>"]), table(["12"]))["pass"]
    assert not compare_tables(table(["N<span>l</span>"]), table(["N l"]))["text_pass"]


def test_caption_units_are_literal_text_and_digest_content():
    from doc_web.literal_tables import _parse, canonical_table_digest

    source = '<table><caption>Doses (g)</caption><tr><td>12</td></tr></table>'
    changed = source.replace("(g)", "(mg)")
    result = compare_tables(source, changed)
    assert not result["text_pass"]
    assert result["structure_pass"]
    assert result["text_mismatches"] == [{"table": 0, "actual_table": 0,
                                          "kind": "captions", "expected": ["Doses (g)"],
                                          "actual": ["Doses (mg)"]}]
    assert _parse(source)[0]["outside_text"] == ""
    assert canonical_table_digest(source) != canonical_table_digest(changed)
    assert not compare_tables(source, source.replace('<caption>Doses (g)</caption>', ''))["text_pass"]


def test_caption_breaks_case_quotes_and_inline_text_preserved():
    source = '<table><caption>“Dose”<br><span>m</span>g</caption><tr><td>1</td></tr></table>'
    actual = '<table><caption>“Dose” mg</caption><tr><td>1</td></tr></table>'
    assert compare_tables(source, actual)["pass"]
    assert not compare_tables(source, actual.replace("“Dose”", '"Dose"'))["text_pass"]
    assert not compare_tables(source, actual.replace("Dose", "dose"))["text_pass"]


def test_outside_cell_text_cannot_disappear_or_change():
    from doc_web.literal_tables import _parse

    source = '<table>Table units: g<tr><td>1</td></tr>End note</table>'
    parsed = _parse(source)[0]
    assert parsed["outside_text"] == "Table units: g End note"
    assert "1" not in parsed["outside_text"]
    assert not compare_tables(source, source.replace("units: g", "units: mg"))["text_pass"]
    assert not compare_tables(source, source.replace("End note", ""))["text_pass"]


def test_nested_caption_and_outside_text_are_owned_once():
    from doc_web.literal_tables import _parse

    nested = '<table><caption>Inner units</caption>inner note<tr><td>2</td></tr></table>'
    source = '<table><caption>Outer units</caption>outer note<tr><td>1' + nested + '</td></tr></table>'
    parsed = _parse(source)
    assert parsed[0]["captions"] == ["Outer units"]
    assert parsed[0]["outside_text"] == "outer note"
    assert parsed[0]["rows"][0][0]["text"] == "1"
    assert parsed[1]["captions"] == ["Inner units"]
    assert parsed[1]["outside_text"] == "inner note"
    result = compare_tables(source, source.replace("Inner units", "Changed units"))
    assert result["text_mismatch_count"] == 1
    assert result["text_mismatches"][0]["table"] == 1


@pytest.mark.parametrize("markup", [
    '<td hidden>1</td>', '<td aria-hidden="true">1</td>',
    '<td style="display: none">1</td>', '<td style="visibility: hidden">1</td>',
    '<td>1<script>ignored()</script></td>', '<td>1<style>td{display:none}</style></td>',
])
def test_unsupported_visibility_fails_closed_even_identical(markup):
    html = '<table><tr>' + markup + '</tr></table>'
    result = compare_tables(html, html)
    assert not result["structure_pass"]
    assert any(e["kind"] == "unsupported_visibility" for e in result["structure_mismatches"])


def test_hidden_ancestor_is_not_silently_accepted():
    html = '<div hidden>' + table(["1"]) + '</div>'
    assert not compare_tables(html, html)["structure_pass"]


def test_outside_cell_text_keeps_boundaries_when_cells_are_excluded():
    from doc_web.literal_tables import _parse

    html = '<table><tr>before<td>cell</td>after</tr></table>'
    assert _parse(html)[0]["outside_text"] == "before after"
