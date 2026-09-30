"""Opt-in single-attempt Sol safety proposals. Default replay is entirely offline."""

import argparse
import json
import math
import os
import re
import time
from pathlib import Path

from modules.common.crop_review import (
    binding,
    custody_path,
    digest,
    require,
)
from modules.common.crop_safety import RESERVE_USD, build_request, parse_response
from modules.common.utils import read_jsonl, save_jsonl


def write_new(path, raw):
    path = Path(path)
    require(not path.exists() and not path.is_symlink(), "Receipt overwrite denied")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)
    path.chmod(0o600)


def persist(path, data):
    path = Path(path)
    temp = path.with_suffix(".tmp")
    require(not temp.exists() and not temp.is_symlink(), "Unsafe ledger temporary path")
    temp.write_text(json.dumps(data, indent=2) + "\n")
    temp.chmod(0o600)
    temp.replace(path)


def live_send(body):
    # This function is unreachable from replay and mock; import/getenv happen
    # only after explicit live admission and a durable unknown reservation.
    import httpx

    key = os.environ.get("DOC_WEB_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    require(bool(key), "Owner OpenAI key not configured")
    response = httpx.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        json=body,
        timeout=180,
    )
    return response.status_code, response.content


def propose(
    root,
    manifest,
    out,
    run_id,
    *,
    mode="replay",
    replay_manifest=None,
    cap_usd=None,
    max_calls=None,
    transport=None,
):
    root_arg = Path(root).absolute()
    require(
        ".." not in root_arg.parts
        and not any(p.is_symlink() for p in (root_arg, *root_arg.parents)),
        "Unsafe custody root",
    )
    root = root_arg.resolve()
    manifest = custody_path(root, str(Path(manifest).absolute().relative_to(root)))
    out = Path(out).absolute()
    require(
        ".." not in out.parts and not any(p.is_symlink() for p in (out, *out.parents)),
        "Unsafe proposal output path",
    )
    require(not out.exists(), "Proposal overwrite denied")
    if out.resolve().is_relative_to(root):
        require(
            out == root / "proposals.jsonl",
            "Only designated new proposal file may be written inside custody",
        )
    else:
        require(
            not root.is_relative_to(out.parent.resolve()),
            "Proposal output aliases custody",
        )
    require(mode in ("replay", "mock", "live"), "Unknown proposer mode")
    rows = list(read_jsonl(manifest))
    require(rows, "No candidates to propose")
    candidates = [binding(row, root, run_id, manifest) for row in rows]
    require(
        len({x["candidate_id"] for x in candidates}) == len(rows)
        and len({r["filename"] for r in rows}) == len(rows),
        "Duplicate candidate inventory",
    )
    bodies = [
        build_request(
            custody_path(root, r["source_image"]),
            manifest.parent / "images" / r["filename"],
            live=mode == "live",
        )
        for r in rows
    ]
    replay = None
    if mode != "live":
        require(
            replay_manifest is not None,
            "Offline replay/mock requires explicit receipt mapping",
        )
        path = Path(replay_manifest).absolute()
        require(path.is_file() and not path.is_symlink(), "Invalid replay mapping")
        replay = json.loads(path.read_text())
        require(replay.get("mode") == mode, "Replay/mock mode mismatch")
        entries = replay["entries"]
        require(
            len(entries) == len(rows)
            and {e["filename"] for e in entries} == {r["filename"] for r in rows},
            "Replay inventory mismatch",
        )
        replay = {e["filename"]: e for e in entries}
        for row, body in zip(rows, bodies):
            item = replay[row["filename"]]
            request = path.parent / item["request_path"]
            response = path.parent / item["response_path"]
            for p in (request, response):
                require(
                    not Path(
                        item["request_path"] if p == request else item["response_path"]
                    ).is_absolute()
                    and p.resolve().is_relative_to(path.parent.resolve())
                    and not p.is_symlink(),
                    "Replay custody escape",
                )
            require(
                digest(request) == item["request_sha256"]
                and digest(response) == item["response_sha256"]
                and json.loads(request.read_bytes()) == body,
                "Replay request/response hash or semantic mismatch",
            )
            item["response_bytes"] = response.read_bytes()
    else:
        require(
            type(max_calls) is int
            and max_calls >= len(rows)
            and isinstance(cap_usd, (int, float))
            and math.isfinite(cap_usd)
            and cap_usd > 0
            and len(rows) * RESERVE_USD <= cap_usd,
            "Explicit sufficient live call/dollar caps required",
        )
    if mode == "live":
        require(
            re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", run_id) is not None,
            "Unsafe live run identity",
        )
        # A durable owner-local run anchor rejects a fresh custody directory
        # reusing the same paid run identity. Synthetic transport tests isolate
        # their anchor under tmp custody; CLI exposes no reset/alternate wallet.
        registry = (
            root.parent / ".synthetic-live-run-anchors"
            if transport is not None
            else Path(__file__).resolve().parents[3] / "output/crop-safety-run-anchors"
        )
        require(
            not any(p.is_symlink() for p in (registry, *registry.parents)),
            "Unsafe live run registry",
        )
        registry.mkdir(parents=True, exist_ok=True)
        anchor = registry / (run_id + ".json")
        identity = {
            "run_id": run_id,
            "custody_root": str(root),
            "manifest_sha256": digest(manifest),
            "cap_usd": cap_usd,
            "max_calls": max_calls,
        }
        if anchor.exists():
            require(
                not anchor.is_symlink() and json.loads(anchor.read_text()) == identity,
                "Live run identity/cap cannot reset in fresh custody",
            )
        else:
            write_new(anchor, json.dumps(identity, sort_keys=True).encode())
    receipts = root / "native-receipts"
    require(not receipts.is_symlink(), "Symlinked receipt directory")
    receipts.mkdir(exist_ok=True)
    ledger_path = receipts / "ledger.json"
    if ledger_path.exists():
        require(not ledger_path.is_symlink(), "Symlinked ledger")
        ledger = json.loads(ledger_path.read_text())
        require(
            ledger["run_id"] == run_id
            and ledger["mode"] == mode
            and ledger["manifest_sha256"] == digest(manifest),
            "Existing run identity changed",
        )
        if mode == "live":
            require(
                ledger["cap_usd"] == cap_usd and ledger["max_calls"] == max_calls,
                "Run cap cannot be reset or changed",
            )
    else:
        ledger = {
            "run_id": run_id,
            "mode": mode,
            "manifest_sha256": digest(manifest),
            "cap_usd": cap_usd,
            "max_calls": max_calls,
            "settled_upper_usd": 0,
            "calls": [],
            "closed": False,
        }
    require(not ledger["closed"], "Run already closed")
    proposals = []
    for row, b, body in zip(rows, candidates, bodies):
        require(
            not any(c["candidate_id"] == b["candidate_id"] for c in ledger["calls"]),
            "Duplicate dispatch denied; no implicit recovery",
        )
        exposure = ledger["settled_upper_usd"] + sum(
            c["reserved_usd"]
            for c in ledger["calls"]
            if c.get("settled_upper_usd") is None
        )
        if mode == "live":
            require(
                len(ledger["calls"]) < max_calls and exposure + RESERVE_USD <= cap_usd,
                "Live admission cap exceeded",
            )
        sequence = len(ledger["calls"]) + 1
        request_path = receipts / f"request-{sequence:03d}.json"
        raw_request = json.dumps(body, sort_keys=True).encode()
        write_new(request_path, raw_request)
        record = {
            "sequence": sequence,
            "candidate_id": b["candidate_id"],
            "request_sha256": digest(request_path),
            "reserved_usd": RESERVE_USD if mode == "live" else 0,
            "settled_upper_usd": None,
            "status": "reserved",
        }
        ledger["calls"].append(record)
        persist(ledger_path, ledger)
        proposal = {
            "candidate_id": b["candidate_id"],
            "binding": b,
            "origin": "native_crop_safety"
            if mode == "live"
            else "replayed_crop_safety"
            if mode == "replay"
            else "mock_crop_safety",
            "mode": mode,
            "verdict": None,
            "status": "unavailable",
            "request": {
                "path": str(request_path.relative_to(root)),
                "sha256": digest(request_path),
            },
            "prompt_sha256": body["input"][0]["content"][0]["text"]
            and __import__("hashlib")
            .sha256(body["input"][0]["content"][0]["text"].encode())
            .hexdigest(),
        }
        started = time.monotonic()
        try:
            if mode == "live":
                status, raw = (transport or live_send)(body)
            else:
                item = replay[row["filename"]]
                status, raw = item["status_code"], item["response_bytes"]
            response_path = receipts / f"response-{sequence:03d}.json"
            write_new(response_path, raw)
            proposal.update(
                receipt={
                    "path": str(response_path.relative_to(root)),
                    "sha256": digest(response_path),
                },
                status_code=status,
            )
            record.update(response_sha256=digest(response_path), status_code=status)
            answer, data, cost = parse_response(raw, status, live=mode == "live")
            proposal.update(
                status="completed",
                verdict=answer["verdict"],
                answer=answer,
                served_model=data["model"],
                response_id=data["id"],
                usage=data["usage"],
            )
            record.update(
                status="completed",
                settled_upper_usd=cost if mode == "live" else 0,
                cost_method="uncached/write maximum rate; native usage upper bound"
                if mode == "live"
                else "offline replay; no new charge",
            )
            ledger["settled_upper_usd"] += record["settled_upper_usd"]
        except Exception as exc:
            # Receipt precedes parsing; exceptions never become a model fail.
            proposal["error_class"] = type(exc).__name__
            if isinstance(exc, ValueError):
                proposal["error_reason"] = str(exc)[:500]
            record.update(status="unavailable", error_class=type(exc).__name__)
            ledger["closed"] = True
        record["latency_ms"] = round((time.monotonic() - started) * 1000)
        proposals.append(proposal)
        persist(ledger_path, ledger)
        if ledger["closed"]:
            break
    save_jsonl(out, proposals)
    return {
        "proposals": str(out),
        "completed": sum(x["status"] == "completed" for x in proposals),
        "unavailable": sum(x["status"] != "completed" for x in proposals),
        "ledger": str(ledger_path),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--custody-root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--mode", choices=("replay", "mock", "live"), default="replay")
    parser.add_argument("--replay-manifest")
    parser.add_argument("--cap-usd", type=float)
    parser.add_argument("--max-calls", type=int)
    parser.add_argument("--state-file")
    parser.add_argument("--progress-file")
    args = parser.parse_args()
    try:
        result = propose(
            args.custody_root,
            args.manifest,
            args.out,
            args.run_id,
            mode=args.mode,
            replay_manifest=args.replay_manifest,
            cap_usd=args.cap_usd,
            max_calls=args.max_calls,
        )
        print(json.dumps(result))
        if result["unavailable"]:
            parser.exit(2, "Native proposal unavailable; review/publication held\n")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
