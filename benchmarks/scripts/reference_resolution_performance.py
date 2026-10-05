#!/usr/bin/env python3
"""Isolated paired Story243 measurements; development inputs only, no providers."""
from __future__ import annotations

import argparse
import cProfile
import hashlib
import importlib.util
import io
import json
import platform
import pstats
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    'modules/common/__init__.py', 'modules/common/utils.py',
    'modules/common/manual_navigation.py', 'modules/common/reference_resolution.py',
    'benchmarks/scripts/reference_resolution_benchmark.py',
    'benchmarks/golden/reference_resolution_freeze.json',
    'tests/fixtures/reference_resolution/development.json',
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str) + '\n')


def load_harness(root):
    sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location('frozen_benchmark', root / 'benchmarks/scripts/reference_resolution_benchmark.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def loaded_receipt(root):
    result = {}
    for name, module in sorted(sys.modules.items()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_file() and (name.startswith(('modules', 'bs4', 'soupsieve', 'yaml')) or name == 'frozen_benchmark'):
            resolved = Path(path).resolve()
            if name.startswith('modules') and not resolved.is_relative_to(root.resolve()):
                raise RuntimeError(f'Variant leaked ambient import: {name}: {resolved}')
            result[name] = {'path': str(resolved), 'sha256': sha(resolved)}
    return result


def worker(root, corpus_path):
    harness = load_harness(root)
    fn = harness.resolver()
    corpus = json.loads(corpus_path.read_text())
    for line in sys.stdin:
        request = json.loads(line)
        action = request['action']
        if action == 'evaluate':
            result = harness.evaluate(corpus, fn, 1)
            save(request['out'], result)
            parity = {}
            for enabled in [False, True]:
                entries, report, _ = harness.invoke(fn, corpus, enabled)
                report.pop('timing', None)
                state = {'entries': entries, 'report': report}
                state_path = request['out'] + ('.on-state.json' if enabled else '.off-state.json')
                save(state_path, state)
                parity[str(enabled)] = sha(state_path)
            response = {'pass': result['pass'], 'cases': len(corpus['cases']), 'parity_sha256': parity, 'loaded': loaded_receipt(root)}
        elif action == 'profile':
            profile = cProfile.Profile()
            profile.enable()
            harness.invoke(fn, corpus, True)
            profile.disable()
            profile.dump_stats(request['out'] + '.pstats')
            stream = io.StringIO()
            pstats.Stats(profile, stream=stream).strip_dirs().sort_stats('cumulative').print_stats(60)
            Path(request['out'] + '.txt').write_text(stream.getvalue())
            response = {'loaded': loaded_receipt(root)}
        elif action == 'time':
            _, _, elapsed = harness.invoke(fn, corpus, True)
            response = {'elapsed_ms': elapsed, 'loaded': loaded_receipt(root)}
        else:
            raise ValueError(action)
        print(json.dumps(response), flush=True)


def spawn(root, corpus, log):
    return subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()), '--worker', str(root), '--corpus', str(corpus)],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log, text=True, cwd=root)


def ask(process, request):
    process.stdin.write(json.dumps(request) + '\n')
    process.stdin.flush()
    line = process.stdout.readline()
    if not line:
        raise RuntimeError(f'Worker terminated: {process.poll()}')
    return json.loads(line)


def snapshot(out):
    baseline = out / 'baseline'
    baseline.mkdir(parents=True, exist_ok=False)
    for relative in FILES:
        source = ROOT / relative
        if source.exists():
            target = baseline / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    harness = load_harness(baseline)
    development, _ = harness.load_corpus('development')
    natural = Path('/Users/cam/Documents/Projects/codex-forge/output/runs/ff-deathtrap-dungeon-small/gamebook.json')
    expected = '6173c7060ce4debf89729dee3bbf6e3637357a150dafb60c71f35c22fe714014'
    if sha(natural) != expected:
        raise RuntimeError('Deathtrap frozen source changed')
    shutil.copy2(natural, out / 'deathtrap-source.json')
    deathtrap = harness.natural_gamebook(out / 'deathtrap-source.json')
    save(out / 'development-corpus.json', development)
    save(out / 'deathtrap-corpus.json', deathtrap)
    runtime_paths = [ROOT / 'driver.py', ROOT / 'schemas.py', ROOT / 'validate_artifact.py',
                     ROOT / 'configs/recipes/recipe-reference-resolution-smoke.yaml',
                     ROOT / 'tests/fixtures/reference_resolution/pages.jsonl',
                     ROOT / 'tests/fixtures/reference_resolution/portions.jsonl',
                     Path(__file__)]
    runtime_paths += list((ROOT / 'modules').rglob('*.py')) + list((ROOT / 'modules').rglob('module.yaml')) + list((ROOT / 'doc_web').glob('*.py'))
    receipt = {'frozen_at': time.time(), 'python': sys.executable, 'python_version': sys.version,
               'platform': platform.platform(), 'snapshot_files': {p: sha(baseline / p) for p in FILES if (baseline / p).exists()},
               'pipeline_sources': {str(p.relative_to(ROOT)): sha(p) for p in runtime_paths},
               'inputs': {p.name: sha(p) for p in out.glob('*corpus.json')},
               'natural_source': {'path': str(natural), 'sha256': sha(natural)},
               'pair_count': 20, 'order': 'ABBA alternating pair order; each pair one measurement per variant',
               'adoption': '>=10% median paired gain per corpus, >=80% winning pairs, no p95 regression; quality parity mandatory',
               'heldout_opened': False, 'api_calls': 0, 'cost_usd': 0}
    save(out / 'baseline-freeze.json', receipt)
    return receipt


