"""Explicit native Google source reader and immutable receipt consumption."""

import base64
import hashlib
import json
from pathlib import Path
import time

import httpx
from PIL import Image

from doc_web.env import get_doc_web_api_key
from doc_web.literal_fidelity import SourcePageReview
from modules.common.ocr_request_receipt import require_completed_identity
from modules.common.table_source_review import POLICY, astra_request

ARGON = "gemini-4-argon"
ASTRA = "gpt-6-astra"
PROFILE = "google-native-argon-source-only-medium-v1"
ASTRA_PROFILE = "openai-native-astra-source-only-medium-v1"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def schema_digest():
    return digest(
        json.dumps(SourcePageReview.model_json_schema(), sort_keys=True).encode()
    )


def google_request(image_path):
    """Build the actual lossless native body; never accepts OCR/native text."""
    path = Path(image_path)
    data = path.read_bytes()
    with Image.open(path) as image:
        width, height = image.size
        mime = Image.MIME[image.format]
    if width * height > 25_000_000 or len(data) > 20 * 1024 * 1024:
        raise ValueError("Source image exceeds bounded review size")
    return {
        "systemInstruction": {"parts": [{"text": POLICY}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"Source image dimensions: {width} x {height} pixels. Read source tables; return JSON only."
                    },
                    {
                        "inlineData": {
                            "mimeType": mime,
                            "data": base64.b64encode(data).decode("ascii"),
                        }
                    },
                ],
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 32768,
            "thinkingConfig": {"thinkingLevel": "medium"},
            "responseMimeType": "application/json",
            "responseJsonSchema": SourcePageReview.model_json_schema(),
        },
    }


def native_google_output(data):
    """No fenced JSON cleanup, output selection, coordinate or content repair."""
    if data.get("error") or data.get("modelVersion") != ARGON:
        raise RuntimeError("Source-read Google served identity/error mismatch")
    candidates = data.get("candidates", [])
    if len(candidates) != 1 or candidates[0].get("finishReason") != "STOP":
        raise RuntimeError("Source-read Google response incomplete")
    parts = candidates[0].get("content", {}).get("parts", [])
    visible = []
    for part in parts:
        if part.get("thought") is True:
            continue
        if not isinstance(part.get("text"), str) or set(part) - {
            "text",
            "thought",
            "thoughtSignature",
        }:
            raise RuntimeError("Source-read Google final output is ambiguous")
        visible.append(part["text"])
    if not visible:
        raise RuntimeError("Source-read Google final output missing")
    validated_google_usage(data)
    return "\n".join(visible)


def validated_google_usage(data):
    """Require native billed counts before authority checks or instrumentation."""
    usage = data.get("usageMetadata", {})
    for name in ("promptTokenCount", "candidatesTokenCount"):
        if type(usage.get(name)) is not int or usage[name] < 0:
            raise RuntimeError("Source-read Google usage missing/invalid")
    for name in ("thoughtsTokenCount", "cachedContentTokenCount"):
        if type(usage.get(name, 0)) is not int or usage.get(name, 0) < 0:
            raise RuntimeError("Source-read Google usage invalid")
    if usage.get("cachedContentTokenCount", 0) > usage["promptTokenCount"]:
        raise RuntimeError("Source-read Google cache usage invalid")
    if usage["candidatesTokenCount"] + usage.get("thoughtsTokenCount", 0) > 32768:
        raise RuntimeError("Source-read Google output allowance exceeded")
    return usage


