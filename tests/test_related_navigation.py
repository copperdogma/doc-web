"""Declared-set symbol resolution: evidence, ambiguity and text preservation."""
from copy import deepcopy

import pytest
from bs4 import BeautifulSoup

from doc_web.related_navigation import resolve_related_entries


def member(member_id, html, *, edition=None, path='chapter.html', rows=None):
    soup = BeautifulSoup(html, 'html.parser')
    if rows is None:
        rows = [{'entry_id': 'chapter', 'block_id': tag['id'],
                 'block_kind': 'heading' if tag.name.startswith('h') else 'paragraph',
                 'text_quote': ' '.join(tag.get_text().split())[:400],
                 'source_element_ids': [f'element-{tag["id"]}'], 'source_page_number': 1}
                for tag in soup.find_all(id=True)]
    return {'member_id': member_id, 'document_id': f'document-{member_id}',
            'edition': edition, 'entries': [{'entry_id': 'chapter',
                'filename': f'{member_id}/{path}', 'body_html': html}],
            'provenance_rows': rows}


def html(item):
    return item['entries'][0]['body_html']


def refs(report):
    return {r['original_text']: r for r in report['references']}


@pytest.mark.parametrize('label', ['x203', 'q71b', 'MAP12', 'ab9.2c', 'k880a', 'zz1001'])
def test_arbitrary_exact_bare_identifiers_are_authorized(label):
    src = member('source', f'<p id="p">Equipment {label} applies.</p>')
    dst = member('target', f'<h2 id="h">{label} Equipment</h2>')
    report = resolve_related_entries([src, dst])
    row = report['references'][0]
    assert row['status'] == 'resolved'
    assert row['label'] == label
    assert row['target']['href'] == '../target/chapter.html#h'
    assert row['target']['evidence']['provenance']['source_element_ids'] == ['element-h']
    assert row['source']['location'] == {'start': 10, 'end': 10 + len(label)}
    assert report['api_calls'] == report['cost_usd'] == 0


@pytest.mark.parametrize('heading', ['Hazards (x203e)', 'Hazards (x203e):', 'x203e: Hazards'])
def test_leading_and_terminal_parenthesized_identifiers(heading):
    src = member('a', '<p id="p">x203e</p>')
    dst = member('b', f'<h2 id="h">{heading}</h2>')
    report = resolve_related_entries([src, dst])
    assert report['references'][0]['status'] == 'resolved'
    assert report['targets'][0]['heading'] == heading


def test_inline_fragments_case_and_quoted_uri_preserve_content_and_ids():
    src = member('a', '<p id="p">See <em id="inline">X2<strong>03e</strong></em>, section <b>2</b> and page 2.</p>')
    dst = member('b', '<h2 id="h space">x203e: Hazards</h2><h3 id="s">Section 2 Paths</h3>', path='chapter space.html')
    before = BeautifulSoup(html(src), 'html.parser')
    snapshot = deepcopy([src['provenance_rows'], dst['provenance_rows']])
    report = resolve_related_entries([src, dst])
    after = BeautifulSoup(html(src), 'html.parser')
    assert after.get_text() == before.get_text()
    assert _ids(after) == _ids(before)
    assert after.em.strong.get_text() == '03e'
    assert not after.select('a a')
    assert {a['href'] for a in after.find_all('a')} == {'../b/chapter%20space.html#h%20space', '../b/chapter%20space.html#s'}
    assert refs(report)['page 2']['reason'] == 'unsupported_page_scope'
    assert [src['provenance_rows'], dst['provenance_rows']] == snapshot


def _ids(soup):
    return sorted(tag['id'] for tag in soup.find_all(id=True))


@pytest.mark.parametrize('heading,reference', [
    ('Chapter IV Paths', 'chapter iv'), ('Section 2a Paths', 'section 2a'),
    ('Paragraph 9 Paths', 'paragraph 9'), ('Figure 3 Paths', 'Figure 3'),
    ('Section q71b Paths', 'q71b'), ('Section q71b Paths', 'section q71b')])
