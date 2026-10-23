"""GET-only generation identity/cost custody; no secret persisted."""
import sys,os,json
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'benchmarks/providers'));import scout096_guard as g
l=json.loads((g.RESULTS/'ledger.json').read_text());out=[]
for x in l['calls']:
 p=g.ROOT/x.get('response','')
 if not p.is_file():continue
 d=json.loads(p.read_text());ident=d.get('id','')
 if not ident.startswith('gen-'):continue
 r=httpx.get('https://openrouter.ai/api/v1/generation',params={'id':ident},headers={'Authorization':'Bearer '+os.environ['OPENROUTER_API_KEY']},timeout=30)
 data=r.json();g.save(g.RESULTS/('generation-'+str(x['stage'])+'.json'),data)
 out.append({'stage':x['stage'],'status':r.status_code,'data':data})
g.save(g.E/'generation-receipts.json',out);print('GET receipts',len(out))
