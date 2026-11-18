"""Freeze Story231 assisted caller native detector/caption matrix."""
import json
from scout116_doc_web import E, OLD, RAW, ROOT, CANDIDATE, digest, openai_body, write

matrix_path=E/"preflight.json"
pre=json.loads(matrix_path.read_text())
def add(name,label,b):
    path=RAW/(name+".request.json")
    if path.exists():
        raise RuntimeError("Already frozen")
    write(path,b)
    pre["matrix"][name]={"lane":"crop","model":label,"request_sha256":digest(path),
        "body_path":str(path.relative_to(ROOT)),"independent":True}
historic=json.loads((OLD/"runtime-12-candidate-detector-4.json").read_text())
parts=historic["contents"][0]["parts"]
b=openai_body(parts[0]["text"],parts[1]["inlineData"],historic["systemInstruction"]["parts"][0]["text"])
from modules.common.openai_crop_vision import DETECTOR_RESPONSE_FORMAT
b["text"]={"format":DETECTOR_RESPONSE_FORMAT}
add("crop-runtime12-astra62",CANDIDATE,b)
for index in range(1,5):
    name=f"runtime-12-candidate-caption-{index}-adequate8192"
    caption = json.loads((OLD/(name+".json")).read_text())
    add(f"crop-runtime12-caption{index}","gemini-3-flash-preview",caption)
pre["assisted_runtime_scope"]="Only native page 12 with original qualified public pixels and frozen Story231 OCR hints; caption calls at driver-requested cardinality, never substituted."
pre["before_runtime_extension_matrix_sha256"]=digest(matrix_path)
write(matrix_path,pre)