def test_typed_headings_and_labels(heading, reference):
    src = member('a', f'<p id="p">Read {reference}.</p>')
    dst = member('b', f'<h2 id="h">{heading}</h2>')
    report = resolve_related_entries([src, dst])
    assert report['references'][0]['status'] == 'resolved'


def test_same_label_never_prefers_local_member_or_first_document():
    src = member('a', '<h2 id="h">x203 Paths</h2><p id="p">x203</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2>')
    for order in ([src, dst], [dst, src]):
        report = resolve_related_entries(order)
        assert report['references'][0]['status'] == 'ambiguous'
        assert report['references'][0]['reason'] == 'duplicate_exact_targets'
        assert len(report['references'][0]['candidates']) == 2
    assert '<a' not in html(src)


@pytest.mark.parametrize('defect,reason', [
    ('missing_id', 'missing_heading_dom_id'),
    ('duplicate_id', 'duplicate_heading_dom_id'),
    ('missing_row', 'missing_heading_provenance'),
    ('duplicate_row', 'duplicate_heading_provenance'),
    ('wrong_quote', 'heading_quote_mismatch'),
    ('empty_elements', 'missing_heading_element_ids'),
    ('wrong_kind', 'non_heading_provenance')])
def test_rejected_headings_remain_inspectable_and_never_link(defect, reason):
    src = member('a', '<p id="p">x203</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2>')
    if defect == 'missing_id':
        dst['entries'][0]['body_html'] = '<h2>x203 Paths</h2>'
    elif defect == 'duplicate_id':
        dst['entries'][0]['body_html'] += '<p id="h">Unrelated text</p>'
    elif defect == 'missing_row':
        dst['provenance_rows'] = []
    elif defect == 'duplicate_row':
        dst['provenance_rows'] *= 2
    elif defect == 'wrong_quote':
        dst['provenance_rows'][0]['text_quote'] = 'x203 Different'
    elif defect == 'empty_elements':
        dst['provenance_rows'][0]['source_element_ids'] = []
    elif defect == 'wrong_kind':
        dst['provenance_rows'][0]['block_kind'] = 'paragraph'
    report = resolve_related_entries([src, dst])
    assert report['targets'][0]['rejection_reason'] == reason
    assert report['references'][0]['reason'] == reason
    assert report['references'][0]['status'] == 'missing'
    assert '<a' not in html(src)


def test_invalid_duplicate_heading_blocks_otherwise_valid_target():
    src = member('a', '<p id="p">x203</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2><h2 id="bad">x203 Missing evidence</h2>')
    dst['provenance_rows'].pop()
    report = resolve_related_entries([src, dst])
    assert len(report['targets']) == 2
    assert report['references'][0]['status'] == 'ambiguous'
    assert '<a' not in html(src)


@pytest.mark.parametrize('defect,reason', [
    ('missing_row', 'missing_source_provenance'),
    ('duplicate_row', 'duplicate_source_provenance'),
    ('wrong_quote', 'source_quote_mismatch'),
    ('empty_elements', 'missing_source_element_ids'),
    ('wrong_entry', 'missing_source_provenance'),
    ('duplicate_id', 'duplicate_source_dom_id'),
    ('missing_id', 'missing_source_block_id')])
def test_source_requires_unique_complete_matching_evidence(defect, reason):
    src = member('a', '<p id="p">See x203.</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2>')
    if defect == 'missing_row':
        src['provenance_rows'] = []
    elif defect == 'duplicate_row':
        src['provenance_rows'] *= 2
    elif defect == 'wrong_quote':
        src['provenance_rows'][0]['text_quote'] = 'x203'
    elif defect == 'empty_elements':
        src['provenance_rows'][0]['source_element_ids'] = []
    elif defect == 'wrong_entry':
        src['provenance_rows'][0]['entry_id'] = 'another-entry'
    elif defect == 'duplicate_id':
        src['entries'][0]['body_html'] += '<p id="p">Unrelated</p>'
    elif defect == 'missing_id':
        src['entries'][0]['body_html'] = '<p>See x203.</p>'
    report = resolve_related_entries([src, dst])
    assert report['references'][0]['reason'] == reason
    assert '<a' not in html(src)


