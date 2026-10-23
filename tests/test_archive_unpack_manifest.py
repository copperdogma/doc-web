import argparse
import hashlib
import json
import os
import zipfile
from pathlib import Path

import pytest

import modules.intake.archive_unpack_manifest_v1.main as unpack


def _run_unpack(monkeypatch, root: Path, members: list[tuple[str, bytes]]):
    archive_path = root / "source.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        for name, payload in members:
            archive.writestr(name, payload)
    outdir = root / "unpacked"
    monkeypatch.setattr(unpack, "parse_args", lambda: argparse.Namespace(
        zip=str(archive_path), outdir=str(outdir), out=unpack.DEFAULT_OUT,
        progress_file=None, state_file=None, run_id="unpack-regression",
    ))
    unpack.main()
    return [json.loads(line) for line in (outdir / unpack.DEFAULT_OUT).read_text().splitlines()]


@pytest.mark.parametrize("second", ["docs/../report.txt", r".\report.txt"])
def test_duplicate_normalized_member_preserves_first_bytes(monkeypatch, tmp_path, second):
    with pytest.raises(SystemExit, match="Duplicate"):
        _run_unpack(monkeypatch, tmp_path, [("report.txt", b"FIRST"), (second, b"SECOND")])
    assert (tmp_path / "unpacked/extracted_members/report.txt").read_bytes() == b"FIRST"
    assert not (tmp_path / "unpacked" / unpack.DEFAULT_OUT).exists()


@pytest.mark.parametrize("payload", [b"FIRST", b"SECOND"])
def test_filesystem_case_alias_cannot_publish_two_members(monkeypatch, tmp_path, payload):
    probe = tmp_path / "CASE-PROBE"
    probe.write_bytes(b"probe")
    if not (tmp_path / "case-probe").exists():
        pytest.skip("Destination volume distinguishes filename case")
    with pytest.raises(SystemExit, match="destination|collid|alias"):
        _run_unpack(monkeypatch, tmp_path, [("docs/Report.txt", b"FIRST"), ("docs/report.txt", payload)])
    assert (tmp_path / "unpacked/extracted_members/docs/Report.txt").read_bytes() == b"FIRST"
    assert not (tmp_path / "unpacked" / unpack.DEFAULT_OUT).exists()


def test_preexisting_hardlink_alias_cannot_publish_two_members(monkeypatch, tmp_path):
    extracted = tmp_path / "unpacked/extracted_members"
    extracted.mkdir(parents=True)
    first = extracted / "first.txt"
    first.write_bytes(b"same bytes")
    (extracted / "second.txt").hardlink_to(first)
    with pytest.raises(SystemExit, match="destination|collid|alias"):
        _run_unpack(monkeypatch, tmp_path, [("first.txt", b"same bytes"), ("second.txt", b"same bytes")])
    assert first.read_bytes() == b"same bytes"
    assert not (tmp_path / "unpacked" / unpack.DEFAULT_OUT).exists()


def test_case_aliased_directories_cannot_merge_member_groups(monkeypatch, tmp_path):
    probe = tmp_path / "CASE-PROBE"
    probe.mkdir()
    if not (tmp_path / "case-probe").exists():
        pytest.skip("Destination volume distinguishes directory case")
    members = [("A/p1.png", b"one"), ("A/p2.png", b"two"),
               ("a/p3.png", b"three"), ("a/p4.png", b"four")]
    with pytest.raises(SystemExit, match="directory"):
        _run_unpack(monkeypatch, tmp_path, members)
    assert (tmp_path / "unpacked/extracted_members/A/p1.png").read_bytes() == b"one"
    assert not (tmp_path / "unpacked/extracted_members/a/p3.png").exists()
    assert not (tmp_path / "unpacked" / unpack.DEFAULT_OUT).exists()


def test_internal_symlink_cannot_alias_logical_directories(monkeypatch, tmp_path):
    extracted = tmp_path / "unpacked/extracted_members"
    (extracted / "A").mkdir(parents=True)
    (extracted / "alias").symlink_to(extracted / "A", target_is_directory=True)
    with pytest.raises(SystemExit, match="directory"):
        _run_unpack(monkeypatch, tmp_path, [("A/one.txt", b"one"), ("alias/two.txt", b"two")])
    assert not (extracted / "A/two.txt").exists()
    assert not (tmp_path / "unpacked" / unpack.DEFAULT_OUT).exists()


def test_logical_directory_cannot_alias_extraction_root(monkeypatch, tmp_path):
    extracted = tmp_path / "unpacked/extracted_members"
    extracted.mkdir(parents=True)
    (extracted / "alias").symlink_to(extracted, target_is_directory=True)
    with pytest.raises(SystemExit, match="directory"):
        _run_unpack(monkeypatch, tmp_path, [("alias/p1.png", b"one"), ("p2.png", b"two")])
    assert not (extracted / "p1.png").exists()
    assert not (tmp_path / "unpacked" / unpack.DEFAULT_OUT).exists()


def test_exact_byte_resume_retains_files_and_manifest_identity(monkeypatch, tmp_path):
    members = [("docs/report.txt", b"FIRST"), ("other.txt", b"SECOND")]
    first_rows = _run_unpack(monkeypatch, tmp_path, members)
    fixed_mtime = 1_000_000_000
    for row in first_rows:
        os.utime(row["extracted_path"], ns=(fixed_mtime, fixed_mtime))
    resumed_rows = _run_unpack(monkeypatch, tmp_path, members)
    for original, resumed in zip(first_rows, resumed_rows):
        path = Path(resumed["extracted_path"])
        assert path.stat().st_mtime_ns == fixed_mtime
        assert resumed["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert resumed["member_id"] == original["member_id"]
        assert resumed["member_path"] == original["member_path"]


def test_changed_preexisting_destination_is_not_overwritten(monkeypatch, tmp_path):
    destination = tmp_path / "unpacked/extracted_members/report.txt"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"retained original")
    with pytest.raises(SystemExit, match="destination"):
        _run_unpack(monkeypatch, tmp_path, [("report.txt", b"changed source")])
    assert destination.read_bytes() == b"retained original"
    assert not (tmp_path / "unpacked" / unpack.DEFAULT_OUT).exists()


@pytest.mark.parametrize("link_kind", ["file", "parent", "root"])
def test_symlink_destination_does_not_touch_external_bytes(monkeypatch, tmp_path, link_kind):
    external = tmp_path / "external"
    external.mkdir()
    sentinel = external / "report.txt"
    sentinel.write_bytes(b"external original")
    extracted = tmp_path / "unpacked/extracted_members"
    extracted.parent.mkdir()
    member = "report.txt"
    if link_kind == "root":
        extracted.symlink_to(external, target_is_directory=True)
    else:
        extracted.mkdir()
        if link_kind == "file":
            (extracted / "report.txt").symlink_to(sentinel)
        else:
            (extracted / "linked").symlink_to(external, target_is_directory=True)
            member = "linked/report.txt"
    with pytest.raises(SystemExit, match="destination|root"):
        _run_unpack(monkeypatch, tmp_path, [(member, b"changed source")])
    assert sentinel.read_bytes() == b"external original"
    assert not (tmp_path / "unpacked" / unpack.DEFAULT_OUT).exists()
