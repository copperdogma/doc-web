"""Guided illustration cropping using OCR metadata + CV contour detection.

Two-pass approach:
1. OCR identifies pages with images (alt text + count)
2. This module runs CV detection ONLY on those pages, extracting N largest contours

This works because:
- We KNOW which pages have images (high confidence from GPT-5.1)
- CV just needs to find N largest non-text regions (not distinguish text from art)
- Falls back to vision model for edge cases
"""

import argparse
import base64
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple

import cv2
import numpy as np
from PIL import Image

import re

from modules.common import ensure_dir, save_jsonl, read_jsonl


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


try:
    from modules.common.openai_client import OpenAI
except Exception as exc:  # pragma: no cover - environment dependency
    OpenAI = None
    _OPENAI_IMPORT_ERROR = exc
else:
    _OPENAI_IMPORT_ERROR = None

try:
    from modules.common.google_client import GeminiVisionClient
except Exception as exc:  # pragma: no cover - environment dependency
    GeminiVisionClient = None
    _GEMINI_IMPORT_ERROR = exc
else:
    _GEMINI_IMPORT_ERROR = None


def _is_gemini_model(model: str) -> bool:
    return model.startswith("gemini-")


def _parse_gemini_box(item: dict) -> dict | None:
    """Extract bbox from a Gemini-native response item.

    Gemini models may return boxes as:
    - Standard: {"image_box": {"x0":..., "y0":..., ...}}
    - Array: {"image_box": [x0, y0, x1, y1]} or [y0, x0, y1, x1]
    - Native: {"box_2d": [y_min, x_min, y_max, x_max]} at 0-1000 scale

    For box_2d (Gemini's native trained format), swap axes and scale.
    Returns dict with x0, y0, x1, y1 in the standard orientation, or None.
    """
    # box_2d is Gemini's native format: [y_min, x_min, y_max, x_max] at 0-1000
    for key in ("box_2d", "box_3d", "box_4d"):
        raw = item.get(key)
        if isinstance(raw, (list, tuple)) and len(raw) == 4:
            try:
                vals = [float(v) for v in raw]
            except (TypeError, ValueError):
                continue
            # Gemini native: [y_min, x_min, y_max, x_max] → swap to [x0, y0, x1, y1]
            y_min, x_min, y_max, x_max = vals
            # Scale from 0-1000 to 0-1 if needed
            if any(v > 1.0 for v in vals):
                x_min, y_min, x_max, y_max = x_min / 1000, y_min / 1000, x_max / 1000, y_max / 1000
            return {"x0": x_min, "y0": y_min, "x1": x_max, "y1": y_max}
    return None


def _auto_fix_axis_swap(boxes: list, page_w: int, page_h: int) -> list:
    """Detect and fix Gemini's axis-swap tendency on all boxes from a page.

    Gemini sometimes returns [y0, x0, y1, x1] instead of [x0, y0, x1, y1] even
    when using standard image_box keys. We detect this by trying both interpretations
    and scoring each based on how well the resulting pixel boxes fit the page geometry.

    The key insight: on a portrait page (w < h), if coordinates are swapped, the
    pixel-space box aspect ratio will be distorted in a predictable way.
    """
    if not boxes or page_w == 0 or page_h == 0:
        return boxes

    def _pixel_boxes(blist, swap=False):
        """Convert normalized boxes to pixel coords, optionally swapping axes."""
        result = []
        for b in blist:
            x0, y0, x1, y1 = b["x0"], b["y0"], b["x1"], b["y1"]
            if swap:
                x0, y0, x1, y1 = y0, x0, y1, x1
            # Scale from 0-1000 to 0-1 if needed
            if any(v > 1.0 for v in (x0, y0, x1, y1)):
                x0, y0, x1, y1 = x0 / 1000, y0 / 1000, x1 / 1000, y1 / 1000
            # Ensure order
            if x0 > x1:
                x0, x1 = x1, x0
            if y0 > y1:
                y0, y1 = y1, y0
            px0, py0 = int(x0 * page_w), int(y0 * page_h)
            px1, py1 = int(x1 * page_w), int(y1 * page_h)
            result.append((px0, py0, px1, py1))
        return result

    def _score_boxes(pixel_boxes):
        """Score how reasonable a set of pixel boxes looks.
        Higher = more likely correct orientation."""
        score = 0.0
        for px0, py0, px1, py1 in pixel_boxes:
            bw = px1 - px0
            bh = py1 - py0
            if bw <= 0 or bh <= 0:
                score -= 10.0
                continue
            # Penalize out-of-bounds
            if px1 > page_w * 1.02 or py1 > page_h * 1.02:
                score -= 5.0
            # Reward boxes with reasonable area (not too tiny, not the whole page)
            area_ratio = (bw * bh) / (page_w * page_h)
            if 0.005 < area_ratio < 0.8:
                score += 1.0
            # Reward boxes that are centered or well-positioned
            # (not jammed into a corner with weird proportions)
            cx = (px0 + px1) / 2 / page_w
            cy = (py0 + py1) / 2 / page_h
            if 0.1 < cx < 0.9 and 0.1 < cy < 0.9:
                score += 0.5
        return score

    normal_pixels = _pixel_boxes(boxes, swap=False)
    swapped_pixels = _pixel_boxes(boxes, swap=True)
    score_normal = _score_boxes(normal_pixels)
    score_swapped = _score_boxes(swapped_pixels)

    if score_swapped > score_normal:
        fixed = []
        for b in boxes:
            b_copy = dict(b)
            b_copy["x0"], b_copy["y0"] = b["y0"], b["x0"]
            b_copy["x1"], b_copy["y1"] = b["y1"], b["x1"]
            fixed.append(b_copy)
        _log(f"    Auto-fix: swapped axes on {len(fixed)} box(es) (score {score_normal:.1f} → {score_swapped:.1f})")
        return fixed
    return boxes

Image.MAX_IMAGE_PIXELS = None

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp"}


def _normalize_output_format(output_format: Optional[str]) -> Tuple[str, str]:
    fmt = (output_format or "png").strip().lower().lstrip(".")
    if fmt == "jpg":
        fmt = "jpeg"
    if fmt not in {"png", "jpeg"}:
        raise ValueError(f"Unsupported output_format: {output_format}")
    ext = "png" if fmt == "png" else "jpg"
    return fmt, ext


_BBOX_PROMPT = """
You are given a scanned book page. Identify each distinct illustration or photo region.
Return a JSON array of objects with keys:
  - image_box: {x0, y0, x1, y1}
  - caption_box: {x0, y0, x1, y1} or null
  - image_description: string — brief description of the image content (e.g. "portrait of a man in military uniform", "pen-and-ink drawing of a farmhouse")
  - contains_text: boolean — true ONLY if the image INHERENTLY contains text as part of the image itself (e.g. stamps, seals, signs, memorial plaques, labels within diagrams, handwritten text on the photo, stylized title text). False for photos/illustrations with no integral text.
  - text_reason: string or null — if contains_text is true, explain what text is part of the image and why it belongs (e.g. "memorial plaque with engraved names", "official seal with organization name", "stylized book title in decorative font")
  - caption_text: string or null — if caption_box is non-null, transcribe the exact caption text (e.g. "Arthur L'Heureux, circa 1942"). Null if no caption.
  - source_issues: string or null — note any quality issues visible in the SOURCE photo itself, not crop issues (e.g. "top of head cut off in original photo", "photo is faded/damaged", "torn edge on right side")
- Coordinates must be normalized floats in [0,1], relative to the full image.
- Origin is top-left; x increases right, y increases down.
- image_box must be a tight box around the image content ONLY (exclude captions, page numbers, and body text).
- EXCEPTION — handwritten signatures, autographs, and hand-drawn marks are IMAGES, not text. Always include them inside image_box. If signatures appear next to a seal, stamp, or emblem, draw ONE image_box that encompasses the seal AND all adjacent signatures together.
- Stylized title text, decorative logos, or text rendered in artistic/display fonts that differ visually from body text ARE images — include them.
- If the image has a clear border, crop to that border.
- If there is any caption or nearby text directly below or above the image, caption_box MUST be that text region (non-null), even if it is a header line.
- Prefer to under-crop rather than include body text; if in doubt, shrink image_box to exclude printed text. But never exclude handwritten signatures.
- If multiple illustrations, return distinct, non-overlapping boxes in top-to-bottom, left-to-right order.
Return JSON only.
""".strip()

_CAPTION_PROMPT = """
You are given a scanned book page. Identify ONLY the caption or nearby text regions that belong to each illustration.
Return a JSON array of objects with keys: x0, y0, x1, y1.
- Each box must tightly bound the caption text (no image content).
- Captions can be above or below the image.
- Return boxes in the same order as the images appear top-to-bottom, left-to-right.
- If a caption is absent for an image, return a zero-area box by repeating x0,y0,x1,y1=0, or omit it.
Return JSON only.
""".strip()


# Keys propagated from detector VLM response through box transformations
_DETECTOR_META_KEYS = (
    "_description",
    "_contains_text",
    "_text_reason",
    "_source_issues",
    "_caption_text",
    "_nearby_text",
    "_expected_visual_contents",
    "_critical_graphics_target_id",
    "_critical_graphics_importance",
    "_critical_graphics_role",
    "_critical_graphics_reason",
)


def _copy_detector_meta(src: dict, dst: dict) -> dict:
    """Copy detector metadata keys from src box to dst box."""
    for k in _DETECTOR_META_KEYS:
        if k in src:
            dst[k] = src[k]
    return dst


def _autocrop_whitespace(img: Image.Image, white_threshold: int = 252) -> Tuple[int, int, int, int]:
    """Find bounding box of non-white content. Returns (x0, y0, x1, y1) in pixels."""
    arr = np.array(img.convert("L"))
    mask = arr < white_threshold
    if not mask.any():
        return (0, 0, img.width, img.height)
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    y0, y1 = int(np.argmax(rows)), int(len(rows) - np.argmax(rows[::-1]))
    x0, x1 = int(np.argmax(cols)), int(len(cols) - np.argmax(cols[::-1]))
    return (x0, y0, x1, y1)


def _encode_image(path: str) -> str:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(path)[1].lower().lstrip(".") or "jpeg"
    return f"data:image/{ext};base64,{b64}"


def _call_vlm_boxes(
    model: str,
    image_data: str,
    expected_count: int,
    alt_hints: Optional[List[str]],
    temperature: float,
    max_tokens: int,
    timeout_seconds: Optional[float],
    extra_instructions: Optional[str] = None,
) -> Tuple[List[Dict[str, float]], Optional[Any], Optional[str], str]:
    raw = ""
    usage = None
    request_id = None
    user_text = (
        f"Return up to {expected_count} boxes. "
        "If fewer illustrations are visible, return only the boxes you can see. "
        "Do NOT guess or invent extra boxes. "
        "Boxes must be distinct and should not significantly overlap."
    )
    if alt_hints:
        hints = "\n".join(f"{idx+1}. {text}" for idx, text in enumerate(alt_hints))
        user_text += (
            "\nImage descriptions (one per image, keep the same order):\n"
            f"{hints}"
        )
    if extra_instructions:
        user_text += f"\n{extra_instructions.strip()}"
    if _is_gemini_model(model):
        if GeminiVisionClient is None:  # pragma: no cover
            raise RuntimeError("google-genai package required") from _GEMINI_IMPORT_ERROR
        gclient = GeminiVisionClient()
        raw, usage, request_id = gclient.generate_vision(
            model=model,
            system_prompt=_BBOX_PROMPT,
            user_text=user_text,
            image_data=image_data,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        if OpenAI is None:  # pragma: no cover
            raise RuntimeError("openai package required") from _OPENAI_IMPORT_ERROR
        client = OpenAI(timeout=timeout_seconds) if timeout_seconds else OpenAI()
        if hasattr(client, "responses"):
            resp = client.responses.create(
                model=model,
                temperature=temperature,
                max_output_tokens=max_tokens,
                input=[
                    {"role": "system", "content": [{"type": "input_text", "text": _BBOX_PROMPT}]},
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": user_text},
                            {"type": "input_image", "image_url": image_data},
                        ],
                    },
                ],
            )
            raw = resp.output_text or ""
            usage = getattr(resp, "usage", None)
            request_id = getattr(resp, "id", None)
        else:
            resp = client.chat.completions.create(
                model=model,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": _BBOX_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_text},
                            {"type": "image_url", "image_url": {"url": image_data}},
                        ],
                    },
                ],
            )
            raw = resp.choices[0].message.content or ""

    boxes = []
    try:
        raw_json = raw.strip()
        if not raw_json.startswith("["):
            start = raw_json.find("[")
            end = raw_json.rfind("]")
            if start != -1 and end != -1:
                raw_json = raw_json[start:end + 1]
        data = json.loads(raw_json)
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                if "image_box" in item:
                    img_box = item.get("image_box") or {}
                    cap_box = item.get("caption_box")
                    schema_mode = True
                else:
                    # Check for Gemini native box_2d/box_3d/box_4d format
                    gemini_box = _parse_gemini_box(item)
                    if gemini_box is not None:
                        img_box = gemini_box
                        cap_box = None
                        schema_mode = False
                        # Pull description from Gemini's native fields
                        desc = item.get("label") or item.get("description") or ""
                        if desc:
                            img_box["_gemini_description"] = str(desc)
                    else:
                        img_box = item
                        cap_box = None
                        schema_mode = False
                # Handle array format from models.
                # Gemini returns arrays as [y0, x0, y1, x1] (native format) even
                # when asked for [x0, y0, x1, y1]. Swap axes for Gemini arrays.
                if isinstance(img_box, (list, tuple)) and len(img_box) == 4:
                    if _is_gemini_model(model):
                        # Gemini native: [y0, x0, y1, x1] → swap to [x0, y0, x1, y1]
                        img_box = {"x0": img_box[1], "y0": img_box[0], "x1": img_box[3], "y1": img_box[2]}
                    else:
                        img_box = {"x0": img_box[0], "y0": img_box[1], "x1": img_box[2], "y1": img_box[3]}
                if isinstance(cap_box, (list, tuple)) and len(cap_box) == 4:
                    if _is_gemini_model(model):
                        cap_box = {"x0": cap_box[1], "y0": cap_box[0], "x1": cap_box[3], "y1": cap_box[2]}
                    else:
                        cap_box = {"x0": cap_box[0], "y0": cap_box[1], "x1": cap_box[2], "y1": cap_box[3]}
                try:
                    x0 = float(img_box.get("x0"))
                    y0 = float(img_box.get("y0"))
                    x1 = float(img_box.get("x1"))
                    y1 = float(img_box.get("y1"))
                except Exception:
                    continue
                box = {"x0": x0, "y0": y0, "x1": x1, "y1": y1}
                if isinstance(cap_box, dict):
                    try:
                        cx0 = float(cap_box.get("x0"))
                        cy0 = float(cap_box.get("y0"))
                        cx1 = float(cap_box.get("x1"))
                        cy1 = float(cap_box.get("y1"))
                    except Exception:
                        cap_box = None
                    else:
                        box["caption_box"] = {
                            "x0": cx0,
                            "y0": cy0,
                            "x1": cx1,
                            "y1": cy1,
                        }
                # Detector metadata (enriched schema)
                if schema_mode:
                    box["_description"] = str(item.get("image_description") or "")
                    box["_contains_text"] = bool(item.get("contains_text", False))
                    box["_text_reason"] = str(item.get("text_reason") or "")
                    box["_source_issues"] = str(item.get("source_issues") or "")
                    box["_caption_text"] = str(item.get("caption_text") or "")
                elif img_box.get("_gemini_description"):
                    box["_description"] = img_box["_gemini_description"]
                boxes.append(box)
    except Exception:
        boxes = []
    return boxes, usage, request_id, raw


def _call_vlm_caption_boxes(
    model: str,
    image_data: str,
    expected_count: int,
    alt_hints: Optional[List[str]],
    temperature: float,
    max_tokens: int,
    timeout_seconds: Optional[float],
    extra_instructions: Optional[str] = None,
) -> Tuple[List[Dict[str, float]], Optional[Any], Optional[str], str]:
    raw = ""
    usage = None
    request_id = None
    user_text = f"Return up to {expected_count} caption boxes."
    if alt_hints:
        hints = "\n".join(f"{idx+1}. {text}" for idx, text in enumerate(alt_hints))
        user_text += (
            "\nImage descriptions (one per image, keep the same order):\n"
            f"{hints}"
        )
    if extra_instructions:
        user_text += f"\n{extra_instructions.strip()}"
    if _is_gemini_model(model):
        if GeminiVisionClient is None:  # pragma: no cover
            raise RuntimeError("google-genai package required") from _GEMINI_IMPORT_ERROR
        gclient = GeminiVisionClient()
        raw, usage, request_id = gclient.generate_vision(
            model=model,
            system_prompt=_CAPTION_PROMPT,
            user_text=user_text,
            image_data=image_data,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        if OpenAI is None:  # pragma: no cover
            raise RuntimeError("openai package required") from _OPENAI_IMPORT_ERROR
        client = OpenAI(timeout=timeout_seconds) if timeout_seconds else OpenAI()
        if hasattr(client, "responses"):
            resp = client.responses.create(
                model=model,
                temperature=temperature,
                max_output_tokens=max_tokens,
                input=[
                    {"role": "system", "content": [{"type": "input_text", "text": _CAPTION_PROMPT}]},
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": user_text},
                            {"type": "input_image", "image_url": image_data},
                        ],
                    },
                ],
            )
            raw = resp.output_text or ""
            usage = getattr(resp, "usage", None)
            request_id = getattr(resp, "id", None)
        else:
            resp = client.chat.completions.create(
                model=model,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": _CAPTION_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_text},
                            {"type": "image_url", "image_url": {"url": image_data}},
                        ],
                    },
                ],
            )
            raw = resp.choices[0].message.content or ""

    boxes: List[Dict[str, float]] = []
    try:
        raw_json = raw.strip()
        if not raw_json.startswith("["):
            start = raw_json.find("[")
            end = raw_json.rfind("]")
            if start != -1 and end != -1:
                raw_json = raw_json[start:end + 1]
        data = json.loads(raw_json)
        if isinstance(data, list):
            for item in data:
                # Handle array format [x0, y0, x1, y1] from some models
                if isinstance(item, (list, tuple)) and len(item) == 4:
                    item = {"x0": item[0], "y0": item[1], "x1": item[2], "y1": item[3]}
                if not isinstance(item, dict):
                    continue
                # Check for Gemini native box_2d format
                gemini_box = _parse_gemini_box(item)
                if gemini_box is not None:
                    boxes.append(gemini_box)
                    continue
                try:
                    x0 = float(item.get("x0"))
                    y0 = float(item.get("y0"))
                    x1 = float(item.get("x1"))
                    y1 = float(item.get("y1"))
                except Exception:
                    continue
                if x0 == x1 or y0 == y1:
                    continue
                boxes.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1})
    except Exception:
        boxes = []
    return boxes, usage, request_id, raw


def _normalize_box(box: Dict[str, float], w: int, h: int) -> Optional[Dict[str, int]]:
    try:
        raw_x0, raw_y0 = float(box["x0"]), float(box["y0"])
        raw_x1, raw_y1 = float(box["x1"]), float(box["y1"])
    except Exception:
        return None
    # Auto-detect coordinate scale per axis: models may return normalized (0-1),
    # Gemini 0-1000 scale, or pixel coordinates. Handle each axis independently
    # since some models mix scales (e.g. x in 0-1, y in 0-1000).
    def _normalize_axis(v0: float, v1: float, dim: int) -> Tuple[float, float]:
        max_v = max(abs(v0), abs(v1))
        if max_v <= 1.0:
            return v0, v1  # already normalized
        if max_v <= 1000:
            return v0 / 1000.0, v1 / 1000.0  # Gemini 0-1000 scale
        return v0 / float(dim), v1 / float(dim)  # pixel coordinates

    raw_x0, raw_x1 = _normalize_axis(raw_x0, raw_x1, w)
    raw_y0, raw_y1 = _normalize_axis(raw_y0, raw_y1, h)
    try:
        x0 = max(0.0, min(1.0, raw_x0))
        y0 = max(0.0, min(1.0, raw_y0))
        x1 = max(0.0, min(1.0, raw_x1))
        y1 = max(0.0, min(1.0, raw_y1))
    except Exception:
        return None
    if x1 <= x0 or y1 <= y0:
        return None
    ix0 = int(round(x0 * w))
    iy0 = int(round(y0 * h))
    ix1 = int(round(x1 * w))
    iy1 = int(round(y1 * h))
    ix0 = max(0, min(w - 1, ix0))
    iy0 = max(0, min(h - 1, iy0))
    ix1 = max(0, min(w, ix1))
    iy1 = max(0, min(h, iy1))
    if ix1 <= ix0 or iy1 <= iy0:
        return None
    return {
        "x0": ix0,
        "y0": iy0,
        "x1": ix1,
        "y1": iy1,
        "width": int(ix1 - ix0),
        "height": int(iy1 - iy0),
    }


def _apply_caption_box(box: Dict[str, int], margin_px: int, max_gap_ratio: float) -> Dict[str, int]:
    caption = box.get("caption_box")
    if not isinstance(caption, dict):
        return box
    try:
        cx0 = int(caption.get("x0", 0))
        cy0 = int(caption.get("y0", 0))
        cx1 = int(caption.get("x1", 0))
        cy1 = int(caption.get("y1", 0))
    except Exception:
        return box
    if cx1 <= cx0 or cy1 <= cy0:
        return box
    box = dict(box)
    overlap_x0 = max(box["x0"], cx0)
    overlap_x1 = min(box["x1"], cx1)
    overlap_w = max(0, overlap_x1 - overlap_x0)
    coverage_ratio = overlap_w / float(max(1, box["width"]))
    # Only trim the full box when the caption spans most of the crop width.
    # Partial-width captions under one side of an irregular image block (for example,
    # a seal on the left with signatures/caption on the right) otherwise slice off
    # valid image content on the untouched side.
    if coverage_ratio < 0.7:
        return box
    applied = False
    max_gap = int(max_gap_ratio * max(1, box["height"]))
    # If caption is below the image box (or overlaps), trim to caption start.
    if cy0 >= box["y0"] and cy0 <= box["y1"] + max_gap:
        new_y1 = cy0 - margin_px
        if new_y1 > box["y0"]:
            box["y1"] = new_y1
            box["height"] = new_y1 - box["y0"]
            applied = True
    # If caption is above the image box (or overlaps), trim to caption end.
    if cy1 >= box["y0"] - max_gap and cy1 <= box["y1"]:
        new_y0 = cy1 + margin_px
        if new_y0 < box["y1"]:
            box["y0"] = new_y0
            box["height"] = box["y1"] - new_y0
            applied = True
    if applied:
        box["_caption_applied"] = True
    return box


def _refine_boxes_remove_text_lines(
    img_gray: np.ndarray,
    boxes: List[Dict[str, int]],
    white_threshold: int,
    text_line_kernel_w: int,
    text_line_kernel_h: int,
    text_line_iterations: int,
    min_component_area_ratio: float = 0.05,
) -> List[Dict[str, int]]:
    if img_gray is None or not boxes:
        return boxes
    refined = []
    for box in boxes:
        x0, y0, x1, y1 = box["x0"], box["y0"], box["x1"], box["y1"]
        roi = img_gray[y0:y1, x0:x1]
        if roi.size == 0:
            refined.append(box)
            continue
        h, w = roi.shape[:2]
        roi_area = float(max(1, h * w))

        # Nonwhite mask for candidate image pixels.
        nonwhite = (roi < white_threshold).astype("uint8") * 255

        # Text-line mask: horizontal morphological open on thresholded ink.
        _, ink = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kw = max(text_line_kernel_w, w // 8)
        kh = max(1, text_line_kernel_h)
        kw = kw if kw % 2 == 1 else kw + 1
        kh = kh if kh % 2 == 1 else kh + 1
        line_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kw, kh))
        text_lines = cv2.morphologyEx(ink, cv2.MORPH_OPEN, line_kernel, iterations=text_line_iterations)
        # Slightly expand text lines to be safe.
        text_lines = cv2.dilate(text_lines, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)

        nontext = cv2.bitwise_and(nonwhite, cv2.bitwise_not(text_lines))
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(nontext, connectivity=8)
        best = None
        best_area = 0
        for lbl in range(1, num_labels):
            x, y, cw, ch, area = stats[lbl]
            if area <= 0:
                continue
            if area > best_area:
                best_area = area
                best = (x, y, cw, ch)
        if best is None:
            refined.append(box)
            continue
        if best_area / roi_area < min_component_area_ratio:
            refined.append(box)
            continue
        bx, by, bw, bh = best
        rx0 = x0 + bx
        ry0 = y0 + by
        rx1 = x0 + bx + bw
        ry1 = y0 + by + bh
        if rx1 <= rx0 or ry1 <= ry0:
            refined.append(box)
        else:
            new_box = {
                "x0": int(rx0),
                "y0": int(ry0),
                "x1": int(rx1),
                "y1": int(ry1),
                "width": int(rx1 - rx0),
                "height": int(ry1 - ry0),
            }
            _copy_detector_meta(box, new_box)
            refined.append(new_box)
    return refined


