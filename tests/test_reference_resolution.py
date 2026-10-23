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


@pytest.mark.parametrize('prose', [
    'As noted above, proceed.', 'The facts are noted.', 'The file was paged.',
    'noted notedi notec notedness notesd section3 chapteriv figure2 table9 paragraph4',
])
def test_spelled_out_reference_kinds_require_word_separators(prose):
    item = entry('<h2 id="d">Footnote D</h2><h2 id="iv">Chapter iv</h2>'
                 '<h2 id="s">Section 3</h2><p id="p">' + prose + '</p>')
    before = item['body_html']
    report = resolve([item])
    assert report['references'] == []
    assert item['body_html'] == before


@pytest.mark.parametrize(('citation', 'heading'), [
    ('note D', 'Footnote D'), ('note <em>IV</em>', 'Footnote IV'),
    ('section 3.2', 'Section 3.2'), ('paragraph 9a', 'Paragraph 9a'),
    ('§3', 'Section 3'), ('¶9', 'Paragraph 9'), ('fig.2', 'Figure 2'),
])
def test_separated_words_and_compact_symbols_or_dotted_abbreviations(citation, heading):
    item = entry('<h2 id="target">' + heading + '</h2><p>See ' + citation + '.</p>')
    before = BeautifulSoup(item['body_html'], 'html.parser').get_text()
    report = resolve([item])
    assert len(report['references']) == 1
    assert report['references'][0]['resolved_href'] == '#target'
    assert BeautifulSoup(item['body_html'], 'html.parser').get_text() == before


@pytest.mark.parametrize('citation', ['p.12', 'pp.12', 'p.iv', 'pp.iv'])
def test_compact_printed_page_abbreviation(citation):
    label = citation.split('.', 1)[1]
    item = entry('<p id="target">Body</p><p>See ' + citation + '.</p>')
    report = resolve([item], [{'page_number': 7, 'printed_page_number_text': label}],
                     [{'block_id': 'target', 'source_page_number': 7}])
    assert report['references'][0]['resolved_href'] == '#target'


@pytest.mark.parametrize('citation', [
    'See section 3 of the separate companion manual.',
    'See section 3 in another document.',
    'See section 3 from a different guide.',
    'In the companion manual, see section 3.',
    'From the external report: refer to section 3.',
    "See the other book’s section 3.",
    "See the separate volume's section 3.",
    'See section <em>3</em> of the <strong>separate companion manual</strong>.',
])
def test_explicit_attached_other_document_scope_never_selects_local_target(citation):
    item = entry('<h2 id="target">Section 3 Local</h2><p id="p">' + citation + '</p>')
    before = BeautifulSoup(item['body_html'], 'html.parser').get_text()
    report = resolve([item])
    assert len(report['references']) == 1
    row = report['references'][0]
    assert row['resolution_status'] == 'missing'
    assert row['reason'] == 'external_document_scope'
    assert row['target'] is None
    assert row['candidates'][0]['id'] == 'target'
    assert 'resolved_href' not in row
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert soup.get_text() == before
    assert not soup.select('p a')
    after = item['body_html']
    resolve([item])
    assert item['body_html'] == after


def test_external_scope_attaches_to_one_occurrence_and_leaves_other_local_references():
    item = entry('<h2 id="target">Section 3 Local</h2><p id="p">'
                 'See section 3 of the companion manual; see section 3 here. '
                 'The separate manual is unavailable. See section 3. '
                 'See section 3 in this manual.</p>')
    report = resolve([item])
    rows = sorted(report['references'], key=lambda r: r['source']['location']['start'])
    assert [r['reason'] for r in rows] == ['external_document_scope'] + ['unique_exact_source_target'] * 3
    assert len(BeautifulSoup(item['body_html'], 'html.parser').select('p a')) == 3


def test_other_document_scope_does_not_cross_excluded_inline_barrier():
    item = entry('<h2 id="target">Section 3</h2><p>See section 3 '
                 '<code>in another manual</code>; see section 3.</p>')
    report = resolve([item])
    assert all(row['resolution_status'] == 'resolved' for row in report['references'])


