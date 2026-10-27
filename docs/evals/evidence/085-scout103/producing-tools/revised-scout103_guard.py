"""Scout103 direct-provider serialized hard-cap ledger; no credential storage."""
import fcntl
import hashlib
import json
import os
import re
import time
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[2]
RESULTS=ROOT/'benchmarks/results/scout103-20261026'
E=ROOT/'docs/evals/evidence/085-scout103'
PRICES={'gpt-6.1-terra':(1,.05,1.25,5),'gpt-6-astra':(10,1,12.5,50),'gemini-3-flash-preview':(.5,.05,.5,3),'gemini-3.7-flash':(.75,.075,.75,3.75),'gemini-3.8-flash':(.75,.075,.75,3.75)}
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');t.replace(p)
def sha(b):return hashlib.sha256(b).hexdigest()
def send(original,client,request,**kwargs):
 if request.method!='POST':return original(client,request,**kwargs)
 google=request.url.host=='generativelanguage.googleapis.com'
 if request.url.host not in ('generativelanguage.googleapis.com','api.openai.com'):raise RuntimeError('unapproved endpoint')
 b=json.loads(request.content)
 model=request.url.path.split('/models/')[1].split(':')[0] if google else b['model']
 if model not in PRICES or model=='gemini-3.8-flash':raise RuntimeError('unapproved requested model')
 stage=os.environ['SCOUT103_STAGE']
 maximum=b['generationConfig']['maxOutputTokens'] if google else b['max_output_tokens']
 if not google and (b.get('store') is not False or b.get('service_tier')!='default'):raise RuntimeError('storage/service contract')
 if model=='gpt-6.1-terra':
  crop='crop' in stage
  assert b['reasoning']['effort']==('medium' if crop else 'high')
  assert maximum==(16384 if crop else 32768)
 prices=PRICES[model]
 count=json.dumps(b).count('"input_image"')+json.dumps(b).count('"inlineData"')
 bound=100000*count+6000 if model=='gpt-6.1-terra' else 20000*count+6000
 reserve=max(1.5 if model=='gpt-6-astra' else 0,(bound*max(prices[:3])+maximum*prices[3])/1e6)
 RESULTS.mkdir(parents=True,exist_ok=True)
 with (RESULTS/'ledger.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  p=RESULTS/'ledger.json';ledger=json.loads(p.read_text())
  if stage.startswith('crop-'):
   key=re.search(r'Image[0-9]+',stage)
   for prior in ledger['calls']:
    prior_key=re.search(r'Image[0-9]+',prior['stage'])
    if prior['stage'].startswith('crop-') and prior_key and key and prior_key[0]!=key[0]:
     reviews=json.loads((E/'source-review.json').read_text()) if (E/'source-review.json').exists() else {}
     if reviews.get('crop-'+prior_key[0],{}).get('status') not in ('pass','decorated-content-pass'):raise RuntimeError('manual source review barrier')
  if ledger['closed'] or ledger['spent_usd']+sum(x['reserved_usd'] for x in ledger['calls'] if x.get('cost_usd') is None)+reserve>12:raise RuntimeError('hard12USD cap')
  if any(x['stage']==stage for x in ledger['calls']):raise RuntimeError('duplicate stage')
  n=len(ledger['calls'])+1;raw=json.dumps(b,sort_keys=True).encode();req=RESULTS/f'request-{n:03}.json';res=RESULTS/f'response-{n:03}.json';req.write_bytes(raw)
  rec={'stage':stage,'model':model,'reserved_usd':reserve,'cost_usd':None,'request':str(req.relative_to(ROOT)),'request_sha256':sha(raw)};ledger['calls'].append(rec);save(p,ledger)
  start=time.monotonic()
  try:r=original(client,request,**kwargs);r.read()
  except Exception as exc:rec['exception']=type(exc).__name__;save(p,ledger);raise
  res.write_bytes(r.content);rec.update(response=str(res.relative_to(ROOT)),response_sha256=sha(r.content),status_code=r.status_code,latency_ms=round((time.monotonic()-start)*1000));d=r.json()
  u=d.get('usageMetadata',{}) if google else d.get('usage',{})
  try:
   served=d.get('modelVersion',d.get('model'));actual_prices=PRICES[served]
   if google:
    inp=u['promptTokenCount'];out=u.get('candidatesTokenCount',0)+u.get('thoughtsTokenCount',0);cached=u.get('cachedContentTokenCount',0);write=0
   else:
    inp=u['input_tokens'];out=u['output_tokens'];details=u.get('input_tokens_details',{});cached=details.get('cached_tokens',0);write=details.get('cache_write_tokens',0)
   cost=((inp-cached-write)*actual_prices[0]+cached*actual_prices[1]+write*actual_prices[2]+out*actual_prices[3])/1e6
   assert type(inp) is int and type(out) is int and inp>=0 and out>=0 and cost>=0
   rec.update(cost_usd=cost,usage=u,served_model=served,provider='Google' if google else 'OpenAI');ledger['spent_usd']+=cost
   if inp>bound or out>maximum or cost>reserve:rec['bound_violation']=True;ledger['closed']=True
  except (KeyError,TypeError,AssertionError):
   rec['billing_unresolved']=True
   if r.status_code in (400,401,402,403,404,429) and not u:rec.update(cost_usd=0,billing_unresolved=False,pre_inference_rejection=True)
  save(p,ledger);return r

def install():
 if getattr(httpx.Client.send,'_scout103',False):return
 original=httpx.Client.send
 def wrapped(c,r,**k):return send(original,c,r,**k)
 wrapped._scout103=True;httpx.Client.send=wrapped
