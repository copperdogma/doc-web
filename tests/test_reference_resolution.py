"""Independent exact navigation controls: text, identity and uncertainty."""
import pytest
from bs4 import BeautifulSoup, NavigableString

from modules.common.manual_navigation import resolve_navigation


def entry(html, filename='one.html', pages=None):
    return {'filename': filename, 'body_html': html,
            'prepared_pages': pages or [{'html': html, 'page_number': 1}]}


def resolve(entries, pages=(), provenance=()):
    return resolve_navigation(entries, resolve_references=True, source_pages=pages, provenance_rows=provenance)


def test_opt_out_does_not_discover_or_enrich():
    item = entry('<h2 id="s">Section 3 Maps</h2><p id="p">See section 3 and https://example.org.</p>')
    report = resolve_navigation([item])
    assert report['references'] == []
    assert '<a' not in item['body_html']
    assert report['api_calls'] == report['cost_usd'] == 0


def test_explicit_typed_references_cross_files_and_inline_markup():
    src = entry('<p id="p">See section <em>3</em>, Figure 2 and paragraph 9.</p>')
    dst = entry('<h2 id="s">Section 3 Maps</h2><figcaption id="f">Figure 2: Diagram</figcaption><h2 id="n">9 Repairs</h2>', 'second chapter.html')
    before = BeautifulSoup(src['body_html'], 'html.parser').get_text()
    report = resolve([src, dst])
    soup = BeautifulSoup(src['body_html'], 'html.parser')
    assert soup.get_text() == before
    assert soup.em.get_text() == '3'
    assert not soup.select('a a')
    assert {a['href'] for a in soup.select('a')} == {'second%20chapter.html#s', 'second%20chapter.html#f', 'second%20chapter.html#n'}
    assert len(report['references']) == 3
    assert all(r['resolution_status'] == 'resolved' for r in report['references'])


def test_observed_print_labels_offset_roman_and_provenance():
    item = entry('<p id="ref">See page 12 and page iv.</p><p id="a">Page twelve body</p><p id="b">Front matter</p>')
    pages = [{'page_number': 20, 'printed_page_number': 12, 'original_page_number': 10, 'spread_side': 'R'},
             {'page_number': 4, 'printed_page_number_text': 'iv'}]
    provenance = [{'block_id': 'a', 'source_page_number': 20}, {'block_id': 'b', 'source_page_number': 4},
                  {'block_id': 'ref', 'source_page_number': 1}]
    report = resolve([item], pages, provenance)
    assert {r['resolved_href'] for r in report['references']} == {'#a', '#b'}
    assert all(r['source']['provenance']['block_id'] == 'ref' for r in report['references'])
    assert next(r for r in report['references'] if r['original_text'] == 'page 12')['target']['evidence']['original_page_number'] == 10


def test_inferred_duplicate_missing_and_range_abstain():
    item = entry('<p id="ref">Pages 2–4; page 8; page 9; page 99.</p><p id="a">A</p><p id="b">B</p>')
    pages = [{'page_number': 10, 'printed_page_number': 8, 'printed_page_number_inferred': True},
             {'page_number': 11, 'printed_page_number': 9}, {'page_number': 12, 'printed_page_number': 9}]
    rows = [{'block_id': 'a', 'source_page_number': 11}, {'block_id': 'b', 'source_page_number': 12}]
    report = resolve([item], pages, rows)
    by_text = {r['original_text']: r for r in report['references']}
    assert by_text['Pages 2–4']['reason'] == 'unsupported_range'
    assert by_text['page 8']['reason'] == 'inferred_printed_label'
    assert by_text['page 9']['resolution_status'] == 'ambiguous'
    assert by_text['page 99']['resolution_status'] == 'missing'
    assert '<a' not in item['body_html']


