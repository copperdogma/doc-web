import argparse
import hashlib
import json
import subprocess

import pytest

import modules.intake.archive_route_members_v1.main as router
from schemas import ArchiveMemberRoute, IntakeHandoff


def _inventory(tmp_path, members, archive_format="folder"):
    source = tmp_path / "source"
    source.mkdir()
    rows = []
    for index, (name, payload) in enumerate(members, start=1):
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        rows.append({
            "schema_version": "archive_member_manifest_v1", "archive_format": archive_format,
            "archive_path": str(source if archive_format == "folder" else tmp_path / "source.zip"),
            "member_id": f"member-{index:03d}", "member_index": index,
            "member_path": name, "extracted_path": str(path), "filename": path.name,
            "file_extension": path.suffix.lower(),
            "detected_input_kind": {".html": "web-page", ".pdf": "pdf"}.get(path.suffix.lower()),
            "file_size_bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
        })
    return source, rows


def _route(monkeypatch, tmp_path, rows, *, dry_run=False, after_recommendation=None, plan_source=None):
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text("".join(json.dumps(row) + "\n" for row in rows))
    outdir = tmp_path / "run" / "02_routes"
    outdir.mkdir(parents=True)
    args = argparse.Namespace(
        manifest=str(manifest), outdir=str(outdir), out=router.DEFAULT_OUT,
        run_id="identity-contract", folder=None, zip=None,
        downstream_end_at=None, grouped_image_downstream_end_at="images_to_manifest",
        pdf_member_handoff_mode="launch", allow_run_id_reuse=False, dry_run=dry_run,
        progress_file=None, state_file=None,
    )
    monkeypatch.setattr(router, "parse_args", lambda: args)
    artifact = tmp_path / "fake-child-artifact.jsonl"
    monkeypatch.setattr(router, "_downstream_artifact", lambda *a, **kw: str(artifact))
    calls = []

    def fake_run(command, cwd):
        calls.append(command)
        if command[3] == router.PDF_MEMBER_RECOMMENDATION_RECIPE:
            plan = {
                "schema_version": "intake_plan_v1", "book_type": "other",
                "recommended_recipe": "configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml",
                "meta": {"source_input": {"input_kind": "pdf", "source_pdf": str(plan_source or command[5])}},
            }
            artifact.write_text(json.dumps(plan) + "\n")
            if after_recommendation:
                after_recommendation()
        else:
            artifact.write_text("{}\n")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(router.subprocess, "run", fake_run)
    code = 0
    try:
        router.main()
    except SystemExit as error:
        code = error.code
    routes = [json.loads(line) for line in (outdir / router.DEFAULT_OUT).read_text().splitlines()]
    for route in routes:
        ArchiveMemberRoute(**route)
    return code, routes, calls, outdir


@pytest.mark.parametrize("archive_format", ["folder", "zip"])
@pytest.mark.parametrize("change", [
    "same-size", "grown", "removed", "directory", "symlink", "parent-symlink",
    "wrong-path", "missing-digest", "bad-digest", "wrong-size",
])
def test_stale_or_unbound_member_cannot_launch(monkeypatch, tmp_path, archive_format, change):
    source, rows = _inventory(tmp_path, [("docs/report.html", b"<p>A</p>")], archive_format)
    path = source / "docs/report.html"
    if change == "same-size":
        path.write_bytes(b"<p>B</p>")
    elif change == "grown":
        path.write_bytes(b"<p>Different longer source</p>")
    elif change in {"removed", "directory", "symlink"}:
        path.unlink()
        if change == "directory":
            path.mkdir()
        elif change == "symlink":
            target = tmp_path / "external.html"
            target.write_bytes(b"<p>A</p>")
            path.symlink_to(target)
    elif change == "parent-symlink":
        path.parent.rename(source / "retained-docs")
        (source / "docs").symlink_to(source / "retained-docs", target_is_directory=True)
    elif change == "wrong-path":
        other = tmp_path / "other.html"
        other.write_bytes(b"<p>A</p>")
        rows[0]["extracted_path"] = str(other)
    elif change == "missing-digest":
        rows[0].pop("sha256")
    elif change == "bad-digest":
        rows[0]["sha256"] = "not-a-digest"
    elif change == "wrong-size":
        rows[0]["file_size_bytes"] += 1
    code, routes, calls, _ = _route(monkeypatch, tmp_path, rows)
    assert code == 1
    assert calls == []
    assert routes[0]["terminal_outcome"] == "failed"
    assert "member_identity" in routes[0]["terminal_reason"]
    assert str(tmp_path / "manifest.jsonl") in routes[0]["terminal_reason"]
    assert rows[0].get("sha256") != hashlib.sha256(b"<p>B</p>").hexdigest()


