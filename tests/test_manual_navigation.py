
import pytest
from bs4 import BeautifulSoup

from modules.build.build_chapter_html_v1.main import _tag_entry_body
from modules.common.manual_navigation import inspect_navigation, resolve_navigation, verify_final_navigation


def _entry(path, html):
    entry = {'filename': path, 'body_html': html, 'prepared_pages': [{'html': html, 'page_number': 1}], 'source_pages': [1]}
    body, rows = _tag_entry_body(entry, run_id='test', created_at='fixed')
    entry['body_html'] = body
    return entry, rows


def test_cross_chapter_numeric_suffixed_named_references_and_provenance():
    first, provenance = _entry('one.html', '<h1>Start</h1><p>Read <a href="#7"><em>7</em></a>, <a href="#12a">12a</a>, and <a href="#setup">Setup</a>.</p>')
    second, other_rows = _entry('two.html', '<h2>7 Travel</h2><h2>12a Repairs</h2><h2>Setup</h2>')
    original_quotes = [r['text_quote'] for r in provenance + other_rows]
    original_source = first['prepared_pages'][0]['html']
    report = resolve_navigation([first, second])
    assert report['summary'] == {'resolved': 3}
    soup = BeautifulSoup(first['body_html'], 'html.parser')
    assert [a['href'] for a in soup.select('a')] == ['two.html#blk-two-0001', 'two.html#blk-two-0002', 'two.html#blk-two-0003']
    assert soup.select_one('a em').get_text() == '7'
    assert [r['text_quote'] for r in provenance + other_rows] == original_quotes
    assert first['prepared_pages'][0]['html'] == original_source
    assert soup.p.get_text() == 'Read 7, 12a, and Setup.'


def test_wrong_existing_destination_is_corrected_from_exact_source_label():
    entry, _ = _entry('one.html', '<h2>7 Travel</h2><h2>8 Repairs</h2><p><a href="#blk-one-0002">7</a></p>')
    report = resolve_navigation([entry])
    assert report['references'][0]['status'] == 'resolved'
    assert BeautifulSoup(entry['body_html'], 'html.parser').a['href'] == '#blk-one-0001'


@pytest.mark.parametrize('before', ['#blk-one-0001', '#%62lk-one-0001'])
def test_valid_destinations_preserved_exactly(before):
    entry, _ = _entry('one.html', f'<h2>7 Travel</h2><p><a href="{before}">7</a></p>')
    report = resolve_navigation([entry])
    assert report['summary'] == {'preserved': 1}
    assert BeautifulSoup(entry['body_html'], 'html.parser').a['href'] == before


def test_old_source_id_is_rebound_even_for_nonheading_destination():
    entry, _ = _entry('one.html', '<p id="note">Keep the wording.</p><p><a href="#note">this note</a></p>')
    report = resolve_navigation([entry])
    assert report['references'][0]['reason'] == 'original_id_rebound'
    assert BeautifulSoup(entry['body_html'], 'html.parser').a['href'] == '#blk-one-0001'


def test_duplicate_unavailable_and_foreign_references_are_explicit_abstentions():
    entry, _ = _entry('one.html', '<h2>7 Travel</h2><h2>7 Another Travel</h2><p><a href="#7">7</a> <a href="#99">99</a> <a href="other-edition.html#7">7</a></p>')
    report = resolve_navigation([entry])
    soup = BeautifulSoup(entry['body_html'], 'html.parser')
    assert not soup.select('a')
    assert [tag['data-doc-web-navigation-status'] for tag in soup.select('p span')] == ['ambiguous', 'unresolved', 'unresolved']
    assert soup.p.get_text() == '7 99 7'
    assert [row['status'] for row in report['references']] == ['ambiguous', 'unresolved', 'unresolved']
    assert len(report['references'][0]['candidates']) == 2


