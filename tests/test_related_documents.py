"""Offline publication, safety and independent portable-link proofs for related sets."""
import hashlib
import json
import posixpath
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest
from bs4 import BeautifulSoup

from doc_web.related_documents import resolve_document_set
from schemas import DocWebBundleManifest, DocWebProvenanceBlock

REPO_ROOT = Path(__file__).resolve().parents[1]
LABELS = ("x501b", "x512", "x528", "x503e", "x525", "x519")
HEADINGS = (
    "x501b: Supply checks", "Movement rules (x512)", "Weather checks (x528):",
    "x503e Encounters", "Equipment (x525)", "x519: Final checks",
)


def _write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _bundle(root, blocks, *, inventory=False):
    root.mkdir(parents=True)
    (root / "provenance").mkdir()
    (root / "assets").mkdir()
    (root / "assets" / "diagram.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    body, rows = [], []
    for ordinal, (kind, html) in enumerate(blocks, 1):
        block_id = f"blk-chapter-001-{ordinal:04d}"
        tag = "h2" if kind == "heading" else "p"
        body.append(f'<{tag} id="{block_id}">{html}</{tag}>')
        rows.append({"block_id": block_id, "entry_id": "chapter-001",
                     "block_kind": kind, "source_page_number": 1,
                     "source_element_ids": [f"el-001-{ordinal:03d}"],
                     "text_quote": BeautifulSoup(html, "html.parser").get_text()})
        DocWebProvenanceBlock.model_validate(rows[-1])
    (root / "chapter-001.html").write_text(
        '<!doctype html><html><body>' + "".join(body) +
        '<a href="index.html">Contents</a><img src="assets/diagram.svg" alt="Diagram">'
        '</body></html>', encoding="utf-8")
    (root / "index.html").write_text('<html><body><a href="chapter-001.html">Chapter</a></body></html>')
    (root / "provenance" / "blocks.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    manifest = {"document_id": "manual", "title": "Manual", "source_artifact": "sha256:" + "0" * 64,
                "entries": [{"entry_id": "chapter-001", "kind": "chapter", "title": "Chapter",
                             "path": "chapter-001.html", "order": 1}],
                "reading_order": ["chapter-001"], "asset_roots": ["assets"]}
    if inventory:
        manifest["files"] = [
            {"path": path, "role": role, "privacy_class": "portable", "safe_to_persist": True,
             "safe_to_replay": True, "required_for_replay": True}
            for path, role in [("manifest.json", "manifest"), ("index.html", "index"),
                               ("chapter-001.html", "entry"), ("provenance/blocks.jsonl", "provenance"),
                               ("assets/diagram.svg", "asset")]]
    DocWebBundleManifest.model_validate(manifest)
    _write_json(root / "manifest.json", manifest)
    return root


def _fixture(tmp_path, *, inventory=False):
    source = _bundle(tmp_path / "source", [("paragraph", f"See <em>{label}</em> for details.")
                                          for label in LABELS], inventory=inventory)
    target = _bundle(tmp_path / "target", [("heading", text) for text in HEADINGS], inventory=inventory)
    declaration = tmp_path / "declaration.json"
    _write_json(declaration, {"schema_version": "doc_web_related_set_declaration_v1", "set_id": "field-guides",
                             "documents": [{"member_id": "guide", "bundle": source.name},
                                           {"member_id": "companion", "bundle": target.name}]})
    return declaration, source, target


def make_related_fixture(root):
    """Create a deterministic offline set for driver/consumer validation."""
    return _fixture(Path(root))[0]


def _report(output):
    return json.loads((output / "related_reference_report.json").read_text())


def test_set_links_preserve_source_and_survive_independent_portable_copy(tmp_path):
    declaration, source, target = _fixture(tmp_path)
    originals = {"guide": _tree(source), "companion": _tree(target)}
    output = tmp_path / "published"
    result = resolve_document_set(declaration, output)
    assert result["api_calls"] == result["cost_usd"] == 0
    report = _report(output)
    resolved = [r for r in report["references"] if r["status"] == "resolved"]
    assert {r["label"] for r in resolved} == set(LABELS)
    assert len(resolved) == 6
    receipt = json.loads((output / "related_documents.json").read_text())
    assert receipt["declaration_sha256"] == _sha(declaration.read_bytes())
    assert {r["path"] for r in receipt["files"]} == set(_tree(output)) - {"related_documents.json"}
    assert str(tmp_path) not in json.dumps(receipt)
    assert str(tmp_path) not in json.dumps(report)
    assert {row["document_id"] for row in receipt["documents"]} == {"manual"}
    assert {row["member_id"] for row in receipt["documents"]} == {"guide", "companion"}
    for row in receipt["files"]:
        assert row["sha256"] == _sha((output / row["path"]).read_bytes())
        if "/" in row["path"]:
            member, relative = row["path"].split("/", 1)
            assert row["input_sha256"] == _sha(originals[member][relative])
    for member, original in originals.items():
        assert _tree(source if member == "guide" else target) == original
        assert (output / member / "provenance/blocks.jsonl").read_bytes() == original["provenance/blocks.jsonl"]
        assert (output / member / "assets/diagram.svg").read_bytes() == original["assets/diagram.svg"]
    before = BeautifulSoup(originals["guide"]["chapter-001.html"], "html.parser")
    after = BeautifulSoup((output / "guide/chapter-001.html").read_text(), "html.parser")
    assert after.body.get_text() == before.body.get_text()
    assert [e.get_text() for e in after.find_all("em")] == list(LABELS)
    assert after.find("a", string="Contents")["href"] == "index.html"
    assert after.img["src"] == "assets/diagram.svg"
    copied = tmp_path / "elsewhere" / "copied"
    shutil.copytree(output, copied)
    shutil.rmtree(output)
    shutil.rmtree(source)
    shutil.rmtree(target)
    for row in resolved:
        assert row["source"]["provenance"]["source_element_ids"]
        assert row["target"]["evidence"]["provenance"]["source_element_ids"]
        source_path = row["source"]["path"]
        parsed = urlsplit(row["target"]["href"])
        assert not parsed.scheme and not parsed.netloc and not parsed.path.startswith("/")
        destination = posixpath.normpath(posixpath.join(posixpath.dirname(source_path), unquote(parsed.path)))
        soup = BeautifulSoup((copied / destination).read_text(), "html.parser")
        found = soup.find_all(id=unquote(parsed.fragment))
        assert len(found) == 1
        assert " ".join(found[0].get_text(" ", strip=True).split()) == row["target"]["heading"]
        source_soup = BeautifulSoup((copied / source_path).read_text(), "html.parser")
        assert source_soup.find("a", href=row["target"]["href"])


def test_identical_operation_in_fresh_outputs_is_deterministic(tmp_path):
    declaration, _, _ = _fixture(tmp_path)
    resolve_document_set(declaration, tmp_path / "first")
    resolve_document_set(declaration, tmp_path / "second")
    assert _tree(tmp_path / "first") == _tree(tmp_path / "second")
    with pytest.raises(ValueError):
        resolve_document_set(declaration, tmp_path / "first")


@pytest.mark.parametrize("damage", ["member_id", "same_root", "same_contents", "path_escape", "symlink", "missing_asset", "broken_fragment"])
def test_invalid_inputs_never_publish_partial_set(tmp_path, damage):
    declaration, source, target = _fixture(tmp_path)
    value = json.loads(declaration.read_text())
    if damage == "member_id":
        value["documents"][1]["member_id"] = "guide"
    elif damage == "same_root":
        value["documents"][1]["bundle"] = "source"
    elif damage == "same_contents":
        shutil.rmtree(target)
        shutil.copytree(source, target)
    elif damage == "path_escape":
        manifest = json.loads((target / "manifest.json").read_text())
        manifest["entries"][0]["path"] = "../chapter-001.html"
        _write_json(target / "manifest.json", manifest)
    elif damage == "symlink":
        (source / "assets/link.svg").symlink_to(target / "assets/diagram.svg")
    elif damage == "missing_asset":
        (source / "assets/diagram.svg").unlink()
    elif damage == "broken_fragment":
        (source / "index.html").write_text('<a href="chapter-001.html#does-not-exist">Broken</a>')
    _write_json(declaration, value)
    before = (_tree(source), _tree(target))
    output = tmp_path / "invalid-output"
    with pytest.raises((ValueError, OSError)):
        resolve_document_set(declaration, output)
    assert not output.exists()
    assert (_tree(source), _tree(target)) == before


def test_output_cannot_overlap_an_input(tmp_path):
    declaration, source, _ = _fixture(tmp_path)
    before = _tree(source)
    with pytest.raises(ValueError):
        resolve_document_set(declaration, source / "derived")
    assert _tree(source) == before
    with pytest.raises(ValueError):
        resolve_document_set(declaration, source)


def test_conflicting_editions_hold_cross_member_references(tmp_path):
    declaration, _, _ = _fixture(tmp_path)
    value = json.loads(declaration.read_text())
    value["documents"][0]["edition"] = "First edition"
    value["documents"][1]["edition"] = "Second edition"
    _write_json(declaration, value)
    output = tmp_path / "editions"
    resolve_document_set(declaration, output)
    references = _report(output)["references"]
    assert len(references) == 6
    assert {r["reason"] for r in references} == {"edition_conflict"}
    assert all(r["status"] != "resolved" and r["target"] is None for r in references)


def test_duplicate_heading_tokens_across_members_are_ambiguous(tmp_path):
    declaration, _, _ = _fixture(tmp_path)
    _bundle(tmp_path / "third", [("heading", HEADINGS[0])])
    value = json.loads(declaration.read_text())
    value["documents"].append({"member_id": "supplement", "bundle": "third"})
    _write_json(declaration, value)
    output = tmp_path / "ambiguous"
    resolve_document_set(declaration, output)
    row = next(r for r in _report(output)["references"] if r["label"] == "x501b")
    assert row["status"] == "ambiguous" and row["target"] is None
    assert {c["member_id"] for c in row["candidates"]} == {"companion", "supplement"}


def test_explicit_inventory_copies_portable_optional_files_excludes_private(tmp_path):
    declaration, source, _ = _fixture(tmp_path, inventory=True)
    (source / "optional.txt").write_text("portable appendix")
    (source / "private.json").write_text('{"private": "owner data"}')
    (source / "unlisted.txt").write_text("unclassified")
    manifest = json.loads((source / "manifest.json").read_text())
    manifest["files"].extend([
        {"path": "optional.txt", "role": "asset", "privacy_class": "portable", "safe_to_persist": True, "safe_to_replay": True},
        {"path": "private.json", "role": "private", "privacy_class": "private"},
    ])
    _write_json(source / "manifest.json", manifest)
    output = tmp_path / "safe"
    resolve_document_set(declaration, output)
    assert (output / "guide/optional.txt").read_text() == "portable appendix"
    assert not (output / "guide/private.json").exists()
    assert not (output / "guide/unlisted.txt").exists()
    receipt = json.loads((output / "related_documents.json").read_text())
    assert "guide/private.json" not in {r["path"] for r in receipt["files"]}


def test_cli_resolve_set_json_and_failure_exit(tmp_path):
    declaration, _, _ = _fixture(tmp_path)
    output = tmp_path / "cli"
    command = [sys.executable, "-m", "doc_web", "resolve-set", "--manifest", str(declaration),
               "--out-dir", str(output), "--json"]
    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["set_id"] == "field-guides"
    assert result["api_calls"] == result["cost_usd"] == 0
    assert (output / "related_documents.json").is_file()
    rejected = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)
    assert rejected.returncode != 0


