"""Offline, explicit related-document binding and portable derivative publication."""
import hashlib
import json
import os
import posixpath
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup

from doc_web.related_resources import css_urls, resource_urls

from schemas import (
    DocWebBundleManifest,
    DocWebProvenanceBlock,
    RelatedDocumentResolutionReport,
    RelatedDocumentSetDeclaration,
    RelatedDocumentSetManifest,
)


MANIFEST_PATH = "related_documents.json"
REPORT_PATH = "related_reference_report.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def _snapshot(root, manifest):
    """Copy explicitly portable files, or the known legacy bundle surface."""
    required = {"manifest.json", manifest.index_path, manifest.provenance_path,
                *(entry.path for entry in manifest.entries)}
    if manifest.literal_fidelity:
        required.add(manifest.literal_fidelity.qualification_path)
        required.update(row.path for row in manifest.literal_fidelity.reports)
    portable = required | {"navigation_resolution_report.json"}
    if manifest.files:
        portable = {row.path for row in manifest.files
                    if row.safe_to_persist and row.safe_to_replay
                    and row.privacy_class == "portable"}
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError(f"Bundle symlink is unsupported: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"Non-regular bundle file: {relative}")
        legacy_asset = not manifest.files and any(
            relative.startswith(asset_root + "/") for asset_root in manifest.asset_roots)
        if relative in portable or legacy_asset:
            result[relative] = path.read_bytes()
    if required - result.keys():
        raise ValueError(f"Missing portable bundle files: {sorted(required - result.keys())}")
    if manifest.files and portable - result.keys():
        raise ValueError(f"Declared portable files missing: {sorted(portable - result.keys())}")
    return result


def _local_target(path, href):
    if any(ord(c) < 32 or ord(c) == 127 for c in href):
        raise ValueError("Control character in local resource URL")
    parsed = urlsplit(href)
    if parsed.scheme.casefold() == "file":
        raise ValueError(f"Local file URI is not portable in {path}: {href}")
    if parsed.scheme or parsed.netloc:
        return None
    decoded = unquote(parsed.path)
    if "\\" in decoded or decoded.startswith("/"):
        raise ValueError(f"Nonportable local resource in {path}: {href}")
    target = posixpath.normpath(posixpath.join(posixpath.dirname(path), decoded)) if decoded else path
    if target == ".." or target.startswith("../"):
        raise ValueError(f"Local resource escapes declared set in {path}: {href}")
    return target, unquote(parsed.fragment)


def validate_set_files(files, *, references=()):
    """Check local links/assets and every newly chosen target after serialization."""
    soups = {path: BeautifulSoup(data.decode("utf-8"), "html.parser")
             for path, data in files.items() if path.endswith(".html")}
    ids = {path: Counter(tag["id"] for tag in soup.find_all(id=True))
           for path, soup in soups.items()}
    local_links, resources = 0, 0

    def check(path, href):
        target = _local_target(path, href)
        if target is None:
            return False
        target_path, fragment = target
        if target_path not in files:
            raise ValueError(f"Missing local resource in {path}: {href}")
        if fragment and target_path in soups and ids[target_path][fragment] != 1:
            raise ValueError(f"Missing or duplicate local fragment in {path}: {href}")
        return True

    for path, soup in soups.items():
        if soup.find("base", href=True):
            raise ValueError(f"HTML base URL is incompatible with portable set links: {path}")
        for href, is_link in resource_urls(soup):
            if check(path, href):
                resources += 1
                local_links += int(is_link)
    for path, data in files.items():
        if path.endswith(".css"):
            for href in css_urls(data):
                resources += int(check(path, href))
    generated = 0
    for row in references:
        if row["status"] != "resolved":
            continue
        source, target = row["source"], row["target"]
        if _local_target(source["path"], target["href"]) != (target["path"], target["id"]):
            raise ValueError("Generated href disagrees with chosen target")
        tags = soups[target["path"]].find_all(id=target["id"])
        if len(tags) != 1 or " ".join(tags[0].get_text(" ", strip=True).split()) != target["heading"]:
            raise ValueError("Generated target no longer matches heading evidence")
        generated += 1
    return {"status": "passed", "local_links_checked": local_links,
            "static_resources_checked": resources,
            "generated_references_checked": generated, "issues": []}


def resolve_document_set(manifest_path, out_dir):
    """Create a new derivative set from an explicit JSON declaration; never overwrite."""
    declaration_path = Path(manifest_path).resolve(strict=True)
    raw_declaration = declaration_path.read_bytes()
    declaration = RelatedDocumentSetDeclaration.model_validate_json(raw_declaration)
    output = Path(out_dir).absolute()
    if output.exists() or output.is_symlink():
        raise ValueError("Output must be a new directory")
    output = output.resolve()
    members, inputs, files, identities, roots, documents = [], {}, {}, set(), [], []
    for member in declaration.documents:
        candidate = Path(member.bundle)
        if not candidate.is_absolute():
            candidate = declaration_path.parent / candidate
        if candidate.is_symlink():
            raise ValueError("Bundle root symlinks are unsupported")
        root = candidate.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("Each bundle must be a directory")
        if output == root or root in output.parents or output in root.parents:
            raise ValueError("Output cannot overlap input bundles")
        if any(root == previous or root in previous.parents or previous in root.parents for previous in roots):
            raise ValueError("Input bundle directories cannot repeat or overlap")
        roots.append(root)
        if (root / "manifest.json").is_symlink():
            raise ValueError("Bundle manifest symlinks are unsupported")
        raw_manifest = (root / "manifest.json").read_bytes()
        bundle = DocWebBundleManifest.model_validate_json(raw_manifest)
        if bundle.module_id == "doc_web_preview_v1" or (root / "preview_metadata.json").exists():
            raise ValueError("Related resolution requires final converted bundles, not previews")
        snapshot = _snapshot(root, bundle)
        if snapshot["manifest.json"] != raw_manifest:
            raise ValueError("Manifest changed while reading input bundle")
        identity = digest(_json_bytes({name: digest(data) for name, data in snapshot.items()}))
        if identity in identities:
            raise ValueError("The same supplied bundle cannot appear twice in a set")
        identities.add(identity)
        rows = []
        for line in snapshot[bundle.provenance_path].decode("utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                DocWebProvenanceBlock.model_validate(row)
                rows.append(row)
        entries = []
        for entry in bundle.entries:
            path = f"{member.member_id}/{entry.path}"
            entries.append({"filename": path, "entry_id": entry.entry_id,
                            "body_html": snapshot[entry.path].decode("utf-8")})
        members.append({"member_id": member.member_id, "document_id": bundle.document_id,
                        "edition": member.edition, "entries": entries, "provenance_rows": rows})
        documents.append({"member_id": member.member_id, "document_id": bundle.document_id,
                          "bundle": member.member_id, "edition": member.edition,
                          "input_manifest_sha256": digest(raw_manifest),
                          "input_bundle_sha256": identity})
        for relative, data in snapshot.items():
            path = f"{member.member_id}/{relative}"
            files[path] = data
            inputs[path] = {"source": root / relative, "sha256": digest(data)}
    # Fail existing broken resources before interpreting or changing anything.
    before_validation = validate_set_files(files)
    from doc_web.related_navigation import resolve_related_entries
    core = resolve_related_entries(members)
    for member in members:
        for entry in member["entries"]:
            path = entry["filename"]
            before = BeautifulSoup(files[path].decode("utf-8"), "html.parser")
            after = BeautifulSoup(entry["body_html"], "html.parser")
            if (before.body or before).get_text() != (after.body or after).get_text():
                raise ValueError(f"Reference resolution changed visible text: {path}")
            if Counter(tag["id"] for tag in before.find_all(id=True)) != Counter(tag["id"] for tag in after.find_all(id=True)):
                raise ValueError(f"Reference resolution changed DOM identities: {path}")
            old_links = [(a.get("href"), a.get_text()) for a in before.find_all("a")]
            new_links = [(a.get("href"), a.get_text()) for a in after.find_all("a")]
            remaining = iter(new_links)
            if any(not any(value == old for value in remaining) for old in old_links):
                raise ValueError(f"Reference resolution changed an existing link: {path}")
            # Preserve bytes when no new links were added (including abstentions).
            if len(new_links) != len(old_links):
                files[path] = entry["body_html"].encode("utf-8")
    validation = validate_set_files(files, references=core["references"])
    validation["existing_local_links_checked"] = before_validation["local_links_checked"]
    report = {**core, "schema_version": "doc_web_related_resolution_v1",
              "set_id": declaration.set_id, "final_validation": validation}
    RelatedDocumentResolutionReport.model_validate(report)
    files[REPORT_PATH] = _json_bytes(report)
    inventory = [{"path": path, "sha256": digest(data),
                  "input_sha256": inputs.get(path, {}).get("sha256")}
                 for path, data in sorted(files.items())]
    receipt = {"schema_version": "doc_web_related_set_v1", "set_id": declaration.set_id,
               "declaration_sha256": digest(raw_declaration), "documents": documents,
               "report_path": REPORT_PATH, "files": inventory}
    RelatedDocumentSetManifest.model_validate(receipt)
    files[MANIFEST_PATH] = _json_bytes(receipt)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".doc-web-related-", dir=output.parent) as temporary:
        staging = Path(temporary) / "set"
        staging.mkdir()
        for relative, data in files.items():
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        for original in inputs.values():
            if digest(original["source"].read_bytes()) != original["sha256"]:
                raise ValueError("Input changed during resolution; derivative not published")
        if declaration_path.read_bytes() != raw_declaration:
            raise ValueError("Declaration changed during resolution")
        if output.exists() or output.is_symlink():
            raise ValueError("Output already exists; derivative not published")
        os.rename(staging, output)
    return {"status": "complete", "set_id": declaration.set_id,
            "output_dir": str(output), "manifest_path": MANIFEST_PATH,
            "report_path": REPORT_PATH, "summary": core["summary"],
            "api_calls": 0, "cost_usd": 0}
