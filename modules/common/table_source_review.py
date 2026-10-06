"""Source-only literal table reading; no OCR or native text in requests."""


import base64
import hashlib
import json
from pathlib import Path
import time

from PIL import Image

from doc_web.literal_fidelity import SourcePageReview
from modules.common.openai_client import OpenAI
from modules.common.ocr_request_receipt import request_receipt, require_completed_identity

POLICY = 'Read every table directly from the supplied source page image. This is literal transcription, not correction of what the author intended. Preserve exact character case, punctuation, apparent typos, empty cells, dashes, modifiers, repeated values and row/column spans. Do not infer identifiers/references or copy repeated values to resolve a glyph. If character interpretations cannot be distinguished from the visible pixels in this font, mark that cell uncertain; do not force a guess. Blur, cropping and unclear cell ownership also require uncertainty. State visually plausible alternatives if possible. A confident-looking token or coherent wording is not source evidence.\nReturn ONLY one JSON object with exactly: {"source_table_count":integer,"tables":[{"bbox":[left,top,right,bottom],"html":"one complete minimal HTML table","uncertain_cells":[{"row":zero-based row index,"cell":zero-based explicit cell index,"reason":"source ambiguity","alternatives":["possible complete cell text"]}]}]}. Include every visible table once in source reading order, including table headers and spanning cells. Bbox coordinates are source image pixels. HTML includes table/thead/tbody/tr/th/td and safe positive rowspan/colspan; preserve literal entities with HTML escaping. For an uncertain cell retain a best observed transcription in HTML solely as diagnostic, and list uncertainty explicitly. No comments, Markdown or outside-table prose. If the image contains no tables return source_table_count0 and emptytables. Never return an uncertain cell as verified by choosing the most plausible spelling.'


class SourceOnlyReader:
    """One dispatch per invocation; reserve before calling, preserve failures."""

    def __init__(self, model="gpt-6-astra", max_requests=10, budget_usd=15.0,
                 ledger_path=None, client=None):
        if model != "gpt-6-astra":
            raise ValueError("This evaluated source-review policy requires gpt-6-astra")
        if max_requests < 1 or budget_usd <= 0:
            raise ValueError("Positive request and reservation caps required")
        self.model = model
        self.max_requests = max_requests
        self.budget_usd = budget_usd
        self.ledger_path = Path(ledger_path) if ledger_path else None
        self.client = client or OpenAI(max_retries=0, timeout=180)
        self.entries = []
        if self.ledger_path and self.ledger_path.exists():
            raise ValueError("Fresh source-review ledger required")

    def __call__(self, image_path, requests):
        path = Path(image_path)
        data = path.read_bytes()
        with Image.open(path) as image:
            width, height = image.size
            mime = Image.MIME[image.format]
        if width * height > 25_000_000 or len(data) > 20 * 1024 * 1024:
            raise ValueError("Source image exceeds bounded review size")
        # Conservative reservation, not billed cost. Usage remains in receipts.
        reserve = 1.5
        if len(self.entries) >= self.max_requests or (len(self.entries) + 1) * reserve > self.budget_usd:
            raise RuntimeError("Source-review request/reservation cap reached")
        schema = SourcePageReview.model_json_schema()
        kwargs = {
            "model": self.model, "max_output_tokens": 8192, "store": False,
            "reasoning": {"effort": "medium"},
            "text": {"format": {"type": "json_schema", "name": "source_page_tables",
                                  "strict": True, "schema": schema}},
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": POLICY}]},
                {"role": "user", "content": [
                    {"type": "input_text", "text": f"Source image dimensions: {width} x {height} pixels. Read source tables; return JSON only."},
                    {"type": "input_image", "detail": "original", "image_url":
                     f"data:{mime};base64," + base64.b64encode(data).decode("ascii")},
                ]},
            ],
        }
        entry = {"submitted_image_sha256": hashlib.sha256(data).hexdigest(),
                 "reserve_usd": reserve, "status": "reserved"}
        self.entries.append(entry)
        self._save_ledger()
        started = time.monotonic()
        record = {**entry, "requested_model": self.model}
        requests.append(record)
        try:
            response = self.client.responses.create(**kwargs)
            record.update(request_receipt(response, kwargs, started))
            record["response_schema_sha256"] = hashlib.sha256(
                json.dumps(schema, sort_keys=True).encode()).hexdigest()
            record["raw_response"] = response.output_text
            require_completed_identity(record)
            result = SourcePageReview.model_validate_json(response.output_text)
            entry["status"] = "completed"
            return result
        except Exception as exc:
            record["error_type"] = type(exc).__name__
            entry["status"] = "failed"
            raise
        finally:
            entry["elapsed_seconds"] = time.monotonic() - started
            self._save_ledger()

    def _save_ledger(self):
        if self.ledger_path:
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            self.ledger_path.write_text(json.dumps({
                "call_cap": self.max_requests, "reserve_cap_usd": self.budget_usd,
                "calls": len(self.entries), "reserved_usd": len(self.entries) * 1.5,
                "entries": self.entries,
            }, indent=2) + "\n")