def test_generated_unsupported_heading_does_not_establish_source_target():
    entry, _ = _entry('one.html', '<p><a href="#Setup">Setup</a></p>')
    entry['body_html'] += '<h2 id="invented">Setup</h2>'
    assert resolve_navigation([entry])['summary'] == {'unresolved': 1}


def test_explicit_file_scope_disambiguates_duplicate_heading_tokens():
    first, _ = _entry('one.html', '<h2>7 Travel</h2><p><a href="two.html#7">7</a></p>')
    second, _ = _entry('two.html', '<h2>7 Repairs</h2>')
    resolve_navigation([first, second])
    assert BeautifulSoup(first['body_html'], 'html.parser').a['href'] == 'two.html#blk-two-0001'


def test_validator_inspects_actual_encoded_crossfile_ids_and_abstentions(tmp_path):
    one = tmp_path / 'one.html'
    two = tmp_path / 'chapter two.html'
    two.write_text('<h2 id="section 7">7 Travel</h2><p id="duplicate">A</p><p id="duplicate">B</p>')
    one.write_text('<a href="chapter%20two.html#section%207">7</a><a href="chapter%20two.html#duplicate">bad</a><a href="#missing">absent</a><a href="https://example.org/#7">external</a><span data-doc-web-navigation-status="ambiguous" data-doc-web-original-href="#8">8</span>')
    (tmp_path / 'index.html').write_text('<a href="not-there.html">missing chapter</a>')
    issues, annotations = inspect_navigation([one, two])
    assert [row['reason'] for row in issues] == ['duplicate_fragment', 'missing_fragment', 'missing_file']
    assert annotations == [{'path': 'one.html', 'status': 'ambiguous', 'original_href': '#8', 'anchor_text': '8'}]


def test_duplicate_final_ids_are_not_selected():
    entry, _ = _entry('one.html', '<h2>7 Travel</h2><p><a href="#7">7</a></p>')
    entry['body_html'] += '<p id="blk-one-0001">Duplicated ID</p>'
    report = resolve_navigation([entry])
    assert report['summary'] == {'unresolved': 1}
    assert not BeautifulSoup(entry['body_html'], 'html.parser').find('a')


def test_validator_detects_source_proven_wrong_existing_crosschapter_target(tmp_path):
    one, two = tmp_path / 'one.html', tmp_path / 'two.html'
    one.write_text('<h2 id="section8">8 Repairs</h2><p><a href="#section8">7</a></p><p><a href="#section8">author choice</a></p>')
    two.write_text('<h2 id="section7">7 Travel</h2>')
    source_pages = [{'html': '<h2>8 Repairs</h2><p><a href="#8">7</a></p><p><a href="#8">author choice</a></p><h2>7 Travel</h2>'}]
    issues, _ = inspect_navigation([one, two], source_pages=source_pages)
    assert issues == [{'path': 'one.html', 'href': '#section8', 'anchor_text': '7', 'reason': 'source_heading_target_mismatch'}]


def test_validator_preserves_uncertain_semantics_for_repeated_named_headings(tmp_path):
    one, two = tmp_path / 'one.html', tmp_path / 'two.html'
    one.write_text('<h2 id="a">Setup</h2><p><a href="#a">Setup</a></p>')
    two.write_text('<h2 id="b">Setup</h2>')
    assert inspect_navigation([one, two], source_pages=[{'html': '<h2>Setup</h2><p><a href="#a">Setup</a></p>'}]) == ([], [])


def test_valid_original_id_disambiguates_repeated_heading_labels():
    entry, _ = _entry('one.html', '<h2 id="first">Setup</h2><h2 id="second">Setup</h2><p><a href="#second">Setup</a></p>')
    assert resolve_navigation([entry])['summary'] == {'resolved': 1}
    assert BeautifulSoup(entry['body_html'], 'html.parser').a['href'] == '#blk-one-0002'


