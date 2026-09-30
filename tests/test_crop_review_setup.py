"""Explicit operator assertions, no fabricated authority, offline driver wiring."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from modules.common.crop_review import CropReviewError, digest
from modules.common.crop_review_setup import attach_proposals, finalize, initialize
from modules.transform.propose_crop_safety_v1.main import propose
from tools.crop_review import show_html
from tools.prepare_crop_safety_runtime_fixture import prepare

REPO = Path(__file__).resolve().parents[1]
RUN = "synthetic-review-runtime"


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / "fixture"
    info = prepare(root, RUN)
    return root, Path(info["custody"]), info


def complete_proposals(root, custody, info):
    out = root / "stage" / "proposals.jsonl"
    propose(
        custody,
        custody / "manifest.jsonl",
        out,
        RUN,
        replay_manifest=info["replay_manifest"],
    )
    return out


def hashes(root):
    return {
        str(p): digest(p) for p in root.rglob("*") if p.is_file() and not p.is_symlink()
    }


def test_pending_queue_all_pages_no_authority_or_approval(bundle):
    root, custody, _ = bundle
    assert not (custody / "authority.json").exists()
    assert (custody / "decisions.jsonl").read_text() == ""
    assert json.loads((custody / "inventory.json").read_text())["complete"] is False
    html = show_html(custody, custody / "manifest.jsonl", root / "pending.html")
    assert "Source page 3" in html.read_text()
    assert "no detected candidate" in html.read_text()
    template = json.loads((custody / "authority-template.json").read_text())
    assert template["operator_id"] is None


def test_explicit_operator_setup_retains_source_and_native_receipts(bundle):
    root, custody, info = bundle
    out = complete_proposals(root, custody, info)
    before = hashes(root / "input")
    attach_proposals(custody, out, RUN)
    assert (
        initialize(custody, root / "synthetic-authority.json", RUN)["synthetic_test"]
        is True
    )
    result = finalize(
        custody, root / "synthetic-review.json", custody / "proposals.jsonl", RUN
    )
    assert result["candidate_count"] == 2 and result["source_page_count"] == 3
    assert (
        json.loads((custody / "pending-inventory.json").read_text())["complete"]
        is False
    )
    assert before == hashes(root / "input")


@pytest.mark.parametrize(
    "kind",
    [
        "no-intent",
        "missing-reason",
        "unauthorized",
        "incomplete",
        "page-missing",
        "stale-page",
        "decision-missing",
        "invalid-action",
    ],
)
def test_untrusted_or_incomplete_operator_input_holds(bundle, kind):
    root, custody, info = bundle
    out = complete_proposals(root, custody, info)
    authority = json.loads((root / "synthetic-authority.json").read_text())
    if kind in ("no-intent", "missing-reason"):
        authority["intent" if kind == "no-intent" else "reason"] = None
        (root / "synthetic-authority.json").write_text(json.dumps(authority))
        with pytest.raises(CropReviewError):
            initialize(custody, root / "synthetic-authority.json", RUN)
        assert not (custody / "authority.json").exists()
        return
    initialize(custody, root / "synthetic-authority.json", RUN)
    review = json.loads((root / "synthetic-review.json").read_text())
    if kind == "unauthorized":
        review["operator_id"] = "model"
    if kind == "incomplete":
        review["source_inventory_complete"] = False
    if kind == "page-missing":
        review["reviewed_pages"].pop()
    if kind == "stale-page":
        review["reviewed_pages"][0]["source_sha256"] = "wrong"
    if kind == "decision-missing":
        review["decisions"].pop()
    if kind == "invalid-action":
        review["decisions"][0]["action"] = "delete_source"
    (root / "synthetic-review.json").write_text(json.dumps(review))
    before = hashes(custody)
    with pytest.raises(CropReviewError):
        finalize(custody, root / "synthetic-review.json", out, RUN)
    assert before == hashes(custody)


@pytest.mark.parametrize(
    "kind",
    [
        "inventory-symlink",
        "decisions-symlink",
        "decisions-hardlink",
        "inventory-hardlink",
    ],
)
def test_setup_alias_cannot_mutate_retained_original(bundle, tmp_path, kind):
    root, custody, info = bundle
    out = complete_proposals(root, custody, info)
    initialize(custody, root / "synthetic-authority.json", RUN)
    name = "inventory.json" if kind.startswith("inventory") else "decisions.jsonl"
    retained = tmp_path / name
    retained.write_bytes((custody / name).read_bytes())
    (custody / name).unlink()
    if kind.endswith("symlink"):
        (custody / name).symlink_to(retained)
    else:
        (custody / name).hardlink_to(retained)
    before = retained.read_bytes()
    with pytest.raises(CropReviewError):
        finalize(custody, root / "synthetic-review.json", out, RUN)
    assert retained.read_bytes() == before


def test_native_operational_failure_cannot_be_overridden_by_review(tmp_path):
    root = tmp_path / "fixture"
    info = prepare(root, RUN, disposition="error")
    custody = Path(info["custody"])
    out = root / "stage" / "proposals.jsonl"
    result = propose(
        custody,
        custody / "manifest.jsonl",
        out,
        RUN,
        mode="mock",
        replay_manifest=info["replay_manifest"],
    )
    assert result["unavailable"] == 1
    initialize(custody, root / "synthetic-authority.json", RUN)
    with pytest.raises(CropReviewError):
        finalize(custody, root / "synthetic-review.json", out, RUN)
    assert json.loads((custody / "inventory.json").read_text())["complete"] is False


@pytest.mark.parametrize("disposition", ["approved", "held", "error"])
def test_actual_driver_proposal_review_release_build(tmp_path, disposition):
    run_id = f"synthetic-driver-{disposition}"
    fixture = tmp_path / "fixture"
    prepare(fixture, run_id, disposition=disposition)
    run = tmp_path / run_id
    recipe = yaml.safe_load(
        (REPO / "configs/recipes/story-242-sol-crop-safety-offline.yaml").read_text()
    )
    recipe["input"]["text_glob"] = str(fixture / "synthetic-authority.json")
    for stage in recipe["stages"]:
        for key, value in stage.get("params", {}).items():
            if isinstance(value, str) and value.startswith(
                "output/runs/story242-crop-safety-fixture"
            ):
                stage["params"][key] = str(
                    fixture
                    / Path(value).relative_to(
                        "output/runs/story242-crop-safety-fixture"
                    )
                )
        if stage["id"] == "propose_safety":
            stage["params"]["mode"] = "mock" if disposition == "error" else "replay"
        if stage["id"] == "build_reviewed":
            stage["params"]["crop_review_release"] = str(
                run / "05_release_reviewed_crops_v1/crop_review_release.json"
            )
    config = tmp_path / "recipe.yaml"
    config.write_text(yaml.safe_dump(recipe))
    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            str(config),
            "--run-id",
            run_id,
            "--output-dir",
            str(run),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if disposition == "approved":
        assert result.returncode == 0, result.stdout + result.stderr
        html = (run / "output/html/chapter-001.html").read_text()
        assert (
            html.count('src="images/S3.png"') == 1
            and html.count('src="images/S4.png"') == 1
        )
        assert "Text-only source page" in html
    else:
        assert result.returncode != 0
        assert not (run / "output/html").exists()
        assert not (
            run / "05_release_reviewed_crops_v1/illustration_manifest.jsonl"
        ).exists()
        if disposition == "held":
            held = json.loads(
                (run / "05_release_reviewed_crops_v1/crop_review_held.json").read_text()
            )
            assert held["released_count"] == 0


def test_native_fail_remains_reviewable_and_never_deletes_crop(tmp_path):
    from modules.transform.release_reviewed_crops_v1.main import release

    root = tmp_path / "fixture"
    info = prepare(root, RUN)
    custody = Path(info["custody"])
    mapping_path = Path(info["replay_manifest"])
    mapping = json.loads(mapping_path.read_text())
    mapping["mode"] = "mock"
    entry = mapping["entries"][1]
    response = mapping_path.parent / entry["response_path"]
    native = json.loads(response.read_text())
    message = next(x for x in native["output"] if x["type"] == "message")
    message["content"][0]["text"] = json.dumps(
        {
            "verdict": "fail",
            "has_page_text": False,
            "excessive_blank": False,
            "reason": "Synthetic false rejection for mechanics only",
        }
    )
    response.write_text(json.dumps(native))
    entry["response_sha256"] = digest(response)
    mapping_path.write_text(json.dumps(mapping))
    out = root / "stage" / "proposals.jsonl"
    propose(
        custody,
        custody / "manifest.jsonl",
        out,
        RUN,
        mode="mock",
        replay_manifest=mapping_path,
    )
    assert not (custody / "authority.json").exists()
    initialize(custody, root / "synthetic-authority.json", RUN)
    finalize(custody, root / "synthetic-review.json", out, RUN)
    paths = {
        k: str(
            custody
            / (
                k + ".jsonl"
                if k in ("manifest", "proposals", "decisions")
                else k + ".json"
            )
        )
        for k in ("manifest", "inventory", "proposals", "decisions", "authority")
    }
    release(custody, paths, root / "released" / "manifest.jsonl", RUN)
    assert digest(custody / "images/S4.png") == digest(root / "released/images/S4.png")
    assert (root / "input/images/S4.png").exists()


def test_unreviewed_native_passes_cannot_release(bundle):
    from modules.transform.release_reviewed_crops_v1.main import release

    root, custody, info = bundle
    out = complete_proposals(root, custody, info)
    attach_proposals(custody, out, RUN)
    paths = {
        k: str(
            custody
            / (
                k + ".jsonl"
                if k in ("manifest", "proposals", "decisions")
                else k + ".json"
            )
        )
        for k in ("manifest", "inventory", "proposals", "decisions", "authority")
    }
    with pytest.raises(CropReviewError):
        release(custody, paths, root / "released" / "manifest.jsonl", RUN)
    assert not (root / "released").exists()
