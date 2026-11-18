"""Frozen public Doc Web Scout116 native requests and progressive receipts."""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time

import httpx
import jsonschema
from PIL import Image
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from benchmarks.scripts.hydrogen_reading import CROP_SCHEMA, render_crop
from benchmarks.providers.historical_literal_readers.table_source_review import astra_request

E = ROOT / "docs/evals/evidence/097-astra62"
RAW = ROOT / "output/fixtures/scout116-astra62"
OLD = ROOT / "docs/evals/evidence/094-hydrogen/rendered"
CANDIDATE = "gpt-6.2-astra"
CAPS = {"ocr": (12, 4, 106000), "table": (10, 5, 26000), "crop": (42, 16, 106000)}
# All rates are Standard. Include possible OpenAI short cache writes in reserves.
RATES = {
    CANDIDATE: (.0 + 8, 40, .40, 10),
    "gpt-6-astra": (10, 50, 1, 12.5),
    "gemini-4-hydrogen": (1.5, 7.5, .075, 1.5),
    "gemini-3.8-flash": (.75, 3.75, .075, .75),
    "gemini-3-flash-preview": (.5, 3, .05, .5),
}
OA = "https://api.openai.com/v1/responses"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def openai_body(text, img, system="", schema=None):
    body = {
        "model": CANDIDATE,
        "store": False,
        "service_tier": "default",
        "max_output_tokens": 32768,
        "reasoning": {"effort": "high"},
        "input": [
            {"role": "user", "content": [
                {"type": "input_text", "text": text},
                {"type": "input_image", "detail": "original",
                 "image_url": f"data:{img['mimeType']};base64,{img['data']}"},
            ]}
        ],
    }
    if system:
        body["input"].insert(0, {"role":"system","content":[{"type":"input_text","text":system}]})
    if schema:
        body["text"] = {"format":{"type":"json_schema","strict":True,"name":"images","schema":schema}}
    return body


def freeze():
    if E.exists() or RAW.exists():
        raise RuntimeError("Fresh run identity required")
    RAW.mkdir(parents=True, mode=0o700)
    E.mkdir(parents=True)
    matrix = {}
    def add(lane, name, model, body):
        file = RAW / (name + ".request.json")
        write(file, body)
        if model.startswith("gpt"):
            image_uri = body["input"][-1]["content"][-1]["image_url"]
            image_data = base64.b64decode(image_uri.split(",", 1)[1])
        else:
            image_data = base64.b64decode(body["contents"][0]["parts"][1]["inlineData"]["data"])
        with Image.open(io.BytesIO(image_data)) as image:
            dimensions = list(image.size)
        # Google media tiling and framing are covered conservatively by 26K.
        matrix[name] = {
            "lane":lane, "model":model, "request_sha256":digest(file),
            "body_path":str(file.relative_to(ROOT)), "independent":True,
            "image_dimensions":dimensions, "image_sha256":hashlib.sha256(image_data).hexdigest(),
        }
    for case in ("barney", "alverson"):
        h = json.loads((OLD / f"ocr-{case}-candidate.json").read_text())
        g = json.loads((OLD / f"ocr-{case}-control.json").read_text())
        parts = h["contents"][0]["parts"]
        add("ocr", f"ocr-{case}-astra62", CANDIDATE,
            openai_body(parts[0]["text"], parts[1]["inlineData"], h["systemInstruction"]["parts"][0]["text"]))
        add("ocr", f"ocr-{case}-hydrogen","gemini-4-hydrogen",h)
        add("ocr", f"ocr-{case}-gemini38","gemini-3.8-flash",g)
    for case in ("image-positive", "native-positive", "ambiguity-negative"):
        path = ROOT / "testdata/literal-table-fidelity/confirmation-v2" / case / "page.png"
        ctrl = astra_request(path)
        add("table",f"table-{case}-astra","gpt-6-astra",ctrl)
        add("table",f"table-{case}-astra62",CANDIDATE,
            {**ctrl,"model":CANDIDATE,"max_output_tokens":32768,"reasoning":{"effort":"high"}})
    task = yaml.safe_load((ROOT / "benchmarks/tasks/image-crop-extraction.yaml").read_text())
    cases = [x["vars"]["golden_key"] for x in task["tests"]]
    assert len(cases)==13 and "Image011" in cases and "Image001" in cases
    for case in ["Image011","Image001"]+[c for c in cases if c not in ["Image011","Image001"]]:
        parts = render_crop(case)[0]["parts"]
        add("crop",f"crop-{case}-astra62",CANDIDATE,openai_body(parts[0]["text"],parts[1]["inlineData"],schema=CROP_SCHEMA))
        ctrl = {"contents":[{"role":"user","parts":parts}],"generationConfig":{"maxOutputTokens":16384,"temperature":0}}
        add("crop",f"crop-{case}-gemini","gemini-3-flash-preview",ctrl)
    write(E / "preflight.json", {"matrix":matrix,"caps":CAPS,"base":"56564d95cd2cf9ce498aaaca84537a64b1e89f31",
        "source":"Attempt094 LOC Barney/Alverson public, authored confirmation-v2, public Onward registered crops",
        "producer_sha256":digest(Path(__file__)), "concurrency":1, "judge":None, "subject_cache":False})
    write(E / "ledger.json", [])


