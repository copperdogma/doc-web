"""Bounded native contracts before Promptfoo parity; complete raw custody below adapter."""
import base64,io,json,os,sys
from pathlib import Path
import httpx
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'benchmarks/providers'))
import mistral4_guard as guard
import mistral4_candidate as candidate
import openrouter_vision_chat as owner
stage=sys.argv[1]
img=Image.new('RGB',(32,32),'black')
if stage=='ocr':
 img=Image.new('RGB',(120,40),'white');ImageDraw.Draw(img).text((8,8),'TEST',fill='black')
out=io.BytesIO();img.save(out,format='PNG');uri='data:image/png;base64,'+base64.b64encode(out.getvalue()).decode()
text='Identify the black square as one illustration, bbox integers 0-1000.'
contract='crop_regions_integer';count=1
if stage=='safety':text='Compare these two identical black square images. Return the page-context verdict fields.';contract='page_context_validation';count=2
messages=[{'role':'user','content':[{'type':'text','text':text}]+[{'type':'image_url','image_url':{'url':uri}}]*count}]
if stage=='ocr':messages=[{'role':'system','content':'Read the visible source text exactly. Return minimal HTML.'},{'role':'user','content':[{'type':'text','text':'Transcribe this image.'},{'type':'image_url','image_url':{'url':uri}}]}]
config={'config':{'model':'mistralai/mistral-large-4-0','expected_served_provider':'Mistral','provider_route':'mistral','pin_provider':True,'require_parameters':True,'data_collection':None,'zdr':None,'output_contract':contract,'max_tokens':16384 if stage=='ocr' else 4096}}
body=candidate.body(json.dumps(messages),config)
if stage=='ocr':body.pop('response_format')
os.environ['MISTRAL_CASE']='native-'+stage;guard.install()
r=httpx.post('https://openrouter.ai/api/v1/chat/completions',headers={'Authorization':'Bearer '+os.environ['OPENROUTER_API_KEY']},json=body,timeout=180)
d=r.json();(guard.RESULTS/('native-'+stage+'.json')).write_text(json.dumps(d,indent=2));print(json.dumps({'http':r.status_code,'model':d.get('model'),'provider':d.get('provider'),'finish':d.get('choices',[{}])[0].get('finish_reason'),'usage':d.get('usage'),'output':owner._output(d)}))
assert r.status_code==200 and d['model']=='mistralai/mistral-large-4-0' and d['provider']=='Mistral' and d['choices'][0]['finish_reason']=='stop';owner._usage(d)
if stage!='ocr':assert not owner._contract_error(owner._output(d),contract)
