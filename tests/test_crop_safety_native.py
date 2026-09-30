"""Offline native-contract tests; every live dispatch uses synthetic transport."""
import copy
import json
from pathlib import Path

import pytest

from benchmarks.providers import openai_responses_model as owner
from modules.common import crop_safety as safety
from modules.common.crop_review import CropReviewError, digest
from modules.transform.propose_crop_safety_v1 import main as proposer
from tools.prepare_crop_review_fixture import prepare

RUN = "story242-native-test"
REPO = Path(__file__).resolve().parents[1]


def rows(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x]


def dump(path, value):
    Path(path).write_text(json.dumps(value))


def envelope(*, live=False):
    data = json.loads((REPO / "tests/fixtures/crop_review_offline/saved-S3-pass.json").read_text())
    if live:
        data["service_tier"] = "default"
    return data


@pytest.fixture
def custody(tmp_path):
    root = tmp_path / "custody"
    paths = prepare(root, RUN)
    Path(paths["proposals"]).unlink()
    return root, Path(paths["manifest"]), tmp_path / "proposal-output" / "proposals.jsonl"


def mapping(root, manifest, mode="mock"):
    """Synthetic S4 reuse is explicitly mock, never claimed as a measured receipt."""
    directory = root / "offline-input"
    directory.mkdir()
    entries = []
    for index, row in enumerate(rows(manifest)):
        request = directory / f"request-{index}.json"
        response = directory / f"response-{index}.json"
        dump(request, safety.build_request(root / row["source_image"], root / "images" / row["filename"]))
        response.write_bytes(json.dumps(envelope()).encode())
        entries.append({"filename": row["filename"], "request_path": request.name,
                        "request_sha256": digest(request), "response_path": response.name,
                        "response_sha256": digest(response), "status_code": 200})
    path = directory / "mapping.json"
    dump(path, {"mode": mode, "entries": entries})
    return path


def ledger(root):
    return json.loads((root / "native-receipts/ledger.json").read_text())


def fake_success(body):
    assert body["service_tier"] == "default"
    return 200, json.dumps(envelope(live=True)).encode()


def test_request_matches_frozen_measured_owner_contract(custody, monkeypatch):
    root, manifest, _ = custody
    row = rows(manifest)[0]
    body = safety.build_request(root / row["source_image"], root / "images" / row["filename"])
    js = REPO / "benchmarks/prompts/validate-page-level-crop.js"
    assert digest(js) == safety.MEASURED_JS_SHA
    frozen_text = js.read_text().split("const PROMPT_TEXT = `", 1)[1].split("`;", 1)[0]
    assert body["input"][0]["content"][0]["text"] == frozen_text
    for key in tuple(owner.os.environ):
        if key.startswith("OPENAI_RESPONSES_"):
            monkeypatch.delenv(key)
    measured = owner._build_body(json.dumps(body["input"]), {"model": safety.MODEL,
        "reasoning_effort": "medium", "max_output_tokens": 4096,
        "image_detail": "high", "output_contract": "page_context_validation"})
    assert body == measured
    content = body["input"][0]["content"]
    assert content[1]["image_url"] == safety.image_uri(root / row["source_image"])
    assert content[2]["image_url"] == safety.image_uri(root / "images" / row["filename"])
    live = safety.build_request(root / row["source_image"], root / "images" / row["filename"], live=True)
    assert live.pop("service_tier") == "default"
    assert live == body


