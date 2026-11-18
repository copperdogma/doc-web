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


MODEL = "gpt-6.2-sol"
PROFILE = "openai-native-sol62-source-only-medium-v1"
OUTPUT_LIMIT = 32_768
INPUT_LIMIT = 26_000
RESERVE_USD = 0.5


class SourceOnlyReader:
    """One dispatch per invocation; reserve before calling, preserve failures."""

    def __init__(self, max_requests=3, budget_usd=1.5, ledger_path=None, client=None):
        if max_requests < 1 or budget_usd <= 0:
            raise ValueError("Positive request and reservation caps required")
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
        if width * height > 25_000_000 or len(data) > 20 * 1024 * 1024:
            raise ValueError("Source image exceeds bounded review size")
        # Conservative reservation, not billed cost. Usage remains in receipts.
        reserve = RESERVE_USD
        if len(self.entries) >= self.max_requests or (len(self.entries) + 1) * reserve > self.budget_usd:
            raise RuntimeError("Source-review request/reservation cap reached")
        schema = SourcePageReview.model_json_schema()
        kwargs = source_request(image_path)
        count_contract = {key: kwargs[key] for key in ("model", "input", "text", "reasoning")}
        input_count = self.client.responses.count_input_tokens(**count_contract)
        if type(input_count) is not int or not 0 < input_count <= INPUT_LIMIT:
            raise ValueError("Source review exceeds the Sol 6.2 request reservation")
        entry = {"submitted_image_sha256": hashlib.sha256(data).hexdigest(),
                 "reserve_usd": reserve, "status": "reserved"}
        entry["exact_input_tokens_before_dispatch"] = input_count
        self.entries.append(entry)
        self._save_ledger()
        started = time.monotonic()
        record = {**entry, "requested_model": MODEL}
        requests.append(record)
        try:
            native = self.client.responses.with_raw_response.create(**kwargs)
            raw = native.content
            if self.ledger_path:
                native_path = self.ledger_path.parent / f"openai-source-response-{len(self.entries):03d}.json"
                with native_path.open("xb") as stream:
                    stream.write(raw)
            record["provider"] = "openai"
            record["authority_profile"] = PROFILE
            record["native_response_sha256"] = hashlib.sha256(raw).hexdigest()
            record["native_response_json"] = raw.decode("utf-8")
            response = native.parse()
            record.update(request_receipt(response, kwargs, started))
            record["response_schema_sha256"] = hashlib.sha256(
                json.dumps(schema, sort_keys=True).encode()).hexdigest()
            record["raw_response"] = response.output_text
            record["service_tier"] = getattr(response, "service_tier", None)
            record["request_sha256"] = hashlib.sha256(json.dumps(kwargs, sort_keys=True).encode()).hexdigest()
            record["usage"] = json.loads(raw).get("usage")
            if (record["usage"] or {}).get("input_tokens") != input_count:
                raise RuntimeError("Source-reader billed input differs from its preflight count")
            require_completed_identity(record)
            result = validate_source_record(record, image_sha256=record["submitted_image_sha256"], image_path=image_path)
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
                "calls": len(self.entries), "reserved_usd": len(self.entries) * RESERVE_USD,
                "entries": self.entries,
            }, indent=2) + "\n")


