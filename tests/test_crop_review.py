"""Offline review custody, explicit authority, and publication boundary tests."""
import json
from pathlib import Path

import pytest

from modules.build.build_chapter_html_v1 import main as builder
from modules.common.crop_review import CropReviewError, digest, validate_release_for_build
from modules.transform.release_reviewed_crops_v1.main import release
from tools.prepare_crop_review_fixture import prepare

RUN_ID = "crop-review-contract-test"


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def write_rows(path, rows):
    Path(path).write_text("".join(json.dumps(row) + "\n" for row in rows))


def read_object(path):
    return json.loads(Path(path).read_text())


def write_object(path, value):
    Path(path).write_text(json.dumps(value) + "\n")


@pytest.fixture
def contract(tmp_path):
    root = tmp_path / "custody"
    paths = prepare(root, RUN_ID)
    return root, paths, tmp_path / "released" / "manifest.jsonl"


def released(contract):
    root, paths, manifest = contract
    release(root, paths, manifest, RUN_ID)
    return manifest, manifest.parent / "crop_review_release.json"


def validate(contract, **kwargs):
    manifest, receipt = released(contract)
    return validate_release_for_build(str(manifest), str(receipt), RUN_ID, **kwargs)


def edit_decision(contract, **updates):
    root, paths, _ = contract
    rows = read_rows(paths["decisions"])
    rows[0].update(updates)
    human_path = root / rows[0]["human_input"]["path"]
    human = read_object(human_path)
    for key in ("candidate_id", "operator_id", "action", "reason"):
        human[key] = rows[0][key]
    write_object(human_path, human)
    rows[0]["human_input"]["sha256"] = digest(human_path)
    write_rows(paths["decisions"], rows)


def run_builder(contract, monkeypatch, **overrides):
    root, _, manifest = contract
    final = root.parent / "published-html"
    out = root.parent / "chapters.jsonl"
    options = {
        "pages": str(root / "pages.jsonl"),
        "portions": str(root / "portions.jsonl"),
        "out": str(out),
        "output-dir": str(final),
        "illustration-manifest": str(manifest),
        "crop-review-release": str(manifest.parent / "crop_review_release.json"),
        "run-id": RUN_ID,
    }
    options.update(overrides)
    argv = ["builder", "--require-crop-review"]
    for key, value in options.items():
        if value is not None:
            argv.extend(["--" + key, str(value)])
    monkeypatch.setattr("sys.argv", argv)
    builder.main()
    return final, out


def test_complete_approved_release_retains_originals(contract, monkeypatch):
    root, paths, _ = contract
    original = {path: digest(path) for path in root.rglob("*") if path.is_file()}
    manifest, receipt = released(contract)
    report = validate_release_for_build(str(manifest), str(receipt), RUN_ID)
    assert report["expected_filenames"] == [row["filename"] for row in read_rows(paths["manifest"])]
    assert report["synthetic_authority"] is True
    final, out = run_builder(contract, monkeypatch)
    assert final.joinpath("index.html").is_file()
    rows = read_rows(out)
    assert rows and all(Path(row["file"]).parent == final for row in rows)
    assert all(path.is_file() and digest(path) == sha for path, sha in original.items())
    builder._check_reviewed_visuals(final, report["expected_filenames"], "images")
    assert not list(final.parent.glob(".crop-review-build-*"))


@pytest.mark.parametrize("kind", ["missing", "stale", "unauthorized", "conflict", "recrop", "unresolved"])
def test_invalid_decisions_block_release_before_creation(contract, kind):
    _, paths, manifest = contract
    rows = read_rows(paths["decisions"])
    if kind == "missing":
        write_rows(paths["decisions"], rows[1:])
    elif kind == "stale":
        rows[0]["binding"]["source_sha256"] = "0" * 64
        write_rows(paths["decisions"], rows)
    elif kind == "unauthorized":
        edit_decision(contract, operator_id="untrusted-model")
    elif kind == "conflict":
        duplicate = dict(rows[0], decision_id="conflicting-event", supersedes=None)
        write_rows(paths["decisions"], rows + [duplicate])
    else:
        edit_decision(contract, action="require_recrop" if kind == "recrop" else "unresolved_ownership")
    with pytest.raises(CropReviewError):
        released(contract)
    assert not manifest.parent.exists()


