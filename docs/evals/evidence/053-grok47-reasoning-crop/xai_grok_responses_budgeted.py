"""Budget-enforced Promptfoo xAI adapter for one serialized calibration request at a time."""
from __future__ import annotations
import fcntl, hashlib, importlib.util, json, math, os, sys, time, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PROVIDER=ROOT/'benchmarks/providers/xai_grok_responses.py'
spec=importlib.util.spec_from_file_location('xai_grok_responses_budgeted_base', PROVIDER)
base=importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
LEDGER=Path(os.environ['GROK47_BUDGET_LEDGER'])
RESERVE=2.098304

def update(fn):
    with LEDGER.open('r+') as h:
        fcntl.flock(h, fcntl.LOCK_EX)
        data=json.load(h); fn(data); h.seek(0); json.dump(data,h,indent=2); h.write('\n'); h.truncate(); h.flush(); os.fsync(h.fileno())
        fcntl.flock(h, fcntl.LOCK_UN)

def call_api(prompt, options, context):
    call_id=str(uuid.uuid4())
    now=time.time()
    admitted={'ok':False}
    def reserve(d):
        if d['settled_usd']+d['unresolved_reservations_usd']+RESERVE <= d['hard_cap_usd']+1e-12:
            d['unresolved_reservations_usd']+=RESERVE
            row={'id':call_id,'provider':'xAI','state':'reserved-before-dispatch','reservation_usd':RESERVE,'timestamp_unix':now,'effort':base._request_settings(options)['reasoning_effort'],'case':(context.get('vars') or {}).get('golden_key'),'prompt_bytes':len(prompt.encode()),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()}
            d['calls'].append(row); admitted['ok']=True
        else:
            d['calls'].append({'id':call_id,'provider':'xAI','state':'refused-reservation-hard-cap','required_reservation_usd':RESERVE,'timestamp_unix':now,'case':(context.get('vars') or {}).get('golden_key')})
            d['state']='hard-cap admission stop'
    update(reserve)
    if not admitted['ok']:
        return {'error':'Grok47 hard-cap reservation refused before dispatch'}
    result=base.call_api(prompt,options,context)
    cost=result.get('cost') if isinstance(result,dict) else None
    metadata=result.get('metadata',{}) if isinstance(result,dict) else {}
    usage=result.get('tokenUsage') if isinstance(result,dict) else None
    valid=(isinstance(cost,(int,float)) and not isinstance(cost,bool) and math.isfinite(cost) and cost>=0 and isinstance(usage,dict) and metadata.get('usage_error') is None)
    def settle(d):
        row=next(x for x in d['calls'] if x['id']==call_id)
        if valid and cost<=RESERVE+1e-12:
            d['unresolved_reservations_usd']-=RESERVE
            d['settled_usd']+=float(cost)
            row.update({'state':'settled','settled_usd':float(cost),'usage':usage,'requested_model':metadata.get('requested_model'),'served_model':metadata.get('served_model'),'terminal_status':metadata.get('response_status'),'output_contract':metadata.get('requested_output_contract'),'raw_envelope_path':metadata.get('raw_envelope_path'),'raw_envelope_sha256':metadata.get('raw_envelope_sha256'),'raw_envelope_bytes':metadata.get('raw_envelope_bytes'),'error_classification':('response-error' if result.get('error') else None)})
            d['state']='candidate calibration request settled'
        else:
            row.update({'state':'unresolved-reservation-retained','usage':usage,'reported_cost':cost,'metadata':{k:metadata.get(k) for k in ['requested_model','served_model','response_status','usage_error','provider_error','raw_envelope_path','raw_envelope_sha256','raw_envelope_bytes']}})
            d['state']='unresolved provider charge; no further call until reconciled'
    update(settle)
    return result