def test_legacy_bundle_does_not_publish_unclassified_extra_files(tmp_path):
    declaration, source, _ = _fixture(tmp_path)
    (source / 'private-notes.json').write_text('{"private": "owner notes"}')
    output = tmp_path / 'portable'
    resolve_document_set(declaration, output)
    assert not (output / 'guide/private-notes.json').exists()
    assert (source / 'private-notes.json').exists()


def test_manifest_cannot_change_between_parse_and_snapshot(tmp_path, monkeypatch):
    import doc_web.related_documents as related
    declaration, source, _ = _fixture(tmp_path)
    snapshot = related._snapshot

    def changing(root, manifest):
        if root == source:
            value = json.loads((root / 'manifest.json').read_text())
            value['document_id'] = 'changed-during-read'
            _write_json(root / 'manifest.json', value)
        return snapshot(root, manifest)

    monkeypatch.setattr(related, '_snapshot', changing)
    with pytest.raises(ValueError, match='Manifest changed'):
        resolve_document_set(declaration, tmp_path / 'published')
    assert not (tmp_path / 'published').exists()


@pytest.mark.parametrize('resource', [
    '<img src="file:///private/original/image.png">',
    '<img src="assets/diagram.svg" srcset="assets/missing.png 2x">',
    '<style>body { background: url("assets/missing.png") }</style>',
    '<div style="background: url(assets/missing.png)"></div>',
    '<style>@import "assets/missing.css";</style>',
    '<style>body { background: image-set("assets/missing.png" 2x) }</style>',
])
def test_nonportable_static_resources_fail_before_publication(tmp_path, resource):
    declaration, source, _ = _fixture(tmp_path)
    page = source / 'chapter-001.html'
    page.write_text(page.read_text().replace('</body>', resource + '</body>'))
    with pytest.raises(ValueError, match='portable|Missing local resource'):
        resolve_document_set(declaration, tmp_path / 'published')
    assert not (tmp_path / 'published').exists()