def test_wrong_existing_file_and_fragment_corrected_within_document_scope():
    first, _ = _entry('one.html', '<h2>8 Repairs</h2><p><a href="one.html#blk-one-0001">7</a></p>')
    second, _ = _entry('two.html', '<h2>7 Travel</h2>')
    assert resolve_navigation([first, second])['summary'] == {'resolved': 1}
    assert BeautifulSoup(first['body_html'], 'html.parser').a['href'] == 'two.html#blk-two-0001'


@pytest.mark.parametrize('href,payload', [('images/map.png', b'\x89PNG\r\n'), ('manual.pdf#page=2', b'%PDF-1.4\n\xff\xfe'), ('image%20map.png#7', b'\xff')])
def test_included_non_html_links_preserve_literal_href_and_inline_markup(tmp_path, href, payload):
    from urllib.parse import unquote, urlsplit
    resource = tmp_path / unquote(urlsplit(href).path)
    resource.parent.mkdir(parents=True, exist_ok=True)
    resource.write_bytes(payload)
    entry, _ = _entry('one.html', f'<h2>7 Travel</h2><p><a download href="{href}"><em>7</em></a></p>')
    report = resolve_navigation([entry], bundle_root=tmp_path)
    anchor = BeautifulSoup(entry['body_html'], 'html.parser').a
    assert anchor['href'] == href and anchor.has_attr('download') and anchor.em.get_text() == '7'
    assert report['summary'] == {'preserved': 1}
    assert report['references'][0]['resource_exists'] is True
    html = tmp_path / 'one.html'
    html.write_text(entry['body_html'])
    observations = []
    assert inspect_navigation([html], source_pages=entry['prepared_pages'], resource_observations=observations) == ([], [])
    assert len(observations) == (1 if urlsplit(href).fragment else 0)


def test_resource_catalog_can_preserve_asset_without_filesystem_access():
    entry, _ = _entry('one.html', '<p><a href="images/map.png">Map</a></p>')
    report = resolve_navigation([entry], resource_catalog={'images/map.png'})
    assert report['summary'] == {'preserved': 1}
    assert BeautifulSoup(entry['body_html'], 'html.parser').a['href'] == 'images/map.png'


def test_missing_resources_remain_links_and_fail_existence_validation(tmp_path):
    entry, _ = _entry('one.html', '<p><a href="absent.pdf#page=2">Manual</a></p>')
    report = resolve_navigation([entry], bundle_root=tmp_path)
    assert report['references'][0]['reason'] == 'missing_resource'
    html = tmp_path / 'one.html'
    html.write_text(entry['body_html'])
    assert BeautifulSoup(entry['body_html'], 'html.parser').a['href'] == 'absent.pdf#page=2'
    issues, _ = inspect_navigation([html])
    assert issues[0]['reason'] == 'missing_file'


def test_unprovided_resource_catalog_reports_unmeasured_without_dropping_asset_link():
    entry, _ = _entry('one.html', '<p><a href="map.png#xywh=0,0,10,10">Map</a></p>')
    report = resolve_navigation([entry])
    assert report['references'][0]['reason'] == 'resource_existence_unmeasured'
    assert report['references'][0]['fragment_status'] == 'unmeasured_media_fragment'
    assert BeautifulSoup(entry['body_html'], 'html.parser').a['href'] == 'map.png#xywh=0,0,10,10'


def test_unreadable_html_target_is_diagnostic_not_parser_crash(tmp_path):
    one = tmp_path / 'one.html'
    one.write_text('<a href="other.html#7">7</a>')
    (tmp_path / 'other.html').write_bytes(b'\xff\xfe')
    issues, _ = inspect_navigation([one])
    assert issues[0]['reason'] == 'unreadable_html_target'


