import copy
import json
import pytest
import pplx_campaign as campaign


def response(arm="pplx"):
    probs = dict.fromkeys(campaign.legacy.LABELS, 0.0)
    probs["conformant"] = 1.0
    answer = {
        "type": "choice",
        "choice": "conformant",
        "confidence": 0.9,
        "probabilities": probs,
    }
    return {
        "model": campaign.MODELS[arm],
        "usage": {"input_tokens": 100, "output_tokens": 1},
        "answers": {"status": answer},
    }


def test_native_identity_and_invalid_probabilities_fail_closed():
    raw = response()
    assert campaign.parse("pplx", raw) == ("conformant", 0.9, 0.000002)
    for mutation in ("identity", "sum", "confidence", "usage"):
        bad = copy.deepcopy(raw)
        if mutation == "identity":
            bad["model"] = "pplx-decider-v1-27b"
        elif mutation == "sum":
            bad["answers"]["status"]["probabilities"]["mixed"] = 0.5
        elif mutation == "confidence":
            bad["answers"]["status"]["confidence"] = True
        else:
            bad["usage"]["input_tokens"] = -1
        with pytest.raises(ValueError):
            campaign.parse("pplx", bad)


def test_payloads_preserve_full_source_and_exclude_gold():
    for case in campaign.fixtures():
        for arm in campaign.ARMS:
            b = campaign.body(arm, case["input"])
            assert b["model"] == campaign.MODELS[arm]
            actual = (
                json.loads(b["input"])
                if arm == "decisions"
                else (
                    json.loads(b["messages"][1]["content"])
                    if arm == "gpt41"
                    else b["state"]
                )
            )
            assert actual == case["input"]
            assert "gold" not in b
            assert "rationale" not in b


def test_oversize_reservation_rejected_before_dispatch():
    with pytest.raises(RuntimeError, match="admission"):
        campaign.reserve("pplx", campaign.body("pplx", {"source": "x" * 5000}))


def test_unknown_exposure_blocks_additional_dispatch(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign, "OUT", tmp_path)
    campaign.write(
        tmp_path / "ledger.json", {"spent_usd": 0, "unknown_usd": 0.1, "calls": []}
    )
    with pytest.raises(RuntimeError, match="Unresolved exposure"):
        campaign.call("pplx", campaign.body("pplx", {}), "new")


def test_hard_cap_rejects_before_dispatch(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign, "OUT", tmp_path)
    campaign.write(
        tmp_path / "ledger.json", {"spent_usd": 2, "unknown_usd": 0, "calls": []}
    )
    with pytest.raises(RuntimeError, match="Hard USD2"):
        campaign.call("pplx", campaign.body("pplx", {}), "new")