def unpack(d, model, google, schema):
    if google:
        from benchmarks.scripts.hydrogen_native import parse
        raw = parse(d,model,schema)
        usage = d["usageMetadata"]
        return raw, usage["promptTokenCount"], usage["candidatesTokenCount"]+usage.get("thoughtsTokenCount",0), usage.get("cachedContentTokenCount",0), usage.get("thoughtsTokenCount",0)
    if d.get("model")!=model or d.get("status")!="completed" or d.get("error") or d.get("incomplete_details") or d.get("service_tier")!="default":
        raise ValueError("Native identity, terminal state or tier invalid")
    messages = [i for i in d["output"] if i.get("type")=="message"]
    if len(messages)!=1 or messages[0].get("status")!="completed" or messages[0].get("role")!="assistant":
        raise ValueError("No complete unique final answer")
    item, = messages[0]["content"]
    if item.get("type")!="output_text" or not item.get("text","").strip():
        raise ValueError("Unexpected final content")
    raw = item["text"]
    if schema:
        jsonschema.validate(json.loads(raw),schema)
    usage=d["usage"]
    return raw, usage["input_tokens"],usage["output_tokens"],usage.get("input_tokens_details",{}).get("cached_tokens",0),usage.get("output_tokens_details",{}).get("reasoning_tokens",0)


