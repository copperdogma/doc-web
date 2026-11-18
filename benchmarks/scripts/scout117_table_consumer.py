"""Offline proof of the ordinary Sol table reader and publication path."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from doc_web.literal_tables import compare_tables

EVIDENCE = ROOT / "docs/evals/evidence/098-sol62"
RAW = ROOT / "output/fixtures/scout117-sol62"
RECIPE = ROOT / "configs/recipes/recipe-pdf-literal-tables-html.yaml"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


# The actual OpenAI SDK and owner caller run inside the driver process. Replace
# only its network transport, require both exact paid request bodies, and
# forbid every socket. This does not use the retained-manifest reader.
TRANSPORT = """
import json, os, socket
from pathlib import Path
import httpx

def forbid(*args, **kwargs):
    raise RuntimeError("Offline proof forbids sockets")

socket.socket.connect = socket.socket.connect_ex = socket.create_connection = forbid

def handle(transport, req):
    expected = json.loads(Path(os.environ["TABLE_PROOF_REQUEST"]).read_bytes())
    assert req.url.host == "api.openai.com" and req.method == "POST"
    route = req.url.path
    if route == "/v1/responses/input_tokens":
        assert json.loads(req.content) == {k: expected[k] for k in ("model", "input", "text", "reasoning")}
        result = httpx.Response(200, json={"object":"response.input_tokens","input_tokens":int(os.environ["TABLE_PROOF_COUNT"])})
    else:
        assert route == "/v1/responses" and json.loads(req.content) == expected
        result = httpx.Response(200, content=Path(os.environ["TABLE_PROOF_RESPONSE"]).read_bytes(), headers={"content-type":"application/json"})
    with Path(os.environ["TABLE_PROOF_LOG"]).open("a") as f:
        f.write(route+"\\n")
    return result

httpx.HTTPTransport.handle_request = handle
"""


def run_case(root, startup, case, *, excess_count=False, ledger=None):
    fixture = EVIDENCE / "heldout-table" if case == "heldout" else ROOT / "testdata/literal-table-fidelity/confirmation-v2" / case
    suffix = "oversize" if excess_count else case
    run_id = "canonical-sol-table-" + suffix
    run = root / "runs" / run_id
    run.mkdir(parents=True)
    raw_name = "table-" + case + "-sol62"
    request = RAW / (raw_name + ".request.json")
    response = RAW / (raw_name + ".response.json")
    if ledger is None:
        ledger=json.loads((EVIDENCE / "ledger.json").read_text())
    row = next(r for r in ledger if r["name"] == raw_name)
    assert digest(request) == row["request_sha256"] and digest(response) == row["raw_sha256"]
    source = fixture / "page.png"
    pdf = fixture / "native.pdf"
    if case == "heldout":
        rendered = root / (suffix + "-from-pdf")
        subprocess.run(["pdftoppm", "-r", "200", "-singlefile", "-png", str(pdf), str(rendered)], check=True)
        assert digest(rendered.with_suffix(".png")) == digest(source)
    # Resume at the first stage under replacement with the author-owned stage-A
    # fixture. The real canonical recipe selects all subsequent stages verbatim.
    gold = (fixture / "golden.html").read_text()
    upstream = run / "02_ocr_ai_gpt51_v1"
    upstream.mkdir()
    artifact = upstream / "pages_html.jsonl"
    artifact.write_text(json.dumps({"schema_version":"page_html_v1","page":1,"page_number":1,"original_page_number":1,
        "image":str(source),"source":[str(pdf)],"html":gold,"raw_html":gold,"module_id":"source_authored_stage_a_fixture"})+"\n")
    write(run / "pipeline_state.json", {"run_id":run_id,"stages":{"ocr_ai":{"status":"done","artifact":str(artifact),"schema_version":"page_html_v1","module_id":"ocr_ai_gpt51_v1"}}})
    calls = root / (suffix + ".calls")
    env = {k:v for k,v in os.environ.items() if not (k.endswith("_KEY") or k.startswith("DOC_WEB_") or "PROXY" in k.upper())}
    env.update(OPENAI_API_KEY="offline-test",DOC_WEB_OPENAI_API_KEY="offline-test",DOC_WEB_ENV_FILE=str(root/"absent.env"),
        PYTHONPATH=os.pathsep.join((str(startup),str(ROOT))),TABLE_PROOF_REQUEST=str(request),
        TABLE_PROOF_RESPONSE=str(response),TABLE_PROOF_COUNT=str(26_001 if excess_count else row["input_bound"]),TABLE_PROOF_LOG=str(calls))
    command=[sys.executable,"driver.py","--recipe",str(RECIPE),"--input-pdf",str(pdf),"--output-dir",str(root/"runs"),
        "--run-id",run_id,"--allow-run-id-reuse","--start-from","literal_table_review"]
    with (root/(suffix+".log")).open("w") as stream:
        proc=subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
    observed=calls.read_text().splitlines() if calls.exists() else []
    required=["/v1/responses/input_tokens"] + ([] if excess_count else ["/v1/responses"])
    assert observed==required, (root/(suffix+".log"), observed)
    positive=case=="heldout" and not excess_count
    assert (proc.returncode==0)==positive
    proofs=list(run.rglob("qualification.json"))
    html=list((run/"output/html").glob("*.html"))
    assert bool(proofs)==positive and bool(html)==positive
    report,=run.glob("**/row-*-page-*-original-*.json")
    checked=json.loads(report.read_text())
    result={"case":suffix,"recipe_sha256":digest(RECIPE),"command":command,"driver_returncode":proc.returncode,
        "source_sha256":digest(source),"native_pdf_sha256":digest(pdf),"report":os.path.relpath(report, ROOT),
        "native_receipt_sha256":row["raw_sha256"],"mock_http_routes":observed,"live_network_calls":0,"status":checked["status"]}
    if not excess_count:
        rec,=checked["requests"]
        assert rec["native_response_sha256"]==row["raw_sha256"] and rec["served_model"]=="gpt-6.2-sol"
    if positive:
        page, = (p for p in html if "<table" in p.read_text())
        score=compare_tables(gold,page.read_text())
        assert score["pass"] and score["counts"]["actual"]["cells"]==20
        result.update(html=os.path.relpath(page, ROOT),html_sha256=digest(page),qualification=os.path.relpath(proofs[0], ROOT),qualification_sha256=digest(proofs[0]),comparison=score)
    elif not excess_count:
        assert "2 uncertain cells" in " ".join(checked["errors"])
        result["holds"]=[c for t in checked["tables"] for c in t["review"]["uncertain_cells"]]
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_name")
    args=parser.parse_args()
    root=RAW/args.output_name
    root.mkdir(mode=0o700,exist_ok=False)
    startup=root/"offline_transport"
    startup.mkdir()
    (startup/"sitecustomize.py").write_text(TRANSPORT)
    results=[run_case(root,startup,"heldout"),run_case(root,startup,"ambiguity-negative"),run_case(root,startup,"heldout",excess_count=True)]
    write(root/"canonical-consumer.json",results)


if __name__=="__main__":
    main()
