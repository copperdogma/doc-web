"""Scout092 force-fresh public/synthetic native owner comparison; no defaults."""
import base64, hashlib, io, json, os, subprocess, sys
from pathlib import Path
from types import SimpleNamespace
import httpx, yaml
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'benchmarks/providers'))
import argon_guard as guard
from doc_web.literal_fidelity import SourcePageReview
from modules.common.table_source_review import POLICY, SourceOnlyReader
from modules.common.literal_table_review import review_literal_tables
from modules.extract.ocr_ai_gpt51_v1.main import _resize_image_bytes, build_system_prompt
from benchmarks.scorers.image_crop_scorer import get_assert as crop_score
R=guard.RESULTS; E=ROOT/'docs/evals/evidence/071-argon'

def sha(b): return hashlib.sha256(b).hexdigest()
def save(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def google(model,system,text,image,mime='image/png',schema=None,stage=None):
    os.environ['ARGON_STAGE']=stage or 'unknown'; guard.install()
    config={'maxOutputTokens':32768 if model=='gemini-4-argon' else 16384}
    if model=='gemini-4-argon': config['thinkingConfig']={'thinkingLevel':'medium'}
    else: config['temperature']=0
    if schema: config.update(responseMimeType='application/json',responseJsonSchema=schema)
    body={'contents':[{'role':'user','parts':[{'text':text},{'inlineData':{'mimeType':mime,'data':base64.b64encode(image).decode()}}]}],'generationConfig':config}
    if system: body['systemInstruction']={'parts':[{'text':system}]}
    response=httpx.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',headers={'x-goog-api-key':os.environ['GEMINI_API_KEY']},json=body,timeout=1200)
    response.raise_for_status(); d=response.json(); c=d.get('candidates',[])
    assert d['modelVersion']==model and len(c)==1 and c[0]['finishReason']=='STOP' and d.get('usageMetadata')
    raw='\n'.join(p['text'] for p in c[0]['content']['parts'] if 'text' in p and not p.get('thought'))
    if schema:
        import jsonschema
        jsonschema.validate(json.loads(raw),schema)
    return raw,d

def table_reader(model,case):
    if model=='gpt-6-astra':
        os.environ['ARGON_STAGE']='table-'+case+'-control'; guard.install()
        return SourceOnlyReader(max_requests=1,budget_usd=1.5)
    def reader(path,requests):
        b=Path(path).read_bytes()
        with Image.open(path) as im: w,h=im.size
        raw,d=google(model,POLICY,f'Source image dimensions: {w} x {h} pixels. Read source tables; return JSON only.',b,schema=SourcePageReview.model_json_schema(),stage='table-'+case+'-candidate')
        requests.append({'requested_model':model,'served_model':d['modelVersion'],'response_id':d.get('responseId'),'status':'completed','usage':d['usageMetadata'],'raw_response':raw,'submitted_image_sha256':sha(b)})
        return SourcePageReview.model_validate_json(raw)
    return reader

def render_crop(key):
    image=(ROOT/f'benchmarks/input/source-pages-b64/{key}.b64.txt').read_text().strip()
    code="""const p=require(process.argv[1]); process.stdout.write(JSON.stringify(p({vars:JSON.parse(require('fs').readFileSync(0,'utf8')),provider:{id:"google:gemini-4-argon"}})))"""
    out=subprocess.check_output(['node','-e',code,str(ROOT/'benchmarks/prompts/crop-conservative-count.js')],input=json.dumps({'image':image}),text=True)
    return json.loads(out)
CROP_SCHEMA={'type':'object','properties':{'images':{'type':'array','items':{'type':'object','properties':{'description':{'type':'string'},'bbox':{'type':'array','items':{'type':'number'},'minItems':4,'maxItems':4}},'required':['description','bbox'],'additionalProperties':False}}},'required':['images'],'additionalProperties':False}

def preflight():
    E.mkdir(parents=True,exist_ok=True); R.mkdir(parents=True,exist_ok=True)
    cases=[]
    cfg=yaml.safe_load((ROOT/'benchmarks/tasks/gpt61-detector-full.yaml').read_text())
    keys=[t['vars']['golden_key'] for t in cfg['tests']]; assert len(keys)==13
    for key in keys:
        messages=render_crop(key); assert len(messages)==1 and len(messages[0]['parts'])==2
        assert 'normalized 0.0-1.0' in messages[0]['parts'][0]['text']
        cases.append({'key':key,'rendered_sha256':sha(json.dumps(messages).encode()),'message_count':1,'image_count':1})
    table=[]
    for case in ('native-positive','image-positive','ambiguity-negative'):
        prior=Path('/Users/cam/Documents/Projects/doc-web/output/runs')/('story244-'+case+'-v2')/'02_ocr_ai_gpt51_v1/pages_html.jsonl'
        assert prior.exists(),prior
        rows=[json.loads(l) for l in prior.read_text().splitlines()]; assert len(rows)==1
        source=ROOT/f'testdata/literal-table-fidelity/confirmation-v2/{case}/page.png'
        table.append({'case':case,'initial':str(prior),'initial_sha256':sha(prior.read_bytes()),'image_sha256':sha(source.read_bytes())})
        save(E/f'initial-{case}.json',rows[0])
    plan={'base_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'cap_usd':15,'candidate':'gemini-4-argon medium32768','controls':{'table':'gpt-6-astra medium8192 original','crop':'gemini-3-flash-preview temperature0 max16384 normalized','ocr':'gemini-3.7-flash maintained default medium max16384'},'cache':'force-fresh no subject reuse except frozen identical initial table OCR','concurrency':1,'judge':'independent source review plus deterministic owner assertions; optional capped Opus table rubric','session_grouping':'one independent native request per case','crop':cases,'tables':table,'schema_sha256':sha(json.dumps(SourcePageReview.model_json_schema(),sort_keys=True).encode()),'policy_sha256':sha(POLICY.encode()),'maximum_subject_reservations':6.83424+4.5+1.0,'operational_recovery_usd':2.0,'no_page_safety':True}
    save(E/'preflight.json',plan)
    if not (R/'ledger.json').exists(): save(R/'ledger.json',{'cap_usd':15,'spent_usd':0,'calls':[],'closed':False})
    print('offline preflight passed',len(cases),'crop keys,3 identical initial OCRs')

def probe():
    image=Image.new('RGB',(300,150),'white'); ImageDraw.Draw(image).text((30,30),'TEST',fill='black'); f=io.BytesIO();image.save(f,format='PNG'); b=f.getvalue()
    for name,schema,system,text in [('table',SourcePageReview.model_json_schema(),POLICY,'Source image dimensions: 300 x 150 pixels. Read source tables; return JSON only.'),('crop',CROP_SCHEMA,'','Find visible visual elements. Return normalized bounding boxes as images JSON.'),('ocr',None,'Read visible text exactly and return minimal HTML.','Transcribe this image.')]:
        raw,d=google('gemini-4-argon',system,text,b,schema=schema,stage='native-'+name)
        save(E/('native-'+name+'.json'),{'raw':raw,'served':d['modelVersion'],'finish':d['candidates'][0]['finishReason']}); print('qualified',name,flush=True)

def tables():
    from doc_web.literal_tables import compare_tables
    results=[]
    for case in ('native-positive','image-positive','ambiguity-negative'):
        initial=json.loads((E/f'initial-{case}.json').read_text()); source=ROOT/f'testdata/literal-table-fidelity/confirmation-v2/{case}/page.png'
        initial['image']=str(source); initial['source']=[]
        for model,label in [('gemini-4-argon','candidate'),('gpt-6-astra','control')]:
            out=R/f'table-{case}-{label}.jsonl'
            row=review_literal_tables([initial],out_path=out,run_id=f'argon-{case}-{label}',reader=table_reader(model,case))[0]
            report=json.loads(Path(row['literal_fidelity']['report_path']).read_text())
            golden=(source.parent/'golden.html').read_text()
            reviewed=report['tables'][0]['review'] if report['tables'] else {}
            quality=compare_tables(golden,reviewed.get('html',''))
            result={'case':case,'arm':label,'status':report['status'],'uncertainties':reviewed.get('uncertain_cells',[]),'literal_score':quality,'report':str(Path(row['literal_fidelity']['report_path']).relative_to(ROOT))}
            results.append(result); save(E/'table-results.json',results); print(case,label,report['status'],quality['pass'],flush=True)

def crops(mode):
    keys=[c['key'] for c in json.loads((E/'preflight.json').read_text())['crop']]
    if mode=='screen': keys=['Image011']
    results=[]
    for key in keys:
        msgs=render_crop(key); parts=msgs[0]['parts']; image=base64.b64decode(parts[1]['inlineData']['data']); mime=parts[1]['inlineData']['mimeType']
        for model,label in [('gemini-4-argon','candidate'),('gemini-3-flash-preview','control')]:
            raw,d=google(model,'',parts[0]['text'],image,mime,schema=CROP_SCHEMA if label=='candidate' else None,stage=f'crop-{mode}-{key}-{label}')
            score=crop_score(raw,{'vars':{'golden_key':key}})
            save(E/f'crop-{mode}-{key}-{label}.json',{'raw':raw,'score':score,'served':d['modelVersion']})
            results.append({'key':key,'arm':label,**score}); save(E/f'crop-{mode}-results.json',results); print(key,label,score,flush=True)
        if not results[-2]['pass']: print('STOP affected crop lane: source review required',flush=True); break

def install_ocr():
    from modules.common.google_client import GeminiVisionClient,_decode_data_uri
    def generate(self,model,system_prompt,user_text,image_data,temperature=0,max_tokens=4096):
        b,mime=_decode_data_uri(image_data)
        raw,d=google(model,system_prompt,user_text,b,mime,stage=os.environ['ARGON_STAGE'])
        u=d['usageMetadata']; usage=SimpleNamespace(prompt_token_count=u['promptTokenCount'],candidates_token_count=u.get('candidatesTokenCount',0),thoughts_token_count=u.get('thoughtsTokenCount',0),cached_content_token_count=u.get('cachedContentTokenCount',0))
        return raw,usage,d.get('responseId')
    GeminiVisionClient.generate_vision=generate

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='preflight': preflight()
    elif mode=='probe': probe()
    elif mode=='tables': tables()
    elif mode in ('screen','full'): crops(mode)