def send(name, recovery=False):
    matrix=json.loads((E/"preflight.json").read_text())["matrix"]
    row=matrix[name]
    lane,model=row["lane"],row["model"]
    cap,max_candidate,max_input=CAPS[lane]
    ledger_path=E/"ledger.json"
    ledger=json.loads(ledger_path.read_text())
    prior=[x for x in ledger if x["lane"]==lane]
    if any(x["name"]==name for x in prior):
        if not recovery or any(x["recovery"] for x in prior) or any(x["state"]=="valid" and x["name"]==name for x in prior):
            raise RuntimeError("Repeated arm is not admissible")
    elif recovery:
        raise RuntimeError("No prior attempt to recover")
    if model==CANDIDATE and sum(x["model"]==CANDIDATE for x in prior)>=max_candidate:
        raise RuntimeError("Candidate request cap")
    body_path=ROOT/row["body_path"]
    if digest(body_path)!=row["request_sha256"]:
        raise RuntimeError("Frozen payload changed")
    body=json.loads(body_path.read_bytes())
    google=model.startswith("gemini")
    if google:
        headers={"x-goog-api-key":os.environ["GEMINI_API_KEY"]}
        endpoint=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        input_limit=26000
        output=body["generationConfig"]["maxOutputTokens"]
        # Google max output is a visible-token limit for some control routes.
        reserve_output=output+32768
        schema=body["generationConfig"].get("responseJsonSchema")
    else:
        headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"]}
        endpoint=OA
        count={k:v for k,v in body.items() if k in {"model","input","text","reasoning"}}
        r=httpx.post(OA+"/input_tokens",headers=headers,json=count,timeout=35)
        if r.status_code!=200:
            write(E/f"{name}-count-stop.json",{"status":r.status_code,"error_code":r.json().get("error",{}).get("code"),"inferences":0})
            raise RuntimeError(f"Input count rejected: HTTP {r.status_code}")
        input_limit=r.json()["input_tokens"]
        if not 0<input_limit<=max_input:
            raise RuntimeError("Exact input count exceeds approved bound")
        output=body["max_output_tokens"]
        reserve_output=output
        schema=body.get("text",{}).get("format",{}).get("schema")
    i_price,o_price,c_price,write_price=RATES[model]
    reserve=(input_limit*write_price+reserve_output*o_price)/1e6
    if sum(x.get("exposure",x["reserve"]) for x in prior)+reserve>cap:
        raise RuntimeError("Cannot reserve request within hard lane cap")
    suffix="-recovery" if recovery else ""
    receipt={"name":name,"lane":lane,"model":model,"reserve":reserve,"state":"reserved","recovery":recovery,"input_bound":input_limit,"request_sha256":row["request_sha256"]}
    ledger.append(receipt)
    write(ledger_path,ledger)
    started=time.monotonic()
    try:
        response=httpx.post(endpoint,headers=headers,content=body_path.read_bytes(),timeout=230)
        # Preserve native bytes before status, parsing or scorer decisions.
        path=RAW/(name+suffix+".response.json")
        with path.open("xb") as f:
            f.write(response.content)
        path.chmod(0o600)
        receipt.update(http=response.status_code, raw_path=str(path.relative_to(ROOT)),raw_sha256=digest(path),raw_bytes=path.stat().st_size)
        if response.status_code!=200:
            receipt["state"]="http-error"
            receipt["error_code"]=response.json().get("error",{}).get("code")
            return
        d=response.json()
        raw,inp,out,cached,thoughts=unpack(d,model,google,schema)
        if any(type(n) is not int or n<0 for n in [inp,out,cached,thoughts]) or inp>input_limit or out>reserve_output or cached>inp or thoughts>out:
            raise ValueError("Invalid or over-reservation usage")
        cost=((inp-cached)*i_price+out*o_price+cached*c_price)/1e6
        # Track reported cache writes separately if the endpoint provides them.
        write_count=d.get("usage",{}).get("input_tokens_details",{}).get("cache_write_tokens")
        if write_count is not None:
            if type(write_count) is not int or not 0<=write_count<=inp-cached:
                raise ValueError("Invalid cache write count")
            cost+=write_count*(write_price-i_price)/1e6
        exposure=cost if google or write_count is not None else ((inp-cached)*write_price+cached*c_price+out*o_price)/1e6
        receipt.update(state="valid",usage={"input":inp,"output":out,"cached_input":cached,"thinking":thoughts,"cache_write":write_count},cost_estimate=cost,exposure=exposure)
        write(E/(name+suffix+".answer.json"),{"raw":raw,"model":model,"native_sha256":receipt["raw_sha256"]})
    except (httpx.HTTPError, ValueError, KeyError, jsonschema.ValidationError) as exc:
        receipt.update(state="invalid-or-unsettled", error_type=type(exc).__name__)
    finally:
        receipt["elapsed_seconds"]=time.monotonic()-started
        write(ledger_path,ledger)
        print(json.dumps(receipt),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=["freeze","send"])
    parser.add_argument("name",nargs="?")
    parser.add_argument("--recovery",action="store_true")
    args=parser.parse_args()
    freeze() if args.command=="freeze" else send(args.name,args.recovery)