def _trim_text_edges(
    img_gray: np.ndarray,
    box: Dict[str, int],
    white_threshold: int,
    text_line_kernel_w: int,
    text_line_kernel_h: int,
    text_line_iterations: int,
    max_trim_ratio: float,
    margin_px: int,
) -> Dict[str, int]:
    x0, y0, x1, y1 = box["x0"], box["y0"], box["x1"], box["y1"]
    if y1 <= y0 or x1 <= x0:
        return box
    roi = img_gray[y0:y1, x0:x1]
    if roi.size == 0:
        return box
    h, w = roi.shape[:2]
    max_trim = int(h * max_trim_ratio)
    if max_trim <= 0:
        return box

    # Avoid trimming on mostly-ink regions unless the top/bottom band looks text-like.
    nonwhite_ratio = float(np.count_nonzero(roi < white_threshold)) / float(max(1, roi.size))
    effective_max_trim = max_trim
    if nonwhite_ratio < 0.25:
        effective_max_trim = max(effective_max_trim, int(h * 0.5))

    _, ink = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kw = max(text_line_kernel_w, w // 8)
    kh = max(1, text_line_kernel_h)
    kw = kw if kw % 2 == 1 else kw + 1
    kh = kh if kh % 2 == 1 else kh + 1
    line_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kw, kh))
    text_lines = cv2.morphologyEx(ink, cv2.MORPH_OPEN, line_kernel, iterations=text_line_iterations)
    row_ratio = (text_lines > 0).sum(axis=1) / float(max(1, w))
    if row_ratio.size == 0:
        return box
    thr = max(0.01, float(np.quantile(row_ratio, 0.9) * 0.5))

    # Allow trimming even on ink-heavy crops if text lines are concentrated near the edge.
    band_h = max(1, min(h, effective_max_trim))
    top_band = roi[:band_h, :]
    bottom_band = roi[h - band_h :, :]
    top_nonwhite = float(np.count_nonzero(top_band < white_threshold)) / float(max(1, top_band.size))
    bottom_nonwhite = float(np.count_nonzero(bottom_band < white_threshold)) / float(max(1, bottom_band.size))

    # Find first text band within the top window (even if there is whitespace above).
    top_trim = 0
    top_idx = None
    for i in range(0, min(h, effective_max_trim)):
        if row_ratio[i] >= thr:
            top_idx = i
            break
    if top_idx is not None:
        j = top_idx
        while j < h and row_ratio[j] >= thr:
            j += 1
        if (j - top_idx) > 0 and j <= effective_max_trim and (nonwhite_ratio <= 0.35 or top_nonwhite <= 0.2):
            top_trim = max(0, j + margin_px)

    # Find last text band within the bottom window.
    bottom_trim = 0
    bottom_idx = None
    for i in range(h - 1, max(-1, h - effective_max_trim) - 1, -1):
        if row_ratio[i] >= thr:
            bottom_idx = i
            break
    if bottom_idx is not None:
        j = bottom_idx
        while j >= 0 and row_ratio[j] >= thr:
            j -= 1
        band_start = j + 1
        if (bottom_idx - band_start + 1) > 0 and (h - band_start) <= effective_max_trim and (nonwhite_ratio <= 0.35 or bottom_nonwhite <= 0.2):
            bottom_trim = max(0, (h - band_start) + margin_px)

    if top_trim == 0 and bottom_trim == 0:
        # Fallback: detect a text band at the top followed by a clear white gap.
        row_nonwhite = (roi < white_threshold).sum(axis=1) / float(max(1, w))
        text_min = 0.05
        text_max = 0.35
        gap_max = 0.01
        band_min = 4
        gap_min = 6
        band_start = None
        band_end = None
        for i in range(0, min(h, effective_max_trim)):
            if text_min <= row_nonwhite[i] <= text_max:
                if band_start is None:
                    band_start = i
                band_end = i
            elif band_start is not None:
                if band_end is not None and (band_end - band_start + 1) >= band_min:
                    break
                band_start = None
                band_end = None
        if band_start is not None and band_end is not None and (band_end - band_start + 1) >= band_min:
            gap_len = 0
            gap_start = None
            for i in range(band_end + 1, min(h, effective_max_trim)):
                if row_nonwhite[i] <= gap_max:
                    if gap_start is None:
                        gap_start = i
                    gap_len += 1
                else:
                    if gap_len >= gap_min:
                        break
                    gap_start = None
                    gap_len = 0
            if gap_start is not None and gap_len >= gap_min and (nonwhite_ratio <= 0.45):
                new_y0 = y0 + max(0, gap_start + margin_px)
                new_y1 = y1
                if new_y1 > new_y0:
                    new_box = {
                        "x0": x0,
                        "y0": new_y0,
                        "x1": x1,
                        "y1": new_y1,
                        "width": x1 - x0,
                        "height": new_y1 - new_y0,
                    }
                    _copy_detector_meta(box, new_box)
                    return new_box
        return box

    new_y0 = y0 + top_trim
    new_y1 = y1 - bottom_trim
    if new_y1 <= new_y0:
        return box
    new_box = {
        "x0": x0,
        "y0": new_y0,
        "x1": x1,
        "y1": new_y1,
        "width": x1 - x0,
        "height": new_y1 - new_y0,
    }
    _copy_detector_meta(box, new_box)
    return new_box


def _should_mask_reference_panel_prose(box: Dict[str, Any]) -> bool:
    role = str(box.get("_critical_graphics_role") or "").casefold()
    if role != "card_reference":
        return False
    description = str(box.get("_description") or "").casefold()
    if any(cue in description for cue in ("annotated", "labelled", "labeled", "callout")):
        return False
    return any(cue in description for cue in ("reference images", "reference panel", "card faces", "card grid", "card sheet"))


def _should_split_card_reference_panel(box: Dict[str, Any]) -> bool:
    role = str(box.get("_critical_graphics_role") or "").casefold()
    if role != "card_reference":
        return False
    description = str(box.get("_description") or "").casefold()
    if any(cue in description for cue in ("annotated", "labelled", "labeled", "callout")):
        return False
    return any(cue in description for cue in ("reference images", "reference panel", "card faces", "card grid", "card sheet"))


def _mask_detached_graphic_background(cropped: Image.Image, box: Dict[str, Any]) -> Optional[Image.Image]:
    """Return an RGBA crop that hides detached prose around complex graphics.

    Course and board layouts are often irregular shapes. A rectangular source
    bbox can be correct for the map but still include prose below an empty
    corner. For map-like crops, make detected detached prose transparent while
    leaving the retained source pixels unchanged.
    """
    role = str(box.get("_critical_graphics_role") or "").casefold()
    if role != "map_or_board":
        return None
    rgb = cropped.convert("RGB")
    arr = np.asarray(rgb)
    h, w = arr.shape[:2]
    if h < 120 or w < 120:
        return None

    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 45, 140)

    # Saturated board elements, dark tracks/walls, and repeated tile/grid edges
    # are map signals. Plain paper and prose-only areas should not survive the
    # component-size filters below.
    signal = (
        (saturation > 32)
        | (value < 112)
        | (edges > 0)
    ).astype("uint8") * 255

    mask = np.full((h, w), 255, dtype=np.uint8)
    changed = False
    changed = _mask_bottom_text_components(signal, mask)
    changed = _mask_edge_prose_with_ocr(rgb, mask) or changed
    if not changed:
        return None
    rgba = np.dstack([arr, mask])
    result = Image.fromarray(rgba, mode="RGBA")
    result.info["_doc_web_masked_graphic_background"] = True
    return result


def _mask_detached_map_background(cropped: Image.Image, box: Dict[str, Any]) -> Optional[Image.Image]:
    return _mask_detached_graphic_background(cropped, box)


def _should_mask_text_heavy_rule_panel(box: Dict[str, Any]) -> bool:
    """Return true for large mixed prose+visual panels where prose is semantic HTML."""
    role = str(box.get("_critical_graphics_role") or "").casefold()
    if role != "rule_example_diagram":
        return False
    try:
        area_ratio = float(box.get("area_ratio") or 0.0)
    except (TypeError, ValueError):
        area_ratio = 0.0
    if area_ratio < 0.20:
        return False
    text = " ".join(
        str(box.get(key) or "")
        for key in ("_description", "_nearby_text", "_expected_visual_contents")
    ).casefold()
    # Callout labels are spatially integrated with the figure and should remain
    # source pixels; plain instructional prose around a visual panel can be
    # represented semantically and hidden in the crop.
    if any(cue in text for cue in ("callout box", "callout boxes", "yellow callout", "annotated callout")):
        return False
    return any(cue in text for cue in ("panel", "example", "upgrade", "reference", "diagram"))


def _mask_detached_rule_panel_prose(cropped: Image.Image, box: Dict[str, Any]) -> Optional[Image.Image]:
    if not _should_mask_text_heavy_rule_panel(box):
        return None
    rgb = cropped.convert("RGB")
    arr = np.asarray(rgb)
    alpha_mask = np.full((arr.shape[0], arr.shape[1]), 255, dtype=np.uint8)
    if not _mask_light_background_reference_prose(rgb, alpha_mask):
        return None
    rgba = np.dstack([arr, alpha_mask])
    result = Image.fromarray(rgba, mode="RGBA")
    result.info["_doc_web_masked_rule_panel_prose"] = True
    return result


def _mask_rule_panel_split_prose(cropped: Image.Image, box: Dict[str, Any]) -> Optional[Image.Image]:
    if str(box.get("_detection_method") or "") != "cv_guided_rule_panel_split":
        return None
    rgb = cropped.convert("RGB")
    arr = np.asarray(rgb)
    alpha_mask = np.full((arr.shape[0], arr.shape[1]), 255, dtype=np.uint8)
    if not _mask_light_edge_text_components(rgb, alpha_mask):
        return None
    rgba = np.dstack([arr, alpha_mask])
    result = Image.fromarray(rgba, mode="RGBA")
    result.info["_doc_web_masked_rule_panel_split_prose"] = True
    return result


def _mask_rule_panel_placement_layout_prose(cropped: Image.Image, box: Dict[str, Any]) -> Optional[Image.Image]:
    if str(box.get("_rule_panel_child_kind") or "") != "placement_layout":
        return None
    rgb = cropped.convert("RGB")
    arr = np.asarray(rgb)
    h, w = arr.shape[:2]
    if h < 120 or w < 120:
        return None
    visual_cluster = _mask_rule_panel_placement_layout_visual_cluster(arr)
    if visual_cluster is not None:
        visual_cluster.info["_doc_web_masked_rule_panel_placement_layout_visual_cluster"] = True
        return visual_cluster

    alpha_mask = np.full((h, w), 255, dtype=np.uint8)
    changed = _mask_light_upper_left_prose_margin(rgb, alpha_mask)
    if not changed:
        return None
    rgba = np.dstack([arr, alpha_mask])
    result = Image.fromarray(rgba, mode="RGBA")
    result.info["_doc_web_masked_rule_panel_placement_layout_prose"] = True
    return result


def _mask_rule_panel_placement_layout_visual_cluster(arr: np.ndarray) -> Optional[Image.Image]:
    """Keep sparse visual placement clusters while dropping ordinary surrounding prose."""
    h, w = arr.shape[:2]
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]

    visual_seed = (((saturation > 45) & (value > 55)) | (value < 82)).astype("uint8") * 255
    visual_seed = cv2.morphologyEx(
        visual_seed,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)),
        iterations=1,
    )
    visual_seed = cv2.dilate(
        visual_seed,
        cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)),
        iterations=1,
    )
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(visual_seed, connectivity=8)

    component_boxes: List[Tuple[int, int, int, int, int]] = []
    min_area = max(90, int(w * h * 0.00028))
    for label in range(1, num_labels):
        x, y, cw, ch, area = stats[label]
        if area < min_area:
            continue
        if cw < 8 or ch < 8:
            continue
        comp_sat = saturation[y:y + ch, x:x + cw]
        comp_val = value[y:y + ch, x:x + cw]
        sat_ratio = float(np.mean((comp_sat > 55) & (comp_val > 55)))
        dark_ratio = float(np.mean(comp_val < 95))
        text_like = ch <= max(24, int(h * 0.045)) and cw > ch * 5 and sat_ratio < 0.18
        low_saturation_text_like = (
            sat_ratio < 0.04
            and dark_ratio < 0.28
            and ch <= max(46, int(h * 0.055))
            and cw > ch * 1.9
            and area < w * h * 0.015
        )
        upper_left_prose_like = (
            (x + cw / 2.0) < w * 0.58
            and (y + ch / 2.0) < h * 0.38
            and sat_ratio < 0.20
            and ch < h * 0.12
        )
        if text_like or low_saturation_text_like or upper_left_prose_like:
            continue
        if sat_ratio < 0.03 and dark_ratio < 0.04 and area < w * h * 0.003:
            continue
        component_boxes.append((int(x), int(y), int(x + cw), int(y + ch), int(area)))

    if len(component_boxes) < 2:
        return None

    alpha = np.zeros((h, w), dtype=np.uint8)

    def paint_box(box: Tuple[int, int, int, int, int], pad: int) -> None:
        x0, y0, x1, y1, _area = box
        alpha[max(0, y0 - pad):min(h, y1 + pad), max(0, x0 - pad):min(w, x1 + pad)] = 255

    small_pad = max(5, int(min(w, h) * 0.01))
    for component in component_boxes:
        paint_box(component, small_pad)

    # Placement layouts often have one lower mat/card cluster and one upper card
    # cluster linked by thin guide lines. Group each cluster rectangularly so
    # source-pixel relationships remain legible without preserving prose bands.
    lower_group = [box for box in component_boxes if (box[1] + box[3]) / 2.0 > h * 0.42]
    if lower_group:
        gx0 = min(box[0] for box in lower_group)
        gy0 = min(box[1] for box in lower_group)
        gx1 = max(box[2] for box in lower_group)
        gy1 = max(box[3] for box in lower_group)
        if (gx1 - gx0) >= w * 0.12 and (gy1 - gy0) >= h * 0.08:
            pad = max(8, int(min(w, h) * 0.018))
            alpha[max(0, gy0 - pad):min(h, gy1 + pad), max(0, gx0 - pad):min(w, gx1 + pad)] = 255

    colored = ((saturation > 70) & (value > 70)).astype("uint8") * 255
    colored = cv2.dilate(
        colored,
        cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)),
        iterations=1,
    )
    alpha[colored > 0] = 255

    alpha = cv2.morphologyEx(
        alpha,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)),
        iterations=1,
    )
    if float(np.mean(alpha > 0)) > 0.86:
        return None

    ys, xs = np.where(alpha > 0)
    if ys.size == 0 or xs.size == 0:
        return None
    pad = max(4, int(min(w, h) * 0.01))
    x0 = max(0, int(xs.min()) - pad)
    y0 = max(0, int(ys.min()) - pad)
    x1 = min(w, int(xs.max()) + pad + 1)
    y1 = min(h, int(ys.max()) + pad + 1)
    if x1 <= x0 or y1 <= y0:
        return None

    rgba = np.dstack([arr, alpha])
    return Image.fromarray(rgba[y0:y1, x0:x1], mode="RGBA")


def _mask_light_upper_left_prose_margin(image: Image.Image, alpha_mask: np.ndarray) -> bool:
    arr = np.asarray(image.convert("RGB"))
    h, w = alpha_mask.shape[:2]
    top = int(h * 0.42)
    left = int(w * 0.58)
    if top <= 0 or left <= 0:
        return False
    hsv = cv2.cvtColor(arr[:top, :left], cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    light_ratio = float(np.mean((value > 160) & (saturation < 80)))
    if light_ratio < 0.55:
        return False
    gray = cv2.cvtColor(arr[:top, :left], cv2.COLOR_RGB2GRAY)
    protected = _saturated_visual_protection_mask(arr)
    text_signal = ((gray < 145) & (saturation < 115)).astype("uint8") * 255
    kernel_w = max(31, min(95, left // 12))
    if kernel_w % 2 == 0:
        kernel_w += 1
    text_like = cv2.morphologyEx(
        text_signal,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_w, 5)),
        iterations=1,
    )
    num_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(text_like, connectivity=8)
    changed = False
    for label in range(1, num_labels):
        x, y, cw, ch, area = stats[label]
        if area < max(40, int(left * top * 0.0003)):
            continue
        if cw < max(45, int(left * 0.04)):
            continue
        if ch < 4 or ch > max(42, int(top * 0.16)):
            continue
        component_sat = saturation[y:y + ch, x:x + cw]
        component_val = value[y:y + ch, x:x + cw]
        visual_ratio = float(np.mean((component_sat > 95) & (component_val > 80)))
        if visual_ratio > 0.12:
            continue
        pad_x = max(8, min(26, int(cw * 0.03)))
        pad_y = max(6, min(18, int(ch * 0.8)))
        my0 = max(0, y - pad_y)
        my1 = min(h, y + ch + pad_y)
        mx0 = max(0, x - pad_x)
        mx1 = min(w, x + cw + pad_x)
        region = alpha_mask[my0:my1, mx0:mx1]
        protected_region = protected[my0:my1, mx0:mx1] > 0
        region[~protected_region] = 0
        changed = True
    return changed


def _saturated_visual_protection_mask(arr: np.ndarray) -> np.ndarray:
    h, w = arr.shape[:2]
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    signal = ((saturation > 38) & (value > 65)).astype("uint8") * 255
    signal = cv2.morphologyEx(
        signal,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)),
        iterations=1,
    )
    signal = cv2.dilate(
        signal,
        cv2.getStructuringElement(cv2.MORPH_RECT, (28, 28)),
        iterations=1,
    )
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(signal, connectivity=8)
    protected = np.zeros((h, w), dtype=np.uint8)
    min_area = max(100, int(w * h * 0.00035))
    for label in range(1, num_labels):
        x, y, cw, ch, area = stats[label]
        if area < min_area:
            continue
        if cw < w * 0.025 and ch < h * 0.025:
            continue
        protected[labels == label] = 255
    return protected


