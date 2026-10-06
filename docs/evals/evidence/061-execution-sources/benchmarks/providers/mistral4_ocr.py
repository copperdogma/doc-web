"""Eval-only OCR transport preserving owner system/user/image bytes."""
import json,os,sys
from pathlib import Path
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parent))
import mistral4_guard as guard
import openrouter_vision_chat as owner

def generate_vision(model,system,user,image,maximum):
    guard.install()
    body={"model":model,"messages":[{"role":"system","content":system},{"role":"user","content":[{"type":"text","text":user},{"type":"image_url","image_url":{"url":image}}]}],"max_tokens":maximum,"provider":{"order":["mistral"],"allow_fallbacks":False,"require_parameters":True,"max_price":{"prompt":0.68,"completion":2.09}}}
    r=httpx.post("https://openrouter.ai/api/v1/chat/completions",headers={"Authorization":"Bearer "+os.environ["OPENROUTER_API_KEY"]},json=body,timeout=180)
    r.raise_for_status();d=r.json();owner._usage(d)
    if d.get("error") or d.get("model")!=model or d.get("provider")!="Mistral" or len(d.get("choices",[]))!=1 or d["choices"][0]["finish_reason"]!="stop":raise RuntimeError("Incomplete or wrong OCR contract")
    output=owner._output(d)
    if not output:raise RuntimeError("Empty OCR output")
    return output,d["usage"],d.get("id")
