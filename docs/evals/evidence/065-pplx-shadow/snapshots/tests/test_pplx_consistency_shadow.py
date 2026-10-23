import copy
import json
from pathlib import Path
import subprocess
import types
import pytest
from modules.validate.plan_onward_document_consistency_v1 import (
    main as planner,
    pplx_shadow as shadow,
)
from modules.validate.plan_onward_document_consistency_v1.pplx_evidence import observed
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
ENV = {"DOC_WEB_PPLX_SHADOW_EVAL": "enabled", "DOC_WEB_PERPLEXITY_API_KEY": "offline"}


def inputs(n=1):
    chapters = [
        {
            "chapter_basename": f"chapter-{j}.html",
            "signals": {"suggested_issue_types": []},
            "signal_examples": {},
            "page_profiles": [],
            "source_context": {
                "expected_page_count": 1,
                "available_page_count": 1,
                "missing_pages": [],
            },
            "runtime_evidence": {
                "chapter": {"observed_html": "<table><tr><td>Ada</td></tr></table>"},
                "source_unanchored_notes": [],
            },
            "current_detector": {"flagged": False},
        }
        for j in range(n)
    ]
    plan = {
        "pattern_conventions": [
            {
                "member_chapters": [c["chapter_basename"] for c in chapters],
                "canonical_headers": ["NAME", "BORN"],
                "document_local_conventions": {"rows": "Preserve source"},
            }
        ]
    }
    auth = {
        "chapters": [
            {"chapter_basename": c["chapter_basename"], "status": "conformant"}
            for c in chapters
        ]
    }
    return chapters, plan, auth


def response(label="conformant", confidence=0.95):
    return {
        "model": shadow.MODEL,
        "usage": {"input_tokens": 500, "output_tokens": 1},
        "answers": {
            "status": {
                "type": "choice",
                "choice": label,
                "confidence": confidence,
                "probabilities": {k: float(k == label) for k in shadow.LABELS},
            }
        },
    }


def test_disabled_no_calls_and_key_alone():
    assert (
        shadow.run_shadow(
            *inputs(),
            env={"DOC_WEB_PERPLEXITY_API_KEY": "offline"},
            request=lambda *a: pytest.fail("dispatch"),
        )
        is None
    )


def test_missing_key_denominator_review():
    r = shadow.run_shadow(
        *inputs(3),
        env={"DOC_WEB_PPLX_SHADOW_EVAL": "enabled"},
        request=lambda *a: pytest.fail("dispatch"),
    )
    assert r["dispatched"] == 0 and len(r["chapters"]) == 3
    assert all(c["shadow_status"] == "uncertain" for c in r["chapters"])


@pytest.mark.parametrize(
    "incomplete", ["missing_page", "unanchored_note", "no_observed_evidence"]
)
@pytest.mark.parametrize("failure", [False, True])
def test_observable_completeness_never_clean(incomplete, failure):
    c, p, a = inputs()
    if incomplete == "missing_page":
        c[0]["source_context"].update(available_page_count=0, missing_pages=[1])
    elif incomplete == "unanchored_note":
        c[0]["runtime_evidence"]["source_unanchored_notes"] = ["One child; no anchor"]
    else:
        c[0]["runtime_evidence"] = {}

    def call(*args):
        if failure:
            raise TimeoutError("offline")
        return response()

    r = shadow.run_shadow(c, p, a, env=ENV, request=call)
    assert r["chapters"][0]["shadow_status"] == "uncertain"


def test_uncertainty_layout_conflict_input_and_run_limits():
    c, p, a = inputs(5)
    c[0]["signals"]["suggested_issue_types"] = ["fused_boygirl_headers"]
    a["chapters"][1]["status"] = "uncertain"
    r = shadow.run_shadow(c, p, a, env=ENV, request=lambda *a: response())
    assert r["chapters"][0]["reason"] == "deterministic_layout_guard"
    assert r["chapters"][1]["reason"] == "authoritative_uncertainty"
    assert r["dispatched"] == 3 and len(r["chapters"]) == 5
    assert r["chapters"][3]["reason"] == "run_limit"
    p["pattern_conventions"][0]["convention_conflicts"] = ["unsupported policy"]
    r = shadow.run_shadow(c, p, a, env=ENV, request=lambda *a: pytest.fail("dispatch"))
    assert r["dispatched"] == 0 and all(
        x["reason"] == "conflicting_conventions" for x in r["chapters"]
    )
    p["pattern_conventions"][0].pop("convention_conflicts")
    c[0]["runtime_evidence"]["chapter"]["observed_html"] = "x" * shadow.MAX_STATE_BYTES
    r = shadow.run_shadow(
        c[:1], p, a, env=ENV, request=lambda *a: pytest.fail("dispatch")
    )
    assert r["chapters"][0]["reason"] == "input_limit"


def test_malformed_safe_and_originals_unchanged():
    data = inputs()
    before = copy.deepcopy(data)
    r = shadow.run_shadow(*data, env=ENV, request=lambda *a: {})
    assert r["chapters"][0]["route"] == "planner_fallback"
    assert r["unknown_cost_reserved_usd"] == shadow.RESERVE_USD
    assert data == before


def test_observed_attachment_attributes_and_span_survive():
    soup = BeautifulSoup(
        '<table data-page-break-before="true"><tr><th colspan="2">Name</th></tr><tr><td rowspan="2">Ada</td></tr></table><aside data-person="Ada"><a href="#Ada">child</a></aside>',
        "html.parser",
    )
    value = observed(soup)
    assert value["tables"][0]["cell_attributes"][0][0]["colspan"] == "2"
    assert value["tables"][0]["cell_attributes"][1][0]["rowspan"] == "2"
    assert value["tables"][0]["page_break_before"]
    assert value["note_attachments"][0]["attributes"]["data-person"] == "Ada"
    assert value["note_attachments"][0]["links"][0]["href"] == "#Ada"
    assert not value["unanchored_notes"]


def test_evidence_switch_disabled_exact_original_dossier_prompt(monkeypatch):
    original = types.ModuleType("original_planner")
    code = subprocess.check_output(
        [
            "git",
            "show",
            "HEAD:modules/validate/plan_onward_document_consistency_v1/main.py",
        ],
        cwd=ROOT,
        text=True,
    )
    exec(compile(code, "original_planner.py", "exec"), original.__dict__)
    monkeypatch.delenv("DOC_WEB_PPLX_SHADOW_EVIDENCE", raising=False)
    monkeypatch.setattr(planner, "_utc", lambda: "fixed")
    original._utc = lambda: "fixed"
    source = ROOT / "benchmarks/pplx-shadow/corpus/doc-01"
    chapters = [
        json.loads(x) for x in (source / "chapters.jsonl").read_text().splitlines()
    ]
    pages = planner._load_page_rows(str(source / "pages.jsonl"))
    args = dict(
        chapters_path=str(source / "chapters.jsonl"),
        pages_path=str(source / "pages.jsonl"),
        flag_threshold=25,
    )
    current = planner.build_document_dossier(chapters, pages, **args)
    old = original.build_document_dossier(chapters, pages, **args)
    assert current == old
    assert planner._build_prompt(current) == original._build_prompt(old)