def test_missing_code_occurrence_is_reported_without_target():
    src = member('a', '<p id="p">x999z is absent.</p>')
    report = resolve_related_entries([src])
    assert report['references'][0]['label'] == 'x999z'
    assert report['references'][0]['reason'] == 'exact_target_unavailable'
    assert report['references'][0]['candidates'] == []
    assert report['references'][0]['target'] is None


@pytest.mark.parametrize('reference', ['x203–x204', 'section 2–3', 'x203-204'])
def test_ranges_are_never_partially_linked(reference):
    src = member('a', f'<p id="p">{reference}</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2><h2 id="h2">Section 2 Paths</h2>')
    report = resolve_related_entries([src, dst])
    assert len(report['references']) == 1
    assert report['references'][0]['reason'] == 'unsupported_range'
    assert '<a' not in html(src)


def test_excluded_text_and_heading_definitions_are_not_citations():
    src = member('a', '<h2 id="h">x203 Paths</h2><pre>x203</pre><code>x203</code><script>x203</script>'
                 '<nav class="toc"><p>x203</p></nav><p hidden>x203</p>'
                 '<p id="p">Hidden <span aria-hidden="true">x203</span> '
                 '<span data-doc-web-generated="true">x203</span> '
                 '<span style="display:none">x203</span> https://example.org/x203</p>')
    report = resolve_related_entries([src])
    assert report['references'] == []
    assert '<a' not in html(src)


@pytest.mark.parametrize('reference', ['x203 in the companion manual',
                                      'in the Equipment Manual, x203',
                                      'the other book: x203',
                                      'section 2 of the companion guide'])
def test_explicit_external_or_named_document_scopes_abstain(reference):
    src = member('a', f'<p id="p">{reference}</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2><h2 id="h2">Section 2 Paths</h2>')
    report = resolve_related_entries([src, dst])
    assert report['references'][0]['reason'] in {'external_document_scope', 'unestablished_document_scope'}
    assert '<a' not in html(src)


def test_existing_anchors_are_opaque_and_local_href_is_unchanged():
    src = member('a', '<p id="p"><a id="old" href="#h"><em>x203</em></a>; x204</p><h2 id="h">x203 Paths</h2>')
    dst = member('b', '<h2 id="h2">x204 Paths</h2>')
    report = resolve_related_entries([src, dst])
    assert len(report['references']) == 1
    soup = BeautifulSoup(html(src), 'html.parser')
    assert soup.find(id='old')['href'] == '#h'
    assert soup.find(id='old').em.get_text() == 'x203'
    assert not soup.select('a a')


def test_old_local_unresolved_spans_can_resolve_with_new_set_scope():
    src = member('a', '<p id="p">See <span id="inline" class="unresolved-reference other" data-doc-web-navigation-status="missing">x203</span>.</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2>')
    report = resolve_related_entries([src, dst])
    assert report['references'][0]['status'] == 'resolved'
    soup = BeautifulSoup(html(src), 'html.parser')
    assert soup.find(id='inline')['class'] == ['other']
    assert not soup.find(id='inline').has_attr('data-doc-web-navigation-status')
    assert soup.a.get_text() == 'x203'


def test_edition_conflict_holds_cross_member_but_not_unique_local_links():
    src = member('a', '<h2 id="h">x203 Paths</h2><p id="p">x203 and x204</p>', edition=' First ')
    dst = member('b', '<h2 id="h2">x204 Paths</h2>', edition='second')
    report = resolve_related_entries([src, dst])
    assert report['policy']['edition_conflict'] is True
    assert refs(report)['x203']['status'] == 'resolved'
    assert refs(report)['x204']['reason'] == 'edition_conflict'


@pytest.mark.parametrize('editions', [(None, None), (' First ', 'first'), ('First', None)])
def test_unknown_or_normalized_equal_editions_do_not_invent_conflicts(editions):
    src = member('a', '<p id="p">x203</p>', edition=editions[0])
    dst = member('b', '<h2 id="h">x203 Paths</h2>', edition=editions[1])
    report = resolve_related_entries([src, dst])
    assert report['policy']['edition_conflict'] is False
    assert report['references'][0]['status'] == 'resolved'


