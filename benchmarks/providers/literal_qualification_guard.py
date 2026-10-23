"""Fail-closed, serial native POST custody for the frozen literal campaign.

Set DOC_WEB_LITERAL_CAMPAIGN_FILE and DOC_WEB_LITERAL_STAGE before using
``install()``. Request hashes use ``request_sha256(body)``; the complete native
body (never headers or credential-bearing URLs) is retained. No retry is made.
The config is bound to the ledger by its file SHA256 on the first admission.
"""

from __future__ import annotations

import fcntl
import hashlib
import importlib
import json
from datetime import date, datetime, timezone
import os
import re
import stat
import time
import uuid
from decimal import Decimal
from pathlib import Path

PRICES = {"gemini-4-argon": (2, 0.1, 2, 10), "gpt-6-astra": (10, 1, 12.5, 50)}
APPROVED_PRIOR = Decimal("0.866677250")
APPROVED_CAMPAIGN_PRIOR = Decimal("3.877369745")


class AdmissionDenied(RuntimeError):
    """The call was denied before dispatch, or the receipt cannot be trusted."""


def request_sha256(body):
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise AdmissionDenied("Invalid campaign amount")
    number = Decimal(str(value))
    if not number.is_finite() or number < 0:
        raise AdmissionDenied("Invalid campaign amount")
    return number


def _count(value):
    if type(value) is not int or value < 0:
        raise ValueError("Invalid token usage")
    return value


