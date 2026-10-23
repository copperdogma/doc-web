#!/usr/bin/env python3
"""Frozen exact-target reference benchmark, independent of resolver report scoring.

Development: python benchmarks/scripts/reference_resolution_benchmark.py --output output/story243-benchmark-dev.json
Holdout requires a candidate freeze receipt; never use its answers for tuning.
No provider calls. Full driver wall time is a separate optional measurement.
"""

from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import inspect
import json
import math
import posixpath
import re
from pathlib import Path
import statistics
import subprocess
import sys
import time
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures/reference_resolution"
FREEZE = ROOT / "benchmarks/golden/reference_resolution_freeze.json"
sys.path.insert(0, str(ROOT))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_candidate_freeze(receipt, natural_source=None):
    path = Path(receipt)
    if not path.is_file():
        raise ValueError("Candidate freeze receipt does not exist")
    data = json.loads(path.read_text())
    sources = data.get("candidate_source_sha256", {})
    required = {
        "modules/common/manual_navigation.py",
        "doc_web/reference_resolution.py",
    }
    if data.get("candidate_frozen") is not True or not required.issubset(sources):
        raise ValueError("Candidate freeze receipt is incomplete")
    for relative, expected in sources.items():
        source = ROOT / relative
        if (
            not source.resolve().is_relative_to(ROOT)
            or not source.is_file()
            or digest(source) != expected
        ):
            raise ValueError(f"Candidate changed after freeze: {relative}")
    if data.get("harness_sha256") != digest(__file__):
        raise ValueError("Benchmark harness changed after candidate freeze")
    if natural_source is not None:
        expected = data.get("natural_source_sha256", {}).get(
            str(Path(natural_source).resolve())
        )
        if expected != digest(natural_source):
            raise ValueError("Natural heldout source is absent or changed after freeze")
    return data


def load_corpus(split, candidate_freeze=None):
    if split == "heldout" and not candidate_freeze:
        raise ValueError(
            "Heldout evaluation requires --candidate-freeze receipt; freeze candidate before opening answers."
        )
    receipt = verify_candidate_freeze(candidate_freeze) if split == "heldout" else None
    path = FIXTURES / f"{split}.json"
    expected = json.loads(FREEZE.read_text())["sha256"][str(path.relative_to(ROOT))]
    if digest(path) != expected:
        raise ValueError(f"Frozen corpus changed: {path}")
    if receipt and receipt.get("corpus_sha256", {}).get(split) != expected:
        raise ValueError(
            "Heldout corpus hash is absent or changed after candidate freeze"
        )
    return json.loads(path.read_text()), expected


def canonical_href(href, source_file):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        return href
    path = (
        posixpath.normpath(
            posixpath.join(posixpath.dirname(source_file), unquote(parsed.path))
        )
        if parsed.path
        else source_file
    )
    return (
        path
        + ("?" + parsed.query if parsed.query else "")
        + ("#" + unquote(parsed.fragment) if parsed.fragment else "")
    )


def unwrap_links(html):
    soup = BeautifulSoup(html, "html.parser")
    for anchor in soup.find_all("a"):
        anchor.unwrap()
    # Only annotation attributes are allowed to differ after abstention.
    for tag in soup.find_all(True):
        annotated = "data-doc-web-navigation-status" in tag.attrs
        for key in list(tag.attrs):
            if key.startswith("data-doc-web-") or (annotated and key == "title"):
                del tag.attrs[key]
        if tag.get("class") == ["unresolved-reference"]:
            del tag.attrs["class"]
        if tag.name == "span" and not tag.attrs:
            tag.unwrap()
    return soup.decode_contents()


