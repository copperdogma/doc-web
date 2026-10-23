# ruff: noqa: E402
"""Scout093 literal-only native benchmark; serial bounded custody, no adoption."""

import base64
import fcntl
import hashlib
import json
import os
import sys
import time
from pathlib import Path
import httpx
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from doc_web.literal_fidelity import SourcePageReview
from modules.common.table_source_review import POLICY, SourceOnlyReader, astra_request
from modules.common.literal_table_review import review_literal_tables
from doc_web.literal_tables import compare_tables

R = ROOT / "benchmarks/results/wonder-thinking-20261014"
E = ROOT / "docs/evals/evidence/075-wonder-thinking"
CASES = ("ambiguity-negative", "image-positive", "native-positive")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def save(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")


def body(path):
    b = path.read_bytes()
    w, h = Image.open(path).size
    return {
        "model": "meta/muse-wonder",
        "max_tokens": 32768,
        "reasoning": {"effort": os.environ.get("WONDER_EFFORT", "high")},
        "provider": {
            "only": ["Meta"],
            "allow_fallbacks": False,
            "require_parameters": True,
            "max_price": {"prompt": 4, "completion": 20},
        },
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "source_page_tables",
                "strict": True,
                "schema": SourcePageReview.model_json_schema(),
            },
        },
        "messages": [
            {"role": "system", "content": POLICY},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Source image dimensions: {w} x {h} pixels. Read source tables; return JSON only.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/png;base64,"
                            + base64.b64encode(b).decode()
                        },
                    },
                ],
            },
        ],
    }


def send(original, client, request, **kwargs):
    if request.method != "POST":
        return original(client, request, **kwargs)
    b = json.loads(request.content)
    model = b["model"]
    route = request.url.host
    if (
        route == "openrouter.ai"
        and request.url.path == "/api/v1/chat/completions"
        and model == "meta/muse-wonder"
    ):
        reserve = 4.849664
        bound = 1048576
        maximum = 32768
    elif (
        route == "api.openai.com"
        and request.url.path == "/v1/responses"
        and model == "gpt-6-astra"
    ):
        reserve = 1.5
        bound = 26000
        maximum = 8192
    else:
        raise RuntimeError("Unmetered POST denied")
    R.mkdir(parents=True, exist_ok=True)
    with (R / "dispatch.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        ledger = json.loads((R / "ledger.json").read_text())
        exposure = ledger["spent_usd"] + sum(
            x["reserved_usd"] for x in ledger["calls"] if x.get("cost_usd") is None
        )
        stage = os.environ["WONDER_STAGE"]
        if (
            ledger["closed"]
            or 0.3223511 + exposure + reserve > 10
            or len(ledger["calls"]) >= 11
            or any(x["stage"] == stage for x in ledger["calls"])
        ):
            raise RuntimeError("Budget/duplicate/closed admission denied")
        n = len(ledger["calls"]) + 1
        raw = json.dumps(b, sort_keys=True).encode()
        req = R / f"request-{n:03}.json"
        res = R / f"response-{n:03}.json"
        if req.exists() or res.exists():
            raise RuntimeError("Receipt collision")
        with req.open("xb") as f:
            f.write(raw)
        rec = {
            "stage": stage,
            "model": model,
            "reserved_usd": reserve,
            "cost_usd": None,
            "request_sha256": sha(raw),
            "request": str(req.relative_to(ROOT)),
        }
        ledger["calls"].append(rec)
        save(R / "ledger.json", ledger)
        start = time.monotonic()
        try:
            response = original(client, request, **kwargs)
            response.read()
        except Exception as exc:
            rec["exception"] = type(exc).__name__
            save(R / "ledger.json", ledger)
            raise
        with res.open("xb") as f:
            f.write(response.content)
        rec.update(
            response=str(res.relative_to(ROOT)),
            response_sha256=sha(response.content),
            response_bytes=len(response.content),
            status_code=response.status_code,
            latency_ms=round((time.monotonic() - start) * 1000),
        )
        d = response.json()
        u = d.get("usage", {})
        try:
            if route == "openrouter.ai":
                inp, out = u["prompt_tokens"], u["completion_tokens"]
                cost = u["cost"]
                cache = u.get("prompt_tokens_details", {}).get("cached_tokens", 0)
                writes = 0
            else:
                inp, out = u["input_tokens"], u["output_tokens"]
                details = u.get("input_tokens_details", {})
                cache = details.get("cached_tokens", 0)
                writes = details.get("cache_write_tokens", 0)
                cost = (
                    (inp - cache - writes) * 10 + cache * 1 + writes * 12.5 + out * 50
                ) / 1e6
            assert (
                all(type(x) is int and x >= 0 for x in (inp, out, cache, writes))
                and cache + writes <= inp
                and type(cost) in (int, float)
                and cost >= 0
            )
            rec.update(
                usage=u,
                cost_usd=cost,
                served_model=d.get("model"),
                provider=d.get("provider", "OpenAI"),
            )
            ledger["spent_usd"] += cost
            if inp > bound or out > maximum or cost > reserve:
                ledger["closed"] = True
                rec["bound_violation"] = True
        except (KeyError, AssertionError, TypeError):
            rec["billing_unresolved"] = True
        save(R / "ledger.json", ledger)
        return response


def install():
    for library in [httpx]:
        if getattr(library.Client.send, "_wonder", False):
            continue
        original = library.Client.send

        def wrapped(c, r, _original=original, **k):
            return send(_original, c, r, **k)

        wrapped._wonder = True
        library.Client.send = wrapped


def candidate(path, requests):
    install()
    b = body(Path(path))
    d = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]},
        json=b,
        timeout=240,
    ).json()
    save(R / (os.environ["WONDER_STAGE"] + "-decoded.json"), d)
    assert (
        d.get("model") in ("meta/muse-wonder", "meta/muse-wonder-20261012")
        and d.get("provider") == "Meta"
        and len(d["choices"]) == 1
        and d["choices"][0]["finish_reason"] == "stop"
        and not d.get("error")
    )
    raw = d["choices"][0]["message"]["content"]
    parsed = SourcePageReview.model_validate_json(raw)
    requests.append(
        {
            "requested_model": "meta/muse-wonder",
            "served_model": d["model"],
            "provider": d["provider"],
            "usage": d["usage"],
            "raw_response": raw,
            "status": "completed",
            "response_id": d["id"],
            "submitted_image_sha256": sha(Path(path).read_bytes()),
        }
    )
    return parsed


