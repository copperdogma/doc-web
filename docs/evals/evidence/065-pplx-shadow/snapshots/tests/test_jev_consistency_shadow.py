import copy
import json

import pytest

from modules.validate.plan_onward_document_consistency_v1 import jev_shadow as shadow

ENV = {"DOC_WEB_JEV_SHADOW": "enabled", "DOC_WEB_TYPESAFE_RUNTIME_API_KEY": "test-only"}


def inputs(count=1):
    chapters = [
        {
            "chapter_basename": f"chapter-{i}.html",
            "signals": {"suggested_issue_types": []},
            "signal_examples": {
                "suspicious_rows": [
                    {"reason": "do not transmit", "row_preview": "Synthetic row"}
                ]
            },
            "page_profiles": [],
            "current_detector": {"flagged": False},
        }
        for i in range(count)
    ]
    plan = {
        "pattern_conventions": [
            {
                "member_chapters": [c["chapter_basename"] for c in chapters],
                "canonical_headers": ["NAME", "BORN"],
                "document_local_conventions": {"rows": "Preserve meanings"},
            }
        ]
    }
    auth = {
        "chapters": [
            {"chapter_basename": c["chapter_basename"], "status": "row_semantic_issue"}
            for c in chapters
        ]
    }
    return chapters, plan, auth


def response(label="conformant", confidence=0.95):
    probs = {k: (1 if k == label else 0) for k in shadow.LABELS}
    return {
        "model": shadow.MODEL,
        "answers": {
            "status": {
                "type": "choice",
                "choice": label,
                "confidence": confidence,
                "probabilities": probs,
            }
        },
        "usage": {"input_tokens": 500, "output_tokens": 20},
    }


def run(reply=None, count=1, env=ENV):
    return shadow.run_shadow(
        *inputs(count),
        env=env,
        request=lambda p, k: response() if reply is None else reply,
    )


def test_off_key_alone_and_eval_key_not_runtime():
    assert run(env={"DOC_WEB_TYPESAFE_RUNTIME_API_KEY": "unused"}) is None
    out = run(
        env={"DOC_WEB_JEV_SHADOW": "enabled", "DOC_WEB_TYPESAFE_API_KEY": "eval-only"}
    )
    assert out["status"] == "missing_runtime_key" and out["dispatched"] == 0


def test_uncertain_preserved_despite_low_confidence():
    row = run(response("uncertain", 0.1))["chapters"][0]
    assert (row["shadow_status"], row["route"]) == ("uncertain", "review")


def test_low_confidence_reuses_authoritative_no_extra_call():
    row = run(response("conformant", 0.2))["chapters"][0]
    assert row["shadow_status"] == "row_semantic_issue"
    assert row["route"] == "planner_fallback"


def test_layout_guard_cannot_be_cleared():
    chapters, plan, auth = inputs()
    chapters[0]["signals"]["suggested_issue_types"] = ["fused_boygirl_headers"]
    out = shadow.run_shadow(
        chapters, plan, auth, env=ENV, request=lambda p, k: response()
    )
    assert out["chapters"][0]["reason"] == "deterministic_layout_guard"
    assert out["chapters"][0]["shadow_status"] == "uncertain"


def test_cost_cap_and_skip_coverage():
    out = run(count=6)
    assert out["total_chapters"] == 6 and out["dispatched"] == 3
    assert [r["reason"] for r in out["chapters"]][3:] == ["run_limit"] * 3
    assert (
        out["known_cost_usd"] + out["unknown_cost_reserved_usd"] <= shadow.MAX_RUN_USD
    )


def test_error_is_redacted_reserved_and_no_retry():
    calls = []

    def fail(p, k):
        calls.append(p)
        raise RuntimeError("secret-value private-text")

    out = shadow.run_shadow(*inputs(4), env=ENV, request=fail)
    assert len(calls) == 3
    assert out["unknown_cost_reserved_usd"] == shadow.MAX_RUN_USD
    assert "secret-value" not in json.dumps(out) and "private-text" not in json.dumps(
        out
    )


def test_input_limit_and_missing_conventions_skip_before_call():
    chapters, plan, auth = inputs()
    chapters[0]["signal_examples"]["big"] = "x" * shadow.MAX_STATE_BYTES
    out = shadow.run_shadow(
        chapters, plan, auth, env=ENV, request=lambda *a: pytest.fail("dispatch")
    )
    assert out["chapters"][0]["reason"] == "input_limit"
    out = shadow.run_shadow(
        chapters, {}, auth, env=ENV, request=lambda *a: pytest.fail("dispatch")
    )
    assert out["chapters"][0]["reason"] == "missing_conventions"


