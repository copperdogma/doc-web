"""Hard line breaks end literal URLs without changing source text or markup."""

import pytest
from bs4 import BeautifulSoup

from doc_web.reference_resolution import text_stream
from modules.common.manual_navigation import resolve_navigation


def _entry(html):
    return {'filename': 'one.html', 'body_html': html,
            'prepared_pages': [{'html': html, 'page_number': 1}]}


def _resolve(item):
    return resolve_navigation([item], resolve_references=True)


def _source_text(html):
    return BeautifulSoup(html, 'html.parser').p.get_text()


def _without_generated_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.select('a[data-doc-web-reference="resolved"]'):
        link.unwrap()
    return soup


def test_hard_break_separates_literal_urls_and_preserves_source_offsets():
    original = ('<p id="ref" data-provenance-id="b1">Country A service: '
                'https://service.example/en-au<br>New region service: '
                'https://service.example/en-nz</p>')
    item = _entry(original)
    before = BeautifulSoup(original, 'html.parser')

    report = _resolve(item)
    after = BeautifulSoup(item['body_html'], 'html.parser')
    urls = [row for row in report['references'] if row['kind'] == 'url']
    expected = ['https://service.example/en-au', 'https://service.example/en-nz']

    assert [link['href'] for link in after.p.find_all('a')] == expected
    assert [link.get_text() for link in after.p.find_all('a')] == expected
    assert after.p.find('br').next_sibling == 'New region service: '
    assert after.p.get_text() == before.p.get_text()
    assert str(_without_generated_links(item['body_html'])) == str(before)
    assert {row['resolved_href'] for row in urls} == set(expected)
    for row in urls:
        location = row['source']['location']
        assert _source_text(original)[location['start']:location['end']] == row['original_text']
        assert row['source']['block_id'] == 'ref'


def test_mixed_inline_url_stops_at_break_without_moving_markup_or_existing_anchor():
    original = ('<p id="ref">See https://service.<em data-source="inline">example/en-au</em>'
                '<br><strong>New</strong> region: https://service.example/en-nz; '
                '<a href="https://authored.example/x" title="kept"><em>Authored</em></a></p>')
    item = _entry(original)
    before = BeautifulSoup(original, 'html.parser')

    _resolve(item)
    after = BeautifulSoup(item['body_html'], 'html.parser')
    generated = after.select('a[data-doc-web-reference="resolved"]')

    assert [(link['href'], link.get_text()) for link in generated] == [
        ('https://service.example/en-au', 'https://service.example/en-au'),
        ('https://service.example/en-nz', 'https://service.example/en-nz')]
    assert after.strong.get_text() == 'New'
    assert after.strong.find_parent('a') is None
    assert after.em['data-source'] == 'inline'
    assert after.find('a', title='kept')['href'] == 'https://authored.example/x'
    assert str(_without_generated_links(item['body_html'])) == str(before)

    first = item['body_html']
    _resolve(item)
    assert item['body_html'] == first


@pytest.mark.parametrize('prefix,suffix', [('<br>', ''), ('', '<br>'), ('<br>', '<br>')])
def test_url_at_start_or_end_of_hard_break(prefix, suffix):
    url = 'https://service.example/en-au'
    original = f'<p id="ref">{prefix}{url}{suffix}</p>'
    item = _entry(original)

    stream, _ = text_stream(BeautifulSoup(original, 'html.parser').p)
    expected_stream = ('\n' if prefix else '') + url + ('\n' if suffix else '')
    assert stream == expected_stream
    report = _resolve(item)
    after = BeautifulSoup(item['body_html'], 'html.parser')

    assert [(link['href'], link.get_text()) for link in after.p.find_all('a')] == [(url, url)]
    assert str(_without_generated_links(item['body_html'])) == str(BeautifulSoup(original, 'html.parser'))
    assert report['references'][0]['source']['location'] == {'start': 0, 'end': len(url)}


def test_break_does_not_expose_forbidden_text_or_join_across_it():
    original = ('<p id="ref">https://service.example/en-au<br>'
                '<code>https://hidden.example/private</code>'
                '<br>https://service.example/en-nz</p>')
    item = _entry(original)

    report = _resolve(item)
    after = BeautifulSoup(item['body_html'], 'html.parser')

    assert [link['href'] for link in after.p.find_all('a')] == [
        'https://service.example/en-au', 'https://service.example/en-nz']
    assert not after.code.find('a')
    assert after.code.get_text() == 'https://hidden.example/private'
    assert all('hidden.example' not in row['original_text'] for row in report['references'])


@pytest.mark.parametrize('tail', ['3', '<em data-source="inline">3</em>'])
def test_reference_across_break_reports_only_literal_source_text(tail):
    original = f'<p id="ref">See section<br>{tail}.</p><h2 id="s3">Section 3 Details</h2>'
    item = _entry(original)
    before = BeautifulSoup(original, 'html.parser')

    report = _resolve(item)
    after = BeautifulSoup(item['body_html'], 'html.parser')
    row = report['references'][0]
    location = row['source']['location']

    assert row['resolved_href'] == '#s3'
    assert row['original_text'] == row['anchor_text'] == 'section3'
    assert before.p.get_text()[location['start']:location['end']] == row['original_text']
    assert [link.get_text() for link in after.p.find_all('a')] == ['section', '3']
    assert str(_without_generated_links(item['body_html'])) == str(before)
