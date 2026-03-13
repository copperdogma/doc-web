import argparse
import base64
import io
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from modules.common.utils import read_jsonl, ensure_dir, append_jsonl, ProgressLogger

try:
    from PIL import Image
except Exception:  # pragma: no cover - optional dependency
    Image = None

try:
    from modules.common.openai_client import OpenAI
except Exception as exc:  # pragma: no cover - environment dependency
    OpenAI = None
    _OPENAI_IMPORT_ERROR = exc

try:
    from modules.common.google_client import GeminiVisionClient
except Exception as exc:  # pragma: no cover - environment dependency
    GeminiVisionClient = None
    _GEMINI_IMPORT_ERROR = exc

try:
    from modules.common.anthropic_client import AnthropicVisionClient
except Exception as exc:  # pragma: no cover - environment dependency
    AnthropicVisionClient = None
    _ANTHROPIC_IMPORT_ERROR = exc


def _is_gemini_model(model: str) -> bool:
    return model.startswith("gemini-")


def _is_anthropic_model(model: str) -> bool:
    return model.startswith("claude-")


ALLOWED_TAGS = {
    "h1", "h2", "h3", "p", "strong", "em", "ol", "ul", "li",
    "table", "thead", "tbody", "tr", "th", "td", "caption",
    "figure", "figcaption",
    "img", "dl", "dt", "dd", "a", "br",
}

RUNNING_HEAD_CLASS = "running-head"
PAGE_NUMBER_CLASS = "page-number"

SYSTEM_PROMPT = """You are an OCR engine for scanned book pages.

Return ONLY minimal HTML that preserves text and basic structure.

Allowed tags (only):
- Structural: <h1>, <h2>, <h3>, <p>, <dl>, <dt>, <dd>, <br>
- Emphasis: <strong>, <em>
- Lists: <ol>, <ul>, <li>
- Tables: <table>, <thead>, <tbody>, <tr>, <th>, <td>, <caption>
- Navigation: <a href="#123"> (use for explicit navigation choices like 'turn to 123')
- Running head / page number: <p class="running-head">, <p class="page-number">
- Figures: <figure>, <figcaption>, <img alt="..." data-count="N"> (placeholder only, no src)
- Metadata: <meta name="ocr-metadata" data-ocr-quality="0.0-1.0" data-ocr-integrity="0.0-1.0" data-continuation-risk="0.0-1.0">

Rules:
- Preserve exact wording, punctuation, and numbers.
- Reflow paragraphs (no hard line breaks within a paragraph).
- Navigation Links: Wrap the target number or the whole instruction in <a href="#N"> where N is the target section number (e.g., <a href="#55">turn to 55</a>).
- Keep running heads and page numbers if present (use the classed <p> tags above).
- Use <h2> for section numbers when they are clearly section headers.
- Use <h1> only for true page titles/headings.
- Use <dl> with <dt>/<dd> for inline label/value blocks (e.g., creature name + SKILL/STAMINA).
- Do not invent <section>, <div>, or <span>.
- When an illustration appears, wrap it in <figure> with <img alt="..."> and <figcaption> if a caption is visible. Place the <figure> at the semantically correct position in the reading flow (near the text it relates to). Example:
  <figure><img alt="Portrait of John Smith"><figcaption>John Smith, circa 1920</figcaption></figure>
  If there are multiple distinct illustrations on the page, use separate <figure> elements or add data-count="N" to the <img> (e.g., data-count="2" for 2 images grouped together). Omit data-count for single images. If no caption is visible, omit <figcaption>.
- Tables must be represented as a single <table> with headers/rows (no splitting).
- If uncertain, default to <p> with plain text.

Also include a single metadata tag as the FIRST line:
<meta name="ocr-metadata" data-ocr-quality="0.0-1.0" data-ocr-integrity="0.0-1.0" data-continuation-risk="0.0-1.0">

Metadata guidance:
- ocr-quality: 1.0 = crisp/easy to read; 0.0 = barely legible (blur/smudging/low contrast).
- ocr-integrity: 1.0 = complete/undistorted; 0.0 = severe cropping/warping/missing parts.
- continuation-risk: 1.0 = strong evidence of continuation (mid-sentence at top or cut-off at bottom); 0.0 = self-contained page.
- If you are confident the page is blank, set ocr-quality and ocr-integrity high (0.9–1.0) and continuation-risk low.

Output ONLY HTML, no Markdown, no code fences, no extra commentary."""