def test_no_scan_page_fallback_and_no_generated_target_authority():
    item = entry('<p id="p">page 1 and section 5</p>')
    item['body_html'] += '<h2 id="invented">Section 5 Invented</h2>'
    report = resolve([item])
    assert report['resolution_summary'] == {'missing': 2}


def test_toc_and_index_page_lists_preserve_leaders_and_ranges():
    item = entry('<section class="toc"><p id="ref">Introduction .... 12</p></section><section role="doc-index"><p id="idx"><em>Maps</em>, 12, iv, 12–15</p></section><p id="a">Body</p><p id="b">Front</p>')
    pages = [{'page_number': 20, 'printed_page_number': 12}, {'page_number': 4, 'printed_page_number_text': 'iv'}]
    provenance = [{'block_id': 'a', 'source_page_number': 20}, {'block_id': 'b', 'source_page_number': 4}]
    before = BeautifulSoup(item['body_html'], 'html.parser').get_text()
    report = resolve([item], pages, provenance)
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert soup.get_text() == before
    assert [a.get_text() for a in soup.select('a')] == ['12', '12', 'iv']
    assert len(report['references']) == 4
    assert next(r for r in report['references'] if r['original_text'] == '12–15')['reason'] == 'unsupported_range'


def test_literal_url_punctuation_and_forbidden_chrome():
    item = entry('<p id="p">(https://example.org/a?q=1&amp;b=2). https://example.org/a_(b).</p><pre>page 12</pre><code>section 2</code><nav>page 4</nav><p><a href="https://example.org">page 2</a></p>')
    report = resolve([item])
    assert len(report['references']) == 3
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert [r['target']['href'] for r in report['references'] if r.get('kind') == 'url'] == ['https://example.org/a_(b)', 'https://example.org/a?q=1&b=2']
    assert not soup.select('a a,pre a,code a,nav a')


def test_idempotent_enrichment_and_alias_authority_over_label():
    item = entry('<h2 id="a">Section 1 Maps</h2><h2 id="b">Section 2 Repairs</h2><p id="p"><a href="#old">Section 1</a>; section 2.</p>')
    item['_navigation_id_aliases'] = {'old': ['b']}
    resolve([item])
    first = item['body_html']
    assert BeautifulSoup(first, 'html.parser').a['href'] == '#b'
    resolve([item])
    assert item['body_html'] == first


def test_numbered_targets_reject_duplicate_ids():
    item = entry('<h2 id="x">Section 2 Maps</h2><p id="x">Duplicate</p><p>See section 2.</p>')
    assert resolve([item])['references'][0]['resolution_status'] == 'missing'


def test_no_chapter_first_id_fallback_for_missing_page_mapping():
    item = entry('<h2 id="first">Start</h2><p id="ref">page 12</p>', pages=[{'page_number': 1, 'html': '<h2>Start</h2>'}, {'page_number': 20, 'printed_page_number': 12, 'html': '<p>Missing final body</p>'}])
    assert resolve([item])['references'][0]['resolution_status'] == 'missing'


def test_duplicate_page_identities_same_location_remain_ambiguous():
    item = entry('<p id="a">Body</p><p id="ref">page 12</p>')
    pages = [{'page_number': 20, 'printed_page_number': 12, 'html': '<p>Body</p>'},
             {'page_number': 21, 'printed_page_number': 12, 'html': '<p>Body</p>'}]
    assert resolve([item], pages)['references'][0]['resolution_status'] == 'ambiguous'


def test_epub_toc_nav_and_generic_dotted_leaders_but_not_navigation_chrome():
    item = entry('<nav epub:type="toc"><ol><li>Maps .... 12</li></ol></nav><p>Repairs .... 12</p><nav class="chapter-navigation">page 12</nav><p id="body">Target</p>')
    report = resolve([item], [{'page_number': 20, 'printed_page_number': 12}], [{'block_id': 'body', 'source_page_number': 20}])
    assert len(report['references']) == 2
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert len(soup.select('nav a')) == 1
    assert not soup.select('.chapter-navigation a')