def source_request(image_path):
    """Inspectable maintained request shared by reader and zero-inference preflight."""
    path = Path(image_path)
    data = path.read_bytes()
    with Image.open(path) as image:
        width, height = image.size
        mime = Image.MIME[image.format]
    return {
        "model": MODEL, "max_output_tokens": OUTPUT_LIMIT, "store": False, "service_tier": "default",
        "reasoning": {"effort": "medium"},
        "text": {"format": {"type": "json_schema", "name": "source_page_tables",
                              "strict": True, "schema": SourcePageReview.model_json_schema()}},
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": POLICY}]},
            {"role": "user", "content": [
                {"type": "input_text", "text": f"Source image dimensions: {width} x {height} pixels. Read source tables; return JSON only."},
                {"type": "input_image", "detail": "original", "image_url":
                 f"data:{mime};base64," + base64.b64encode(data).decode("ascii")},
            ]},
        ],
    }


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_source_record(record, *, image_sha256, image_path):
    """Bind a Sol source receipt to its native envelope, request and page bytes."""
    if record.get("requested_model") != MODEL:
        raise ValueError("Source-read authority does not match selected reader")
    if record.get("submitted_image_sha256") != image_sha256:
        raise ValueError("Source-read image identity mismatch")
    if (
        record.get("prompt_sha256") != digest(POLICY.encode())
        or record.get("response_schema_sha256") != digest(json.dumps(SourcePageReview.model_json_schema(), sort_keys=True).encode())
    ):
        raise ValueError("Source-read policy/schema changed")
    if (
        record.get("provider") != "openai"
        or record.get("authority_profile") != PROFILE
    ):
        raise ValueError("Unqualified OpenAI source-read authority profile")
    require_completed_identity(record)
    if record.get("served_model") != MODEL:
        raise ValueError("Source-read must serve the qualified 6.2 identity")
    if (
        record.get("image_detail") != "original"
        or record.get("reasoning") != {"effort": "medium"}
        or record.get("service_tier") != "default"
    ):
        raise ValueError("Unqualified Sol source-read configuration")
    raw = record.get("raw_response") or ""
    native = record.get("native_response_json") or ""
    if digest(native.encode()) != record.get("native_response_sha256"):
        raise ValueError("Source-read raw native envelope changed")
    data = json.loads(native)
    if (
        data.get("object") != "response"
        or not isinstance(data.get("id"), str)
        or not data["id"].strip()
        or data.get("model") != record.get("served_model")
        or data.get("status") != "completed"
        or data.get("error")
        or data.get("incomplete_details")
        or data.get("service_tier") != "default"
        or data.get("id") != record.get("response_id")
        or data.get("usage") != record.get("usage")
    ):
        raise ValueError("Source-read receipt differs from native raw response")
    usage = data.get("usage")
    if not isinstance(usage, dict) or any(
        type(usage.get(k)) is not int or usage[k] < 0
        for k in ("input_tokens", "output_tokens")
    ):
        raise ValueError("Source-read native usage missing/invalid")
    native_format = (data.get("text") or {}).get("format") or {}
    if (
        not 0 < usage["input_tokens"] <= INPUT_LIMIT
        or type(record.get("exact_input_tokens_before_dispatch")) is not int
        or record["exact_input_tokens_before_dispatch"] != usage["input_tokens"]
        or (data.get("reasoning") or {}).get("effort") != "medium"
        or data.get("max_output_tokens") != OUTPUT_LIMIT
        or data.get("store") is not False
        or native_format.get("type") != "json_schema"
        or native_format.get("name") != "source_page_tables"
        or native_format.get("strict") is not True
        or native_format.get("schema") != SourcePageReview.model_json_schema()
    ):
        raise ValueError("Sol source-read native contract or input-count mismatch")
    if usage["output_tokens"] > OUTPUT_LIMIT:
        raise ValueError("Source-read native output allowance exceeded")
    messages = [item for item in data.get("output", []) if item.get("type") != "reasoning"]
    if len(messages) != 1:
        raise ValueError("Source-read native final output incomplete/ambiguous")
    message = messages[0]
    content = message.get("content") or []
    if (
        message.get("type") != "message"
        or message.get("role") != "assistant"
        or message.get("status") != "completed"
        or len(content) != 1
        or content[0].get("type") != "output_text"
        or not isinstance(content[0].get("text"), str)
        or not content[0]["text"].strip()
        or content[0]["text"] != raw
        or record.get("max_output_tokens") != OUTPUT_LIMIT
    ):
        raise ValueError("Source-read native final output/configuration differs from the receipt")
    if (
        image_path is None
        or not Path(image_path).is_file()
        or Path(image_path).is_symlink()
    ):
        raise ValueError("Native Sol source review requires actual bound image")
    if digest(Path(image_path).read_bytes()) != image_sha256 or record.get(
        "request_sha256"
    ) != digest(json.dumps(source_request(image_path), sort_keys=True).encode()):
        raise ValueError(
            "Source-read native request differs from selected policy/image/schema"
        )
    return SourcePageReview.model_validate_json(raw)


class RetainedSourceOnlyReader:
    """Consume individually generated native receipts without re-inference."""

    def __init__(self, manifest_path):
        manifest = json.loads(Path(manifest_path).read_text())
        if (
            manifest.get("model") != MODEL
            or manifest.get("schema_version") != "retained_source_reviews_v1"
        ):
            raise ValueError("Retained source-review profile mismatch")
        self.records, self.used = {}, set()
        for entry in manifest["records"]:
            key = entry["image_sha256"]
            if key in self.records:
                raise ValueError("Duplicate retained source image")
            path = Path(entry["record_path"])
            if (
                not path.is_file()
                or path.is_symlink()
                or digest(path.read_bytes()) != entry["record_sha256"]
            ):
                raise ValueError("Retained source-review record changed/missing")
            record = json.loads(path.read_text())
            if record.get("requested_model") != MODEL or record.get("authority_profile") != PROFILE:
                raise ValueError("Retained source review requires the qualified Sol authority")
            self.records[key] = record

    def __call__(self, image_path, requests):
        key = digest(Path(image_path).read_bytes())
        if key in self.used or key not in self.records:
            raise ValueError("Missing or repeated retained source review")
        self.used.add(key)
        record = self.records[key]
        result = validate_source_record(
            record, image_sha256=key, image_path=image_path
        )
        requests.append(record)
        return result
