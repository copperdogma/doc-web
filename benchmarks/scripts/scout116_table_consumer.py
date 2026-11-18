"""Run the selected reader via real SDK and driver against saved native evidence."""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys

import httpx
import yaml
from openai import OpenAI as SDKOpenAI
from scout116_doc_web import E, RAW, ROOT, CANDIDATE, digest, write

from doc_web.literal_tables import compare_tables
from modules.common import openai_client
from benchmarks.providers.historical_literal_readers.table_source_review import SourceOnlyReader

if not (ROOT/"configs/recipes/recipe-pdf-literal-tables-html-astra62.yaml").is_file():
    raise SystemExit("Retired Astra 6.2 driver replay: use isolated revision 0a9dc6055e5ebe8e30f1b8ce3549050251bdb1a1 plus the retained Attempt097 evidence.")

fixture_root=RAW/(sys.argv[1] if len(sys.argv)>1 else "consumer")
fixture_root.mkdir(mode=0o700,exist_ok=False)


def block(*args,**kwargs):
    raise RuntimeError("Network forbidden during provider replay")


def reviewer(case, source):
    request=RAW/f"table-{case}-astra62.request.json"
    response=RAW/f"table-{case}-astra62.response.json"
    entry=next(x for x in json.loads((E/"ledger.json").read_text()) if x["name"]==f"table-{case}-astra62")
    assert digest(request)==entry["request_sha256"] and digest(response)==entry["raw_sha256"]
    seen=[]
    def mock(req):
        assert req.url.host=="api.openai.com"
        expected = json.loads(request.read_bytes())
        seen.append(req.url.path)
        if req.url.path == "/v1/responses/input_tokens":
            assert json.loads(req.content)=={k:expected[k] for k in ("model","input","text","reasoning")}
            return httpx.Response(200,json={"object":"response.input_tokens","input_tokens":entry["input_bound"]})
        assert req.url.path=="/v1/responses"
        assert json.loads(req.content)==expected
        return httpx.Response(200,content=response.read_bytes(),headers={"Content-Type":"application/json"})
    sdk=SDKOpenAI(api_key="offline",max_retries=0,http_client=httpx.Client(transport=httpx.MockTransport(mock)))
    client=openai_client.OpenAI.__new__(openai_client.OpenAI)
    client._client=sdk
    client.responses=openai_client._ResponsesProxy(sdk,lambda *args:None)
    records=[]
    SourceOnlyReader(CANDIDATE,max_requests=1,budget_usd=2,client=client)(source, records)
    assert seen == ["/v1/responses/input_tokens", "/v1/responses"] and len(records)==1
    rec=fixture_root/f"{case}.receipt.json"
    write(rec,records[0])
    return rec,entry["raw_sha256"]


def reject_over_reservation():
    seen=[]
    def mock(req):
        seen.append(req.url.path)
        assert req.url.path == "/v1/responses/input_tokens"
        return httpx.Response(200,json={"object":"response.input_tokens","input_tokens":68929})
    sdk=SDKOpenAI(api_key="offline",max_retries=0,http_client=httpx.Client(transport=httpx.MockTransport(mock)))
    client=openai_client.OpenAI.__new__(openai_client.OpenAI)
    client.responses=openai_client._ResponsesProxy(sdk,lambda *args:None)
    reader=SourceOnlyReader(CANDIDATE,max_requests=1,budget_usd=2,client=client)
    try:
        reader(E/"heldout-table/page.png",[])
    except ValueError as exc:
        assert "exceeds the Astra 6.2 request reservation" in str(exc)
    else:
        raise AssertionError("Over-cap native inference was not blocked")
    assert seen == ["/v1/responses/input_tokens"] and not reader.entries