def collect(out, variant=None):
    result = {}
    for name in ['development', 'deathtrap']:
        corpus = out / f'{name}-corpus.json'
        with (out / f'{name}-workers.log').open('a') as log:
            base = spawn(out / 'baseline', corpus, log)
            candidate = spawn(variant, corpus, log) if variant else None
            try:
                if candidate is None:
                    quality = ask(base, {'action': 'evaluate', 'out': str(out / f'baseline-{name}-quality.json')})
                    if not quality['pass']:
                        raise RuntimeError('Baseline quality failed')
                    profile = ask(base, {'action': 'profile', 'out': str(out / f'baseline-{name}-profile')})
                    samples = [ask(base, {'action': 'time'})['elapsed_ms'] for _ in range(5)]
                    result[name] = {'quality': quality, 'profile': profile, 'baseline_samples_ms': samples}
                else:
                    qualities = [ask(proc, {'action': 'evaluate', 'out': str(out / f'{variant.name}-{name}-{label}-quality.json')})
                                 for proc, label in [(base, 'baseline'), (candidate, 'candidate')]]
                    if not all(q['pass'] for q in qualities) or qualities[0]['parity_sha256'] != qualities[1]['parity_sha256']:
                        raise RuntimeError('Paired quality failed')
                    ask(base, {'action': 'time'})
                    ask(candidate, {'action': 'time'})
                    pairs = []
                    for pair in range(20):
                        processes = [('baseline', base), ('candidate', candidate)] if pair % 2 == 0 else [('candidate', candidate), ('baseline', base)]
                        values = {label: ask(proc, {'action': 'time'})['elapsed_ms'] for label, proc in processes}
                        values['order'] = [label for label, _ in processes]
                        values['paired_gain'] = 1 - values['candidate'] / values['baseline']
                        pairs.append(values)
                    gain = statistics.median(p['paired_gain'] for p in pairs)
                    wins = sum(p['paired_gain'] > 0 for p in pairs)
                    bp95 = sorted(p['baseline'] for p in pairs)[18]
                    cp95 = sorted(p['candidate'] for p in pairs)[18]
                    result[name] = {'quality': qualities, 'pairs': pairs, 'median_paired_gain': gain, 'winning_pairs': wins,
                                    'baseline_p50_ms': statistics.median(p['baseline'] for p in pairs),
                                    'candidate_p50_ms': statistics.median(p['candidate'] for p in pairs),
                                    'baseline_p95_ms': bp95, 'candidate_p95_ms': cp95,
                                    'speed_gate': gain >= .10 and wins >= 16 and cp95 <= bp95}
            finally:
                for process in [base, candidate]:
                    if process:
                        process.stdin.close()
                        process.wait(timeout=10)
    save(out / (f'{variant.name}-comparison.json' if variant else 'baseline-profile-summary.json'), result)
    print(json.dumps({name: {k: v for k, v in row.items() if k not in {'quality', 'profile', 'pairs'}} for name, row in result.items()}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--snapshot', action='store_true')
    parser.add_argument('--variant', type=Path)
    parser.add_argument('--worker', type=Path)
    parser.add_argument('--corpus', type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.corpus)
        return
    out = args.out.resolve()
    if args.snapshot:
        snapshot(out)
    collect(out, args.variant.resolve() if args.variant else None)


if __name__ == '__main__':
    main()