def test_plain_mention_does_not_define_section_and_turn_to_is_explicit():
    item = entry('<p id="mention">Section 7 is discussed here.</p><h2 id="n">9</h2><p id="ref">See section 7. Turn to 9. Return to 9.</p>')
    # A bare numeric heading is an explicit numbered paragraph target.
    report = resolve([item])
    assert all(r['resolution_status'] == 'missing' for r in report['references'] if 'section 7' in r['original_text'].casefold())
    assert all(r['resolved_href'] == '#n' for r in report['references'] if 'to 9' in r['original_text'])


def test_malformed_url_reports_abstention_without_crash():
    report = resolve([entry('<p>https://[bad-host/a</p>')])
    assert report['references'][0]['reason'] == 'invalid_http_url'


def test_partial_nested_inline_reference_keeps_parent_tree_and_single_record():
    item = entry('<h2 id="n">Section 9</h2><p id="p"><em id="e">Before turn <strong id="s">to 9 after</strong> end</em>.</p>')
    before = BeautifulSoup(item['body_html'], 'html.parser').get_text()
    report = resolve([item])
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert soup.get_text() == before
    assert len(soup.find_all(id='e')) == len(soup.find_all(id='s')) == 1
    assert soup.find(id='e').strong['id'] == 's'
    assert {a['href'] for a in soup.select('p a')} == {'#n'}
    assert ''.join(a.get_text() for a in soup.select('p a')) == 'turn to 9'
    assert len(report['references']) == 1
    assert report['references'][0]['resolution_status'] == 'resolved'
    assert not soup.select('a a')


def test_reference_does_not_cross_excluded_inline_text_or_existing_links():
    item = entry('<h2 id="n">Section 9</h2><p>turn to <code>ignored</code>9; section <a href="https://example.org">9</a>; turn <em>to 9</em></p>')
    report = resolve([item])
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert len([r for r in report['references'] if r.get('kind') == 'numbered_location']) == 1
    assert not soup.select('code a,a a')
    assert soup.code.get_text() == 'ignored'


def test_duplicate_raw_printed_labels_abstain_when_one_page_not_emitted():
    item = entry('<p id="target">Body</p><p id="ref">page 22</p>')
    pages = [{'page_number': 4, 'printed_page_number': 22}, {'page_number': 5, 'printed_page_number': 22}]
    report = resolve([item], pages, [{'block_id': 'target', 'source_page_number': 4}])
    row = report['references'][0]
    assert row['resolution_status'] == 'ambiguous'
    assert row['reason'] == 'duplicate_observed_printed_labels'
    assert len(row['page_observations']) == 2
    assert '<a' not in item['body_html']


def test_unique_cross_split_source_alias_rebinds_without_filename():
    first = entry('<p id="ref"><a href="#old-note">this note</a></p>')
    second = entry('<p id="note">Original note</p>', 'two.html')
    second['_navigation_id_aliases'] = {'old-note': ['note']}
    report = resolve_navigation([first, second])
    assert BeautifulSoup(first['body_html'], 'html.parser').a['href'] == 'two.html#note'
    assert report['references'][0]['reason'] == 'original_id_rebound'


def test_duplicate_cross_file_source_aliases_abstain():
    first = entry('<p id="ref"><a href="#old-note">this note</a></p>')
    second = entry('<p id="note">Original note</p>', 'two.html')
    third = entry('<p id="note">Different note</p>', 'three.html')
    for item in [second, third]:
        item['_navigation_id_aliases'] = {'old-note': ['note']}
    report = resolve_navigation([first, second, third])
    assert report['references'][0]['resolution_status'] == 'ambiguous'
    assert '<a' not in first['body_html']


