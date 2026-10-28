"""Unresolved image cleanup must not revisit detached figure descendants."""
import pytest
from bs4 import BeautifulSoup
from modules.build.build_chapter_html_v1.main import _remove_unresolved_image_placeholders


@pytest.mark.parametrize("body,expected,images,callouts", [
    ('<figure><img alt="one"><img alt="two"><figcaption>Caption once</figcaption></figure>', 'Caption once', 0, 0),
    ('<figure><img alt="one"><img alt="two"><img alt="three"><figcaption>Caption once</figcaption></figure>', 'Caption once', 0, 0),
    ('<p>Before</p><figure><img><img></figure><p>After</p>', 'Before After', 0, 0),
    ('<figure><img alt="unresolved"><img src="images/valid.png"><figcaption>Caption once</figcaption></figure>', 'Caption once', 1, 0),
    ('<figure><img alt="reminder"><img alt="other"><figcaption>Caption once</figcaption></figure>', 'Caption once', 0, 1),
])
def test_unresolved_figure_cleanup_preserves_caption_once(body, expected, images, callouts):
    soup = BeautifulSoup(body, "html.parser")
    _remove_unresolved_image_placeholders(soup)
    assert soup.get_text(" ", strip=True) == expected
    assert len(soup.find_all("img")) == images
    assert len(soup.find_all("aside")) == callouts
    if images:
        assert soup.img["src"] == "images/valid.png"
    once = str(soup)
    _remove_unresolved_image_placeholders(soup)
    assert str(soup) == once
