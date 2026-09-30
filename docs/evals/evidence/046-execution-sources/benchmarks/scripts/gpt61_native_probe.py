"""Small native OpenAI Responses probes for the selected public/synthetic campaign."""
import base64
import io
import json
import os
import sys
from pathlib import Path

import httpx
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'benchmarks/providers'))
import gpt61_guard as guard
import openai_responses_model as owner


def generated_uri():
    image=Image.new('RGB',(32,32),'white')
    ImageDraw.Draw(image).rectangle([8,8,23,23],fill='black')
    out=io.BytesIO();image.save(out,format='PNG')
    return 'data:image/png;base64,'+base64.b64encode(out.getvalue()).decode()


def call(body):
    guard.install()
    response=httpx.post('https://api.openai.com/v1/responses',
       headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY'],'Content-Type':'application/json'},
       json=body,timeout=180)
    data=response.json()
    summary={'status_code':response.status_code,'id':data.get('id'),'model':data.get('model'),
             'status':data.get('status'),'incomplete_details':data.get('incomplete_details'),
             'usage':data.get('usage'),'output_text_len':len(owner._extract_output_text(data))}
    print(json.dumps(summary))
    if response.status_code!=200 or data.get('model')!='gpt-6.1-sol' or data.get('status')!='completed' or data.get('incomplete_details') is not None or not data.get('usage'):
        raise RuntimeError('native access/terminal contract failed')
    return data


def main():
    stage=sys.argv[1]
    uri=generated_uri()
    if stage=='catalog':
        response=httpx.get('https://api.openai.com/v1/models/gpt-6.1-sol',
          headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY']},timeout=30)
        data=response.json()
        print(json.dumps({'status_code':response.status_code,'id':data.get('id'),'object':data.get('object')}))
        if response.status_code!=200 or data.get('id')!='gpt-6.1-sol':
            raise RuntimeError('catalog access unavailable')
        return
    if stage=='detector':
        prompt=json.dumps([{'role':'user','content':[{'type':'input_text','text':'Find the one black square. Return its bounding box as integers 0-1000.'}, {'type':'input_image','image_url':uri}]}])
        body=owner._build_body(prompt,{'config':{'model':'gpt-6.1-sol','reasoning_effort':'low','output_contract':'crop_regions_integer','max_output_tokens':4096}})
        data=call(body)
        error=owner._contract_error(owner._extract_output_text(data),'crop_regions_integer')
        if error: raise RuntimeError(error)
        return
    if stage=='page':
        prompt=json.dumps([{'role':'user','content':[{'type':'input_text','text':'Compare these two identical synthetic square images. Return page-context verdict JSON.'},{'type':'input_image','image_url':uri},{'type':'input_image','image_url':uri}]}])
        body=owner._build_body(prompt,{'config':{'model':'gpt-6.1-sol','reasoning_effort':'low','output_contract':'page_context_validation','max_output_tokens':4096}})
        data=call(body)
        error=owner._contract_error(owner._extract_output_text(data),'page_context_validation')
        if error: raise RuntimeError(error)
        return
    if stage=='ocr':
        body={'model':'gpt-6.1-sol','input':[{'role':'system','content':[{'type':'input_text','text':'Read visible text exactly and return only minimal HTML.'}]},{'role':'user','content':[{'type':'input_text','text':'Read the text in this image.'},{'type':'input_image','image_url':uri}]}],
              'reasoning':{'effort':'low'},'max_output_tokens':16384,'store':False}
        call(body)
        return
    raise ValueError(stage)

if __name__=='__main__':main()
