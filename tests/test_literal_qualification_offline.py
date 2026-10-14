"""Native transport/retention topology proof using only public synthetic gold.

The integration fixture runs the actual PDF driver, SDK, Google transport,
reader CLI and export driver once. Its quality evidence is explicitly MOCK.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from bs4 import BeautifulSoup
import pytest

from benchmarks.scripts import literal_qualification_offline as offline


def test_frozen_gold_mock_preserves_hold_and_spans():
    from modules.extract.ocr_ai_gpt51_v1.main import _extract_ocr_metadata, sanitize_html

    rows = {
        row["case_id"]: row
        for row in offline.read(offline.PANEL / "manifest.json")["pages"]
    }
    for case, row in rows.items():
        actual = json.loads(offline.mock_output(f"reader-{case}-astra"))
        assert actual == offline.read(offline.PANEL / row["gold"])
        assert (
            sum(len(table["uncertain_cells"]) for table in actual["tables"])
            == row["uncertain_cells"]
        )
        assert row["cell_slots"] <= 40
        soup = BeautifulSoup(offline.mock_output("ocr-" + case), "html.parser")
        assert len(soup.find_all("table")) == row["tables"]
        stripped, metadata, _, warning = _extract_ocr_metadata(
            offline.mock_output("ocr-" + case)
        )
        assert warning is None and metadata["ocr_quality"] == 1.0
        assert len(BeautifulSoup(sanitize_html(stripped), "html.parser").find_all("table")) == row["tables"]
        for span in row["spans"]:
            table = soup.find_all("table")[span["table_index"]]
            cell = table.find_all("tr")[span["row"]].find_all(
                ["th", "td"], recursive=False
            )[span["cell"]]
            assert int(cell.get("rowspan", 1)) == span["rowspan"]
            assert int(cell.get("colspan", 1)) == span["colspan"]
    with pytest.raises(RuntimeError, match="Only initial"):
        offline.mock_output("repeat-N1-astra")


def test_environment_has_only_dummy_keys_and_nonexistent_dotenv(tmp_path, monkeypatch):
    monkeypatch.setenv("DOC_WEB_OPENAI_API_KEY", "inherited-secret-must-not-propagate")
    monkeypatch.setenv("GOOGLE_API_KEY", "inherited-secret-must-not-propagate")
    monkeypatch.setenv("HTTP_PROXY", "inherited-proxy-must-not-propagate")
    env = offline.clean_environment(
        tmp_path / "startup", tmp_path / "campaign.json", tmp_path
    )
    assert env["DOC_WEB_ENV_FILE"] == str(tmp_path / "no-credentials.env")
    assert not Path(env["DOC_WEB_ENV_FILE"]).exists()
    assert (
        env["OPENAI_API_KEY"]
        == env["DOC_WEB_OPENAI_API_KEY"]
        == env["DOC_WEB_GEMINI_API_KEY"]
        == offline.DUMMY
    )
    assert "GOOGLE_API_KEY" not in env and "HTTP_PROXY" not in env
    assert "inherited-secret-must-not-propagate" not in env.values()


def test_mock_native_envelopes_parse_as_actual_provider_contracts():
    from openai.types.responses import Response
    from modules.common.google_table_source_review import native_google_output

    for stage in ("ocr-N1", "reader-N1-astra"):
        text = offline.mock_output(stage)
        response = Response.model_validate(offline.native_envelope(stage, text))
        assert response.output_text == text
        assert response.status == "completed" and response.model == "gpt-6-astra"
    text = offline.mock_output("reader-N1-argon")
    assert (
        native_google_output(offline.native_envelope("reader-N1-argon", text, True))
        == text
    )


def test_stage_environment_restores_parent_even_after_error(tmp_path):
    before = dict(os.environ)
    env = offline.clean_environment(tmp_path, tmp_path / "campaign.json", tmp_path)
    with pytest.raises(ValueError):
        with offline.stage_environment(env, "ocr-N1"):
            assert os.environ["DOC_WEB_LITERAL_STAGE"] == "ocr-N1"
            assert os.environ["DOC_WEB_LITERAL_OFFLINE"] == "1"
            raise ValueError("test")
    assert dict(os.environ) == before


def test_sockets_fail_closed_and_namespaces_are_bounded():
    with pytest.raises(RuntimeError, match="forbids socket"):
        offline.deny_socket()
    for name in ("live", "offline/../../live", "offline-x/y", "offline-*"):
        with pytest.raises(ValueError, match="namespace"):
            offline.run_proof(namespace=name)


@pytest.fixture(scope="module")
def proof(tmp_path_factory):
    # An explicitly supplied, current hash-bound packet avoids repeating the
    # unchanged minute-long integration run during close-out validation.
    supplied = os.environ.get("DOC_WEB_LITERAL_OFFLINE_PROOF")
    if supplied:
        path = Path(supplied).resolve()
    else:
        result_root = tmp_path_factory.mktemp("literal-offline") / "proof"
        namespace = "offline-test-" + uuid.uuid4().hex[:12]
        command = [
            sys.executable,
            str(offline.ROOT / "benchmarks/scripts/literal_qualification_offline.py"),
            "--result-root",
            str(result_root),
            "--namespace",
            namespace,
        ]
        result = subprocess.run(
            command,
            cwd=offline.ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=300,
        )
        assert result.returncode == 0, result.stdout
        path = result_root / "proof.json"
    data = offline.read(path)
    assert data["code_sha256"][
        "benchmarks/scripts/literal_qualification_offline.py"
    ] == offline.sha(
        (
            offline.ROOT / "benchmarks/scripts/literal_qualification_offline.py"
        ).read_bytes()
    )
    assert data["source_manifest_sha256"] == offline.sha(
        (offline.PANEL / "manifest.json").read_bytes()
    )
    root = Path(data["result_root"])
    for relative, digest in data["artifact_sha256"].items():
        assert offline.sha((root / relative).read_bytes()) == digest, relative
    frozen = offline.read(root / "evidence/freeze.json")
    for group in ("code_sha256", "fixture_sha256"):
        for relative, digest in frozen[group].items():
            if relative == "benchmarks/scripts/qualify_argon_literal.py":
                assert digest == data["initial_producing_harness_sha256"]
                assert offline.sha((offline.ROOT / relative).read_bytes()) == data["export_producing_harness_sha256"]
                continue
            assert offline.sha((offline.ROOT / relative).read_bytes()) == digest, (
                relative
            )
    return data


def test_actual_guard_counts_only_24_initial_native_mock_posts(proof):
    assert proof["evidence_class"] == offline.LABEL
    assert proof["actual_provider_spend_usd"] == 0
    assert proof["network_connections"] == 0
    assert proof["guard_mock_post_count"] == 24
    assert proof["ocr_mock_posts"] == 8 and proof["reader_mock_posts"] == 16
    assert proof["exports_additional_posts"] == proof["holds_additional_posts"] == 0
    root = Path(proof["result_root"])
    ledger = offline.read(root / "guard/ledger.json")
    config = offline.read(root / "evidence/campaign.json")
    assert ledger["config_sha256"] == offline.sha(
        (root / "evidence/campaign.json").read_bytes()
    )
    assert len(config["matrix"]) == 32 and config["max_calls"] == 33
    assert len(ledger["calls"]) == 24 and not ledger["closed"]
    stages = {entry["stage"]: entry for entry in config["matrix"]}
    transport = [
        json.loads(line)
        for line in (root / "guard/mock-transport.jsonl").read_text().splitlines()
    ]
    for index, call in enumerate(ledger["calls"], 1):
        assert call["sequence"] == index
        assert call["request_sha256"] == stages[call["stage"]]["request_sha256"]
        assert call["status_code"] == 200
        assert call["served_model"] == call["model"]
        assert call["usage"]["input_tokens"] == call["usage"]["output_tokens"] == 100
        response_path = root / f"guard/response-{index:03d}.json"
        assert call["response_sha256"] == offline.sha(response_path.read_bytes())
        assert transport[index - 1]["guard_intent_sequence"] == index
        assert transport[index - 1]["actual_provider_spend_usd"] == 0
        assert transport[index - 1]["request_sha256"] == call["request_sha256"]
    startup = (root / "mock-startup/sitecustomize.py").read_text()
    assert startup.index("socket.socket.connect = deny") < startup.index(
        "import install_backend"
    )


def test_four_real_driver_exports_bind_exact_final_tables_and_native_receipts(proof):
    assert {(entry["group"], entry["arm"]) for entry in proof["positive_exports"]} == {
        (group, arm) for group in ("N", "R") for arm in ("astra", "argon")
    }
    from doc_web.literal_tables import compare_tables

    for export in proof["positive_exports"]:
        path = Path(export["proof"])
        assert offline.sha(path.read_bytes()) == export["proof_sha256"]
        data = offline.read(path)
        assert data["comparison"]["pass"]
        html_root = Path(data["manifest"]).parent
        manifest = offline.read(data["manifest"])
        assert (
            offline.sha(Path(data["manifest"]).read_bytes()) == data["manifest_sha256"]
        )
        qualification_path = (
            html_root / "provenance/literal-fidelity/qualification.json"
        )
        qualification = offline.read(qualification_path)
        assert qualification == data["qualification"]
        assert (
            qualification["status"] == "qualified"
            and qualification["scope"] == "table_literal_text"
        )
        assert len(qualification["reports"]) == 3
        assert manifest["literal_fidelity"]["qualification_sha256"] == offline.sha(
            qualification_path.read_bytes()
        )
        for retained in qualification["reports"]:
            report_path = html_root / retained["path"]
            assert offline.sha(report_path.read_bytes()) == retained["sha256"]
            report = offline.read(report_path)
            assert len(report["requests"]) == 1
            request = report["requests"][0]
            assert "offline" in request["response_id"]
            assert (
                request["requested_model"]
                == {"astra": "gpt-6-astra", "argon": "gemini-4-argon"}[export["arm"]]
            )
            native = request["native_response_json"]
            assert offline.sha(native.encode()) == request["native_response_sha256"]
        for entry in qualification["entries"]:
            assert (
                offline.sha((html_root / entry["path"]).read_bytes()) == entry["sha256"]
            )
        pages = {
            row["case_id"]: row
            for row in offline.read(offline.PANEL / "manifest.json")["pages"]
        }
        expected = "".join(
            table["html"]
            for case in data["source_cases"]
            for table in offline.read(offline.PANEL / pages[case]["gold"])["tables"]
        )
        actual = "".join(
            (html_root / entry["path"]).read_text()
            for entry in qualification["entries"]
        )
        assert compare_tables(expected, actual)["pass"]


def test_real_driver_holds_both_ambiguous_pages_for_both_authorities(proof):
    assert {(entry["case"], entry["arm"]) for entry in proof["negative_holds"]} == {
        (case, arm) for case in ("A1", "A2") for arm in ("astra", "argon")
    }
    for hold in proof["negative_holds"]:
        assert hold["driver_returncode"] != 0 and hold["review_returncode"] == 2
        assert hold["manifest_absent"] and hold["additional_posts"] == 0
        report_path = Path(hold["report_path"])
        assert offline.sha(report_path.read_bytes()) == hold["report_sha256"]
        report = offline.read(report_path)
        assert report["status"] != "verified"
        assert any(table["review"]["uncertain_cells"] for table in report["tables"])
        output = offline.ROOT / "output/runs" / hold["run_id"]
        assert not (output / "output/html/manifest.json").exists()
        assert not (
            output / "output/html/provenance/literal-fidelity/qualification.json"
        ).exists()