def test_payload_no_verdict_or_paths_and_report_no_text():
    chapters, plan, auth = inputs()
    before = copy.deepcopy((chapters, plan, auth))
    payloads = []

    def request(p, key):
        payloads.append(p)
        return response()

    out = shadow.run_shadow(chapters, plan, auth, env=ENV, request=request)
    state = json.dumps(payloads[0]["state"])
    assert "chapter-0" not in state and "do not transmit" not in state
    assert "suggested_issue_types" not in state and "current_detector" not in state
    assert "Synthetic row" not in json.dumps(out)
    assert (chapters, plan, auth) == before
    assert (
        out["chapters"][0]["probabilities"]
        == response()["answers"]["status"]["probabilities"]
    )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r.update(model="jev-latest"),
        lambda r: r.update(status="failed"),
        lambda r: r["usage"].update(input_tokens=True),
        lambda r: r["usage"].update(input_tokens=64001),
        lambda r: r["answers"]["status"].update(confidence=float("nan")),
        lambda r: r["answers"]["status"]["probabilities"].update(uncertain=0.5),
        lambda r: r["answers"]["status"].update(choice="mixed"),
    ],
)
def test_invalid_native_contract(mutation):
    raw = response()
    mutation(raw)
    with pytest.raises(ValueError):
        shadow.parse_response(raw)


def test_sidecar_failure_does_not_escape_and_disabled_removes_stale(tmp_path):
    file = tmp_path / "sidecar.json"
    file.write_text("stale")
    assert shadow.write_shadow(file, *inputs(), env={})
    assert not file.exists()
    assert not shadow.write_shadow(
        tmp_path / "absent" / "x", *inputs(), env=ENV, request=lambda p, k: response()
    )


def test_native_transport_pin_timeout_bound_no_redirect(monkeypatch):
    observed = {}

    class Reply:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, n):
            assert n == shadow.MAX_RESPONSE_BYTES + 1
            return json.dumps(response()).encode()

    class Opener:
        def open(self, req, timeout):
            observed.update(url=req.full_url, timeout=timeout)
            return Reply()

    def opener(handler):
        assert isinstance(handler, shadow.NoRedirect)
        return Opener()

    monkeypatch.setattr(shadow.urllib.request, "build_opener", opener)
    assert (
        shadow.native_request(shadow.request_payload({}), "test")["model"]
        == shadow.MODEL
    )
    assert observed == {"url": shadow.ENDPOINT, "timeout": 2.0}


def test_wall_deadline_stops_waiting_for_slow_body(monkeypatch):
    import threading
    import time

    finished = threading.Event()

    def slow(*args):
        finished.wait(0.5)
        return response()

    monkeypatch.setattr(shadow, "_native_http", slow)
    monkeypatch.setattr(shadow, "TIMEOUT_SECONDS", 0.02)
    start = time.monotonic()
    try:
        with pytest.raises(TimeoutError):
            shadow.native_request({}, "test-only")
        assert time.monotonic() - start < 0.2
    finally:
        finished.set()


def test_stale_sidecar_removed_when_attempt_fails_before_write(tmp_path):
    file = tmp_path / "shadow.json"
    file.write_text("stale-success")
    chapters, plan, auth = inputs()
    chapters[0]["signals"]["not_json"] = object()
    assert not shadow.write_shadow(file, chapters, plan, auth, env=ENV)
    assert not file.exists()


def test_report_binds_inputs_plan_and_run_without_mutation():
    chapters, plan, auth = inputs()
    auth["run_id"] = "synthetic-run"
    report = shadow.run_shadow(
        chapters, plan, auth, env=ENV, request=lambda p, k: response()
    )
    assert report["run_id"] == "synthetic-run"
    assert len(report["input_sha256"]) == len(report["plan_sha256"]) == 64
    before = report["input_sha256"]
    chapters[0]["signals"]["table_count"] = 2
    assert (
        shadow.run_shadow(
            chapters, plan, auth, env=ENV, request=lambda p, k: response()
        )["input_sha256"]
        != before
    )


def test_request_receives_detached_convention_snapshot():
    chapters, plan, auth = inputs()
    original = copy.deepcopy(plan)

    def mutate(payload, key):
        payload["state"]["conventions"]["canonical_headers"].append("injected")
        payload["state"]["extracted_evidence"]["signals"]["new"] = True
        return response()

    shadow.run_shadow(chapters, plan, auth, env=ENV, request=mutate)
    assert plan == original
    assert "new" not in chapters[0]["signals"]
