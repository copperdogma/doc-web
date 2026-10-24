from copy import deepcopy
import json
import os
import subprocess
import sys

import pytest
import yaml
import numpy as np
from PIL import Image, ImageDraw

from scripts import replay_reviewed_visual_intent as replay


FIXTURE = replay.ROOT / "tests/fixtures/reviewed_visual_intent/onward-reviewed-public.json"


def fixture():
    return json.loads(FIXTURE.read_text())


def test_authored_fixture_and_recipe_keep_normal_caption_layout_controls():
    replay.validate_fixture(fixture())
    recipe = yaml.safe_load(replay.TEMPLATE.read_text())
    params = recipe["stages"][2]["params"]
    baseline = yaml.safe_load((replay.ROOT / "configs/recipes/recipe-onward-images-html-mvp.yaml").read_text())
    normal = next(s["params"] for s in baseline["stages"] if s["id"] == "crop_illustrations")
    for key in ("rescue_always", "rescue_caption_second_pass", "trim_layout_text", "rescue_model",
                "rescue_max_tokens", "rescue_caption_max_tokens", "layout_text_model"):
        assert params[key] == normal[key]
    assert params["output_format"] == "png"
    assert "cover_pages" not in params and "highres_images_dir" not in params


@pytest.mark.parametrize("mutation", ["hold", "quarantine", "bounds", "native", "duplicate", "derivation"])
def test_invalid_or_falsely_native_reviewed_intent_rejected(mutation):
    data = fixture()
    if mutation == "hold":
        data["publication_status"] = "approved"
    elif mutation == "quarantine":
        data["historical_run_unsafe"] = False
    elif mutation == "bounds":
        data["cases"][0]["targets"][0]["bbox_pixels"]["x1"] = 99999
    elif mutation == "native":
        data["cases"][0]["targets"][0]["request_id"] = "fabricated"
    elif mutation == "duplicate":
        data["cases"].append(deepcopy(data["cases"][0]))
    else:
        data["cases"][0]["derivation"] = ""
    with pytest.raises(ValueError):
        replay.validate_fixture(data)


def test_frozen_input_hash_and_path_escape_are_rejected(tmp_path):
    input_file = tmp_path / "input.json"
    input_file.write_text("original")
    digest = replay.sha(input_file)
    assert replay.checked_file(tmp_path, "input.json", digest) == input_file
    input_file.write_text("changed")
    with pytest.raises(ValueError):
        replay.checked_file(tmp_path, "input.json", digest)
    with pytest.raises(ValueError):
        replay.checked_file(tmp_path / "sub", "../input.json", replay.sha(input_file))


@pytest.mark.parametrize("mutation", ["wrongpage", "droppedrole", "alteredcontains", "reason", "contents"])
def test_crop_metadata_mutations_fail_before_proof(mutation):
    case = fixture()["cases"][0]
    target = case["targets"][0]
    crop = {"source_page": case["page_number"], "critical_graphics_target_id": target["target_id"],
            "critical_graphics_importance": target["importance"], "critical_graphics_role": target["role"],
            "critical_graphics_reason": target["reason"], "contains_text": target["contains_text"],
            "nearby_text": target["nearby_text"], "expected_visual_contents": target["expected_visual_contents"]}
    replay.validate_crop_intent(crop, case, target)
    if mutation == "wrongpage":
        crop["source_page"] += 1
    elif mutation == "droppedrole":
        del crop["critical_graphics_role"]
    elif mutation == "alteredcontains":
        crop["contains_text"] = not crop["contains_text"]
    elif mutation == "reason":
        crop["critical_graphics_reason"] = "wrong"
    else:
        del crop["expected_visual_contents"]
    with pytest.raises(ValueError, match="metadata mismatch"):
        replay.validate_crop_intent(crop, case, target)


def test_presence_aware_ocr_comparison_records_only_actual_declared_schema_default():
    before = {"page_number": 2, "html": "<p>Literal</p>", "images": None,
              "run_id": "historical", "created_at": "old"}
    after = {**before, "run_id": "replay", "created_at": "new", "literal_fidelity": None}
    result = replay.compare_ocr_rows(before, after)
    assert result["schema_defaults_added"] == {"literal_fidelity": None}
    assert result["envelope_changes"] == ["created_at", "run_id"]
    assert result["all_original_fields_retained"]


@pytest.mark.parametrize("mutation", ["unknown-null", "missing-null", "content", "nondefault"])
def test_presence_aware_ocr_comparison_rejects_unapproved_additions_deletions_and_content(mutation):
    before = {"page_number": 2, "html": "<p>Literal</p>", "images": None}
    after = {**before, "literal_fidelity": None}
    if mutation == "unknown-null":
        after["unknown"] = None
    elif mutation == "missing-null":
        del after["images"]
    elif mutation == "content":
        after["html"] = "<p>Changed</p>"
    else:
        after["literal_fidelity"] = {"fabricated": True}
    with pytest.raises(ValueError, match="content/presence"):
        replay.compare_ocr_rows(before, after)


