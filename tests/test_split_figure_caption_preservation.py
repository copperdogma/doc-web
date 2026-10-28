"""Caption conservation when a resolved multi-image figure is split."""
import pytest
from bs4 import BeautifulSoup

from modules.build.build_chapter_html_v1.main import _split_labeled_multi_image_figures


@pytest.mark.parametrize("owner", ["numeric_distinct", "ambiguous", "absent"])
def test_split_preserves_caption_without_guessing_owner(owner: str) -> None:
    caption = "An extension costs 20 Florins."
    nearby = {
        "numeric_distinct": ("An extension costs 30 Florins.", " An extension  costs 20 Florins. "),
        "ambiguous": (caption, caption),
        "absent": ("An extension costs 30 Florins.", "A warehouse costs 40 Florins."),
    }[owner]
    soup = BeautifulSoup(
        f"""
        <article>
          <p>An extension costs 30 Florins.</p>
          <p>An extension costs 20 Florins.</p>
          <p>A warehouse costs 40 Florins.</p>
          <p id="before">Source position before.</p>
          <figure id="original">
            <img src="images/first.png" data-crop-filename="first.png"
                 data-critical-graphics-role="rule_example_diagram"
                 data-critical-graphics-importance="essential"
                 data-critical-graphics-nearby-text="{nearby[0]}" alt="First diagram"/>
            <img src="images/second.png" data-crop-filename="second.png"
                 data-critical-graphics-role="rule_example_diagram"
                 data-critical-graphics-importance="essential"
                 data-critical-graphics-nearby-text="{nearby[1]}" alt="Second diagram"/>
            <figcaption id="preserved">An extension costs <em>20</em> Florins.</figcaption>
          </figure>
          <p id="after">Source position after.</p>
        </article>
        """,
        "html.parser",
    )
    assert _split_labeled_multi_image_figures(soup) == 2
    preserved = soup.find_all(id="preserved")
    assert len(preserved) == 1
    assert preserved[0].get_text(" ", strip=True) == caption
    assert preserved[0].find("em").get_text() == "20"
    assert sorted(img["src"] for img in soup.find_all("img")) == [
        "images/first.png", "images/second.png",
    ]
    if owner == "numeric_distinct":
        assert preserved[0].name == "figcaption"
        assert preserved[0].parent.find("img")["data-crop-filename"] == "second.png"
        assert soup.find("img", {"data-crop-filename": "first.png"}).parent.find("figcaption") is None
    else:
        assert preserved[0].name == "p"
        assert preserved[0].parent is soup.article
        assert preserved[0].find_previous_sibling("p")["id"] == "before"
        assert preserved[0].find_next_sibling("p")["id"] == "after"
        assert not soup.find_all("figcaption")
    once = str(soup)
    assert _split_labeled_multi_image_figures(soup) == 0
    assert str(soup) == once