def _mask_unprotected_light_text_lines(image: Image.Image, alpha_mask: np.ndarray) -> bool:
    """Clear OCR text lines that are not spatially inside saturated visuals."""
    try:
        import pytesseract
        from pytesseract import Output
    except Exception:
        return False
    try:
        data = pytesseract.image_to_data(image, output_type=Output.DICT, config="--psm 6")
    except Exception:
        return False

    arr = np.asarray(image.convert("RGB"))
    h, w = alpha_mask.shape[:2]
    protected = _saturated_visual_protection_mask(arr)
    words: List[Dict[str, Any]] = []
    texts = data.get("text") or []
    for idx, raw_text in enumerate(texts):
        text = str(raw_text or "").strip()
        if not re.search(r"[A-Za-z]{3,}", text):
            continue
        try:
            conf = float(data.get("conf", [])[idx])
        except Exception:
            conf = -1.0
        if conf >= 0 and conf < 20:
            continue
        try:
            x = int(data.get("left", [])[idx])
            y = int(data.get("top", [])[idx])
            bw = int(data.get("width", [])[idx])
            bh = int(data.get("height", [])[idx])
        except Exception:
            continue
        if bw <= 0 or bh <= 0:
            continue
        cx = min(w - 1, max(0, x + bw // 2))
        cy = min(h - 1, max(0, y + bh // 2))
        words.append(
            {
                "box": (x, y, x + bw, y + bh),
                "cy": cy,
                "protected": protected[cy, cx] > 0,
            }
        )
    if not words:
        return False

    words.sort(key=lambda item: (item["cy"], item["box"][0]))
    line_gap = max(12, int(h * 0.025))
    lines: List[Dict[str, Any]] = []
    for word in words:
        if not lines or abs(word["cy"] - lines[-1]["cy"]) > line_gap:
            lines.append({"words": [word], "cy": float(word["cy"])})
        else:
            lines[-1]["words"].append(word)
            lines[-1]["cy"] = sum(item["cy"] for item in lines[-1]["words"]) / len(lines[-1]["words"])

    changed = False
    for line in lines:
        line_words = line["words"]
        protected_ratio = sum(1 for word in line_words if word["protected"]) / float(len(line_words))
        if protected_ratio >= 0.45:
            continue
        x0 = min(word["box"][0] for word in line_words)
        y0 = min(word["box"][1] for word in line_words)
        x1 = max(word["box"][2] for word in line_words)
        y1 = max(word["box"][3] for word in line_words)
        pad = max(8, min(22, int((y1 - y0) * 0.8)))
        alpha_mask[max(0, y0 - pad):min(h, y1 + pad), max(0, x0 - pad):min(w, x1 + pad)] = 0
        changed = True
    return changed


def _mask_rule_example_edge_prose(cropped: Image.Image, box: Dict[str, Any]) -> Optional[Image.Image]:
    role = str(box.get("_critical_graphics_role") or "").casefold()
    if role != "rule_example_diagram":
        return None
    rgb = cropped.convert("RGB")
    arr = np.asarray(rgb)
    alpha_mask = np.full((arr.shape[0], arr.shape[1]), 255, dtype=np.uint8)
    if not _mask_light_edge_text_components(rgb, alpha_mask):
        return None
    rgba = np.dstack([arr, alpha_mask])
    result = Image.fromarray(rgba, mode="RGBA")
    result.info["_doc_web_masked_rule_example_edge_prose"] = True
    return result


def _mask_bottom_text_components(signal: np.ndarray, alpha_mask: np.ndarray) -> bool:
    """Clear detached horizontal text components in the lower edge band."""
    h, w = alpha_mask.shape[:2]
    if h <= 0 or w <= 0:
        return False
    kernel_w = max(17, min(45, w // 45))
    kernel_h = max(3, min(7, h // 140))
    if kernel_w % 2 == 0:
        kernel_w += 1
    if kernel_h % 2 == 0:
        kernel_h += 1
    text_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_w, kernel_h))
    text_like = cv2.morphologyEx(signal, cv2.MORPH_CLOSE, text_kernel, iterations=1)
    num_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(text_like, connectivity=8)
    changed = False
    for label in range(1, num_labels):
        x, y, cw, ch, area = stats[label]
        if area <= 0:
            continue
        if y < h * 0.68:
            continue
        if x > w * 0.28 and (x + cw) < w * 0.72:
            continue
        if ch > h * 0.09:
            continue
        if cw < w * 0.035 or cw > w * 0.38:
            continue
        density = area / float(max(1, cw * ch))
        if density < 0.2:
            continue
        pad = max(4, min(18, int(max(cw, ch) * 0.05)))
        x0 = max(0, int(x) - pad)
        y0 = max(0, int(y) - pad)
        x1 = min(w, int(x + cw) + pad)
        y1 = min(h, int(y + ch) + pad)
        alpha_mask[y0:y1, x0:x1] = 0
        changed = True
    return changed


def _mask_edge_prose_with_ocr(image: Image.Image, alpha_mask: np.ndarray) -> bool:
    """Clear OCR-detected prose words near the bottom edge of a map crop."""
    try:
        import pytesseract
        from pytesseract import Output
    except Exception:
        return False
    try:
        data = pytesseract.image_to_data(image, output_type=Output.DICT, config="--psm 6")
    except Exception:
        return False
    h, w = alpha_mask.shape[:2]
    changed = False
    texts = data.get("text") or []
    for idx, raw_text in enumerate(texts):
        text = str(raw_text or "").strip()
        if not re.search(r"[A-Za-z]{3,}", text):
            continue
        try:
            conf = float(data.get("conf", [])[idx])
        except Exception:
            conf = -1.0
        if conf >= 0 and conf < 20:
            continue
        try:
            x = int(data.get("left", [])[idx])
            y = int(data.get("top", [])[idx])
            bw = int(data.get("width", [])[idx])
            bh = int(data.get("height", [])[idx])
        except Exception:
            continue
        if bw <= 0 or bh <= 0:
            continue
        if y < h * 0.62:
            continue
        if x > w * 0.28 and (x + bw) < w * 0.72:
            continue
        pad = max(4, min(18, int(max(bw, bh) * 0.08)))
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(w, x + bw + pad)
        y1 = min(h, y + bh + pad)
        alpha_mask[y0:y1, x0:x1] = 0
        changed = True
    return changed


def _mask_light_background_reference_prose(image: Image.Image, alpha_mask: np.ndarray) -> bool:
    """Clear OCR words printed on light paper while preserving dark card faces."""
    try:
        import pytesseract
        from pytesseract import Output
    except Exception:
        return False
    try:
        data = pytesseract.image_to_data(image, output_type=Output.DICT, config="--psm 6")
    except Exception:
        return False
    arr = np.asarray(image.convert("RGB"))
    h, w = alpha_mask.shape[:2]
    boxes = []
    texts = data.get("text") or []
    for idx, raw_text in enumerate(texts):
        text = str(raw_text or "").strip()
        if not re.search(r"[A-Za-z]{3,}", text):
            continue
        try:
            conf = float(data.get("conf", [])[idx])
        except Exception:
            conf = -1.0
        if conf >= 0 and conf < 20:
            continue
        try:
            x = int(data.get("left", [])[idx])
            y = int(data.get("top", [])[idx])
            bw = int(data.get("width", [])[idx])
            bh = int(data.get("height", [])[idx])
        except Exception:
            continue
        if bw <= 0 or bh <= 0:
            continue
        pad = max(4, min(18, int(max(bw, bh) * 0.12)))
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(w, x + bw + pad)
        y1 = min(h, y + bh + pad)
        roi = arr[y0:y1, x0:x1]
        if roi.size == 0:
            continue
        mean_value = float(np.mean(np.max(roi, axis=2)))
        mean_saturation = float(np.mean(cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)[:, :, 1]))
        # Body/prose labels sit on light paper. Card titles sit inside dark,
        # saturated card frames and should remain source pixels.
        if mean_value < 150 or mean_saturation > 95:
            continue
        boxes.append((x0, y0, x1, y1))
    if not boxes:
        return False

    boxes.sort(key=lambda item: ((item[1] + item[3]) / 2, item[0]))
    line_gap = max(18, int(h * 0.025))
    lines: list[list[tuple[int, int, int, int]]] = []
    for box in boxes:
        cy = (box[1] + box[3]) / 2
        if not lines:
            lines.append([box])
            continue
        last = lines[-1]
        last_cy = sum((b[1] + b[3]) / 2 for b in last) / len(last)
        if abs(cy - last_cy) <= line_gap or box[1] <= max(b[3] for b in last):
            last.append(box)
        else:
            lines.append([box])

    line_boxes = [
        (
            min(b[0] for b in line),
            min(b[1] for b in line),
            max(b[2] for b in line),
            max(b[3] for b in line),
        )
        for line in lines
    ]
    clusters: list[list[tuple[int, int, int, int]]] = []
    paragraph_gap = max(38, int(h * 0.04))
    for line_box in line_boxes:
        if not clusters:
            clusters.append([line_box])
            continue
        last = clusters[-1]
        previous = last[-1]
        vertical_gap = line_box[1] - previous[3]
        horizontal_overlap = min(line_box[2], previous[2]) - max(line_box[0], previous[0])
        if vertical_gap <= paragraph_gap and horizontal_overlap >= -max(30, int(w * 0.03)):
            last.append(line_box)
        else:
            clusters.append([line_box])

    for cluster in clusters:
        pad = max(12, int(max((b[3] - b[1]) for b in cluster) * 1.2), int(h * 0.015))
        x0 = max(0, min(b[0] for b in cluster) - pad)
        y0 = max(0, min(b[1] for b in cluster) - pad)
        x1 = min(w, max(b[2] for b in cluster) + pad)
        y1 = min(h, max(b[3] for b in cluster) + pad)
        alpha_mask[y0:y1, x0:x1] = 0
    return True


def _mask_light_edge_text_components(image: Image.Image, alpha_mask: np.ndarray) -> bool:
    """Clear partial prose clipped into light edge bands of split visual crops."""
    arr = np.asarray(image.convert("RGB"))
    h, w = alpha_mask.shape[:2]
    if h < 80 or w < 80:
        return False
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    text_like = ((value < 170) & (saturation < 90)).astype("uint8") * 255
    if not np.any(text_like):
        return False
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    text_like = cv2.morphologyEx(text_like, cv2.MORPH_OPEN, kernel, iterations=1)
    num_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(text_like, connectivity=8)
    changed = False
    right_start = int(w * 0.78)
    right_sat = saturation[:, right_start:w]
    right_val = value[:, right_start:w]
    if right_sat.size:
        right_light_ratio = float(np.mean((right_val > 170) & (right_sat < 80)))
        right_text_ratio = float(np.mean((right_val < 145) & (right_sat < 90)))
        if right_light_ratio > 0.45 and right_text_ratio > 0.002:
            alpha_mask[:, right_start:w] = 0
            changed = True
    for label in range(1, num_labels):
        x, y, cw, ch, area = stats[label]
        if area < 6 or area > max(800, int(w * h * 0.01)):
            continue
        if cw > w * 0.22 or ch > h * 0.18:
            continue
        pad = max(5, min(18, int(max(cw, ch) * 0.35)))
        x0 = max(0, int(x) - pad)
        y0 = max(0, int(y) - pad)
        x1 = min(w, int(x + cw) + pad)
        y1 = min(h, int(y + ch) + pad)
        edge_x = max(14, int(w * 0.06))
        edge_y = max(14, int(h * 0.06))
        touches_edge = x0 <= edge_x or x1 >= w - edge_x or y0 <= edge_y or y1 >= h - edge_y
        if not touches_edge:
            continue
        roi_sat = saturation[y0:y1, x0:x1]
        roi_val = value[y0:y1, x0:x1]
        if roi_sat.size == 0:
            continue
        light_ratio = float(np.mean((roi_val > 170) & (roi_sat < 80)))
        if light_ratio < 0.35:
            continue
        alpha_mask[y0:y1, x0:x1] = 0
        changed = True
    return changed


def _box_has_text_band(
    img_gray: np.ndarray,
    box: Dict[str, int],
    white_threshold: int,
    edge_ratio: float,
) -> bool:
    x0, y0, x1, y1 = box["x0"], box["y0"], box["x1"], box["y1"]
    if x1 <= x0 or y1 <= y0:
        return False
    roi = img_gray[y0:y1, x0:x1]
    if roi.size == 0:
        return False
    h, w = roi.shape[:2]
    window = int(h * edge_ratio)
    if window <= 0:
        return False
    row_nonwhite = (roi < white_threshold).sum(axis=1) / float(max(1, w))
    text_min = 0.05
    text_max = 0.45
    band_min = 4
    gap_min = 6
    gap_max = 0.01

    def _has_band_with_gap(start: int, end: int) -> bool:
        run = 0
        band_start = None
        band_end = None
        for i in range(start, end):
            if text_min <= row_nonwhite[i] <= text_max:
                if band_start is None:
                    band_start = i
                run += 1
                band_end = i
            else:
                if run >= band_min:
                    break
                run = 0
                band_start = None
                band_end = None
        if band_start is None or band_end is None or run < band_min:
            return False
        gap_len = 0
        for i in range(band_end + 1, end):
            if row_nonwhite[i] <= gap_max:
                gap_len += 1
                if gap_len >= gap_min:
                    return True
            else:
                gap_len = 0
        return False

    top_end = min(h, window)
    if _has_band_with_gap(0, top_end):
        return True
    bottom_start = max(0, h - window)
    if _has_band_with_gap(bottom_start, h):
        return True
    return False


def _trim_box_by_ocr_text(
    img_gray: np.ndarray,
    box: Dict[str, int],
    tesseract_cmd: Optional[str],
    edge_ratio: float,
    min_conf: int,
    min_word_len: int,
    white_threshold: int,
    min_line_words: int,
    min_line_chars: int,
    max_trim_ratio: float,
    margin_px: int,
) -> Dict[str, int]:
    if tesseract_cmd is None:
        return box
    x0, y0, x1, y1 = box["x0"], box["y0"], box["x1"], box["y1"]
    if x1 <= x0 or y1 <= y0:
        return box
    roi = img_gray[y0:y1, x0:x1]
    if roi.size == 0:
        return box
    h, w = roi.shape[:2]
    window = int(h * edge_ratio)
    if window <= 0:
        return box
    max_trim = int(h * max_trim_ratio)
    if max_trim <= 0:
        return box
    try:
        import tempfile
        import subprocess

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "crop.png"
            cv2.imwrite(str(tmp_path), roi)
            cmd = [
                tesseract_cmd,
                str(tmp_path),
                "stdout",
                "--psm",
                "6",
                "tsv",
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if proc.returncode != 0:
                return box
            lines = proc.stdout.splitlines()
    except Exception:
        return box

    top_text_max = None
    bottom_text_min = None
    lines_by_id: Dict[Tuple[int, int, int], Dict[str, int]] = {}
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) < 12:
            continue
        try:
            conf = int(float(parts[10]))
        except Exception:
            continue
        text = parts[11].strip()
        if conf < min_conf or len(text) < min_word_len:
            continue
        try:
            block_num = int(parts[2])
            par_num = int(parts[4])
            line_num = int(parts[5])
            y = int(parts[7])
            h_box = int(parts[9])
        except Exception:
            continue
        if h_box <= 0:
            continue
        key = (block_num, par_num, line_num)
        entry = lines_by_id.get(key)
        if entry is None:
            entry = {"words": 0, "chars": 0, "y0": y, "y1": y + h_box}
            lines_by_id[key] = entry
        entry["words"] += 1
        entry["chars"] += len(text)
        if y < entry["y0"]:
            entry["y0"] = y
        if y + h_box > entry["y1"]:
            entry["y1"] = y + h_box

    for entry in lines_by_id.values():
        if entry["words"] < min_line_words or entry["chars"] < min_line_chars:
            continue
        y0_box = entry["y0"]
        y1_box = entry["y1"]
        if y1_box <= window:
            if top_text_max is None or y1_box > top_text_max:
                top_text_max = y1_box
        if y0_box >= h - window:
            if bottom_text_min is None or y0_box < bottom_text_min:
                bottom_text_min = y0_box

    new_y0 = y0
    new_y1 = y1
    if top_text_max is not None:
        trim = min(max_trim, top_text_max + margin_px)
        if trim > 0:
            new_y0 = y0 + trim
    if bottom_text_min is not None:
        trim = min(max_trim, (h - bottom_text_min) + margin_px)
        if trim > 0:
            new_y1 = y1 - trim
    if new_y1 <= new_y0:
        return box
    if new_y0 == y0 and new_y1 == y1:
        return box
    new_box = {
        "x0": x0,
        "y0": new_y0,
        "x1": x1,
        "y1": new_y1,
        "width": x1 - x0,
        "height": new_y1 - new_y0,
    }
    _copy_detector_meta(box, new_box)
    return new_box


def _trim_box_by_layout_text(
    box: Dict[str, int],
    text_boxes: List[Any],
    max_gap_ratio: float,
    bottom_band_ratio: float,
    top_band_ratio: float,
    margin_px: int,
    min_width_ratio: float,
    max_height_ratio: float,
) -> Dict[str, int]:
    x0, y0, x1, y1 = box["x0"], box["y0"], box["x1"], box["y1"]
    if x1 <= x0 or y1 <= y0:
        return box
    h = y1 - y0
    max_gap = max(0, int(h * max_gap_ratio))
    bottom_band = y0 + int(h * (1.0 - bottom_band_ratio))
    top_band = y0 + int(h * top_band_ratio)
    bottom_trim = None
    top_trim = None
    for tb in text_boxes:
        if isinstance(tb, dict):
            try:
                tx0, ty0, tx1, ty1 = tb["x0"], tb["y0"], tb["x1"], tb["y1"]
            except Exception:
                continue
            tb.get("label")
        else:
            if len(tb) != 4:
                continue
            tx0, ty0, tx1, ty1 = tb
        if ty1 < y0 - max_gap or ty0 > y1 + max_gap:
            continue
        tw = tx1 - tx0
        th = ty1 - ty0
        if tw <= 0 or th <= 0:
            continue
        # Text box must overlap horizontally with image box — otherwise
        # text in an adjacent column can incorrectly trim the image.
        overlap_x = min(tx1, x1) - max(tx0, x0)
        if overlap_x <= 0:
            continue
        if (tw / float(max(1, x1 - x0))) < min_width_ratio:
            continue
        if (th / float(max(1, y1 - y0))) > max_height_ratio:
            continue
        if ty0 >= bottom_band and ty0 <= y1 + max_gap:
            if bottom_trim is None or ty0 < bottom_trim:
                bottom_trim = ty0
        if ty1 <= top_band and ty1 >= y0 - max_gap:
            if top_trim is None or ty1 > top_trim:
                top_trim = ty1
    new_y0 = y0
    new_y1 = y1
    if top_trim is not None:
        new_y0 = max(new_y0, top_trim + margin_px)
    if bottom_trim is not None:
        new_y1 = min(new_y1, bottom_trim - margin_px)
    if new_y1 <= new_y0:
        return box
    if new_y0 == y0 and new_y1 == y1:
        return box
    new_box = {
        "x0": x0,
        "y0": new_y0,
        "x1": x1,
        "y1": new_y1,
        "width": x1 - x0,
        "height": new_y1 - new_y0,
    }
    _copy_detector_meta(box, new_box)
    return new_box


def _split_box_by_layout_text_band(
    box: Dict[str, int],
    text_boxes: List[Any],
    min_width_ratio: float,
    max_height_ratio: float,
    min_gap_ratio: float,
    margin_px: int,
) -> List[Dict[str, int]]:
    x0, y0, x1, y1 = box["x0"], box["y0"], box["x1"], box["y1"]
    if x1 <= x0 or y1 <= y0:
        return [box]
    bw = x1 - x0
    bh = y1 - y0
    min_gap = max(1, int(bh * min_gap_ratio))
    bands = []
    for tb in text_boxes:
        if isinstance(tb, dict):
            try:
                tx0, ty0, tx1, ty1 = tb["x0"], tb["y0"], tb["x1"], tb["y1"]
            except Exception:
                continue
        else:
            if len(tb) != 4:
                continue
            tx0, ty0, tx1, ty1 = tb
        if ty1 <= y0 or ty0 >= y1:
            continue
        tw = tx1 - tx0
        th = ty1 - ty0
        if tw <= 0 or th <= 0:
            continue
        # Text box must overlap horizontally with image box
        overlap_x = min(tx1, x1) - max(tx0, x0)
        if overlap_x <= 0:
            continue
        if (tw / float(max(1, bw))) < min_width_ratio:
            continue
        if (th / float(max(1, bh))) > max_height_ratio:
            continue
        bands.append((ty0, ty1))
    if not bands:
        return [box]
    band_y0 = min(b[0] for b in bands)
    band_y1 = max(b[1] for b in bands)
    if band_y0 - y0 < min_gap or y1 - band_y1 < min_gap:
        return [box]
    top_y1 = band_y0 - margin_px
    bottom_y0 = band_y1 + margin_px
    out = []
    if top_y1 > y0:
        top_box = {
            "x0": x0,
            "y0": y0,
            "x1": x1,
            "y1": top_y1,
            "width": bw,
            "height": top_y1 - y0,
        }
        _copy_detector_meta(box, top_box)
        out.append(top_box)
    if bottom_y0 < y1:
        bottom_box = {
            "x0": x0,
            "y0": bottom_y0,
            "x1": x1,
            "y1": y1,
            "width": bw,
            "height": y1 - bottom_y0,
        }
        _copy_detector_meta(box, bottom_box)
        out.append(bottom_box)
    return out if out else [box]


def _layout_text_boxes_for_page(
    layout_engine: Any,
    image_path: str,
    score_thresh: float,
) -> List[Dict[str, int]]:
    try:
        results = layout_engine.predict(image_path)
    except Exception:
        return []
    if not results:
        return []
    record = results[0]
    boxes = []
    for item in record.get("boxes", []):
        label = item.get("label")
        score = float(item.get("score", 1.0))
        if label not in ("text", "figure_title", "doc_title", "number"):
            continue
        if score < score_thresh:
            continue
        coords = item.get("coordinate") or []
        if len(coords) != 4:
            continue
        x0, y0, x1, y1 = [int(round(float(v))) for v in coords]
        if x1 <= x0 or y1 <= y0:
            continue
        boxes.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "label": label})
    return boxes


def _layout_image_boxes_for_page(
    layout_engine: Any,
    image_path: str,
    score_thresh: float,
) -> List[Dict[str, int]]:
    try:
        results = layout_engine.predict(image_path)
    except Exception:
        return []
    if not results:
        return []
    record = results[0]
    boxes = []
    for item in record.get("boxes", []):
        label = item.get("label")
        score = float(item.get("score", 1.0))
        if label != "image" or score < score_thresh:
            continue
        coords = item.get("coordinate") or []
        if len(coords) != 4:
            continue
        x0, y0, x1, y1 = [int(round(float(v))) for v in coords]
        if x1 <= x0 or y1 <= y0:
            continue
        boxes.append(
            {
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "width": x1 - x0,
                "height": y1 - y0,
            }
        )
    return boxes


def _refine_boxes_with_nonwhite(
    image_path: str,
    boxes: List[Dict[str, int]],
    white_threshold: int,
    close_kernel: int,
    close_iterations: int,
) -> List[Dict[str, int]]:
    if not boxes:
        return boxes
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return boxes
    h, w = img.shape[:2]
    mask = (img < white_threshold).astype("uint8") * 255
    k = close_kernel if close_kernel % 2 == 1 else close_kernel + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=close_iterations)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    refined = []
    for box in boxes:
        x0, y0, x1, y1 = box["x0"], box["y0"], box["x1"], box["y1"]
        region = labels[y0:y1, x0:x1]
        if region.size == 0:
            refined.append(box)
            continue
        overlap_labels = set(int(v) for v in np.unique(region) if v > 0)
        if not overlap_labels:
            refined.append(box)
            continue
        xs = []
        ys = []
        xes = []
        yes = []
        for lbl in overlap_labels:
            x, y, cw, ch, _area = stats[lbl]
            xs.append(x)
            ys.append(y)
            xes.append(x + cw)
            yes.append(y + ch)
        rx0 = max(0, min(xs))
        ry0 = max(0, min(ys))
        rx1 = min(w, max(xes))
        ry1 = min(h, max(yes))
        if rx1 <= rx0 or ry1 <= ry0:
            refined.append(box)
        else:
            new_box = {
                "x0": int(rx0),
                "y0": int(ry0),
                "x1": int(rx1),
                "y1": int(ry1),
                "width": int(rx1 - rx0),
                "height": int(ry1 - ry0),
            }
            _copy_detector_meta(box, new_box)
            refined.append(new_box)
    return refined


def _refine_boxes_with_nontext(
    img_gray: np.ndarray,
    boxes: List[Dict[str, int]],
    white_threshold: int,
    close_kernel: int,
    close_iterations: int,
    text_block_kernel_w: int,
    text_block_kernel_h: int,
    text_block_iterations: int,
    min_component_area_ratio: float = 0.02,
) -> List[Dict[str, int]]:
    if img_gray is None or not boxes:
        return boxes
    refined = []
    for box in boxes:
        x0, y0, x1, y1 = box["x0"], box["y0"], box["x1"], box["y1"]
        roi = img_gray[y0:y1, x0:x1]
        if roi.size == 0:
            refined.append(box)
            continue
        h, w = roi.shape[:2]
        roi_area = float(max(1, h * w))

        nonwhite = (roi < white_threshold).astype("uint8") * 255
        k = close_kernel if close_kernel % 2 == 1 else close_kernel + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
        nonwhite = cv2.morphologyEx(nonwhite, cv2.MORPH_CLOSE, kernel, iterations=close_iterations)

        _, text_bin = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kw = text_block_kernel_w if text_block_kernel_w % 2 == 1 else text_block_kernel_w + 1
        kh = text_block_kernel_h if text_block_kernel_h % 2 == 1 else text_block_kernel_h + 1
        text_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kw, kh))
        text_blocks = cv2.dilate(text_bin, text_kernel, iterations=text_block_iterations)

        nontext = cv2.bitwise_and(nonwhite, cv2.bitwise_not(text_blocks))
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(nontext, connectivity=8)
        best = None
        best_area = 0
        for lbl in range(1, num_labels):
            x, y, cw, ch, area = stats[lbl]
            if area <= 0:
                continue
            if area > best_area:
                best_area = area
                best = (x, y, cw, ch)
        if best is None:
            refined.append(box)
            continue
        if best_area / roi_area < min_component_area_ratio:
            refined.append(box)
            continue
        bx, by, bw, bh = best
        rx0 = x0 + bx
        ry0 = y0 + by
        rx1 = x0 + bx + bw
        ry1 = y0 + by + bh
        if rx1 <= rx0 or ry1 <= ry0:
            refined.append(box)
        else:
            new_box = {
                "x0": int(rx0),
                "y0": int(ry0),
                "x1": int(rx1),
                "y1": int(ry1),
                "width": int(rx1 - rx0),
                "height": int(ry1 - ry0),
            }
            _copy_detector_meta(box, new_box)
            refined.append(new_box)
    return refined