def validate_source_record(record, *, model, image_sha256, image_path=None):
    """Validate the explicitly selected authority; Google cannot impersonate Astra."""
    if record.get("requested_model") != model:
        raise ValueError("Source-read authority does not match selected reader")
    if record.get("submitted_image_sha256") != image_sha256:
        raise ValueError("Source-read image identity mismatch")
    if (
        record.get("prompt_sha256") != digest(POLICY.encode())
        or record.get("response_schema_sha256") != schema_digest()
    ):
        raise ValueError("Source-read policy/schema changed")
    if model == ASTRA:
        if (
            record.get("provider") != "openai"
            or record.get("authority_profile") != ASTRA_PROFILE
        ):
            raise ValueError("Unqualified OpenAI source-read authority profile")
        require_completed_identity(record)
        if (
            record.get("image_detail") != "original"
            or record.get("reasoning") != {"effort": "medium"}
            or record.get("service_tier") != "default"
        ):
            raise ValueError("Unqualified Astra source-read configuration")
        raw = record.get("raw_response") or ""
        native = record.get("native_response_json") or ""
        if digest(native.encode()) != record.get("native_response_sha256"):
            raise ValueError("Source-read raw native envelope changed")
        data = json.loads(native)
        if (
            data.get("model") != record.get("served_model")
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
        if usage["output_tokens"] > 8192:
            raise ValueError("Source-read native output allowance exceeded")
        visible = []
        for output in data.get("output", []):
            if output.get("type") == "reasoning":
                continue
            if output.get("type") != "message" or output.get("status") != "completed":
                raise ValueError("Source-read native final output incomplete/ambiguous")
            for part in output.get("content", []):
                if part.get("type") != "output_text" or not isinstance(
                    part.get("text"), str
                ):
                    raise ValueError(
                        "Source-read native final output incomplete/ambiguous"
                    )
                visible.append(part["text"])
        if (
            "".join(visible) != raw
            or not visible
            or record.get("max_output_tokens") != 8192
        ):
            raise ValueError(
                "Source-read raw output/configuration differs from native response"
            )
        if (
            image_path is None
            or not Path(image_path).is_file()
            or Path(image_path).is_symlink()
        ):
            raise ValueError("Native Astra source review requires actual bound image")
        if digest(Path(image_path).read_bytes()) != image_sha256 or record.get(
            "request_sha256"
        ) != digest(json.dumps(astra_request(image_path), sort_keys=True).encode()):
            raise ValueError(
                "Source-read native request differs from selected policy/image/schema"
            )
    elif model == ARGON:
        if (
            record.get("provider") != "google"
            or record.get("authority_profile") != PROFILE
            or record.get("served_model") != ARGON
            or record.get("status") != "STOP"
            or record.get("thinking_config") != {"thinkingLevel": "medium"}
            or record.get("max_output_tokens") != 32768
            or record.get("image_detail") != "original-bytes"
            or record.get("response_mime_type") != "application/json"
        ):
            raise ValueError("Unqualified Google source-read configuration")
        if image_path is not None:
            expected = digest(
                json.dumps(google_request(image_path), sort_keys=True).encode()
            )
            if record.get("request_sha256") != expected:
                raise ValueError(
                    "Source-read native request differs from selected policy/image/schema"
                )
        native = record.get("native_response_json") or ""
        if digest(native.encode()) != record.get("native_response_sha256"):
            raise ValueError("Source-read raw native envelope changed")
        data = json.loads(native)
        raw = native_google_output(data)
        if (
            raw != record.get("raw_response")
            or data.get("usageMetadata") != record.get("usage")
            or data.get("responseId") != record.get("response_id")
        ):
            raise ValueError("Source-read receipt differs from native raw response")
    else:
        raise ValueError("Unqualified source-read model")
    return SourcePageReview.model_validate_json(raw)


class GoogleSourceOnlyReader:
    """One native POST per page, explicit selection, no fallback or SDK retries."""

    def __init__(
        self,
        max_requests=3,
        budget_usd=4.5,
        ledger_path=None,
        client=None,
        api_key=None,
    ):
        if min(max_requests, budget_usd) <= 0:
            raise ValueError("Positive source-review caps required")
        self.max_requests, self.budget_usd = max_requests, budget_usd
        self.ledger_path = Path(ledger_path) if ledger_path else None
        if self.ledger_path and self.ledger_path.exists():
            raise ValueError("Fresh source-review ledger required")
        self.client = client or httpx.Client(
            timeout=1200, transport=httpx.HTTPTransport(retries=0)
        )
        self.api_key = api_key or get_doc_web_api_key("gemini")
        if not self.api_key:
            raise ValueError("DOC_WEB_GEMINI_API_KEY is missing")
        self.entries = []

    def __call__(self, image_path, requests):
        reserve = 0.37968
        if (
            len(self.entries) >= self.max_requests
            or (len(self.entries) + 1) * reserve > self.budget_usd
        ):
            raise RuntimeError("Source-review request/reservation cap reached")
        body = google_request(image_path)
        record = {
            "requested_model": ARGON,
            "provider": "google",
            "authority_profile": PROFILE,
            "submitted_image_sha256": digest(Path(image_path).read_bytes()),
            "prompt_sha256": digest(POLICY.encode()),
            "response_schema_sha256": schema_digest(),
            "request_sha256": digest(json.dumps(body, sort_keys=True).encode()),
            "thinking_config": {"thinkingLevel": "medium"},
            "max_output_tokens": 32768,
            "image_detail": "original-bytes",
            "response_mime_type": "application/json",
            "reserve_usd": reserve,
            "status": "reserved",
        }
        self.entries.append(record)
        requests.append(record)
        self._save()
        started = time.monotonic()
        try:
            response = self.client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{ARGON}:generateContent",
                headers={"x-goog-api-key": self.api_key},
                json=body,
            )
            raw = response.content
            # Preserve the complete bytes BEFORE HTTP, envelope or schema validation.
            if self.ledger_path:
                path = (
                    self.ledger_path.parent
                    / f"google-source-response-{len(self.entries):03d}.json"
                )
                with path.open("xb") as stream:
                    stream.write(raw)
                record["native_response_path"] = str(path.resolve())
            record["native_response_json"] = raw.decode("utf-8")
            record["native_response_sha256"] = digest(raw)
            response.raise_for_status()
            data = json.loads(raw)
            record.update(
                served_model=data.get("modelVersion"),
                response_id=data.get("responseId"),
                status=data.get("candidates", [{}])[0].get("finishReason"),
                usage=data.get("usageMetadata"),
            )
            from modules.common.utils import log_llm_usage

            usage = validated_google_usage(data)
            log_llm_usage(
                model=data.get("modelVersion") or ARGON,
                prompt_tokens=usage.get("promptTokenCount", 0),
                completion_tokens=(usage.get("candidatesTokenCount", 0)
                                   + usage.get("thoughtsTokenCount", 0)),
                provider="google",
                request_ms=(time.monotonic() - started) * 1000,
                request_id=data.get("responseId"),
            )
            record["raw_response"] = native_google_output(data)
            return validate_source_record(
                record,
                model=ARGON,
                image_sha256=record["submitted_image_sha256"],
                image_path=image_path,
            )
        except Exception as exc:
            record["error_type"] = type(exc).__name__
            raise
        finally:
            record["elapsed_seconds"] = time.monotonic() - started
            self._save()

    def _save(self):
        if self.ledger_path:
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            self.ledger_path.write_text(
                json.dumps(
                    {
                        "calls": len(self.entries),
                        "reserved_usd": len(self.entries) * 0.37968,
                        "entries": self.entries,
                    },
                    indent=2,
                )
                + "\n"
            )


class RetainedSourceOnlyReader:
    """Consume individually generated native receipts without re-inference."""

    def __init__(self, manifest_path, *, model):
        manifest = json.loads(Path(manifest_path).read_text())
        if (
            manifest.get("model") != model
            or manifest.get("schema_version") != "retained_source_reviews_v1"
        ):
            raise ValueError("Retained source-review profile mismatch")
        self.model, self.records, self.used = model, {}, set()
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
            if model == ASTRA and record.get("authority_profile") != ASTRA_PROFILE:
                raise ValueError(
                    "Retained Astra review requires native request/envelope lineage"
                )
            if model != ASTRA:
                validate_source_record(record, model=model, image_sha256=key)
            self.records[key] = record

    def __call__(self, image_path, requests):
        key = digest(Path(image_path).read_bytes())
        if key in self.used or key not in self.records:
            raise ValueError("Missing or repeated retained source review")
        self.used.add(key)
        record = self.records[key]
        result = validate_source_record(
            record, model=self.model, image_sha256=key, image_path=image_path
        )
        requests.append(record)
        return result
