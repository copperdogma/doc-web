"""Scout117 exact-input, independently budgeted Doc Web owner evaluation."""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

import httpx
from PIL import Image

import scout116_doc_web as owner
from scout116_doc_web import ROOT, OLD, astra_request, digest, openai_body, write
from scout116_doc_web_score import score_ocr, score_table
from doc_web.literal_fidelity import SourcePageReview
from doc_web.literal_tables import compare_tables
from modules.common.openai_crop_vision import DETECTOR_RESPONSE_FORMAT

E = ROOT / "docs/evals/evidence/098-sol62"
RAW = ROOT / "output/fixtures/scout117-sol62"
CANDIDATE = "gpt-6.2-sol"
CAPS = {"ocr": (4,4,106000), "table": (4,5,26000), "crop": (12,16,106000)}
owner.E, owner.RAW, owner.CANDIDATE, owner.CAPS = E, RAW, CANDIDATE, CAPS
owner.RATES[CANDIDATE] = (2,10,.1,2.5)
PUBLIC = ROOT / "testdata/literal-table-fidelity/confirmation-v2"


def load(path):
    return json.loads(path.read_bytes())


def freeze():
    E.mkdir(parents=True,exist_ok=False)
    RAW.mkdir(parents=True,mode=0o700,exist_ok=False)
    matrix = {}
    def add(lane, name, body, golden=None):
        path=RAW/(name+".request.json")
        write(path,body)
        is_google="contents" in body
        image=body["contents"][0]["parts"][1]["inlineData"]["data"] if is_google else body["input"][-1]["content"][-1]["image_url"].split(",",1)[1]
        source=base64.b64decode(image)
        row={"lane":lane,"model":body.get("model") or {"gemini38":"gemini-3.8-flash","hydrogen":"gemini-4-hydrogen"}[name.rsplit("-",1)[1]],
             "body_path":str(path.relative_to(ROOT)),"request_sha256":digest(path),
             "image_dimensions":list(Image.open(io.BytesIO(source)).size),"image_sha256":hashlib.sha256(source).hexdigest()}
        if golden:
            row.update(golden=str(golden.relative_to(ROOT)),golden_sha256=digest(golden))
        matrix[name]=row
    historic=load(OLD/"runtime-12-candidate-detector-4.json")
    parts=historic["contents"][0]["parts"]
    body=openai_body(parts[0]["text"],parts[1]["inlineData"],historic["systemInstruction"]["parts"][0]["text"])
    body["text"]={"format":DETECTOR_RESPONSE_FORMAT}
    add("crop","crop-assisted-Image011-sol62",body)
    for case in ("barney","alverson"):
        h=load(OLD/f"ocr-{case}-candidate.json")
        g=load(OLD/f"ocr-{case}-control.json")
        parts=h["contents"][0]["parts"]
        gold=ROOT/f"testdata/handwritten-notes-{case}-real.txt"
        add("ocr",f"ocr-{case}-sol62", openai_body(parts[0]["text"],parts[1]["inlineData"],h["systemInstruction"]["parts"][0]["text"]),gold)
        add("ocr",f"ocr-{case}-hydrogen",h,gold)
        add("ocr",f"ocr-{case}-gemini38",g,gold)
    held=E/"heldout-table"
    spec=E/"heldout-table.source.json"
    write(spec,{"title":"Independent greenhouse tray register","font":"Courier","widths":[155,115,116,156],
        "rows":[[{"text":s,"header":True} for s in ["Zone","Tag","Trays","Treatment"]],
            [{"text":"Bench A","rowspan":2},{"text":"T4-N7"},{"text":"0"},{"text":"re-check"}],
            [{"text":"T4-M7"},{"text":""},{"text":"Recheck"}],
            [{"text":"East"},{"text":"K3-X2"},{"text":"-"},{"text":"shade cloth"}],
            [{"text":"West"},{"text":"k3-x2"},{"text":"+2"},{"text":"shade-cloth"}],
            [{"text":"Log empty trays before noon.","colspan":4}]]})
    subprocess.run([sys.executable,"testdata/generate_literal_table_fixtures.py","--source",str(spec),"--out",str(held)],cwd=ROOT,check=True)
    for case in ["image-positive","native-positive","ambiguity-negative","heldout"]:
        folder=held if case=="heldout" else PUBLIC/case
        control=astra_request(folder/"page.png")
        add("table",f"table-{case}-sol62",{**control,"model":CANDIDATE,"max_output_tokens":32768},folder/"golden.html")
        add("table",f"table-{case}-astra",control,folder/"golden.html")
    scripts=["benchmarks/scripts/scout117_doc_web.py","benchmarks/scripts/scout116_doc_web.py","benchmarks/scripts/scout116_doc_web_score.py","benchmarks/scripts/hydrogen_native.py","modules/common/table_source_review.py","modules/common/openai_crop_vision.py","doc_web/literal_tables.py","benchmarks/scorers/handwritten_notes_transcription.py","testdata/generate_literal_table_fixtures.py"]
    write(E/"preflight.json",{"base":subprocess.check_output(["git","rev-parse","HEAD"],text=True,cwd=ROOT).strip(),"matrix":matrix,"caps":CAPS,"producer_hashes":{s:digest(ROOT/s) for s in scripts},"concurrency":1,"judge":None,"subject_cache":False,"service":"Standard","fresh":True,"heldout_source":digest(spec)})
    write(E/"ledger.json",[])