def _trim_caption_from_box(
    img_gray: np.ndarray,
    box: Dict[str, int],
    max_caption_height_ratio: float,
    text_ratio_threshold: float,
    margin_px: int,
    caption_max_nonwhite_ratio: float,
    white_threshold: int,
) -> Dict[str, int]:
    x0, y0, x1, y1 = box["x0"], box["y0"], box["x1"], box["y1"]
    if y1 <= y0 or x1 <= x0:
        return box
    h_box = y1 - y0
    max_caption_h = int(h_box * max_caption_height_ratio)
    if max_caption_h <= 0:
        return box
    roi = img_gray[y0:y1, x0:x1]
    if roi.size == 0:
        return box
    caption_h = min(max_caption_h, roi.shape[0])
    caption_roi = roi[-caption_h:, :]
    caption_nonwhite = float(np.count_nonzero(caption_roi < white_threshold)) / float(caption_roi.size)
    start = max(0, h_box - max_caption_h)
    band = roi[start:h_box, :]
    if band.size == 0:
        return box

    # Text-line projection (caption detection).
    _, text_bin = cv2.threshold(band, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel_w = max(30, band.shape[1] // 10)
    text_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_w, 1))
    text_lines = cv2.morphologyEx(text_bin, cv2.MORPH_OPEN, text_kernel, iterations=1)
    row_counts = (text_lines > 0).sum(axis=1) / float(max(1, band.shape[1]))
    if row_counts.size:
        # Dynamic threshold for text-line density.
        thr = max(0.01, float(np.quantile(row_counts, 0.9) * 0.5))
        # Find bottom-most run of text-like rows.
        last_idx = None
        for idx in range(len(row_counts) - 1, -1, -1):
            if row_counts[idx] >= thr:
                last_idx = idx
                break
        if last_idx is not None:
            top_idx = last_idx
            while top_idx > 0 and row_counts[top_idx - 1] >= thr:
                top_idx -= 1
            # Only treat as caption if it's in the bottom half of the band.
            if top_idx >= int(0.5 * band.shape[0]):
                cut_row = top_idx
                new_y1 = y0 + start + cut_row - margin_px
                if new_y1 > y0:
                    new_box = {
                        "x0": x0,
                        "y0": y0,
                        "x1": x1,
                        "y1": new_y1,
                        "width": x1 - x0,
                        "height": new_y1 - y0,
                    }
                    _copy_detector_meta(box, new_box)
                    return new_box

    nonwhite_ratios = []
    for yy in range(band.shape[0]):
        row = band[yy, :]
        nonwhite = float(np.count_nonzero(row < white_threshold)) / float(max(row.size, 1))
        nonwhite_ratios.append(nonwhite)
    smooth = []
    for i, val in enumerate(nonwhite_ratios):
        window = nonwhite_ratios[max(0, i - 1):min(len(nonwhite_ratios), i + 2)]
        smooth.append(sum(window) / float(len(window)))
    nonwhite_ratios = smooth

    gap_threshold = max(0.02, text_ratio_threshold)
    gap_run = 3
    gap_y = None
    # Find the first significant whitespace gap within the bottom band.
    for idx in range(0, len(nonwhite_ratios) - gap_run):
        if all(nonwhite_ratios[j] <= gap_threshold for j in range(idx, idx + gap_run)):
            if any(r >= gap_threshold for r in nonwhite_ratios[idx + gap_run:]):
                # Require some content above the gap to avoid trimming blank tails.
                if max(nonwhite_ratios[:idx + gap_run]) >= gap_threshold:
                    gap_y = idx
                    break
    if gap_y is not None:
        cut_row = gap_y
    else:
        # Blackhat to emphasize dark text on light background.
            k_w = max(25, band.shape[1] // 20)
            k_h = max(3, band.shape[0] // 60)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k_w, k_h))
            blackhat = cv2.morphologyEx(band, cv2.MORPH_BLACKHAT, kernel)
            bh = cv2.normalize(blackhat, None, 0, 255, cv2.NORM_MINMAX)
            _, bw = cv2.threshold(bh, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            proj = np.sum(bw > 0, axis=1)
            width = max(1, band.shape[1])
            ratios = proj / float(width)
            ratios = np.convolve(ratios, np.ones(3) / 3, mode="same")
            thr = max(0.01, 0.5 * np.median(ratios) + 0.25 * np.max(ratios))
            min_run = 2
            run = 0
            caption_start = None
            for idx, ratio in enumerate(ratios):
                if ratio >= thr:
                    run += 1
                    if run >= min_run:
                        if idx - min_run >= 0 and ratios[idx - min_run] < thr:
                            caption_start = idx - min_run + 1
                            break
                else:
                    run = 0
            if caption_start is not None:
                cut_row = caption_start
            else:
                # Detect a caption text run near the bottom (transition from sparse to denser rows).
                min_run = 3
                caption_start = None
                run = 0
                for idx, ratio in enumerate(nonwhite_ratios):
                    if ratio >= text_ratio_threshold:
                        run += 1
                        if run >= min_run:
                            if idx - min_run >= 0 and nonwhite_ratios[idx - min_run] < text_ratio_threshold:
                                caption_start = idx - min_run + 1
                                break
                    else:
                        run = 0
                if caption_start is None:
                    edges = cv2.Canny(band, 50, 150)
                    edge_ratios = []
                    for yy in range(edges.shape[0]):
                        row = edges[yy, :]
                        edge_ratios.append(float(np.count_nonzero(row)) / float(max(row.size, 1)))
                    edge_thr = max(0.04, text_ratio_threshold * 3.0)
                    run = 0
                    for idx, ratio in enumerate(edge_ratios):
                        if ratio >= edge_thr:
                            run += 1
                            if run >= 2:
                                if idx - 2 >= 0 and edge_ratios[idx - 2] < edge_thr:
                                    caption_start = idx - 2 + 1
                                    break
                        else:
                            run = 0
                    if caption_start is None:
                        _, text_bin = cv2.threshold(band, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                        kernel_w = max(30, band.shape[1] // 12)
                        text_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_w, 1))
                        text_lines = cv2.morphologyEx(text_bin, cv2.MORPH_OPEN, text_kernel, iterations=1)
                        contours, _ = cv2.findContours(text_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        if contours:
                            min_y = None
                            for cnt in contours:
                                x, y, w, h = cv2.boundingRect(cnt)
                                if w < band.shape[1] * 0.08:
                                    continue
                                if h > band.shape[0] * 0.2:
                                    continue
                                if min_y is None or y < min_y:
                                    min_y = y
                            if min_y is not None:
                                cut_row = min_y
                            else:
                                if caption_nonwhite > caption_max_nonwhite_ratio:
                                    return box
                                return box
                        else:
                            if caption_nonwhite > caption_max_nonwhite_ratio:
                                return box
                            return box
                    else:
                        cut_row = caption_start
                else:
                    cut_row = caption_start

    new_y1 = y0 + start + cut_row - margin_px
    if new_y1 <= y0:
        return box
    new_box = {
        "x0": x0,
        "y0": y0,
        "x1": x1,
        "y1": new_y1,
        "width": x1 - x0,
        "height": new_y1 - y0,
    }
    _copy_detector_meta(box, new_box)
    return new_box


def _trim_rule_example_bottom_prose_band(
    image_path: str,
    box: Dict[str, int],
    *,
    margin_px: int = 8,
) -> Dict[str, int]:
    role = str(box.get("_critical_graphics_role") or "").casefold()
    if role not in {"rule_example_diagram", "component_reference"}:
        return box
    if str(box.get("_detection_method") or "") == "cv_guided_rule_panel_split":
        return box
    img_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img_bgr is None:
        return box
    img_h, img_w = img_bgr.shape[:2]
    x0 = max(0, int(box.get("x0", 0)))
    y0 = max(0, int(box.get("y0", 0)))
    x1 = min(img_w, int(box.get("x1", img_w)))
    y1 = min(img_h, int(box.get("y1", img_h)))
    if x1 <= x0 or y1 <= y0:
        return box
    roi = img_bgr[y0:y1, x0:x1]
    if roi.size == 0:
        return box
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    dark_text = (gray < 150) & (sat < 90)
    saturated = sat > 100
    h, w = gray.shape[:2]
    if h < 120 or w < 120:
        return box
    row_signal = dark_text.sum(axis=1) / float(max(1, w))
    sat_signal = saturated.sum(axis=1) / float(max(1, w))
    candidates = [
        row
        for row in range(int(h * 0.75), h)
        if 0.005 < row_signal[row] < 0.25 and sat_signal[row] < 0.08
    ]
    if not candidates:
        return box
    groups: List[Tuple[int, int]] = []
    start = last = candidates[0]
    for row in candidates[1:]:
        if row <= last + 3:
            last = row
            continue
        groups.append((start, last))
        start = last = row
    groups.append((start, last))
    prose_groups = [(start, end) for start, end in groups if start >= int(h * 0.88)]
    if not prose_groups:
        return box
    trim_start = min(start for start, _end in prose_groups)
    new_y1 = y0 + max(0, trim_start - margin_px)
    if new_y1 <= y0 or y1 - new_y1 < max(8, int(h * 0.015)):
        return box
    new_box = {
        "x0": x0,
        "y0": y0,
        "x1": x1,
        "y1": new_y1,
        "width": x1 - x0,
        "height": new_y1 - y0,
    }
    _copy_detector_meta(box, new_box)
    new_box["_detection_method"] = box.get("_detection_method", "critical_graphics_manifest")
    new_box["_trimmed_rule_example_bottom_prose"] = True
    return new_box


def _trim_rule_panel_cost_reference_card(
    image_path: str,
    box: Dict[str, int],
    *,
    pad_px: int = 0,
) -> Dict[str, int]:
    """Trim split cost-reference children to the card-like visual object."""
    if str(box.get("_rule_panel_child_kind") or "") != "cost_reference":
        return box
    img_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img_bgr is None:
        return box
    img_h, img_w = img_bgr.shape[:2]
    x0 = max(0, int(box.get("x0", 0)))
    y0 = max(0, int(box.get("y0", 0)))
    x1 = min(img_w, int(box.get("x1", img_w)))
    y1 = min(img_h, int(box.get("y1", img_h)))
    if x1 <= x0 or y1 <= y0:
        return box
    roi = img_bgr[y0:y1, x0:x1]
    if roi.size == 0:
        return box
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    value = hsv[:, :, 2]
    h, w = value.shape[:2]
    if h < 120 or w < 120:
        return box

    # Cost reference visuals are usually card/object crops. Detached prose can
    # be connected by a thin callout line, so prefer the tall dark visual body
    # rather than a saturation union that follows the callout into text.
    dark = (value < 85).astype("uint8") * 255
    dark = cv2.morphologyEx(
        dark,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)),
        iterations=1,
    )
    num_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(dark, connectivity=8)
    components: List[Tuple[int, int, int, int, int]] = []
    min_area = max(600, int(w * h * 0.025))
    for label in range(1, num_labels):
        cx, cy, cw, ch, area = stats[label]
        if area < min_area:
            continue
        if ch < h * 0.55 or cw < w * 0.25:
            continue
        components.append((int(cx), int(cy), int(cx + cw), int(cy + ch), int(area)))
    if not components:
        return box

    component = max(components, key=lambda item: item[4])
    local_x1 = min(w, component[2] + pad_px)
    if local_x1 < int(w * 0.45):
        return box
    trims_right_edge = local_x1 < int(w * 0.94)
    if not trims_right_edge:
        local_x1 = w

    if not trims_right_edge:
        return box
    new_box = dict(box)
    new_box["x1"] = x0 + local_x1
    new_box["width"] = int(new_box["x1"] - new_box["x0"])
    new_box["height"] = int(new_box["y1"] - new_box["y0"])
    new_box["area"] = int(new_box["width"] * new_box["height"])
    new_box["area_ratio"] = round(new_box["area"] / float(max(1, img_w * img_h)), 4)
    new_box["_trimmed_rule_panel_cost_reference"] = True
    return new_box


def _expand_rule_panel_placement_layout_box(
    image_path: str,
    box: Dict[str, int],
    *,
    bottom_pad_ratio: float = 0.06,
) -> Dict[str, int]:
    """Add a small lower safety margin for sparse placement-layout clusters."""
    if str(box.get("_rule_panel_child_kind") or "") != "placement_layout":
        return box
    try:
        with Image.open(image_path) as img:
            img_w, img_h = img.size
    except Exception:
        return box
    x0 = max(0, int(box.get("x0", 0)))
    y0 = max(0, int(box.get("y0", 0)))
    x1 = min(img_w, int(box.get("x1", img_w)))
    y1 = min(img_h, int(box.get("y1", img_h)))
    if x1 <= x0 or y1 <= y0:
        return box
    pad = max(8, int((y1 - y0) * bottom_pad_ratio))
    new_y1 = min(img_h, y1 + pad)
    if new_y1 == y1:
        return box
    new_box = dict(box)
    new_box["x0"] = x0
    new_box["y0"] = y0
    new_box["x1"] = x1
    new_box["y1"] = new_y1
    new_box["width"] = int(x1 - x0)
    new_box["height"] = int(new_y1 - y0)
    new_box["area"] = int(new_box["width"] * new_box["height"])
    new_box["area_ratio"] = round(new_box["area"] / float(max(1, img_w * img_h)), 4)
    new_box["_expanded_rule_panel_placement_layout"] = True
    return new_box


def _looks_like_player_mat_register_target(box: Dict[str, Any]) -> bool:
    if str(box.get("_rule_panel_child_kind") or ""):
        return False
    if str(box.get("_critical_graphics_role") or "").casefold() != "rule_example_diagram":
        return False
    text = " ".join(
        str(box.get(key) or "")
        for key in ("_description", "_nearby_text", "_expected_visual_contents")
    ).casefold()
    return any(
        cue in text
        for cue in (
            "player mat",
            "programming mat",
            "first register",
            "remaining register",
            "energy reserve",
            "discard area",
        )
    )


def _expand_player_mat_register_rule_example_box(
    image_path: str,
    box: Dict[str, int],
    *,
    max_search_ratio: float = 0.4,
    max_detached_gap_ratio: float = 0.12,
    pad_px: int = 16,
) -> Dict[str, int]:
    """Expand player-mat/register examples when the top edge cuts through the mat."""
    if not _looks_like_player_mat_register_target(box):
        return box
    img_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img_bgr is None:
        return box
    img_h, img_w = img_bgr.shape[:2]
    x0 = max(0, int(box.get("x0", 0)))
    y0 = max(0, int(box.get("y0", 0)))
    x1 = min(img_w, int(box.get("x1", img_w)))
    y1 = min(img_h, int(box.get("y1", img_h)))
    if x1 <= x0 or y1 <= y0:
        return box
    h = y1 - y0
    w = x1 - x0
    search_y0 = max(0, y0 - max(140, int(h * max_search_ratio)))
    if search_y0 >= y0:
        return box
    roi = img_bgr[search_y0:y1, x0:x1]
    if roi.size == 0:
        return box
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    # Player mats mix colored card slots, dark card borders, robot icons, and
    # gray board texture. Keep the signal broad, then only accept components
    # whose bottom is very close to the current crop edge.
    visual = (((saturation > 55) & (value > 60)) | (value < 150)).astype("uint8") * 255
    visual = cv2.morphologyEx(
        visual,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)),
        iterations=1,
    )
    visual = cv2.dilate(
        visual,
        cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)),
        iterations=1,
    )
    num_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(visual, connectivity=8)
    current_top = y0 - search_y0
    max_detached_gap = max(36, int(h * max_detached_gap_ratio))
    min_area = max(700, int(w * h * 0.003))
    candidate_tops: List[int] = []
    for label in range(1, num_labels):
        cx, cy, cw, ch, area = stats[label]
        if area < min_area:
            continue
        if cw < max(24, int(w * 0.035)) or ch < 18:
            continue
        if cy >= current_top - 4:
            continue
        comp_sat = saturation[cy:cy + ch, cx:cx + cw]
        comp_val = value[cy:cy + ch, cx:cx + cw]
        sat_ratio = float(np.mean((comp_sat > 55) & (comp_val > 60)))
        dark_ratio = float(np.mean(comp_val < 150))
        text_like_above_figure = (
            ch <= max(42, int(h * 0.085))
            and cw > max(36, ch * 1.2)
            and sat_ratio < 0.04
            and dark_ratio < 0.45
        )
        if text_like_above_figure:
            continue
        gap = current_top - int(cy + ch)
        if gap > max_detached_gap:
            continue
        candidate_tops.append(int(cy))

    if not candidate_tops:
        return box
    new_y0 = max(0, search_y0 + min(candidate_tops) - pad_px)
    if y0 - new_y0 < max(12, int(h * 0.025)):
        return box
    new_box = dict(box)
    new_box["x0"] = x0
    new_box["y0"] = new_y0
    new_box["x1"] = x1
    new_box["y1"] = y1
    new_box["width"] = int(w)
    new_box["height"] = int(y1 - new_y0)
    new_box["area"] = int(new_box["width"] * new_box["height"])
    new_box["area_ratio"] = round(new_box["area"] / float(max(1, img_w * img_h)), 4)
    new_box["_expanded_player_mat_register_top"] = True
    return new_box


def _looks_like_integrated_callout_target(box: Dict[str, Any]) -> bool:
    if str(box.get("_rule_panel_child_kind") or ""):
        return False
    if str(box.get("_detection_method") or "") == "cv_guided_rule_panel_split":
        return False
    if str(box.get("_critical_graphics_role") or "").casefold() != "rule_example_diagram":
        return False
    text = " ".join(
        str(box.get(key) or "")
        for key in ("_description", "_nearby_text", "_expected_visual_contents")
    ).casefold()
    return any(cue in text for cue in ("callout", "numbered", "step", "yellow"))


def _expand_integrated_callout_rule_example_box(
    image_path: str,
    box: Dict[str, int],
    *,
    min_row_ratio: float = 0.015,
    max_search_ratio: float = 0.75,
    pad_px: int = 16,
) -> Dict[str, int]:
    """Expand rule-example crops that cut through integrated callout panels."""
    if not _looks_like_integrated_callout_target(box):
        return box
    img_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img_bgr is None:
        return box
    img_h, img_w = img_bgr.shape[:2]
    x0 = max(0, int(box.get("x0", 0)))
    y0 = max(0, int(box.get("y0", 0)))
    x1 = min(img_w, int(box.get("x1", img_w)))
    y1 = min(img_h, int(box.get("y1", img_h)))
    if x1 <= x0 or y1 <= y0:
        return box
    h = y1 - y0
    search_y1 = min(img_h, y1 + max(160, int(h * max_search_ratio)))
    if search_y1 <= y1:
        return box
    roi = img_bgr[y0:search_y1, x0:x1]
    if roi.size == 0:
        return box
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    colored = ((saturation > 80) & (value > 110)).astype("uint8") * 255
    colored = cv2.morphologyEx(
        colored,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)),
        iterations=1,
    )
    current_bottom = y1 - y0

    num_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(colored, connectivity=8)
    candidate_bottoms: List[int] = []
    max_detached_gap = max(70, int(h * 0.12))
    min_area = max(80, int((x1 - x0) * h * min_row_ratio * 0.45))
    for label in range(1, num_labels):
        cx, cy, cw, ch, area = stats[label]
        if area < min_area:
            continue
        if cw < max(40, int((x1 - x0) * 0.035)) or ch < 12:
            continue
        if cy + ch <= current_bottom + 12:
            continue
        if cy > current_bottom + max_detached_gap:
            continue
        candidate_bottoms.append(int(cy + ch))

    if not candidate_bottoms:
        return box
    last_active = max(candidate_bottoms)
    if last_active <= current_bottom + 12:
        return box
    new_y1 = min(img_h, y0 + last_active + pad_px)
    if new_y1 <= y1:
        return box
    new_box = dict(box)
    new_box["x0"] = x0
    new_box["y0"] = y0
    new_box["x1"] = x1
    new_box["y1"] = new_y1
    new_box["width"] = int(x1 - x0)
    new_box["height"] = int(new_y1 - y0)
    new_box["area"] = int(new_box["width"] * new_box["height"])
    new_box["area_ratio"] = round(new_box["area"] / float(max(1, img_w * img_h)), 4)
    new_box["_expanded_integrated_callouts"] = True
    return new_box


def _is_text_only_rule_panel_split_box(img_bgr: np.ndarray, box: Dict[str, int]) -> bool:
    """Return true for split children that are only prominent prose, not visuals."""
    if img_bgr is None:
        return False
    img_h, img_w = img_bgr.shape[:2]
    x0 = max(0, int(box.get("x0", 0)))
    y0 = max(0, int(box.get("y0", 0)))
    x1 = min(img_w, int(box.get("x1", img_w)))
    y1 = min(img_h, int(box.get("y1", img_h)))
    if x1 <= x0 or y1 <= y0:
        return False
    roi = img_bgr[y0:y1, x0:x1]
    if roi.size == 0:
        return False
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    h, w = value.shape[:2]
    if h < 80 or w < 80:
        return False

    light_ratio = float(np.mean((value > 170) & (saturation < 80)))
    saturated_ratio = float(np.mean((saturation > 100) & (value > 80)))
    dark_ratio = float(np.mean(value < 90))
    if light_ratio < 0.70 or saturated_ratio < 0.02 or dark_ratio > 0.035:
        return False

    non_light = (((value < 170) | (saturation > 90))).astype("uint8") * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    connected = cv2.morphologyEx(non_light, cv2.MORPH_CLOSE, kernel, iterations=1)
    num_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(connected, connectivity=8)
    for label in range(1, num_labels):
        _x, _y, cw, ch, area = stats[label]
        if area > max(900, int(w * h * 0.03)) and cw > w * 0.18 and ch > h * 0.18:
            return False

    row_coverage = (non_light > 0).mean(axis=1)
    active_rows = np.flatnonzero((row_coverage > 0.018) & (row_coverage < 0.65))
    if active_rows.size == 0:
        return False
    groups = 1
    last = int(active_rows[0])
    for row in active_rows[1:]:
        row_int = int(row)
        if row_int > last + 4:
            groups += 1
        last = row_int
    return groups >= 2


def _split_mixed_rule_panel_visual_clusters(
    img_bgr: np.ndarray,
    box: Dict[str, int],
) -> List[Dict[str, int]]:
    """Split an overbroad rule-panel child when prose creates a large empty corner."""
    if img_bgr is None:
        return [box]
    img_h, img_w = img_bgr.shape[:2]
    x0 = max(0, int(box.get("x0", 0)))
    y0 = max(0, int(box.get("y0", 0)))
    x1 = min(img_w, int(box.get("x1", img_w)))
    y1 = min(img_h, int(box.get("y1", img_h)))
    if x1 <= x0 or y1 <= y0:
        return [box]
    roi = img_bgr[y0:y1, x0:x1]
    if roi.size == 0:
        return [box]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    h, w = value.shape[:2]
    if h < 180 or w < 180:
        return [box]

    top_left = roi[: max(1, int(h * 0.45)), : max(1, int(w * 0.45))]
    top_left_hsv = cv2.cvtColor(top_left, cv2.COLOR_BGR2HSV)
    top_left_light_ratio = float(np.mean((top_left_hsv[:, :, 2] > 170) & (top_left_hsv[:, :, 1] < 80)))
    if top_left_light_ratio < 0.78:
        return [box]

    non_light = (((value < 170) | (saturation > 80))).astype("uint8") * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    connected = cv2.morphologyEx(non_light, cv2.MORPH_CLOSE, kernel, iterations=1)
    num_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(connected, connectivity=8)
    components: List[Tuple[int, int, int, int, int]] = []
    min_area = max(900, int(w * h * 0.012))
    for label in range(1, num_labels):
        cx, cy, cw, ch, area = stats[label]
        if area < min_area:
            continue
        if cw < max(35, int(w * 0.05)) or ch < max(35, int(h * 0.05)):
            continue
        components.append((int(cx), int(cy), int(cx + cw), int(cy + ch), int(area)))
    if len(components) < 3:
        return [box]

    top_components = [c for c in components if ((c[1] + c[3]) / 2.0) < h * 0.55]
    bottom_components = [c for c in components if ((c[1] + c[3]) / 2.0) >= h * 0.45]
    if not top_components or not bottom_components:
        return [box]

    def make_group(group: List[Tuple[int, int, int, int, int]]) -> Dict[str, int]:
        pad = max(8, int(min(w, h) * 0.015))
        gx0 = max(0, min(c[0] for c in group) - pad)
        gy0 = max(0, min(c[1] for c in group) - pad)
        gx1 = min(w, max(c[2] for c in group) + pad)
        gy1 = min(h, max(c[3] for c in group) + pad)
        new_box = {
            "x0": x0 + gx0,
            "y0": y0 + gy0,
            "x1": x0 + gx1,
            "y1": y0 + gy1,
        }
        new_box["width"] = int(new_box["x1"] - new_box["x0"])
        new_box["height"] = int(new_box["y1"] - new_box["y0"])
        new_box["area"] = int(new_box["width"] * new_box["height"])
        new_box["area_ratio"] = round(new_box["area"] / float(max(1, img_w * img_h)), 4)
        return new_box

    refined = [make_group(top_components), make_group(bottom_components)]
    refined = [candidate for candidate in refined if candidate["width"] > 0 and candidate["height"] > 0]
    if len(refined) < 2:
        return [box]
    original_area = max(1, (x1 - x0) * (y1 - y0))
    refined_area = sum(candidate["width"] * candidate["height"] for candidate in refined)
    if refined_area >= original_area * 0.92:
        return [box]
    return _sort_boxes_reading_order(refined)


def _rule_panel_sentences(text: str) -> List[str]:
    parts = [
        _normalize_ws(part)
        for part in re.split(r"(?:;|\n|(?<=[.!?])\s+)", str(text or ""))
        if _normalize_ws(part)
    ]
    return parts


def _select_rule_panel_context(original_box: Dict[str, Any], keywords: Set[str]) -> str:
    text = str(original_box.get("_nearby_text") or "")
    sentences = _rule_panel_sentences(text)
    selected = [
        sentence
        for sentence in sentences
        if any(keyword in sentence.casefold() for keyword in keywords)
    ]
    if selected:
        return " ".join(selected)
    return _normalize_ws(text)


def _merge_rule_panel_box_group(
    img_bgr: np.ndarray,
    boxes: List[Dict[str, int]],
) -> Dict[str, int]:
    img_h, img_w = img_bgr.shape[:2]
    x0 = max(0, min(int(box["x0"]) for box in boxes))
    y0 = max(0, min(int(box["y0"]) for box in boxes))
    x1 = min(img_w, max(int(box["x1"]) for box in boxes))
    y1 = min(img_h, max(int(box["y1"]) for box in boxes))
    merged = {
        "x0": x0,
        "y0": y0,
        "x1": x1,
        "y1": y1,
        "width": x1 - x0,
        "height": y1 - y0,
    }
    merged["area"] = int(merged["width"] * merged["height"])
    merged["area_ratio"] = round(merged["area"] / float(max(1, img_w * img_h)), 4)
    return merged


def _should_group_rule_panel_placement_layout(box: Dict[str, Any]) -> bool:
    text = " ".join(
        str(box.get(key) or "")
        for key in ("_nearby_text", "_description", "_expected_visual_contents")
    ).casefold()
    return (
        any(keyword in text for keyword in ("place", "placement", "installed", "slot", "player mat"))
        and any(keyword in text for keyword in ("temporary", "permanent", "upgrade", "card"))
    )


def _group_rule_panel_placement_layout(
    original_box: Dict[str, Any],
    split_boxes: List[Dict[str, int]],
    img_bgr: np.ndarray,
) -> List[Dict[str, int]]:
    """Keep a cost/example child separate while grouping placement-layout children."""
    if len(split_boxes) < 3 or not _should_group_rule_panel_placement_layout(original_box):
        return split_boxes

    ox0 = int(original_box.get("x0", 0))
    oy0 = int(original_box.get("y0", 0))
    ow = max(1, int(original_box.get("width") or (int(original_box.get("x1", ox0 + 1)) - ox0)))
    oh = max(1, int(original_box.get("height") or (int(original_box.get("y1", oy0 + 1)) - oy0)))

    cost_candidates: List[Dict[str, int]] = []
    for candidate in split_boxes:
        cx = ((candidate["x0"] + candidate["x1"]) / 2.0 - ox0) / float(ow)
        cy = ((candidate["y0"] + candidate["y1"]) / 2.0 - oy0) / float(oh)
        if cx < 0.42 and cy < 0.52:
            cost_candidates.append(candidate)
    if not cost_candidates:
        return split_boxes

    cost_box = min(
        cost_candidates,
        key=lambda candidate: (
            candidate.get("area", candidate["width"] * candidate["height"]),
            candidate["y0"],
            candidate["x0"],
        ),
    )
    placement_boxes = [candidate for candidate in split_boxes if candidate is not cost_box]
    if len(placement_boxes) < 2:
        return split_boxes

    placement = _merge_rule_panel_box_group(img_bgr, placement_boxes)
    cost_box = dict(cost_box)
    placement["_rule_panel_child_kind"] = "placement_layout"
    cost_box["_rule_panel_child_kind"] = "cost_reference"
    return _sort_boxes_reading_order([cost_box, placement])


def _apply_rule_panel_child_metadata(
    new_box: Dict[str, Any],
    original_box: Dict[str, Any],
) -> None:
    child_kind = str(new_box.get("_rule_panel_child_kind") or "")
    if child_kind == "cost_reference":
        new_box["_nearby_text"] = _select_rule_panel_context(
            original_box,
            {"cost", "number", "pay", "energy", "top left"},
        )
        new_box["_description"] = "Card cost reference visual"
    elif child_kind == "placement_layout":
        new_box["_nearby_text"] = _select_rule_panel_context(
            original_box,
            {"place", "placement", "slot", "mat", "permanent", "temporary", "installed"},
        )
        new_box["_description"] = "Card placement layout visual"


def _extract_images_from_html(html: str) -> List[Dict[str, Any]]:
    """Extract image metadata from HTML img tags (fallback for older OCR output)."""
    images = []
    pattern_with_count = r'<img\s+alt="([^"]*)"\s+data-count="(\d+)">'
    pattern_simple = r'<img\s+alt="([^"]*)"(?:\s*/)?>'

    found_positions = set()
    for match in re.finditer(pattern_with_count, html):
        alt = match.group(1)
        count = int(match.group(2))
        images.append({"alt": alt, "count": count})
        found_positions.add(match.start())

    for match in re.finditer(pattern_simple, html):
        if match.start() not in found_positions:
            full_match = html[match.start():match.start()+150]
            if 'data-count=' not in full_match:
                alt = match.group(1)
                images.append({"alt": alt, "count": 1})

    return images


def _target_description(target: Dict[str, Any]) -> str:
    parts = [
        str(target.get("description") or "").strip(),
        str(target.get("nearby_text") or "").strip(),
        str(target.get("role") or "").replace("_", " ").strip(),
    ]
    return " — ".join(part for part in parts if part)


