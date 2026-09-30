"""Serial one-case continuation; never retries or advances a failed arm."""
import json
import os
import subprocess
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'benchmarks/results/safety-repair-048-20260929-continuation1'
for arm in os.environ.get('SAFETY_REPAIR_ARMS', 'luna,sol,control').split(','):
    stage = os.environ.get('SAFETY_REPAIR_STAGE_KIND', 'full')
    os.environ['SAFETY_REPAIR_STAGE'] = stage + '-' + arm
    task_path = ROOT / f'benchmarks/tasks/safety-repair-048-{arm}-{stage}-continuation1.yaml'
    task = yaml.safe_load(task_path.read_text())
    aggregate = []
    for index, row in enumerate(task['tests']):
        ledger = json.loads((OUT/'ledger.json').read_text())
        if any(c.get('stage') == stage + '-' + arm and c.get('case_key') == row['vars']['crop_key'] for c in ledger['calls']):
            continue  # Preserve completed and unavailable attempts; never resend.
        single = dict(task, tests=[row])
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', prefix='_048-single-', dir=task_path.parent, delete=False) as f:
            yaml.safe_dump(single, f, sort_keys=False)
            config = Path(f.name)
        result = OUT / f'{stage}-{arm}-case-{index+1:02d}.json'
        try:
            with result.with_suffix('.log').open('w') as log:
                status = subprocess.run(['promptfoo', 'eval', '-c', str(config), '--no-cache', '--output', str(result), '-j', '1'], cwd=ROOT/'benchmarks', stdout=log, stderr=subprocess.STDOUT).returncode
        finally:
            config.unlink(missing_ok=True)
        if not result.exists():
            print('operational stop', arm, row['vars']['crop_key'], status, flush=True)
            break
        records = json.loads(result.read_text())['results']['results']
        aggregate.extend(records)
        saved = [{'case':x['vars']['crop_key'], 'success':x['success'], 'response':x.get('response'), 'error':x.get('error')} for x in aggregate]
        (OUT/f'{stage}-{arm}-case-summary.json').write_text(json.dumps(saved, indent=2)+'\n')
        x=records[0]
        print(json.dumps({'arm':arm,'case':x['vars']['crop_key'],'success':x['success'],'output':x.get('response',{}).get('output'),'error':x.get('error')}),flush=True)
        ledger=json.loads((OUT/'ledger.json').read_text())
        if ledger.get('closed') or ledger['calls'][-1].get('cost_usd') is None:
            raise SystemExit('Operational stop; no recovery allowance remains')
        diagnostic_exception = (stage == 'full' and x['vars']['crop_key'] == 'page-012-001') or (stage == 'fresh' and x['vars']['crop_key'] == 'S3')
        if not x['success'] and not diagnostic_exception:
            print('arm gate failed; source adjudication required; no later subjects sent for this arm',arm,flush=True)
            break
