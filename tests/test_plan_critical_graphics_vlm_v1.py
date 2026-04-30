from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from modules.transform.plan_critical_graphics_vlm_v1.main import (
    build_manifest,
    extract_json_object,
    normalize_page_plan,
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_extract_json_object_accepts_fenced_model_output() -> None:
    raw = """```json
{"targets": [{"importance": "critical", "role": "card grid"}]}
```"""

    parsed = extract_json_object(raw)

    assert parsed["targets"][0]["importance"] == "critical"


def test_normalize_page_plan_maps_roles_importance_and_bboxes() -> None:
    page = normalize_page_plan(
        {
            "page_role": "Card reference",
            "visual_density": "high",
            "targets": [
                {
                    "importance": "critical",
                    "role": "card grid",
                    "description": "Six programming cards",
                    "reason": "Visual card faces carry rule timing.",
                    "nearby_text": "Special Programming Cards",
                    "expected_visual_contents": "six cards",
                    "bbox": {"x0": 0.1, "y0": 0.2, "x1": 0.6, "y1": 0.7},
                    "confidence": 0.91,
                }
            ],
        },
        page_number=25,
        source_image="/tmp/page-025.png",
        image_width=1000,
        image_height=2000,
    )

    target = page["targets"][0]
    assert target["importance"] == "essential"
    assert target["role"] == "card_reference"
    assert target["bbox_pixels"] == {"x0": 100, "y0": 400, "x1": 600, "y1": 1400, "width": 500, "height": 1000}
    assert target["target_id"] == "p025-g01"
    assert target["confidence"] == 0.91


def test_build_manifest_can_fallback_from_ocr_without_api(tmp_path: Path) -> None:
    image_path = tmp_path / "page-001.png"
    Image.new("RGB", (80, 60), "white").save(image_path)
    pages_path = tmp_path / "pages.jsonl"
    html_path = tmp_path / "html.jsonl"
    raw_path = tmp_path / "raw.jsonl"
    _write_jsonl(pages_path, [{"page_number": 1, "image": str(image_path)}])
    _write_jsonl(
        html_path,
        [
            {
                "page_number": 1,
                "html": '<h1>Setup</h1><figure><img alt="Setup board diagram" data-count="2"></figure>',
            }
        ],
    )

    manifest = build_manifest(
        page_rows=list(json.loads(line) for line in pages_path.read_text().splitlines()),
        html_rows=list(json.loads(line) for line in html_path.read_text().splitlines()),
        model="test-model",
        run_id="test",
        max_context_chars=1000,
        max_long_side=0,
        max_output_tokens=1024,
        temperature=0.0,
        concurrency=1,
        timeout_seconds=None,
        fallback_from_ocr=True,
        raw_out_path=raw_path,
    )

    assert manifest["schema_version"] == "critical_graphics_manifest_v1"
    assert manifest["summary"]["uncertain_count"] == 2
    assert manifest["pages"][0]["targets"][0]["description"] == "Setup board diagram"
    assert raw_path.exists()