def build_system_prompt(hints: Optional[str]) -> str:
    if not hints:
        return SYSTEM_PROMPT
    return SYSTEM_PROMPT + "\n\nRecipe hints:\n" + hints.strip() + "\n"


def _resize_image_bytes(image_bytes: bytes, max_long_side: int, mime: str) -> tuple:
    """Resize image if either dimension exceeds max_long_side. Returns (bytes, mime, resized_flag)."""
    if Image is None or max_long_side <= 0:
        return image_bytes, mime, False
    img = Image.open(io.BytesIO(image_bytes))
    w, h = img.size
    long_side = max(w, h)
    if long_side <= max_long_side:
        return image_bytes, mime, False
    scale = max_long_side / long_side
    new_w = int(w * scale)
    new_h = int(h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue(), "image/jpeg", True


def _is_blank_page(image_bytes: bytes, threshold: float = 0.99) -> bool:
    """Check if an image is blank enough to skip OCR safely.

    The detector is intentionally conservative: sparse-text pages with large
    white regions should still be OCRed. We therefore evaluate a thumbnail and
    require both a very high white ratio and almost no dark ink.
    """
    if Image is None:
        return False
    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    img.thumbnail((256, 256))
    pixels = list(img.getdata())
    if not pixels:
        return True
    white_ratio = sum(1 for p in pixels if p >= 245) / len(pixels)
    if white_ratio < threshold:
        return False
    ink_ratio = sum(1 for p in pixels if p <= 220) / len(pixels)
    return ink_ratio < 0.002


def _utc() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _extract_code_fence(text: str) -> str:
    if "```" not in text:
        return text
    parts = text.split("```")
    if len(parts) >= 3:
        return parts[1].strip()
    return text.replace("```", "").strip()

def _extract_ocr_metadata(raw_html: str) -> (str, dict, Optional[str], Optional[str]):
    if not raw_html:
        return raw_html, {}, None, None
    # Expect metadata tag on the first line; strip it before sanitizing.
    lines = raw_html.lstrip().splitlines()
    if not lines:
        return raw_html, {}, None, None
    tag = None
    tag_index = None
    for i, line in enumerate(lines[:5]):
        candidate = line.strip()
        if candidate.lower().startswith("<meta") and re.search(r"name\s*=\s*['\"]ocr-metadata['\"]", candidate, re.IGNORECASE):
            tag = candidate
            tag_index = i
            break
    if tag is None:
        return raw_html, {}, None, None
    def _attr(name: str) -> Optional[float]:
        m_attr = re.search(rf"\b{name}\s*=\s*[\"']([^\"']+)[\"']", tag, re.IGNORECASE)
        if not m_attr:
            return None
        try:
            val = float(m_attr.group(1))
        except Exception:
            return None
        if val < 0:
            return 0.0
        if val > 1:
            return 1.0
        return val
    meta = {
        "ocr_quality": _attr("data-ocr-quality"),
        "ocr_integrity": _attr("data-ocr-integrity"),
        "continuation_risk": _attr("data-continuation-risk"),
    }
    if tag_index is not None:
        del lines[tag_index]
    cleaned = "\n".join(lines)
    warning = None
    if tag_index is not None and tag_index != 0:
        warning = f"ocr_metadata_not_first_line:{tag_index}"
    return cleaned.strip(), meta, tag, warning


class TagSanitizer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out: List[str] = []

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()
        if tag not in ALLOWED_TAGS:
            return
        if tag == "img":
            alt = ""
            count = ""
            for k, v in attrs:
                if k.lower() == "alt":
                    alt = v or ""
                elif k.lower() == "data-count":
                    count = v or ""
            if count:
                self.out.append(f"<img alt=\"{alt}\" data-count=\"{count}\">")
            else:
                self.out.append(f"<img alt=\"{alt}\">")
            return
        if tag == "br":
            self.out.append("<br>")
            return
        if tag == "a":
            href = ""
            for k, v in attrs:
                if k.lower() == "href":
                    href = v or ""
                    break
            # Only keep internal fragments (like #123)
            if href.startswith("#"):
                self.out.append(f"<a href=\"{href}\">")
            else:
                self.out.append("<a>")
            return
        if tag == "p":
            cls = None
            for k, v in attrs:
                if k.lower() == "class":
                    cls = v
                    break
            if cls in (RUNNING_HEAD_CLASS, PAGE_NUMBER_CLASS):
                self.out.append(f"<p class=\"{cls}\">")
            else:
                self.out.append("<p>")
            return
        self.out.append(f"<{tag}>")

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag in ALLOWED_TAGS and tag not in {"img", "br"}:
            self.out.append(f"</{tag}>")

    def handle_data(self, data: str):
        if data:
            self.out.append(data)

    def get_html(self) -> str:
        html = "".join(self.out)
        html = re.sub(r"\s+", " ", html)
        html = re.sub(r">\s+<", ">\n<", html)
        return html.strip() + "\n"


def sanitize_html(html: str) -> str:
    parser = TagSanitizer()
    parser.feed(html)
    return parser.get_html()


def extract_image_metadata(html: str) -> List[dict]:
    """Extract illustration metadata from HTML img tags.

    Returns list of dicts with keys: alt, count (number of images, default 1).
    """
    images = []
    # Match img tags with optional data-count
    pattern_with_count = r'<img\s+alt="([^"]*)"\s+data-count="(\d+)">'
    pattern_simple = r'<img\s+alt="([^"]*)">'

    # First find all img tags with data-count
    found_positions = set()
    for match in re.finditer(pattern_with_count, html):
        alt = match.group(1)
        count = int(match.group(2))
        images.append({
            "alt": alt,
            "count": count
        })
        found_positions.add(match.start())

    # Then find simple img tags (without data-count)
    for match in re.finditer(pattern_simple, html):
        if match.start() not in found_positions:
            # Check it's not part of a data-count tag we already found
            full_match = html[match.start():match.start()+100]
            if 'data-count=' not in full_match:
                alt = match.group(1)
                images.append({
                    "alt": alt,
                    "count": 1
                })

    return images


def _call_vision_model(
    model: str,
    system_prompt: str,
    user_text: str,
    data_uri: str,
    temperature: float,
    max_output_tokens: int,
    *,
    openai_client=None,
    gemini_client=None,
    anthropic_client=None,
) -> Tuple[str, Optional[object], Optional[str]]:
    """Run one OCR request against the provider implied by the model name."""
    if _is_anthropic_model(model):
        if anthropic_client is None:
            raise RuntimeError("anthropic package required for Claude models")
        return anthropic_client.generate_vision(
            model=model,
            system_prompt=system_prompt,
            user_text=user_text,
            image_data=data_uri,
            temperature=temperature,
            max_tokens=max_output_tokens,
        )
    if _is_gemini_model(model):
        if gemini_client is None:
            raise RuntimeError("google-genai package required for Gemini models")
        return gemini_client.generate_vision(
            model=model,
            system_prompt=system_prompt,
            user_text=user_text,
            image_data=data_uri,
            temperature=temperature,
            max_tokens=max_output_tokens,
        )
    if openai_client is None:
        raise RuntimeError("openai package required")
    if hasattr(openai_client, "responses"):
        resp = openai_client.responses.create(
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": user_text},
                        {"type": "input_image", "image_url": data_uri},
                    ],
                },
            ],
        )
        return resp.output_text or "", getattr(resp, "usage", None), getattr(resp, "id", None)
    resp = openai_client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_completion_tokens=max_output_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            },
        ],
    )
    return resp.choices[0].message.content or "", getattr(resp, "usage", None), getattr(resp, "id", None)