@pytest.mark.parametrize("change", [
    lambda d: d.update(model="different-served-model"),
    lambda d: d.update(id="unknown"),
    lambda d: d.update(status="incomplete"),
    lambda d: d.update(error={"message": "failed"}),
    lambda d: d.update(incomplete_details={"reason": "max_output_tokens"}),
    lambda d: d.update(output=[]),
    lambda d: d.update(output=[{"type": "tool_call"}]),
    lambda d: d["output"].extend([copy.deepcopy(next(x for x in d["output"] if x["type"] == "message"))]),
    lambda d: next(x for x in d["output"] if x["type"] == "message").update(role="user"),
    lambda d: next(x for x in d["output"] if x["type"] == "message").update(content=[{"type": "refusal", "refusal": "no"}]),
    lambda d: next(x for x in d["output"] if x["type"] == "message").update(content=[{"type": "output_text", "text": '{"verdict":"pass"}'}]),
    lambda d: next(x for x in d["output"] if x["type"] == "message").update(content=[{"type": "output_text", "text": '{"verdict":"pass","has_page_text":0,"excessive_blank":false,"reason":"ok"}'}]),
    lambda d: d.update(usage=None),
    lambda d: d["usage"].update(input_tokens=True),
    lambda d: d["usage"].update(total_tokens=0),
    lambda d: d["usage"].update(output_tokens=4097),
    lambda d: d["usage"].update(input_tokens_details={"cached_tokens": -1}),
    lambda d: d["usage"].update(output_tokens_details={"reasoning_tokens": 100000}),
    lambda d: d["usage"].update(input_tokens_details=[]),
])
def test_native_malformed_envelopes_fail_closed(change):
    data = envelope()
    change(data)
    with pytest.raises((CropReviewError, ValueError)):
        safety.parse_response(json.dumps(data).encode())


def test_native_http_and_live_tier_fail_closed():
    with pytest.raises(CropReviewError):
        safety.parse_response(json.dumps(envelope()).encode(), 429)
    data = envelope(live=True)
    data["service_tier"] = "flex"
    with pytest.raises(CropReviewError):
        safety.parse_response(json.dumps(data).encode(), live=True)
    answer, data, cost = safety.parse_response(json.dumps(envelope()).encode())
    assert answer["verdict"] == "pass"
    assert 0 < cost <= safety.RESERVE_USD


def test_default_replay_never_accesses_credentials_or_network(custody, monkeypatch):
    root, manifest, out = custody
    # One genuine S3 replay only; no invented measured S4 result.
    manifest.write_text(json.dumps(rows(manifest)[0]) + "\n")
    replay = mapping(root, manifest, "replay")
    def forbidden(*args, **kwargs):
        pytest.fail("offline path accessed credentials or network")
    monkeypatch.setattr(proposer.os.environ, "get", forbidden)
    monkeypatch.setattr(proposer, "live_send", forbidden)
    monkeypatch.setattr(owner.httpx, "post", forbidden)
    result = proposer.propose(root, manifest, out, RUN, replay_manifest=replay)
    assert result["completed"] == 1
    assert rows(out)[0]["mode"] == "replay"
    assert ledger(root)["settled_upper_usd"] == 0
    assert ledger(root)["calls"][0]["reserved_usd"] == 0


@pytest.mark.parametrize("cap,max_calls", [(None, None), (0.1, 2), (1, 1), (float("nan"), 2), (float("inf"), 2)])
def test_live_caps_admit_before_any_write_or_dispatch(custody, cap, max_calls):
    root, manifest, out = custody
    def forbidden(body):
        pytest.fail("insufficient caps dispatched")
    with pytest.raises(CropReviewError):
        proposer.propose(root, manifest, out, RUN, mode="live", cap_usd=cap, max_calls=max_calls, transport=forbidden)
    assert not (root / "native-receipts").exists()
    assert not out.exists()


def test_intent_reserved_and_exact_raw_receipt_persist_before_parse(custody, monkeypatch):
    root, manifest, out = custody
    raw = b'{"malformed": true}\n'
    calls = []
    def transport(body):
        calls.append(body)
        record = ledger(root)["calls"][0]
        assert record["status"] == "reserved"
        assert record["settled_upper_usd"] is None
        assert record["reserved_usd"] == safety.RESERVE_USD
        assert json.loads((root / "native-receipts/request-001.json").read_bytes()) == body
        return 200, raw
    def parse(receipt, status, **kwargs):
        assert receipt == raw
        assert (root / "native-receipts/response-001.json").read_bytes() == raw
        raise ValueError("deliberate parser failure")
    monkeypatch.setattr(proposer, "parse_response", parse)
    result = proposer.propose(root, manifest, out, RUN, mode="live", cap_usd=1, max_calls=2, transport=transport)
    assert len(calls) == 1
    assert result["unavailable"] == 1
    assert ledger(root)["closed"] is True
    assert ledger(root)["calls"][0]["settled_upper_usd"] is None
    assert rows(out)[0]["verdict"] is None


