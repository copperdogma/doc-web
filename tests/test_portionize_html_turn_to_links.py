#!/usr/bin/env python3
"""
Unit tests for turn_to_links extraction in portionize_html_extract_v1.
"""
from modules.portionize.portionize_html_extract_v1.main import _extract_turn_to_links


def test_extract_turn_to_links_from_anchors():
    html = """
    <p>Choose:</p>
    <a href="#12">Turn to 12</a>
    <a href="#300">Go to 300</a>
    <a href="#12">Turn to 12</a>
    """
    assert _extract_turn_to_links(html) == ["12", "300"]


def test_extract_turn_to_links_empty_html():
    assert _extract_turn_to_links("") == []
    assert _extract_turn_to_links(None) == []


if __name__ == "__main__":
    test_extract_turn_to_links_from_anchors()
    test_extract_turn_to_links_empty_html()
    print("✅ All turn_to_links extraction tests passed!")
