import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import driver


def _core(**updates):
    return {
        "id": "source-1",
        "seq": 0,
        "page": 1,
        "kind": "text",
        "text": "Literal source",
        **updates,
    }


@pytest.mark.parametrize(
    "bad_row",
    [
        {"seq": 1, "page": 1, "kind": "text"},
        _core(error="upstream extraction failed"),
        ["not an object"],
        None,
    ],
)
def test_invalid_row_fails_without_changing_producer_bytes(tmp_path, bad_row):
    artifact = tmp_path / "elements.jsonl"
    original = "\n".join(json.dumps(r) for r in [_core(), bad_row]) + "\n"
    artifact.write_text(original)
    with pytest.raises(ValueError, match="row 2"):
        driver.stamp_artifact(str(artifact), "element_core_v1", "probe", "run")
    assert artifact.read_text() == original


def test_malformed_json_preserves_original(tmp_path):
    artifact = tmp_path / "elements.jsonl"
    original = json.dumps(_core()) + '\n{"broken":\n'
    artifact.write_text(original)
    with pytest.raises(ValueError):
        driver.stamp_artifact(str(artifact), "element_core_v1", "probe", "run")
    assert artifact.read_text() == original


@pytest.mark.parametrize("envelope", ["object", "list", "jsonl"])
def test_stamping_preserves_document_envelope(tmp_path, envelope):
    artifact = tmp_path / ("artifact.jsonl" if envelope == "jsonl" else "artifact.json")
    data = [_core(), _core(id="source-2", seq=1)] if envelope == "list" else _core()
    artifact.write_text(
        json.dumps(data, indent=2) if envelope != "jsonl" else json.dumps(data) + "\n"
    )
    driver.stamp_artifact(str(artifact), "page_doc_v1", "probe", "run")
    output = json.loads(artifact.read_text())
    assert isinstance(output, list) == (envelope == "list")
    rows = output if envelope == "list" else [output]
    assert [row["text"] for row in rows] == ["Literal source"] * len(rows)
    assert all(row["run_id"] == "run" for row in rows)


def test_atomic_replacement_failure_preserves_original(tmp_path, monkeypatch):
    artifact = tmp_path / "elements.jsonl"
    original = json.dumps(_core()) + "\n"
    artifact.write_text(original)

    def fail_replace(source, destination):
        assert Path(source).parent == artifact.parent
        assert Path(destination) == artifact
        raise OSError("controlled publication failure")

    monkeypatch.setattr(driver.os, "replace", fail_replace)
    with pytest.raises(OSError, match="controlled publication"):
        driver.stamp_artifact(str(artifact), "page_doc_v1", "probe", "run")
    assert artifact.read_text() == original
    assert list(tmp_path.iterdir()) == [artifact]


def test_serialization_failure_preserves_original(tmp_path, monkeypatch):
    artifact = tmp_path / "elements.jsonl"
    original = json.dumps(_core()) + "\n"
    artifact.write_text(original)

    def fail_serialization(*args, **kwargs):
        raise TypeError("controlled serialization failure")

    monkeypatch.setattr(driver.json, "dumps", fail_serialization)
    with pytest.raises(TypeError, match="controlled serialization"):
        driver.stamp_artifact(str(artifact), "page_doc_v1", "probe", "run")
    assert artifact.read_text() == original
    assert list(tmp_path.iterdir()) == [artifact]


def test_invalid_json_list_member_preserves_original(tmp_path):
    artifact = tmp_path / "elements.json"
    original = json.dumps([_core(), {"page": 2}], indent=2)
    artifact.write_text(original)
    with pytest.raises(ValueError, match="row 2"):
        driver.stamp_artifact(str(artifact), "element_core_v1", "probe", "run")
    assert artifact.read_text() == original


@pytest.mark.parametrize("schema", ["unregistered_v1", None])
def test_unknown_schema_remains_untouched(tmp_path, schema):
    artifact = tmp_path / "diagnostic.jsonl"
    artifact.write_text('{"custom": "payload"}\n')
    original = artifact.read_bytes()
    driver.stamp_artifact(str(artifact), schema, "probe", "run")
    assert artifact.read_bytes() == original