@pytest.mark.parametrize("failure", ["quota", "timeout"])
def test_one_attempt_no_retry_unknown_reservation_closes_run(custody, failure):
    root, manifest, out = custody
    calls = []
    def transport(body):
        calls.append(body)
        if failure == "timeout":
            raise TimeoutError("synthetic timeout")
        return 429, b'{"error":{"code":"insufficient_quota"}}'
    proposer.propose(root, manifest, out, RUN, mode="live", cap_usd=1, max_calls=2, transport=transport)
    before = digest(root / "native-receipts/ledger.json")
    assert len(calls) == 1
    assert ledger(root)["closed"] is True
    assert ledger(root)["calls"][0]["reserved_usd"] == safety.RESERVE_USD
    assert ledger(root)["calls"][0]["settled_upper_usd"] is None
    with pytest.raises(CropReviewError):
        proposer.propose(root, manifest, out.parent / "second.jsonl", RUN, mode="live", cap_usd=1, max_calls=2, transport=transport)
    assert digest(root / "native-receipts/ledger.json") == before
    assert len(calls) == 1


def test_success_cannot_reset_caps_or_duplicate_dispatch(custody):
    root, manifest, out = custody
    calls = []
    def transport(body):
        calls.append(body)
        return fake_success(body)
    proposer.propose(root, manifest, out, RUN, mode="live", cap_usd=1, max_calls=2, transport=transport)
    assert len(calls) == 2
    assert ledger(root)["settled_upper_usd"] > 0
    before = digest(root / "native-receipts/ledger.json")
    for cap in (1, 2):
        with pytest.raises(CropReviewError):
            proposer.propose(root, manifest, out.parent / f"reset-{cap}.jsonl", RUN, mode="live", cap_usd=cap, max_calls=2, transport=transport)
    assert len(calls) == 2
    assert digest(root / "native-receipts/ledger.json") == before


def test_output_alias_to_ledger_is_rejected_without_mutation(custody):
    root, manifest, out = custody
    replay = mapping(root, manifest)
    proposer.propose(root, manifest, out, RUN, mode="mock", replay_manifest=replay)
    before = {p: digest(p) for p in root.rglob("*") if p.is_file()}
    alias = out.parent / "alias"
    alias.symlink_to(root / "native-receipts", target_is_directory=True)
    with pytest.raises(CropReviewError):
        proposer.propose(root, manifest, alias / "ledger.json", RUN, mode="mock", replay_manifest=replay)
    assert all(digest(path) == hashed for path, hashed in before.items())


def test_native_gate_revalidates_verdict_request_and_response(custody):
    root, manifest, out = custody
    replay = mapping(root, manifest)
    proposer.propose(root, manifest, out, RUN, mode="mock", replay_manifest=replay)
    row = rows(manifest)[0]
    proposal = rows(out)[0]
    safety.validate_native_proposal(root, proposal, row, manifest)
    for key, value in (("verdict", "fail"), ("served_model", "wrong"), ("prompt_sha256", "0" * 64)):
        changed = copy.deepcopy(proposal)
        changed[key] = value
        with pytest.raises(CropReviewError):
            safety.validate_native_proposal(root, changed, row, manifest)
    request = root / proposal["request"]["path"]
    data = json.loads(request.read_bytes())
    data["reasoning"]["effort"] = "low"
    dump(request, data)
    changed = copy.deepcopy(proposal)
    changed["request"]["sha256"] = digest(request)
    with pytest.raises(CropReviewError):
        safety.validate_native_proposal(root, changed, row, manifest)


def test_unknown_reservations_count_against_next_admission(custody):
    root, manifest, out = custody
    receipts = root / "native-receipts"
    receipts.mkdir()
    cap = 2 * safety.RESERVE_USD
    prior = {"run_id": RUN, "mode": "live", "manifest_sha256": digest(manifest),
             "cap_usd": cap, "max_calls": 3, "settled_upper_usd": 0,
             "closed": False, "calls": [{"candidate_id": "synthetic-prior-unknown",
             "reserved_usd": cap, "settled_upper_usd": None, "status": "unavailable"}]}
    dump(receipts / "ledger.json", prior)
    before = digest(receipts / "ledger.json")
    def forbidden(body):
        pytest.fail("unknown exposure was ignored")
    with pytest.raises(CropReviewError, match="admission cap"):
        proposer.propose(root, manifest, out, RUN, mode="live", cap_usd=cap, max_calls=3, transport=forbidden)
    assert digest(receipts / "ledger.json") == before
    assert not out.exists()
    assert not list(receipts.glob("request-*.json"))


