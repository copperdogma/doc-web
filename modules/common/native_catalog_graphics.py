"""Offline, opt-in recovery of source-associated catalog image occurrences.

Native geometry supplies locations, not semantic importance. This policy admits
only repeated, uniquely labelled catalog entries and records every association.
It crops retained rendered pixels, never extracts or reconstructs artwork.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
from typing import Any

import fitz
from bs4 import BeautifulSoup
from PIL import Image


POLICY_ID = "source-associated-catalog-illustrations-v1"
POLICY = {
    "id": POLICY_ID,
    "authority": "explicit opt-in inclusion of source-associated catalog illustrations",
    "semantic_limit": "Spatial association does not establish essential/decorative importance.",
    "anchors": "Unique compact HTML heading or first table cell; exact case-equivalent native title line.",
    "association": "Unique image immediately left; gap <= image width, top difference <= 15% image height.",
    "catalog_gate": "At least two uniquely associated entries on the logical page.",
    "image_gate": "Full logical viewport containment; width <= 40%, height <= 45%, area <= 15% of viewport.",
    "layer_grouping": "Contained native image layers with outer area no more than twice inner area.",
    "registration": "Exact decoded full raster or declared left/right slice; uniform PDF-to-raster scale.",
    "existing_occurrence": "Existing crop covers at least 90% of native inner rectangle; partial overlap holds for review.",
    "pixels": "Outward-rounded rectangular crop of retained raster, lossless PNG, no rotation or resize.",
    "text": "Keep every existing transcribed word and ordered block, including text repeated inside graphics.",
    "ambiguity": "Hold missing/duplicate native titles, nonunique spatial neighbors, conflicting ownership or registration.",
}


def sha256(path: str | Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _record_hash(rows: list[dict[str, Any]]) -> str:
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _key(text: str) -> str:
    return " ".join(text.split()).casefold()


def _compact(text: str) -> bool:
    letters = sum(c.isalpha() for c in text)
    return bool(text and len(text) <= 90 and len(text.split()) <= 8
                and not re.search(r"[.!?]", text) and not text.endswith(":")
                and letters / len(text) >= .45)


def catalog_labels(html: str) -> list[dict[str, Any]]:
    """Return authored labels without changing HTML or consuming figure text."""
    soup = BeautifulSoup(html, "html.parser")
    labels = []
    nodes = list(soup.find_all(re.compile(r"^h[1-6]$")))
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"], recursive=False)
        if len(cells) >= 2 and any(c.name == "td" for c in cells):
            nodes.append(cells[0])
    for index, node in enumerate(nodes):
        if node.find_parent("figure"):
            continue
        clone = BeautifulSoup(str(node), "html.parser")
        for figure in clone.find_all(["figure", "img"]):
            figure.decompose()
        label = " ".join(clone.get_text(" ", strip=True).split())
        if _compact(label):
            labels.append({"label": label, "key": _key(label), "html_tag": node.name,
                           "anchor_index": index})
    return labels


def register_page(page: dict[str, Any], physical: dict[str, Any], pdf_page) -> dict[str, Any]:
    """Prove the logical raster is exactly the declared full/left/right source."""
    if pdf_page.rotation or pdf_page.cropbox != pdf_page.mediabox:
        raise ValueError("unsupported PDF page rotation or nontrivial crop box")
    full_path, logical_path = Path(physical["image"]), Path(page["image"])
    with Image.open(full_path) as full_in, Image.open(logical_path) as logical_in:
        full, logical = full_in.convert("RGB"), logical_in.convert("RGB")
        fw, fh = full.size
        lw, lh = logical.size
        if lh != fh or lw > fw:
            raise ValueError("logical raster dimensions do not match a physical page slice")
        sx, sy = fw / pdf_page.rect.width, fh / pdf_page.rect.height
        if abs(sx - sy) > max(sx, sy) / max(fw, fh):
            raise ValueError("nonuniform or unproven PDF-to-raster scaling")
        side = page.get("spread_side")
        if logical.size == full.size:
            offset = 0
        elif side == "L":
            offset = 0
        elif side == "R":
            offset = fw - lw
        else:
            raise ValueError("partial raster requires an explicit left/right source side")
        expected = full.crop((offset, 0, offset + lw, fh))
        if expected.tobytes() != logical.tobytes():
            raise ValueError("retained logical raster is not the exact declared physical slice")
        return {
            "physical_image": str(full_path.resolve()), "physical_sha256": sha256(full_path),
            "logical_image": str(logical_path.resolve()), "logical_sha256": sha256(logical_path),
            "physical_dimensions": [fw, fh], "logical_dimensions": [lw, lh],
            "split_origin_pixels": [offset, 0], "pdf_to_raster_scale": [sx, sy],
            "pdf_page_rect": list(pdf_page.rect), "registration": "exact_decoded_slice",
            "logical_decoded_sha256": hashlib.sha256(logical.tobytes()).hexdigest(),
            "viewport_pdf": [offset / sx, 0, (offset + lw) / sx, fh / sy],
        }


def native_image_groups(pdf_page, viewport: fitz.Rect) -> list[dict[str, Any]]:
    """Group contained composite image layers, retaining occurrence identities."""
    candidates = []
    for item in pdf_page.get_image_info(xrefs=True):
        rect = fitz.Rect(item["bbox"])
        if not rect.is_valid or rect.is_empty or not viewport.contains(rect):
            continue
        if (rect.width > viewport.width * .4 or rect.height > viewport.height * .45
                or rect.get_area() > viewport.get_area() * .15):
            continue
        candidates.append(item)
    groups: dict[tuple[float, ...], dict[str, Any]] = {}
    for item in candidates:
        rect = fitz.Rect(item["bbox"])
        containers = [other for other in candidates
                      if fitz.Rect(other["bbox"]).contains(rect)
                      and fitz.Rect(other["bbox"]).get_area() <= rect.get_area() * 2]
        outer = max(containers, key=lambda other: fitz.Rect(other["bbox"]).get_area())
        key = tuple(outer["bbox"])
        group = groups.setdefault(key, {"bbox_pdf": list(key), "occurrences": []})
        group["occurrences"].append({
            "number": item["number"], "xref": item.get("xref", 0),
            "bbox": list(item["bbox"]), "transform": list(item["transform"]),
            "embedded_dimensions": [item["width"], item["height"]],
            "digest_md5": item.get("digest", b"").hex(),
        })
    for group in groups.values():
        # The smaller artwork rectangle distinguishes an existing tight crop
        # from its shadow while the outer rectangle preserves the composition.
        group["inner_bbox_pdf"] = min(
            group["occurrences"], key=lambda a: fitz.Rect(a["bbox"]).get_area())["bbox"]
    return sorted(groups.values(), key=lambda g: (g["bbox_pdf"][1], g["bbox_pdf"][0]))


def _pixel_box(rect, mapping: dict[str, Any]) -> dict[str, int]:
    sx, sy = mapping["pdf_to_raster_scale"]
    ox, oy = mapping["split_origin_pixels"]
    x0, y0, x1, y1 = rect
    coords = [math.floor(x0 * sx) - ox, math.floor(y0 * sy) - oy,
              math.ceil(x1 * sx) - ox, math.ceil(y1 * sy) - oy]
    out = dict(zip(["x0", "y0", "x1", "y1"], coords))
    out.update(width=coords[2] - coords[0], height=coords[3] - coords[1])
    return out


def associate_page(pdf_page, html: str, mapping: dict[str, Any]) -> list[dict[str, Any]]:
    """Enumerate accepted/held associations under the explicit inclusion policy."""
    labels = catalog_labels(html)
    counts = Counter(label["key"] for label in labels)
    viewport = fitz.Rect(mapping["viewport_pdf"])
    groups = native_image_groups(pdf_page, viewport)
    lines = []
    flags = fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES
    for block in pdf_page.get_text("dict", flags=flags)["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            if viewport.contains(fitz.Rect(line["bbox"])):
                lines.append({"text": "".join(span["text"] for span in line["spans"]),
                              "bbox": list(line["bbox"])})
    decisions = []
    for anchor in labels:
        decision = {"anchor": anchor, "status": "held"}
        decisions.append(decision)
        if counts[anchor["key"]] != 1:
            decision["reason"] = "duplicate_html_catalog_label"
            continue
        matches = [line for line in lines if _key(line["text"]) == anchor["key"]]
        if len(matches) != 1:
            decision["reason"] = "native_title_missing_or_nonunique"
            continue
        line = matches[0]
        decision["native_title"] = line
        x, y, _, _ = line["bbox"]
        neighbors = []
        for group in groups:
            rect = fitz.Rect(group["bbox_pdf"])
            if 0 <= x - rect.x1 <= rect.width and abs(y - rect.y0) <= rect.height * .15:
                neighbors.append(group)
        decision["neighbor_count"] = len(neighbors)
        if len(neighbors) != 1:
            decision["reason"] = "spatial_neighbor_missing_or_nonunique"
            continue
        decision.update(status="associated", reason="unique_exact_title_and_native_neighbor",
                        native_group=neighbors[0], bbox=_pixel_box(neighbors[0]["bbox_pdf"], mapping),
                        inner_bbox=_pixel_box(neighbors[0]["inner_bbox_pdf"], mapping))
    owners = Counter(tuple(d["native_group"]["bbox_pdf"]) for d in decisions if d["status"] == "associated")
    for decision in decisions:
        if decision["status"] == "associated" and owners[tuple(decision["native_group"]["bbox_pdf"])] != 1:
            decision.update(status="held", reason="native_occurrence_has_multiple_html_owners")
    if sum(d["status"] == "associated" for d in decisions) < 2:
        for decision in decisions:
            if decision["status"] == "associated":
                decision.update(status="held", reason="insufficient_repeated_catalog_entries")
    return decisions


def _covered(inner: dict[str, int], crop: dict[str, Any]) -> bool:
    bbox = crop.get("bbox") or {}
    try:
        overlap = max(0, min(inner["x1"], bbox["x1"]) - max(inner["x0"], bbox["x0"])) * max(
            0, min(inner["y1"], bbox["y1"]) - max(inner["y0"], bbox["y0"]))
        return overlap / (inner["width"] * inner["height"]) >= .9
    except (KeyError, TypeError, ZeroDivisionError):
        return False


def _intersects(inner: dict[str, int], crop: dict[str, Any]) -> bool:
    bbox = crop.get("bbox") or {}
    try:
        return (min(inner["x1"], bbox["x1"]) > max(inner["x0"], bbox["x0"])
                and min(inner["y1"], bbox["y1"]) > max(inner["y0"], bbox["y0"]))
    except (KeyError, TypeError):
        return False


def _safe_filename(value: str) -> str:
    if not value or Path(value).name != value or value in {".", ".."}:
        raise ValueError("crop filenames must be plain, nonempty filenames")
    return value


def validate_native_inventory(rows: list[dict[str, Any]], report: dict[str, Any], output_images: str | Path) -> None:
    """Verify the unstamped sidecar contract against current source/crop bytes."""
    output_images = Path(output_images)
    hashes: dict[str, str] = {}

    def current_hash(path: str) -> str:
        if path not in hashes:
            hashes[path] = sha256(path)
        return hashes[path]

    if report.get("policy") != POLICY or current_hash(report["source_pdf"]) != report["source_pdf_sha256"]:
        raise ValueError("native inventory policy or PDF identity mismatch")
    for asset in report["retained_assets"]:
        if sha256(output_images / _safe_filename(asset["filename"])) != asset["sha256"]:
            raise ValueError("retained crop bytes changed")
    if _record_hash(rows[:report["summary"]["retained_crop_rows"]]) != report["retained_crop_records_sha256"]:
        raise ValueError("retained crop rectangles or metadata changed")
    native_rows = [row for row in rows[report["summary"]["retained_crop_rows"]:]
                   if row.get("native_graphics_provenance")]
    accepted = {decision["filename"]: decision for page in report["pages"] for decision in page["decisions"]
                if decision["status"] == "recovered"}
    accepted_pages = {decision["filename"]: page for page in report["pages"] for decision in page["decisions"]
                      if decision["status"] == "recovered"}
    if len(native_rows) != report["summary"]["recovered_occurrences"] or len(accepted) != len(native_rows):
        raise ValueError("native inventory accepted count mismatch")
    for row in native_rows:
        provenance = row["native_graphics_provenance"]
        mapping = provenance["mapping"]
        filename = _safe_filename(row["filename"])
        if (filename not in accepted or accepted[filename]["provenance"] != provenance
                or provenance["inclusion_policy"] != POLICY_ID
                or provenance["source_pdf_sha256"] != report["source_pdf_sha256"]
                or provenance.get("preserve_transcribed_text") is not True):
            raise ValueError("native crop lacks an accepted source/policy receipt")
        source_page = accepted_pages[filename]
        if (row.get("source_page") != source_page["source_page"]
                or provenance["physical_page"] != source_page["physical_page"]
                or Path(row["source_image"]).resolve() != Path(mapping["logical_image"]).resolve()
                or row.get("source_dimensions") != mapping["logical_dimensions"]
                or row.get("coordinate_system") != "source_pixels"
                or row.get("crop_transform") != "rectangle_and_encode"):
            raise ValueError("native crop source coordinates differ from its registered receipt")
        if (current_hash(mapping["logical_image"]) != mapping["logical_sha256"]
                or current_hash(mapping["physical_image"]) != mapping["physical_sha256"]):
            raise ValueError("native crop source identity changed")
        bbox = row["bbox"]
        if bbox != provenance["bbox"] or bbox != _pixel_box(provenance["native_group"]["bbox_pdf"], mapping):
            raise ValueError("native crop geometry differs from its source occurrence")
        if _key(provenance["anchor"]["label"]) != _key(provenance["native_title"]["text"]):
            raise ValueError("native crop anchor is not the exact source title")
        if sha256(output_images / filename) != provenance["crop_sha256"]:
            raise ValueError("native crop encoded bytes changed")
        with Image.open(row["source_image"]) as source, Image.open(output_images / filename) as crop:
            expected = source.crop(tuple(bbox[k] for k in ("x0", "y0", "x1", "y1")))
            if (crop.size != expected.size or crop.mode != expected.mode
                    or crop.tobytes() != expected.tobytes()
                    or hashlib.sha256(crop.tobytes()).hexdigest() != provenance["decoded_crop_sha256"]):
                raise ValueError("native crop is not the exact source-pixel rectangle")


def recover_native_graphics(*, pdf_path: str | Path, pages: list[dict[str, Any]],
                            physical_pages: list[dict[str, Any]], existing_crops: list[dict[str, Any]],
                            existing_images: str | Path, output_images: str | Path,
                            inclusion_policy: str, run_id: str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Copy retained assets and append proven missing source occurrences."""
    if inclusion_policy != POLICY_ID:
        raise ValueError(f"explicit inclusion policy must be {POLICY_ID}")
    pdf_path = Path(pdf_path).resolve()
    existing_images, output_images = Path(existing_images).resolve(), Path(output_images).resolve()
    input_paths = [pdf_path, existing_images] + [Path(a["image"]).resolve() for a in pages + physical_pages]
    if any(output_images == p or output_images in p.parents or p in output_images.parents for p in input_paths):
        raise ValueError("output asset directory must be disjoint from retained inputs")
    if output_images.exists() and any(output_images.iterdir()):
        raise ValueError("output image directory must be new or empty")
    physical_by_number = {}
    for physical in physical_pages:
        number = physical.get("original_page_number") or physical.get("page_number") or physical.get("page")
        if number in physical_by_number:
            raise ValueError("duplicate physical page identity")
        physical_by_number[number] = physical
    names = set()
    retained_assets = []
    for row in existing_crops:
        for field in ("filename", "filename_alpha"):
            if not row.get(field):
                continue
            name = _safe_filename(row[field])
            if name in names:
                raise ValueError("duplicate retained crop filename")
            names.add(name)
            path = existing_images / name
            retained_assets.append({"filename": name, "sha256": sha256(path)})
    output_images.mkdir(parents=True, exist_ok=True)
    for asset in retained_assets:
        shutil.copyfile(existing_images / asset["filename"], output_images / asset["filename"])
    rows = deepcopy(existing_crops)
    report: dict[str, Any] = {"schema_version": "native_graphics_inventory_v1", "module_id": "recover_native_graphics_v1",
                            "policy": deepcopy(POLICY),
                            "run_id": run_id, "source_pdf": str(pdf_path), "source_pdf_sha256": sha256(pdf_path),
                            "retained_crop_records_sha256": _record_hash(existing_crops),
                            "retained_assets": retained_assets, "pages": [], "summary": {}}
    recovered = represented = held = 0
    seen_pages = set()
    with fitz.open(pdf_path) as document:
        for page in pages:
            number = page.get("page_number") or page.get("page")
            if number in seen_pages:
                raise ValueError("duplicate logical page identity")
            seen_pages.add(number)
            physical_number = page.get("original_page_number")
            entry = {"source_page": number, "physical_page": physical_number, "decisions": []}
            report["pages"].append(entry)
            try:
                if (not isinstance(physical_number, int) or physical_number < 1
                        or physical_number > len(document) or physical_number not in physical_by_number):
                    raise ValueError("missing or invalid physical page identity")
                physical = physical_by_number[physical_number]
                declared = physical.get("source") or []
                if str(pdf_path) not in [str(Path(path).resolve()) for path in declared]:
                    raise ValueError("physical raster source does not identify the supplied PDF")
                pdf_page = document[physical_number - 1]
                mapping = register_page(page, physical, pdf_page)
                entry["mapping"] = mapping
                decisions = associate_page(pdf_page, page.get("html") or page.get("raw_html") or "", mapping)
                entry["decisions"] = decisions
                associated_bounds = {tuple(d["native_group"]["bbox_pdf"]) for d in decisions if d.get("native_group")}
                entry["unassociated_native_groups"] = [
                    {"status": "held", "reason": "no_unique_catalog_anchor", "native_group": group}
                    for group in native_image_groups(pdf_page, fitz.Rect(mapping["viewport_pdf"]))
                    if tuple(group["bbox_pdf"]) not in associated_bounds]
                held += len(entry["unassociated_native_groups"])
            except (ValueError, KeyError, OSError) as exc:
                entry.update(status="held", reason=str(exc))
                held += 1
                continue
            existing = [r for r in existing_crops if r.get("source_page") == number]
            for decision in decisions:
                if decision["status"] != "associated":
                    held += 1
                    continue
                source_path = Path(page["image"]).resolve()
                inconsistent = [crop for crop in existing if crop.get("source_image")
                                and Path(crop["source_image"]).resolve() != source_path]
                if inconsistent:
                    decision.update(status="held", reason="existing_crop_coordinate_source_mismatch")
                    held += 1
                    continue
                covers = [crop["filename"] for crop in existing if _covered(decision["inner_bbox"], crop)]
                if covers:
                    decision.update(status="retained", reason="native_occurrence_already_cropped", existing_filenames=covers)
                    represented += 1
                    continue
                overlaps = [crop["filename"] for crop in existing if _intersects(decision["inner_bbox"], crop)]
                if overlaps:
                    decision.update(status="held", reason="existing_crop_partially_overlaps_native_occurrence",
                                    existing_filenames=overlaps)
                    held += 1
                    continue
                bbox = decision["bbox"]
                width, height = mapping["logical_dimensions"]
                if not (0 <= bbox["x0"] < bbox["x1"] <= width and 0 <= bbox["y0"] < bbox["y1"] <= height):
                    decision.update(status="held", reason="rounded_crop_exceeds_registered_viewport")
                    held += 1
                    continue
                occurrence = min(o["number"] for o in decision["native_group"]["occurrences"])
                filename = f"native-page-{number:03d}-occurrence-{occurrence:04d}.png"
                if filename in names:
                    raise ValueError("native crop filename collision")
                names.add(filename)
                with Image.open(source_path) as image:
                    crop = image.crop(tuple(bbox[k] for k in ("x0", "y0", "x1", "y1")))
                    crop.save(output_images / filename, format="PNG")
                    decoded_hash = hashlib.sha256(crop.tobytes()).hexdigest()
                    transparent = crop.mode in {"RGBA", "LA"} or "transparency" in crop.info
                    is_color = crop.mode not in {"1", "L", "LA"}
                provenance = {
                    "inclusion_policy": POLICY_ID, "source_pdf_sha256": report["source_pdf_sha256"],
                    "physical_page": physical_number, "native_group": decision["native_group"],
                    "anchor": decision["anchor"], "native_title": decision["native_title"],
                    "mapping": mapping, "bbox": bbox,
                    "crop_sha256": sha256(output_images / filename), "decoded_crop_sha256": decoded_hash,
                    "preserve_transcribed_text": True,
                }
                label = decision["anchor"]["label"]
                rows.append({
                    "schema_version": "illustration_v1", "module_id": "recover_native_graphics_v1",
                    "run_id": run_id, "source_image": str(source_path), "source_dimensions": [width, height],
                    "coordinate_system": "source_pixels", "crop_transform": "rectangle_and_encode",
                    "source_page": number, "filename": filename, "has_transparency": transparent,
                    "is_color": is_color, "alt": f"Source illustration beside {label}",
                    "image_description": f"Source illustration beside {label} — {label} — component reference",
                    "bbox": bbox, "area_ratio": bbox["width"] * bbox["height"] / (width * height),
                    "detection_method": "native_pdf_catalog_occurrence", "contains_text": True,
                    "critical_graphics_role": "component_reference", "critical_graphics_importance": "useful",
                    "nearby_text": label, "native_graphics_provenance": provenance,
                })
                decision.update(status="recovered", filename=filename, provenance=provenance)
                recovered += 1
    report["summary"] = {"retained_crop_rows": len(existing_crops), "recovered_occurrences": recovered,
                         "represented_native_occurrences": represented, "held_decisions_or_pages": held,
                         "provider_calls": 0}
    validate_native_inventory(rows, report, output_images)
    report["validation"] = {"sidecar_contract": "passed", "retained_encoded_bytes": "equal",
                            "recovered_decoded_source_pixels": "equal"}
    return rows, report