def test_overlapping_phrases_and_url_paths_never_nest_links():
    item = entry('<h2 id="n">Paragraph 9</h2><h2 id="s">Section 9</h2><p>Turn to paragraph 9. https://example.org/section9</p>')
    report = resolve([item])
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert len(report['references']) == 2
    assert not soup.select('a a')
    assert {a.get_text() for a in soup.select('p a')} == {'Turn to paragraph 9', 'https://example.org/section9'}


def test_url_cannot_cross_excluded_inline_code():
    item = entry('<p>https://example.<code>BAD</code>org/x</p>')
    report = resolve([item])
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert '<a' not in item['body_html']
    assert soup.code.get_text() == 'BAD'
    assert report['references'][0]['reason'] == 'excluded_inline_url_boundary'


def test_generated_heading_cannot_borrow_source_authority_from_other_file():
    first = entry('<p><a href="one.html#missing">Setup</a></p>')
    first['body_html'] += '<h2 id="invented">Setup</h2>'
    second = entry('<h2 id="real">Setup</h2>', 'two.html')
    resolve_navigation([first, second])
    assert BeautifulSoup(first['body_html'], 'html.parser').a['href'] == 'two.html#real'


def test_shared_logical_page_number_requires_spread_identity():
    item = entry('<p id="left">L</p><p id="right">R</p><p>page 12 and page 13</p>')
    pages = [{'page_number': 20, 'page_id': 'left-page', 'spread_side': 'L', 'printed_page_number': 12},
             {'page_number': 20, 'page_id': 'right-page', 'spread_side': 'R', 'printed_page_number': 13}]
    rows = [{'block_id': 'left', 'source_page_number': 20, 'source_page_id': 'left-page', 'source_spread_side': 'L'},
            {'block_id': 'right', 'source_page_number': 20, 'source_page_id': 'right-page', 'source_spread_side': 'R'}]
    report = resolve([item], pages, rows)
    assert {r['resolved_href'] for r in report['references']} == {'#left', '#right'}
    item = entry('<p id="left">L</p><p id="right">R</p><p>page 12 and page 13</p>')
    report = resolve([item], pages, [{'block_id': 'left', 'source_page_number': 20}, {'block_id': 'right', 'source_page_number': 20}])
    assert all(r['resolution_status'] == 'missing' for r in report['references'])


def test_intervening_break_and_image_stay_in_document_order():
    item = entry('<h2 id="n">Section 3</h2><p>See section<br/><img src="icon.png" alt="icon"/> 3.</p>')
    resolve([item])
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    children = list(soup.p.children)
    assert [getattr(n, 'name', None) for n in children] == [None, 'a', 'br', 'img', 'a', None]
    assert children[1].get_text() == 'section'
    assert children[4].get_text() == ' 3'
    assert soup.p.get_text() == 'See section 3.'
    assert not soup.select('a a')


def _unwrapped_topology(html):
    """Independent original-node oracle, ignoring only added link wrappers."""
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.select('[data-doc-web-reference], span.unresolved-reference'):
        tag.unwrap()

    def inspect(tag):
        result = []
        for child in tag.children:
            if type(child) is NavigableString:
                if result and result[-1][0] == 'text':
                    result[-1] = ('text', result[-1][1] + str(child))
                else:
                    result.append(('text', str(child)))
            elif isinstance(child, NavigableString):
                result.append((type(child).__name__, str(child)))
            else:
                result.append((child.name, dict(child.attrs), inspect(child)))
        return result
    return inspect(soup)


@pytest.mark.parametrize('opaque', ['<!-- see section 3 -->', '<?pi see section 3?>', '<![CDATA[see section 3]]>', '<template><p>see section 3</p></template>', '<script>see section 3</script>', '<style>see section 3</style>', '<span hidden>see section 3</span>', '<code>see section 3</code>'])
def test_special_and_excluded_nodes_never_become_editable_or_visible(opaque):
    item = entry('<h2 id="n">Section 3</h2><p>Before' + opaque + 'after; see section 3.</p>')
    original = item['body_html']
    report = resolve([item])
    assert len(report['references']) == 1
    assert _unwrapped_topology(item['body_html']) == _unwrapped_topology(original)
    assert report['references'][0]['original_text'] == 'section 3'