def _ocr_with_fallback(
    image_bytes: bytes,
    image_path: str,
    *,
    model: str,
    retry_model: Optional[str],
    system_prompt: str,
    user_text: str,
    temperature: float,
    max_output_tokens: int,
    openai_client=None,
    gemini_client=None,
    anthropic_client=None,
) -> Tuple[str, str, Dict[str, float], Optional[str], Optional[str], Optional[str]]:
    """OCR a page, retrying once on empty output.

    The retry can use either the same model (preserving the legacy second
    attempt) or a stronger provider-specific model when `retry_model` is set.
    Returns stripped raw HTML, sanitized HTML, metadata, metadata tag/warning,
    and the model that produced the kept output.
    """
    mime = "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_uri = f"data:{mime};base64,{b64}"

    model_sequence = [model, retry_model or model]
    last_raw = ""
    last_cleaned = ""
    last_meta: Dict[str, float] = {}
    last_meta_tag = None
    last_meta_warning = None
    last_model_used = None

    for selected_model in model_sequence:
        try:
            raw, _usage, _request_id = _call_vision_model(
                selected_model,
                system_prompt,
                user_text,
                data_uri,
                temperature,
                max_output_tokens,
                openai_client=openai_client,
                gemini_client=gemini_client,
                anthropic_client=anthropic_client,
            )
        except Exception as exc:
            raise RuntimeError(f"OCR failed on page image {image_path}: {exc}") from exc
        raw = _extract_code_fence(raw)
        raw, meta, meta_tag, meta_warning = _extract_ocr_metadata(raw)
        cleaned = sanitize_html(raw)
        last_raw = raw
        last_cleaned = cleaned
        last_meta = meta
        last_meta_tag = meta_tag
        last_meta_warning = meta_warning
        last_model_used = selected_model
        if cleaned.strip():
            return raw, cleaned, meta, meta_tag, meta_warning, selected_model

    return last_raw, last_cleaned, last_meta, last_meta_tag, last_meta_warning, last_model_used