def score(corpus, entries):
    originals = {
        e["filename"]: BeautifulSoup(e["body_html"], "html.parser")
        for e in corpus["entries"]
    }
    actual = {
        e["filename"]: BeautifulSoup(e["body_html"], "html.parser") for e in entries
    }
    document_text_preserved = set(originals) == set(actual) and all(
        originals[path].get_text() == actual[path].get_text() for path in originals
    )
    document_markup_preserved = set(originals) == set(actual) and all(
        unwrap_links(str(originals[path])) == unwrap_links(str(actual[path]))
        for path in originals
    )
    rows = []
    correct = expected_resolved = wrong = abstention_correct = abstention_count = 0
    text_ok = markup_ok = True
    for case in corpus["cases"]:
        expected = case.get(
            "expected_hrefs",
            [case["expected_href"]] if case.get("expected_href") else [],
        )
        expected = [canonical_href(href, case["file"]) for href in expected]
        expected_resolved += len(expected)
        if not expected:
            abstention_count += 1
        selector = f'[data-eval-case="{case["id"]}"]'
        before = originals[case["file"]].select_one(selector)
        after = (
            actual[case["file"]].select_one(selector)
            if case["file"] in actual
            else None
        )
        if before is None or after is None:
            rows.append(
                {"id": case["id"], "pass": False, "reason": "missing_occurrence"}
            )
            continue
        raw_hrefs = [a["href"] for a in after.find_all("a", href=True)]
        enclosing = after.find_parent("a", href=True)
        if enclosing:
            raw_hrefs.insert(0, enclosing["href"])
        canonical_raw = [canonical_href(href, case["file"]) for href in raw_hrefs]
        hrefs = [
            href
            for i, href in enumerate(canonical_raw)
            if i == 0 or href != canonical_raw[i - 1]
        ]
        success = hrefs == expected
        text_same = before.get_text() == after.get_text()
        markup_same = unwrap_links(str(before)) == unwrap_links(str(after))
        text_ok &= text_same
        markup_ok &= markup_same
        if expected:
            correct += sum(1 for target in expected if target in hrefs)
            wrong += sum(1 for target in canonical_raw if target not in expected)
        else:
            abstention_correct += not hrefs
            wrong += len(raw_hrefs)
        rows.append(
            {
                "id": case["id"],
                "expected_hrefs": expected,
                "actual_hrefs": hrefs,
                "raw_actual_hrefs": raw_hrefs,
                "anchor_count": len(raw_hrefs),
                "expected_status": case["expected_status"],
                "pass": bool(success and text_same and markup_same),
                "visible_text_preserved": text_same,
                "inline_markup_preserved": markup_same,
            }
        )
    # Independently prove every local emitted href denotes exactly one final ID.
    target_errors = []
    for filename, soup in actual.items():
        for a in soup.find_all("a", href=True):
            parsed = urlsplit(a["href"])
            if parsed.scheme or parsed.netloc:
                continue
            target = (
                posixpath.normpath(
                    posixpath.join(posixpath.dirname(filename), unquote(parsed.path))
                )
                if parsed.path
                else filename
            )
            if target not in actual or (
                parsed.fragment
                and len(actual[target].find_all(id=unquote(parsed.fragment))) != 1
            ):
                target_errors.append({"file": filename, "href": a["href"]})
    return {
        "cases": rows,
        "case_count": len(rows),
        "passed_cases": sum(r["pass"] for r in rows),
        "exact_target_recall": correct / expected_resolved
        if expected_resolved
        else 1.0,
        "wrong_targets": wrong,
        "abstention_accuracy": abstention_correct / abstention_count
        if abstention_count
        else 1.0,
        "visible_text_preserved": bool(text_ok),
        "inline_markup_preserved": bool(markup_ok),
        "invalid_final_targets": target_errors,
        "document_text_preserved": document_text_preserved,
        "document_markup_preserved": document_markup_preserved,
        "pass": all(r["pass"] for r in rows)
        and not target_errors
        and document_text_preserved
        and document_markup_preserved,
    }