def admission():
    pre=load(E/"preflight.json")
    results={}
    path=E/"admission.json"
    if path.exists():
        results=load(path)
    for name,row in pre["matrix"].items():
        if name in results:
            continue
        body=load(ROOT/row["body_path"])
        model=row["model"]
        assert digest(ROOT/row["body_path"])==row["request_sha256"]
        if model.startswith("gpt"):
            headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"]}
            count={k:v for k,v in body.items() if k in ("model","input","text","reasoning")}
            response=httpx.post(owner.OA+"/input_tokens",headers=headers,json=count,timeout=90)
            key="input_tokens"
        else:
            url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:countTokens"
            headers={"x-goog-api-key":os.environ["GEMINI_API_KEY"]}
            response=httpx.post(url,headers=headers,json={"generateContentRequest":{"model":"models/"+model,**body}},timeout=90)
            key="totalTokens"
        data=response.json()
        result={"http":response.status_code,"count":data.get(key),"request_sha256":row["request_sha256"]}
        if response.status_code!=200:
            error=data.get("error",{})
            result["error"]={k:error.get(k) for k in ("code","type","param","message")}
        results[name]=result
        write(path,results)
        print(name,result,flush=True)


def access():
    model=CANDIDATE
    res=httpx.get("https://api.openai.com/v1/models/"+model,headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"]},timeout=45)
    data=res.json()
    result={"http":res.status_code,"id":data.get("id"),"owner":data.get("owned_by"),"openai_owner_present":bool(os.environ.get("DOC_WEB_OPENAI_API_KEY")),"gemini_owner_present":bool(os.environ.get("DOC_WEB_GEMINI_API_KEY"))}
    write(E/"access.json",result)
    print(result)
    assert res.status_code==200 and data["id"]==model


def score(name):
    raw=load(E/(name+".answer.json"))["raw"]
    lane,rest=name.split("-",1)
    case,arm=rest.rsplit("-",1)
    if lane=="ocr":
        result=score_ocr(case,raw)
    elif case=="heldout":
        review=SourcePageReview.model_validate_json(raw)
        result=compare_tables((E/"heldout-table/golden.html").read_text(),"".join(t.html for t in review.tables))
        result.update(source_table_count=review.source_table_count,uncertainties=[[c.model_dump() for c in t.uncertain_cells] for t in review.tables])
    else:
        result=score_table(case,raw)
    write(E/(name+".score.json"),result)
    print({k:v for k,v in result.items() if k!="recognized_text"})


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("op",choices=["freeze","access","admission","send","score"])
    parser.add_argument("name",nargs="?")
    args=parser.parse_args()
    if args.op=="send":
        assert load(E/"reservation.json")["admitted"][args.name.split("-")[0]]
        assert load(E/"admission.json")[args.name]["http"]==200
        owner.send(args.name)
    elif args.op=="score":
        score(args.name)
    else:
        globals()[args.op]()