def test_valid_authored_duplicate_heading_destination_preserved_with_semantic_ambiguity_observation(tmp_path):
    entry, _ = _entry('one.html', '<h2 id="a">Setup</h2><h2 id="b">Setup</h2><p><a href="#blk-one-0002">Setup</a></p>')
    before = BeautifulSoup(entry['body_html'], 'html.parser').a['href']
    report = resolve_navigation([entry])
    assert report['summary'] == {'preserved': 1}
    assert len(report['semantic_observations']) == 1
    assert report['references'][0]['semantic_status'] == 'semantic_label_ambiguity'
    assert BeautifulSoup(entry['body_html'], 'html.parser').a['href'] == before
    html = tmp_path / 'one.html'
    html.write_text(entry['body_html'])
    observations = []
    assert inspect_navigation([html], source_pages=entry['prepared_pages'], semantic_observations=observations) == ([], [])
    assert observations[0]['status'] == 'semantic_label_ambiguity'
    assert observations[0]['href'] == before
    assert len(observations[0]['candidates']) == 2


@pytest.mark.parametrize('href', ['https://[broken/a', 'https://example.org:invalid/a', 'https://example.org/\x01bad'])
def test_malformed_existing_uri_is_a_diagnostic_in_optout_and_inspector(tmp_path, href):
    entry, _ = _entry('one.html', f'<p><a href="{href}">Original text</a></p>')
    report = resolve_navigation([entry])
    assert report['references'][0]['resolution_status'] == 'missing'
    assert report['references'][0]['reason'].startswith('invalid_')
    path = tmp_path / 'one.html'
    path.write_text(f'<p><a href="{href}">Original text</a></p>')
    issues, _ = inspect_navigation([path])
    assert issues[0]['reason'].startswith('invalid_')


def test_final_inspector_detects_nested_anchors(tmp_path):
    path = tmp_path / 'one.html'
    path.write_text('<p id="p"><a href="#p">outer<a href="#p">inner</a></a></p>')
    issues, _ = inspect_navigation([path])
    assert any(r['reason'] == 'nested_anchor' for r in issues)


@pytest.mark.parametrize('heading,label', [
    ('3 Equipment', 'See page 3'),
    ('Return policy', 'Return to section 10'),
])
def test_existing_typed_prose_cannot_borrow_wrong_heading(heading, label):
    entry, _ = _entry('one.html', f'<h2>{heading}</h2><p><a href="#missing">{label}</a></p>')
    report = resolve_navigation([entry], resolve_references=False)
    assert report['references'][0]['resolution_status'] == 'missing'
    assert not BeautifulSoup(entry['body_html'], 'html.parser').find('a')


def test_existing_prefixed_typed_reference_matches_exact_kind_and_label():
    entry, _ = _entry('one.html', '<h2>Section 10 Repairs</h2><p><a href="#missing">Return to section 10</a></p>')
    report = resolve_navigation([entry], resolve_references=False)
    assert report['references'][0]['resolution_status'] == 'resolved'
    assert BeautifulSoup(entry['body_html'], 'html.parser').a['href'] == '#blk-one-0001'


@pytest.mark.parametrize('label', ['See sections 3', 'See section 3–4', 'See section 3 and section 4'])
def test_existing_plural_range_multiple_typed_references_abstain(label):
    entry, _ = _entry('one.html', f'<h2>Section 3</h2><h2>Section 4</h2><p><a href="#missing">{label}</a></p>')
    report = resolve_navigation([entry], resolve_references=False)
    row = report['references'][0]
    assert row['resolution_status'] == 'ambiguous'
    assert row['reason'] == 'ambiguous_typed_reference'
    assert not BeautifulSoup(entry['body_html'], 'html.parser').find('a')


@pytest.mark.parametrize('href', ['#original', '#blk-one-0001'])
def test_existing_authoritative_targets_survive_typed_label_uncertainty(href):
    entry, _ = _entry('one.html', f'<h2 id="original">3 Equipment</h2><p><a href="{href}">See pages 3–4</a></p>')
    report = resolve_navigation([entry], resolve_references=False)
    assert report['references'][0]['resolution_status'] == 'resolved'
    assert BeautifulSoup(entry['body_html'], 'html.parser').a['href'] == '#blk-one-0001'


