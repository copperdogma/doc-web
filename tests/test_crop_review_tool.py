"""Actual local review recording and recrop custody mechanics; synthetic inputs."""

import json
from pathlib import Path

import pytest

from modules.common.crop_review import CropReviewError, digest, binding
from modules.common.utils import read_jsonl, save_jsonl
from modules.transform.release_reviewed_crops_v1.main import release
from tools.crop_review import record
from tools.prepare_crop_review_fixture import prepare


def test_record_supersession_and_retained_recrop(tmp_path):
    root = tmp_path / "old"
    paths = prepare(root, "test")
    previous = list(read_jsonl(paths["decisions"]))[0]
    human = {
        k: previous[k] for k in ("candidate_id", "operator_id", "action", "reason")
    }
    human.update(
        action="require_recrop",
        reason="Synthetic recrop request; retain source and old crop",
    )
    evidence = root / "recrop-human.json"
    evidence.write_text(json.dumps(human))
    event = record(
        root,
        paths["manifest"],
        paths["authority"],
        paths["decisions"],
        evidence,
        "test",
        previous["decision_id"],
    )
    with pytest.raises(CropReviewError):
        release(root, paths, tmp_path / "held" / "manifest.jsonl", "test")
    old_hashes = {str(p): digest(p) for p in root.rglob("*") if p.is_file()}
    fresh = tmp_path / "recropped"
    newpaths = prepare(fresh, "test-recopped")
    rows = list(read_jsonl(newpaths["manifest"]))
    rows[0]["bbox"]["x0"] += 1
    save_jsonl(newpaths["manifest"], rows)
    # Old authority cannot approve changed geometry/run: newly source-reviewed bindings required.
    with pytest.raises(CropReviewError):
        release(fresh, newpaths, tmp_path / "stale" / "manifest.jsonl", "test-recopped")
    b = binding(rows[0], fresh, "test-recopped", Path(newpaths["manifest"]))
    inventory = json.loads(Path(newpaths["inventory"]).read_text())
    inventory["visuals"][0]["candidate_ids"] = [b["candidate_id"]]
    Path(newpaths["inventory"]).write_text(json.dumps(inventory))
    proposals = list(read_jsonl(newpaths["proposals"]))
    proposals[0].update(candidate_id=b["candidate_id"], binding=b)
    save_jsonl(newpaths["proposals"], proposals)
    decisions = list(read_jsonl(newpaths["decisions"]))
    decisions[0].update(candidate_id=b["candidate_id"], binding=b)
    hp = fresh / decisions[0]["human_input"]["path"]
    h = json.loads(hp.read_text())
    h["candidate_id"] = b["candidate_id"]
    hp.write_text(json.dumps(h))
    decisions[0]["human_input"]["sha256"] = digest(hp)
    save_jsonl(newpaths["decisions"], decisions)
    release(
        fresh, newpaths, tmp_path / "new-release" / "manifest.jsonl", "test-recopped"
    )
    assert event["action"] == "require_recrop"
    assert old_hashes == {str(p): digest(p) for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize(
    "alias", ["manifest", "authority", "human", "hardlink", "pages", "proposals"]
)
def test_record_cannot_append_to_retained_input(tmp_path, alias):
    root = tmp_path / "custody"
    paths = prepare(root, "test")
    decision = list(read_jsonl(paths["decisions"]))[0]
    human = root / decision["human_input"]["path"]
    target = (
        Path(paths["manifest"])
        if alias == "manifest"
        else Path(paths["authority"])
        if alias == "authority"
        else human
    )
    if alias in ("pages", "proposals"):
        target = root / (alias + ".jsonl")
    if alias == "hardlink":
        target = root / "aliased-decisions.jsonl"
        target.hardlink_to(paths["manifest"])
    hashes = {str(p): digest(p) for p in root.rglob("*") if p.is_file()}
    with pytest.raises((ValueError, KeyError, TypeError)):
        record(root, paths["manifest"], paths["authority"], target, human, "test")
    assert hashes == {str(p): digest(p) for p in root.rglob("*") if p.is_file()}


def test_real_driver_recipe_releases_then_builds(tmp_path):
    import subprocess
    import sys
    import yaml
    from bs4 import BeautifulSoup

    root = tmp_path / "custody"
    prepare(root, "synthetic-driver-proof")
    repo = Path(__file__).resolve().parents[1]
    config = yaml.safe_load(
        (repo / "configs/recipes/story-241-reviewed-crop-offline.yaml").read_text()
    )
    run = tmp_path / "synthetic-driver-proof"
    for stage in config["stages"]:
        for key, value in stage.get("params", {}).items():
            if isinstance(value, str) and value.startswith(
                "tests/fixtures/crop_review_offline/approved"
            ):
                stage["params"][key] = (
                    str(root / Path(value).name)
                    if Path(value).name != "approved"
                    else str(root)
                )
        if stage["id"] == "build_reviewed":
            stage["params"]["crop_review_release"] = str(
                run / "03_release_reviewed_crops_v1/crop_review_release.json"
            )
    recipe = tmp_path / "recipe.yaml"
    recipe.write_text(yaml.safe_dump(config))
    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            str(recipe),
            "--run-id",
            "synthetic-driver-proof",
            "--output-dir",
            str(run),
        ],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    soup = BeautifulSoup(
        (run / "output/html/chapter-001.html").read_text(), "html.parser"
    )
    assert sorted(x["src"] for x in soup.find_all("img")) == [
        "images/S3.png",
        "images/S4.png",
    ]
    for filename in ("S3.png", "S4.png"):
        assert digest(root / "images" / filename) == digest(
            run / "output/html/images" / filename
        )


def test_review_display_embeds_exact_source_and_crop_without_mutating(tmp_path):
    import base64
    from bs4 import BeautifulSoup
    from tools.crop_review import show_html

    root = tmp_path / "custody"
    paths = prepare(root, "synthetic-display")
    hashes = {str(p): digest(p) for p in root.rglob("*") if p.is_file()}
    output = show_html(root, paths["manifest"], tmp_path / "review.html")
    soup = BeautifulSoup(output.read_text(), "html.parser")
    embedded = [
        base64.b64decode(x["href"].split(",")[1]) for x in soup.find_all("image")
    ]
    embedded += [base64.b64decode(x["src"].split(",")[1]) for x in soup.find_all("img")]
    assert len(embedded) == 4
    assert set(embedded) == {
        p.read_bytes()
        for p in (
            root / "S3-source.png",
            root / "S4-source.png",
            root / "images/S3.png",
            root / "images/S4.png",
        )
    }
    assert "saved_evaluation_replay" in soup.get_text()
    assert "synthetic_test" in soup.get_text()
    with pytest.raises(CropReviewError):
        show_html(root, paths["manifest"], Path(paths["manifest"]))
    assert hashes == {str(p): digest(p) for p in root.rglob("*") if p.is_file()}


def test_display_includes_source_inventory_page_without_detected_candidate(tmp_path):
    from tools.crop_review import show_html
    import shutil

    root = tmp_path / "custody"
    paths = prepare(root, "synthetic-completeness")
    shutil.copyfile(root / "S4-source.png", root / "page3-source.png")
    inventory = json.loads(Path(paths["inventory"]).read_text())
    inventory["pages"].append(
        {
            "source_page": 3,
            "source_image": "page3-source.png",
            "source_sha256": digest(root / "page3-source.png"),
        }
    )
    Path(paths["inventory"]).write_text(json.dumps(inventory))
    output = show_html(root, paths["manifest"], tmp_path / "review.html")
    assert "Source page 3" in output.read_text()
    assert "Inspect the entire source for missed visuals" in output.read_text()
