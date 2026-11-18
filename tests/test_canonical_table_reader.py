"""Exercise the ordinary Sol recipe offline with source-authored mock responses."""
import hashlib
import json

import pytest
from bs4 import BeautifulSoup

from benchmarks.scripts import scout117_table_consumer as replay
from modules.common.table_source_review import MODEL, source_request


@pytest.fixture(scope="module")
def driver_proof(tmp_path_factory):
    root = tmp_path_factory.mktemp("canonical-table")
    startup = root / "offline-transport"
    startup.mkdir()
    (startup / "sitecustomize.py").write_text(replay.TRANSPORT)
    ledger = []
    for case in ("heldout", "ambiguity-negative"):
        fixture = replay.EVIDENCE / "heldout-table" if case == "heldout" else replay.ROOT / "testdata/literal-table-fidelity/confirmation-v2" / case
        body = source_request(fixture / "page.png")
        from PIL import Image
        with Image.open(fixture / "page.png") as image:
            width, height = image.size
        holds = [] if case == "heldout" else [
            {"row": idx, "cell": 1, "reason": "Identical source glyphs.", "alternatives": ["I", "l"]}
            for idx in (1, 2)
        ]
        review = {"source_table_count": 1, "tables": [{"bbox": [0, 0, width, height],
                  "html": str(BeautifulSoup((fixture / "golden.html").read_text(), "html.parser").table), "uncertain_cells": holds}]}
        response = {k: body[k] for k in ("model", "store", "service_tier", "reasoning", "max_output_tokens", "text")}
        response.update(id="resp_mock", object="response", created_at=0, status="completed", error=None, incomplete_details=None,
            usage={"input_tokens": 40, "output_tokens": 30, "total_tokens": 70},
            output=[{"id": "msg_mock", "type": "message", "status": "completed", "role": "assistant",
                     "content": [{"type": "output_text", "text": json.dumps(review), "annotations": []}]}])
        name = "table-" + case + "-sol62"
        hashes = []
        for kind, payload in [("request", body), ("response", response)]:
            path = root / f"{name}.{kind}.json"
            replay.write(path, payload)
            hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
        ledger.append({"name": name, "input_bound": 40, "request_sha256": hashes[0], "raw_sha256": hashes[1]})
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(replay, "RAW", root)
        return {name: replay.run_case(root, startup, case, ledger=ledger, excess_count=(name == "over-limit"))
                for name, case in [("positive","heldout"),("uncertain","ambiguity-negative"),("over-limit","heldout")]}


def test_default_export_requires_current_source_reader(driver_proof):
    assert MODEL == "gpt-6.2-sol"
    assert driver_proof["positive"]["comparison"]["counts"]["actual"]["cells"] == 20
    assert driver_proof["positive"]["mock_http_routes"] == ["/v1/responses/input_tokens", "/v1/responses"]


def test_ordinary_recipe_holds_uncertainty_and_rejects_excess_before_inference(driver_proof):
    assert len(driver_proof["uncertain"]["holds"]) == 2
    assert driver_proof["uncertain"]["status"] == "unresolved"
    assert driver_proof["over-limit"]["mock_http_routes"] == ["/v1/responses/input_tokens"]
