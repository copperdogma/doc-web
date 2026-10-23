"""US$0 saved-output audit. Run under sandbox-exec deny network, env -i.

Never normalizes an envelope, manufactures native provenance, or sends a request.
"""

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import sys
import tempfile


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--old-root", type=Path, required=True)
    args.add_argument("--out", type=Path, required=True)
    a = args.parse_args()
    root = Path(__file__).resolve().parents[4]
    old, out = a.old_root.resolve(), a.out.resolve()
    assert root != old
    out.mkdir(parents=True, exist_ok=True)
    # This must run before owner imports. EPERM establishes OS denial; a
    # connection-refused/DNS-failure sentinel does not count as denial proof.
    blocked = []
    for host in ("127.0.0.1", "1.1.1.1"):
        with socket.socket() as connection:
            try:
                connection.connect((host, 9))
            except PermissionError as exc:
                assert exc.errno == 1
                blocked.append({"host": host, "port": 9, "errno": exc.errno,
                                "error": str(exc)})
            else:
                raise AssertionError("OS process network denial missing")
    assert len(blocked) == 2
    assert not [name for name in os.environ if "KEY" in name or "TOKEN" in name]
    sys.path.insert(0, str(root))
    from PIL import Image
    import yaml
    from modules.common.crop_safety import build_request, parse_response, FORMAT

    source_ledger = old / "benchmarks/results/scout099-20261020/ledger.json"
    ledger_bytes = source_ledger.read_bytes()
    calls = json.loads(ledger_bytes)["calls"]
    golden_rel = "benchmarks/golden/crop-page-level-safety-repair-048-source-adjudicated.json"
    golden = json.loads((old / golden_rel).read_text())
    task_rel = "benchmarks/tasks/safety-repair-048-control-full-continuation1.yaml"
    task_vars = {test["vars"]["crop_key"]: test["vars"] for test in
                 yaml.safe_load((root / task_rel).read_text())["tests"]}
    rows = {}
    complete_payloads = []
    files = {}
    frozen = [golden_rel, task_rel, "benchmarks/prompts/validate-page-level-crop.js",
              "benchmarks/scorers/crop_validation_scorer.py",
              "modules/common/crop_safety.py",
              "modules/transform/propose_crop_safety_v1/main.py",
              "modules/transform/propose_crop_safety_v1/prompt.txt",
              "modules/common/crop_review.py",
              "modules/common/crop_review_setup.py",
              "modules/common/crop_safety_custody.py"]
    for rel in frozen:
        files[rel] = {"old_sha256": sha((old / rel).read_bytes()),
                      "current_sha256": sha((root / rel).read_bytes())}
        files[rel]["unchanged"] = files[rel]["old_sha256"] == files[rel]["current_sha256"]
    scratch = root / "output/scout099-safety-feasibility"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as work:
        work = Path(work)
        for call in calls:
            stage = call["stage"]
            if not stage.startswith("safety-"):
                continue
            candidate = "candidate" in stage
            arm = "candidate" if candidate else "control"
            key = stage.removeprefix("safety-").split("-candidate")[0].split("-control")[0]
            request_path, response_path = old / call["request"], old / call["response"]
            request_raw, response_raw = request_path.read_bytes(), response_path.read_bytes()
            assert sha(request_raw) == call["request_sha256"]
            assert sha(response_raw) == call["response_sha256"]
            body, envelope = json.loads(request_raw), json.loads(response_raw)
            if not candidate:
                assert body["text"]["format"] == FORMAT
            payload = json.loads(envelope["choices"][0]["message"]["content"]) if candidate else json.loads(
                [m for m in envelope["output"] if m["type"] == "message"][0]["content"][0]["text"])
            assert set(payload) == set(FORMAT["schema"]["properties"])
            assert payload["verdict"] in ("pass", "fail")
            assert type(payload["has_page_text"]) is bool
            assert type(payload["excessive_blank"]) is bool
            assert isinstance(payload["reason"], str) and payload["reason"].strip()
            try:
                parse_response(response_raw, call["status_code"])
                parse_result = "admitted"
            except ValueError as exc:
                parse_result = str(exc)
            record = {"key": key, "arm": arm, "stage": stage,
                      "request": call["request"], "response": call["response"],
                      "request_sha256": sha(request_raw), "response_sha256": sha(response_raw),
                      "served_model": envelope.get("model"),
                      "provider": envelope.get("provider", "OpenAI"),
                      "payload": payload, "payload_shape": "four fields valid locally; not native admission",
                      "native_parse_result": parse_result,
                      "saved_grade": {"golden_verdict": golden[key]["verdict"],
                                      "correct": payload["verdict"] == golden[key]["verdict"],
                                      "false_safe": payload["verdict"] == "pass" and golden[key]["verdict"] == "fail"},
                      "historical_http_latency_ms": call["latency_ms"]}
            complete_payloads.append(record)
            row = rows.setdefault(key, {"key": key, "arms": {}})
            row["arms"][arm] = record
            parts = body["messages"][0]["content"] if candidate else body["input"][0]["content"]
            prompt = parts[0]["text"]
            assert sha(prompt.encode()) == "9931ded6b7e732687b0889e6959ef9a873e6f459a292c132443db0f6bc9a7371"
            images = []
            paths = []
            for index, part in enumerate(parts[1:]):
                uri = part["image_url"]["url"] if candidate else part["image_url"]
                fixture_var = "page_image" if index == 0 else "crop_image"
                fixture = (root / "benchmarks/tasks" /
                           task_vars[key][fixture_var].removeprefix("file://")).resolve()
                assert fixture.read_text().strip() == uri
                raw = base64.b64decode(uri.split(",", 1)[1], validate=True)
                image = Image.open(io.BytesIO(raw))
                path = work / f"{key}-{arm}-{index}.jpg"
                path.write_bytes(raw)
                paths.append(path)
                images.append({"sha256": sha(raw), "dimensions": list(image.size),
                               "format": image.format, "bytes": len(raw),
                               "current_fixture": str(fixture.relative_to(root)),
                               "current_fixture_exact_uri_match": True,
                               "detail": None if candidate else part.get("detail")})
            record["images_source_then_crop"] = images
            try:
                expected = build_request(*paths)
                record["native_build_result"] = "built; saved request differs"
                record["native_request_equal"] = expected == body
                if not candidate:
                    record["request_different_top_fields"] = sorted(k for k in set(expected) | set(body) if expected.get(k) != body.get(k))
            except ValueError as exc:
                record["native_build_result"] = str(exc)
            record["saved_request_controls"] = {k: body.get(k) for k in (
                "model", "reasoning", "max_tokens", "max_output_tokens", "response_format", "text", "provider", "store") if k in body}
        for key, row in rows.items():
            assert set(row["arms"]) == {"candidate", "control"}
            ci = row["arms"]["candidate"]["images_source_then_crop"]
            gi = row["arms"]["control"]["images_source_then_crop"]
            assert [x["sha256"] for x in ci] == [x["sha256"] for x in gi]
    assert len(rows) == 22 and len(complete_payloads) == 44
    assert all(r["native_parse_result"] != "admitted" for r in complete_payloads)
    assert sum("Image exceeds" in row["arms"]["control"]["native_build_result"] for row in rows.values()) == 15
    assert source_ledger.read_bytes() == ledger_bytes
    archive_rel = "docs/evals/evidence/080-scout099/native-evidence-dedup.tar.gz"
    manifest_rel = "docs/evals/evidence/080-scout099/manifest.json"
    archive_hash = sha((old / archive_rel).read_bytes())
    assert archive_hash == json.loads((old / manifest_rel).read_text())["sha256"]
    result = {"base_sha": "1a347f3f5ea13cb672a4e92d040704b99e556118", "current_root": str(root),
              "source_root": str(old), "network_denial": {"mechanism": "macOS sandbox-exec deny network*",
              "sentinel_before_owner_imports": blocked, "credential_environment": "empty key/token names; env -i; no env-file load"},
              "provider_dispatches": 0, "judge_dispatches": 0, "spend_usd": 0,
              "source_ledger_sha256": sha(ledger_bytes), "source_ledger_unchanged": True,
              "frozen_files": files, "cases": list(rows.values()),
              "routing": {"admitted_proposals": 0, "accepted": 0, "rejected": 0,
                          "review_required": "not measured: no native receipt admitted; all22 unavailable for production replay",
                          "request_image_bounds_rejected": 15, "request_image_bounds_within": 7,
                          "native_receipts_rejected": 44, "native_request_exact_matches": 0},
              "durable_raw": {"archive": str(old / archive_rel), "sha256": archive_hash,
                              "manifest": str(old / manifest_rel), "manifest_sha256": sha((old / manifest_rel).read_bytes()),
                              "restore_script": str(old / "docs/evals/evidence/080-scout099/restore.py"),
                              "restore_script_sha256": sha((old / "docs/evals/evidence/080-scout099/restore.py").read_bytes()),
                              "restore": "python RESTORE_SCRIPT NEW_DISJOINT_DIRECTORY (filesystem only)"},
              "boundary": "Actual unchanged build_request and parse_response; no native custody/geometry invented and no production parser patched. No release/human-authority claim."}
    write(out / "consumer-replay.json", result)
    write(out / "complete-payloads.json", complete_payloads)
    print(json.dumps({"cases": len(rows), "payloads": len(complete_payloads),
                      "network_sentinels_denied": len(blocked), "native_admitted": 0,
                      "oversized_crop_cases": 15, "provider_dispatches": 0, "spend_usd": 0}))


if __name__ == "__main__":
    main()