def test_replay_tampering_is_rejected_before_receipts_or_output(custody):
    root, manifest, out = custody
    replay = mapping(root, manifest)
    data = json.loads(replay.read_text())
    (replay.parent / data["entries"][0]["response_path"]).write_bytes(b'{}')
    with pytest.raises(CropReviewError, match="hash or semantic mismatch"):
        proposer.propose(root, manifest, out, RUN, mode="mock", replay_manifest=replay)
    assert not (root / "native-receipts").exists()
    assert not out.exists()


def test_rehashed_response_cannot_rewrite_proposal_verdict(custody):
    root, manifest, out = custody
    proposer.propose(root, manifest, out, RUN, mode="mock", replay_manifest=mapping(root, manifest))
    proposal = rows(out)[0]
    response = root / proposal["receipt"]["path"]
    data = json.loads(response.read_bytes())
    message = next(x for x in data["output"] if x["type"] == "message")
    payload = json.loads(message["content"][0]["text"])
    payload["verdict"] = "fail"
    message["content"][0]["text"] = json.dumps(payload)
    dump(response, data)
    proposal["receipt"]["sha256"] = digest(response)
    with pytest.raises(CropReviewError, match="does not match raw receipt"):
        safety.validate_native_proposal(root, proposal, rows(manifest)[0], manifest)


@pytest.mark.parametrize("field", ["content_none", "text_none", "input_details_none", "output_details_none"])
def test_malformed_native_structures_raise_review_error(field):
    data = envelope()
    message = next(x for x in data["output"] if x["type"] == "message")
    if field == "content_none":
        message["content"] = [None]
    elif field == "text_none":
        message["content"] = [{"type": "output_text", "text": None}]
    elif field == "input_details_none":
        data["usage"]["input_tokens_details"] = None
    else:
        data["usage"]["output_tokens_details"] = None
    with pytest.raises(CropReviewError):
        safety.parse_response(json.dumps(data).encode())


@pytest.mark.parametrize("second_cap", [1, 2])
def test_live_run_anchor_blocks_fresh_custody_and_cap_reset(custody, second_cap):
    root, manifest, out = custody
    calls = []
    def timeout(body):
        calls.append(body)
        raise TimeoutError("synthetic unknown exposure")
    proposer.propose(root, manifest, out, RUN, mode="live", cap_usd=1, max_calls=2, transport=timeout)
    anchor = root.parent / ".synthetic-live-run-anchors" / f"{RUN}.json"
    identity = json.loads(anchor.read_text())
    assert identity["custody_root"] == str(root.resolve())
    assert identity["manifest_sha256"] == digest(manifest)
    assert identity["cap_usd"] == 1
    assert identity["max_calls"] == 2
    before_anchor = digest(anchor)
    before_ledger = digest(root / "native-receipts/ledger.json")
    second_root = root.parent / "fresh-custody"
    second_paths = prepare(second_root, RUN)
    second_manifest = Path(second_paths["manifest"])
    # Fresh row identity intentionally differs, yet claims the same paid run.
    second_rows = rows(second_manifest)
    second_rows[0]["alt"] = "Synthetic changed manifest, same run identity"
    second_manifest.write_text("".join(json.dumps(row) + "\n" for row in second_rows))
    second_out = out.parent / "fresh-output.jsonl"
    with pytest.raises(CropReviewError, match="cannot reset in fresh custody"):
        proposer.propose(second_root, second_manifest, second_out, RUN, mode="live", cap_usd=second_cap, max_calls=2, transport=timeout)
    assert len(calls) == 1
    assert digest(anchor) == before_anchor
    assert digest(root / "native-receipts/ledger.json") == before_ledger
    assert ledger(root)["calls"][0]["settled_upper_usd"] is None
    assert ledger(root)["calls"][0]["reserved_usd"] == safety.RESERVE_USD
    assert not (second_root / "native-receipts").exists()
    assert not second_out.exists()