@pytest.mark.parametrize(('label', 'cue'), [
    ('R123', 'See '), ('APP7', 'refer to '), ('Q42', 'turn to '),
    ('Appendix123', 'Consult '), ('Ref12.3b', 'Read '),
])
def test_plain_prefixed_reference_uses_literal_source_heading_with_generic_cue(label, cue):
    src = entry('<p id="ref">' + cue + '<em>' + label + '</em>.</p>')
    dst = entry('<h2 id="target">' + label + ' Target</h2>', 'other.html')
    before = BeautifulSoup(src['body_html'], 'html.parser').get_text()
    report = resolve([src, dst])
    assert len(report['references']) == 1
    row = report['references'][0]
    assert row['original_text'] == label
    assert row['resolved_href'] == 'other.html#target'
    assert row['target']['evidence']['source_text'] == label + ' Target'
    soup = BeautifulSoup(src['body_html'], 'html.parser')
    assert soup.get_text() == before
    assert soup.em.get_text() == label
    first = src['body_html']
    resolve([src, dst])
    assert src['body_html'] == first


def test_prefixed_case_is_normalized_without_stripping_or_partial_token_matching():
    item = entry('<h2 id="target">R123 Target</h2><p>See r123. See 123. '
                 'See R123xyz. See xR123. See R123.4. See R123_filename.</p>')
    report = resolve([item])
    assert len(report['references']) == 1
    assert report['references'][0]['original_text'] == 'r123'
    assert report['references'][0]['resolved_href'] == '#target'


def test_prefixed_missing_generated_or_duplicate_heading_authority():
    item = entry('<p id="ref">See R123; See APP7; See Q42.</p>'
                 '<h2 id="a">APP7 Target</h2><h2 id="b">APP7 Alternative</h2>')
    item['body_html'] += '<h2 id="invented">Q42 Invented</h2>'
    report = resolve([item])
    assert len(report['references']) == 1
    assert report['references'][0]['original_text'] == 'APP7'
    assert report['references'][0]['resolution_status'] == 'ambiguous'
    assert not BeautifulSoup(item['body_html'], 'html.parser').select('p a')


def test_arbitrary_prefixed_code_prose_and_excluded_regions_are_not_citations():
    item = entry('<h2 id="r">R123 Target</h2><p>Product R123 is available; '
                 'the variable R123 is assigned.</p><pre>See R123</pre>'
                 '<p><code>See R123</code></p>')
    before = item['body_html']
    assert resolve([item])['references'] == []
    assert item['body_html'] == before


@pytest.mark.parametrize('citation', ['(Q42)', '[Q42]'])
def test_parenthesized_or_bracketed_prefixed_reference(citation):
    item = entry('<h2 id="target">Q42 Target</h2><p>Details ' + citation + '.</p>')
    report = resolve([item])
    assert report['references'][0]['resolved_href'] == '#target'
    assert BeautifulSoup(item['body_html'], 'html.parser').p.get_text() == 'Details ' + citation + '.'


@pytest.mark.parametrize('title', ['Rules & Tables Index', 'Reference Contents', 'Table of Contents'])
def test_source_authored_index_or_contents_accepts_prefixed_heading_labels(title):
    item = entry('<h2>' + title + '</h2><table><tr><td>Q42</td><td>Repair</td>'
                 '</tr><tr><td>APP7</td><td>Unknown</td></tr></table>'
                 '<h2 id="target">Q42 Repair</h2>')
    report = resolve([item])
    assert len(report['references']) == 1
    assert report['references'][0]['resolved_href'] == '#target'


def test_prefixed_reference_scope_abstains_per_occurrence():
    item = entry('<h2 id="target">Q42 Target</h2><p>See Q42 of the companion manual; '
                 'in the separate document, see Q42; see Q42.</p>')
    rows = sorted(resolve([item])['references'], key=lambda r: r['source']['location']['start'])
    assert [row['reason'] for row in rows] == ['external_document_scope', 'external_document_scope', 'unique_exact_source_target']


@pytest.mark.parametrize('citation', ['See Q42–Q45.', 'Details (Q42-Q45).', 'Details [Q42–Q45].'])
def test_prefixed_ranges_abstain_without_guessing_first_target(citation):
    item = entry('<h2 id="target">Q42 Target</h2><p>' + citation + '</p>')
    report = resolve([item])
    assert len(report['references']) == 1
    assert report['references'][0]['reason'] == 'unsupported_range'
    assert report['references'][0]['resolution_status'] == 'ambiguous'
    assert not BeautifulSoup(item['body_html'], 'html.parser').select('p a')


