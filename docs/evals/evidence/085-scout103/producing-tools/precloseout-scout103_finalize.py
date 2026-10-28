"""Offline summary of frozen Scout103 receipts; no provider dispatch."""
import hashlib
import json
import statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'docs/evals/evidence/085-scout103'
R=ROOT/'benchmarks/results/scout103-20261026'
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
reviews=json.loads((E/'source-review.json').read_text());reviews['crop-Image126']={'status':'pass','finding':'Both original monument/plaque photographs fully retained, preserving inscriptions and surrounding photograph content. No smaller central-plaque reinterpretation. Source overlay inspected.'};save(E/'source-review.json',reviews)
ledger=json.loads((R/'ledger.json').read_text());assert all(c.get('cost_usd') is not None for c in ledger['calls']);ledger['closed']=True;save(R/'ledger.json',ledger);save(E/'ledger.json',ledger)
keys=[x['key'] for x in json.loads((E/'preflight.json').read_text())['crop']]
rows=[]
for key in keys:
 for arm in ['candidate','control']:
  d=json.loads((E/f'crop-screen-{key}-{arm}.json').read_text());rows.append({'key':key,'arm':arm,**d})
save(E/'crop-results-all.json',rows)
summary={'cap_usd':12,'spent_usd':ledger['spent_usd'],'unknown_exposure_usd':0,'dispatches':len(ledger['calls']),'subjects_fresh':True,'judge_cost_usd':0,'crop':{},'tables':{'cases':1,'candidate_exact_cells':22,'control_exact_cells':23,'clear_cells_tested':23,'candidate_clear_holds':1,'candidate_accepted_wrong_cells':0,'later_clear_cells_unmeasured':13,'genuine_ambiguity_cells_unmeasured':2},'ocr':{'candidate_barney_ratio':.96527,'threshold':.99,'control_requested':'gemini-3.7-flash','control_served':'gemini-3.8-flash','control_quarantined':True,'fresh_relative_claim':False},'scope_holds':['Image000 undecorated cover extent unresolved; integral decorated content retained','both-arm crop scoring uses golden-assisted axis normalization; not native coordinate parity','Attempt083 production grouping policy hold unchanged; no actual consumer qualification','handwriting production OpenAI integration not qualified by eval-only shim'], 'credential_custody':'existing owner credentials via normal DOC_WEB_ENV_FILE primary override; no copy/injection/cleanup required'}
for arm in ['candidate','control']:
 rr=[x for x in rows if x['arm']==arm];calls=[x for x in ledger['calls'] if x['stage'].startswith('crop-') and arm in x['stage']]
 summary['crop'][arm]={'cases':len(rr),'tolerant_passes':sum(x['score']['pass'] for x in rr),'mean_score':statistics.mean(x['score']['score'] for x in rr),'subject_cost_usd':sum(x['cost_usd'] for x in calls),'native_http_mean_ms':statistics.mean(x['latency_ms'] for x in calls),'native_http_median_ms':statistics.median(x['latency_ms'] for x in calls),'raw_box_axis_oracle':'maintained scorer unchanged; per-case normalization records retained'}
summary['crop']['source_review']={'candidate_integral_content_clear':12,'cover_extent_unresolved':1,'definite_integral_amputations':0,'full_source_acceptance':False}
for kind in ['native','table','ocr']:
 cc=[x for x in ledger['calls'] if x['stage'].startswith(kind+'-')];summary[kind+'_cost_usd']=sum(x['cost_usd'] for x in cc)
save(E/'summary.json',summary)
print(json.dumps(summary,indent=2))