@pytest.mark.parametrize("schema", ["element_core_v1", "unstructured_element_v1"])
def test_empty_stream_policy_is_unchanged(tmp_path, schema):
    artifact = tmp_path / "empty.jsonl"
    artifact.write_text("")
    driver.stamp_artifact(str(artifact), schema, "probe", "run")
    assert artifact.read_bytes() == b""


def test_native_elements_are_validated_without_normalization(tmp_path):
    artifact = tmp_path / "native.jsonl"
    row = {
        "id": "native-7",
        "type": "Table",
        "text": "Name\tRole",
        "metadata": {
            "text_as_html": "<table><tr><td>Name</td></tr></table>",
            "coordinates": {"points": [[1, 2], [3, 4]]},
        },
        "_codex": {
            "run_id": "producer-run",
            "module_id": "producer",
            "sequence": 7,
            "future_provenance": "retained",
        },
        "future_native_field": {"literal": "keep"},
    }
    original = json.dumps(row, ensure_ascii=False) + "\n"
    artifact.write_text(original)
    driver.stamp_artifact(str(artifact), "unstructured_element_v1", "driver", "new-run")
    assert artifact.read_text() == original
    assert "codex" not in json.loads(artifact.read_text())


@pytest.mark.parametrize("valid", [True, False])
def test_native_validator_cli_enforces_schema(tmp_path, valid):
    artifact = tmp_path / "native.jsonl"
    row = {
        "type": "Text",
        "text": "Source text",
        **({"id": "element"} if valid else {}),
    }
    artifact.write_text(json.dumps(row) + "\n")
    result = subprocess.run(
        [
            sys.executable,
            "validate_artifact.py",
            "--schema",
            "unstructured_element_v1",
            "--file",
            str(artifact),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == (0 if valid else 1), result.stdout + result.stderr
    assert ("Validation OK" if valid else "id") in result.stdout


@pytest.mark.parametrize(
    "schema,no_validate",
    [
        ("element_core_v1", False),
        ("unstructured_element_v1", False),
        ("element_core_v1", True),
    ],
)
def test_driver_rejects_invalid_artifact_and_stops_dependents(
    tmp_path, schema, no_validate
):
    source = tmp_path / "source.jsonl"
    rows = (
        [_core(), {"seq": 1, "page": 1, "kind": "text"}]
        if schema == "element_core_v1"
        else [{"id": "native", "type": "Text"}, {"type": "Text"}]
    )
    source.write_text("".join(json.dumps(row) + "\n" for row in rows))
    recipe = tmp_path / "recipe.yaml"
    recipe.write_text(
        yaml.safe_dump(
            {
                "stages": [
                    {
                        "id": "source",
                        "stage": "extract",
                        "module": "load_artifact_v1",
                        "out": source.name,
                        "params": {"path": str(source), "schema_version": schema},
                    },
                    {
                        "id": "dependent",
                        "stage": "extract",
                        "module": "load_artifact_v1",
                        "out": source.name,
                        "needs": ["source"],
                        "params": {"path": str(source), "schema_version": schema},
                    },
                ]
            }
        )
    )
    run_dir = tmp_path / "invalid-output-probe"
    command = [
        sys.executable,
        "driver.py",
        "--recipe",
        str(recipe),
        "--output-dir",
        str(run_dir),
        "--run-id",
        "invalid-output-probe",
        "--instrument",
    ]
    if no_validate:
        command.append("--no-validate")
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0
    assert "row 2" in result.stderr
    state = json.loads((run_dir / "pipeline_state.json").read_text())
    assert state["status"] == "failed"
    assert state["stages"]["source"]["status"] == "failed"
    assert "dependent" not in state["stages"]
    produced = run_dir / "01_load_artifact_v1" / source.name
    observed = [json.loads(line) for line in produced.read_text().splitlines()]
    assert len(observed) == 2
    assert all(observed[1][key] == value for key, value in rows[1].items())
    instrumentation = json.loads((run_dir / "instrumentation.json").read_text())
    assert instrumentation["stages"][0]["status"] == "failed"