def test_known_400_character_prefix_only_authorizes_covered_occurrences():
    src = member('a', '<p id="p">x203 ' + 'ordinary words ' * 40 + 'x204</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2><h2 id="h2">x204 Paths</h2>')
    report = resolve_related_entries([src, dst])
    assert refs(report)['x203']['status'] == 'resolved'
    assert refs(report)['x204']['reason'] == 'insufficient_source_evidence'


def test_repeated_invocation_is_html_idempotent_and_provenance_is_immutable():
    src = member('a', '<p id="p">See x203 and x999.</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2>')
    before_rows = deepcopy([m['provenance_rows'] for m in [src, dst]])
    first = resolve_related_entries([src, dst])
    after_first = [html(src), html(dst)]
    second = resolve_related_entries([src, dst])
    assert first['summary'] == {'resolved': 1, 'missing': 1}
    assert second['summary'] == {'missing': 1}
    assert [html(src), html(dst)] == after_first
    assert [m['provenance_rows'] for m in [src, dst]] == before_rows


def test_repeated_document_metadata_keeps_member_provenance_namespaces():
    src = member('a', '<p id="same">x203</p>')
    dst = member('b', '<h2 id="same">x203 Paths</h2>')
    src['document_id'] = dst['document_id'] = 'manual'
    report = resolve_related_entries([src, dst])
    row = report['references'][0]
    assert row['status'] == 'resolved'
    assert row['source']['provenance']['block_kind'] == 'paragraph'
    assert row['target']['evidence']['provenance']['block_kind'] == 'heading'
    assert row['target']['member_id'] == 'b'


@pytest.mark.parametrize('heading', ['Prefix x203 Paths', 'x203.Title', 'Section 2.Title'])
def test_embedded_or_incomplete_heading_identifiers_do_not_authorize(heading):
    src = member('a', '<p id="p">x203 and section 2</p>')
    dst = member('b', f'<h2 id="h">{heading}</h2>')
    report = resolve_related_entries([src, dst])
    assert report['targets'] == []
    assert all(row['status'] == 'missing' for row in report['references'])


@pytest.mark.parametrize('reference', ['x203 in the first edition', 'second edition: x203',
                                      'x203 in edition 2', 'For other editions use x203'])
@pytest.mark.parametrize('edition', [None, 'first'])
def test_literal_edition_mentions_hold_without_semantic_edition_inference(reference, edition):
    src = member('a', f'<p id="p">{reference}</p>', edition=edition)
    dst = member('b', '<h2 id="h">x203 Paths</h2>', edition=edition)
    report = resolve_related_entries([src, dst])
    assert report['references'][0]['reason'] == 'textual_edition_scope'
    assert report['references'][0]['status'] == 'missing'
    assert '<a' not in html(src)


def test_full_leaf_separated_producer_quotes_preserve_raw_offsets():
    src = member('a', '<p id="p">See <em>x2<strong>03e</strong></em>.</p>')
    dst = member('b', '<h2 id="h"><em>x203e</em>: <b>Paths</b></h2>')
    for item in (src, dst):
        soup = BeautifulSoup(html(item), 'html.parser')
        item['provenance_rows'][0]['text_quote'] = ' '.join(soup.find(id=item['provenance_rows'][0]['block_id']).get_text(' ', strip=True).split())
    report = resolve_related_entries([src, dst])
    row = report['references'][0]
    assert row['status'] == 'resolved'
    assert row['source']['location'] == {'start': 4, 'end': 9}
    assert row['target']['heading'] == 'x203e : Paths'
    assert BeautifulSoup(html(src), 'html.parser').get_text() == 'See x203e.'


def test_prefix_leaf_separated_producer_quotes_authorize_only_covered_references():
    src = member('a', '<p id="p"><em>x203</em>' + '<em> word </em>' * 80 + '<em>x204</em></p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2><h2 id="h2">x204 Paths</h2>')
    source_soup = BeautifulSoup(html(src), 'html.parser')
    src['provenance_rows'][0]['text_quote'] = ' '.join(source_soup.p.get_text(' ', strip=True).split())[:400]
    report = resolve_related_entries([src, dst])
    assert refs(report)['x203']['status'] == 'resolved'
    assert refs(report)['x204']['reason'] == 'insufficient_source_evidence'


