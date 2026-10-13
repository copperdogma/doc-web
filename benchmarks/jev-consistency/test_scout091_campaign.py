from importlib.util import module_from_spec, spec_from_file_location
import json
import tarfile
from pathlib import Path
import pytest

spec = spec_from_file_location(
    "scout091_test", Path(__file__).with_name("scout091_campaign.py")
)
m = module_from_spec(spec)
spec.loader.exec_module(m)


def native_response(arm):
    # Regression fixtures must work in a fresh clone without ignored HTTP originals.
    with tarfile.open(m.OUT / "receipts.tar.gz", "r:gz") as archive:
        response = archive.extractfile("native-" + arm + ".response.json")
        assert response is not None
        return json.loads(response.read())


def test_lossless_scaledown_state_all_fields():
    state = {
        "conventions": {"headers": ["A", "B"]},
        "source_evidence": "á source",
        "tables": [{"rows": [["one", "two"]]}],
        "extra": {"owned": True},
    }
    b = m.body("scaledown", state)
    assert set(b["state"]) == {"text"}
    assert json.loads(b["state"]["text"]) == state
    assert b["state"]["text"] == m.state_json(state)


def test_drex_short_reservation_rejects_overlong_state():
    with pytest.raises((ValueError, AssertionError)):
        m.reserve("drex", m.body("drex", {"text": "x" * 10000}), "text")


def test_nonzero_accounting_output_tokens_native_typed_is_valid():
    for arm in ["drex", "scaledown", "solar"]:
        raw = native_response(arm)
        label, conf, cost = m.parse(arm, raw, m.legacy.LABELS)
        assert raw["usage"]["output_tokens"] > 0
        assert label in m.legacy.LABELS and 0 <= conf <= 1 and cost >= 0


def test_wrong_served_model_or_provider_rejected():
    raw = native_response("drex")
    raw["model"] = "nace-ai/drex-v1.5"
    with pytest.raises(ValueError):
        m.parse("drex", raw, m.legacy.LABELS)
    raw["model"] = m.MODELS["drex"]
    raw["provider"] = "Different"
    with pytest.raises(ValueError):
        m.parse("drex", raw, m.legacy.LABELS)


def test_hard_cap_and_closed_ledger_do_not_send(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "OUT", tmp_path)
    m.write(
        tmp_path / "text-ledger.json",
        {"cap_usd": 4, "spent_usd": 4.0, "unknown_usd": 0, "calls": []},
    )
    with pytest.raises(RuntimeError, match="cap"):
        m.call("clef", m.body("clef", {}), "never", "text", m.legacy.LABELS)
    m.write(tmp_path / "text-ledger.json", {"closed": True})
    with pytest.raises(RuntimeError, match="closed"):
        m.call("clef", m.body("clef", {}), "never", "text", m.legacy.LABELS)


def test_actual_two_image_body_keeps_uri_bytes():
    b = m.image_body("page-012-000", "clef")
    g = m.image_body("page-012-000", "gpt55")
    assert len(b["state"]) == 3
    assert [x["image_url"]["url"] for x in b["state"] if isinstance(x, dict)] == [
        x["image_url"] for x in g["input"][0]["content"] if x["type"] == "input_image"
    ]
    assert b["provider"]["allow_fallbacks"] is False


def test_preflight_cannot_overwrite_closed_campaign_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "OUT", tmp_path)
    ledger = tmp_path / "text-ledger.json"
    ledger.write_text('{"closed": true}')
    frozen = tmp_path / "preflight.json"
    frozen.write_text("retained paid evidence")
    with pytest.raises(RuntimeError, match="closed campaign evidence"):
        m.preflight()
    assert frozen.read_text() == "retained paid evidence"
    assert ledger.read_text() == '{"closed": true}'
