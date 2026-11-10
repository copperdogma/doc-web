"""Default-off provider identity and full caller-chain evaluation boundaries."""

import copy
import json
import os
from pathlib import Path

import pytest

from modules.common import crop_safety as safety
from modules.common.crop_review import CropReviewError, digest
from modules.common.crop_safety_fable_eval import CONTRACT, ENV
from modules.common.utils import read_jsonl
from modules.transform.propose_crop_safety_v1 import main as proposer
from tools.prepare_crop_review_fixture import prepare
from tools.run_safety_qual_caller import run, synthetic_envelope

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def opted(monkeypatch):
    monkeypatch.setenv(ENV, CONTRACT)
    monkeypatch.delenv("DOC_WEB_SAFETY_QUAL_088_REPLAY_LIVE", raising=False)
    monkeypatch.delenv("DOC_WEB_SAFETY_QUAL_088_TRANSPORT", raising=False)


def test_default_sol_and_unknown_external_contract(monkeypatch):
    monkeypatch.delenv(ENV, raising=False)
    assert safety.evaluation_contract() is None
    assert safety.reservation_usd() == 0.155960
    monkeypatch.setenv(ENV, "unrecognized-model")
    with pytest.raises(CropReviewError):
        safety.evaluation_contract()


def test_native_build_exact_schema_tier_effort_pixels_and_bound(opted, tmp_path):
    from PIL import Image

    a = tmp_path / "source.png"
    b = tmp_path / "crop.jpg"
    Image.new("RGB", (100, 100), "white").save(a)
    Image.new("RGB", (50, 50), "white").save(b)
    body = safety.build_request(a, b, live=True)
    assert set(body) == {
        "model",
        "service_tier",
        "max_tokens",
        "output_config",
        "messages",
    }
    assert (
        body["model"] == "claude-fable-5-2"
        and body["service_tier"] == "standard_only"
        and body["max_tokens"] == 32768
    )
    assert body["output_config"] == {
        "effort": "xhigh",
        "format": {"type": "json_schema", "schema": safety.FORMAT["schema"]},
    }
    import base64

    parts = body["messages"][0]["content"]
    assert parts[0]["text"] == safety.PROMPT_PATH.read_text()
    assert base64.b64decode(parts[1]["source"]["data"]) == a.read_bytes()
    assert base64.b64decode(parts[2]["source"]["data"]) == b.read_bytes()
    Image.new("RGB", (2049, 20)).save(a)
    with pytest.raises(CropReviewError, match="no implicit resize"):
        safety.build_request(a, b)


@pytest.mark.parametrize("case,verdict", [("S3", "fail"), ("S4", "pass")])
def test_native_valid_answers_preserve_provider_envelope(opted, case, verdict):
    raw = json.dumps(synthetic_envelope("fable", case)).encode()
    answer, data, cost = safety.parse_response(raw, live=True)
    assert answer["verdict"] == verdict and data["id"].startswith("msg_")
    assert cost <= safety.reservation_usd()
    assert "output" not in data and "total_tokens" not in data["usage"]


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d.update(id="resp_forged"),
        lambda d: d.update(model="gpt-6.1-sol"),
        lambda d: d.update(stop_reason="max_tokens"),
        lambda d: d.update(stop_reason="refusal"),
        lambda d: d.update(role="user"),
        lambda d: d.update(content=[{"type": "tool_use", "name": "x"}]),
        lambda d: d["usage"].update(output_tokens=32769),
        lambda d: d["usage"].update(input_tokens=True),
        lambda d: d["usage"].update(cache_read_input_tokens=-1),
        lambda d: d["usage"].update(service_tier="priority"),
        lambda d: d["usage"].update(speed="fast"),
        lambda d: d["usage"].update(output_tokens_details={"thinking_tokens": 101}),
        lambda d: d["content"][0].update(text="{}"),
        lambda d: d["content"][0].update(
            text=json.dumps(
                {
                    "verdict": "pass",
                    "has_page_text": False,
                    "excessive_blank": False,
                    "reason": "",
                }
            )
        ),
    ],
)
def test_malformed_or_unavailable_never_becomes_semantic_fail(opted, mutation):
    data = synthetic_envelope("fable", "S3")
    mutation(data)
    with pytest.raises((CropReviewError, ValueError, KeyError, TypeError)):
        safety.parse_response(json.dumps(data).encode(), live=True)