def test_final_existing_printed_page_target_does_not_borrow_numbered_heading(tmp_path):
    html = '<h2 id="wrong">3 Equipment</h2><p id="page3">Printed page content.</p><p><a href="#page3">See page 3</a></p>'
    entry = {'filename': 'one.html', 'body_html': html, 'prepared_pages': [{'html': html, 'page_number': 1}]}
    assert resolve_navigation([entry], resolve_references=False)['references'][0]['status'] == 'preserved'
    path = tmp_path / 'one.html'
    path.write_text(entry['body_html'])
    assert inspect_navigation([path], source_pages=entry['prepared_pages']) == ([], [])


@pytest.mark.parametrize('href', ['#old', 'two.html#old'])
def test_final_inspection_composes_original_alias_authority_and_repeat_resolution(tmp_path, href):
    source = f'<h2 id="a">Section 1 Maps</h2><p><a href="{href}">Section 1</a></p>'
    first = {'filename': 'one.html', 'body_html': source, 'prepared_pages': [{'html': source}]}
    second_html = '<h2 id="b">Section 2 Repairs</h2><h2 id="c">Section 3 Other</h2>'
    second = {'filename': 'two.html', 'body_html': second_html, 'prepared_pages': [{'html': second_html}],
              '_navigation_id_aliases': {'old': ['b']}}
    entries = [first, second]
    pages = [page for item in entries for page in item['prepared_pages']]
    resolve_navigation(entries, resolve_references=True)
    assert BeautifulSoup(first['body_html'], 'html.parser').a['href'] == 'two.html#b'
    before = first['body_html']
    resolve_navigation(entries, resolve_references=True)
    assert first['body_html'] == before
    files = []
    for item in entries:
        path = tmp_path / item['filename']
        path.write_text(item['body_html'])
        files.append(path)
    assert verify_final_navigation(files, source_pages=pages, source_entries=entries)['status'] == 'passed'
    # A changed actual href cannot borrow the alias's receipt.
    files[0].write_text(first['body_html'].replace('two.html#b', 'two.html#c'))
    assert verify_final_navigation(files, source_pages=pages, source_entries=entries)['issues'][0]['reason'] == 'alias_receipt_missing_or_changed'
    files[0].write_text(first['body_html'].replace('two.html#b', '#absent'))
    assert any(issue['reason'] == 'missing_fragment' for issue in verify_final_navigation(files, source_pages=pages, source_entries=entries)['issues'])


@pytest.mark.parametrize('href', ['#old', '#b'])
def test_final_same_file_alias_receipt_survives_existing_href_authority(tmp_path, href):
    html = f'<h2 id="a">Section 1 Maps</h2><h2 id="b">Section 2 Repairs</h2><p><a href="{href}">Section 1</a></p>'
    item = {'filename': 'one.html', 'body_html': html, 'prepared_pages': [{'html': html}],
            '_navigation_id_aliases': {href[1:]: ['b']}}
    resolve_navigation([item], resolve_references=True)
    before = item['body_html']
    resolve_navigation([item], resolve_references=True)
    assert item['body_html'] == before
    path = tmp_path / 'one.html'
    path.write_text(item['body_html'])
    assert verify_final_navigation([path], source_entries=[item])['status'] == 'passed'


def test_final_alias_map_requires_matching_original_source_anchor(tmp_path):
    path = tmp_path / 'one.html'
    path.write_text('<h2 id="a">Section 1</h2><h2 id="b">Section 2</h2><p><a href="#b">Section 1</a></p>')
    aliases = {'old': ['b']}
    pages = [{'html': '<h2>Section 1</h2><h2>Section 2</h2><a href="#different">Section 1</a>'}]
    assert verify_final_navigation([path], source_entries=[{'filename': 'one.html', 'prepared_pages': pages, '_navigation_id_aliases': aliases}])['issues'][0]['reason'] == 'source_heading_target_mismatch'