def test_static_css_and_srcset_resources_remain_portable(tmp_path):
    declaration, source, _ = _fixture(tmp_path)
    (source / 'assets/style.css').write_text('body { background: url(diagram.svg) }')
    page = source / 'chapter-001.html'
    page.write_text(page.read_text().replace('</body>', '<link href="assets/style.css" rel="stylesheet">'
                    '<img srcset="assets/diagram.svg 1x, data:image/svg+xml;base64,PHN2Zy8+ 2x">'
                    '<div style="background: url(assets/diagram.svg)"></div></body>'))
    resolve_document_set(declaration, tmp_path / 'published')
    assert _report(tmp_path / 'published')['final_validation']['static_resources_checked'] > 6


def test_related_set_runs_through_driver(tmp_path):
    output = tmp_path / 'runs'
    process = subprocess.run([sys.executable, 'driver.py', '--recipe',
                              'configs/recipes/recipe-related-document-set.yaml',
                              '--run-id', 'related-test', '--output-dir', str(output)],
                             cwd=REPO_ROOT, text=True, capture_output=True)
    assert process.returncode == 0, process.stdout + process.stderr
    stage = output / 'related-test/02_resolve_document_set_v1'
    result = json.loads((stage / 'related_set_result.json').read_text())
    assert result['schema_version'] == 'doc_web_related_set_result_v1'
    assert result['summary'] == {'resolved': 6}
    assert _report(stage / 'related-set')['final_validation']['status'] == 'passed'
    first = _tree(stage / 'related-set')
    process = subprocess.run([sys.executable, 'driver.py', '--recipe',
                              'configs/recipes/recipe-related-document-set.yaml',
                              '--run-id', 'related-test', '--output-dir', str(output),
                              '--start-from', 'references', '--allow-run-id-reuse'],
                             cwd=REPO_ROOT, text=True, capture_output=True)
    assert process.returncode == 0, process.stdout + process.stderr
    resumed = json.loads((stage / 'related_set_result.json').read_text())
    assert resumed['output_dir'] != result['output_dir']
    assert _tree(stage / 'related-set') == first
    assert _report(Path(resumed['output_dir']))['summary'] == {'resolved': 6}


def test_installed_cli_resolves_without_source_checkout(tmp_path):
    import os
    declaration, _, _ = _fixture(tmp_path)
    install = tmp_path / 'installed'
    process = subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-index', '--no-deps',
                              '--no-build-isolation', '--target', str(install), str(REPO_ROOT)],
                             cwd=tmp_path, text=True, capture_output=True)
    assert process.returncode == 0, process.stdout + process.stderr
    env = {**os.environ, 'PYTHONPATH': str(install)}
    process = subprocess.run([sys.executable, '-m', 'doc_web', 'resolve-set', '--manifest', str(declaration),
                              '--out-dir', str(tmp_path / 'installed-output'), '--json'],
                             cwd=tmp_path, env=env, text=True, capture_output=True)
    assert process.returncode == 0, process.stdout + process.stderr
    assert json.loads(process.stdout)['summary'] == {'resolved': 6}