def test_explicit_supersession_accepts_latest_review(contract):
    root, paths, _ = contract
    rows = read_rows(paths["decisions"])
    previous = rows[0]
    new = dict(previous, decision_id="explicit-new-review", supersedes=previous["decision_id"], reason="Rechecked complete visual ownership")
    human_path = root / "superseding-human-input.json"
    write_object(human_path, {key: new[key] for key in ("candidate_id", "operator_id", "action", "reason")})
    new["human_input"] = {"path": human_path.name, "sha256": digest(human_path)}
    write_rows(paths["decisions"], rows + [new])
    assert validate(contract)["expected_filenames"]


@pytest.mark.parametrize("kind", ["complete", "pages", "visuals", "operator"])
def test_incomplete_or_unauthorized_inventory_blocks_release(contract, kind):
    _, paths, manifest = contract
    inventory = read_object(paths["inventory"])
    if kind == "complete":
        inventory["complete"] = False
    elif kind in ("pages", "visuals"):
        inventory[kind] = inventory[kind][1:]
    else:
        inventory["operator_id"] = "model"
    write_object(paths["inventory"], inventory)
    with pytest.raises(CropReviewError):
        released(contract)
    assert not manifest.parent.exists()


@pytest.mark.parametrize("kind", ["source", "crop", "decisions", "proposals", "authority", "inventory", "pages", "portions", "released_crop", "released_manifest"])
def test_changed_evidence_after_release_blocks_builder_without_output(contract, monkeypatch, kind):
    root, paths, manifest = contract
    released(contract)
    row = read_rows(paths["manifest"])[0]
    changed = {
        "source": root / row["source_image"],
        "crop": Path(paths["manifest"]).parent / "images" / row["filename"],
        "pages": root / "pages.jsonl",
        "portions": root / "portions.jsonl",
        "released_crop": manifest.parent / "images" / row["filename"],
        "released_manifest": manifest,
        **{key: Path(paths[key]) for key in ("decisions", "proposals", "authority", "inventory")},
    }[kind]
    changed.write_bytes(changed.read_bytes() + b" ")
    with pytest.raises(SystemExit) as error:
        run_builder(contract, monkeypatch)
    assert error.value.code == 2
    assert not (root.parent / "published-html").exists()
    assert not (root.parent / "chapters.jsonl").exists()
    assert not list(root.parent.glob(".crop-review-build-*"))


@pytest.mark.parametrize("kind", ["traversal", "absolute", "symlink", "filename", "zero", "outside", "nan", "bool"])
def test_unsafe_candidates_fail_before_release(contract, kind):
    root, paths, manifest = contract
    rows = read_rows(paths["manifest"])
    row = rows[0]
    if kind == "traversal":
        row["source_image"] = "../outside.png"
    elif kind == "absolute":
        row["source_image"] = str(root / row["source_image"])
    elif kind == "symlink":
        source = root / row["source_image"]
        replacement = root / "source-copy.png"
        replacement.write_bytes(source.read_bytes())
        source.unlink()
        source.symlink_to(replacement)
    elif kind == "filename":
        row["filename"] = "../source.png"
    else:
        row["bbox"]["x1"] = {"zero": row["bbox"]["x0"], "outside": 10**8, "nan": float("nan"), "bool": True}[kind]
    write_rows(paths["manifest"], rows)
    with pytest.raises(CropReviewError):
        released(contract)
    assert not manifest.parent.exists()


@pytest.mark.parametrize("destination", ["custody", "release", "symlink", "images_escape", "state", "progress"])
def test_output_aliases_cannot_mutate_protected_evidence(contract, destination):
    root, _, manifest = contract
    manifest, receipt = released(contract)
    alias = root.parent / "alias"
    alias.symlink_to(root, target_is_directory=True)
    out = root.parent / "html"
    values = {
        "custody": {"output_dir": str(root / "html")},
        "release": {"output_manifest_path": str(manifest)},
        "symlink": {"output_dir": str(alias / "html")},
        "images_escape": {"output_dir": str(out), "images_dir": str(out / ".." / "escaped")},
        "state": {"state_file": str(root / "authority.json")},
        "progress": {"progress_file": str(manifest.parent / "progress.jsonl")},
    }[destination]
    with pytest.raises(CropReviewError):
        validate_release_for_build(str(manifest), str(receipt), RUN_ID, **values)