def test_native_http_failure(opted):
    with pytest.raises(CropReviewError, match="HTTP"):
        safety.parse_response(
            json.dumps(synthetic_envelope("fable", "S3")), 503, live=True
        )


def test_no_default_fable_network_or_key_access(opted, monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda *a, **k: pytest.fail("credential read"))
    with pytest.raises(CropReviewError, match="combined campaign transport"):
        proposer.live_send({})


def fixture_proposals(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, CONTRACT)
    from modules.common import crop_safety_fable_eval as native

    monkeypatch.setattr(
        native, "validate_dispatch_anchor", lambda *args: None
    )  # parser-only synthetic transport unit fixture
    root = tmp_path / "custody"
    paths = prepare(root, "fable-receipt-test")
    Path(paths["proposals"]).unlink()
    out = tmp_path / "proposal-output/proposals.jsonl"

    def transport(body):
        assert body["model"] == "claude-fable-5-2"
        return 200, json.dumps(synthetic_envelope("fable", "S3")).encode()

    proposer.propose(
        root,
        paths["manifest"],
        out,
        "fable-receipt-test",
        mode="live",
        cap_usd=4.09344,
        max_calls=2,
        transport=transport,
    )
    return root, Path(paths["manifest"]), list(read_jsonl(out))


def test_full_native_receipt_external_optin_revalidation_and_tamper(
    tmp_path, monkeypatch
):
    root, manifest, proposals = fixture_proposals(tmp_path, monkeypatch)
    row = list(read_jsonl(manifest))[0]
    p = proposals[0]
    safety.validate_native_proposal(root, p, row, manifest)
    assert p["evaluation_contract"] == CONTRACT
    monkeypatch.delenv(ENV)
    with pytest.raises(CropReviewError, match="external opt-in"):
        safety.validate_native_proposal(root, p, row, manifest)
    monkeypatch.setenv(ENV, CONTRACT)
    receipt = root / p["receipt"]["path"]
    native = json.loads(receipt.read_text())
    native["model"] = "wrong"
    receipt.write_text(json.dumps(native))
    p["receipt"]["sha256"] = digest(receipt)
    with pytest.raises(CropReviewError, match="served model"):
        safety.validate_native_proposal(root, p, row, manifest)


def test_request_and_verdict_rehash_cannot_bypass_native_receipt(tmp_path, monkeypatch):
    root, manifest, proposals = fixture_proposals(tmp_path, monkeypatch)
    row = list(read_jsonl(manifest))[0]
    p = proposals[0]
    p["verdict"] = "pass"
    with pytest.raises(CropReviewError, match="does not match raw receipt"):
        safety.validate_native_proposal(root, p, row, manifest)
    p["verdict"] = "fail"
    request = root / p["request"]["path"]
    data = json.loads(request.read_text())
    data["output_config"]["effort"] = "max"
    request.write_text(json.dumps(data))
    p["request"]["sha256"] = digest(request)
    with pytest.raises(CropReviewError, match="frozen source/crop contract"):
        safety.validate_native_proposal(root, p, row, manifest)


