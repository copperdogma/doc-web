"""Reconcile preserved native results and source-level scores without provider calls."""
from __future__ import annotations

import statistics
from scout117_doc_web import CANDIDATE, E, RAW, ROOT, digest, load, owner, write


def reconcile():
    pre=load(E/"preflight.json")
    ledger=load(E/"ledger.json")
    assert len({row["name"] for row in ledger})==len(ledger)
    present={}
    charges={}
    for row in ledger:
        assert row["state"]=="valid",row["name"]
        name=row["name"]
        matrix=pre["matrix"][name]
        req=ROOT/matrix["body_path"]
        resp=ROOT/row["raw_path"]
        assert digest(req)==row["request_sha256"]==matrix["request_sha256"]
        assert digest(resp)==row["raw_sha256"] and resp.stat().st_size==row["raw_bytes"]
        b,d=load(req),load(resp)
        model=row["model"]
        google=model.startswith("gemini")
        if not google:
            assert d["reasoning"]["effort"]==b["reasoning"]["effort"] and d["store"] is False
            assert d["max_output_tokens"]==b["max_output_tokens"] and d["service_tier"]=="default"
            assert row["input_bound"]==row["usage"]["input"]
            if row["lane"]=="table":
                assert b["text"]["format"]["strict"] and d["text"]["format"]["strict"]
        schema=b.get("text",{}).get("format",{}).get("schema")
        raw,*_=owner.unpack(d,model,google,schema)
        assert raw==load(E/f"{name}.answer.json")["raw"]
        result=load(E/f"{name}.score.json")
        if row["lane"]=="table" and "ambiguity" in name:
            uncertain=[(x["row"],x["cell"],set(x["alternatives"])) for x in result["uncertainties"][0]]
            holds={(r,c) for r,c,alts in uncertain if {"I","l"}.issubset(alts)}
            success=(holds=={(1,1),(2,1)} and len(uncertain)==2 and result["structure_pass"] and
                all((x["row"],x["cell"]) in holds for x in result["text_mismatches"]))
            present[name]={"gate":success,"safe_hold_count":len(holds),"uncertainties":len(uncertain)}
        elif row["lane"]=="table":
            success=result["pass"] and result["uncertainties"]==[[]]
            present[name]={"gate":success,"exact_clear_cells":result["counts"]["actual"]["cells"] if success else None}
        else:
            present[name]={"gate":result["ratio"]>=.99 and result["metadata_first"],"ratio":result["ratio"]}
    for lane in ["table","ocr","crop"]:
        rows=[r for r in ledger if r["lane"]==lane]
        charges[lane]={"known_usd":sum(r["cost_estimate"] for r in rows),
            "reserved_unsettled_usd":sum(r["exposure"]-r["cost_estimate"] for r in rows),
            "valid":len(rows),"models":{}}
        for model in {r["model"] for r in rows}:
            subset=[r for r in rows if r["model"]==model]
            charges[lane]["models"][model]={"known_usd":sum(r["cost_estimate"] for r in subset),
                "mean_seconds":statistics.mean(r["elapsed_seconds"] for r in subset),"calls":len(subset)}
    write(E/"reconciliation.json",{"cases":present,"pools":charges,"known_total":sum(x["known_usd"] for x in charges.values()),"held_total":sum(x["reserved_unsettled_usd"] for x in charges.values())})
    files=[p for p in RAW.rglob("*") if p.is_file()]
    write(E/"manifest.json",{"protected_dir":str(RAW),"base":pre["base"],"frozen_producers":pre["producer_hashes"],
        "reconciler":digest(ROOT/"benchmarks/scripts/scout117_reconcile.py"),
        "files":[{"path":str(p.relative_to(ROOT)),"sha256":digest(p),"bytes":p.stat().st_size} for p in sorted(files)]})


if __name__=="__main__":
    reconcile()