def preflight():
    R.mkdir(parents=True, exist_ok=True)
    E.mkdir(parents=True, exist_ok=True)
    matrix = []
    for c in CASES:
        p = ROOT / f"testdata/literal-table-fidelity/confirmation-v2/{c}/page.png"
        prior = (
            Path("/Users/cam/Documents/Projects/doc-web/output/runs")
            / f"story244-{c}-v2/02_ocr_ai_gpt51_v1/pages_html.jsonl"
        )
        rows = [json.loads(x) for x in prior.read_text().splitlines()]
        assert len(rows) == 1
        save(E / f"initial-{c}.json", rows[0])
        candidate_body = body(p)
        control_body = astra_request(p)
        matrix.append(
            {
                "case": c,
                "image_sha256": sha(p.read_bytes()),
                "dimensions": Image.open(p).size,
                "initial_sha256": sha(prior.read_bytes()),
                "candidate_request_sha256": sha(
                    json.dumps(candidate_body, sort_keys=True).encode()
                ),
                "control_request_sha256": sha(
                    json.dumps(control_body, sort_keys=True).encode()
                ),
                "gold_sha256": sha((p.parent / "golden.html").read_bytes()),
            }
        )
    save(
        E / "preflight.json",
        {
            "base": "e44c0a41abf02ad266c10afdf5d95d48bb1b1fe2",
            "cap_usd": 10,
            "matrix": matrix,
            "candidate": "meta/muse-wonder high32768; fresh medium bakery; conditional max32768",
            "control": "gpt-6-astra medium8192 original source-only",
            "cache": "fresh readers frozen identical upstream OCR",
            "judge": "independent root source review; deterministic exact comparator authoritative; zero paid judge",
            "concurrency": 1,
            "grouping": "independent one-page requests",
            "policy_sha256": sha(POLICY.encode()),
            "schema_sha256": sha(
                json.dumps(
                    SourcePageReview.model_json_schema(), sort_keys=True
                ).encode()
            ),
            "candidate_reserve_usd": 4.849664,
            "reservation_basis": "entire 1048576 context input at4/M +32768 combined output at20/M; conservative serial settlement; unknown stays reserved",
            "control_reserve_usd": 1.5,
            "producer_sha256": sha(Path(__file__).read_bytes()),
            "prior_settled_usd": 0.3223511,
            "hard_incremental_cap_usd": 9.6776489,
            "maximum_post_count": 11,
            "no_runtime_profile": True,
            "exposed_regression": True,
        },
    )
    save(
        R / "ledger.json", {"cap_usd": 10, "spent_usd": 0, "calls": [], "closed": False}
    )
    print("preflight3cases independent native requests source-only no judge")


def run(c, label):
    if c not in CASES or label not in ("high", "max", "medium", "control") or (label == "medium" and c != "image-positive"):
        raise ValueError("Outside approved fixed thinking matrix")
    os.environ["WONDER_STAGE"] = c + "-" + label
    os.environ["WONDER_EFFORT"] = label if label != "control" else "medium"
    install()
    p = ROOT / f"testdata/literal-table-fidelity/confirmation-v2/{c}/page.png"
    initial = json.loads((E / f"initial-{c}.json").read_text())
    initial["image"] = str(p)
    initial["source"] = []
    reader = (
        candidate
        if label != "control"
        else SourceOnlyReader(max_requests=1, budget_usd=1.5)
    )
    out = R / f"{c}-{label}.jsonl"
    row = review_literal_tables(
        [initial], out_path=out, run_id=f"wonder-thinking-{c}-{label}", reader=reader
    )[0]
    report = json.loads(Path(row["literal_fidelity"]["report_path"]).read_text())
    review = report["tables"][0]["review"] if report["tables"] else {}
    score = compare_tables(
        (p.parent / "golden.html").read_text(), review.get("html", "")
    )
    result = {
        "case": c,
        "arm": label,
        "status": report["status"],
        "errors": report["errors"],
        "uncertainties": review.get("uncertain_cells", []),
        "quality": score,
        "report": str(Path(row["literal_fidelity"]["report_path"]).relative_to(ROOT)),
    }
    save(E / f"{c}-{label}.json", result)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "preflight":
        preflight()
    else:
        run(sys.argv[1], sys.argv[2])