def test_unknown_and_closed_single_attempt_caps(opted, tmp_path):
    root = tmp_path / "custody"
    paths = prepare(root, "fable-timeout")
    Path(paths["proposals"]).unlink()
    out = tmp_path / "proposal-output/out.jsonl"
    called = []

    def timeout(body):
        called.append(body)
        raise TimeoutError("synthetic no response")

    result = proposer.propose(
        root,
        paths["manifest"],
        out,
        "fable-timeout",
        mode="live",
        cap_usd=4.09344,
        max_calls=2,
        transport=timeout,
    )
    ledger = json.loads(Path(result["ledger"]).read_text())
    assert ledger["closed"] and len(called) == 1
    assert (
        ledger["calls"][0]["reserved_usd"] == 2.04672
        and ledger["calls"][0]["settled_upper_usd"] is None
    )
    with pytest.raises(CropReviewError, match="closed"):
        proposer.propose(
            root,
            paths["manifest"],
            tmp_path / "proposal-output/other.jsonl",
            "fable-timeout",
            mode="live",
            cap_usd=4.09344,
            max_calls=2,
            transport=timeout,
        )
    assert len(called) == 1


@pytest.mark.parametrize("arm", ["fable", "sol"])
@pytest.mark.parametrize("disposition", ["approved", "held", "recrop", "error"])
def test_actual_driver_both_contracts_native_receipts_and_operator_holds(
    tmp_path, monkeypatch, arm, disposition
):
    # Use a temporary repo-local output root so normal driver paths/receipt
    # validation are exercised without polluting durable evidence identities.
    import tools.run_safety_qual_caller as wrapper

    monkeypatch.setattr(wrapper, "ROOT", ROOT)
    run_id = "test-fable088-" + tmp_path.name + "-" + arm + "-" + disposition
    result = run(arm, run_id, disposition=disposition)
    assert result["mechanics_pass"] and result["synthetic_authority_only"]
    fixture = Path(result["fixture"])
    policy = json.loads((fixture / "model-policy-before-operator.json").read_text())
    assert not policy["live_subjects"]
    inventory = json.loads((fixture / "custody/inventory.json").read_text())
    assert len(inventory["pages"]) == 3
    # These are test-created disposable artifacts, not campaign output.
    import shutil

    shutil.rmtree(fixture)
    shutil.rmtree(Path(result["output"]))


def test_fully_consistent_rehashed_substitution_cannot_replace_dispatch(
    tmp_path, monkeypatch, opted
):
    """Independent synthetic wallet is isolated; no real campaign record written."""
    from modules.common import crop_safety_fable_eval as native

    source = ROOT / "tests/fixtures/crop_review_offline/approved"
    body = safety.build_request(
        source / "S3-source.png", source / "images/S3.png", live=True
    )
    raw = json.dumps(synthetic_envelope("fable", "S3")).encode()
    directory = tmp_path / "raw"
    directory.mkdir()
    request = directory / "001-request.json"
    response = directory / "001-response.json"
    request.write_text(json.dumps(body))
    response.write_bytes(raw)
    record = {
        "stage": "caller:fable:S3",
        "arm": "fable",
        "model": "claude-fable-5-2",
        "semantic_eligible": True,
        "request": str(request),
        "response": str(response),
        "request_sha256": digest(request),
        "response_sha256": digest(response),
    }
    ledger = tmp_path / "ledger.json"
    ledger.write_text(
        json.dumps({"id": "088-fable52-safety-20261109", "calls": [record]})
    )
    monkeypatch.setattr(native, "DISPATCH_LEDGER", ledger)
    native.validate_dispatch_anchor(body, raw)
    changed = json.loads(raw)
    changed["content"][0]["text"] = json.dumps(
        {
            "verdict": "pass",
            "has_page_text": False,
            "excessive_blank": False,
            "reason": "Substituted but consistent forged content",
        }
    )
    # A proposal can rehash its own copy, but the separate dispatch raw stays.
    forged = json.dumps(changed).encode()
    with pytest.raises(CropReviewError, match="anchored"):
        native.validate_dispatch_anchor(body, forged)
    modified = copy.deepcopy(body)
    modified["output_config"]["effort"] = "max"
    with pytest.raises(CropReviewError, match="genuine combined dispatch"):
        native.validate_dispatch_anchor(modified, raw)