@pytest.mark.parametrize('citation', [
    'See (Q42) in the companion manual.', 'Details [Q42] of another document.',
    'In the separate manual, see (Q42).', 'In the other guide: [Q42].',
])
def test_attached_scope_for_delimited_prefixed_citation(citation):
    item = entry('<h2 id="target">Q42 Target</h2><p>' + citation + '</p>')
    report = resolve([item])
    assert len(report['references']) == 1
    assert report['references'][0]['reason'] == 'external_document_scope'
    assert report['references'][0]['target'] is None


@pytest.mark.parametrize('description', [
    'installation', 'maintenance', 'technical', 'setup', 'reference',
    'advanced installation reference', 'quick-start technical',
])
@pytest.mark.parametrize('position', ['prefix', 'suffix'])
def test_foreign_document_noun_phrase_allows_bounded_generic_descriptors(description, position):
    foreign = 'the other ' + description + ' guide'
    citation = ('In ' + foreign + ', see (section <em>3</em>).' if position == 'prefix'
                else 'See (section <em>3</em>) of ' + foreign + '.')
    item = entry('<h2 id="target">Section 3 Local</h2><p id="ref">' + citation +
                 ' See section 3 here.</p>')
    before = BeautifulSoup(item['body_html'], 'html.parser').get_text()
    rows = sorted(resolve([item])['references'], key=lambda r: r['source']['location']['start'])
    assert [r['reason'] for r in rows] == ['external_document_scope', 'unique_exact_source_target']
    assert rows[0]['target'] is None
    assert rows[1]['resolved_href'] == '#target'
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert soup.get_text() == before
    assert soup.em.get_text() == '3'
    assert len(soup.select('p a')) == 1


@pytest.mark.parametrize('prose', [
    'Another option; in this technical guide, see section 3.',
    'Other setup choices and this guide: see section 3.',
    'A different setup is here. In this guide, see section 3.',
    'Read the other technical guide; see section 3 here.',
    'See section 3 for another installation guide.',
])
def test_foreign_descriptor_scope_cannot_absorb_a_separate_local_clause(prose):
    item = entry('<h2 id="target">Section 3 Local</h2><p>' + prose + '</p>')
    rows = resolve([item])['references']
    assert len(rows) == 1
    assert rows[0]['resolved_href'] == '#target'


def test_foreign_descriptors_and_scope_qualifier_across_inline_markup():
    item = entry('<h2 id="target">Section 3 Local</h2><p>In the <strong>other '
                 'maintenance</strong> <em>reference guide</em>, see section 3. '
                 'See section 3 of the separate <em>technical setup manual</em>.</p>')
    before = BeautifulSoup(item['body_html'], 'html.parser').get_text()
    rows = resolve([item])['references']
    assert len(rows) == 2
    assert all(row['reason'] == 'external_document_scope' for row in rows)
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert soup.get_text() == before
    assert soup.strong.get_text() == 'other maintenance'
    assert not soup.select('p a')


@pytest.mark.parametrize('citation', [
    'See section 3 and section 4 of the companion manual.',
    'In the companion manual, see section 3 and section 4.',
    'See section 3, section 4, and section 5 in another reference guide.',
    'In the other technical manual, see section 3, section 4 or section 5.',
    'See (section 3) and (section <em>4</em>) of the companion manual.',
])
def test_bounded_explicit_coordinated_references_share_foreign_document_scope(citation):
    item = entry('<h2 id="a">Section 3 Local</h2><h2 id="b">Section 4 Local</h2>'
                 '<h2 id="c">Section 5 Local</h2><p>' + citation + '</p>')
    before = BeautifulSoup(item['body_html'], 'html.parser').get_text()
    rows = resolve([item])['references']
    assert len(rows) >= 2
    assert all(row['reason'] == 'external_document_scope' for row in rows)
    assert all(row['target'] is None for row in rows)
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert soup.get_text() == before
    assert not soup.select('p a')