def main():
    socket.socket.connect=block
    socket.socket.connect_ex=block
    socket.create_connection=block
    recipe_path = ROOT/"configs/recipes/recipe-pdf-literal-tables-html-astra62.yaml"
    reject_over_reservation()
    summary={"over_reservation_count_only":{"input_tokens":68929,"inference_calls":0}}
    for case,fixture,want_pass in (
        ("heldout",E/"heldout-table",True),
        ("ambiguity-negative",ROOT/"testdata/literal-table-fidelity/confirmation-v2/ambiguity-negative",False),
    ):
        source=fixture/"page.png"
        pdf=fixture/"native.pdf"
        gold=(fixture/"golden.html").read_text()
        retained,native_sha=reviewer(case,source)
        receipts=fixture_root/f"{case}.manifest.json"
        write(receipts,{"model":CANDIDATE,"schema_version":"retained_source_reviews_v1","records":[
            {"image_sha256":digest(source),"record_path":str(retained),"record_sha256":digest(retained)}
        ]})
        (fixture_root/case).mkdir()
        row=fixture_root/case/"pages_html.jsonl"
        # The first OCR step stays outside the replacement. Authored page HTML is
        # a deterministic positive/negative input to the unchanged review path.
        row.write_text(json.dumps({"schema_version":"page_html_v1","page":1,"page_number":1,
            "original_page_number":1,"image":str(source),"source":[str(pdf)] if pdf.exists() else [],
            "html":gold,"raw_html":gold,"module_id":"scout116_fixture"})+"\n")
        recipe=yaml.safe_load(recipe_path.read_text())
        recipe["stages"]=recipe["stages"][1:]
        recipe["stages"][0]={"id":"ocr_ai","stage":"extract","module":"load_artifact_v1",
            "out":"pages_html.jsonl","params":{"path":str(row),"schema_version":"page_html_v1"}}
        recipe["stages"][1]["params"]["source_review_receipts"]=str(receipts)
        path=fixture_root/f"{case}.yaml"
        path.write_text(yaml.safe_dump(recipe,sort_keys=False))
        run=f"scout116-astra62-{case}"
        output=fixture_root/"runs"
        # Child receives no credentials, and socket calls fail locally.
        startup=fixture_root/"startup"
        startup.mkdir(exist_ok=True)
        (startup/"sitecustomize.py").write_text(
            "import socket\n"
            "def block(*args, **kwargs):\n raise RuntimeError('Network forbidden during retained replay')\n"
            "socket.socket.connect=socket.socket.connect_ex=socket.create_connection=block\n"
        )
        env={k:v for k,v in os.environ.items() if not (k.endswith("_API_KEY") or k=="DOC_WEB_ENV_FILE")}
        env["PYTHONPATH"]=f"{startup}:{ROOT}"
        log=fixture_root/f"{case}.log"
        with log.open("w") as stream:
            proc=subprocess.run([sys.executable,"driver.py","--recipe",str(path),"--run-id",run,"--output-dir",str(output)],
                cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
        rd=output/run
        proof=list(rd.glob("**/qualification.json"))
        html=list(rd.glob("**/html/*.html"))
        outcomes={"driver_returncode":proc.returncode,"qualification_files":len(proof),
            "native_response_sha256":native_sha,"sdk_live_http_requests":0,"mock_requests":2,
            "input_page_sha256":digest(row),"driver_recipe_sha256":digest(path)}
        if want_pass:
            assert proc.returncode==0 and len(proof)==1 and html, (log,rd,proof,html)
            actual=next((h for h in html if "<table" in h.read_text()),None)
            assert actual is not None
            comparison=compare_tables(gold,actual.read_text())
            assert comparison["pass"]
            outcomes.update(table_comparison=comparison,qualification_sha256=digest(proof[0]),
                final_html_sha256=digest(actual))
        else:
            assert proc.returncode!=0 and not proof, (log,rd,proof)
            report,=list(rd.glob("**/row-*-page-*-original-*.json"))
            decision=json.loads(report.read_text())
            assert decision["status"]=="unresolved" and "2 uncertain cells" in " ".join(decision["errors"])
            outcomes["unresolved_report_sha256"]=digest(report)
        summary[case]=outcomes
    write(E/"table-consumer.json",summary)


if __name__=="__main__":
    main()