@pytest.mark.parametrize("missing", ["crop-review-release", "illustration-manifest", "run-id"])
def test_required_builder_inputs_fail_before_reading_pages(contract, monkeypatch, missing):
    root, _, _ = contract
    monkeypatch.setattr(builder, "read_jsonl", lambda _: pytest.fail("Input read before review validation"))
    with pytest.raises(SystemExit):
        run_builder(contract, monkeypatch, **{missing: None})
    assert not (root.parent / "published-html").exists()


def test_accepted_crop_omitted_during_build_cannot_publish(contract, monkeypatch):
    root, _, _ = contract
    released(contract)
    monkeypatch.setattr(builder, "_attach_images", lambda *args, **kwargs: "<p>Fixture intentionally omitted accepted images</p>")
    with pytest.raises(SystemExit) as error:
        run_builder(contract, monkeypatch)
    assert error.value.code == 2
    assert not (root.parent / "published-html").exists()
    assert not (root.parent / "chapters.jsonl").exists()
    assert not list(root.parent.glob(".crop-review-build-*"))


def test_empty_receipt_argument_does_not_disable_review(contract, monkeypatch):
    with pytest.raises(SystemExit):
        run_builder(contract, monkeypatch, **{"crop-review-release": ""})


def test_reviewed_build_refuses_existing_output(contract, monkeypatch):
    root, _, _ = contract
    released(contract)
    final = root.parent / "published-html"
    final.mkdir()
    sentinel = final / "keep.txt"
    sentinel.write_text("prior output")
    with pytest.raises(SystemExit):
        run_builder(contract, monkeypatch)
    assert sentinel.read_text() == "prior output"


@pytest.mark.parametrize("kind", ["absolute_images", "empty_images", "dot_images", "traversal_images", "unnormalized_images", "out_index", "out_image", "state_html", "progress_html", "same_metadata", "nested_metadata"])
def test_unsafe_output_layout_fails_before_any_mutation(contract, monkeypatch, kind):
    root, _, _ = contract
    released(contract)
    final = root.parent / "published-html"
    out = root.parent / "chapters.jsonl"
    values = {
        "absolute_images": {"images-subdir": str(final / "images")},
        "empty_images": {"images-subdir": ""},
        "dot_images": {"images-subdir": "."},
        "traversal_images": {"images-subdir": "../escaped"},
        "unnormalized_images": {"images-subdir": "nested/./images"},
        "out_index": {"out": str(final / "index.html")},
        "out_image": {"out": str(final / "images" / "S3.png")},
        "state_html": {"state-file": str(final / "pipeline_state.json")},
        "progress_html": {"progress-file": str(final / "progress.jsonl")},
        "same_metadata": {"state-file": str(out)},
        "nested_metadata": {"state-file": str(out / "state.json")},
    }[kind]
    before = {path: digest(path) for path in root.parent.rglob("*") if path.is_file()}
    monkeypatch.setattr(builder, "_build", lambda *a, **kw: pytest.fail("Unsafe destination reached build"))
    with pytest.raises(SystemExit) as error:
        run_builder(contract, monkeypatch, **values)
    assert error.value.code == 2
    assert not final.exists()
    after = {path: digest(path) for path in root.parent.rglob("*") if path.is_file()}
    assert before == after


def test_existing_metadata_hardlink_to_custody_cannot_mutate_original(contract, monkeypatch):
    import os

    root, paths, _ = contract
    released(contract)
    alias = root.parent / "existing-state.json"
    os.link(paths["authority"], alias)
    sha = digest(paths["authority"])
    with pytest.raises(SystemExit) as error:
        run_builder(contract, monkeypatch, **{"state-file": str(alias)})
    assert error.value.code == 2
    assert digest(paths["authority"]) == sha == digest(alias)
    assert not (root.parent / "published-html").exists()


