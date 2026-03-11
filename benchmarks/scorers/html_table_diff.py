"""HTML table structural diff scorer for promptfoo.

Uses sequence alignment (LCS) to match golden rows to output rows,
tolerating insertions/deletions (e.g., section headers in different
positions). Scores matched rows for cell accuracy.
"""
import re
from bs4 import BeautifulSoup


def _normalize_cell(text):
    """Collapse whitespace, normalize quotes, and strip for fair comparison."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    # Normalize curly quotes/apostrophes to ASCII
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    return text


HEADER_KEYWORDS = {"name", "born", "married", "spouse", "boy", "girl", "died"}


def _is_header_row(row):
    """Check if a row looks like the NAME/BORN/MARRIED/.../DIED header."""
    if len(row) < 5:
        return False
    normalized = {_normalize_cell(c).lower() for c in row}
    return len(normalized & HEADER_KEYWORDS) >= 5


def parse_html_table(html):
    """Extract all rows from all tables as lists of cell text."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if not cells:
                continue
            row_data = [_normalize_cell(c.get_text()) for c in cells]
            rows.append(row_data)
    return rows


def _align_on_header(rows):
    """Find the header row and return rows from that point onward."""
    for i, row in enumerate(rows):
        if _is_header_row(row):
            return rows[i:]
    return rows


def _row_text(row):
    """Canonical text of a row for comparison."""
    return " | ".join(row)


def _row_similarity(a, b):
    """Quick similarity between two rows (0-1). Used for alignment."""
    if not a or not b:
        return 0.0
    # If column counts differ wildly, low similarity
    if abs(len(a) - len(b)) > 2:
        return 0.1
    # Compare overlapping cells
    matches = 0
    total = max(len(a), len(b))
    for ca, cb in zip(a, b):
        if ca == cb:
            matches += 1
        elif ca and cb and (ca in cb or cb in ca):
            matches += 0.5
    return matches / total if total else 0.0


def _lcs_align(golden_rows, output_rows, threshold=0.5):
    """Align golden and output rows using LCS-like dynamic programming.

    Returns list of (golden_idx, output_idx) pairs for matched rows.
    Unmatched rows are not included.
    """
    n = len(golden_rows)
    m = len(output_rows)

    # Build similarity matrix (only compute for reasonable pairs)
    # Use DP for longest common subsequence with similarity threshold
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sim = _row_similarity(golden_rows[i - 1], output_rows[j - 1])
            if sim >= threshold:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack to find aligned pairs
    pairs = []
    i, j = n, m
    while i > 0 and j > 0:
        sim = _row_similarity(golden_rows[i - 1], output_rows[j - 1])
        if sim >= threshold and dp[i][j] == dp[i - 1][j - 1] + 1:
            pairs.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    pairs.reverse()
    return pairs


def _score_matched_rows(golden_rows, output_rows, pairs):
    """Score the matched row pairs for cell-level accuracy.

    Returns (total_cells, cell_errors, row_errors, error_details).
    """
    total_cells = 0
    cell_errors = 0
    errors = []

    for gi, oi in pairs:
        g_row = golden_rows[gi]
        o_row = output_rows[oi]
        total_cells += len(g_row)

        if len(g_row) != len(o_row):
            cell_errors += abs(len(g_row) - len(o_row))
            errors.append(
                f"Row g{gi}/o{oi} column count: Expected {len(g_row)}, Got {len(o_row)}"
            )
            # Still compare overlapping cells
            for k, (gc, oc) in enumerate(zip(g_row, o_row)):
                if gc != oc:
                    cell_errors += 1
                    if len(errors) < 25:
                        errors.append(
                            f"Row g{gi}/o{oi} Col {k}: Expected '{gc}', Got '{oc}'"
                        )
        else:
            for k, (gc, oc) in enumerate(zip(g_row, o_row)):
                if gc != oc:
                    cell_errors += 1
                    if len(errors) < 25:
                        errors.append(
                            f"Row g{gi}/o{oi} Col {k}: Expected '{gc}', Got '{oc}'"
                        )

    return total_cells, cell_errors, errors


def get_assert(output, context):
    try:
        golden_path = context["vars"]["golden_path"]
        with open(golden_path, "r") as f:
            golden_html = f.read()

        # Strip code fences (Gemini sometimes wraps output)
        output_clean = output
        fence_match = re.search(r"```(?:html)?\s*(.*?)```", output, re.DOTALL)
        if fence_match:
            output_clean = fence_match.group(1)

        golden_rows = _align_on_header(parse_html_table(golden_html))
        output_rows = _align_on_header(parse_html_table(output_clean))

        if not golden_rows:
            return {"pass": False, "score": 0, "reason": "Golden file has no tables"}
        if not output_rows:
            return {"pass": False, "score": 0, "reason": "Output has no tables"}

        # Align rows using LCS
        pairs = _lcs_align(golden_rows, output_rows)

        # Score matched rows
        total_cells, cell_errors, errors = _score_matched_rows(
            golden_rows, output_rows, pairs
        )

        # Penalty for unmatched rows
        matched_golden = {gi for gi, _ in pairs}
        matched_output = {oi for _, oi in pairs}
        missing_rows = len(golden_rows) - len(matched_golden)
        extra_rows = len(output_rows) - len(matched_output)

        # Add cells from missing golden rows to total
        for i, row in enumerate(golden_rows):
            if i not in matched_golden:
                total_cells += len(row)
                cell_errors += len(row)

        if missing_rows > 0:
            errors.insert(0, f"Missing {missing_rows} golden rows (unmatched)")
        if extra_rows > 0:
            errors.insert(0, f"Extra {extra_rows} output rows (unmatched)")

        total_cells = max(total_cells, 1)
        matched_pct = len(pairs) / len(golden_rows) * 100 if golden_rows else 0

        if cell_errors > 0:
            score = max(0.0, 1.0 - cell_errors / total_cells)
            summary = f"Matched {len(pairs)}/{len(golden_rows)} rows ({matched_pct:.0f}%), {cell_errors} cell errors"
            reason = summary + "\n" + "\n".join(errors[:25])
            if len(errors) > 25:
                reason += f"\n...and {len(errors) - 25} more"
            return {"pass": False, "score": round(score, 4), "reason": reason}

        return {"pass": True, "score": 1.0, "reason": "Exact match"}

    except Exception as e:
        return {"pass": False, "score": 0, "reason": f"Scorer error: {str(e)}"}