@pytest.mark.parametrize('citation', [
    'See section 3 of the companion manual; see section 4 in this manual.',
    'In the companion manual, see section 3. See section 4.',
    'See section 3 of the other setup guide, and here see section 4.',
])
def test_scope_coordination_cannot_absorb_separate_local_reference(citation):
    item = entry('<h2 id="a">Section 3 Local</h2><h2 id="b">Section 4 Local</h2>'
                 '<p id="p">' + citation + '</p>')
    rows = sorted(resolve([item])['references'], key=lambda r: r['source']['location']['start'])
    assert [row['reason'] for row in rows] == ['external_document_scope', 'unique_exact_source_target']
    assert rows[1]['resolved_href'] == '#b'


def test_coordinated_prefixed_references_share_only_attached_external_scope():
    item = entry('<h2 id="a">Q42 Local</h2><h2 id="b">APP7 Local</h2><p>'
                 'See (Q42) and [APP7] in the companion guide; see Q42 here.</p>')
    rows = sorted(resolve([item])['references'], key=lambda r: r['source']['location']['start'])
    assert [row['reason'] for row in rows] == ['external_document_scope', 'external_document_scope', 'unique_exact_source_target']


def test_long_explicit_coordination_has_no_silently_local_tail():
    labels = list(range(1, 10))
    headings = ''.join('<h2 id="s' + str(n) + '">Section ' + str(n) + '</h2>' for n in labels)
    refs = ', '.join('section ' + str(n) for n in labels)
    item = entry(headings + '<p>See ' + refs + ' of the companion manual.</p>')
    rows = resolve([item])['references']
    assert len(rows) == len(labels)
    assert all(row['reason'] == 'external_document_scope' for row in rows)
    assert not BeautifulSoup(item['body_html'], 'html.parser').select('p a')


@pytest.mark.parametrize('tail', ['and 4', 'or 4', ', 4 and 5', ', 4, 5, 6, 7, 8, 9 and 10', 'and 4.2', 'and IV'])
@pytest.mark.parametrize('position', ['prefix', 'suffix'])
def test_shared_kind_numeric_list_retains_attached_foreign_scope(tail, position):
    phrase = 'sections 3 ' + tail
    prose = ('In the companion manual, see ' + phrase + '.' if position == 'prefix'
             else 'See ' + phrase + ' of the companion manual.')
    item = entry('<h2 id="target">Section 3 Local</h2><p id="p">' + prose + '</p>')
    before = BeautifulSoup(item['body_html'], 'html.parser').get_text()
    rows = resolve([item])['references']
    assert len(rows) == 1  # Scope-binding support does not invent bare-tail links.
    assert rows[0]['reason'] == 'external_document_scope'
    assert rows[0]['target'] is None
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert soup.get_text() == before
    assert not soup.select('p a')


@pytest.mark.parametrize('prose', [
    'See sections 3 and 4 here; see sections 3 and 4 of the companion manual.',
    'See sections 3, 4 and 5 in this manual. In the other setup guide, see sections 3, 4 and 5.',
    'See sections 3 or 4 here; see sections 3 or 4 from another manual.',
])
def test_mixed_local_foreign_shared_kind_lists_use_occurrence_scope(prose):
    item = entry('<h2 id="target">Section 3 Local</h2><p id="p">' + prose + '</p>')
    rows = sorted(resolve([item])['references'], key=lambda r: r['source']['location']['start'])
    assert [row['reason'] for row in rows] == ['unique_exact_source_target', 'external_document_scope']
    assert rows[0]['resolved_href'] == '#target'
    assert rows[1]['target'] is None


@pytest.mark.parametrize('prose', [
    'See section 3 and 4. Read the companion manual.',
    'See section 3 and 4. Of the companion manual, nothing is known.',
    'See section 3 and 4XYZ of the companion manual.',
    'See section 3 and 4_filename of the companion manual.',
    'See section 3 and 4.description of the companion manual.',
    'See section 3 and 4 are measurements in the companion manual.',
])
def test_shared_kind_scope_does_not_swallow_word_identity_sentence_or_prose_boundaries(prose):
    item = entry('<h2 id="target">Section 3 Local</h2><p>' + prose + '</p>')
    rows = resolve([item])['references']
    assert len(rows) == 1
    assert rows[0]['resolved_href'] == '#target'