def test_clean_environment_does_not_inherit_credential_or_dotenv_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-never-use")
    monkeypatch.setenv("DOC_WEB_ENV_FILE", "/must/not/read.env")
    env = replay.environment(tmp_path / "audit.jsonl")
    assert "OPENAI_API_KEY" not in env and "DOC_WEB_ENV_FILE" not in env
    assert env["PYTHONPATH"].split(os.pathsep)[0] == str(replay.GUARD)


@pytest.mark.parametrize("operation", [
    "import socket; socket.create_connection(('127.0.0.1',9))",
    "import socket; socket.socket().bind(('0.0.0.0',0))",
    "import socket; socket.socket(socket.AF_INET6).bind(('::1',0))",
    "import socket; socket.socket().listen()",
    "import socket; socket.socket().accept()",
    "open('/nonexistent/.env').read()",
    "import subprocess; subprocess.run(['/usr/bin/curl','https://example.invalid'])",
    "import subprocess,sys; subprocess.run([sys.executable,'-S','-c','print(1)'])",
])
def test_guard_denies_network_envfiles_and_unguarded_children(tmp_path, operation):
    audit = tmp_path / "guard.jsonl"
    p = subprocess.run([sys.executable, "-c", operation], env=replay.environment(audit),
                       capture_output=True, text=True)
    assert p.returncode != 0
    assert any(e["event"] == "denied" for e in replay.read_rows(audit))


def test_guard_inherits_into_python_child_and_missing_sink_fails_startup(tmp_path):
    audit = tmp_path / "guard.jsonl"
    env = replay.environment(audit)
    code = "import subprocess,sys; subprocess.run([sys.executable,'-c','print(1)'],check=True)"
    p = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    events = replay.read_rows(audit)
    assert len([e for e in events if e["event"] == "guard-installed"]) == 2
    del env["REVIEWED_REPLAY_AUDIT"]
    p = subprocess.run([sys.executable, "-c", "print('must not execute')"], env=env, capture_output=True)
    assert p.returncode == 78 and b"must not execute" not in p.stdout


def test_guard_blocks_verified_urllib3_capability_probe_without_network(tmp_path):
    audit = tmp_path / "guard.jsonl"
    code = "from urllib3.util.connection import HAS_IPV6; assert HAS_IPV6 is False"
    p = subprocess.run([sys.executable, "-c", code], env=replay.environment(audit),
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    events = replay.read_rows(audit)
    assert any(e["event"] == "blocked-local-capability-probe" for e in events)
    assert not any(e["event"] == "denied" for e in events)


@pytest.mark.parametrize("title_position,date_position,bounds", [
    ((20, 25), (40, 65), (10, 15, 190, 95)),
    ((130, 90), (155, 125), (115, 80, 310, 155)),
])
def test_distinct_synthetic_title_date_layouts_reuse_existing_owned_path(
        tmp_path, monkeypatch, title_position, date_position, bounds):
    import modules.extract.crop_illustrations_guided_v1.main as crop

    image = tmp_path / "source.png"
    canvas = Image.new("RGB", (340, 230), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text(title_position, "SOURCE TITLE", fill="black")
    draw.text(date_position, "1921 - 2021", fill="black")
    draw.text((25, 190), "External ordinary caption", fill="black")
    canvas.save(image)
    ocr = tmp_path / "ocr.jsonl"
    ocr.write_text(json.dumps({"page_number": 17, "image": str(image), "images": None,
                               "html": "<h1>SOURCE TITLE</h1><p>1921 - 2021</p><p>External ordinary caption</p>"}) + "\n")
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"pages": [{"page_number": 17, "source_image": str(image),
        "image_width": 340, "image_height": 230, "targets": [{"target_id": "authored-unit",
        "role": "other", "importance": "useful", "description": "Reviewed synthetic visual unit",
        "contains_text": True, "bbox_pixels": dict(zip(("x0", "y0", "x1", "y1"), bounds))}]}]}))

    def forbidden(*args, **kwargs):
        pytest.fail("Owned targets must not invoke detector/caption inference")

    monkeypatch.setattr(crop, "_call_vlm_boxes", forbidden)
    monkeypatch.setattr(crop, "_call_vlm_caption_boxes", forbidden)
    result = crop.crop_illustrations_guided(str(ocr), str(tmp_path / "out"),
        critical_graphics_manifest=str(plan), output_format="png", rescue_model="gemini-3-flash-preview",
        rescue_always=True, rescue_caption_second_pass=True, trim_layout_text=True)
    assert len(result) == 1 and result[0]["source_page"] == 17
    with Image.open(tmp_path / "out/images" / result[0]["filename"]) as output:
        assert np.array_equal(np.asarray(output.convert("RGB")), np.asarray(canvas.crop(bounds)))
    assert json.loads(ocr.read_text())["images"] is None