def _save(path, data):
    """Atomic durable ledger replacement under the campaign's flock."""
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            os.chmod(temporary, 0o600)
            stream.write(json.dumps(data, indent=2, allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        _sync_dir(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def _sync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _exclusive(path, raw):
    with path.open("xb") as stream:
        os.chmod(path, 0o600)
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    _sync_dir(path.parent)


def _select_stage(config, stage):
    selected = next(
        (entry for entry in config["matrix"] if entry["stage"] == stage), None
    )
    if selected is not None:
        return selected
    if (
        config.get("operational_recovery") is True
        and isinstance(stage, str)
        and stage.startswith("recovery-")
    ):
        base_stage = stage.removeprefix("recovery-")
        base = next(
            (
                entry
                for entry in config["matrix"]
                if entry["stage"] == base_stage and not entry.get("recovery_of")
            ),
            None,
        )
        if base is not None:
            return {**base, "stage": stage, "recovery_of": base_stage}
    return None


def _required_gate(selected):
    """Read trusted owner clearance without following a final-path symlink."""
    if "required_gate" not in selected:
        return
    filename = selected["required_gate"]
    if not isinstance(filename, str) or not Path(filename).is_absolute():
        raise AdmissionDenied("Required gate must be an absolute JSON file")
    try:
        descriptor = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise AdmissionDenied("Required gate must be a regular nonsymlink file")
            data = json.loads(stream.read())
        if not isinstance(data, dict) or data.get("allowed") is not True:
            raise AdmissionDenied("Required owner gate has not cleared this stage")
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        raise AdmissionDenied(
            "Required owner gate missing, unsafe, or malformed"
        ) from exc


def _transport_check(client, request, kwargs):
    # SDK retries re-enter Client.send and lose duplicate admission. Pool-level
    # retries do not, so inspect the actual URL-selected transport before POST.
    if kwargs.get("follow_redirects") is True or getattr(
        client, "follow_redirects", False
    ):
        raise AdmissionDenied("Redirecting native POST transport denied")
    selector = getattr(client, "_transport_for_url", None)
    if not callable(selector):
        raise AdmissionDenied("Unverifiable native transport")
    transport = selector(request.url)
    module = importlib.import_module(type(client).__module__.split(".")[0])
    if isinstance(transport, getattr(module, "MockTransport", ())):
        return
    if not isinstance(transport, getattr(module, "HTTPTransport", ())):
        raise AdmissionDenied("Unverifiable native transport")
    retries = getattr(getattr(transport, "_pool", None), "_retries", None)
    if type(retries) is not int or retries != 0:
        raise AdmissionDenied("Transport retries must be verifiably zero")


def _native(request, body):
    if request.url.scheme != "https" or request.url.port not in (None, 443):
        raise AdmissionDenied("Only standard native HTTPS service allowed")
    if request.url.host == "api.openai.com" and request.url.path == "/v1/responses":
        if request.url.query or body.get("model") != "gpt-6-astra":
            raise AdmissionDenied("Unapproved native OpenAI route/model")
        if (
            body.get("tools")
            or body.get("store") is not False
            or body.get("stream", False)
        ):
            raise AdmissionDenied("Native tool/storage/stream contract denied")
        if body.get("service_tier") != "default" or body.get("background", False):
            raise AdmissionDenied("Nonstandard native service denied")
        return "gpt-6-astra", _count(body["max_output_tokens"]), False
    match = re.fullmatch(
        r"/(v1|v1beta)/models/(gemini-4-argon):generateContent", request.url.path
    )
    if request.url.host == "generativelanguage.googleapis.com" and match:
        # Query may contain the Google API key; it is never retained.
        if (
            set(request.url.params.keys()) - {"key"}
            or body.get("tools")
            or body.get("cachedContent")
        ):
            raise AdmissionDenied("Nonstandard Google route or tools denied")
        return match[2], _count(body["generationConfig"]["maxOutputTokens"]), True
    raise AdmissionDenied("Unmetered POST denied by literal campaign")


def _usage(data, google):
    if not isinstance(data, dict):
        raise ValueError("Invalid response envelope")
    usage = data["usageMetadata" if google else "usage"]
    if not isinstance(usage, dict):
        raise ValueError("Invalid usage envelope")
    if google:
        inp = _count(usage["promptTokenCount"])
        output = _count(usage["candidatesTokenCount"])
        thinking = _count(usage.get("thoughtsTokenCount", 0))
        cached = _count(usage.get("cachedContentTokenCount", 0))
        writes = 0
        if "totalTokenCount" in usage:
            _count(usage["totalTokenCount"])
        output += thinking
    else:
        inp, output = _count(usage["input_tokens"]), _count(usage["output_tokens"])
        details = usage.get("input_tokens_details", {})
        out_details = usage.get("output_tokens_details", {})
        if not isinstance(details, dict) or not isinstance(out_details, dict):
            raise ValueError("Invalid token details")
        cached = _count(details.get("cached_tokens", 0))
        writes = _count(details.get("cache_write_tokens", 0))
        thinking = _count(out_details.get("reasoning_tokens", 0))
        if thinking > output:
            raise ValueError("Reasoning tokens exceed inclusive output")
    if cached + writes > inp:
        raise ValueError("Cache tokens exceed input")
    return {
        "input_tokens": inp,
        "cached_tokens": cached,
        "cache_write_tokens": writes,
        "output_tokens": output,
        "thinking_tokens": thinking,
    }


def _observed_bound_violation(data, google, bound, maximum):
    """Even an otherwise malformed receipt can prove an envelope was exceeded."""
    if not isinstance(data, dict):
        return False
    usage = data.get("usageMetadata" if google else "usage")
    if not isinstance(usage, dict):
        return False
    inp = usage.get("promptTokenCount" if google else "input_tokens")
    output = usage.get("candidatesTokenCount" if google else "output_tokens")
    thinking = usage.get("thoughtsTokenCount", 0) if google else 0

    def known(value):
        return type(value) is int and value >= 0

    return (
        (known(inp) and inp > bound)
        or (known(output) and output > maximum)
        or (google and known(thinking) and thinking > maximum)
        or (
            google and known(output) and known(thinking) and output + thinking > maximum
        )
    )


def _cost(usage, model, *, cold=False, december=False):
    prices = [Decimal(str(x)) for x in PRICES[model]]
    if december and model == "gemini-4-argon":
        prices = [price * 2 for price in prices]
    inp, out = usage["input_tokens"], usage["output_tokens"]
    cached, writes = (
        (0, 0) if cold else (usage["cached_tokens"], usage["cache_write_tokens"])
    )
    return (
        (inp - cached - writes) * prices[0]
        + cached * prices[1]
        + writes * prices[2]
        + out * prices[3]
    ) / Decimal(1000000)


class LiteralCampaignGuard:
    def __init__(self, config_file=None):
        selected = config_file or os.environ.get("DOC_WEB_LITERAL_CAMPAIGN_FILE")
        if not selected:
            raise AdmissionDenied("Frozen campaign config required")
        self.config_file = Path(selected).resolve()

    def _config(self):
        if datetime.now(timezone.utc).date() >= date(2026, 12, 1):
            raise AdmissionDenied(
                "October campaign pricing expired; fresh rates/reservations required"
            )
        raw = self.config_file.read_bytes()
        config = json.loads(raw)
        if not isinstance(config, dict):
            raise AdmissionDenied("Invalid frozen campaign config")
        limits = (("cap_usd", 3), ("owner_cap_usd", 15), ("campaign_cap_usd", 35))
        for key, maximum in limits:
            if not 0 < _number(config[key]) <= maximum:
                raise AdmissionDenied("Unapproved campaign ceiling")
        if (
            _number(config["prior_exposure_usd"]) < APPROVED_PRIOR
            or _number(config["campaign_prior_exposure_usd"]) < APPROVED_CAMPAIGN_PRIOR
        ):
            raise AdmissionDenied("Prior exposure cannot be reduced")
        if type(config["max_calls"]) is not int or not 0 < config["max_calls"] <= 33:
            raise AdmissionDenied("Invalid finite call ceiling")
        if (
            "operational_recovery" in config
            and type(config["operational_recovery"]) is not bool
        ):
            raise AdmissionDenied("Operational recovery selection must be boolean")
        matrix = config["matrix"]
        if not isinstance(matrix, list) or len(matrix) > config["max_calls"]:
            raise AdmissionDenied("Invalid frozen matrix")
        stages = [entry["stage"] for entry in matrix]
        if len(set(stages)) != len(stages) or not all(
            isinstance(x, str) and x for x in stages
        ):
            raise AdmissionDenied("Frozen stage identities must be unique")
        recovery = [entry for entry in matrix if entry.get("recovery_of")]
        if len(recovery) > 1:
            raise AdmissionDenied("Only one selected recovery stage allowed")
        for entry in recovery:
            base = next((x for x in matrix if x["stage"] == entry["recovery_of"]), None)
            if (
                base is None
                or base.get("recovery_of")
                or any(base[key] != entry[key] for key in ("model", "request_sha256"))
            ):
                raise AdmissionDenied(
                    "Recovery must preserve original semantic request"
                )
        if (
            not isinstance(config["old_ledger_sha256"], dict)
            or not config["old_ledger_sha256"]
        ):
            raise AdmissionDenied("Frozen prior ledger hashes required")
        for filename, digest in config["old_ledger_sha256"].items():
            if hashlib.sha256(Path(filename).read_bytes()).hexdigest() != digest:
                raise AdmissionDenied("Closed prior ledger changed")
        return config, hashlib.sha256(raw).hexdigest()

    def send(self, original, client, request, **kwargs):
        if request.method != "POST":
            return original(client, request, **kwargs)
        config, digest = self._config()
        selected = _select_stage(config, os.environ.get("DOC_WEB_LITERAL_STAGE"))
        if selected is None:
            raise AdmissionDenied("Explicit frozen stage required")
        _required_gate(selected)  # Before even creating the operational lock directory.
        result_dir = Path(config["result_dir"]).resolve()
        result_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        with (result_dir / "dispatch.lock").open("a") as lock:
            os.chmod(result_dir / "dispatch.lock", 0o600)
            fcntl.flock(lock, fcntl.LOCK_EX)
            # Recheck frozen config/old ledgers after acquiring the lock.
            current, current_digest = self._config()
            if current_digest != digest:
                raise AdmissionDenied("Campaign config changed while waiting")
            return self._send_locked(
                current, digest, result_dir, original, client, request, kwargs
            )

    def _send_locked(
        self, config, digest, result_dir, original, client, request, kwargs
    ):
        stop_paths = [
            result_dir / "stop.json",
            *map(Path, config.get("stop_files", [])),
        ]
        if any(path.exists() for path in stop_paths):
            raise AdmissionDenied("Campaign stop file denies dispatch")
        stage = os.environ.get("DOC_WEB_LITERAL_STAGE")
        selected = _select_stage(config, stage)
        if selected is None:
            raise AdmissionDenied("Explicit frozen stage required")
        _required_gate(selected)  # Recheck owner state under the admission lock.
        try:
            native_request = request.content
            body = json.loads(native_request)
            if not isinstance(body, dict):
                raise ValueError("Body must be object")
            model, maximum, google = _native(request, body)
        except (ValueError, KeyError, TypeError) as exc:
            raise AdmissionDenied("Invalid native POST body") from exc
        if selected["model"] != model or selected["request_sha256"] != request_sha256(
            body
        ):
            raise AdmissionDenied("Request/model not in frozen stage")
        bound = _count(selected["input_token_bound"])
        if not 0 < bound <= 26000 or maximum != selected["max_output_tokens"]:
            raise AdmissionDenied("Frozen input/output bound denied")
        kind = selected["kind"]
        if model == "gemini-4-argon":
            required_reserve, expected_output = Decimal("0.379680"), 32768
        elif kind == "ocr":
            required_reserve, expected_output = Decimal("0.734600"), 8192
        elif kind == "reader":
            required_reserve, expected_output = Decimal("1.500000"), maximum
        else:
            raise AdmissionDenied("Unknown frozen stage kind")
        if (
            kind not in ("ocr", "reader")
            or (model == "gemini-4-argon" and kind != "reader")
            or maximum != expected_output
            or not 0 < maximum <= 32768
        ):
            raise AdmissionDenied("Unapproved native output envelope")
        reserve = _number(selected["reserved_usd"])
        envelope = (
            bound * Decimal(str(max(PRICES[model][:3])))
            + maximum * Decimal(str(PRICES[model][3]))
        ) / Decimal(1000000)
        if reserve < required_reserve or reserve < envelope:
            raise AdmissionDenied("Frozen reservation below conservative envelope")
        _transport_check(client, request, kwargs)
        path = result_dir / "ledger.json"
        ledger = (
            json.loads(path.read_text())
            if path.exists()
            else {
                "config_sha256": digest,
                "spent_usd": 0,
                "calls": [],
                "closed": False,
                "cap_usd": config["cap_usd"],
                "max_calls": config["max_calls"],
            }
        )
        if ledger.get("config_sha256") != digest or ledger.get("closed"):
            raise AdmissionDenied("Frozen ledger mismatch or closed campaign")
        calls = ledger["calls"]
        if any(call["stage"] == stage for call in calls):
            raise AdmissionDenied("Duplicate stage dispatch denied")
        if len(calls) >= config["max_calls"]:
            raise AdmissionDenied("Finite call ceiling exhausted")
        if selected.get("recovery_of"):
            if any(
                call.get("recovery_of")
                or (_select_stage(config, call["stage"]) or {}).get("recovery_of")
                for call in calls
            ):
                raise AdmissionDenied(
                    "Single operational recovery slot already consumed"
                )
            if not any(
                call["stage"] == selected["recovery_of"]
                and not any(
                    call.get(flag) is True
                    for flag in (
                        "semantic_failure",
                        "latency_violation",
                        "bound_violation",
                        "served_model_violation",
                    )
                )
                and (
                    call.get("status_code") == 502
                    or call.get("harness_repair_authorized") is True
                )
                for call in calls
            ):
                raise AdmissionDenied("Recovery requires preserved operational failure")
        spent = sum(
            (
                _number(call["cost_usd"])
                for call in calls
                if call.get("cost_usd") is not None
            ),
            Decimal(0),
        )
        unknown = sum(
            (
                _number(call["reserved_usd"])
                for call in calls
                if call.get("cost_usd") is None
            ),
            Decimal(0),
        )
        if _number(ledger["spent_usd"]) != spent:
            raise AdmissionDenied("Ledger settlement sum mismatch")
        liability = spent + unknown + reserve
        if (
            liability > _number(config["cap_usd"])
            or liability + _number(config["prior_exposure_usd"])
            > _number(config["owner_cap_usd"])
            or liability + _number(config["campaign_prior_exposure_usd"])
            > _number(config["campaign_cap_usd"])
        ):
            raise AdmissionDenied("Campaign admission exceeds inclusive cap")
        seq = len(calls) + 1
        request_path, response_path = (
            result_dir / f"{name}-{seq:03d}.json" for name in ("request", "response")
        )
        if request_path.exists() or response_path.exists():
            raise AdmissionDenied("Exclusive receipt namespace collision")
        record = {
            "stage": stage,
            "recovery_of": selected.get("recovery_of"),
            "sequence": seq,
            "model": model,
            "kind": kind,
            "request_sha256": selected["request_sha256"],
            "native_request_bytes_sha256": hashlib.sha256(native_request).hexdigest(),
            "native_request_bytes": len(native_request),
            "reserved_usd": float(reserve),
            "cost_usd": None,
            "input_token_bound": bound,
            "max_output_tokens": maximum,
            "started_unix": time.time(),
            "guard_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        }
        calls.append(record)
        _save(path, ledger)  # Durable intent must precede request receipt and POST.
        started = time.monotonic()
        try:
            _exclusive(request_path, native_request)
            response = original(client, request, **kwargs)
            response.read()
            raw = response.content
            _exclusive(
                response_path, raw
            )  # Complete raw bytes before json/usage parsing.
        except Exception as exc:
            record.update(
                transport_exception=type(exc).__name__,
                latency_ms=round((time.monotonic() - started) * 1000),
            )
            if "Timeout" in type(exc).__name__ or (
                model == "gemini-4-argon" and record["latency_ms"] > 180000
            ):
                record["latency_violation"] = True
                ledger["closed"] = True
            _save(path, ledger)
            raise
        record.update(
            response_sha256=hashlib.sha256(raw).hexdigest(),
            response_bytes=len(raw),
            status_code=response.status_code,
            latency_ms=round((time.monotonic() - started) * 1000),
        )
        if model == "gemini-4-argon" and record["latency_ms"] > 180000:
            record["latency_violation"] = True
            ledger["closed"] = True
        successful_astra = not google and 200 <= response.status_code < 300
        tier_checked = False
        try:
            data = json.loads(raw)
            if not google:
                record["served_service_tier"] = (
                    data.get("service_tier") if isinstance(data, dict) else None
                )
                tier_checked = True
                if record["served_service_tier"] != "default":
                    if successful_astra or record["served_service_tier"] is not None:
                        record["service_tier_violation"] = True
                        ledger["closed"] = True
                    raise ValueError("Standard native service tier was not proved")
            if _observed_bound_violation(data, google, bound, maximum):
                record["bound_violation"] = True
                ledger["closed"] = True
            if (
                isinstance(data, dict)
                and data.get("modelVersion", data.get("model", model)) != model
            ):
                record["served_model_violation"] = True
                ledger["closed"] = True
            usage = _usage(data, google)
            actual = _cost(usage, model)
            record.update(
                cost_usd=float(actual),
                usage=usage,
                cold_cost_usd=float(_cost(usage, model, cold=True)),
                december_cost_usd=float(_cost(usage, model, december=True)),
                december_cold_cost_usd=float(
                    _cost(usage, model, cold=True, december=True)
                ),
                served_model=data.get("modelVersion", data.get("model")),
                response_id=data.get("responseId", data.get("id")),
            )
            ledger["spent_usd"] = float(spent + actual)
            if record["served_model"] != model:
                record["served_model_violation"] = True
                ledger["closed"] = True
            if (
                usage["input_tokens"] > bound
                or usage["output_tokens"] > maximum
                or actual > reserve
            ):
                record["bound_violation"] = True
                ledger["closed"] = True
        except (KeyError, ValueError, TypeError):
            record["billing_unresolved"] = True
            if successful_astra and not tier_checked:
                record["service_tier_violation"] = True
                ledger["closed"] = True
        _save(path, ledger)
        return response


def guarded_send(original, client, request, **kwargs):
    return LiteralCampaignGuard().send(original, client, request, **kwargs)


def install():
    """Patch both native synchronous HTTP clients; repeat installation is safe."""
    for name in ("httpx", "httpx2"):
        try:
            library = importlib.import_module(name)
        except ImportError:
            if name == "httpx":
                raise
            continue
        original = library.Client.send
        if getattr(original, "_literal_campaign_guard", False):
            continue

        def send(client, request, _original=original, **kwargs):
            return guarded_send(_original, client, request, **kwargs)

        send._literal_campaign_guard = True
        send._literal_original = original
        library.Client.send = send
