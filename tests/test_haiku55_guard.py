"""Campaign boundary checks; no network or credentials."""

import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks/providers"))
import haiku55_guard as guard  # noqa: E402
import httpx  # noqa: E402

BODY = {
    "model": "claude-haiku-5-5",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Synthetic test"},
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/png;base64,AA=="},
                },
            ],
        }
    ],
    "max_tokens": 4096,
    "thinking": {"type": "adaptive"},
}


def initialize(tmp_path, monkeypatch, cap=11):
    monkeypatch.setattr(guard, "RESULTS", tmp_path)
    guard.write(
        tmp_path / "ledger.json",
        {"cap_usd": cap, "spent_usd": 0, "calls": [], "closed": False},
    )
    monkeypatch.setenv("HAIKU55_STAGE", "offline")
    monkeypatch.setenv("HAIKU55_CASE", "one")


def test_cap_prevents_dispatch(tmp_path, monkeypatch):
    initialize(tmp_path, monkeypatch, cap=0.001)
    calls = []
    with pytest.raises(RuntimeError, match="reserve"):
        guard.guarded_send(
            lambda *a, **k: calls.append(1),
            None,
            httpx.Request("POST", "https://api.anthropic.com/v1/messages", json=BODY),
        )
    assert calls == []


def test_unknown_reservation_and_duplicate_denial(tmp_path, monkeypatch):
    initialize(tmp_path, monkeypatch)
    calls = []

    def fail(*a, **k):
        calls.append(1)
        raise httpx.ReadTimeout("mock")

    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages", json=BODY)
    with pytest.raises(httpx.ReadTimeout):
        guard.guarded_send(fail, None, req)
    assert (
        json.loads((tmp_path / "ledger.json").read_text())["calls"][0]["cost_usd"]
        is None
    )
    with pytest.raises(RuntimeError, match="Duplicate"):
        guard.guarded_send(fail, None, req)
    assert len(calls) == 1


def test_cross_process_actual_dispatch_serial(tmp_path):
    guard.write(
        tmp_path / "ledger.json",
        {"cap_usd": 11, "spent_usd": 0, "calls": [], "closed": False},
    )
    program = """import sys,json,time,os
from pathlib import Path
sys.path.insert(0,sys.argv[1]);import haiku55_guard as g;import httpx  # noqa: E402
g.RESULTS=Path(sys.argv[2]);os.environ['HAIKU55_STAGE']='offline';os.environ['HAIKU55_CASE']=sys.argv[3]
body=json.loads(sys.argv[4])
def original(client,request,**kwargs):
 start=time.monotonic();time.sleep(.15);end=time.monotonic()
 with (g.RESULTS/'intervals').open('a') as f:f.write(json.dumps([start,end])+'\\n')
 return httpx.Response(200,json={'model':body['model'],'usage':{'input_tokens':10,'output_tokens':10}},request=request)
httpx.Client.send=original;g.install()
httpx.post('https://api.anthropic.com/v1/messages',json=body)
"""
    processes = [
        subprocess.Popen(
            [
                sys.executable,
                "-c",
                program,
                str(ROOT / "benchmarks/providers"),
                str(tmp_path),
                str(i),
                json.dumps(BODY),
            ]
        )
        for i in range(2)
    ]
    assert [p.wait(timeout=10) for p in processes] == [0, 0]
    intervals = sorted(
        json.loads(line) for line in (tmp_path / "intervals").read_text().splitlines()
    )
    assert intervals[0][1] <= intervals[1][0]
    final_ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert len(final_ledger["calls"]) == 2
    assert final_ledger["spent_usd"] == pytest.approx(0.000012)