def test_fail_proposal_can_release_only_after_explicit_human_approval(contract):
    _, paths, _ = contract
    proposals = read_rows(paths["proposals"])
    assert {proposal["verdict"] for proposal in proposals} == {"pass", "fail"}
    decisions = read_rows(paths["decisions"])
    assert all(decision["action"] == "approve_current_crop" for decision in decisions)
    assert len(validate(contract)["expected_filenames"]) == len(proposals)


@pytest.mark.parametrize("kind", ["stale_proposal", "missing_proposal", "missing_human", "wrong_human", "authority_evidence"])
def test_review_evidence_is_required_and_bound(contract, kind):
    root, paths, manifest = contract
    if kind in ("stale_proposal", "missing_proposal"):
        rows = read_rows(paths["proposals"])
        if kind == "stale_proposal":
            rows[0]["binding"]["crop_sha256"] = "0" * 64
        else:
            rows = rows[1:]
        write_rows(paths["proposals"], rows)
    elif kind in ("missing_human", "wrong_human"):
        rows = read_rows(paths["decisions"])
        human = root / rows[0]["human_input"]["path"]
        if kind == "missing_human":
            human.unlink()
        else:
            value = read_object(human)
            value["action"] = "require_recrop"
            write_object(human, value)
            rows[0]["human_input"]["sha256"] = digest(human)
            write_rows(paths["decisions"], rows)
    else:
        authority = read_object(paths["authority"])
        evidence = root / authority["operators"][0]["evidence"]["path"]
        evidence.write_text("Changed authority")
    with pytest.raises(CropReviewError):
        released(contract)
    assert not manifest.parent.exists()


def test_metadata_hardlinks_must_be_distinct(contract, monkeypatch):
    import os

    root, _, _ = contract
    released(contract)
    state = root.parent / "state.json"
    progress = root.parent / "progress.jsonl"
    state.write_text("{}")
    os.link(state, progress)
    with pytest.raises(SystemExit):
        run_builder(contract, monkeypatch, **{"state-file": str(state), "progress-file": str(progress)})
    assert state.read_text() == progress.read_text() == "{}"
    assert not (root.parent / "published-html").exists()


@pytest.mark.parametrize("evidence", ["source", "crop", "decisions", "proposals", "pages"])
def test_evidence_changed_during_staging_blocks_publication(contract, monkeypatch, evidence):
    root, paths, _ = contract
    released(contract)
    row = read_rows(paths["manifest"])[0]
    target = {
        "source": root / row["source_image"],
        "crop": Path(paths["manifest"]).parent / "images" / row["filename"],
        "decisions": Path(paths["decisions"]),
        "proposals": Path(paths["proposals"]),
        "pages": root / "pages.jsonl",
    }[evidence]
    before = {path: digest(path) for path in root.rglob("*") if path.is_file()}
    build = builder._build

    def mutate_after_build(*args, **kwargs):
        rows = build(*args, **kwargs)
        target.write_bytes(target.read_bytes() + b" ")
        return rows

    monkeypatch.setattr(builder, "_build", mutate_after_build)
    with pytest.raises(SystemExit) as error:
        run_builder(contract, monkeypatch)
    assert error.value.code == 2
    assert not (root.parent / "published-html").exists()
    assert not (root.parent / "chapters.jsonl").exists()
    assert not list(root.parent.glob(".crop-review-build-*"))
    assert all(path.is_file() for path in before)
    assert all(digest(path) == sha for path, sha in before.items() if path != target)


@pytest.mark.parametrize("kind", ["missing_key", "invalid_binding_type"])
def test_malformed_contract_blocks_builder_without_traceback(contract, monkeypatch, kind):
    root, _, _ = contract
    _, receipt = released(contract)
    value = read_object(receipt)
    if kind == "missing_key":
        del value["custody_root"]
    else:
        value["inputs"]["manifest"] = None
    write_object(receipt, value)
    with pytest.raises(SystemExit) as error:
        run_builder(contract, monkeypatch)
    assert error.value.code == 2
    assert not (root.parent / "published-html").exists()
    assert not (root.parent / "chapters.jsonl").exists()
