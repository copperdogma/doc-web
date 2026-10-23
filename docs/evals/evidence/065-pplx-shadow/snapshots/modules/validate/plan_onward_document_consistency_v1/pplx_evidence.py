"""Explicit eval-only lossless observed features, never reviewer labels/conventions."""

from bs4 import BeautifulSoup


def observed(soup):
    return {
        "observed_html": str(soup),
        "note_attachments": [
            {
                "text": n.get_text(" ", strip=True),
                "attributes": dict(n.attrs),
                "links": [
                    {"text": a.get_text(" ", strip=True), "href": a.get("href")}
                    for a in n.find_all("a", href=True)
                ],
            }
            for n in soup.find_all("aside")
        ],
        "tables": [
            {
                "headers": [x.get_text(" ", strip=True) for x in t.find_all("th")],
                "rows": [
                    [c.get_text(" ", strip=True) for c in tr.find_all("td")]
                    for tr in t.find_all("tr")
                    if tr.find_all("td")
                ],
                "cell_attributes": [
                    [dict(c.attrs) for c in tr.find_all(["td", "th"])]
                    for tr in t.find_all("tr")
                ],
                "table_attributes": dict(t.attrs),
                "page_break_before": bool(t.get("data-page-break-before") == "true"),
            }
            for t in soup.find_all("table")
        ],
        "prose": [
            p.get_text(" ", strip=True)
            for p in soup.find_all(["p", "aside", "h1", "h2", "h3"])
        ],
        "unanchored_notes": [
            p.get_text(" ", strip=True)
            for p in soup.find_all("aside")
            if not p.get("data-person") and not p.find("a", href=True)
        ],
    }


def observed_chapter(soup, source_pages, page_rows):
    pages = [
        {
            "page_number": n,
            **observed(
                BeautifulSoup(
                    page_rows[n].get("html") or page_rows[n].get("raw_html") or "",
                    "html.parser",
                )
            ),
        }
        for n in source_pages
        if n in page_rows
    ]
    return {
        "chapter": observed(soup),
        "source_pages": pages,
        "source_unanchored_notes": [x for p in pages for x in p["unanchored_notes"]],
        "basis": "observed synthetic extracted chapter HTML and available source-page HTML; absence is not evidence of correctness",
    }