@pytest.mark.parametrize('opaque', ['<!--hidden-->', '<?pi hidden?>', '<![CDATA[hidden]]>', '<code></code>', '<template>hidden</template>'])
def test_special_string_or_exclusion_boundaries_do_not_join_reference_tokens(opaque):
    item = entry('<h2 id="n">Section 3</h2><p>section ' + opaque + '3</p>')
    original = item['body_html']
    report = resolve([item])
    assert _unwrapped_topology(item['body_html']) == _unwrapped_topology(original)
    assert not report['references']
    assert not BeautifulSoup(item['body_html'], 'html.parser').select('code a,template a,a a')


def test_nested_block_ownership_links_parent_and_child_occurrences_exactly_once():
    item = entry('<section class="toc"><ol><li id="parent">Part .... 12<ul><li id="child">Setup .... 13</li></ul>After .... 12</li></ol></section><p id="left">L</p><p id="right">R</p>')
    original = item['body_html']
    report = resolve([item], [{'page_number': 1, 'printed_page_number': 12}, {'page_number': 2, 'printed_page_number': 13}],
                     [{'block_id': 'left', 'source_page_number': 1}, {'block_id': 'right', 'source_page_number': 2}])
    assert len(report['references']) == 3
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert len(soup.select('#child a')) == 1
    assert len(soup.select('#parent > a')) == 2
    assert _unwrapped_topology(item['body_html']) == _unwrapped_topology(original)


@pytest.mark.parametrize('rows, expected', [
    ([{'block_id': 'left', 'source_page_number': 20, 'source_original_page_number': 10}], {}),
    ([{'block_id': 'left', 'source_page_number': 20, 'source_original_page_number': 10, 'source_spread_side': 'L'}], {'page 12': '#left'}),
    ([{'block_id': 'right', 'source_page_number': 20, 'source_printed_page_label': '13'}], {'page 13': '#right'}),
    ([{'block_id': 'left', 'source_page_number': 20, 'source_page_id': 'left-page', 'source_spread_side': 'R'}], {}),
    ([{'block_id': 'left', 'source_page_number': 20, 'source_page_id': 'unknown-page'}], {}),
    ([{'block_id': 'left', 'source_page_number': 20, 'source_page_id': 'left-page', 'source_printed_page_label': '13'}], {}),
])
def test_page_evidence_projection_must_select_exactly_one_complete_raw_identity(rows, expected):
    item = entry('<p id="left">L</p><p id="right">R</p><p>page 12 and page 13</p>')
    pages = [{'page_number': 20, 'original_page_number': 10, 'page_id': 'left-page', 'spread_side': 'L', 'printed_page_number': 12},
             {'page_number': 20, 'original_page_number': 10, 'page_id': 'right-page', 'spread_side': 'R', 'printed_page_number': 13}]
    report = resolve([item], pages, rows)
    assert {r['original_text']: r['resolved_href'] for r in report['references'] if r['resolution_status'] == 'resolved'} == expected


def test_contradictory_single_page_provenance_does_not_fallback_to_matching_html():
    html = '<p id="body">Body</p><p>page 12</p>'
    item = entry(html)
    report = resolve([item], [{'page_number': 1, 'printed_page_number': 12, 'page_id': 'real', 'html': '<p>Body</p>'}],
                     [{'block_id': 'body', 'source_page_number': 1, 'source_page_id': 'different'}])
    assert report['references'][0]['resolution_status'] == 'missing'


def test_conflicting_aliases_for_same_identity_field_abstain():
    item = entry('<p id="body">Body</p><p>page 12</p>')
    report = resolve([item], [{'page_number': 1, 'page_id': 'left', 'printed_page_number': 12}],
                     [{'block_id': 'body', 'source_page_number': 1, 'source_page_id': 'left', 'page_id': 'right'}])
    assert report['references'][0]['resolution_status'] == 'missing'


