"""Campaign projection of owner OpenRouter schemas; documented no reasoning control."""
import json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import openrouter_vision_chat as owner
import mistral4_guard as guard
BASE_BODY=owner._body

def body(prompt,options):
    result=BASE_BODY(prompt,options)
    result.pop("reasoning",None)
    result["provider"]["max_price"]={"prompt":0.68,"completion":2.09}
    return result

def call_api(prompt,options,context):
    os.environ["MISTRAL_CASE"]=str(context.get("vars",{}).get("golden_key",context.get("vars",{}).get("crop_key","native")))
    guard.install()
    owner._body=body
    try:
        result=owner.call_api(prompt,options,context)
        result.get("metadata",{}).pop("requested_reasoning_effort",None)
        return result
    finally:
        owner._body=BASE_BODY