@pytest.mark.parametrize("archive_format", ["folder", "zip"])
@pytest.mark.parametrize("change", ["added", "removed", "modified", "symlink", "parent-symlink", "wrong-parent"])
def test_changed_group_fails_every_member_before_launch(monkeypatch, tmp_path, archive_format, change):
    source, rows = _inventory(tmp_path, [("pages/p1.png", b"one"), ("pages/p2.PNG", b"two")], archive_format)
    if change == "added":
        (source / "pages/extra.JPEG").write_bytes(b"three")
    elif change == "removed":
        (source / "pages/p2.PNG").unlink()
    elif change == "modified":
        (source / "pages/p2.PNG").write_bytes(b"new")
    elif change == "symlink":
        path = source / "pages/p2.PNG"
        path.unlink()
        target = tmp_path / "external.png"
        target.write_bytes(b"two")
        path.symlink_to(target)
    elif change == "parent-symlink":
        (source / "pages").rename(source / "retained-pages")
        (source / "pages").symlink_to(source / "retained-pages", target_is_directory=True)
    else:
        other = tmp_path / "foreign/pages/p2.PNG"
        other.parent.mkdir(parents=True)
        other.write_bytes(b"two")
        rows[1]["extracted_path"] = str(other)
    code, routes, calls, _ = _route(monkeypatch, tmp_path, rows)
    assert code == 1
    assert calls == []
    assert len(routes) == 2
    assert all(row["terminal_outcome"] == "failed" for row in routes)
    assert len({row["terminal_reason"] for row in routes}) == 1


def test_unchanged_group_ignores_files_the_consumer_does_not_read(monkeypatch, tmp_path):
    source, rows = _inventory(tmp_path, [("pages/p1.png", b"one"), ("pages/p2.PNG", b"two")])
    (source / "pages/notes.txt").write_bytes(b"not consumed")
    nested = source / "pages/nested"
    nested.mkdir()
    (nested / "p3.png").write_bytes(b"not consumed")
    code, routes, calls, _ = _route(monkeypatch, tmp_path, rows)
    assert code == 0
    assert len(calls) == 1
    assert all(row["terminal_outcome"] == "launched" for row in routes)


@pytest.mark.parametrize("changed", [False, True])
def test_dry_run_checks_current_group_identity(monkeypatch, tmp_path, changed):
    source, rows = _inventory(tmp_path, [("pages/p1.png", b"one"), ("pages/p2.png", b"two")])
    if changed:
        (source / "pages/extra.png").write_bytes(b"three")
    code, routes, calls, _ = _route(monkeypatch, tmp_path, rows, dry_run=True)
    assert code == int(changed)
    assert calls == []
    assert all(row["terminal_outcome"] == ("failed" if changed else "skipped") for row in routes)


@pytest.mark.parametrize("change", ["same-size", "wrong-plan-path", "unchanged"])
def test_pdf_handoff_rechecks_member_and_source_path(monkeypatch, tmp_path, change):
    source, rows = _inventory(tmp_path, [("docs/proposal.pdf", b"%PDF source A")])
    path = source / "docs/proposal.pdf"
    other = tmp_path / "other.pdf"
    other.write_bytes(path.read_bytes())
    callback = (lambda: path.write_bytes(b"%PDF source B")) if change == "same-size" else None
    code, routes, calls, outdir = _route(
        monkeypatch, tmp_path, rows, after_recommendation=callback,
        plan_source=other if change == "wrong-plan-path" else None,
    )
    expected_failure = change != "unchanged"
    assert code == int(expected_failure)
    assert len(calls) == (1 if expected_failure else 2)
    assert routes[0]["terminal_outcome"] == ("failed" if expected_failure else "launched")
    handoff_path = outdir / "pdf_member_handoffs/member-001/intake_handoff.jsonl"
    handoff = IntakeHandoff(**json.loads(handoff_path.read_text()))
    assert handoff.terminal_outcome == ("failed" if expected_failure else "launched")


def test_unchanged_member_keeps_original_identity(monkeypatch, tmp_path):
    source, rows = _inventory(tmp_path, [("docs/report.html", b"<p>A</p>")])
    before = json.loads(json.dumps(rows))
    code, routes, calls, _ = _route(monkeypatch, tmp_path, rows)
    assert code == 0
    assert len(calls) == 1
    assert routes[0]["launch_input_path"] == str(source / "docs/report.html")
    assert routes[0]["terminal_outcome"] == "launched"
    assert rows == before