@pytest.mark.parametrize('prefix', ['A<!--hidden reference 99-->B ', 'A<?pi hidden?>B ', 'A<code></code>B ', 'A<![CDATA[visible prefix]]>B ', '<template>invisible prefix</template>A '])
def test_report_offsets_after_special_nodes_use_original_block_text(prefix):
    item = entry('<h2 id="n">Section 3</h2><p id="ref">' + prefix + 'see section 3.</p>')
    source = BeautifulSoup(item['body_html'], 'html.parser').find(id='ref').get_text()
    report = resolve([item])
    row = report['references'][0]
    loc = row['source']['location']
    assert source[loc['start']:loc['end']] == row['original_text'] == 'section 3'
    assert loc['start'] == source.index('section 3')


def test_nested_block_source_location_is_relative_to_its_id_bearing_ancestor():
    item = entry('<h2 id="n">Section 3</h2><table id="ref"><caption>Prefix</caption><tr><td>See section 3.</td></tr></table>')
    source = BeautifulSoup(item['body_html'], 'html.parser').find(id='ref').get_text()
    report = resolve([item])
    row = report['references'][0]
    loc = row['source']['location']
    assert row['source']['block_id'] == 'ref'
    assert source[loc['start']:loc['end']] == 'section 3'


@pytest.mark.parametrize('container', ['p', 'li', 'td', 'th', 'dt', 'dd', 'figcaption', 'caption', 'ul', 'ol', 'table', 'div', 'section', 'blockquote'])
@pytest.mark.parametrize('content', ['', 'other text'])
def test_structural_boundaries_are_independent_of_descendant_text(container, content):
    opaque = f'<{container}>{content}</{container}>'
    item = entry('<h2 id="n">Section 3</h2><li id="ref">section ' + opaque + '3</li>')
    original = item['body_html']
    assert not resolve([item])['references']
    assert _unwrapped_topology(item['body_html']) == _unwrapped_topology(original)


@pytest.mark.parametrize('container', ['<ul><li></li></ul>', '<table><tr><td></td></tr></table>', '<div></div>'])
def test_empty_structural_containers_preserve_both_toc_occurrences(container):
    item = entry('<section class="toc"><li id="ref">Part .... 12' + container + 'After .... 13</li></section><p id="a">A</p><p id="b">B</p>')
    original = item['body_html']
    report = resolve([item], [{'page_number': 1, 'printed_page_number': 12}, {'page_number': 2, 'printed_page_number': 13}], [{'block_id': 'a', 'source_page_number': 1}, {'block_id': 'b', 'source_page_number': 2}])
    assert {r['resolved_href'] for r in report['references']} == {'#a', '#b'}
    assert len(report['references']) == 2
    text = BeautifulSoup(original, 'html.parser').find(id='ref').get_text()
    for row in report['references']:
        loc = row['source']['location']
        assert text[loc['start']:loc['end']] == row['original_text']
    assert _unwrapped_topology(item['body_html']) == _unwrapped_topology(original)


def test_structural_url_boundary_never_synthesizes_destination():
    item = entry('<li>https://example<table><tr><td></td></tr></table>.org</li>')
    original = item['body_html']
    report = resolve([item])
    assert not any(row['resolution_status'] == 'resolved' for row in report['references'])
    assert not BeautifulSoup(item['body_html'], 'html.parser').find('a')
    assert _unwrapped_topology(item['body_html']) == _unwrapped_topology(original)


def test_nested_source_heading_is_definition_not_parent_reference():
    item = entry('<li><h2 id="n">Section 3</h2></li><p>See section 3.</p>')
    report = resolve([item])
    assert len(report['references']) == 1
    assert not BeautifulSoup(item['body_html'], 'html.parser').select('h2 a')
