"""Source-authored generic repair controls at the public driver boundary."""
import json
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def test_reference_repair_driver_on_off(tmp_path):
    bundles = {}
    for enabled in (False, True):
        out = tmp_path / ('on' if enabled else 'off')
        command = [sys.executable, 'driver.py', '--recipe',
                   'configs/recipes/recipe-reference-resolution-repairs.yaml',
                   '--run-id', f'reference-repairs-{enabled}', '--output-dir', str(out)]
        if enabled:
            command.append('--resolve-references')
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        html_root = out / f'reference-repairs-{enabled}' / 'output' / 'html'
        report = json.loads((html_root / 'navigation_resolution_report.json').read_text())
        assert report['final_validation']['status'] == 'passed'
        assert report['api_calls'] == report['cost_usd'] == 0
        soups = {p.name: BeautifulSoup(p.read_text(), 'html.parser')
                 for p in html_root.glob('*.html') if p.name != 'index.html'}
        source = next(s for s in soups.values() if s.find('p', string=lambda t: t and t.startswith('As noted')))
        legacy = next(p for p in source.find_all('p') if p.get_text().startswith('Legacy:'))
        assert legacy.a is not None
        target_file, target_id = legacy.a['href'].split('#')
        target_soup = soups[target_file] if target_file else source
        assert target_soup.find(id=target_id).get_text() == 'R123 Combat'
        ordinary = next(p for p in source.find_all('p') if p.get_text().startswith('As noted'))
        assert not ordinary.select('a, [data-doc-web-navigation-status]')
        foreign = [p for p in source.find_all('p') if 'companion manual' in p.get_text()
                   or 'other installation guide' in p.get_text()
                   or p.get_text().startswith('According to')]
        assert all(not p.a for p in foreign)
        if enabled:
            local = next(p for p in source.find_all('p') if p.get_text() == 'See section 3 in this manual.')
            assert local.a
            prefix = next(p for p in source.find_all('p') if p.get_text() == 'See Q42 and (APP7).')
            assert [a.get_text() for a in prefix.find_all('a')] == ['Q42', 'APP7']
            assert source.table.find('a').get_text() == 'Q42'
            assert sum(r.get('reason') == 'external_document_scope' for r in report['references']) >= 3
            assert sum(r.get('reason') == 'unestablished_document_scope' for r in report['references']) >= 2
        else:
            assert not source.table.find('a')
            assert len(source.article.select('a')) == 1
        bundles[enabled] = (soups, html_root)
    def provenance(root):
        rows = [json.loads(line) for line in (root / 'provenance' / 'blocks.jsonl').read_text().splitlines()]
        return [{k: v for k, v in row.items() if k not in {'run_id', 'created_at'}} for row in rows]
    assert provenance(bundles[True][1]) == provenance(bundles[False][1])
    for filename, soup in bundles[False][0].items():
        other = bundles[True][0][filename]
        assert soup.article.get_text() == other.article.get_text()
        assert [t['id'] for t in soup.article.find_all(id=True)] == [t['id'] for t in other.article.find_all(id=True)]