def _load_critical_graphics_targets(path: Optional[str]) -> Dict[int, List[Dict[str, Any]]]:
    """Load visual-planner targets by logical page.

    Only non-decorative targets are crop intent. Decorative notes stay in the
    manifest/report and should not create final manual assets.
    """
    if not path:
        return {}
    manifest_path = Path(path)
    if not manifest_path.exists():
        raise FileNotFoundError(f"critical graphics manifest not found: {manifest_path}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    page_targets: Dict[int, List[Dict[str, Any]]] = {}
    for page in data.get("pages", []):
        if not isinstance(page, dict):
            continue
        page_number = page.get("page_number")
        if not isinstance(page_number, int):
            continue
        for target in page.get("targets", []):
            if not isinstance(target, dict):
                continue
            importance = str(target.get("importance") or "").strip().lower()
            if importance == "decorative":
                continue
            page_targets.setdefault(page_number, []).append(target)
    return page_targets


def _box_from_critical_target(
    target: Dict[str, Any],
    *,
    image_width: Optional[int] = None,
    image_height: Optional[int] = None,
    padding_percent: float = 0.0,
) -> Optional[Dict[str, int]]:
    bbox = target.get("bbox_pixels")
    if not isinstance(bbox, dict):
        return None
    try:
        x0 = int(round(float(bbox["x0"])))
        y0 = int(round(float(bbox["y0"])))
        x1 = int(round(float(bbox["x1"])))
        y1 = int(round(float(bbox["y1"])))
    except (KeyError, TypeError, ValueError):
        return None
    if x1 <= x0 or y1 <= y0:
        return None
    if image_width and image_height and padding_percent > 0:
        pad_x = int(round((x1 - x0) * padding_percent))
        pad_y = int(round((y1 - y0) * padding_percent))
        x0 = max(0, x0 - pad_x)
        y0 = max(0, y0 - pad_y)
        x1 = min(int(image_width), x1 + pad_x)
        y1 = min(int(image_height), y1 + pad_y)
    box: Dict[str, int] = {
        "x0": x0,
        "y0": y0,
        "x1": x1,
        "y1": y1,
        "width": x1 - x0,
        "height": y1 - y0,
        "_from_vlm": True,
        "_detection_method": "critical_graphics_manifest",
        "_description": _target_description(target),
        "_nearby_text": target.get("nearby_text"),
        "_expected_visual_contents": target.get("expected_visual_contents"),
        "_critical_graphics_target_id": target.get("target_id"),
        "_critical_graphics_importance": target.get("importance"),
        "_critical_graphics_role": target.get("role"),
        "_critical_graphics_reason": target.get("reason"),
    }
    return box


def _critical_target_padding_percent(target: Dict[str, Any]) -> float:
    """Return conservative role-specific padding for visual-planner crop intent."""
    role = str(target.get("role") or "").casefold()
    if role == "component_reference":
        # Component reference boxes from VLMs are often semantically correct but
        # visually tight around the object. A small margin preserves edge board
        # squares/icons while downstream prose trimming still removes detached
        # text bands.
        return 0.06
    return 0.0


def _align_descriptions_to_detected_boxes(descriptions: List[str], boxes: List[Dict[str, int]]) -> List[str]:
    if len(boxes) >= len(descriptions):
        return descriptions
    skippable_pattern = re.compile(r"\b(callout|note|reminder|summary panel)\b", re.IGNORECASE)
    without_text_callouts = [desc for desc in descriptions if not skippable_pattern.search(desc or "")]
    if len(without_text_callouts) == len(boxes):
        return without_text_callouts
    return descriptions


def _extract_numbers(name: str) -> List[int]:
    return [int(m) for m in re.findall(r"\d+", name)]


def _sort_key(path: Path) -> Tuple[int, List[int], str]:
    numbers = _extract_numbers(path.name)
    has_numbers = 0 if numbers else 1
    return (has_numbers, numbers, path.name.lower())


def _iter_images(input_dir: Path) -> List[Path]:
    images = [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]
    return sorted(images, key=_sort_key)


def _utc() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _log(message: str):
    """Simple logging function."""
    print(message, flush=True)


def _prune_stale_crop_images(
    images_dir: str,
    *,
    page_numbers: Optional[Set[int]] = None,
    keep_filenames: Optional[Set[str]] = None,
) -> int:
    """Remove stale crop image files after targeted or full reruns."""
    images_path = Path(images_dir)
    if not images_path.exists():
        return 0

    removed = 0
    if page_numbers is not None:
        for page_num in page_numbers:
            for old_file in images_path.glob(f"page-{page_num:03d}-*"):
                if not old_file.is_file():
                    continue
                old_file.unlink()
                removed += 1
        return removed

    keep = keep_filenames or set()
    for old_file in images_path.iterdir():
        if not old_file.is_file():
            continue
        if old_file.name in keep:
            continue
        old_file.unlink()
        removed += 1
    return removed


def _is_bw_image(img: Image.Image) -> bool:
    """Check if image is black & white (grayscale or near-grayscale).
    
    Handles beige/cream paper backgrounds by checking both color variance
    and saturation levels. Desaturated images (low saturation) are treated
    as B&W even if they have slight color variance from aged paper.
    """
    if img.mode in ('L', '1'):
        return True

    if img.mode == 'RGB' or img.mode == 'RGBA':
        img_array = np.array(img)
        if img.mode == 'RGBA':
            rgb = img_array[:, :, :3]
        else:
            rgb = img_array

        # Method 1: Check color variance (strict)
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        color_variance = np.std([np.mean(r), np.mean(g), np.mean(b)])
        if color_variance < 5:
            return True
        
        # Method 2: Check saturation (handles beige/cream backgrounds)
        # Convert to normalized RGB for saturation calculation
        rgb_norm = rgb.astype(np.float32) / 255.0
        max_val = np.max(rgb_norm, axis=2)
        min_val = np.min(rgb_norm, axis=2)
        delta = max_val - min_val
        
        # Calculate mean saturation (0.0 = grayscale, 1.0 = fully saturated)
        mean_saturation = np.mean(delta)
        
        # If saturation is very low (< 0.25), treat as B&W even with color variance
        # This handles beige/cream paper that has slight R/G/B differences but is effectively grayscale
        if mean_saturation < 0.25:
            return True
        
        # Fallback: if color variance is moderate (< 20) and saturation is low (< 0.30)
        if color_variance < 20 and mean_saturation < 0.30:
            return True

    return False


def _make_transparent(img: Image.Image, threshold: int = 230) -> Image.Image:
    """Convert white background to transparent for B&W artwork.
    
    First converts the image to proper grayscale to remove any beige/cream
    tint, then generates alpha channel from the grayscale values.
    """
    # Convert to proper grayscale first (removes beige/cream tint)
    # This ensures consistent black/white values regardless of paper color
    if img.mode != 'L':
        gray = img.convert('L')
    else:
        gray = img
    
    # Use the grayscale image for both RGB and alpha calculations
    # This ensures the final image is truly black & white (not beige-tinted)
    gray_array = np.array(gray)
    
    # Convert grayscale to RGB (single channel repeated for R, G, B)
    rgb_array = np.stack([gray_array, gray_array, gray_array], axis=2)

    # Invert grayscale to get alpha (dark = opaque, white/light = transparent)
    alpha_array = 255 - gray_array

    # Force near-white pixels fully transparent
    alpha_array[gray_array > threshold] = 0

    rgba_array = np.dstack((rgb_array, alpha_array))
    return Image.fromarray(rgba_array.astype('uint8'), 'RGBA')


def detect_contours_cv(
    image_path: Path,
    expected_count: int = 1,
    blur: int = 7,
    text_kernel: int = 3,
    text_iterations: int = 1,
    min_area_ratio: float = 0.01,
    max_area_ratio: float = 0.99,
    min_width: int = 50,
    min_height: int = 50,
    padding_percent: float = 0.05
) -> List[Dict[str, int]]:
    """Detect illustration bounding boxes using CV contour detection.

    Args:
        image_path: Path to page image
        expected_count: Number of illustrations expected on this page
        blur: Gaussian blur kernel size
        min_area_ratio: Minimum box area as fraction of page area
        max_area_ratio: Maximum box area as fraction of page area
        min_width: Minimum box width in pixels
        min_height: Minimum box height in pixels
        padding_percent: Percentage padding to add around detected boxes (default 0.15 = 15%)

    Returns:
        List of bounding boxes {x0, y0, x1, y1, width, height}
    """
    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        return []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_k = blur if blur % 2 == 1 else blur + 1
    gray = cv2.GaussianBlur(gray, (blur_k, blur_k), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Morph open to drop specks and suppress small text.
    kernel_size = text_kernel if text_kernel % 2 == 1 else text_kernel + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=text_iterations)

    contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    h, w = gray.shape[:2]
    img_area = w * h
    candidates = []

    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch
        ratio = area / img_area

        # Filter by area ratio
        if ratio < min_area_ratio or ratio > max_area_ratio:
            continue

        # Filter by minimum pixel dimensions
        if cw < min_width or ch < min_height:
            continue

        # Looser aspect ratio for guided detection (we know it's an image)
        aspect = cw / max(ch, 1)
        if aspect > 5.0 or aspect < 0.2:
            continue

        candidates.append({
            "x0": int(x),
            "y0": int(y),
            "x1": int(x + cw),
            "y1": int(y + ch),
            "width": int(cw),
            "height": int(ch),
            "area": area,
            "area_ratio": round(ratio, 4)
        })

    # Sort by area (largest first)
    candidates.sort(key=lambda b: b["area"], reverse=True)

    # Take top N non-overlapping candidates
    selected = []
    for candidate in candidates:
        if len(selected) >= expected_count:
            break

        # Check for overlap with already selected boxes
        overlaps = False
        for sel in selected:
            if _boxes_overlap(candidate, sel):
                overlaps = True
                break

        if not overlaps:
            selected.append(candidate)

    # Add padding to selected boxes to capture lighter elements around main subject
    padded = []
    for box in selected:
        # Calculate padding in pixels
        pad_w = int(box["width"] * padding_percent)
        pad_h = int(box["height"] * padding_percent)

        # Expand box with padding, clamped to image boundaries
        x0 = max(0, box["x0"] - pad_w)
        y0 = max(0, box["y0"] - pad_h)
        x1 = min(w, box["x1"] + pad_w)
        y1 = min(h, box["y1"] + pad_h)

        padded.append({
            "x0": int(x0),
            "y0": int(y0),
            "x1": int(x1),
            "y1": int(y1),
            "width": int(x1 - x0),
            "height": int(y1 - y0),
            "area": int((x1 - x0) * (y1 - y0)),
            "area_ratio": round(((x1 - x0) * (y1 - y0)) / img_area, 4)
        })

    return padded


def _boxes_overlap(box1: Dict, box2: Dict) -> bool:
    """Check if two boxes overlap."""
    if (box1["x1"] <= box2["x0"] or box1["x0"] >= box2["x1"] or
        box1["y1"] <= box2["y0"] or box1["y0"] >= box2["y1"]):
        return False
    return True


def _box_iou(box1: Dict[str, int], box2: Dict[str, int]) -> float:
    x0 = max(box1["x0"], box2["x0"])
    y0 = max(box1["y0"], box2["y0"])
    x1 = min(box1["x1"], box2["x1"])
    y1 = min(box1["y1"], box2["y1"])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    inter = (x1 - x0) * (y1 - y0)
    area1 = (box1["x1"] - box1["x0"]) * (box1["y1"] - box1["y0"])
    area2 = (box2["x1"] - box2["x0"]) * (box2["y1"] - box2["y0"])
    union = area1 + area2 - inter
    if union <= 0:
        return 0.0
    return inter / union


def _dedupe_boxes(
    boxes: List[Dict[str, int]],
    iou_threshold: float = 0.95,
    center_threshold: int = 10,
    size_ratio_threshold: float = 0.02,
) -> List[Dict[str, int]]:
    if not boxes:
        return boxes
    kept: List[Dict[str, int]] = []
    for box in boxes:
        duplicate = False
        cx = (box["x0"] + box["x1"]) / 2.0
        cy = (box["y0"] + box["y1"]) / 2.0
        for prev in kept:
            if _box_iou(box, prev) >= iou_threshold:
                duplicate = True
                break
            pcx = (prev["x0"] + prev["x1"]) / 2.0
            pcy = (prev["y0"] + prev["y1"]) / 2.0
            if abs(cx - pcx) <= center_threshold and abs(cy - pcy) <= center_threshold:
                w = max(1, box["x1"] - box["x0"])
                h = max(1, box["y1"] - box["y0"])
                pw = max(1, prev["x1"] - prev["x0"])
                ph = max(1, prev["y1"] - prev["y0"])
                if abs(w - pw) / max(w, pw) <= size_ratio_threshold and abs(h - ph) / max(h, ph) <= size_ratio_threshold:
                    duplicate = True
                    break
        if not duplicate:
            kept.append(box)
    return kept


def _sort_boxes_reading_order(boxes: List[Dict[str, int]]) -> List[Dict[str, int]]:
    """Sort boxes by visual rows, then x-position within each row."""
    if not boxes:
        return boxes
    heights = sorted(max(1, int(b.get("height") or (b["y1"] - b["y0"]))) for b in boxes)
    median_height = heights[len(heights) // 2]
    row_tolerance = max(20, int(median_height * 0.35))
    rows: List[List[Dict[str, int]]] = []
    for box in sorted(boxes, key=lambda b: ((b["y0"] + b["y1"]) / 2.0, b["x0"])):
        center_y = (box["y0"] + box["y1"]) / 2.0
        placed = False
        for row in rows:
            row_center = sum((b["y0"] + b["y1"]) / 2.0 for b in row) / float(len(row))
            if abs(center_y - row_center) <= row_tolerance:
                row.append(box)
                placed = True
                break
        if not placed:
            rows.append([box])
    rows.sort(key=lambda row: min(b["y0"] for b in row))
    sorted_boxes: List[Dict[str, int]] = []
    for row in rows:
        sorted_boxes.extend(sorted(row, key=lambda b: b["x0"]))
    return sorted_boxes


def _prune_contained_boxes(
    boxes: List[Dict[str, int]],
    contain_ratio: float = 0.9,
    min_area_ratio: float = 1.5,
) -> List[Dict[str, int]]:
    if len(boxes) < 2:
        return boxes
    areas = []
    for b in boxes:
        w = max(0, b["x1"] - b["x0"])
        h = max(0, b["y1"] - b["y0"])
        areas.append(float(w * h))
    keep = [True] * len(boxes)
    for i, a in enumerate(boxes):
        if not keep[i]:
            continue
        ax0, ay0, ax1, ay1 = a["x0"], a["y0"], a["x1"], a["y1"]
        for j, b in enumerate(boxes):
            if i == j or not keep[j]:
                continue
            bx0, by0, bx1, by1 = b["x0"], b["y0"], b["x1"], b["y1"]
            ix0 = max(ax0, bx0)
            iy0 = max(ay0, by0)
            ix1 = min(ax1, bx1)
            iy1 = min(ay1, by1)
            if ix1 <= ix0 or iy1 <= iy0:
                continue
            inter = float((ix1 - ix0) * (iy1 - iy0))
            if areas[j] <= 0:
                continue
            if inter / areas[j] >= contain_ratio:
                if areas[i] >= areas[j] * min_area_ratio:
                    keep[i] = False
                    break
    return [b for k, b in zip(keep, boxes) if k]


def _split_box_by_gaps(
    img_gray: np.ndarray,
    box: Dict[str, int],
    white_threshold: int,
    gap_ratio_threshold: float,
    min_gap_px: int,
    min_segment_height: int,
    min_segment_nonwhite_ratio: float,
) -> List[Dict[str, int]]:
    x0, y0, x1, y1 = box["x0"], box["y0"], box["x1"], box["y1"]
    if y1 <= y0 or x1 <= x0:
        return [box]
    roi = img_gray[y0:y1, x0:x1]
    if roi.size == 0:
        return [box]
    h, w = roi.shape[:2]
    if h < min_segment_height * 2:
        return [box]
    nonwhite = (roi < white_threshold).astype("uint8")
    row_ratios = nonwhite.sum(axis=1) / float(max(1, w))
    gaps = row_ratios <= gap_ratio_threshold
    gap_runs = []
    run_start = None
    for idx, is_gap in enumerate(gaps):
        if is_gap and run_start is None:
            run_start = idx
        elif not is_gap and run_start is not None:
            if idx - run_start >= min_gap_px:
                gap_runs.append((run_start, idx - 1))
            run_start = None
    if run_start is not None and h - run_start >= min_gap_px:
        gap_runs.append((run_start, h - 1))
    if not gap_runs:
        return [box]

    split_rows = []
    for g0, g1 in gap_runs:
        split_rows.append((g0 + g1) // 2)
    split_rows = sorted(set([r for r in split_rows if 0 < r < h - 1]))
    if not split_rows:
        return [box]

    segments = []
    prev = 0
    for cut in split_rows + [h]:
        seg_h = cut - prev
        if seg_h >= min_segment_height:
            seg = {
                "x0": x0,
                "y0": y0 + prev,
                "x1": x1,
                "y1": y0 + cut,
                "width": x1 - x0,
                "height": seg_h,
            }
            _copy_detector_meta(box, seg)
            seg_roi = img_gray[seg["y0"]:seg["y1"], seg["x0"]:seg["x1"]]
            if seg_roi.size > 0:
                ratio = float(np.count_nonzero(seg_roi < white_threshold)) / float(seg_roi.size)
                if ratio >= min_segment_nonwhite_ratio:
                    segments.append(seg)
        prev = cut

    if not segments:
        return [box]
    return segments


def _split_boxes_to_count(
    img_gray: np.ndarray,
    boxes: List[Dict[str, int]],
    expected_count: int,
    white_threshold: int,
    gap_ratio_threshold: float,
    min_gap_px: int,
    min_segment_height: int,
    min_segment_nonwhite_ratio: float,
) -> List[Dict[str, int]]:
    if expected_count <= len(boxes) or not boxes:
        return boxes
    boxes_sorted = sorted(
        boxes,
        key=lambda b: (b.get("height", 0) * b.get("width", 0)),
        reverse=True,
    )
    out: List[Dict[str, int]] = []
    for box in boxes_sorted:
        if len(out) >= expected_count:
            out.append(box)
            continue
        splits = _split_box_by_gaps(
            img_gray,
            box,
            white_threshold=white_threshold,
            gap_ratio_threshold=gap_ratio_threshold,
            min_gap_px=min_gap_px,
            min_segment_height=min_segment_height,
            min_segment_nonwhite_ratio=min_segment_nonwhite_ratio,
        )
        if len(splits) > 1:
            out.extend(splits)
        else:
            out.append(box)
    if len(out) > expected_count:
        out.sort(key=lambda b: (b.get("height", 0) * b.get("width", 0)))
        out = out[-expected_count:]
    return _sort_boxes_reading_order(out)


def _detect_saturated_regions_for_dense_split(
    img_bgr: np.ndarray,
    region: Dict[str, int],
    *,
    expected_count: int,
    saturation_threshold: int,
    min_component_area_ratio: float,
    max_component_area_ratio: float,
    padding_percent: float,
) -> List[Dict[str, int]]:
    """Find repeated colorful visual blocks inside an overbroad crop box.

    Dense reference pages often have a textured or decorative background that
    makes the first-pass detector return the whole page. This pass uses a
    generic saturation mask to find repeated maps, card faces, icons, or callout
    panels without relying on document titles or page-specific labels.
    """
    if img_bgr is None or expected_count <= 1:
        return []
    img_h, img_w = img_bgr.shape[:2]
    x0 = max(0, int(region.get("x0", 0)))
    y0 = max(0, int(region.get("y0", 0)))
    x1 = min(img_w, int(region.get("x1", img_w)))
    y1 = min(img_h, int(region.get("y1", img_h)))
    if x1 <= x0 or y1 <= y0:
        return []

    roi = img_bgr[y0:y1, x0:x1]
    if roi.size == 0:
        return []
    roi_h, roi_w = roi.shape[:2]
    page_area = float(max(1, img_w * img_h))
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    mask = ((saturation >= saturation_threshold) & (value >= 45)).astype("uint8") * 255

    kernel_size = max(5, int(min(roi_w, roi_h) * 0.01))
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates: List[Dict[str, int]] = []
    for cnt in contours:
        cx, cy, cw, ch = cv2.boundingRect(cnt)
        if cw <= 0 or ch <= 0:
            continue
        abs_x0 = x0 + cx
        abs_y0 = y0 + cy
        abs_x1 = abs_x0 + cw
        abs_y1 = abs_y0 + ch
        area_ratio = (cw * ch) / page_area
        if area_ratio < min_component_area_ratio or area_ratio > max_component_area_ratio:
            continue
        if cw < max(45, int(img_w * 0.025)) or ch < max(45, int(img_h * 0.025)):
            continue
        aspect = cw / float(max(1, ch))
        if aspect < 0.15 or aspect > 4.5:
            continue
        if ch > 0.85 * img_h or cw > 0.85 * img_w:
            continue
        center_x = (abs_x0 + abs_x1) / 2.0 / float(max(1, img_w))
        center_y = (abs_y0 + abs_y1) / 2.0 / float(max(1, img_h))
        if area_ratio < 0.006 and aspect > 3.0 and ch < 0.05 * img_h:
            continue
        if area_ratio < 0.006 and center_y > 0.88 and center_x > 0.65:
            continue
        if area_ratio < 0.008 and aspect < 0.4 and center_y > 0.8 and center_x > 0.7:
            continue

        pad = int(max(cw, ch) * padding_percent)
        box = {
            "x0": max(0, abs_x0 - pad),
            "y0": max(0, abs_y0 - pad),
            "x1": min(img_w, abs_x1 + pad),
            "y1": min(img_h, abs_y1 + pad),
        }
        box["width"] = int(box["x1"] - box["x0"])
        box["height"] = int(box["y1"] - box["y0"])
        if box["width"] <= 0 or box["height"] <= 0:
            continue
        box["area"] = int(box["width"] * box["height"])
        box["area_ratio"] = round(box["area"] / page_area, 4)
        box["_detection_method"] = "cv_guided_dense_split"
        candidates.append(box)

    candidates = _merge_stacked_dense_components(candidates, img_w=img_w, img_h=img_h)
    candidates.sort(key=lambda b: b.get("area", 0), reverse=True)
    selected: List[Dict[str, int]] = []
    for candidate in candidates:
        if len(selected) >= expected_count:
            break
        if any(_boxes_overlap(candidate, existing) for existing in selected):
            continue
        selected.append(candidate)
    selected = _expand_dense_boxes_with_upper_panels(img_bgr, selected)
    return _sort_boxes_reading_order(selected)


def _dense_box_x_overlap_ratio(a: Dict[str, int], b: Dict[str, int]) -> float:
    overlap = max(0, min(a["x1"], b["x1"]) - max(a["x0"], b["x0"]))
    return overlap / float(max(1, min(a["width"], b["width"])))


def _merge_dense_boxes(a: Dict[str, int], b: Dict[str, int], *, img_w: int, img_h: int) -> Dict[str, int]:
    merged = {
        "x0": max(0, min(a["x0"], b["x0"])),
        "y0": max(0, min(a["y0"], b["y0"])),
        "x1": min(img_w, max(a["x1"], b["x1"])),
        "y1": min(img_h, max(a["y1"], b["y1"])),
    }
    merged["width"] = int(merged["x1"] - merged["x0"])
    merged["height"] = int(merged["y1"] - merged["y0"])
    merged["area"] = int(merged["width"] * merged["height"])
    merged["area_ratio"] = round(merged["area"] / float(max(1, img_w * img_h)), 4)
    merged["_detection_method"] = "cv_guided_dense_split"
    merged["_dense_component_merge_count"] = int(a.get("_dense_component_merge_count") or 1) + int(
        b.get("_dense_component_merge_count") or 1
    )
    return merged


def _merge_stacked_dense_components(
    boxes: List[Dict[str, int]],
    *,
    img_w: int,
    img_h: int,
) -> List[Dict[str, int]]:
    """Merge close, same-column saturated components into one card/panel crop."""
    if len(boxes) < 2:
        return boxes
    sorted_boxes = sorted(boxes, key=lambda b: (b["x0"], b["y0"], b["x1"]))
    used: set[int] = set()
    merged: List[Dict[str, int]] = []
    for idx, box in enumerate(sorted_boxes):
        if idx in used:
            continue
        best_idx = None
        best_gap = None
        for jdx, other in enumerate(sorted_boxes):
            if jdx == idx or jdx in used:
                continue
            if other["y0"] < box["y1"]:
                continue
            gap = other["y0"] - box["y1"]
            max_gap = max(14, int(min(box["height"], other["height"]) * 0.35))
            if gap > max_gap:
                continue
            x_overlap = _dense_box_x_overlap_ratio(box, other)
            if x_overlap < 0.7:
                continue
            width_ratio = min(box["width"], other["width"]) / float(max(1, max(box["width"], other["width"])))
            if width_ratio < 0.65:
                continue
            combined_height = other["y1"] - box["y0"]
            if combined_height > 0.45 * img_h:
                continue
            if best_gap is None or gap < best_gap:
                best_gap = gap
                best_idx = jdx
        if best_idx is None:
            merged.append(box)
            used.add(idx)
            continue
        merged.append(_merge_dense_boxes(box, sorted_boxes[best_idx], img_w=img_w, img_h=img_h))
        used.add(idx)
        used.add(best_idx)
    return merged


def _expand_dense_boxes_with_upper_panels(
    img_bgr: np.ndarray,
    boxes: List[Dict[str, int]],
) -> List[Dict[str, int]]:
    """Expand dense card/reference crops upward to include nearby header panels."""
    if img_bgr is None or not boxes:
        return boxes
    img_h, img_w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    out: List[Dict[str, int]] = []
    for box in boxes:
        x0 = max(0, int(box["x0"]))
        x1 = min(img_w, int(box["x1"]))
        y0 = max(0, int(box["y0"]))
        height = max(1, int(box.get("height") or (box["y1"] - box["y0"])))
        search_top = max(0, y0 - max(80, int(height * 0.7)))
        if x1 <= x0 or y0 <= search_top:
            out.append(box)
            continue
        roi = gray[search_top:y0, x0:x1]
        if roi.size == 0:
            out.append(box)
            continue
        dark_mask = roi < 150
        row_coverage = dark_mask.mean(axis=1)
        active_rows = np.flatnonzero(row_coverage >= 0.18)
        if active_rows.size == 0:
            out.append(box)
            continue
        segments: List[tuple[int, int]] = []
        start = int(active_rows[0])
        last = start
        for row in active_rows[1:]:
            row_int = int(row)
            if row_int <= last + 2:
                last = row_int
                continue
            segments.append((start, last))
            start = row_int
            last = row_int
        segments.append((start, last))

        chosen: tuple[int, int] | None = None
        for seg_start, seg_end in reversed(segments):
            gap = (y0 - 1) - (search_top + seg_end)
            seg_height = seg_end - seg_start + 1
            if gap <= max(22, int(height * 0.16)) and seg_height >= max(12, int(height * 0.08)):
                chosen = (seg_start, seg_end)
                break
        if chosen is None:
            out.append(box)
            continue

        new_box = dict(box)
        new_y0 = max(0, search_top + chosen[0] - int(height * 0.04))
        if new_y0 < y0:
            new_box["y0"] = new_y0
            new_box["height"] = int(new_box["y1"] - new_box["y0"])
            new_box["area"] = int(new_box["width"] * new_box["height"])
            new_box["area_ratio"] = round(new_box["area"] / float(max(1, img_w * img_h)), 4)
            new_box["_dense_upper_panel_expanded"] = True
        out.append(new_box)
    return out


def _split_dense_reference_boxes(
    image_path: str,
    boxes: List[Dict[str, int]],
    *,
    expected_count: int,
    min_expected_count: int,
    min_overbroad_area_ratio: float,
    saturation_threshold: int,
    min_component_area_ratio: float,
    max_component_area_ratio: float,
    padding_percent: float,
) -> List[Dict[str, int]]:
    if expected_count < min_expected_count or len(boxes) >= expected_count or not boxes:
        return boxes
    img_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img_bgr is None:
        return boxes
    img_h, img_w = img_bgr.shape[:2]
    page_area = float(max(1, img_w * img_h))
    overbroad: List[Dict[str, int]] = []
    retained: List[Dict[str, int]] = []
    for box in boxes:
        area = (box["x1"] - box["x0"]) * (box["y1"] - box["y0"])
        area_ratio = float(box.get("area_ratio") or (area / page_area))
        if area_ratio >= min_overbroad_area_ratio:
            overbroad.append(box)
        else:
            retained.append(box)
    if not overbroad:
        return boxes

    dense_candidates: List[Dict[str, int]] = []
    remaining_needed = max(0, expected_count - len(retained))
    for region in overbroad:
        dense_candidates.extend(
            _detect_saturated_regions_for_dense_split(
                img_bgr,
                region,
                expected_count=max(expected_count, remaining_needed),
                saturation_threshold=saturation_threshold,
                min_component_area_ratio=min_component_area_ratio,
                max_component_area_ratio=max_component_area_ratio,
                padding_percent=padding_percent,
            )
        )
    if not dense_candidates:
        return boxes

    combined = retained + dense_candidates
    combined.sort(key=lambda b: b.get("area", b.get("width", 0) * b.get("height", 0)), reverse=True)
    selected: List[Dict[str, int]] = []
    for candidate in combined:
        if len(selected) >= expected_count:
            break
        if any(_box_iou(candidate, existing) >= 0.6 for existing in selected):
            continue
        selected.append(candidate)
    if len(selected) <= len(boxes):
        return boxes
    return _sort_boxes_reading_order(selected)


_REFERENCE_LABEL_CATEGORY_RE = re.compile(
    r"\b(?:card\s+index|programming\s+cards?|special\s+programming\s+cards?|"
    r"upgrade\s+cards?|permanent\s+upgrades?|temporary\s+upgrades?)\b",
    re.IGNORECASE,
)
_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}


def _compact_reference_label(raw: str) -> Optional[str]:
    label = re.sub(r"\s+", " ", str(raw or "")).strip(" .:;|")
    if not label:
        return None
    if _REFERENCE_LABEL_CATEGORY_RE.fullmatch(label):
        return None
    words = [word for word in re.split(r"\s+", label) if word]
    if not words or len(words) > 4:
        return None
    if sum(1 for ch in label if ch.isalpha()) < 2:
        return None
    return label


def _card_reference_labels(box: Dict[str, Any]) -> List[str]:
    """Return compact labels that can anchor split card-reference crops."""
    texts: List[str] = []
    nearby = box.get("_nearby_text")
    if isinstance(nearby, str) and nearby.strip():
        texts.append(nearby)
    description = box.get("_description")
    if not texts and isinstance(description, str) and description.strip():
        # _target_description joins nearby text as an em-dash segment. Use it as
        # a fallback for older boxes that predate explicit nearby_text metadata.
        texts.extend(re.split(r"\s+[—–]\s+", description))

    labels: List[str] = []
    seen: Set[str] = set()
    for text in texts:
        for part in re.split(r"[;\n]", text):
            for candidate in re.split(r",", part):
                label = _compact_reference_label(candidate)
                if not label:
                    continue
                key = label.casefold()
                if key in seen:
                    continue
                labels.append(label)
                seen.add(key)
    return labels


def _card_reference_expected_count(box: Dict[str, Any], labels: List[str]) -> int:
    if labels:
        return len(labels)
    description = str(box.get("_description") or "")
    match = re.search(r"\b(\d{1,2})\s+(?:card|component|reference)\b", description, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match = re.search(r"\b(" + "|".join(_NUMBER_WORDS) + r")\s+(?:card|component|reference)", description, re.IGNORECASE)
    if match:
        return _NUMBER_WORDS[match.group(1).casefold()]
    expected = box.get("_expected_visual_contents")
    if isinstance(expected, list):
        return len(expected)
    return 0


def _split_card_reference_panel_boxes(
    image_path: str,
    boxes: List[Dict[str, int]],
    *,
    min_expected_count: int,
    saturation_threshold: int,
    min_component_area_ratio: float,
    max_component_area_ratio: float,
    padding_percent: float,
) -> List[Dict[str, int]]:
    """Split a multi-card reference panel into individual card-face crops.

    A visual planner may correctly decide that "the card reference grid" is an
    essential graphic, but a single rectangular panel often mixes source-pixel
    card faces with prose that is better represented as semantic HTML. When the
    panel exposes enough compact labels, reuse the dense visual-block detector
    to emit one crop per repeated card-like block.
    """
    if not boxes:
        return boxes
    img_bgr = None
    out: List[Dict[str, int]] = []
    changed = False
    for box in boxes:
        if not _should_split_card_reference_panel(box):
            out.append(box)
            continue
        labels = _card_reference_labels(box)
        expected_count = _card_reference_expected_count(box, labels)
        if expected_count < min_expected_count:
            out.append(box)
            continue
        if img_bgr is None:
            img_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if img_bgr is None:
            out.append(box)
            continue

        split_boxes = _detect_saturated_regions_for_dense_split(
            img_bgr,
            box,
            expected_count=expected_count,
            saturation_threshold=saturation_threshold,
            min_component_area_ratio=min_component_area_ratio,
            max_component_area_ratio=max_component_area_ratio,
            padding_percent=padding_percent,
        )
        minimum_usable = max(min_expected_count, int(round(expected_count * 0.7)))
        if len(split_boxes) < minimum_usable:
            out.append(box)
            continue

        base_target_id = str(box.get("_critical_graphics_target_id") or "").strip()
        for idx, split_box in enumerate(split_boxes):
            new_box = dict(split_box)
            _copy_detector_meta(box, new_box)
            label = labels[idx] if idx < len(labels) else ""
            new_box["_critical_graphics_role"] = "card_face"
            new_box["_contains_text"] = True
            new_box["_detection_method"] = "cv_guided_reference_panel_split"
            new_box["_description"] = f"Card face titled {label}" if label else "Card face from reference panel"
            if base_target_id:
                new_box["_critical_graphics_target_id"] = f"{base_target_id}-card-{idx + 1:02d}"
            out.append(new_box)
        changed = True
    if not changed:
        return boxes
    return _sort_boxes_reading_order(out)


def _rule_panel_expected_split_count(box: Dict[str, Any]) -> int:
    expected = box.get("_expected_visual_contents")
    if isinstance(expected, list):
        return max(2, min(8, len(expected)))
    return 4


def _split_text_heavy_rule_panel_boxes(
    image_path: str,
    boxes: List[Dict[str, int]],
    *,
    saturation_threshold: int,
    min_component_area_ratio: float,
    max_component_area_ratio: float,
    padding_percent: float,
) -> List[Dict[str, int]]:
    if not boxes:
        return boxes
    img_bgr = None
    out: List[Dict[str, int]] = []
    changed = False
    for box in boxes:
        if not _should_mask_text_heavy_rule_panel(box):
            out.append(box)
            continue
        if img_bgr is None:
            img_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if img_bgr is None:
            out.append(box)
            continue
        split_boxes = _detect_saturated_regions_for_dense_split(
            img_bgr,
            box,
            expected_count=_rule_panel_expected_split_count(box),
            saturation_threshold=saturation_threshold,
            min_component_area_ratio=min_component_area_ratio,
            max_component_area_ratio=max_component_area_ratio,
            padding_percent=padding_percent,
        )
        if len(split_boxes) < 2:
            out.append(box)
            continue

        refined_split_boxes: List[Dict[str, int]] = []
        for split_box in split_boxes:
            if _is_text_only_rule_panel_split_box(img_bgr, split_box):
                continue
            refined_split_boxes.extend(_split_mixed_rule_panel_visual_clusters(img_bgr, split_box))
        refined_split_boxes = _sort_boxes_reading_order(refined_split_boxes)
        refined_split_boxes = _group_rule_panel_placement_layout(box, refined_split_boxes, img_bgr)
        if len(refined_split_boxes) < 2:
            out.append(box)
            continue

        base_target_id = str(box.get("_critical_graphics_target_id") or "").strip()
        for idx, split_box in enumerate(refined_split_boxes, start=1):
            new_box = dict(split_box)
            _copy_detector_meta(box, new_box)
            new_box["_detection_method"] = "cv_guided_rule_panel_split"
            if base_target_id:
                new_box["_critical_graphics_target_id"] = f"{base_target_id}-part-{idx:02d}"
            _apply_rule_panel_child_metadata(new_box, box)
            out.append(new_box)
        changed = True
    if not changed:
        return boxes
    return _sort_boxes_reading_order(out)


def detect_nonwhite_boxes(
    image_path: Path,
    expected_count: int = 1,
    white_threshold: int = 245,
    close_kernel: int = 15,
    close_iterations: int = 2,
    min_nonwhite_ratio: float = 0.02,
    max_text_ratio: float = 0.02,
    text_line_kernel_w: int = 25,
    text_line_kernel_h: int = 3,
    text_line_iterations: int = 1,
    min_area_ratio: float = 0.01,
    max_area_ratio: float = 0.99,
    min_width: int = 50,
    min_height: int = 50,
    padding_percent: float = 0.05
) -> List[Dict[str, int]]:
    """Detect illustration boxes by thresholding non-white pixels and bounding large components."""
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return []

    h, w = img.shape[:2]
    img_area = w * h

    # Non-white mask: keep pixels darker than threshold
    mask = (img < white_threshold).astype("uint8") * 255

    # Close to fill halftone dots and unify photo regions
    k = close_kernel if close_kernel % 2 == 1 else close_kernel + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=close_iterations)

    # Build a coarse text-line mask for filtering (favor long horizontal text)
    _, text_bin = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    tlw = text_line_kernel_w if text_line_kernel_w % 2 == 1 else text_line_kernel_w + 1
    tlh = text_line_kernel_h if text_line_kernel_h % 2 == 1 else text_line_kernel_h + 1
    text_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (tlw, tlh))
    text_lines = cv2.morphologyEx(text_bin, cv2.MORPH_OPEN, text_kernel, iterations=text_line_iterations)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch
        ratio = area / img_area
        if ratio < min_area_ratio or ratio > max_area_ratio:
            continue
        if cw < min_width or ch < min_height:
            continue
        # Filter low-density text blocks (few nonwhite pixels)
        box = closed[y:y + ch, x:x + cw]
        nonwhite_ratio = float(np.count_nonzero(box)) / float(area)
        if nonwhite_ratio < min_nonwhite_ratio:
            continue
        text_box = text_lines[y:y + ch, x:x + cw]
        text_ratio = float(np.count_nonzero(text_box)) / float(area)
        if text_ratio > max_text_ratio:
            continue
        candidates.append({
            "x0": int(x),
            "y0": int(y),
            "x1": int(x + cw),
            "y1": int(y + ch),
            "width": int(cw),
            "height": int(ch),
            "area": area,
            "area_ratio": round(ratio, 4),
        })

    candidates.sort(key=lambda b: b["area"], reverse=True)

    selected = []
    for candidate in candidates:
        if len(selected) >= expected_count:
            break
        overlaps = False
        for sel in selected:
            if _boxes_overlap(candidate, sel):
                overlaps = True
                break
        if not overlaps:
            selected.append(candidate)

    padded = []
    for box in selected:
        pad_w = int(box["width"] * padding_percent)
        pad_h = int(box["height"] * padding_percent)
        x0 = max(0, box["x0"] - pad_w)
        y0 = max(0, box["y0"] - pad_h)
        x1 = min(w, box["x1"] + pad_w)
        y1 = min(h, box["y1"] + pad_h)
        padded.append({
            "x0": int(x0),
            "y0": int(y0),
            "x1": int(x1),
            "y1": int(y1),
            "width": int(x1 - x0),
            "height": int(y1 - y0),
            "area": int((x1 - x0) * (y1 - y0)),
            "area_ratio": round(((x1 - x0) * (y1 - y0)) / img_area, 4),
        })

    return padded


def detect_nontext_boxes(
    image_path: Path,
    expected_count: int = 1,
    white_threshold: int = 245,
    close_kernel: int = 15,
    close_iterations: int = 2,
    text_block_kernel_w: int = 35,
    text_block_kernel_h: int = 7,
    text_block_iterations: int = 2,
    min_area_ratio: float = 0.01,
    max_area_ratio: float = 0.99,
    min_width: int = 50,
    min_height: int = 50,
    padding_percent: float = 0.05
) -> List[Dict[str, int]]:
    """Detect illustration boxes by removing text blocks from non-white mask."""
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return []

    h, w = img.shape[:2]
    img_area = w * h

    # Non-white mask
    nonwhite = (img < white_threshold).astype("uint8") * 255

    # Close to fill halftone dots / unify photo regions
    k = close_kernel if close_kernel % 2 == 1 else close_kernel + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    nonwhite = cv2.morphologyEx(nonwhite, cv2.MORPH_CLOSE, kernel, iterations=close_iterations)

    # Text mask: threshold and dilate to join text into blocks
    _, text_bin = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kw = text_block_kernel_w if text_block_kernel_w % 2 == 1 else text_block_kernel_w + 1
    kh = text_block_kernel_h if text_block_kernel_h % 2 == 1 else text_block_kernel_h + 1
    text_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kw, kh))
    text_blocks = cv2.dilate(text_bin, text_kernel, iterations=text_block_iterations)

    # Remove text blocks from nonwhite mask
    nontext = cv2.bitwise_and(nonwhite, cv2.bitwise_not(text_blocks))

    contours, _ = cv2.findContours(nontext, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch
        ratio = area / img_area
        if ratio < min_area_ratio or ratio > max_area_ratio:
            continue
        if cw < min_width or ch < min_height:
            continue
        candidates.append({
            "x0": int(x),
            "y0": int(y),
            "x1": int(x + cw),
            "y1": int(y + ch),
            "width": int(cw),
            "height": int(ch),
            "area": area,
            "area_ratio": round(ratio, 4),
        })

    candidates.sort(key=lambda b: b["area"], reverse=True)

    selected = []
    for candidate in candidates:
        if len(selected) >= expected_count:
            break
        overlaps = False
        for sel in selected:
            if _boxes_overlap(candidate, sel):
                overlaps = True
                break
        if not overlaps:
            selected.append(candidate)

    padded = []
    for box in selected:
        pad_w = int(box["width"] * padding_percent)
        pad_h = int(box["height"] * padding_percent)
        x0 = max(0, box["x0"] - pad_w)
        y0 = max(0, box["y0"] - pad_h)
        x1 = min(w, box["x1"] + pad_w)
        y1 = min(h, box["y1"] + pad_h)
        padded.append({
            "x0": int(x0),
            "y0": int(y0),
            "x1": int(x1),
            "y1": int(y1),
            "width": int(x1 - x0),
            "height": int(y1 - y0),
            "area": int((x1 - x0) * (y1 - y0)),
            "area_ratio": round(((x1 - x0) * (y1 - y0)) / img_area, 4),
        })

    return padded


def _nonwhite_ratio(img_gray: np.ndarray, box: Dict[str, int], threshold: int) -> float:
    x0, y0, x1, y1 = box["x0"], box["y0"], box["x1"], box["y1"]
    crop = img_gray[y0:y1, x0:x1]
    if crop.size == 0:
        return 0.0
    mask = crop < threshold
    return float(mask.mean())


def select_boxes(
    image_path: Path,
    expected_count: int,
    candidates: List[Dict[str, int]],
    nonwhite_threshold: int,
    score_min_nonwhite: float
) -> List[Dict[str, int]]:
    """Select top non-overlapping boxes by area and nonwhite density."""
    if not candidates:
        return []

    img_gray = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img_gray is None:
        return candidates[:expected_count]

    scored = []
    for box in candidates:
        ratio = _nonwhite_ratio(img_gray, box, nonwhite_threshold)
        if ratio < score_min_nonwhite:
            continue
        score = (box.get("area_ratio", 0.0) or 0.0) * (0.5 + 0.5 * ratio)
        scored.append((score, box))
    if not scored:
        scored = [(box.get("area_ratio", 0.0) or 0.0, box) for box in candidates]

    scored.sort(key=lambda t: t[0], reverse=True)
    selected: List[Dict[str, int]] = []
    for _, candidate in scored:
        if len(selected) >= expected_count:
            break
        overlaps = False
        for sel in selected:
            if _boxes_overlap(candidate, sel):
                overlaps = True
                break
        if not overlaps:
            selected.append(candidate)
    return selected


def crop_illustrations_guided(
    ocr_manifest: str,
    output_dir: str,
    run_id: Optional[str] = None,
    transparency: bool = False,
    threshold: int = 230,
    output_format: Optional[str] = None,
    jpeg_quality: int = 92,
    blur: int = 7,
    text_kernel: int = 3,
    text_iterations: int = 1,
    detection_mode: str = "contour",
    white_threshold: int = 245,
    close_kernel: int = 15,
    close_iterations: int = 2,
    text_block_kernel_w: int = 35,
    text_block_kernel_h: int = 7,
    text_block_iterations: int = 2,
    score_min_nonwhite: float = 0.02,
    min_nonwhite_ratio: float = 0.02,
    max_text_ratio: float = 0.02,
    text_line_kernel_w: int = 25,
    text_line_kernel_h: int = 3,
    text_line_iterations: int = 1,
    min_area_ratio: float = 0.01,
    max_area_ratio: float = 0.99,
    min_width: int = 50,
    min_height: int = 50,
    highres_manifest: Optional[str] = None,
    highres_images_dir: Optional[str] = None,
    critical_graphics_manifest: Optional[str] = None,
    padding_percent: float = 0.05,
    rescue_model: Optional[str] = None,
    rescue_temperature: float = 0.0,
    rescue_max_tokens: int = 800,
    rescue_max_pages: int = 20,
    rescue_timeout_seconds: Optional[float] = None,
    rescue_include_alt: bool = False,
    rescue_always: bool = False,
    rescue_caption_second_pass: bool = False,
    rescue_caption_max_tokens: int = 400,
    refine_with_nonwhite: bool = False,
    refine_close_kernel: int = 5,
    refine_close_iterations: int = 1,
    refine_with_nontext: bool = False,
    refine_with_textlines: bool = False,
    refine_textlines_min_area_ratio: float = 0.05,
    trim_text_edges: bool = False,
    text_edge_max_ratio: float = 0.2,
    text_edge_margin_px: int = 4,
    trim_ocr_text_edges: bool = False,
    ocr_trim_edge_ratio: float = 0.2,
    ocr_trim_min_conf: int = 50,
    ocr_trim_min_word_len: int = 3,
    ocr_trim_min_line_words: int = 2,
    ocr_trim_min_line_chars: int = 6,
    ocr_trim_max_ratio: float = 0.45,
    ocr_trim_margin_px: int = 6,
    ocr_tesseract_cmd: Optional[str] = None,
    trim_layout_text: bool = False,
    layout_text_model: str = "PP-DocLayout_plus-L",
    layout_text_score_thresh: float = 0.6,
    layout_text_max_gap_ratio: float = 0.2,
    layout_text_bottom_band_ratio: float = 0.35,
    layout_text_top_band_ratio: float = 0.35,
    layout_text_margin_px: int = 6,
    layout_text_min_width_ratio: float = 0.3,
    layout_text_max_height_ratio: float = 0.25,
    layout_split_text: bool = False,
    layout_split_min_gap_ratio: float = 0.15,
    layout_split_margin_px: int = 6,
    split_when_missing: bool = True,
    split_gap_ratio_threshold: float = 0.01,
    split_min_gap_px: int = 12,
    split_min_segment_height_ratio: float = 0.12,
    split_min_segment_nonwhite_ratio: float = 0.01,
    dense_split_when_missing: bool = False,
    dense_split_min_expected_count: int = 3,
    dense_split_min_area_ratio: float = 0.35,
    dense_split_min_component_area_ratio: float = 0.0015,
    dense_split_max_component_area_ratio: float = 0.12,
    dense_split_saturation_threshold: int = 35,
    trim_caption: bool = False,
    caption_max_height_ratio: float = 0.18,
    caption_text_ratio_threshold: float = 0.2,
    caption_margin_px: int = 4,
    caption_max_nonwhite_ratio: float = 0.2,
    caption_trim_passes: int = 1,
    caption_relax_max_gap_ratio: float = 0.15,
    cover_pages: str = "",
    only_pages: str = "",
) -> List[Dict[str, Any]]:
    """Crop illustrations from pages identified by OCR.

    Args:
        ocr_manifest: Path to OCR JSONL (page_html_v1 schema with images field)
        output_dir: Output directory for cropped images
        run_id: Optional run identifier
        transparency: Generate alpha versions for B&W images
        threshold: White threshold for transparency
        output_format: Output image format (png or jpeg)
        jpeg_quality: JPEG quality when output_format=jpeg
        blur: Gaussian blur kernel size for CV
        min_area_ratio: Min box area ratio for CV
        max_area_ratio: Max box area ratio for CV
        min_width: Min box width in pixels
        min_height: Min box height in pixels
        highres_manifest: Optional path to high-res page images manifest (for better quality crops)
        critical_graphics_manifest: Optional VLM visual-planner manifest with source-pixel crop targets
        padding_percent: Percentage padding around detected boxes (default 0.05 = 5%)

    Returns:
        List of manifest records for cropped illustrations
    """
    ensure_dir(output_dir)
    images_dir = os.path.join(output_dir, "images")
    ensure_dir(images_dir)

    fmt, ext = _normalize_output_format(output_format)
    if transparency and fmt == "jpeg":
        _log("  WARNING: transparency requested with JPEG output; disabling transparency.")
        transparency = False

    tesseract_cmd = ocr_tesseract_cmd or os.environ.get("TESSERACT_CMD") or shutil.which("tesseract")
    if trim_ocr_text_edges and not tesseract_cmd:
        _log("  WARNING: trim_ocr_text_edges enabled but no tesseract found; skipping OCR trims.")
    layout_engine = None
    layout_engine_failed = False
    layout_text_cache: Dict[int, List[List[int]]] = {}

    pages = list(read_jsonl(ocr_manifest))
    manifest = []
    critical_targets_by_page = _load_critical_graphics_targets(critical_graphics_manifest)
    if critical_targets_by_page:
        target_count = sum(len(targets) for targets in critical_targets_by_page.values())
        _log(f"Loaded {target_count} critical graphics target(s) from {critical_graphics_manifest}")

    # Build high-res page map from highres_manifest OR from image_native fields
    highres_page_map = {}

    # First, check if pages have image_native field (preferred)
    native_count = 0
    for page in pages:
        page_num = page.get("page_number")
        image_native = page.get("image_native")
        if page_num and image_native and os.path.exists(image_native):
            highres_page_map[page_num] = image_native
            native_count += 1

    if native_count > 0:
        _log(f"Using image_native from manifest for {native_count} pages")

    # If a high-res images directory is provided, map by sorted order (1-based page_number)
    if highres_images_dir:
        input_dir = Path(highres_images_dir)
        if input_dir.exists() and input_dir.is_dir():
            images = _iter_images(input_dir)
            if images:
                for idx, img_path in enumerate(images, start=1):
                    highres_page_map[idx] = str(img_path.resolve())
                _log(f"Loaded {len(images)} high-res images from directory {input_dir}")
        else:
            _log(f"High-res images dir not found: {input_dir}")

    # If highres_manifest provided, override/supplement with those
    if highres_manifest:
        _log(f"Loading additional high-res images from {highres_manifest}")
        highres_pages = list(read_jsonl(highres_manifest))
        external_count = 0
        for hr_page in highres_pages:
            page_num = hr_page.get("page_number")
            # Check both image and image_native from external manifest
            image_path = hr_page.get("image_native") or hr_page.get("image")
            if page_num and image_path and os.path.exists(image_path):
                highres_page_map[page_num] = image_path
                external_count += 1
        _log(f"Loaded {external_count} high-res images from external manifest")

    # Filter to pages with images (check images field or extract from HTML)
    pages_with_images = []
    for p in pages:
        if p.get("images"):
            pages_with_images.append(p)
        elif p.get("html") and "<img" in p.get("html", ""):
            # Fallback: extract from HTML for older OCR output
            extracted = _extract_images_from_html(p.get("html", ""))
            if extracted:
                p["images"] = extracted
                pages_with_images.append(p)

    if critical_targets_by_page:
        existing_page_nums = {p.get("page_number") for p in pages_with_images}
        for p in pages:
            pn = p.get("page_number")
            if pn in critical_targets_by_page and pn not in existing_page_nums:
                pages_with_images.append(p)
                _log(f"  Added page {pn} to processing list (critical graphics manifest)")
        pages_with_images.sort(key=lambda p: p.get("page_number", 0))

    _log(f"Found {len(pages_with_images)} pages with images out of {len(pages)} total")

    # Parse cover_pages param
    cover_pages_set = set()
    if cover_pages:
        for token in cover_pages.split(","):
            token = token.strip()
            if token:
                try:
                    cover_pages_set.add(int(token))
                except ValueError:
                    pass

    # Ensure cover pages are in the processing list even if OCR didn't flag them
    if cover_pages_set:
        existing_page_nums = {p.get("page_number") for p in pages_with_images}
        for p in pages:
            pn = p.get("page_number")
            if pn in cover_pages_set and pn not in existing_page_nums:
                pages_with_images.append(p)
                _log(f"  Added page {pn} to processing list (cover page)")
        # Re-sort by page number to maintain order
        pages_with_images.sort(key=lambda p: p.get("page_number", 0))

    # --only-pages: filter to specific pages for targeted re-runs
    only_pages_set: Set[int] = set()
    if only_pages:
        for token in only_pages.split(","):
            token = token.strip()
            if token:
                try:
                    only_pages_set.add(int(token))
                except ValueError:
                    pass
    if only_pages_set:
        pages_with_images = [
            p for p in pages_with_images
            if p.get("page_number") in only_pages_set
        ]
        _log(f"--only-pages: filtered to {len(pages_with_images)} pages {sorted(only_pages_set)}")

        # Clean up old crop images for targeted pages so stale files don't linger
        removed = _prune_stale_crop_images(images_dir, page_numbers=only_pages_set)
        if removed:
            _log(f"Removed {removed} stale crop images for targeted pages")

    rescue_used = 0
    for page_rec in pages_with_images:
        page_num = page_rec.get("page_number")
        image_path = page_rec.get("image")
        ocr_images = page_rec.get("images", [])
        critical_targets = critical_targets_by_page.get(page_num, [])

        # Use high-res image if available, otherwise use OCR image
        source_image_path = highres_page_map.get(page_num, image_path)

        if not source_image_path or not os.path.exists(source_image_path):
            _log(f"  Page {page_num}: Image not found, skipping")
            continue

        # Cover page: capture full page with whitespace trimming only
        if page_num in cover_pages_set:
            _log(f"  Page {page_num}: Cover page — full-page capture with whitespace trim")
            try:
                cover_img = Image.open(source_image_path)
                cx0, cy0, cx1, cy1 = _autocrop_whitespace(cover_img, white_threshold=white_threshold)
                cropped = cover_img.crop((cx0, cy0, cx1, cy1))
                filename = f"page-{page_num:03d}-000.{ext}"
                filepath = os.path.join(images_dir, filename)
                if fmt == "jpeg":
                    if cropped.mode not in ("RGB", "L"):
                        cropped = cropped.convert("RGB")
                    cropped.save(filepath, "JPEG", quality=jpeg_quality, optimize=True)
                else:
                    cropped.save(filepath, "PNG")
                is_bw = _is_bw_image(cropped)
                alt = ""
                if ocr_images:
                    alt = ocr_images[0].get("alt", "")
                manifest.append({
                    "schema_version": "illustration_v1",
                    "module_id": "crop_illustrations_guided_v1",
                    "run_id": run_id,
                    "created_at": _utc(),
                    "source_image": image_path,
                    "source_page": page_num,
                    "filename": filename,
                    "filename_alpha": None,
                    "has_transparency": False,
                    "is_color": not is_bw,
                    "alt": alt,
                    "bbox": {"x0": cx0, "y0": cy0, "x1": cx1, "y1": cy1,
                             "width": cx1 - cx0, "height": cy1 - cy0},
                    "area_ratio": round(((cx1 - cx0) * (cy1 - cy0)) / float(max(1, cover_img.width * cover_img.height)), 4),
                    "detection_method": "cover_page",
                    "image_description": "Book cover page",
                    "contains_text": True,
                    "source_issues": "",
                    "caption_box": None,
                    "caption_text": None,
                })
            except Exception as exc:
                _log(f"  Page {page_num}: Cover page capture failed: {exc}")
            continue

        # Calculate expected count. Prefer the visual-planner manifest when it
        # exists; it is a semantic intent signal, while OCR placeholders are a
        # fallback proxy.
        if critical_targets:
            expected_count = len(critical_targets)
        elif len(ocr_images) > 1:
            # If multiple <img> tags exist, prefer tag count (data-count is often noisy).
            expected_count = len(ocr_images)
        else:
            # If only one tag exists, allow data-count to request multiple crops.
            expected_count = sum(img.get("count", 1) for img in ocr_images)

        # Flatten descriptions for crop alt text, VLM rescue hints, and matching.
        ocr_descriptions = []
        if critical_targets:
            for target in critical_targets:
                ocr_descriptions.append(_target_description(target))
        elif len(ocr_images) > 1:
            for img in ocr_images:
                ocr_descriptions.append(img.get("alt", ""))
        else:
            for img in ocr_images:
                count = img.get("count", 1)
                for _ in range(count):
                    ocr_descriptions.append(img.get("alt", ""))

        using_highres = source_image_path != image_path
        resolution_label = "high-res" if using_highres else "OCR-res"
        _log(f"  Page {page_num}: Expecting {expected_count} illustration(s) [{resolution_label}]")

        source_img_w = None
        source_img_h = None
        if critical_targets:
            try:
                with Image.open(source_image_path) as size_img:
                    source_img_w, source_img_h = size_img.size
            except Exception:
                source_img_w = None
                source_img_h = None
        boxes_from_critical_manifest = [
            _box_from_critical_target(
                target,
                image_width=source_img_w,
                image_height=source_img_h,
                # Visual-planner targets are already semantic source-pixel crop
                # intent. Only apply narrow role-specific safety margins where
                # visual completeness is more likely to fail than prose pickup.
                padding_percent=_critical_target_padding_percent(target),
            )
            for target in critical_targets
        ]
        boxes_from_critical_manifest = [box for box in boxes_from_critical_manifest if box]
        if boxes_from_critical_manifest:
            boxes = boxes_from_critical_manifest
            _log(f"    Critical graphics manifest supplied {len(boxes)} bbox target(s)")
        # Run CV detection with expected count
        elif detection_mode == "layout":
            if layout_engine is None and not layout_engine_failed:
                try:
                    os.environ.setdefault("DISABLE_MODEL_SOURCE_CHECK", "True")
                    from paddleocr import LayoutDetection
                    layout_engine = LayoutDetection(model_name=layout_text_model)
                except Exception as exc:
                    layout_engine_failed = True
                    _log(f"  WARNING: layout detection failed to init: {exc}")
            if layout_engine is None:
                boxes = []
            else:
                boxes = _layout_image_boxes_for_page(
                    layout_engine,
                    source_image_path,
                    score_thresh=layout_text_score_thresh,
                )
                if boxes:
                    boxes = _prune_contained_boxes(boxes, contain_ratio=0.9, min_area_ratio=1.5)
        elif detection_mode == "nonwhite":
            boxes = detect_nonwhite_boxes(
                Path(source_image_path),
                expected_count=expected_count,
                white_threshold=white_threshold,
                close_kernel=close_kernel,
                close_iterations=close_iterations,
                min_nonwhite_ratio=min_nonwhite_ratio,
                max_text_ratio=max_text_ratio,
                text_line_kernel_w=text_line_kernel_w,
                text_line_kernel_h=text_line_kernel_h,
                text_line_iterations=text_line_iterations,
                min_area_ratio=min_area_ratio,
                max_area_ratio=max_area_ratio,
                min_width=min_width,
                min_height=min_height,
                padding_percent=padding_percent,
            )
        elif detection_mode == "nontext":
            boxes = detect_nontext_boxes(
                Path(source_image_path),
                expected_count=expected_count,
                white_threshold=white_threshold,
                close_kernel=close_kernel,
                close_iterations=close_iterations,
                text_block_kernel_w=text_block_kernel_w,
                text_block_kernel_h=text_block_kernel_h,
                text_block_iterations=text_block_iterations,
                min_area_ratio=min_area_ratio,
                max_area_ratio=max_area_ratio,
                min_width=min_width,
                min_height=min_height,
                padding_percent=padding_percent,
            )
        elif detection_mode == "auto":
            contour_boxes = detect_contours_cv(
                Path(source_image_path),
                expected_count=expected_count,
                blur=blur,
                text_kernel=text_kernel,
                text_iterations=text_iterations,
                min_area_ratio=min_area_ratio,
                max_area_ratio=max_area_ratio,
                min_width=min_width,
                min_height=min_height,
                padding_percent=padding_percent,
            )
            nonwhite_boxes = detect_nonwhite_boxes(
                Path(source_image_path),
                expected_count=expected_count,
                white_threshold=white_threshold,
                close_kernel=close_kernel,
                close_iterations=close_iterations,
                min_nonwhite_ratio=min_nonwhite_ratio,
                max_text_ratio=max_text_ratio,
                text_line_kernel_w=text_line_kernel_w,
                text_line_kernel_h=text_line_kernel_h,
                text_line_iterations=text_line_iterations,
                min_area_ratio=min_area_ratio,
                max_area_ratio=max_area_ratio,
                min_width=min_width,
                min_height=min_height,
                padding_percent=padding_percent,
            )
            boxes = select_boxes(
                Path(source_image_path),
                expected_count,
                contour_boxes + nonwhite_boxes,
                nonwhite_threshold=white_threshold,
                score_min_nonwhite=score_min_nonwhite,
            )
        else:
            boxes = detect_contours_cv(
                Path(source_image_path),
                expected_count=expected_count,
                blur=blur,
                text_kernel=text_kernel,
                text_iterations=text_iterations,
                min_area_ratio=min_area_ratio,
                max_area_ratio=max_area_ratio,
                min_width=min_width,
                min_height=min_height,
                padding_percent=padding_percent,
            )

        image_data = None
        if rescue_model and rescue_used < rescue_max_pages and (rescue_always or len(boxes) < expected_count):
            try:
                img = cv2.imread(str(source_image_path), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    raise RuntimeError("image load failed")
                h, w = img.shape[:2]
                image_data = _encode_image(source_image_path)
                _log(f"    VLM rescue: requesting {expected_count} box(es) via {rescue_model}")
                alt_hints = ocr_descriptions if rescue_include_alt else None
                vlm_boxes, usage, request_id, vlm_raw = _call_vlm_boxes(
                    rescue_model,
                    image_data,
                    expected_count,
                    alt_hints,
                    rescue_temperature,
                    rescue_max_tokens,
                    rescue_timeout_seconds,
                )
                # Fix Gemini's axis-swap tendency: [y,x,y,x] → [x,y,x,y]
                if _is_gemini_model(rescue_model) and vlm_boxes:
                    vlm_boxes = _auto_fix_axis_swap(vlm_boxes, w, h)
                debug_dir = os.environ.get("CROP_VLM_DEBUG_DIR")
                if debug_dir:
                    ensure_dir(debug_dir)
                    debug_path = os.path.join(debug_dir, f"page-{page_num:03d}-vlm.json")
                    with open(debug_path, "w", encoding="utf-8") as f:
                        json.dump(
                            {
                                "page_number": page_num,
                                "expected_count": expected_count,
                                "alt_hints": alt_hints or [],
                                "raw": vlm_raw,
                            },
                            f,
                            ensure_ascii=True,
                            indent=2,
                        )
                normalized = []
                for box in vlm_boxes:
                    px = _normalize_box(box, w, h)
                    if not px:
                        continue
                    cap_box = box.get("caption_box")
                    if isinstance(cap_box, dict):
                        cap_px = _normalize_box(cap_box, w, h)
                        if cap_px:
                            px["caption_box"] = cap_px
                    px["_from_vlm"] = True
                    _copy_detector_meta(box, px)
                    area_ratio = (px["width"] * px["height"]) / float(w * h)
                    px["area_ratio"] = round(area_ratio, 4)
                    normalized.append(px)
                if normalized:
                    boxes = normalized[:expected_count]
                    rescue_used += 1
                    _log(f"    VLM rescue: using {len(boxes)} box(es) (request {request_id})")
                else:
                    _log("    VLM rescue: no valid boxes parsed")
            except Exception as exc:
                _log(f"    VLM rescue failed: {exc}")

        img_gray = None
        if boxes and (trim_caption or (split_when_missing and len(boxes) < expected_count)):
            img_gray = cv2.imread(str(source_image_path), cv2.IMREAD_GRAYSCALE)

        if rescue_caption_second_pass and rescue_model and boxes:
            try:
                if img_gray is None:
                    img_gray = cv2.imread(str(source_image_path), cv2.IMREAD_GRAYSCALE)
                if img_gray is not None:
                    if image_data is None:
                        image_data = _encode_image(source_image_path)
                    h, w = img_gray.shape[:2]
                    cap_boxes, _, _, _ = _call_vlm_caption_boxes(
                        rescue_model,
                        image_data,
                        expected_count=len(boxes),
                        alt_hints=ocr_descriptions if rescue_include_alt else None,
                        temperature=rescue_temperature,
                        max_tokens=rescue_caption_max_tokens,
                        timeout_seconds=rescue_timeout_seconds,
                    )
                    normalized_caps = []
                    for cap in cap_boxes:
                        cap_px = _normalize_box(cap, w, h)
                        if cap_px:
                            normalized_caps.append(cap_px)
                    if normalized_caps:
                        for idx, cap_px in enumerate(normalized_caps):
                            if idx >= len(boxes):
                                break
                            boxes[idx]["caption_box"] = {
                                "x0": cap_px["x0"],
                                "y0": cap_px["y0"],
                                "x1": cap_px["x1"],
                                "y1": cap_px["y1"],
                            }
            except Exception as exc:
                _log(f"    VLM caption pass failed: {exc}")

        if refine_with_nonwhite and boxes:
            boxes = _refine_boxes_with_nonwhite(
                source_image_path,
                boxes,
                white_threshold=white_threshold,
                close_kernel=refine_close_kernel,
                close_iterations=refine_close_iterations,
            )

        if refine_with_nontext and boxes:
            if img_gray is None:
                img_gray = cv2.imread(str(source_image_path), cv2.IMREAD_GRAYSCALE)
            boxes = _refine_boxes_with_nontext(
                img_gray,
                boxes,
                white_threshold=white_threshold,
                close_kernel=close_kernel,
                close_iterations=close_iterations,
                text_block_kernel_w=text_block_kernel_w,
                text_block_kernel_h=text_block_kernel_h,
                text_block_iterations=text_block_iterations,
            )

        if refine_with_textlines and boxes:
            if img_gray is None:
                img_gray = cv2.imread(str(source_image_path), cv2.IMREAD_GRAYSCALE)
            refined = []
            to_refine = []
            for box in boxes:
                if box.get("_from_vlm"):
                    refined.append(box)
                else:
                    to_refine.append(box)
            if to_refine:
                refined.extend(
                    _refine_boxes_remove_text_lines(
                        img_gray,
                        to_refine,
                        white_threshold=white_threshold,
                        text_line_kernel_w=text_line_kernel_w,
                        text_line_kernel_h=text_line_kernel_h,
                        text_line_iterations=text_line_iterations,
                        min_component_area_ratio=refine_textlines_min_area_ratio,
                    )
                )
            boxes = refined

        if trim_text_edges and boxes:
            if img_gray is None:
                img_gray = cv2.imread(str(source_image_path), cv2.IMREAD_GRAYSCALE)
            trimmed_edges = []
            for box in boxes:
                trimmed_edges.append(
                    _trim_text_edges(
                        img_gray,
                        box,
                        white_threshold=white_threshold,
                        text_line_kernel_w=text_line_kernel_w,
                        text_line_kernel_h=text_line_kernel_h,
                        text_line_iterations=text_line_iterations,
                        max_trim_ratio=text_edge_max_ratio,
                        margin_px=text_edge_margin_px,
                    )
                )
            boxes = trimmed_edges

        if not boxes:
            _log(f"    CV detection found 0 boxes (expected {expected_count})")
            continue

        if len(boxes) < expected_count:
            _log(f"    CV detection found {len(boxes)} boxes (expected {expected_count})")

        # Load page image for cropping
        page_img = Image.open(source_image_path)
        img_w, img_h = page_img.size
        for box in boxes:
            if "area_ratio" not in box:
                area = (box["width"] * box["height"]) if box.get("width") and box.get("height") else 0
                if area and img_w and img_h:
                    box["area_ratio"] = round(area / float(img_w * img_h), 4)
                else:
                    box["area_ratio"] = 0.0
        if detection_mode == "layout" and boxes:
            boxes = sorted(boxes, key=lambda b: b.get("area_ratio", 0.0), reverse=True)[:expected_count]

        # Match boxes with OCR image descriptions by visual reading order.
        boxes_sorted = _sort_boxes_reading_order(boxes)
        boxes_deduped = _dedupe_boxes(boxes_sorted)
        if len(boxes_deduped) < len(boxes_sorted):
            boxes_sorted = boxes_deduped
            _log(f"    Deduped boxes: {len(boxes)} -> {len(boxes_sorted)}")

        if dense_split_when_missing and boxes_sorted:
            split_rule_panel_boxes = _split_text_heavy_rule_panel_boxes(
                source_image_path,
                boxes_sorted,
                saturation_threshold=dense_split_saturation_threshold,
                min_component_area_ratio=dense_split_min_component_area_ratio,
                max_component_area_ratio=dense_split_max_component_area_ratio,
                padding_percent=padding_percent,
            )
            if len(split_rule_panel_boxes) > len(boxes_sorted):
                _log(f"    Rule panel split: {len(boxes_sorted)} -> {len(split_rule_panel_boxes)} boxes")
                boxes_sorted = split_rule_panel_boxes
            split_reference_boxes = _split_card_reference_panel_boxes(
                source_image_path,
                boxes_sorted,
                min_expected_count=dense_split_min_expected_count,
                saturation_threshold=dense_split_saturation_threshold,
                min_component_area_ratio=dense_split_min_component_area_ratio,
                max_component_area_ratio=dense_split_max_component_area_ratio,
                padding_percent=padding_percent,
            )
            if len(split_reference_boxes) > len(boxes_sorted):
                _log(f"    Card reference split: {len(boxes_sorted)} -> {len(split_reference_boxes)} boxes")
                boxes_sorted = split_reference_boxes

        if dense_split_when_missing and boxes_sorted and len(boxes_sorted) < expected_count:
            dense_boxes = _split_dense_reference_boxes(
                source_image_path,
                boxes_sorted,
                expected_count=expected_count,
                min_expected_count=dense_split_min_expected_count,
                min_overbroad_area_ratio=dense_split_min_area_ratio,
                saturation_threshold=dense_split_saturation_threshold,
                min_component_area_ratio=dense_split_min_component_area_ratio,
                max_component_area_ratio=dense_split_max_component_area_ratio,
                padding_percent=padding_percent,
            )
            if len(dense_boxes) > len(boxes_sorted):
                _log(f"    Dense reference split: {len(boxes_sorted)} -> {len(dense_boxes)} boxes")
                boxes_sorted = dense_boxes

        if img_gray is not None and boxes_sorted and split_when_missing and len(boxes_sorted) < expected_count:
            min_segment_height = max(40, int(img_gray.shape[0] * split_min_segment_height_ratio))
            boxes_sorted = _split_boxes_to_count(
                img_gray,
                boxes_sorted,
                expected_count=expected_count,
                white_threshold=white_threshold,
                gap_ratio_threshold=split_gap_ratio_threshold,
                min_gap_px=split_min_gap_px,
                min_segment_height=min_segment_height,
                min_segment_nonwhite_ratio=split_min_segment_nonwhite_ratio,
            )

        if boxes_sorted:
            boxes_sorted = [_apply_caption_box(b, caption_margin_px, caption_relax_max_gap_ratio) for b in boxes_sorted]

        if trim_layout_text and boxes_sorted:
            if layout_engine is None and not layout_engine_failed:
                try:
                    os.environ.setdefault("DISABLE_MODEL_SOURCE_CHECK", "True")
                    from paddleocr import LayoutDetection
                    layout_engine = LayoutDetection(model_name=layout_text_model)
                except Exception as exc:
                    layout_engine_failed = True
                    _log(f"  WARNING: layout text trim disabled (LayoutDetection init failed): {exc}")
            if layout_engine is not None:
                layout_boxes = layout_text_cache.get(page_num)
                if layout_boxes is None:
                    layout_boxes = _layout_text_boxes_for_page(
                        layout_engine,
                        source_image_path,
                        score_thresh=layout_text_score_thresh,
                    )
                    layout_text_cache[page_num] = layout_boxes
                if layout_boxes:
                    processed = []
                    for box in boxes_sorted:
                        split_boxes = [box]
                        if layout_split_text:
                            split_boxes = _split_box_by_layout_text_band(
                                box,
                                layout_boxes,
                                min_width_ratio=layout_text_min_width_ratio,
                                max_height_ratio=layout_text_max_height_ratio,
                                min_gap_ratio=layout_split_min_gap_ratio,
                                margin_px=layout_split_margin_px,
                            )
                        for split_box in split_boxes:
                            processed.append(
                                _trim_box_by_layout_text(
                                    split_box,
                                    layout_boxes,
                                    max_gap_ratio=layout_text_max_gap_ratio,
                                    bottom_band_ratio=layout_text_bottom_band_ratio,
                                    top_band_ratio=layout_text_top_band_ratio,
                                    margin_px=layout_text_margin_px,
                                    min_width_ratio=layout_text_min_width_ratio,
                                    max_height_ratio=layout_text_max_height_ratio,
                                )
                            )
                    boxes_sorted = processed

        if trim_ocr_text_edges and boxes_sorted and tesseract_cmd:
            if img_gray is None:
                img_gray = cv2.imread(str(source_image_path), cv2.IMREAD_GRAYSCALE)
            if img_gray is not None:
                trimmed_ocr = []
                for box in boxes_sorted:
                    trimmed_ocr.append(
                        _trim_box_by_ocr_text(
                            img_gray,
                            box,
                            tesseract_cmd=tesseract_cmd,
                            edge_ratio=ocr_trim_edge_ratio,
                            min_conf=ocr_trim_min_conf,
                            min_word_len=ocr_trim_min_word_len,
                            white_threshold=white_threshold,
                            min_line_words=ocr_trim_min_line_words,
                            min_line_chars=ocr_trim_min_line_chars,
                            max_trim_ratio=ocr_trim_max_ratio,
                            margin_px=ocr_trim_margin_px,
                        )
                    )
                boxes_sorted = trimmed_ocr

        if trim_caption and boxes_sorted:
            if img_gray is None:
                img_gray = cv2.imread(str(source_image_path), cv2.IMREAD_GRAYSCALE)
            if img_gray is not None:
                trimmed = []
                for idx, box in enumerate(boxes_sorted):
                    if box.get("_caption_applied"):
                        trimmed.append(box)
                        continue
                    new_box = box
                    passes = max(1, int(caption_trim_passes))
                    for pass_idx in range(passes):
                        ratio = min(0.6, caption_max_height_ratio * (1.5 ** pass_idx))
                        next_box = _trim_caption_from_box(
                            img_gray,
                            new_box,
                            max_caption_height_ratio=ratio,
                            text_ratio_threshold=caption_text_ratio_threshold,
                            margin_px=caption_margin_px,
                            caption_max_nonwhite_ratio=caption_max_nonwhite_ratio,
                            white_threshold=white_threshold,
                        )
                        if next_box.get("y1") == new_box.get("y1"):
                            break
                        new_box = next_box
                    if new_box.get("y1") != box.get("y1"):
                        _log(f"    Trimmed caption: page {page_num} box {idx} y1 {box.get('y1')} -> {new_box.get('y1')}")
                    trimmed.append(new_box)
                boxes_sorted = trimmed

        if boxes_sorted:
            boxes_sorted = [
                _trim_rule_example_bottom_prose_band(source_image_path, box)
                for box in boxes_sorted
            ]
            boxes_sorted = [
                _trim_rule_panel_cost_reference_card(source_image_path, box)
                for box in boxes_sorted
            ]
            boxes_sorted = [
                _expand_rule_panel_placement_layout_box(source_image_path, box)
                for box in boxes_sorted
            ]
            boxes_sorted = [
                _expand_player_mat_register_rule_example_box(source_image_path, box)
                for box in boxes_sorted
            ]
            boxes_sorted = [
                _expand_integrated_callout_rule_example_box(source_image_path, box)
                for box in boxes_sorted
            ]

        for box in boxes_sorted:
            if "area_ratio" not in box:
                area = (box["x1"] - box["x0"]) * (box["y1"] - box["y0"])
                box["area_ratio"] = round(area / float(img_w * img_h), 4) if area and img_w and img_h else 0.0

        boxes_sorted = _sort_boxes_reading_order(boxes_sorted)
        matched_descriptions = _align_descriptions_to_detected_boxes(ocr_descriptions, boxes_sorted)
        for box_idx, box in enumerate(boxes_sorted):
            # Prefer metadata that traveled with the box. Index-based matching is
            # only safe for detector outputs that do not already carry descriptors.
            alt = str(box.get("_description") or "").strip()
            if not alt and box_idx < len(matched_descriptions):
                alt = matched_descriptions[box_idx]

            # Crop illustration
            cropped = page_img.crop((box["x0"], box["y0"], box["x1"], box["y1"]))
            masked_crop = _mask_detached_map_background(cropped, box)
            if masked_crop is None:
                masked_crop = _mask_rule_panel_placement_layout_prose(cropped, box)
            if masked_crop is None:
                masked_crop = _mask_rule_panel_split_prose(cropped, box)
            if masked_crop is None:
                masked_crop = _mask_detached_rule_panel_prose(cropped, box)
            if masked_crop is not None:
                cropped = masked_crop

            # Generate filename
            actual_ext = "png" if cropped.mode == "RGBA" else ext
            filename = f"page-{page_num:03d}-{box_idx:03d}.{actual_ext}"
            filepath = os.path.join(images_dir, filename)

            # Save original
            if cropped.mode == "RGBA":
                cropped.save(filepath, "PNG")
            elif fmt == "jpeg":
                if cropped.mode not in ("RGB", "L"):
                    cropped = cropped.convert("RGB")
                cropped.save(filepath, "JPEG", quality=jpeg_quality, optimize=True)
            else:
                cropped.save(filepath, "PNG")

            # Detect if image is color or B&W
            is_bw = _is_bw_image(cropped)
            is_color = not is_bw

            # Generate alpha version if B&W and transparency enabled
            filename_alpha = None
            has_transparency = cropped.mode == "RGBA"

            if transparency and is_bw:
                filename_alpha = f"page-{page_num:03d}-{box_idx:03d}-alpha.png"
                filepath_alpha = os.path.join(images_dir, filename_alpha)

                cropped_alpha = _make_transparent(cropped, threshold)
                cropped_alpha.save(filepath_alpha, "PNG")
                has_transparency = True

            # Build manifest record
            record = {
                "schema_version": "illustration_v1",
                "module_id": "crop_illustrations_guided_v1",
                "run_id": run_id,
                "created_at": _utc(),
                "source_image": image_path,
                "source_page": page_num,
                "filename": filename,
                "filename_alpha": filename_alpha,
                "has_transparency": has_transparency,
                "is_color": is_color,
                "alt": alt,
                "bbox": {
                    "x0": box["x0"],
                    "y0": box["y0"],
                    "x1": box["x1"],
                    "y1": box["y1"],
                    "width": box["width"],
                    "height": box["height"]
                },
                "area_ratio": box["area_ratio"],
                "detection_method": box.get("_detection_method", "cv_guided"),
                "image_description": box.get("_description", ""),
                "contains_text": box.get("_contains_text", False),
                "source_issues": box.get("_source_issues", ""),
                "caption_box": box.get("caption_box"),
                "caption_text": box.get("_caption_text") or None,
            }
            if box.get("_critical_graphics_target_id"):
                record["critical_graphics_target_id"] = box.get("_critical_graphics_target_id")
                record["critical_graphics_importance"] = box.get("_critical_graphics_importance")
                record["critical_graphics_role"] = box.get("_critical_graphics_role")
                record["critical_graphics_reason"] = box.get("_critical_graphics_reason")
            if box.get("_nearby_text"):
                record["nearby_text"] = box.get("_nearby_text")
            if box.get("_expected_visual_contents"):
                record["expected_visual_contents"] = box.get("_expected_visual_contents")

            manifest.append(record)

    # Count color vs B&W illustrations
    color_count = sum(1 for m in manifest if m.get("is_color", False))
    bw_count = len(manifest) - color_count

    _log(f"\nCropped {len(manifest)} illustration(s) from {len(pages_with_images)} pages")
    _log(f"  Color: {color_count}, B&W: {bw_count}")
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Crop illustrations using OCR metadata + CV detection"
    )
    parser.add_argument(
        "--ocr-manifest",
        required=True,
        help="OCR JSONL manifest (page_html_v1 with images field)"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory"
    )
    parser.add_argument(
        "--run-id",
        help="Run identifier"
    )
    parser.add_argument(
        "--transparency",
        action="store_true",
        help="Generate alpha versions for B&W images"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=230,
        help="White threshold for transparency (default 230)"
    )
    parser.add_argument(
        "--output-format",
        default="png",
        choices=["png", "jpeg", "jpg"],
        help="Output image format: png (default) or jpeg"
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=92,
        help="JPEG quality when output-format=jpeg (default 92)"
    )
    parser.add_argument(
        "--blur",
        type=int,
        default=7,
        help="Gaussian blur kernel size for CV (default 7)"
    )
    parser.add_argument(
        "--text-kernel",
        type=int,
        default=3,
        help="Morphological open kernel size to suppress small text (default 3)"
    )
    parser.add_argument(
        "--text-iterations",
        type=int,
        default=1,
        help="Morphological open iterations for text suppression (default 1)"
    )
    parser.add_argument(
        "--detection-mode",
        default="contour",
        choices=["contour", "nonwhite", "nontext", "auto", "layout"],
        help="Detection mode: contour (default), nonwhite, nontext, auto, or layout"
    )
    parser.add_argument(
        "--white-threshold",
        type=int,
        default=245,
        help="Nonwhite detection threshold (default 245)"
    )
    parser.add_argument(
        "--close-kernel",
        type=int,
        default=15,
        help="Morphological close kernel size for nonwhite mode (default 15)"
    )
    parser.add_argument(
        "--close-iterations",
        type=int,
        default=2,
        help="Morphological close iterations for nonwhite mode (default 2)"
    )
    parser.add_argument(
        "--text-block-kernel-w",
        type=int,
        default=35,
        help="Text block kernel width for nontext mode (default 35)"
    )
    parser.add_argument(
        "--text-block-kernel-h",
        type=int,
        default=7,
        help="Text block kernel height for nontext mode (default 7)"
    )
    parser.add_argument(
        "--text-block-iterations",
        type=int,
        default=2,
        help="Text block dilation iterations for nontext mode (default 2)"
    )
    parser.add_argument(
        "--score-min-nonwhite",
        type=float,
        default=0.02,
        help="Minimum nonwhite ratio for scoring candidate boxes (auto mode)"
    )
    parser.add_argument(
        "--min-nonwhite-ratio",
        type=float,
        default=0.02,
        help="Minimum nonwhite ratio for nonwhite mode (default 0.02)"
    )
    parser.add_argument(
        "--max-text-ratio",
        type=float,
        default=0.02,
        help="Maximum text ratio for nonwhite mode (default 0.02)"
    )
    parser.add_argument(
        "--text-line-kernel-w",
        type=int,
        default=25,
        help="Text line kernel width for nonwhite mode (default 25)"
    )
    parser.add_argument(
        "--text-line-kernel-h",
        type=int,
        default=3,
        help="Text line kernel height for nonwhite mode (default 3)"
    )
    parser.add_argument(
        "--text-line-iterations",
        type=int,
        default=1,
        help="Text line morphology iterations for nonwhite mode (default 1)"
    )
    parser.add_argument(
        "--min-area-ratio",
        type=float,
        default=0.01,
        help="Min box area ratio (default 0.01)"
    )
    parser.add_argument(
        "--max-area-ratio",
        type=float,
        default=0.99,
        help="Max box area ratio (default 0.99)"
    )
    parser.add_argument(
        "--min-width",
        type=int,
        default=50,
        help="Min box width in pixels (default 50)"
    )
    parser.add_argument(
        "--min-height",
        type=int,
        default=50,
        help="Min box height in pixels (default 50)"
    )
    parser.add_argument(
        "--highres-manifest",
        help="Optional high-res page images manifest (for better quality crops)"
    )
    parser.add_argument(
        "--highres-images-dir",
        default=None,
        help="Optional high-res images directory (sorted to page order)"
    )
    parser.add_argument(
        "--critical-graphics-manifest",
        default=None,
        help="Optional critical_graphics_manifest_v1 JSON with VLM-selected crop targets"
    )
    parser.add_argument(
        "--padding-percent",
        type=float,
        default=0.05,
        help="Percentage padding around detected boxes (default 0.05 = 5%%)"
    )
    parser.add_argument(
        "--rescue-model",
        default=None,
        help="Optional vision model to rescue image boxes when CV misses (e.g., gpt-5.1)"
    )
    parser.add_argument(
        "--rescue-temperature",
        type=float,
        default=0.0,
        help="Rescue model temperature (default 0.0)"
    )
    parser.add_argument(
        "--rescue-max-tokens",
        type=int,
        default=800,
        help="Rescue model max output tokens (default 800)"
    )
    parser.add_argument(
        "--rescue-max-pages",
        type=int,
        default=20,
        help="Maximum pages to rescue with VLM (default 20)"
    )
    parser.add_argument(
        "--rescue-timeout-seconds",
        type=float,
        default=None,
        help="Timeout seconds for rescue model requests"
    )
    parser.add_argument(
        "--rescue-include-alt",
        action="store_true",
        help="Include OCR image descriptions in rescue prompt"
    )
    parser.add_argument(
        "--rescue-always",
        action="store_true",
        help="Always use rescue model on image pages (overrides CV boxes)"
    )
    parser.add_argument(
        "--rescue-caption-second-pass",
        action="store_true",
        help="Run a second VLM pass to locate caption boxes"
    )
    parser.add_argument(
        "--rescue-caption-max-tokens",
        type=int,
        default=400,
        help="Max tokens for VLM caption pass (default 400)"
    )
    parser.add_argument(
        "--cover-pages",
        type=str,
        default="",
        help="Comma-separated page numbers to capture as full-page images (e.g. '1' or '1,127')"
    )
    parser.add_argument(
        "--only-pages",
        type=str,
        default="",
        help="Comma-separated page numbers to process (skip all others). Merges results into existing manifest."
    )
    parser.add_argument(
        "--refine-with-nonwhite",
        action="store_true",
        help="Refine boxes by expanding to nonwhite connected components"
    )
    parser.add_argument(
        "--refine-close-kernel",
        type=int,
        default=5,
        help="Close kernel size for refine nonwhite mask (default 5)"
    )
    parser.add_argument(
        "--refine-close-iterations",
        type=int,
        default=1,
        help="Close iterations for refine nonwhite mask (default 1)"
    )
    parser.add_argument(
        "--refine-with-nontext",
        action="store_true",
        help="Refine boxes by removing text blocks from nonwhite mask"
    )
    parser.add_argument(
        "--refine-with-textlines",
        action="store_true",
        help="Refine boxes by removing horizontal text lines (keep largest non-text component)"
    )
    parser.add_argument(
        "--refine-textlines-min-area-ratio",
        type=float,
        default=0.05,
        help="Minimum area ratio for text-line refinement (default 0.05)"
    )
    parser.add_argument(
        "--trim-text-edges",
        action="store_true",
        help="Trim text-line runs at top/bottom edges of a crop"
    )
    parser.add_argument(
        "--text-edge-max-ratio",
        type=float,
        default=0.2,
        help="Max fraction of box height allowed for text-edge trimming (default 0.2)"
    )
    parser.add_argument(
        "--text-edge-margin-px",
        type=int,
        default=4,
        help="Extra margin to remove past detected text-edge (default 4)"
    )
    parser.add_argument(
        "--trim-ocr-text-edges",
        action="store_true",
        help="Trim crops using OCR text detection in top/bottom bands"
    )
    parser.add_argument(
        "--ocr-trim-edge-ratio",
        type=float,
        default=0.2,
        help="Fraction of crop height to scan for OCR text (default 0.2)"
    )
    parser.add_argument(
        "--ocr-trim-min-conf",
        type=int,
        default=50,
        help="Minimum OCR confidence to consider text (default 50)"
    )
    parser.add_argument(
        "--ocr-trim-min-word-len",
        type=int,
        default=3,
        help="Minimum OCR word length to consider text (default 3)"
    )
    parser.add_argument(
        "--ocr-trim-min-line-words",
        type=int,
        default=2,
        help="Minimum number of words in a line to trim (default 2)"
    )
    parser.add_argument(
        "--ocr-trim-min-line-chars",
        type=int,
        default=6,
        help="Minimum number of characters in a line to trim (default 6)"
    )
    parser.add_argument(
        "--ocr-trim-max-ratio",
        type=float,
        default=0.45,
        help="Maximum fraction of crop height allowed for OCR trimming (default 0.45)"
    )
    parser.add_argument(
        "--ocr-trim-margin-px",
        type=int,
        default=6,
        help="Extra margin to remove past OCR text (default 6)"
    )
    parser.add_argument(
        "--ocr-tesseract-cmd",
        type=str,
        default=None,
        help="Optional tesseract command path for OCR trimming"
    )
    parser.add_argument(
        "--trim-layout-text",
        action="store_true",
        help="Trim crops using layout text boxes (PaddleOCR LayoutDetection)"
    )
    parser.add_argument(
        "--layout-text-model",
        type=str,
        default="PP-DocLayout_plus-L",
        help="Layout detection model name (default PP-DocLayout_plus-L)"
    )
    parser.add_argument(
        "--layout-text-score-thresh",
        type=float,
        default=0.6,
        help="Minimum score for layout text boxes (default 0.6)"
    )
    parser.add_argument(
        "--layout-text-max-gap-ratio",
        type=float,
        default=0.2,
        help="Max gap ratio beyond crop edge to consider text (default 0.2)"
    )
    parser.add_argument(
        "--layout-text-bottom-band-ratio",
        type=float,
        default=0.35,
        help="Bottom band ratio for caption trimming (default 0.35)"
    )
    parser.add_argument(
        "--layout-text-top-band-ratio",
        type=float,
        default=0.35,
        help="Top band ratio for header trimming (default 0.35)"
    )
    parser.add_argument(
        "--layout-text-margin-px",
        type=int,
        default=6,
        help="Extra margin to remove past layout text (default 6)"
    )
    parser.add_argument(
        "--layout-text-min-width-ratio",
        type=float,
        default=0.3,
        help="Minimum width ratio for layout text boxes (default 0.3)"
    )
    parser.add_argument(
        "--layout-text-max-height-ratio",
        type=float,
        default=0.25,
        help="Maximum height ratio for layout text boxes (default 0.25)"
    )
    parser.add_argument(
        "--layout-split-text",
        action="store_true",
        help="Split image boxes on mid-page layout text bands"
    )
    parser.add_argument(
        "--layout-split-min-gap-ratio",
        type=float,
        default=0.15,
        help="Minimum gap ratio around text band for splitting (default 0.15)"
    )
    parser.add_argument(
        "--layout-split-margin-px",
        type=int,
        default=6,
        help="Extra margin to remove past layout text band when splitting (default 6)"
    )
    parser.add_argument(
        "--split-when-missing",
        action="store_true",
        help="Split large boxes by whitespace gaps when expected_count is higher"
    )
    parser.add_argument(
        "--split-gap-ratio-threshold",
        type=float,
        default=0.01,
        help="Row nonwhite ratio threshold for gap splitting (default 0.01)"
    )
    parser.add_argument(
        "--split-min-gap-px",
        type=int,
        default=12,
        help="Minimum consecutive gap rows for splitting (default 12)"
    )
    parser.add_argument(
        "--split-min-segment-height-ratio",
        type=float,
        default=0.12,
        help="Minimum segment height as fraction of page height (default 0.12)"
    )
    parser.add_argument(
        "--split-min-segment-nonwhite-ratio",
        type=float,
        default=0.01,
        help="Minimum nonwhite ratio for segment retention (default 0.01)"
    )
    parser.add_argument(
        "--dense-split-when-missing",
        action="store_true",
        help="Split overbroad dense reference crops into repeated saturated visual blocks"
    )
    parser.add_argument(
        "--dense-split-min-expected-count",
        type=int,
        default=3,
        help="Minimum expected image count before dense reference splitting is considered"
    )
    parser.add_argument(
        "--dense-split-min-area-ratio",
        type=float,
        default=0.35,
        help="Minimum page area ratio for a crop to be considered overbroad"
    )
    parser.add_argument(
        "--dense-split-min-component-area-ratio",
        type=float,
        default=0.0015,
        help="Minimum page area ratio for dense split components"
    )
    parser.add_argument(
        "--dense-split-max-component-area-ratio",
        type=float,
        default=0.12,
        help="Maximum page area ratio for dense split components"
    )
    parser.add_argument(
        "--dense-split-saturation-threshold",
        type=int,
        default=35,
        help="HSV saturation threshold for dense split visual-block detection"
    )
    parser.add_argument(
        "--trim-caption",
        action="store_true",
        help="Trim caption text from bottom of detected image boxes"
    )
    parser.add_argument(
        "--caption-max-height-ratio",
        type=float,
        default=0.18,
        help="Max caption height as fraction of box height (default 0.18)"
    )
    parser.add_argument(
        "--caption-text-ratio-threshold",
        type=float,
        default=0.2,
        help="Row text ratio threshold for caption trimming (default 0.2)"
    )
    parser.add_argument(
        "--caption-margin-px",
        type=int,
        default=4,
        help="Extra margin to remove above detected caption line (default 4)"
    )
    parser.add_argument(
        "--caption-max-nonwhite-ratio",
        type=float,
        default=0.2,
        help="Skip caption trimming if bottom window has high nonwhite ratio (default 0.2)"
    )
    parser.add_argument(
        "--caption-trim-passes",
        type=int,
        default=1,
        help="Number of caption trim passes (default 1)"
    )
    parser.add_argument(
        "--caption-relax-max-gap-ratio",
        type=float,
        default=0.15,
        help="Max gap ratio to allow caption trim even if separated (default 0.15)"
    )

    args = parser.parse_args()

    manifest = crop_illustrations_guided(
        ocr_manifest=args.ocr_manifest,
        output_dir=args.output_dir,
        run_id=args.run_id,
        transparency=args.transparency,
        threshold=args.threshold,
        output_format=args.output_format,
        jpeg_quality=args.jpeg_quality,
        blur=args.blur,
        text_kernel=args.text_kernel,
        text_iterations=args.text_iterations,
        detection_mode=args.detection_mode,
        white_threshold=args.white_threshold,
        close_kernel=args.close_kernel,
        close_iterations=args.close_iterations,
        text_block_kernel_w=args.text_block_kernel_w,
        text_block_kernel_h=args.text_block_kernel_h,
        text_block_iterations=args.text_block_iterations,
        score_min_nonwhite=args.score_min_nonwhite,
        min_nonwhite_ratio=args.min_nonwhite_ratio,
        max_text_ratio=args.max_text_ratio,
        text_line_kernel_w=args.text_line_kernel_w,
        text_line_kernel_h=args.text_line_kernel_h,
        text_line_iterations=args.text_line_iterations,
        min_area_ratio=args.min_area_ratio,
        max_area_ratio=args.max_area_ratio,
        min_width=args.min_width,
        min_height=args.min_height,
        highres_manifest=args.highres_manifest,
        highres_images_dir=args.highres_images_dir,
        critical_graphics_manifest=args.critical_graphics_manifest,
        padding_percent=args.padding_percent,
        rescue_model=args.rescue_model,
        rescue_temperature=args.rescue_temperature,
        rescue_max_tokens=args.rescue_max_tokens,
        rescue_max_pages=args.rescue_max_pages,
        rescue_timeout_seconds=args.rescue_timeout_seconds,
        rescue_include_alt=args.rescue_include_alt,
        rescue_always=args.rescue_always,
        rescue_caption_second_pass=args.rescue_caption_second_pass,
        rescue_caption_max_tokens=args.rescue_caption_max_tokens,
        refine_with_nonwhite=args.refine_with_nonwhite,
        refine_close_kernel=args.refine_close_kernel,
        refine_close_iterations=args.refine_close_iterations,
        refine_with_nontext=args.refine_with_nontext,
        refine_with_textlines=args.refine_with_textlines,
        refine_textlines_min_area_ratio=args.refine_textlines_min_area_ratio,
        trim_text_edges=args.trim_text_edges,
        text_edge_max_ratio=args.text_edge_max_ratio,
        text_edge_margin_px=args.text_edge_margin_px,
        trim_ocr_text_edges=args.trim_ocr_text_edges,
        ocr_trim_edge_ratio=args.ocr_trim_edge_ratio,
        ocr_trim_min_conf=args.ocr_trim_min_conf,
        ocr_trim_min_word_len=args.ocr_trim_min_word_len,
        ocr_trim_min_line_words=args.ocr_trim_min_line_words,
        ocr_trim_min_line_chars=args.ocr_trim_min_line_chars,
        ocr_trim_max_ratio=args.ocr_trim_max_ratio,
        ocr_trim_margin_px=args.ocr_trim_margin_px,
        ocr_tesseract_cmd=args.ocr_tesseract_cmd,
        trim_layout_text=args.trim_layout_text,
        layout_text_model=args.layout_text_model,
        layout_text_score_thresh=args.layout_text_score_thresh,
        layout_text_max_gap_ratio=args.layout_text_max_gap_ratio,
        layout_text_bottom_band_ratio=args.layout_text_bottom_band_ratio,
        layout_text_top_band_ratio=args.layout_text_top_band_ratio,
        layout_text_margin_px=args.layout_text_margin_px,
        layout_text_min_width_ratio=args.layout_text_min_width_ratio,
        layout_text_max_height_ratio=args.layout_text_max_height_ratio,
        layout_split_text=args.layout_split_text,
        layout_split_min_gap_ratio=args.layout_split_min_gap_ratio,
        layout_split_margin_px=args.layout_split_margin_px,
        split_when_missing=args.split_when_missing,
        split_gap_ratio_threshold=args.split_gap_ratio_threshold,
        split_min_gap_px=args.split_min_gap_px,
        split_min_segment_height_ratio=args.split_min_segment_height_ratio,
        split_min_segment_nonwhite_ratio=args.split_min_segment_nonwhite_ratio,
        dense_split_when_missing=args.dense_split_when_missing,
        dense_split_min_expected_count=args.dense_split_min_expected_count,
        dense_split_min_area_ratio=args.dense_split_min_area_ratio,
        dense_split_min_component_area_ratio=args.dense_split_min_component_area_ratio,
        dense_split_max_component_area_ratio=args.dense_split_max_component_area_ratio,
        dense_split_saturation_threshold=args.dense_split_saturation_threshold,
        trim_caption=args.trim_caption,
        caption_max_height_ratio=args.caption_max_height_ratio,
        caption_text_ratio_threshold=args.caption_text_ratio_threshold,
        caption_margin_px=args.caption_margin_px,
        caption_max_nonwhite_ratio=args.caption_max_nonwhite_ratio,
        caption_trim_passes=args.caption_trim_passes,
        caption_relax_max_gap_ratio=args.caption_relax_max_gap_ratio,
        cover_pages=args.cover_pages,
        only_pages=args.only_pages,
    )

    # Save manifest — merge when --only-pages is active
    manifest_path = os.path.join(args.output_dir, "illustration_manifest.jsonl")
    if args.only_pages and os.path.exists(manifest_path):
        # Parse which pages were targeted
        targeted = set()
        for token in args.only_pages.split(","):
            token = token.strip()
            if token:
                try:
                    targeted.add(int(token))
                except ValueError:
                    pass
        # Keep existing entries for non-targeted pages, replace targeted pages
        existing = list(read_jsonl(manifest_path))
        merged = [r for r in existing if r.get("source_page") not in targeted]
        merged.extend(manifest)
        merged.sort(key=lambda r: (r.get("source_page", 0), r.get("filename", "")))
        save_jsonl(manifest_path, merged)
        _log(f"Merged {len(manifest)} new + {len(merged) - len(manifest)} existing = {len(merged)} total records")
    else:
        save_jsonl(manifest_path, manifest)
        keep_filenames = {
            str(row["filename"])
            for row in manifest
            if row.get("filename")
        }
        removed = _prune_stale_crop_images(
            os.path.join(args.output_dir, "images"),
            keep_filenames=keep_filenames,
        )
        if removed:
            _log(f"Removed {removed} stale crop images not present in the refreshed manifest")

    _log(f"Manifest: {manifest_path}")
    _log(f"Images: {os.path.join(args.output_dir, 'images')}")


if __name__ == "__main__":
    main()