@pytest.mark.parametrize('reference,heading,status', [
    ('section x203', 'Table x203 Paths', 'missing'),
    ('table x203', 'Section x203 Paths', 'missing'),
    ('chapter x203', 'x203 Paths', 'missing'),
    ('table x203', 'x203 Paths', 'missing'),
    ('section x203', 'x203 Paths', 'resolved'),
    ('paragraph x203', 'x203 Paths', 'resolved'),
    ('table x203', 'Table x203 Paths', 'resolved'),
    ('x203', 'Table x203 Paths', 'resolved')])
def test_explicit_kinds_constrain_which_heading_can_bind(reference, heading, status):
    src = member('a', f'<p id="p">{reference}</p>')
    dst = member('b', f'<h2 id="h">{heading}</h2>')
    report = resolve_related_entries([src, dst])
    row = report['references'][0]
    assert row['status'] == status
    if status == 'missing':
        assert row['reason'] == 'target_kind_mismatch'


@pytest.mark.parametrize('qualifier,reason', [
    ('second edition', 'textual_edition_scope'),
    ('companion manual', 'external_document_scope'),
    ('Equipment Manual', 'unestablished_document_scope')])
def test_visible_anchor_qualifiers_are_read_only_scope_evidence(qualifier, reason):
    original = f'<p id="p">x203 in the <a id="qualifier" href="https://example.org"><em>{qualifier}</em></a>.</p>'
    src = member('a', original)
    dst = member('b', '<h2 id="h">x203 Paths</h2>')
    report = resolve_related_entries([src, dst])
    row = report['references'][0]
    assert row['reason'] == reason
    assert row['target'] is None
    assert row['source']['location'] == {'start': 0, 'end': 4}
    assert html(src) == original


@pytest.mark.parametrize('reference', [
    'x203 of the Equipment Manual', 'x203 in the Equipment Manual',
    'x203 from Equipment Manual', 'x203, x204 of the Equipment Manual',
    'x203 and x204 in the Equipment Manual',
    'x203 of the <a href="other.html">Equipment Manual</a>',
    'x203, <a href="#old">x204</a> of the Equipment Manual',
    'section 2 and section 3 from the Equipment Manual'])
def test_postfix_named_scope_holds_entire_exact_citation_group(reference):
    src = member('a', f'<p id="p">{reference}</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2><h2 id="h2">x204 Paths</h2>'
                 '<h2 id="s2">Section 2 Paths</h2><h2 id="s3">Section 3 Paths</h2>')
    original = html(src)
    report = resolve_related_entries([src, dst])
    assert report['references']
    assert all(row['reason'] == 'unestablished_document_scope' for row in report['references'])
    assert html(src) == original


def test_named_postfix_scope_does_not_cross_intervening_prose_or_sentence():
    src = member('a', '<p id="p">x203 applies here; x204 in the Equipment Manual. x205 applies.</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2><h2 id="h2">x204 Paths</h2><h2 id="h3">x205 Paths</h2>')
    report = resolve_related_entries([src, dst])
    assert refs(report)['x203']['status'] == 'resolved'
    assert refs(report)['x204']['reason'] == 'unestablished_document_scope'
    assert refs(report)['x205']['status'] == 'resolved'


@pytest.mark.parametrize('uri', ['ftp://example.org/x203', 'custom+v2://example.org/x203',
                                'file:///tmp/x203', 'mailto:x203@example.org',
                                'x203@example.org', 'person@example.org/x203',
                                'ftp://example.org/<em>x203</em>',
                                'ftp://<a href="#old">example.org/</a>x203'])
def test_uri_and_email_text_are_opaque_to_symbol_binding(uri):
    src = member('a', f'<p id="p">{uri}</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2>')
    original = html(src)
    report = resolve_related_entries([src, dst])
    assert report['references'] == []
    assert html(src) == original


@pytest.mark.parametrize('qualifier', ['<code>second edition</code>',
                                      '<span hidden>second edition</span>',
                                      '<span aria-hidden="true">second edition</span>',
                                      '<span data-doc-web-generated="true">second edition</span>',
                                      '<span style="display:none">second edition</span>'])
