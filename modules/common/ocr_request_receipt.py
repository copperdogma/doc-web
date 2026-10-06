"""Inspectable bounded OCR request receipts without storing image payloads."""
import base64
import hashlib
import re
import time


def request_receipt(response, kwargs, started):
    usage = getattr(response, "usage", None)
    record = {
        "schema_version": "ocr_request_receipt_v1",
        "requested_model": kwargs["model"],
        "served_model": getattr(response, "model", None),
        "response_id": getattr(response, "id", None),
        "status": getattr(response, "status", None),
        "max_output_tokens": kwargs["max_output_tokens"],
        "reasoning": kwargs.get("reasoning"),
        "elapsed_seconds": time.monotonic() - started,
        "usage": usage.model_dump() if hasattr(usage, "model_dump") else usage,
    }
    for message in kwargs["input"]:
        for item in message["content"]:
            if message["role"] == "system" and item["type"] == "input_text":
                record["prompt_sha256"] = hashlib.sha256(item["text"].encode()).hexdigest()
            if item["type"] == "input_image":
                encoded = item["image_url"].split(",", 1)[1]
                record["submitted_image_sha256"] = hashlib.sha256(base64.b64decode(encoded)).hexdigest()
                record["image_detail"] = item.get("detail", "auto")
    return record


def require_completed_identity(record):
    if record["status"] != "completed":
        raise RuntimeError("OCR response incomplete or status unavailable; inspect request receipt")
    expected, actual = record["requested_model"], record["served_model"] or ""
    if actual != expected and not re.fullmatch(re.escape(expected) + r"-20\d{2}-\d{2}-\d{2}", actual):
        raise RuntimeError("OCR served model identity mismatch; inspect request receipt")
