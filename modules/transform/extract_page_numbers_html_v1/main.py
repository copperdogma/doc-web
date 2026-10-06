#!/usr/bin/env python3
"""
Extract printed page numbers from OCR HTML and store them in JSON fields.
Leaves HTML unchanged (page-number tags can be stripped later).
"""
import argparse
import re
from typing import Any, Dict, Optional, List

from bs4 import BeautifulSoup

from modules.common.utils import read_jsonl, save_jsonl, ProgressLogger


PAGE_NUMBER_CLASS = "page-number"


def _strip_tags(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _coerce_int(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _select_page_number_from_text(cleaned: str, source_page_number: Optional[int]) -> Optional[int]:
    # Explicit current/total labels carry their own semantic order. Preserve
    # the first value as the printed page and leave the complete label intact
    # in printed_page_number_text for provenance.
    labeled_total = re.search(
        r"\b(?:p(?:age)?\.?\s*)(\d+)\s*/\s*(\d+)\b",
        cleaned or "",
        flags=re.IGNORECASE,
    )
    if labeled_total:
        return int(labeled_total.group(1))
    # A bare fraction may be a dice roll, ratio, or other body notation; it
    # does not identify a printed page without an explicit page label.
    if re.search(r"\b\d+\s*/\s*\d+\b", cleaned or ""):
        return None
    digits = [int(token) for token in re.findall(r"\d+", cleaned or "")]
    if not digits:
        return None
    # Imposed/split manuals can leave spread-range footers such as "8-9" on
    # both halves. If the upstream manifest already has reader-order page
    # numbers, prefer the number that agrees with the current logical page.
    if source_page_number in digits:
        return source_page_number
    return digits[-1]


def _extract_printed_page_number(html: str, source_page_number: Optional[int] = None) -> Dict[str, Optional[Any]]:
    if not html:
        return {"printed_page_number": None, "printed_page_number_text": None}
    matches = re.findall(
        r'<p[^>]*class=["\']%s["\'][^>]*>(.*?)</p>' % PAGE_NUMBER_CLASS,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not matches:
        # An unmarked numeric paragraph is only a candidate at the document
        # boundary. A catalog code before the title is body content, not a folio.
        soup = BeautifulSoup(html, "html.parser")
        blocks = [tag for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "dt", "dd", "figure", "table"])
                  if tag.get_text(" ", strip=True)]
        last = blocks[-1] if blocks else None
        if last is None or last.name != "p" or last.find_parent(["table", "figure"]) is not None:
            return {"printed_page_number": None, "printed_page_number_text": None}
        cleaned = _strip_tags(str(last))
        if not (re.fullmatch(r"\d+", cleaned) or re.fullmatch(r"[ivxlcdm]+", cleaned.lower())):
            return {"printed_page_number": None, "printed_page_number_text": None}
        return {"printed_page_number": _select_page_number_from_text(cleaned, source_page_number),
                "printed_page_number_text": cleaned or None, "_requires_sequence_support": True}
    # Prefer the last occurrence (footers are typically last).
    raw = matches[-1]
    cleaned = _strip_tags(raw)
    page_number = _select_page_number_from_text(cleaned, source_page_number)
    if page_number is None:
        return {"printed_page_number": None, "printed_page_number_text": cleaned or None}
    return {"printed_page_number": page_number, "printed_page_number_text": cleaned or None}


def _infer_missing_page_numbers(rows: List[Dict[str, Any]]) -> None:
    def page_key(row: Dict[str, Any]) -> int:
        return int(row.get("page_number") or row.get("page") or 0)

    ordered = sorted(enumerate(rows), key=lambda ir: page_key(ir[1]))
    idxs = [i for i, (_, r) in enumerate(ordered) if isinstance(r.get("printed_page_number"), int)]
    if not idxs:
        return

    # Fill gaps between known numeric page numbers when perfectly sequential.
    for a, b in zip(idxs, idxs[1:]):
        _, ra = ordered[a]
        _, rb = ordered[b]
        pa = ra.get("printed_page_number")
        pb = rb.get("printed_page_number")
        if not isinstance(pa, int) or not isinstance(pb, int):
            continue
        if pb > pa and (pb - pa) == (b - a):
            for k in range(a + 1, b):
                _, rk = ordered[k]
                if rk.get("printed_page_number") is None:
                    rk["printed_page_number"] = pa + (k - a)
                    rk["printed_page_number_inferred"] = True

    # Extrapolation requires at least two independent observed anchors with
    # matching logical-page offsets. One printed label cannot number a book.
    first = idxs[0]
    first_supported = len(idxs) >= 2 and (
        ordered[idxs[1]][1]["printed_page_number"] - ordered[first][1]["printed_page_number"] == idxs[1] - first
    )
    last = idxs[-1]
    last_supported = len(idxs) >= 2 and (
        ordered[last][1]["printed_page_number"] - ordered[idxs[-2]][1]["printed_page_number"] == last - idxs[-2]
    )
    # Backfill before the first corroborated numeric label (only if >= 1).
    _, r_first = ordered[first]
    p_first = r_first.get("printed_page_number")
    if first_supported and isinstance(p_first, int):
        for k in range(first - 1, -1, -1):
            inferred = p_first - (first - k)
            if inferred < 1:
                break
            _, rk = ordered[k]
            if rk.get("printed_page_number") is None:
                rk["printed_page_number"] = inferred
                rk["printed_page_number_inferred"] = True

    # Forward fill after last known numeric.
    _, r_last = ordered[last]
    p_last = r_last.get("printed_page_number")
    if last_supported and isinstance(p_last, int):
        for k in range(last + 1, len(ordered)):
            inferred = p_last + (k - last)
            _, rk = ordered[k]
            if rk.get("printed_page_number") is None:
                rk["printed_page_number"] = inferred
                rk["printed_page_number_inferred"] = True


def extract_page_numbers(rows: List[Dict[str, Any]], *, infer_missing: bool = True) -> List[Dict[str, Any]]:
    """Keep source indices separate from explicitly evidenced printed labels."""
    output = []
    candidates = []
    for original in rows:
        row = dict(original)
        html = row.get("html") or row.get("raw_html") or ""
        extracted = _extract_printed_page_number(html, _coerce_int(row.get("page_number") or row.get("page")))
        row["printed_page_number"] = extracted["printed_page_number"]
        row["printed_page_number_text"] = extracted["printed_page_number_text"]
        row["printed_page_number_inferred"] = False
        if extracted.get("_requires_sequence_support") and isinstance(row["printed_page_number"], int):
            candidates.append(len(output))
        output.append(row)
    # Unmarked terminal numbers need an independently observed label at the
    # same printed-versus-source offset; no magnitude cutoff or title exception.
    observed = [(i, _coerce_int(row.get("page_number") or row.get("page")), row["printed_page_number"])
                for i, row in enumerate(output) if type(row["printed_page_number"]) is int]
    for i in candidates:
        row = output[i]
        source_page = _coerce_int(row.get("page_number") or row.get("page"))
        number = row["printed_page_number"]
        supported = source_page is not None and any(
            j != i and other_source is not None and other_source != source_page
            and other_number - number == other_source - source_page
            for j, other_source, other_number in observed
        )
        if not supported:
            row["printed_page_number"] = None
            row["printed_page_number_text"] = None
    if infer_missing:
        _infer_missing_page_numbers(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract printed page numbers from OCR HTML into JSON fields."
    )
    parser.add_argument("--pages", required=True, help="page_html_v1 JSONL path")
    parser.add_argument("--out", required=True, help="Output JSONL path")
    parser.add_argument("--infer-missing", dest="infer_missing", action="store_true", default=True,
                        help="Infer missing numeric page numbers from sequential order")
    parser.add_argument("--no-infer-missing", dest="infer_missing", action="store_false")
    parser.add_argument("--run-id", dest="run_id", default=None, help="Ignored (driver compatibility)")
    parser.add_argument("--state-file", dest="state_file", default=None, help="Ignored (driver compatibility)")
    parser.add_argument("--progress-file", dest="progress_file", default=None, help="Ignored (driver compatibility)")
    args = parser.parse_args()

    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log("extract_page_numbers", "running", message=f"Loading {args.pages}")

    rows = extract_page_numbers(list(read_jsonl(args.pages)), infer_missing=args.infer_missing)

    save_jsonl(args.out, rows)
    logger.log(
        "extract_page_numbers",
        "done",
        current=len(rows),
        total=len(rows),
        message=f"Wrote {len(rows)} rows to {args.out}",
    )


if __name__ == "__main__":
    main()
