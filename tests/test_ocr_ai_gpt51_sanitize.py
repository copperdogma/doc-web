from modules.extract.ocr_ai_gpt51_v1.main import sanitize_html
from schemas import PageHtml


def test_sanitize_html_allows_only_whitelisted_tags():
    raw = (
        '<div>Bad<div><script>alert(1)</script>'
        '<p class="running-head">6-8</p>'
        '<p class="page-number">17</p>'
        '<p class="other">Text</p>'
        '<span>Ignored</span>'
        '<h2>6</h2>'
        '<table><tr><td>Cell</td></tr></table>'
        '<img alt="Illustration">'
        '</div>'
    )
    clean = sanitize_html(raw)

    assert '<div>' not in clean
    assert '<script>' not in clean
    assert '<span>' not in clean
    assert '<p class="running-head">6-8</p>' in clean
    assert '<p class="page-number">17</p>' in clean
    # non-allowed class is stripped to plain <p>
    assert '<p>Text</p>' in clean
    assert '<h2>6</h2>' in clean
    assert '<table>' in clean
    assert '<td>Cell</td>' in clean
    assert '<img alt="Illustration">' in clean


def test_sanitize_html_allows_figure_and_figcaption():
    """Story 009: <figure>/<figcaption> pass through the sanitizer."""
    raw = '<figure><img alt="Portrait"><figcaption>John Smith, 1920</figcaption></figure>'
    clean = sanitize_html(raw)
    assert '<figure>' in clean
    assert '</figure>' in clean
    assert '<figcaption>' in clean
    assert '</figcaption>' in clean
    assert '<img alt="Portrait">' in clean
    assert 'John Smith, 1920' in clean


def test_sanitize_html_preserves_safe_table_spans_and_page_html_schema_accepts_them():
    clean = sanitize_html(
        '<table><tr><th rowspan="2" colspan="7">Header</th>'
        '<td rowspan="65535" colspan="1001">Invalid spans</td></tr></table>'
    )

    assert '<th rowspan="2" colspan="7">Header</th>' in clean
    assert '<td>Invalid spans</td>' in clean
    PageHtml(page=1, html=clean)


def test_sanitize_html_escapes_decoded_text_and_retained_attribute_values():
    clean = sanitize_html(
        '<p>r2l3 &lt; &amp; &quot; &#39;</p>'
        '<img alt="a &quot;quoted&quot; &amp; useful">'
        '<a href="#one&amp;two&quot;">link</a>'
    )

    assert '<p>r2l3 &lt; &amp; " \'</p>' in clean
    assert '<img alt="a &quot;quoted&quot; &amp; useful">' in clean
    assert '<a href="#one&amp;two&quot;">link</a>' in clean
