"""Native transport/retention topology proof using only public synthetic gold.

Historical Astra/Argon benchmark controls. The current driver proof lives in
test_canonical_table_reader.py and uses the sole product authority.
"""

import json
import os
from pathlib import Path

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
    from benchmarks.providers.historical_literal_readers.google_table_source_review import native_google_output

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
