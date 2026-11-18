"""Resolve the full eligible matrix and verify owner request shaping without inference."""
from scout117_doc_web import CANDIDATE, CAPS, E, ROOT, astra_request, digest, load, owner, write
from types import SimpleNamespace
from modules.common.table_source_review import ASTRA_READER_PROFILES
from modules.extract.ocr_ai_gpt51_v1.main import _call_vision_model

pre=load(E/"preflight.json")
counts=load(E/"admission.json")
assert set(pre["matrix"])==set(counts)
assert "33120" in counts["crop-assisted-Image011-sol62"]["error"]["message"]
assert counts["crop-assisted-Image011-sol62"]["http"]==400
cand={"table":[],"ocr":[]}
control={"table":[],"ocr":[]}
parity=[]
for name,row in pre["matrix"].items():
    lane=row["lane"]
    if lane=="crop":
        continue
    model=row["model"]
    c=counts[name]
    assert c["http"]==200 and 0<c["count"]<=CAPS[lane][2]
    path=ROOT/row["body_path"]
    assert digest(path)==row["request_sha256"]
    b=load(path)
    if lane=="table":
        image=ROOT/row["golden"]
        # Proposed in-memory profile uses the maintained builder in isolation.
        ASTRA_READER_PROFILES[CANDIDATE]=("evaluation-only", "medium",32768,.4)
        assert astra_request(image.parent/"page.png", model)==b
        parity.append(name)
    elif model==CANDIDATE:
        calls=[]
        def capture(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(output_text="offline contract fixture")
        sys_part, usr_part = b["input"]
        text,img=usr_part["content"]
        _call_vision_model(model,sys_part["content"][0]["text"],text["text"],img["image_url"],0,32768,
            openai_client=SimpleNamespace(responses=SimpleNamespace(create=capture)),
            request_options={"image_detail":"original","service_tier":"default","reasoning_effort":"high"})
        assert calls==[b], (name,set(calls[0])-set(b))
        parity.append(name)
    input_bound=c["count"] if model.startswith("gpt") else 26000
    out=b.get("max_output_tokens") or b["generationConfig"]["maxOutputTokens"]+32768
    _,order,_,input_price=owner.RATES[model]
    bound=(input_bound*input_price+out*order)/1e6
    (cand if model==CANDIDATE else control)[lane].append(bound)
result={"admitted":{"crop":False},"reservations":{},"candidate_and_table_control_owner_request_parity":parity,
    "google_controls":"Immutable exact owner-local opt-in/control request replays from Attempt094, matched input images. Fresh independent requests.",
    "executor_sha256":digest(ROOT/"benchmarks/scripts/scout117_reservation.py"),"count_source":"exact real provider input counters over full request; controls reserve extra Google thought tokens"}
for lane in ("table","ocr"):
    candidate=max(cand[lane])*CAPS[lane][1]
    controls=sum(control[lane])
    assert candidate+controls<=CAPS[lane][0]
    result["reservations"][lane]={"candidate_finite_max":candidate,"controls_finite_max":controls,"total":candidate+controls,"max_candidate":CAPS[lane][1],"max_controls":len(control[lane]),"wallet":CAPS[lane][0]}
    result["admitted"][lane]=True
write(E/"reservation.json",result)
print(result)