def test_ordinary_numeric_prose_never_seeds_shared_kind_scope_or_links():
    item = entry('<h2 id="a">Section 3 Local</h2><h2 id="b">Section 4 Local</h2>'
                 '<p>There are 3 and 4 of the companion manual. Use 3, 4 and 5 here.</p>')
    before = item['body_html']
    assert resolve([item])['references'] == []
    assert item['body_html'] == before


def test_explicit_shared_kind_list_survives_inline_markup():
    item = entry('<h2 id="target">Section 3 Local</h2><p>See sections <em>3</em>, '
                 '<strong>4 and 5</strong> of the companion manual.</p>')
    report = resolve([item])
    assert report['references'][0]['reason'] == 'external_document_scope'
    soup = BeautifulSoup(item['body_html'], 'html.parser')
    assert soup.em.get_text() == '3'
    assert soup.strong.get_text() == '4 and 5'
    assert not soup.select('p a')


def test_generated_final_index_heading_does_not_authorize_prefixed_prose_discovery():
    source = '<h2>Maintenance</h2><p>Product Q42 is assigned.</p><h2 id="target">Q42 Target</h2>'
    item = entry(source)
    item['body_html'] = source.replace('<h2>Maintenance</h2>', '<h2>Rules Index</h2>')
    before = item['body_html']
    assert resolve([item])['references'] == []
    assert item['body_html'] == before


def test_generated_final_index_class_does_not_authorize_prefixed_prose_discovery():
    source = '<section><p>Product Q42 is assigned.</p></section><h2 id="target">Q42 Target</h2>'
    item = entry(source)
    item['body_html'] = source.replace('<section>', '<section class="index">')
    assert resolve([item])['references'] == []
    assert not BeautifulSoup(item['body_html'], 'html.parser').select('p a')


def test_duplicate_source_text_in_index_and_ordinary_prose_cannot_share_index_authority():
    source = ('<h2>Rules Index</h2><p>Q42</p><h2>Maintenance</h2><p>Q42</p>'
              '<h2 id="target">Q42 Target</h2>')
    item = entry(source)
    assert resolve([item])['references'] == []
    assert not BeautifulSoup(item['body_html'], 'html.parser').select('p a')


def test_repeated_source_index_cells_with_same_context_retain_authority():
    item = entry('<h2>Rules Index</h2><table><tr><td>Q42</td><td>Q42</td></tr>'
                 '</table><h2 id="target">Q42 Target</h2>')
    rows = resolve([item])['references']
    assert len(rows) == 2
    assert all(row['resolved_href'] == '#target' for row in rows)


def test_generated_index_context_cannot_authorize_bare_page_discovery_either():
    source = '<h2>Maintenance</h2><p>Measured length 12</p><p id="target">Page body</p>'
    item = entry(source)
    item['body_html'] = source.replace('<h2>Maintenance</h2>', '<h2>Rules Index</h2>')
    rows = resolve([item], [{'page_number': 7, 'printed_page_number': 12}],
                   [{'block_id': 'target', 'source_page_number': 7}])['references']
    assert rows == []


def test_precomputed_scope_context_matches_per_occurrence_compatibility_helper():
    import re
    from doc_web.reference_resolution import ReferenceScope, reference_scope_reason
    text = ('See sections 3, 4 and 5 of the companion manual; see section 3 here. '
            'In another setup guide, see section 3 and section 4. See Q42 here.')
    scope = ReferenceScope(text)
    spans = [match.span() for match in re.finditer(r'sections? \d|Q42', text)]
    assert [scope.reason(*span) for span in spans] == [reference_scope_reason(text, *span) for span in spans]
    assert [scope.reason(*span) for span in spans] == ['external_document_scope', None, 'external_document_scope', 'external_document_scope', None]


def test_precomputed_scope_context_is_isolated_and_handles_anchor_navigation_cue():
    from doc_web.reference_resolution import ReferenceScope
    foreign = 'See sections 3 and 4 of another guide.'
    local = 'See sections 3 and 4 here.'
    assert ReferenceScope(foreign).reason(0, len('See sections 3')) == 'external_document_scope'
    assert ReferenceScope(local).reason(0, len('See sections 3')) is None
    assert ReferenceScope(foreign).reason(foreign.index('guide'), len(foreign)) is None