def test_final_same_label_alias_evidence_must_have_one_destination(tmp_path):
    path = tmp_path / 'one.html'
    path.write_text('<h2 id="a">Section 1</h2><h2 id="b">Section 2</h2><p><a href="#b">Section 1</a></p>')
    pages = [{'html': '<h2>Section 1</h2><h2>Section 2</h2><a href="#old-a">Section 1</a><a href="#old-b">Section 1</a>'}]
    aliases = {'old-a': ['a'], 'old-b': ['b']}
    assert verify_final_navigation([path], source_entries=[{'filename': 'one.html', 'prepared_pages': pages, '_navigation_id_aliases': aliases}])['issues'][0]['reason'] == 'source_heading_target_mismatch'


@pytest.mark.parametrize('other_file', [False, True])
def test_final_alias_receipt_cannot_be_borrowed_by_same_label_occurrence(tmp_path, other_file):
    first_html = '<h2 id="a">Section 1</h2><p><a href="#missing">Section 1</a></p>'
    alias_html = '<h2 id="b">Section 2</h2><p><a href="#old">Section 1</a></p>'
    if other_file:
        entries = [{'filename': 'one.html', 'body_html': first_html, 'prepared_pages': [{'html': first_html}]},
                   {'filename': 'two.html', 'body_html': alias_html, 'prepared_pages': [{'html': alias_html}], '_navigation_id_aliases': {'old': ['b']}}]
    else:
        entries = [{'filename': 'one.html', 'body_html': first_html + alias_html,
                    'prepared_pages': [{'html': first_html + alias_html}], '_navigation_id_aliases': {'old': ['b']}}]
    resolve_navigation(entries)
    paths = []
    for item in entries:
        path = tmp_path / item['filename']
        path.write_text(item['body_html'])
        paths.append(path)
    assert verify_final_navigation(paths, source_entries=entries)['status'] == 'passed'
    parsed = BeautifulSoup(entries[0]['body_html'], 'html.parser')
    parsed.a['href'] = 'two.html#b' if other_file else '#b'
    paths[0].write_text(str(parsed))
    issues = verify_final_navigation(paths, source_entries=entries)['issues']
    assert len(issues) == 1 and issues[0]['reason'] == 'source_heading_target_mismatch'


def test_initial_spoofed_alias_receipt_is_removed_and_recomputed(tmp_path):
    html = '<h2 id="a">Section 1</h2><h2 id="b">Section 2</h2><p><a href="#missing" data-doc-web-alias-receipt="1" data-doc-web-original-alias-href="#old">Section 1</a><a href="#old">Section 1</a></p>'
    item = {'filename': 'one.html', 'body_html': html, 'prepared_pages': [{'html': html}], '_navigation_id_aliases': {'old': ['b']}}
    resolve_navigation([item])
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert soup.find_all('a')[0]['href'] == '#a'
    assert not soup.find_all('a')[0].has_attr('data-doc-web-alias-receipt')
    assert soup.find_all('a')[1]['href'] == '#b'
    path = tmp_path / 'one.html'
    path.write_text(item['body_html'])
    assert verify_final_navigation([path], source_entries=[item])['status'] == 'passed'


@pytest.mark.parametrize('mutation', ['move', 'delete', 'semantic_target', 'delete_file'])
def test_expected_alias_receipt_is_fatal_when_moved_missing_or_changed(tmp_path, mutation):
    html = '<h2 id="a">Section 1</h2><h2 id="b">Section 2</h2><p><a href="#missing">Section 1</a><a href="#old">Section 1</a></p>'
    item = {'filename': 'one.html', 'body_html': html, 'prepared_pages': [{'html': html}], '_navigation_id_aliases': {'old': ['b']}}
    resolve_navigation([item])
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    first, alias = soup.find_all('a')
    if mutation == 'move':
        first['href'], alias['href'] = alias['href'], first['href']
        for attribute in ['data-doc-web-alias-receipt', 'data-doc-web-original-alias-href']:
            first[attribute] = alias.attrs.pop(attribute)
    elif mutation == 'delete':
        alias.attrs.pop('data-doc-web-alias-receipt')
        alias.attrs.pop('data-doc-web-original-alias-href')
    else:
        alias['href'] = '#a'
    path = tmp_path / 'one.html'
    path.write_text(str(soup))
    if mutation == 'delete_file':
        path.unlink()
    result = verify_final_navigation([path], source_entries=[item])
    assert result['status'] == 'failed'
    expected = 'alias_receipt_file_missing' if mutation == 'delete_file' else 'alias_receipt_missing_or_changed'
    assert any(issue['reason'] == expected for issue in result['issues'])