@pytest.mark.parametrize("origin", ["saved_evaluation_replay", "synthetic_test"])
def test_rehashed_evaluation_origin_cannot_skip_native_validation(
    tmp_path, monkeypatch, origin
):
    from modules.common.crop_review import evaluate, bound_paths

    result = run("fable", "test-origin088-" + tmp_path.name + "-" + origin)
    root = Path(result["fixture"]) / "custody"
    monkeypatch.setenv(ENV, CONTRACT)
    monkeypatch.setenv("DOC_WEB_SAFETY_QUAL_088_CONTEXT", "1")
    proposal_file = root / "proposals.jsonl"
    rows = list(read_jsonl(proposal_file))
    rows[0]["origin"] = origin
    proposal_file.write_text("".join(json.dumps(r) + "\n" for r in rows))
    named = {
        k: root
        / (k + ".jsonl" if k in ("manifest", "proposals", "decisions") else k + ".json")
        for k in ("manifest", "inventory", "proposals", "decisions", "authority")
    }
    with pytest.raises(CropReviewError, match="validated native origin"):
        evaluate(root, bound_paths(root, named), result["run_id"])
    import shutil

    shutil.rmtree(Path(result["fixture"]))
    shutil.rmtree(Path(result["output"]))


def test_evaluation_authority_can_never_become_real(tmp_path, monkeypatch):
    from modules.common.crop_review import evaluate, bound_paths

    result = run("fable", "test-authority088-" + tmp_path.name)
    root = Path(result["fixture"]) / "custody"
    monkeypatch.setenv(ENV, CONTRACT)
    monkeypatch.setenv("DOC_WEB_SAFETY_QUAL_088_CONTEXT", "1")
    named = {
        k: root
        / (k + ".jsonl" if k in ("manifest", "proposals", "decisions") else k + ".json")
        for k in ("manifest", "inventory", "proposals", "decisions", "authority")
    }
    original = json.loads((root / "authority.json").read_text())
    # Even with locally trusted operator trust-boundary, the synthetic flag is
    # propagated into release/build and cannot turn into publication authority.
    assert (
        evaluate(root, bound_paths(root, named), result["run_id"])[
            "synthetic_authority"
        ]
        is True
    )
    for removal in ("remove", "false"):
        altered = copy.deepcopy(original)
        if removal == "remove":
            altered.pop("synthetic_test")
        else:
            altered["synthetic_test"] = False
        (root / "authority.json").write_text(json.dumps(altered))
        with pytest.raises(CropReviewError, match="synthetic test authority"):
            evaluate(root, bound_paths(root, named), result["run_id"])
    import shutil

    shutil.rmtree(Path(result["fixture"]))
    shutil.rmtree(Path(result["output"]))


def test_sol_qualification_cannot_fall_through_unmetered_transport(monkeypatch):
    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setenv("DOC_WEB_SAFETY_QUAL_088_CONTEXT", "1")
    monkeypatch.delenv("DOC_WEB_SAFETY_QUAL_088_TRANSPORT", raising=False)
    monkeypatch.setattr(os, "getenv", lambda *args: pytest.fail("credential read"))
    import httpx

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: pytest.fail("network"))
    with pytest.raises(CropReviewError, match="combined campaign transport"):
        proposer.live_send({})


def test_external_anchor_requirement_survives_mode_origin_downgrade(
    tmp_path, monkeypatch
):
    root, manifest, proposals = fixture_proposals(tmp_path, monkeypatch)
    proposal = proposals[0]
    row = list(read_jsonl(manifest))[0]
    monkeypatch.setenv("DOC_WEB_SAFETY_QUAL_088_REQUIRE_ANCHOR", "1")
    proposal["requires_dispatch_anchor"] = True
    proposal.update(mode="mock", origin="mock_crop_safety")
    with pytest.raises(CropReviewError, match="external qualification phase"):
        safety.validate_native_proposal(root, proposal, row, manifest)
    proposal["requires_dispatch_anchor"] = False
    with pytest.raises(CropReviewError, match="anchor requirement"):
        safety.validate_native_proposal(root, proposal, row, manifest)
