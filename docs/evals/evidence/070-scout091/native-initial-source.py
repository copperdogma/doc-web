"""Approved Scout091 native owner campaign. Two hard ledgers, serial and fresh."""
from __future__ import annotations
import argparse
import base64
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/evals/evidence/070-scout091'
RAW=ROOT/'benchmarks/results/scout091-20261013'
CAPS={'text':4.,'visual':8.}
MODELS={'clef':'cloudflare/clef-omni-20261009','drex':'nace-ai/drex-v2.0-20261009','liquid':'liquid/d1-20260930','scaledown':'scaledown/classify-1-20260928','solar':'upstage/solar-decide-20260928'}
RATES={'clef':.15,'drex':.06,'liquid':.04,'scaledown':.04,'solar':.05}
PROVIDERS={'clef':'Cloudflare','drex':'DeepInfra','liquid':'Liquid','scaledown':'ScaleDown','solar':'Upstage'}

def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
legacy=load('scout091_legacy',ROOT/'benchmarks/jev-consistency/run.py')
image=load('scout091_images',ROOT/'benchmarks/jev-consistency/decisions_campaign.py')

def write(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');tmp.replace(path)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def fixtures():return json.loads((ROOT/'benchmarks/jev-consistency/fixtures.json').read_text())
def state_json(state):return json.dumps(state,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def body(arm,state,labels=None,instruction=None):
 if arm=='gpt41':return legacy.payload('gpt',state)
 labels=legacy.LABELS if labels is None else labels;instruction=legacy.INSTRUCTION if instruction is None else instruction
 if arm=='scaledown' and not isinstance(state,list):
  encoded=state_json(state);assert json.loads(encoded)==state;state={'text':encoded}
 return {'model':MODELS[arm],'state':state,'questions':{'status':{'type':'choice','instructions':instruction,'criteria':labels}},'provider':{'only':[PROVIDERS[arm]],'allow_fallbacks':False}}

def image_body(key,arm):
 b=image.image_body(key,'gpt55')
 if arm=='gpt55':return b
 content=b['input'][0]['content']
 state=[]
 for part in content:
  if part['type']=='input_text':state.append(part['text'])
  elif part['type']=='input_image':state.append({'type':'image_url','image_url':{'url':part['image_url']}})
  else:raise ValueError('unknown input part')
 return body(arm,state,{'pass':'The crop meets the supplied PASS rules and no FAIL condition applies.','fail':'A supplied FAIL condition applies, including unresolved source-boundary uncertainty; do not accept without review.'},'Select the verdict using all source-context rules supplied with the images. A fail verdict routes this crop for review; it never authorizes source deletion.')

def mapping(arm):
 catalog=json.loads((OUT/'router-catalog.json').read_text());return next(x for x in catalog if x['canonical_slug']==MODELS[arm])

def parse(arm,raw,labels):
 if arm=='gpt41':return legacy.parse('gpt',raw)
 if arm=='gpt55':return image.parse(arm,raw,labels)
 mapped=mapping(arm)
 if raw.get('model') not in [MODELS[arm],mapped['id']] or raw.get('provider')!=PROVIDERS[arm] or raw.get('error'):
  raise ValueError('served identity/provider/error')
 if set(raw.get('answers',{}))!={'status'}:raise ValueError('answer set')
 a=raw['answers']['status'];p=a.get('probabilities',{});c=a.get('confidence');choice=a.get('choice')
 if a.get('type')!='choice' or set(p)!=set(labels) or choice not in labels:raise ValueError('choice contract/refusal')
 if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in [*p.values(),c]):raise ValueError('probability/confidence')
 if abs(sum(p.values())-1)>.002 or p[choice]<max(p.values()):raise ValueError('sum/argmax')
 u=raw.get('usage',{})
 if any(type(u.get(k)) is not int or u[k]<0 for k in ['input_tokens','output_tokens']):raise ValueError('usage')
 if u['output_tokens']!=0:raise ValueError('unexpected generated tokens')
 cost=u.get('cost')
 if type(cost) not in (float,int) or not math.isfinite(cost) or cost<0:raise ValueError('cost')
 if abs(cost-u['input_tokens']*RATES[arm]/1e6)>1e-8:raise ValueError('cost-rate mismatch')
 return choice,c,cost

def reserve(arm,payload,lane):
 if lane=='visual':return .29144 if arm=='gpt55' else 64000*RATES[arm]/1e6
 bound=len(json.dumps(payload,ensure_ascii=False).encode())+512
 if bound>8192:raise ValueError('short state bound')
 if arm=='drex':
  assert len(state_json(payload['state']).encode())+256<=8192
 return ((4096*2+160*8) if arm=='gpt41' else bound*RATES[arm])/1e6

def call(arm,payload,name,lane,labels):
 ledger_path=OUT/(lane+'-ledger.json');ledger=json.loads(ledger_path.read_text())
 if ledger.get('closed'):raise RuntimeError('closed ledger')
 prior=next((x for x in ledger['calls'] if x['name']==name),None)
 if prior:
  if prior['status']=='complete':return prior
  raise RuntimeError('duplicate unresolved dispatch')
 amount=reserve(arm,payload,lane)
 if ledger['spent_usd']+ledger['unknown_usd']+amount>CAPS[lane]:raise RuntimeError('hard cap')
 encoded=json.dumps(payload,ensure_ascii=False).encode();entry={'name':name,'arm':arm,'reserve_usd':amount,'status':'dispatched','request_sha256':hashlib.sha256(encoded).hexdigest(),'request_bytes':len(encoded)}
 ledger['calls'].append(entry);ledger['unknown_usd']+=amount;write(ledger_path,ledger)
 RAW.mkdir(parents=True,exist_ok=True,mode=0o700);(RAW/(name+'.request.json')).write_bytes(encoded)
 endpoint='https://openrouter.ai/api/alpha/decisions' if arm in MODELS else 'https://api.openai.com/v1/'+('responses' if arm=='gpt55' else 'chat/completions')
 key=os.environ['OPENROUTER_API_KEY' if arm in MODELS else 'OPENAI_API_KEY']
 req=urllib.request.Request(endpoint,data=encoded,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 start=time.monotonic()
 try:
  try:
   with urllib.request.urlopen(req,timeout=120) as r:response,status=r.read(),r.status
  except urllib.error.HTTPError as e:response,status=e.read(),e.code
 except Exception as e:
  entry.update(status='delivery_unknown',error_type=type(e).__name__,latency_ms=(time.monotonic()-start)*1000);write(ledger_path,ledger);raise RuntimeError('delivery unknown') from None
 entry.update(http_status=status,latency_ms=(time.monotonic()-start)*1000,response_bytes=len(response),response_sha256=hashlib.sha256(response).hexdigest())
 (RAW/(name+'.response.json')).write_bytes(response)
 raw=json.loads(response);entry.update(served_model=raw.get('model'),provider=raw.get('provider'),usage=raw.get('usage'))
 # Known provider usage settles cost even if semantic contract fails; failures without usage retain reserve.
 try:
  label,conf,cost=parse(arm,raw,labels)
  if cost>amount+1e-9:raise ValueError('reservation exceeded')
  entry.update(status='complete',label=label,confidence=conf,cost_usd=cost)
  ledger['unknown_usd']-=amount;ledger['spent_usd']+=cost
 except Exception as e:
  entry.update(status='contract_invalid' if status==200 else 'http_error',error_type=type(e).__name__)
  u=raw.get('usage',{});known=u.get('cost')
  if arm in MODELS and type(known) in (float,int) and math.isfinite(known) and 0<=known<=amount:
   entry['known_failed_cost_usd']=known;ledger['unknown_usd']-=amount;ledger['spent_usd']+=known
  write(ledger_path,ledger);return entry
 write(ledger_path,ledger);return entry

def preflight():
 OUT.mkdir(parents=True,exist_ok=True)
 review=json.loads((ROOT/'docs/evals/artifacts/jev-consistency-20260921/review.json').read_text());assert review['approved_fixture_sha256']==sha(ROOT/'benchmarks/jev-consistency/fixtures.json')
 eligibility=json.loads((ROOT/'docs/evals/evidence/063-decisions/image-eligibility.json').read_text())
 for r in eligibility['bindings']:
  for s in r['sources']:assert sha(ROOT/s['path'])==s['uri_sha256']
 write(OUT/'image-eligibility.json',eligibility)
 matrix=[{'id':f"r{rep}-{c['id']}",'gold':c['gold'],'requests':{a:body(a,c['input']) for a in [*MODELS,'gpt41']}} for rep in [1,2] for c in fixtures()]
 total=sum(reserve(a,r['requests'][a],'text') for r in matrix for a in [*MODELS,'gpt41'])+200*reserve('gpt41',matrix[0]['requests']['gpt41'],'text')
 write(OUT/'text-rendered.json',matrix)
 visual=[]
 for k in image.image_cases():
  payload=image_body(k,'gpt55');candidate=image_body(k,'clef')
  assert len(candidate['state'])==3
  sizes=[len(base64.b64decode(x['image_url']['url'].split(',',1)[1])) for x in candidate['state'] if isinstance(x,dict)]
  visual.append({'key':k,'request_sha256':hashlib.sha256(json.dumps(payload,ensure_ascii=False).encode()).hexdigest(),'request_bytes':len(json.dumps(payload).encode()),'decoded_image_bytes':sizes,'source_refs':next(r['sources'] for r in eligibility['bindings'] if r['key']==k),'clef_documented_image_admission':all(n<=4*1024*1024 for n in sizes) and sum(sizes)<=8*1024*1024})
 write(OUT/'image-topology.json',visual)
 sources={}
 for rel in ['benchmarks/jev-consistency/scout091_campaign.py','benchmarks/jev-consistency/decisions_campaign.py','benchmarks/jev-consistency/run.py','benchmarks/jev-consistency/fixtures.json','benchmarks/jev-consistency/detector.py','benchmarks/prompts/validate-page-level-crop.js','benchmarks/golden/crop-page-level-safety-repair-048-source-adjudicated.json','benchmarks/providers/openai_responses_model.py','benchmarks/scorers/crop_validation_scorer.py','scripts/run_with_doc_web_env.py','doc_web/env.py']:
  p=ROOT/rel;dest=OUT/'snapshots'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);sources[rel]=sha(p)
 proof={'base_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'sources':sources,'text_cases':20,'repeats':2,'source_documents':2,'text_full_reservation_usd':total,'visual_full_reservation_usd':22*.29144+22*64000*.19/1e6,'caps':CAPS,'concurrency':1,'sessions':'independent; no chain/cache/retries','judge':'none; finite maintained scorer and source review','fallback':'preserve explicit uncertain review; otherwise confidence<.8 real per-arm fresh serial GPT4.1','visual_order':['page-012-000','page-012-001','page-122-001','page-126-000','page-126-001','page-127-000'],'visual_stop':'confirmed unsafe accept stops arm; no downsample/OCR rescue','liquid_visual':'no eligible configured direct key; deferred','privacy':'synthetic text and explicitly owner-public source-bound22images. Provider retention/training unresolved; allowed on disclosed public/synthetic basis.','generated_rationale':'unqualified; finite verdict projection only','matrix_source':'Attempt048 source-adjudicated prompt/gold; Decisions063 eligibility manifest'}
 assert total<4 and proof['visual_full_reservation_usd']<8
 write(OUT/'preflight.json',proof)
 for lane in CAPS:
  p=OUT/(lane+'-ledger.json')
  if not p.exists():write(p,{'cap_usd':CAPS[lane],'spent_usd':0.,'unknown_usd':0.,'calls':[]})
 print(json.dumps({k:v for k,v in proof.items() if k!='sources'},indent=2))

def frozen():
 p=json.loads((OUT/'preflight.json').read_text())
 for name,digest in p['sources'].items():assert sha(ROOT/name)==digest,name

def qualify():
 frozen();rows={}
 for arm in MODELS:
  rows[arm]=call(arm,body(arm,fixtures()[0]['input']),'native-'+arm,'text',legacy.LABELS)
  print(arm,rows[arm]['status'],rows[arm].get('label'),flush=True)
 write(OUT/'qualification.json',rows)
 if any(x['status']=='complete' for x in rows.values()):
  r=call('gpt41',body('gpt41',fixtures()[0]['input']),'native-gpt41','text',legacy.LABELS);print('gpt41',r['status']);write(OUT/'control-qualification.json',r)

def text_run():
 frozen();q=json.loads((OUT/'qualification.json').read_text());arms=[a for a in MODELS if q[a]['status']=='complete'];rows=[]
 if not arms:return
 for rep in [1,2]:
  for c in fixtures():
   identity=f"r{rep}-{c['id']}";g=call('gpt41',body('gpt41',c['input']),identity+'-gpt41','text',legacy.LABELS)
   if g['status']!='complete':raise RuntimeError('control contract')
   rows.append(dict(g,id=identity,gold=c['gold'],arm='gpt41'))
   for arm in arms[:]:
    r=call(arm,body(arm,c['input']),identity+'-'+arm,'text',legacy.LABELS)
    if r['status']!='complete':arms.remove(arm);continue
    rows.append(dict(r,id=identity,gold=c['gold'],arm=arm))
    if r['label']!='uncertain' and r['confidence']<.8:
     f=call('gpt41',body('gpt41',c['input']),identity+'-'+arm+'-fallback','text',legacy.LABELS)
     if f['status']!='complete':raise RuntimeError('fallback contract')
     casc=dict(f,cost_usd=r['cost_usd']+f['cost_usd'],latency_ms=r['latency_ms']+f['latency_ms'],fallback=True)
    else:casc=dict(r,fallback=False)
    rows.append(dict(casc,id=identity,gold=c['gold'],arm=arm+'-cascade'))
   write(OUT/'text-results.json',rows);print(identity,flush=True)
 summary={}
 for arm in sorted({r['arm'] for r in rows}):
  rr=[r for r in rows if r['arm']==arm];summary[arm]=dict(legacy.metrics(rr),review_count=sum(x['label']=='uncertain' for x in rr),fallback_count=sum(x.get('fallback',False) for x in rr))
 write(OUT/'text-summary.json',summary)

def visual_run():
 frozen();gold=json.loads((ROOT/'benchmarks/golden/crop-page-level-safety-repair-048-source-adjudicated.json').read_text());print('gold keys',list(gold)[:3])
 # Caller chooses each exact case so source review and admission occur between sends.

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','qualify','text','image']);p.add_argument('--arm');p.add_argument('--key');a=p.parse_args()
 if a.mode=='preflight':return preflight()
 RAW.mkdir(parents=True,exist_ok=True,mode=0o700)
 with (RAW/'dispatch.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if a.mode=='qualify':return qualify()
  if a.mode=='text':return text_run()
  frozen();r=call(a.arm,image_body(a.key,a.arm),'image-'+a.key+'-'+a.arm,'visual',{'pass':'','fail':''});print(json.dumps(r,indent=2))
if __name__=='__main__':main()