@pytest.mark.parametrize('tail', ['and 4–5', ', 4–5 and 6', ', 4–5, 6–8 or 9', 'or IV–VI'])
@pytest.mark.parametrize('position', ['prefix', 'suffix'])
def test_shared_kind_scope_list_retains_bare_ranges_without_guessing_endpoints(tail, position):
    phrase = 'sections 3 ' + tail
    prose = ('In the companion manual, see ' + phrase + '.' if position == 'prefix'
             else 'See ' + phrase + ' of the companion manual.')
    item = entry('<h2 id="target">Section 3 Local</h2><p>' + prose + '</p>')
    rows = resolve([item])['references']
    assert len(rows) == 1
    assert rows[0]['reason'] == 'external_document_scope'
    assert rows[0]['target'] is None
    assert not BeautifulSoup(item['body_html'], 'html.parser').select('p a')


def test_bare_range_scope_lists_are_per_occurrence_and_do_not_seed_prose_links():
    item = entry('<h2 id="target">Section 3 Local</h2><p id="p">'
                 'See sections 3 and 4–5 here; see sections 3 and 4–5 of the companion manual. '
                 'There are 3 and 4–5 of another guide.</p>')
    rows = sorted(resolve([item])['references'], key=lambda row: row['source']['location']['start'])
    assert [row['reason'] for row in rows] == ['unique_exact_source_target', 'external_document_scope']


def test_interstitial_scope_preserves_disjoint_foreign_local_and_barrier_boundaries():
    from doc_web.reference_resolution import ReferenceScope
    text = ('In the companion manual, see section 1. See section 2 here. '
            'See section 3 of another guide. See section 4\x00 of the other manual. '
            'In another guide\x00 see section 5. See section 6 in this manual.')
    import re
    scope = ReferenceScope(text)
    spans = [match.span() for match in re.finditer(r'section \d', text)]
    assert [scope.reason(*span) for span in spans] == ['external_document_scope', None, 'external_document_scope', None, None, None]


def test_generated_heading_promotion_of_product_prose_does_not_define_prefixed_target():
    source = '<p id="body">Q42 Product model</p><p>See Q42.</p>'
    item = entry(source)
    item['body_html'] = source.replace('<p id="body">Q42 Product model</p>', '<h2 id="body">Q42 Product model</h2>')
    assert resolve([item])['references'] == []
    assert not BeautifulSoup(item['body_html'], 'html.parser').select('p a')


def test_authored_prefixed_heading_without_source_id_still_authorizes_final_unique_target():
    source = '<h2>Q42 Product model</h2><p>See Q42.</p>'
    item = entry(source)
    item['body_html'] = source.replace('<h2>', '<h2 id="final">')
    rows = resolve([item])['references']
    assert rows[0]['resolved_href'] == '#final'


def test_existing_numeric_heading_reconstruction_contract_is_preserved():
    source = '<p id="body">42 Repairs</p><p>See section 42.</p>'
    item = entry(source)
    item['body_html'] = source.replace('<p id="body">42 Repairs</p>', '<h2 id="body">42 Repairs</h2>')
    assert resolve([item])['references'][0]['resolved_href'] == '#body'


@pytest.mark.parametrize('document', ['the installation guide', 'a maintenance manual', 'the technical reference volume', 'the report', 'our setup book', 'Installation Guide'])
@pytest.mark.parametrize('qualifier', ['According to', 'In', 'From'])
def test_descriptive_document_source_prefix_has_unestablished_scope(document, qualifier):
    item = entry('<h2 id="target">Section 3 Local</h2><p id="p">' + qualifier + ' ' + document + ', see section <em>3</em>.</p>')
    rows = resolve([item])['references']
    assert len(rows) == 1
    assert rows[0]['reason'] == 'unestablished_document_scope'
    assert rows[0]['target'] is None
    assert not BeautifulSoup(item['body_html'], 'html.parser').select('p a')


@pytest.mark.parametrize('document', ['this manual', 'the current installation guide', 'this reference book', 'the present document'])
def test_demonstrative_document_source_prefix_retains_explicit_local_scope(document):
    item = entry('<h2 id="target">Section 3 Local</h2><p>According to ' + document + ', see section 3.</p>')
    assert resolve([item])['references'][0]['resolved_href'] == '#target'