def test_semantic_context_keeps_code_hidden_and_generated_text_opaque(qualifier):
    src = member('a', f'<p id="p">x203 {qualifier}</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2>')
    report = resolve_related_entries([src, dst])
    assert report['references'][0]['status'] == 'resolved'


def test_existing_anchor_citations_remain_noneditable_with_visible_context():
    src = member('a', '<p id="p"><a id="old" href="#original">x203</a>, then x204.</p>')
    dst = member('b', '<h2 id="h">x203 Paths</h2><h2 id="h2">x204 Paths</h2>')
    report = resolve_related_entries([src, dst])
    assert [row['label'] for row in report['references']] == ['x204']
    soup = BeautifulSoup(html(src), 'html.parser')
    assert soup.find(id='old')['href'] == '#original'
    assert not soup.select('a a')


@pytest.mark.parametrize('kind,labels', [('paragraph', ('x203', 'x204')),
                                        ('section', ('x203', 'x204')),
                                        ('paragraph', ('2', '3')),
                                        ('section', ('2', '3'))])
@pytest.mark.parametrize('scope,reason', [
    ('in the companion manual, ', 'external_document_scope'),
    ('in the Equipment Manual, ', 'unestablished_document_scope'),
    ('in the <a href="https://example.org">companion manual</a>, ', 'external_document_scope'),
    ('in the <a href="https://example.org">Equipment Manual</a>, ', 'unestablished_document_scope')])
@pytest.mark.parametrize('list_form', ['single', 'explicit', 'shared'])
def test_complete_typed_scope_grammar_handles_prefixed_numeric_and_shared_lists(kind, labels, scope, reason, list_form):
    first, second = labels
    citation = f'{kind} {first}'
    if list_form == 'explicit':
        citation += f' and {kind} {second}'
    elif list_form == 'shared':
        citation += f' and {second}'
    src = member('a', f'<p id="p">{scope}{citation}</p>')
    dst = member('b', f'<h2 id="h">{kind.title()} {first} Paths</h2>'
                 f'<h2 id="h2">{kind.title()} {second} Paths</h2>')
    original = html(src)
    report = resolve_related_entries([src, dst])
    assert report['references']
    assert all(row['reason'] == reason for row in report['references'])
    assert html(src) == original


@pytest.mark.parametrize('kind,label,tail', [('section', 'x203', '2'),
                                           ('paragraph', '2', '3')])
def test_shared_numeric_list_tail_carries_postfix_document_scope(kind, label, tail):
    src = member('a', f'<p id="p">{kind} {label} and {tail} in the Equipment Manual</p>')
    dst = member('b', f'<h2 id="h">{kind.title()} {label} Paths</h2>')
    report = resolve_related_entries([src, dst])
    assert report['references'][0]['reason'] == 'unestablished_document_scope'
    assert '<a' not in html(src)


@pytest.mark.parametrize('label', ['x203', '2'])
@pytest.mark.parametrize('heading_kind,expected', [('Table', 'missing'),
                                                 ('Section', 'missing'),
                                                 ('Paragraph', 'resolved')])
def test_turn_to_paragraph_preserves_explicit_kind(label, heading_kind, expected):
    src = member('a', f'<p id="p">turn to paragraph {label}</p>')
    dst = member('b', f'<h2 id="h">{heading_kind} {label} Paths</h2>')
    report = resolve_related_entries([src, dst])
    row = report['references'][0]
    assert row['kind'] == 'paragraph'
    assert row['status'] == expected
    if expected == 'missing':
        assert row['reason'] == 'target_kind_mismatch'


@pytest.mark.parametrize('prefix,reason', [('in the companion manual, ', 'external_document_scope'),
                                         ('in the Equipment Manual, ', 'unestablished_document_scope')])
def test_turn_paragraph_prefixed_identifier_keeps_complete_prefix_scope(prefix, reason):
    src = member('a', f'<p id="p">{prefix}turn to paragraph x203</p>')
    dst = member('b', '<h2 id="h">Paragraph x203 Paths</h2>')
    report = resolve_related_entries([src, dst])
    assert report['references'][0]['reason'] == reason
