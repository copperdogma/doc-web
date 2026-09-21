import importlib.util
from pathlib import Path
import pytest

s = importlib.util.spec_from_file_location(
    "observation_run", Path(__file__).with_name("run.py")
)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)


def test_duplicate_and_budget(tmp_path):
    c = m.Custody(tmp_path / "run")
    c.dispatch("planner", {}, 0.14)
    with pytest.raises(ValueError, match="duplicate"):
        c.dispatch("planner", {}, 0)
    with pytest.raises(ValueError, match="spend"):
        c.dispatch("jev", {}, 0.02)
    assert len(c.names) == 1


def test_custody_before_parse_and_no_overwrite(tmp_path):
    c = m.Custody(tmp_path / "run")
    c.dispatch("jev", {}, 0.002688)
    c.response("jev", {"malformed_envelope": True})
    assert "malformed_envelope" in (c.directory / "jev.response.json").read_text()
    with pytest.raises(FileExistsError):
        c.response("jev", {})
    with pytest.raises(FileExistsError):
        m.Custody(tmp_path / "run")


def test_seven_call_ceiling(tmp_path):
    c = m.Custody(tmp_path / "run")
    for i in range(7):
        c.dispatch(str(i), {}, 0)
    with pytest.raises(ValueError, match="cap"):
        c.dispatch("8", {}, 0)


def test_identical_payloads_keep_attempt_identity():
    names = m.AttemptNames()
    a = {"same": "body"}
    b = {"same": "body"}
    assert names.register(a) == "jev-1"
    assert names.register(b) == "jev-2"
    assert names.lookup(a) == "jev-1" and names.lookup(b) == "jev-2"
    with pytest.raises(ValueError):
        names.register(a)


def test_planner_contract():
    from types import SimpleNamespace as N

    good = N(
        model="gpt-4.1-2025-04-14",
        choices=[N(finish_reason="stop")],
        usage=N(prompt_tokens=50, completion_tokens=100),
    )
    m.verify_planner(good, 100)
    good.model = "other"
    with pytest.raises(AssertionError):
        m.verify_planner(good, 100)
    good.model = "gpt-4.1-2025-04-14"
    good.usage.prompt_tokens = True
    with pytest.raises(AssertionError):
        m.verify_planner(good, 100)