@pytest.mark.parametrize('prose', [
    'According to the installation guide, see section 3; see section 3 here.',
    'According to the installation guide, see sections 3 and 4. See section 3 in this manual.',
])
def test_unestablished_document_source_scope_remains_per_occurrence(prose):
    item = entry('<h2 id="target">Section 3 Local</h2><p id="p">' + prose + '</p>')
    rows = sorted(resolve([item])['references'], key=lambda row: row['source']['location']['start'])
    assert [row['reason'] for row in rows] == ['unestablished_document_scope', 'unique_exact_source_target']


def test_document_source_prefix_does_not_leak_across_prose_sentence_or_code_barriers():
    item = entry('<h2 id="target">Section 3 Local</h2><p>According to the installation guide, '
                 'work is complete. See section 3. In <code>the installation guide,</code> see section 3.</p>')
    rows = resolve([item])['references']
    assert len(rows) == 2
    assert all(row['resolved_href'] == '#target' for row in rows)


def test_according_to_explicit_foreign_document_retains_stronger_scope_reason():
    item = entry('<h2 id="target">Section 3 Local</h2><p>According to the companion manual, see section 3.</p>')
    assert resolve([item])['references'][0]['reason'] == 'external_document_scope'


@pytest.mark.parametrize('enabled', [False, True])
def test_existing_anchor_fallback_uses_unestablished_document_source_scope(enabled):
    item = entry('<h2 id="target">Section 3 Local</h2><p>According to the technical reference volume, '
                 'see <a href="#missing">section 3</a>.</p>')
    report = resolve_navigation([item], resolve_references=enabled)
    assert report['references'][0]['reason'] == 'unestablished_document_scope'
    assert report['references'][0]['target'] is None
    assert not BeautifulSoup(item['body_html'], 'html.parser').select('p a')


@pytest.mark.parametrize('prose', ['See Q42 and APP7.', 'Refer to Q42, APP7 and REF9.', 'Consult (Q42) or [APP7].'])
def test_shared_navigation_cue_discovers_exact_coordinated_prefixed_labels(prose):
    item = entry('<h2 id="a">Q42 Target</h2><h2 id="b">APP7 Target</h2><h2 id="c">REF9 Target</h2><p>' + prose + '</p>')
    rows = resolve([item])['references']
    expected = {'Q42': '#a', 'APP7': '#b'}
    if 'REF9' in prose:
        expected['REF9'] = '#c'
    assert {row['original_text']: row['resolved_href'] for row in rows} == expected


def test_shared_prefixed_list_gates_each_source_heading_and_abstains_duplicates_ranges():
    source = ('<h2 id="a">Q42 Target</h2><h2 id="b">APP7 Target</h2><h2 id="c">APP7 Alternative</h2>'
              '<p id="fake">REF9 Product</p><p>See Q42 and APP7, REF9 or Q42–Q45.</p>')
    item = entry(source)
    item['body_html'] = source.replace('<p id="fake">REF9 Product</p>', '<h2 id="fake">REF9 Product</h2>')
    rows = sorted(resolve([item])['references'], key=lambda row: row['source']['location']['start'])
    assert [row['original_text'] for row in rows] == ['Q42', 'APP7', 'Q42–Q45']
    assert [row['resolution_status'] for row in rows] == ['resolved', 'ambiguous', 'ambiguous']


def test_prefixed_cue_does_not_extend_through_ordinary_prose_or_sentence_boundaries():
    item = entry('<h2 id="a">Q42 Target</h2><h2 id="b">APP7 Target</h2><p>See Q42. '
                 'Product APP7 is assigned. See Q42 and the product APP7. See Q42 '
                 '<code>and</code> APP7.</p>')
    rows = resolve([item])['references']
    assert len(rows) == 3
    assert all(row['original_text'] == 'Q42' for row in rows)


def test_parenthesized_prefixed_tokens_inside_code_shaped_words_do_not_become_citations():
    item = entry('<h2 id="target">Q42 Target</h2><p>Product(Q42) is assigned; array[Q42] is set.</p>')
    assert resolve([item])['references'] == []