def test_alias_receipt_final_ordinal_includes_newly_discovered_earlier_anchors(tmp_path):
    html = '<h2 id="a">Section 1</h2><h2 id="b">Section 2</h2><p>See section 1. https://example.org. <a href="#old">Section 1</a></p>'
    item = {'filename': 'one.html', 'body_html': html, 'prepared_pages': [{'html': html}], '_navigation_id_aliases': {'old': ['b']}}
    resolve_navigation([item], resolve_references=True)
    receipt = next(iter(item['_navigation_alias_receipts'].values()))
    assert receipt['final_anchor_ordinal'] == 3
    before = item['body_html']
    resolve_navigation([item], resolve_references=True)
    assert item['body_html'] == before
    path = tmp_path / 'one.html'
    path.write_text(item['body_html'])
    assert verify_final_navigation([path], source_entries=[item])['status'] == 'passed'


@pytest.mark.parametrize('boundary', ['article', 'office'])
def test_alias_receipt_ordinal_excludes_only_caller_owned_chrome(tmp_path, boundary):
    html = '<h2 id="a">Section 1</h2><h2 id="b">Section 2</h2><p><a href="#old">Section 1</a></p>'
    item = {'filename': 'one.html', 'body_html': html, 'prepared_pages': [{'html': html}], '_navigation_id_aliases': {'old': ['b']}}
    resolve_navigation([item])
    chrome = '<nav class="doc-nav"><a href="#a">Previous</a></nav>'
    if boundary == 'article':
        exported = '<body>' + chrome + '<article>' + item['body_html'] + '</article></body>'
        context = {**item, '_navigation_content_selector': 'body > article'}
    else:
        exported = '<body>' + chrome + item['body_html'] + '</body>'
        context = {**item, '_navigation_content_selector': 'body', '_navigation_generated_prefix_selector': 'body > nav.doc-nav:first-child'}
    path = tmp_path / 'one.html'
    path.write_text(exported)
    assert verify_final_navigation([path], source_entries=[context])['status'] == 'passed'


@pytest.mark.parametrize('mapped', ['b', 'c'])
def test_generated_reference_cannot_acquire_source_alias_authority_on_repeat(mapped):
    html = '<h2 id="b">Section 2</h2><h2 id="c">Section 3</h2><p>See section 2.</p>'
    item = {'filename': 'one.html', 'body_html': html, 'prepared_pages': [{'html': html}], '_navigation_id_aliases': {'b': [mapped]}}
    resolve_navigation([item], resolve_references=True)
    before = item['body_html']
    assert BeautifulSoup(before, 'html.parser').a['href'] == '#b'
    resolve_navigation([item], resolve_references=True)
    assert item['body_html'] == before
    assert item['_navigation_alias_receipts'] == {}


def test_alias_requires_original_anchor_in_owning_source():
    source = '<h2 id="b">Section 2</h2>'
    item = {'filename': 'one.html', 'body_html': source + '<p><a href="#old">Section 1</a></p>',
            'prepared_pages': [{'html': source}], '_navigation_id_aliases': {'old': ['b']}}
    report = resolve_navigation([item])
    assert report['references'][0]['resolution_status'] == 'missing'
    assert report['references'][0]['reason'] == 'source_reference_unavailable'
    assert item['_navigation_alias_receipts'] == {}
    assert not BeautifulSoup(item['body_html'], 'html.parser').find('a')
