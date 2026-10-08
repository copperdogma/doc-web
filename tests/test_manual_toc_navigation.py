"""Whole source TOC rows authorize heading targets, never bare-number guesses."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
from bs4 import BeautifulSoup

from modules.build.build_chapter_html_v1.main import _tag_entry_body
from modules.common.manual_navigation import inspect_navigation, resolve_navigation


def _page(number, html, *, printed=None, inferred=False, original=None, side=None):
    return {'page_number': number, 'html': html, 'printed_page_number': printed,
            'printed_page_number_text': None if inferred or printed is None else str(printed),
            'printed_page_number_inferred': inferred, 'original_page_number': original or number,
            'spread_side': side}


def _entry(path, pages):
    entry = {'filename': path, 'prepared_pages': pages,
             'body_html': '\n'.join(p['html'] for p in pages),
             'source_pages': [p['page_number'] for p in pages]}
    entry['body_html'], rows = _tag_entry_body(entry, run_id='test', created_at='fixed')
    return entry, rows


def _toc(*rows):
    return '<h2>Navigation</h2><table><tbody>' + ''.join(
        f'<tr><td><strong>{title}</strong></td><td><a href="{href}"><em>{label}</em></a></td></tr>'
        for title, label, href in rows) + '</tbody></table>'


def _resolve(entries, rows):
    return resolve_navigation(entries, source_pages=[p for e in entries for p in e['prepared_pages']],
                              provenance_rows=rows)


def _inspect(tmp_path, entries, rows):
    files = []
    for entry in entries:
        path = tmp_path / entry['filename']
        path.write_text(entry['body_html'])
        files.append(path)
    return inspect_navigation(files, source_entries=entries,
                              source_pages=[p for e in entries for p in e['prepared_pages']], provenance_rows=rows)


def test_adjacent_titles_disambiguate_same_page_and_numbered_heading(tmp_path):
    first, rows = _entry('contents.html', [_page(1, _toc(('Setting out', '3', '#3'), ('Route Choices', '3', '#3')))])
    target, more = _entry('guide.html', [_page(2, '<h2>3 Unrelated phase</h2>', printed=2),
                                       _page(3, '<h2>SETTING OUT</h2><h3>Route Choices</h3>', printed=3)])
    before_pages, before_rows = copy.deepcopy(first['prepared_pages']), copy.deepcopy(rows + more)
    before_text = BeautifulSoup(first['body_html'], 'html.parser').get_text()
    report = _resolve([first, target], rows + more)
    assert report['summary'] == {'resolved': 2}
    links = BeautifulSoup(first['body_html'], 'html.parser').find_all('a')
    assert [a['href'] for a in links] == ['guide.html#blk-guide-0002', 'guide.html#blk-guide-0003']
    assert [a.em.get_text() for a in links] == ['3', '3']
    assert BeautifulSoup(first['body_html'], 'html.parser').get_text() == before_text
    assert first['prepared_pages'] == before_pages and rows + more == before_rows
    assert all(r['target']['evidence']['printed_page_authority'] for r in report['references'])
    assert _inspect(tmp_path, [first, target], rows + more) == ([], [])
    assert _resolve([first, target], rows + more)['summary'] == {'preserved': 2}


def test_observed_page_disambiguates_case_equivalent_repeated_title():
    source, rows = _entry('contents.html', [_page(1, _toc(('Round overview', '11', '#11')))])
    target, more = _entry('guide.html', [_page(11, '<h2>Round overview</h2>', printed=11),
                                       _page(32, '<h2>ROUND OVERVIEW</h2>', printed=32)])
    report = _resolve([source, target], rows + more)
    assert report['references'][0]['resolved_href'] == 'guide.html#blk-guide-0001'
    assert report['references'][0]['reason'] == 'unique_source_toc_title_and_page'


@pytest.mark.parametrize('printed,inferred', [(None, False), (2, True)])
def test_unique_heading_fallback_does_not_authorize_inferred_page(printed, inferred):
    source, rows = _entry('contents.html', [_page(1, _toc(('First Steps', '2', '#2')))])
    target, more = _entry('guide.html', [_page(2, '<h2>FIRST STEPS</h2>', printed=printed, inferred=inferred)])
    row = _resolve([source, target], rows + more)['references'][0]
    assert row['reason'] == 'unique_source_toc_heading'
    assert row['target']['evidence']['printed_page_authority'] is False
    assert row['target']['evidence']['page_observations'] == []


def test_known_title_page_conflict_holds_even_when_href_exists(tmp_path):
    source, rows = _entry('contents.html', [_page(1, _toc(('Route Choices', '4', 'guide.html#blk-guide-0002')))])
    target, more = _entry('guide.html', [_page(3, '<h2>Route Choices</h2>', printed=3),
                                       _page(4, '<h2>Other Material</h2>', printed=4)])
    assert _inspect(tmp_path, [source, target], rows + more)[0][0]['reason'] == 'toc_title_printed_page_conflict'
    row = _resolve([source, target], rows + more)['references'][0]
    assert row['status'] == 'unresolved' and row['reason'] == 'toc_title_printed_page_conflict'
    assert BeautifulSoup(source['body_html'], 'html.parser').select_one('td span')['data-doc-web-navigation-status'] == 'unresolved'


def test_absent_referenced_page_cannot_override_known_different_heading_page():
    source, rows = _entry('contents.html', [_page(1, _toc(('First Steps', '2', '#2')))])
    target, more = _entry('guide.html', [_page(3, '<h2>First Steps</h2>', printed=3)])
    row = _resolve([source, target], rows + more)['references'][0]
    assert row['status'] == 'unresolved' and row['reason'] == 'toc_title_printed_page_conflict'


def test_valid_but_wrong_target_is_corrected_and_independently_inspected(tmp_path):
    source, rows = _entry('contents.html', [_page(1, _toc(('Route Choices', '4', 'guide.html#blk-guide-0001')))])
    target, more = _entry('guide.html', [_page(4, '<h2>Other Material</h2><h2>Route Choices</h2>', printed=4)])
    assert _inspect(tmp_path, [source, target], rows + more)[0][0]['reason'] == 'source_toc_target_mismatch'
    report = _resolve([source, target], rows + more)
    assert report['references'][0]['resolved_href'] == 'guide.html#blk-guide-0002'
    assert _inspect(tmp_path, [source, target], rows + more) == ([], [])
    source['body_html'] = source['body_html'].replace('guide.html#blk-guide-0002', 'guide.html#blk-guide-0001')
    assert _inspect(tmp_path, [source, target], rows + more)[0][0]['reason'] == 'source_toc_target_mismatch'


@pytest.mark.parametrize('target_pages,reason', [
    ([_page(4, '<h2>Route Choices</h2><h2>ROUTE CHOICES</h2>', printed=4)], 'toc_duplicate_heading_targets'),
    ([_page(4, '<h2>Route Choices</h2>'), _page(5, '<h2>ROUTE CHOICES</h2>')], 'toc_duplicate_heading_targets'),
    ([_page(4, '<h2>Route Choices</h2>', printed=4), _page(5, '<h2>Other Material</h2>', printed=4)], 'duplicate_observed_printed_labels'),
])
def test_duplicate_targets_or_observed_labels_remain_ambiguous(target_pages, reason):
    source, rows = _entry('contents.html', [_page(1, _toc(('Route Choices', '4', '#4')))])
    target, more = _entry('guide.html', target_pages)
    row = _resolve([source, target], rows + more)['references'][0]
    assert row['status'] == 'ambiguous' and row['reason'] == reason


@pytest.mark.parametrize('mode', ['source_duplicate', 'final_duplicate', 'missing_provenance', 'wrong_provenance'])
def test_row_occurrence_and_provenance_gate(mode):
    toc = _toc(('Route Choices', '4', '#4'))
    if mode == 'source_duplicate':
        toc = _toc(('Route Choices', '4', '#4'), ('Route Choices', '4', '#4'))
    source, rows = _entry('contents.html', [_page(1, toc)])
    target, more = _entry('guide.html', [_page(4, '<h2>Route Choices</h2>', printed=4)])
    if mode == 'final_duplicate':
        soup = BeautifulSoup(source['body_html'], 'html.parser')
        soup.tbody.append(copy.copy(soup.tr))
        source['body_html'] = str(soup)
    if mode == 'missing_provenance':
        rows = []
    if mode == 'wrong_provenance':
        rows = copy.deepcopy(rows)
        for row in rows:
            row['source_page_number'] = 99
    row = _resolve([source, target], rows + more)['references'][0]
    assert row['status'] != 'resolved'
    assert row['reason'].startswith('toc_source_row_')


def test_generated_heading_and_prefix_match_cannot_authorize_toc():
    source, rows = _entry('contents.html', [_page(1, _toc(('Route Choices', '4', '#4')))])
    target, more = _entry('guide.html', [_page(4, '<h2>Route Choices extended</h2>', printed=4)])
    target['body_html'] += '<h2 id="fake">Route Choices</h2>'
    row = _resolve([source, target], rows + more)['references'][0]
    assert row['status'] == 'unresolved'
    assert row['reason'] == 'toc_title_printed_page_conflict'


def test_foreign_explicit_file_cannot_borrow_local_heading():
    source, rows = _entry('contents.html', [_page(1, _toc(('Route Choices', '4', 'other-edition.html#4')))])
    target, more = _entry('guide.html', [_page(4, '<h2>Route Choices</h2>', printed=4)])
    row = _resolve([source, target], rows + more)['references'][0]
    assert row['reason'] == 'toc_source_destination_outside_document'
    assert row['status'] == 'unresolved'


@pytest.mark.parametrize('href', ['#quantity-note', 'contents.html#quantity-note'])
def test_numeric_quantity_table_preserves_exact_source_id_authority(tmp_path, href):
    source_html = ('<h2>Order quantities</h2><table><tr><td>Route Choices</td>'
                   f'<td><a href="{href}">4</a></td></tr></table>'
                   '<p id="quantity-note">Four copies are included.</p>')
    source, rows = _entry('contents.html', [_page(1, source_html)])
    target, more = _entry('guide.html', [_page(4, '<h2>Route Choices</h2>', printed=4)])
    report = _resolve([source, target], rows + more)
    row = report['references'][0]
    assert row['reason'] == 'original_id_rebound'
    assert BeautifulSoup(source['body_html'], 'html.parser').a['href'] == '#blk-contents-0003'
    assert not row.get('toc_evidence')
    assert _inspect(tmp_path, [source, target], rows + more) == ([], [])
    assert _resolve([source, target], rows + more)['references'][0]['reason'] == 'original_id_authority'
    assert _inspect(tmp_path, [source, target], rows + more) == ([], [])
    # A reachable heading cannot borrow the genuine note's authority receipt.
    source['body_html'] = source['body_html'].replace('href="#blk-contents-0003"', 'href="guide.html#blk-guide-0001"')
    assert _inspect(tmp_path, [source, target], rows + more)[0]


@pytest.mark.parametrize('chapter_portions', [False, True])
def test_real_builder_retains_spread_identity_and_inferred_flag(tmp_path, chapter_portions):
    """Exercise both prepared-page constructors, beyond hand-built entries."""
    pages = [
        _page(1, _toc(('First Steps', '2', '#2'), ('Route Choices', '3', '#3')), printed=1),
        _page(2, '<h2>First Steps</h2><p>Start here.</p>', printed=2,
              inferred=True, original=2, side='L'),
        _page(3, '<h2>Route Choices</h2><p>Choose a route.</p>', printed=3,
              original=2, side='R'),
    ]
    for page in pages:
        page['page_id'] = f"source-page-{page['page_number']}"
    portions = ([{'title': title, 'page_start': number, 'page_end': number}
                 for number, title in [(1, 'Navigation'), (2, 'First Steps'), (3, 'Route Choices')]]
                if chapter_portions else [{'title': 'Uncovered section', 'page_start': 99, 'page_end': 99}])
    pages_path, portions_path = tmp_path / 'pages.jsonl', tmp_path / 'portions.jsonl'
    pages_path.write_text(''.join(json.dumps(page) + '\n' for page in pages))
    portions_path.write_text(''.join(json.dumps(portion) + '\n' for portion in portions))
    (tmp_path / 'pipeline_state.json').write_text('{}')
    html_dir = tmp_path / 'html'
    result = subprocess.run([
        sys.executable, '-m', 'modules.build.build_chapter_html_v1.main',
        '--pages', str(pages_path), '--portions', str(portions_path),
        '--out', str(tmp_path / 'manifest.jsonl'), '--output-dir', str(html_dir),
    ], cwd=str(Path(__file__).resolve().parents[1]), capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = json.loads((html_dir / 'navigation_resolution_report.json').read_text())
    references = [row for row in report['references'] if row.get('toc_evidence')]
    assert len(references) == 2
    assert all(row['status'] == 'resolved' for row in references)
    assert references[0]['reason'] == 'unique_source_toc_heading'
    assert references[0]['target']['evidence']['printed_page_authority'] is False
    assert references[1]['reason'] == 'unique_source_toc_title_and_page'
    assert references[1]['target']['evidence']['page_observations'][0]['spread_side'] == 'R'
    assert report['final_validation']['status'] == 'passed'