def resolver(module_path=None):
    if module_path:
        spec = importlib.util.spec_from_file_location(
            "reference_candidate", module_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.resolve_navigation
    from modules.common.manual_navigation import resolve_navigation

    return resolve_navigation


def invoke(fn, corpus, enabled):
    entries = copy.deepcopy(corpus["entries"])
    available = inspect.signature(fn).parameters
    kwargs = {
        "resolve_references": enabled,
        "source_pages": corpus["source_pages"],
        "provenance_rows": corpus["provenance_rows"],
    }
    kwargs = {k: v for k, v in kwargs.items() if k in available}
    start = time.perf_counter_ns()
    report = fn(entries, **kwargs)
    elapsed = (time.perf_counter_ns() - start) / 1e6
    return entries, report, elapsed


def audit_row_errors(row, case, original, corpus, final):
    """Check inspectable evidence against source inputs and final DOM, not summaries."""
    errors = []

    def normalized(value):
        return " ".join(str(value).split())

    original_text = row.get("original_text")
    source = row.get("source")
    reason = row.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        errors.append("missing_reason")
    if not isinstance(source, dict):
        return errors + ["missing_source"]
    if row.get("path") != case["file"] or source.get("path") != case["file"]:
        errors.append("incorrect_source_path")
    source_region = (
        original.find_parent(["p", "li", "td", "dd"])
        if "literal_target" in case
        else original
    )
    source_region = source_region or original
    expected_block = source_region.get("id")
    if (
        source.get("block_id") != expected_block
        or row.get("block_id") != expected_block
    ):
        errors.append("incorrect_source_block")
    expected_provenance = next(
        (
            p
            for p in corpus["provenance_rows"]
            if p.get("html_path") == case["file"]
            and p.get("block_id") == expected_block
        ),
        None,
    )
    if expected_provenance:
        observed = source.get("provenance")
        if not isinstance(observed, dict) or any(
            observed.get(k) != v for k, v in expected_provenance.items()
        ):
            errors.append("missing_or_changed_source_provenance")
    anchors = original.find_all("a", href=True)
    if anchors:
        if len(anchors) != 1 or row.get("original_href") != anchors[0]["href"]:
            errors.append("missing_or_changed_original_href")
        if normalized(original_text) != normalized(
            anchors[0].get_text(" ", strip=True)
        ):
            errors.append("missing_or_changed_original_wording")
        if not isinstance(row.get("anchor_ordinal"), int) or row["anchor_ordinal"] < 1:
            errors.append("missing_anchor_location")
        else:
            source_document = list(original.parents)[-1]
            if (
                row["anchor_ordinal"]
                != source_document.find_all("a", href=True).index(anchors[0]) + 1
            ):
                errors.append("incorrect_anchor_location")
    else:
        allowed = []
        visible = source_region.get_text(" ", strip=True)
        if "literal_target" in case:
            allowed = ["turn to " + case["literal_target"]]
        else:
            allowed.extend(
                m.group(0)
                for m in re.finditer(
                    r"\b(?:pages?|sections?|paragraphs?|chapters?|figures?|tables?|footnotes?)\s+(?:\d+|[ivxlcdm]+)(?:\s*[-–—]\s*\d+)?",
                    visible,
                    re.I,
                )
            )
            allowed.extend(
                m.group(0).rstrip(".,;:!?)")
                for m in re.finditer(r"https?://\S+", visible)
            )
            if original.name in {"li", "tr", "dd"}:
                allowed.extend(m.group(0) for m in re.finditer(r"\b\d+\b", visible))
        if not isinstance(original_text, str) or normalized(
            original_text
        ).casefold() not in {normalized(t).casefold() for t in allowed}:
            errors.append("missing_or_changed_original_wording")
        location = source.get("location")
        texts = [
            t.get_text()
            for t in [
                source_region,
                *source_region.find_all(["p", "li", "td", "th", "dd"]),
            ]
        ]
        if not isinstance(location, dict) or not all(
            isinstance(location.get(k), int) for k in ("start", "end")
        ):
            errors.append("missing_source_offsets")
        elif not any(
            0 <= location["start"] < location["end"] <= len(text)
            and text[location["start"] : location["end"]] == original_text
            for text in texts
        ):
            errors.append("incorrect_source_offsets")
    candidates = row.get("candidates")
    if not isinstance(candidates, list):
        errors.append("missing_candidates")
        candidates = []

    def evidence_errors(candidate):
        evidence = candidate.get("evidence", {})
        path, identifier = candidate.get("path"), candidate.get("id")
        if "source_text" in evidence or candidate.get("heading"):
            target_soup = final.get(path)
            tags = target_soup.find_all(id=identifier) if target_soup else []
            quoted = evidence.get("source_text", candidate.get("heading"))
            if normalized(quoted) not in {
                normalized(t.get_text(" ", strip=True)) for t in tags
            }:
                return ["incorrect_candidate_source_text"]
        elif "printed_label" in evidence:
            supporting = [
                p
                for p in corpus["source_pages"]
                if p.get("page_number", p.get("page"))
                == evidence.get("source_page_number")
                and str(
                    p.get("printed_page_number_text", p.get("printed_page_number", ""))
                )
                == str(evidence["printed_label"])
                and not p.get("printed_page_number_inferred")
            ]
            if not supporting or evidence.get("observed") is not True:
                return ["incorrect_candidate_printed_page_evidence"]
            for key in ("original_page_number", "spread_side", "page_id"):
                if key in evidence and not any(
                    p.get(key) == evidence[key] for p in supporting
                ):
                    return ["incorrect_candidate_page_identity"]
        elif "original_href" in evidence:
            if evidence["original_href"] != row.get("original_href") or evidence.get(
                "reason"
            ) != row.get("reason"):
                return ["incorrect_existing_link_evidence"]
        elif "literal_url" in evidence:
            if (
                evidence["literal_url"] != candidate.get("href")
                or normalized(original_text) != evidence["literal_url"]
            ):
                return ["incorrect_literal_url_evidence"]
        else:
            return ["unsupported_candidate_evidence"]
        return []

    for candidate in candidates:
        if (
            not isinstance(candidate, dict)
            or not candidate.get("path")
            or not candidate.get("id")
        ):
            errors.append("invalid_candidate_identity")
            continue
        if not candidate.get("evidence") and not candidate.get("heading"):
            errors.append("missing_candidate_evidence")
        else:
            errors.extend(evidence_errors(candidate))
        if candidate["path"] not in final or not final[candidate["path"]].find(
            id=candidate["id"]
        ):
            errors.append("candidate_absent_from_final_document")
    status = row.get("resolution_status")
    target = row.get("target")
    if status == "resolved":
        if (
            not isinstance(target, dict)
            or not target.get("href")
            or not target.get("evidence")
        ):
            errors.append("missing_chosen_target_evidence")
        else:
            errors.extend(evidence_errors(target))
            actual_identity = canonical_href(target["href"], case["file"])
            expected = case.get(
                "expected_hrefs",
                [case["expected_href"]] if case.get("expected_href") else [],
            )
            if actual_identity not in {
                canonical_href(href, case["file"]) for href in expected
            }:
                errors.append("incorrect_report_destination")
            parsed = urlsplit(target["href"])
            identity = target.get("path", "") + (
                "#" + str(target["id"]) if target.get("id") else ""
            )
            if not (parsed.scheme or parsed.netloc) and identity != actual_identity:
                errors.append("chosen_target_identity_disagrees_with_href")
            if (parsed.scheme or parsed.netloc) and (
                target.get("path") != target["href"] or target.get("id") is not None
            ):
                errors.append("chosen_external_identity_disagrees_with_href")
            actual_soup = final.get(case["file"])
            marker = (
                actual_soup.select_one(f'[data-eval-case="{case["id"]}"]')
                if actual_soup
                else None
            )
            actual_links = list(marker.find_all("a", href=True)) if marker else []
            if marker and marker.find_parent("a", href=True):
                actual_links.append(marker.find_parent("a", href=True))
            if actual_identity not in {
                canonical_href(a["href"], case["file"]) for a in actual_links
            }:
                errors.append("report_destination_absent_from_occurrence")
            if (
                not anchors
                and row.get("kind") != "url"
                and not any(
                    candidate.get("path") == target.get("path")
                    and candidate.get("id") == target.get("id")
                    for candidate in candidates
                )
            ):
                errors.append("chosen_target_absent_from_candidates")
    elif status in {"ambiguous", "missing"}:
        if target is not None or "target" not in row:
            errors.append("abstention_target_must_be_explicit_null")
    else:
        errors.append("missing_canonical_status")
    return errors


def evaluate(corpus, fn, repeat):
    baseline_provenance = copy.deepcopy(corpus["provenance_rows"])
    entries, report, cold = invoke(fn, corpus, True)
    result = score(corpus, entries)
    report_rows = report.get("references", [])
    report_checks = []
    consumed_reports = set()
    final = {
        entry["filename"]: BeautifulSoup(entry["body_html"], "html.parser")
        for entry in entries
    }
    for case in corpus["cases"]:
        if case["expected_status"] == "skipped":
            continue
        original = BeautifulSoup(
            next(
                e["body_html"]
                for e in corpus["entries"]
                if e["filename"] == case["file"]
            ),
            "html.parser",
        ).select_one(f'[data-eval-case="{case["id"]}"]')
        blockid = original.get("id")
        matching = [
            r
            for r in report_rows
            if r.get("block_id") == blockid
            or r.get("source", {}).get("block_id") == blockid
        ]
        if "literal_target" in case:
            # Historical input spans can sit inside a larger paragraph lacking
            # a stable block ID. Match retained literal reference text and file,
            # consuming one occurrence; never use the selected output target.
            source_region = original.find_parent(["p", "li", "td", "dd"]) or original
            source_text = source_region.get_text()

            def matches_source_offsets(row):
                location = row.get("source", {}).get("location") or {}
                start, end = location.get("start"), location.get("end")
                return (
                    isinstance(start, int)
                    and isinstance(end, int)
                    and 0 <= start < end <= len(source_text)
                    and source_text[start:end] == row.get("original_text")
                )

            matches = [
                (index, row)
                for index, row in enumerate(report_rows)
                if index not in consumed_reports
                and row.get("path") == case["file"]
                and re.fullmatch(
                    r"turn to\s+" + re.escape(case["literal_target"]),
                    " ".join(row.get("original_text", "").split()),
                    re.I,
                )
                and matches_source_offsets(row)
            ]
            matches.sort(
                key=lambda item: (item[1].get("source", {}).get("location") or {}).get(
                    "start", 0
                )
            )
            matching = [matches[0][1]] if matches else []
            if matches:
                consumed_reports.add(matches[0][0])
        expected = case.get("expected_report_statuses", [case["expected_status"]])
        statuses = [r.get("resolution_status", r.get("status")) for r in matching]
        contract_errors = [
            error
            for row in matching
            for error in audit_row_errors(row, case, original, corpus, final)
        ]
        report_checks.append(
            {
                "id": case["id"],
                "expected_statuses": expected,
                "actual_statuses": statuses,
                "complete": len(statuses) == len(expected),
                "status_correct": sorted(statuses) == sorted(expected),
                "contract_errors": contract_errors,
                "audit_contract_correct": not contract_errors
                and len(statuses) == len(expected),
            }
        )
    result["report_checks"] = report_checks
    result["report_occurrences_complete"] = all(c["complete"] for c in report_checks)
    result["report_statuses_correct"] = all(c["status_correct"] for c in report_checks)
    result["report_audit_contract_correct"] = all(
        c["audit_contract_correct"] for c in report_checks
    )
    timings = []
    for _ in range(repeat):
        _, _, elapsed = invoke(fn, corpus, True)
        timings.append(elapsed)
    again = copy.deepcopy(corpus)
    again["entries"] = entries
    repeated, _, _ = invoke(fn, again, True)
    idempotent = all(
        a["body_html"] == b["body_html"] for a, b in zip(entries, repeated)
    )
    off, off_report, _ = invoke(fn, corpus, False)
    off_changes = []
    original_by_file = {e["filename"]: e for e in corpus["entries"]}
    # Existing-link validation/repair remains allowed off. Plain-reference enrichment must stop.
    for e in off:
        before = BeautifulSoup(
            original_by_file[e["filename"]]["body_html"], "html.parser"
        )
        after = BeautifulSoup(e["body_html"], "html.parser")
        for node in before.select("[data-eval-case]"):
            if node.find("a"):
                continue
            new = after.select_one(f'[data-eval-case="{node["data-eval-case"]}"]')
            if new is None or str(node) != str(new):
                off_changes.append(node["data-eval-case"])
    result.update(
        {
            "idempotent": idempotent,
            "opt_out_plain_markup_parity": not off_changes,
            "opt_out_changed_cases": off_changes,
            "provenance_unchanged": corpus["provenance_rows"] == baseline_provenance,
            "timing": {
                "cold_resolver_ms": cold,
                "warm_resolver_p50_ms": statistics.median(timings),
                "warm_resolver_samples_ms": timings,
                "warm_resolver_p95_ms": sorted(timings)[
                    max(0, math.ceil(0.95 * len(timings)) - 1)
                ],
                "repeats": repeat,
                "boundary": "resolve_navigation only; corpus load/deepcopy outside timer",
            },
            "api_calls": 0,
            "api_cost_usd": 0,
            "report": report,
            "off_report": off_report,
        }
    )
    result["pass"] &= (
        result["report_occurrences_complete"]
        and result["report_statuses_correct"]
        and result["report_audit_contract_correct"]
        and idempotent
        and not off_changes
        and result["provenance_unchanged"]
    )
    return result


def natural_gamebook(path):
    """Observed historical workload, never a complete/manual OCR golden.

    Expected destination comes from literal printed `turn to N` text, cross-checked
    against retained anchor href. All other source anchors are counted and
    classified; they are not silently removed from the workload denominator.
    """
    data = json.loads(Path(path).read_text())
    sections = data["sections"]
    entries = []
    cases = []
    classifications = []
    for label, section in sections.items():
        soup = BeautifulSoup(section.get("presentation_html") or "", "html.parser")
        for ordinal, a in enumerate(list(soup.find_all("a", href=True)), 1):
            text = a.get_text(" ", strip=True)
            href = a["href"]
            context = a.parent.get_text(" ", strip=True)
            match = re.fullmatch(r"turn to\s+(\d+)", text, re.I)
            if not match and re.fullmatch(r"\d+", text):
                # Bare anchor is admitted only when its immediately preceding
                # literal source prose says turn to; full paragraph alone is unsafe.
                left = "".join(str(x) for x in reversed(list(a.previous_siblings)))[
                    -120:
                ]
                left = BeautifulSoup(left, "html.parser").get_text()
                if re.search(r"turn to\s*$", left, re.I):
                    match = re.fullmatch(r"(\d+)", text)
            target = match.group(1) if match else None
            supported = bool(target and target in sections and href == "#" + target)
            caseid = f"section-{label}-anchor-{ordinal}"
            classifications.append(
                {
                    "id": caseid,
                    "source_section": label,
                    "anchor_text": text,
                    "original_href": href,
                    "context": context,
                    "classification": "literal_turn_to_crosschecked"
                    if supported
                    else "unsupported_or_conflicting_source_anchor",
                    "literal_target": target,
                }
            )
            # Retain anchor text in an independent marker before unwrapping.
            span = soup.new_tag("span")
            span["data-eval-case"] = caseid
            span["id"] = "occ-" + caseid
            for child in list(a.contents):
                span.append(child.extract())
            a.replace_with(span)
            if supported:
                cases.append(
                    {
                        "id": caseid,
                        "file": "section-" + label + ".html",
                        "expected_href": "section-"
                        + target
                        + ".html#section-"
                        + target,
                        "expected_status": "resolved",
                        "literal_target": target,
                    }
                )
        heading = (
            f'<h2 id="section-{label}">Section {label}</h2>'
            if label.isdigit()
            else '<h2 id="section-background">Background</h2>'
        )
        body = heading + str(soup)
        page = section.get("pageStart")
        entries.append(
            {
                "filename": "section-" + label + ".html",
                "body_html": body,
                "prepared_pages": [{"page_number": page, "html": body}],
                "source_pages": section.get("provenance", {}).get("source_pages", []),
            }
        )
    provenance = [
        {
            "block_id": "section-" + label,
            "html_path": "section-" + label + ".html",
            "source_page_number": section.get("pageStart"),
            "source_pages_original": section.get("provenance", {}).get(
                "source_pages_original", []
            ),
        }
        for label, section in sections.items()
    ]
    return {
        "version": 1,
        "split": "natural-development",
        "entries": entries,
        "source_pages": [p for e in entries for p in e["prepared_pages"]],
        "provenance_rows": provenance,
        "cases": cases,
        "classifications": classifications,
        "source_sha256": digest(path),
        "health_limit": "Historical check-reuse unsafe; empty OCR pages. Reference-only observed workload; no full-book completeness, OCR fidelity or graduation claim.",
        "expected_target_source": "literal turn-to number agrees with retained anchor href and unique observed section metadata. Injected section heading inventory is benchmark adapter context.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--split", choices=["development", "heldout"], default="development")
    p.add_argument("--candidate-freeze", type=Path)
    p.add_argument("--module-path", type=Path)
    p.add_argument("--repeat", type=int, default=10)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument(
        "--natural-gamebook",
        type=Path,
        help="Historical development gamebook observed workload; not a full-book golden",
    )
    p.add_argument(
        "--driver-run-id",
        help="Optional separate full driver wall-time run with frozen smoke recipe",
    )
    args = p.parse_args()
    if args.repeat < 1 or args.repeat > 1000:
        p.error("--repeat must be 1..1000")
    if args.candidate_freeze and not args.candidate_freeze.is_file():
        p.error("candidate freeze receipt does not exist")
    if args.split == "heldout" and args.module_path:
        p.error(
            "Heldout uses the frozen project candidate; alternate module paths are not permitted"
        )
    if args.natural_gamebook:
        natural_manifest = json.loads(
            (
                ROOT / "benchmarks/golden/reference_resolution_natural_sources.json"
            ).read_text()
        )
        for split, source in natural_manifest["sources"].items():
            if args.natural_gamebook.resolve() == Path(source["path"]).resolve():
                if split == "heldout" and args.split != "heldout":
                    p.error(
                        "Reserved natural source requires --split heldout and candidate freeze"
                    )
                if digest(args.natural_gamebook) != source["sha256"]:
                    p.error("Frozen natural source changed")
        if args.split == "heldout" and not args.candidate_freeze:
            p.error("Natural heldout also requires candidate freeze receipt")
        if args.split == "heldout":
            verify_candidate_freeze(args.candidate_freeze, args.natural_gamebook)
        corpus = natural_gamebook(args.natural_gamebook)
        corpus_hash = corpus["source_sha256"]
    else:
        corpus, corpus_hash = load_corpus(args.split, args.candidate_freeze)
    result = evaluate(corpus, resolver(args.module_path), args.repeat)
    result.update(
        {
            "split": args.split,
            "corpus_sha256": corpus_hash,
            "harness_sha256": digest(__file__),
            "candidate_sha256": digest(
                args.module_path or ROOT / "modules/common/manual_navigation.py"
            ),
            "candidate_freeze_sha256": digest(args.candidate_freeze)
            if args.candidate_freeze
            else None,
            "heldout_used_for_tuning": False,
            "natural_document_claim": "Synthetic controls only. Natural-document stress is separate; no full-book/OCR accuracy claim.",
        }
    )
    if args.natural_gamebook:
        result["natural_workload"] = {
            k: corpus[k]
            for k in (
                "classifications",
                "source_sha256",
                "health_limit",
                "expected_target_source",
            )
        }
        result["natural_workload"].update(
            section_count=len(corpus["entries"]),
            source_anchor_count=len(corpus["classifications"]),
            supported_literal_occurrences=len(corpus["cases"]),
            unsupported_source_anchor_count=sum(
                c["classification"] != "literal_turn_to_crosschecked"
                for c in corpus["classifications"]
            ),
        )
        result["natural_document_claim"] = corpus["health_limit"]
    if args.driver_run_id:
        cmd = [
            sys.executable,
            "driver.py",
            "--recipe",
            "configs/recipes/recipe-reference-resolution-smoke.yaml",
            "--run-id",
            args.driver_run_id,
            "--resolve-references",
        ]
        start = time.perf_counter()
        run = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        result["driver"] = {
            "command": cmd,
            "full_driver_wall_ms": (time.perf_counter() - start) * 1000,
            "exit_code": run.returncode,
            "stdout_tail": run.stdout[-2000:],
            "stderr_tail": run.stderr[-2000:],
        }
        result["pass"] &= run.returncode == 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str) + "\n"
    )
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "pass",
                    "passed_cases",
                    "case_count",
                    "exact_target_recall",
                    "wrong_targets",
                    "abstention_accuracy",
                    "timing",
                    "api_cost_usd",
                )
            }
        )
    )
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