def resolve_manifest_path(args) -> Path:
    if args.pages:
        return Path(args.pages)
    if args.inputs:
        return Path(args.inputs[0])
    raise SystemExit("Missing --pages or --inputs manifest path")


def main() -> None:
    parser = argparse.ArgumentParser(description="GPT-5.1 OCR to per-page HTML")
    parser.add_argument("--pages", help="Path to page_image_v1 manifest JSONL")
    parser.add_argument("--pdf", help="Ignored (driver compatibility)")
    parser.add_argument("--images", help="Ignored (driver compatibility)")
    parser.add_argument("--inputs", nargs="*", help="Driver-provided inputs")
    parser.add_argument("--outdir", help="Output directory")
    parser.add_argument("--out", default="pages_html.jsonl", help="Output JSONL filename")
    parser.add_argument("--model", default="gpt-5.1")
    parser.add_argument("--max-output-tokens", dest="max_output_tokens", type=int, default=4096)
    parser.add_argument("--max_output_tokens", dest="max_output_tokens", type=int, default=4096)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--allow-empty", dest="allow_empty", action="store_true")
    parser.add_argument("--retry-model", dest="retry_model", default=None,
                        help="Optional stronger model to retry with when OCR returns empty HTML")
    parser.add_argument("--retry_model", dest="retry_model", default=None)
    parser.add_argument("--ocr-hints", dest="ocr_hints", help="Recipe-level OCR hints text")
    parser.add_argument("--ocr_hints", dest="ocr_hints", help="Recipe-level OCR hints text")
    parser.add_argument("--max-long-side", dest="max_long_side", type=int, default=0,
                        help="Downsample images so longest side <= N pixels (0=disabled)")
    parser.add_argument("--max_long_side", dest="max_long_side", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=1,
                        help="Number of parallel API calls (1=sequential)")
    parser.add_argument("--skip-blank-pages", dest="skip_blank_pages", action="store_true",
                        help="Skip near-white pages without API call")
    parser.add_argument("--skip_blank_pages", dest="skip_blank_pages", action="store_true")
    parser.add_argument("--blank-threshold", dest="blank_threshold", type=float, default=0.99,
                        help="Fraction of near-white pixels to consider blank")
    parser.add_argument("--blank_threshold", dest="blank_threshold", type=float, default=0.99)
    parser.add_argument("--force", action="store_true", help="Overwrite existing output")
    parser.add_argument("--resume", action="store_true", help="Skip pages already written (default)")
    parser.set_defaults(resume=True)
    parser.add_argument("--progress-file")
    parser.add_argument("--state-file")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    try:
        manifest_path = resolve_manifest_path(args)
        if not manifest_path.exists():
            raise SystemExit(f"Manifest not found: {manifest_path}")

        if not args.outdir:
            args.outdir = str(manifest_path.parent)
        ensure_dir(args.outdir)
        out_path = Path(args.outdir) / args.out if not os.path.isabs(args.out) else Path(args.out)

        rows = list(read_jsonl(str(manifest_path)))
        total = len(rows)
        if total == 0:
            raise SystemExit(f"Manifest is empty: {manifest_path}")

        logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
        logger.log(
            "extract",
            "running",
            current=0,
            total=total,
            message=f"Running OCR to HTML (model={args.model})",
            artifact=str(out_path),
            module_id="ocr_ai_gpt51_v1",
            schema_version="page_html_v1",
        )

        needs_anthropic = any(_is_anthropic_model(m) for m in [args.model, args.retry_model] if m)
        needs_gemini = any(_is_gemini_model(m) for m in [args.model, args.retry_model] if m)
        needs_openai = any(
            m and not _is_gemini_model(m) and not _is_anthropic_model(m)
            for m in [args.model, args.retry_model]
        )

        if needs_anthropic:
            if AnthropicVisionClient is None:
                raise RuntimeError("anthropic package required for Claude models") from _ANTHROPIC_IMPORT_ERROR
            anthropic_client = AnthropicVisionClient()
        else:
            anthropic_client = None
        if needs_gemini:
            if GeminiVisionClient is None:
                raise RuntimeError("google-genai package required for Gemini models") from _GEMINI_IMPORT_ERROR
            gemini_client = GeminiVisionClient()
        else:
            gemini_client = None
        if needs_openai:
            if OpenAI is None:
                raise RuntimeError("openai package required") from _OPENAI_IMPORT_ERROR
            openai_client = OpenAI()
        else:
            openai_client = None
        system_prompt = build_system_prompt(args.ocr_hints)
        if out_path.exists() and args.force:
            out_path.unlink()

        completed_pages = set()
        if out_path.exists() and args.resume:
            try:
                for row in read_jsonl(str(out_path)):
                    pn = row.get("page_number")
                    if pn is not None:
                        completed_pages.add(pn)
            except Exception:
                completed_pages = set()

        # --- Per-page processing function (called sequentially or in parallel) ---
        def _process_one_page(page, idx):
            """Process a single page and return the output row dict."""
            image_path = page.get("image")
            if not image_path or not os.path.exists(image_path):
                raise SystemExit(f"Missing image for page: {page}")

            page_number = page.get("page_number")
            image_bytes = Path(image_path).read_bytes()

            # A6: Blank page detection
            if args.skip_blank_pages and _is_blank_page(image_bytes, args.blank_threshold):
                return {
                    "schema_version": "page_html_v1",
                    "module_id": "ocr_ai_gpt51_v1",
                    "run_id": args.run_id,
                    "source": page.get("source"),
                    "created_at": _utc(),
                    "page": page.get("page"),
                    "page_number": page_number,
                    "original_page_number": page.get("original_page_number"),
                    "image": image_path,
                    "spread_side": page.get("spread_side"),
                    "html": "",
                    "raw_html": "",
                    "ocr_empty": True,
                    "ocr_empty_reason": "blank_page_detected",
                }

            # A1: Image downsampling
            mime = "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
            if args.max_long_side > 0:
                image_bytes, mime, _resized = _resize_image_bytes(image_bytes, args.max_long_side, mime)

            meta = {}
            meta_tag = None
            meta_warning = None
            cleaned = ""
            user_text = "Return HTML only. FIRST line MUST be: <meta name=\"ocr-metadata\" data-ocr-quality=\"0.0-1.0\" data-ocr-integrity=\"0.0-1.0\" data-continuation-risk=\"0.0-1.0\">"
            raw, cleaned, meta, meta_tag, meta_warning, _model_used = _ocr_with_fallback(
                image_bytes,
                image_path,
                model=args.model,
                retry_model=args.retry_model,
                system_prompt=system_prompt,
                user_text=user_text,
                temperature=args.temperature,
                max_output_tokens=args.max_output_tokens,
                openai_client=openai_client,
                gemini_client=gemini_client,
                anthropic_client=anthropic_client,
            )

            empty_msg = None
            if not cleaned.strip():
                empty_msg = f"Empty HTML output for page {page_number}"
                cleaned = ""

            row = {
                "schema_version": "page_html_v1",
                "module_id": "ocr_ai_gpt51_v1",
                "run_id": args.run_id,
                "source": page.get("source"),
                "created_at": _utc(),
                "page": page.get("page"),
                "page_number": page_number,
                "original_page_number": page.get("original_page_number"),
                "image": image_path,
                "spread_side": page.get("spread_side"),
            }
            if meta:
                row.update({k: v for k, v in meta.items() if v is not None})
            if meta_warning:
                row["ocr_metadata_warning"] = meta_warning
            if meta_tag and not all(v is not None for v in meta.values()):
                row["ocr_metadata_tag"] = meta_tag
            if not meta_tag:
                row["ocr_metadata_missing"] = True
            row["html"] = cleaned

            images = extract_image_metadata(cleaned)
            if images:
                row["images"] = images

            if empty_msg:
                row["ocr_empty"] = True
                row["ocr_empty_reason"] = empty_msg
            row["raw_html"] = raw
            return row

        # --- Build work list (skip completed pages) ---
        work = []
        for idx, page in enumerate(rows, start=1):
            page_number = page.get("page_number")
            if page_number in completed_pages:
                logger.log(
                    "extract", "running", current=idx, total=total,
                    message=f"Skipping page {page_number} (already completed)",
                    artifact=str(out_path), module_id="ocr_ai_gpt51_v1",
                    schema_version="page_html_v1",
                )
                continue
            work.append((idx, page))

        # --- Execute: parallel or sequential ---
        concurrency = max(1, args.concurrency)
        write_lock = threading.Lock()
        completed_count = total - len(work)  # already-done pages

        if concurrency <= 1:
            # Sequential (original behavior)
            for idx, page in work:
                row = _process_one_page(page, idx)
                append_jsonl(str(out_path), row)
                completed_count += 1
                logger.log(
                    "extract", "running", current=completed_count, total=total,
                    message=f"OCR HTML for page {page.get('page_number')}"
                    + (" [blank]" if row.get("ocr_empty_reason") == "blank_page_detected" else ""),
                    artifact=str(out_path), module_id="ocr_ai_gpt51_v1",
                    schema_version="page_html_v1",
                )
        else:
            # A2: Parallel execution
            results = []
            errors = []

            def _submit_with_delay(executor, fn, items, delay_ms):
                """Submit work items with optional delay between submissions for rate limiting."""
                futures = {}
                for i, (idx, page) in enumerate(items):
                    f = executor.submit(fn, page, idx)
                    futures[f] = (idx, page)
                    if delay_ms > 0 and i < len(items) - 1:
                        time.sleep(delay_ms / 1000.0)
                return futures

            rate_delay_ms = 200 if concurrency > 5 else 0
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = _submit_with_delay(executor, _process_one_page, work, rate_delay_ms)
                for future in as_completed(futures):
                    idx, page = futures[future]
                    try:
                        row = future.result()
                        results.append((idx, row))
                        with write_lock:
                            completed_count += 1
                            logger.log(
                                "extract", "running", current=completed_count, total=total,
                                message=f"OCR HTML for page {page.get('page_number')}"
                                + (" [blank]" if row.get("ocr_empty_reason") == "blank_page_detected" else ""),
                                artifact=str(out_path), module_id="ocr_ai_gpt51_v1",
                                schema_version="page_html_v1",
                            )
                    except Exception as exc:
                        errors.append((page.get("page_number"), str(exc)))
                        logger.log(
                            "extract", "failed", current=idx, total=total,
                            message=f"OCR failed on page {page.get('page_number')}: {exc}",
                            artifact=str(out_path), module_id="ocr_ai_gpt51_v1",
                            schema_version="page_html_v1",
                        )

            if errors:
                raise RuntimeError(f"OCR failed on {len(errors)} page(s): {errors}")

            # Write results sorted by original page order
            results.sort(key=lambda x: x[0])
            for _idx, row in results:
                append_jsonl(str(out_path), row)

        logger.log(
            "extract",
            "done",
            current=total,
            total=total,
            message="GPT-5.1 OCR HTML complete",
            artifact=str(out_path),
            module_id="ocr_ai_gpt51_v1",
            schema_version="page_html_v1",
            extra={"summary_metrics": {"pages_processed_count": total}},
        )
    except Exception as exc:
        logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
        logger.log(
            "extract",
            "failed",
            message=f"Unhandled OCR failure: {exc}",
            module_id="ocr_ai_gpt51_v1",
            schema_version="page_html_v1",
        )
        raise


if __name__ == "__main__":
    main()
