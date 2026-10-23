"""Bounded MOCK native envelopes through the actual guarded CLI/driver topology.

This proves wiring and retained-receipt export, never provider quality or billing.
No provider callback is replaced. The native HTTPTransport is stopped locally,
Client.send retains the production campaign guard, and sockets fail closed.
"""

from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "benchmarks/fixtures/argon-literal-qualification-v1"
LABEL = "OFFLINE MOCK ONLY; frozen gold responses; zero actual provider spend; no model-quality evidence"
DUMMY = "offline-dummy-never-a-real-key"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def deny_socket(*args, **kwargs):
    raise RuntimeError("Offline literal proof forbids socket connections")


def mock_output(stage, panel=PANEL):
    """Gold is simulation input, not an independent source-quality judgment."""
    pieces = stage.split("-")
    if len(pieces) not in (2, 3) or pieces[0] not in ("ocr", "reader"):
        raise RuntimeError("Only initial frozen mock stages are supported")
    case = pieces[1]
    manifest = read(panel / "manifest.json")
    row = next(p for p in manifest["pages"] if p["case_id"] == case)
    gold_path = panel / row["gold"]
    if sha(gold_path.read_bytes()) != row["gold_sha256"]:
        raise RuntimeError("Mock gold changed from panel manifest")
    gold = read(gold_path)
    if pieces[0] == "reader":
        return json.dumps(gold, ensure_ascii=False)
    return (
        '<meta name="ocr-metadata" data-ocr-quality="1.0" '
        'data-ocr-integrity="1.0" data-continuation-risk="0.0">\n'
        f"<h1>Offline fixture {case}</h1>" + "".join(t["html"] for t in gold["tables"])
    )


def native_envelope(stage, text, google=False):
    if google:
        return {
            "modelVersion": "gemini-4-argon",
            "responseId": "offline-mock-" + stage,
            "candidates": [
                {
                    "content": {"role": "model", "parts": [{"text": text}]},
                    "finishReason": "STOP",
                    "index": 0,
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 100,
                "candidatesTokenCount": 100,
                "thoughtsTokenCount": 0,
                "totalTokenCount": 200,
            },
        }
    return {
        "id": "resp_offline_mock_" + stage,
        "object": "response",
        "created_at": 0,
        "status": "completed",
        "error": None,
        "incomplete_details": None,
        "instructions": None,
        "max_output_tokens": 8192,
        "model": "gpt-6-astra",
        "service_tier": "default",
        "output": [
            {
                "id": "msg_offline_" + stage,
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [
                    {
                        "type": "output_text",
                        "text": text,
                        "annotations": [],
                        "logprobs": [],
                    }
                ],
            }
        ],
        "parallel_tool_calls": False,
        "previous_response_id": None,
        "reasoning": {"effort": "medium", "summary": None},
        "store": False,
        "temperature": 1.0,
        "text": {"format": {"type": "text"}},
        "tool_choice": "auto",
        "tools": [],
        "top_p": 1.0,
        "truncation": "disabled",
        "usage": {
            "input_tokens": 100,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens": 100,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 200,
        },
        "metadata": {},
    }


def install_backend():
    """Startup-only transport patch; production Client.send remains in custody."""
    socket.socket.connect = deny_socket
    socket.socket.connect_ex = deny_socket
    socket.create_connection = deny_socket
    if os.environ.get("DOC_WEB_LITERAL_OFFLINE") != "1":
        raise RuntimeError("Explicit offline environment required")
    for key in ("OPENAI_API_KEY", "DOC_WEB_OPENAI_API_KEY", "DOC_WEB_GEMINI_API_KEY"):
        if os.environ.get(key) != DUMMY:
            raise RuntimeError("Only explicit dummy credentials are permitted")
    if Path(os.environ["DOC_WEB_ENV_FILE"]).exists():
        raise RuntimeError("Offline dotenv override must be nonexistent")
    from benchmarks.providers.literal_qualification_guard import install, request_sha256

    install()
    for library_name in ("httpx", "httpx2"):
        try:
            library = importlib.import_module(library_name)
        except ImportError:
            continue

        def handle_request(transport, request, _library=library):
            if not getattr(_library.Client.send, "_literal_campaign_guard", False):
                raise RuntimeError("Actual production guard missing")
            config = read(os.environ["DOC_WEB_LITERAL_CAMPAIGN_FILE"])
            stage = os.environ["DOC_WEB_LITERAL_STAGE"]
            body = json.loads(request.content)
            # A durable admission entry must already exist before mock transport.
            ledger = read(Path(config["result_dir"]) / "ledger.json")
            call = ledger["calls"][-1]
            if call["stage"] != stage or call["request_sha256"] != request_sha256(body):
                raise RuntimeError("Mock transport bypassed frozen admission")
            if request.method != "POST" or call.get("cost_usd") is not None:
                raise RuntimeError("Unexpected mock native dispatch")
            google = request.url.host == "generativelanguage.googleapis.com"
            if google:
                encoded = body["contents"][0]["parts"][1]["inlineData"]["data"]
            else:
                encoded = body["input"][1]["content"][1]["image_url"].split(",", 1)[1]
            row = next(
                p
                for p in read(PANEL / "manifest.json")["pages"]
                if p["case_id"] == stage.split("-")[1]
            )
            if sha(base64.b64decode(encoded)) != row["render_sha256"]:
                raise RuntimeError(
                    "Native request did not contain actual frozen renderer bytes"
                )
            events = Path(config["result_dir"]) / "mock-transport.jsonl"
            with events.open("a") as stream:
                stream.write(
                    json.dumps(
                        {
                            "evidence_class": LABEL,
                            "stage": stage,
                            "request_sha256": request_sha256(body),
                            "guard_intent_sequence": call["sequence"],
                            "actual_provider_spend_usd": 0,
                        }
                    )
                    + "\n"
                )
            return _library.Response(
                200,
                json=native_envelope(stage, mock_output(stage), google),
                request=request,
                headers={"content-type": "application/json"},
            )

        library.HTTPTransport.handle_request = handle_request


def clean_environment(startup, campaign, result_root):
    """Only process essentials are inherited; no credential values are inspected."""
    names = ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "SYSTEMROOT")
    env = {name: os.environ[name] for name in names if name in os.environ}
    env.update(
        {
            "OPENAI_API_KEY": DUMMY,
            "DOC_WEB_OPENAI_API_KEY": DUMMY,
            "DOC_WEB_GEMINI_API_KEY": DUMMY,
            "DOC_WEB_LITERAL_OFFLINE": "1",
            "DOC_WEB_ENV_FILE": str(result_root / "no-credentials.env"),
            "DOC_WEB_LITERAL_CAMPAIGN_FILE": str(campaign),
            "PYTHONPATH": str(startup) + os.pathsep + str(ROOT),
        }
    )
    return env


@contextmanager
def stage_environment(env, stage):
    old = dict(os.environ)
    os.environ.clear()
    os.environ.update(env, DOC_WEB_LITERAL_STAGE=stage)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old)


def negative_export(h, case, arm, namespace, env, source_namespace=None):
    """The actual driver stops at review on retained ambiguous source evidence."""
    import yaml

    folder = h.RESULTS / namespace / f"hold-{case}-{arm}"
    folder.mkdir(parents=True, exist_ok=False)
    source = folder / "common-pages.jsonl"
    source_namespace = source_namespace or namespace
    row = json.loads(h.common_path(case, source_namespace).read_text().splitlines()[0])
    row["page_number"] = 1
    source.write_text(json.dumps(row) + "\n")
    record = h.RESULTS / source_namespace / f"reader-{case}-{arm}/native-record.json"
    retained = folder / "retained.json"
    write(
        retained,
        {
            "schema_version": "retained_source_reviews_v1",
            "model": h.MODELS[arm],
            "records": [
                {
                    "image_sha256": sha(Path(row["image"]).read_bytes()),
                    "record_path": str(record),
                    "record_sha256": sha(record.read_bytes()),
                }
            ],
        },
    )
    recipe = yaml.safe_load(
        (ROOT / "configs/recipes/recipe-pdf-literal-tables-html.yaml").read_text()
    )
    recipe["stages"] = recipe["stages"][1:]
    recipe["stages"][0] = {
        "id": "ocr_ai",
        "stage": "extract",
        "module": "load_artifact_v1",
        "out": "pages_html.jsonl",
        "params": {
            "path": str(source), "out": "pages_html.jsonl", "schema_version": "page_html_v1"
        },
    }
    recipe["stages"][1]["params"].update(
        model=h.MODELS[arm], source_review_receipts=str(retained)
    )
    recipe["stages"][-1]["params"]["literal_reader_model"] = h.MODELS[arm]
    path = folder / "recipe.yaml"
    path.write_text(yaml.safe_dump(recipe, sort_keys=False))
    runid = f"literal073-{namespace}-hold-{case}-{arm}"
    output = ROOT / "output/runs" / runid
    command = [
        sys.executable,
        "driver.py",
        "--recipe",
        str(path),
        "--run-id",
        runid,
        "--output-dir",
        str(output),
    ]
    with stage_environment(env, f"hold-{case}-{arm}"):
        result = subprocess.run(
            command,
            cwd=ROOT,
            env=dict(os.environ),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    (folder / "driver.log").write_text(result.stdout)
    # Inspect actual review report regardless of its current report filename.
    reviewed = output / "02_literal_table_review_v1/pages_html_reviewed.jsonl"
    if not reviewed.exists():
        reviewed_candidates = list(output.glob("**/pages_html_reviewed.jsonl"))
        if len(reviewed_candidates) != 1:
            raise RuntimeError("Negative driver did not preserve reviewed artifact")
        reviewed = reviewed_candidates[0]
    entry = json.loads(reviewed.read_text().splitlines()[0])
    report = read(entry["literal_fidelity"]["report_path"])
    final_manifest = output / "output/html/manifest.json"
    if (
        result.returncode == 0
        or "literal_table_review failed with code 2" not in result.stdout
        or report["status"] == "verified"
        or not any(t["review"]["uncertain_cells"] for t in report["tables"])
        or final_manifest.exists()
        or (
            output / "output/html/provenance/literal-fidelity/qualification.json"
        ).exists()
    ):
        raise RuntimeError("Ambiguous source was not held by the actual driver")
    proof = {
        "evidence_class": LABEL,
        "run_id": runid,
        "case": case,
        "arm": arm,
        "driver_returncode": result.returncode,
        "review_returncode": 2,
        "report_path": entry["literal_fidelity"]["report_path"],
        "report_sha256": sha(
            Path(entry["literal_fidelity"]["report_path"]).read_bytes()
        ),
        "status": report["status"],
        "manifest_absent": True,
        "additional_posts": 0,
        "command": command,
    }
    write(folder / "hold-proof.json", proof)
    return proof


def run_proof(result_root=None, namespace="offline"):
    if not re.fullmatch(r"offline(?:-[a-zA-Z0-9]+)*", namespace):
        raise ValueError("Offline output namespace required")
    sys.path.insert(0, str(ROOT))
    from benchmarks.scripts import qualify_argon_literal as h

    result_root = Path(result_root or h.RESULTS / "offline").resolve()
    if result_root.exists():
        raise RuntimeError("Fresh offline result root required; retain prior evidence")
    # Output/run IDs are also exclusive: never resume or overwrite earlier proof.
    run_pattern = re.compile(
        r"literal073-" + re.escape(namespace)
        + r"-(?:ocr-[NRA][123]|export-[NR]-(?:astra|argon)|hold-A[12]-(?:astra|argon))"
    )
    if any(run_pattern.fullmatch(path.name) for path in (ROOT / "output/runs").iterdir()):
        raise RuntimeError("Fresh offline run namespace required")
    result_root.mkdir(parents=True)
    h.RESULTS = result_root
    h.EVIDENCE = result_root / "evidence"
    h.prepare()
    # Provisional offline freeze is intentionally separate from any live freeze.
    config = read(h.EVIDENCE / "campaign.json")
    config["result_dir"] = str(result_root / "guard")
    config["evidence_class"] = LABEL
    (h.EVIDENCE / "campaign.json").write_text(json.dumps(config, indent=2) + "\n")
    frozen = read(h.EVIDENCE / "freeze.json")
    frozen.update(config=config, evidence_class=LABEL)
    (h.EVIDENCE / "freeze.json").write_text(json.dumps(frozen, indent=2) + "\n")
    for gate in ("screen-clearance.json", "panel-clearance.json"):
        write(
            h.EVIDENCE / gate,
            {"allowed": True, "evidence_class": LABEL, "live_authorization": False},
        )
    startup = result_root / "mock-startup"
    startup.mkdir()
    (startup / "sitecustomize.py").write_text(
        "import socket\n"
        "def deny(*args, **kwargs):\n    raise RuntimeError('Offline literal proof forbids socket connections')\n"
        "socket.socket.connect = deny\nsocket.socket.connect_ex = deny\nsocket.create_connection = deny\n"
        f"import sys\nsys.path.insert(0,{str(ROOT)!r})\n"
        "from benchmarks.scripts.literal_qualification_offline import install_backend\ninstall_backend()\n"
    )
    env = clean_environment(startup, h.EVIDENCE / "campaign.json", result_root)
    reviews = []
    for case in h.ORDER:
        with stage_environment(env, "ocr-" + case):
            h.ocr_case(case, namespace=namespace)
        arms = ["astra", "argon"] if case in h.ASTRA_FIRST else ["argon", "astra"]
        for arm in arms:
            with stage_environment(env, f"reader-{case}-{arm}"):
                metric = h.reader_case(case, arm, namespace=namespace)
            hold = case in ("A1", "A2")
            if (
                metric["returncode"] != (2 if hold else 0)
                or (metric["review_status"] == "verified") == hold
                or bool(metric["uncertain_cells"]) != hold
                or not metric["source_exact"]
            ):
                raise RuntimeError(
                    "Offline reader differs from frozen literal/uncertainty contract"
                )
            reviews.append(metric)
    return complete_exports(h, result_root, namespace, namespace, reviews, env)


def complete_exports(h, result_root, namespace, source_namespace, reviews, env):
    """Consume initial native receipts; no mock transport is expected here."""
    guard_path = result_root / "guard/ledger.json"
    before = len(read(guard_path)["calls"])
    if before != 24:
        raise RuntimeError("Actual guard did not count exactly 24 initial mock POSTs")
    exports = []
    for group in ("N", "R"):
        for arm in ("astra", "argon"):
            with stage_environment(env, f"export-{group}-{arm}"):
                h.export_group(group, arm, namespace=namespace, source_namespace=source_namespace)
            proof_path = (
                result_root / namespace / f"export-{group}-{arm}/export-proof.json"
            )
            exports.append(
                {
                    "group": group,
                    "arm": arm,
                    "proof": str(proof_path),
                    "proof_sha256": sha(proof_path.read_bytes()),
                }
            )
            if len(read(guard_path)["calls"]) != before:
                raise RuntimeError(
                    "Retained positive export unexpectedly performed inference"
                )
    holds = [
        negative_export(h, case, arm, namespace, env, source_namespace)
        for case in ("A1", "A2")
        for arm in ("astra", "argon")
    ]
    ledger = read(guard_path)
    events = [
        json.loads(line)
        for line in (result_root / "guard/mock-transport.jsonl")
        .read_text()
        .splitlines()
    ]
    if len(ledger["calls"]) != before or len(events) != before:
        raise RuntimeError("Driver retention performed an extra native POST")
    files = [p for p in result_root.rglob("*") if p.is_file()]
    summary = {
        "evidence_class": LABEL,
        "actual_provider_spend_usd": 0,
        "guard_mock_post_count": before,
        "ocr_mock_posts": 8,
        "reader_mock_posts": 16,
        "positive_exports": exports,
        "negative_holds": holds,
        "exports_additional_posts": 0,
        "holds_additional_posts": 0,
        "network_connections": 0,
        "initial_reviews": reviews,
        "synthetic_usage_guard_settlement_usd": ledger["spent_usd"],
        "source_manifest_sha256": sha((PANEL / "manifest.json").read_bytes()),
        "code_sha256": {
            "benchmarks/scripts/literal_qualification_offline.py": sha(
                Path(__file__).read_bytes()
            )
        },
        "artifact_sha256": {
            str(p.relative_to(result_root)): sha(p.read_bytes()) for p in files
        },
        "namespace": namespace,
        "initial_namespace": source_namespace,
        "reused_initial_native_receipts": namespace != source_namespace,
        "initial_producing_harness_sha256": read(result_root / "evidence/freeze.json")["code_sha256"][
            "benchmarks/scripts/qualify_argon_literal.py"
        ],
        "export_producing_harness_sha256": sha(Path(h.__file__).read_bytes()),
        "result_root": str(result_root),
    }
    write(result_root / "proof.json", summary)
    print(
        json.dumps(
            {
                "proof": str(result_root / "proof.json"),
                "actual_provider_spend_usd": 0,
                "guard_mock_posts": before,
                "positive_exports": len(exports),
                "negative_holds": len(holds),
            }
        )
    )
    return summary


def resume_exports(result_root, namespace, source_namespace):
    """Reuse an intact initial campaign after a bounded export-recipe correction."""
    for selected in (namespace, source_namespace):
        if not re.fullmatch(r"offline(?:-[a-zA-Z0-9]+)*", selected):
            raise ValueError("Offline output namespace required")
    if namespace == source_namespace:
        raise ValueError("A fresh export namespace is required")
    sys.path.insert(0, str(ROOT))
    from benchmarks.scripts import qualify_argon_literal as h

    result_root = Path(result_root).resolve()
    if (result_root / namespace).exists() or (result_root / "proof.json").exists():
        raise RuntimeError("Fresh export artifacts required")
    h.RESULTS, h.EVIDENCE = result_root, result_root / "evidence"
    frozen = read(h.EVIDENCE / "freeze.json")
    # Only the orchestrating export recipe may differ. Every native producer,
    # policy, guard, renderer, builder, module declaration and fixture is bound.
    for group in ("code_sha256", "fixture_sha256"):
        for relative, digest in frozen[group].items():
            if relative == "benchmarks/scripts/qualify_argon_literal.py":
                continue
            if sha((ROOT / relative).read_bytes()) != digest:
                raise RuntimeError("Initial source/native producing code changed: " + relative)
    config_path = h.EVIDENCE / "campaign.json"
    ledger = read(result_root / "guard/ledger.json")
    if ledger["config_sha256"] != sha(config_path.read_bytes()) or len(ledger["calls"]) != 24:
        raise RuntimeError("Initial guarded campaign incomplete or changed")
    reviews = [read(result_root / source_namespace / f"reader-{case}-{arm}/metrics.json")
               for case in h.ORDER for arm in ("astra", "argon")]
    for metric in reviews:
        hold = metric["case"] in ("A1", "A2")
        if (metric["returncode"] != (2 if hold else 0)
                or (metric["review_status"] == "verified") == hold
                or bool(metric["uncertain_cells"]) != hold or not metric["source_exact"]):
            raise RuntimeError("Initial offline reviews do not satisfy their frozen mock contract")
    env = clean_environment(result_root / "mock-startup", config_path, result_root)
    # Tiny maintained loader smoke exercises the explicit output-name contract
    # before consuming all four export groups. It performs no model inference.
    smoke = result_root / namespace / "loader-smoke/pages_html.jsonl"
    command = [sys.executable, "-m", "modules.common.load_artifact_v1.main",
               "--path", str(h.common_path("N1", source_namespace)), "--out", str(smoke),
               "--run-id", "literal073-" + namespace + "-loader-smoke"]
    with stage_environment(env, "loader-smoke"):
        result = subprocess.run(command, cwd=ROOT, env=dict(os.environ), text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    write(smoke.parent / "command.json", {"command": command, "returncode": result.returncode,
                                         "log": result.stdout, "evidence_class": LABEL})
    if result.returncode or not smoke.exists():
        raise RuntimeError("Explicit output-name loader smoke failed")
    return complete_exports(h, result_root, namespace, source_namespace, reviews, env)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-root", type=Path)
    parser.add_argument("--namespace", default="offline")
    parser.add_argument("--resume-initial", help="Consume this existing offline initial namespace without re-inference")
    args = parser.parse_args()
    if args.resume_initial:
        if args.result_root is None:
            parser.error("--result-root is required with --resume-initial")
        resume_exports(args.result_root, args.namespace, args.resume_initial)
    else:
        run_proof(args.result_root, args.namespace)


if __name__ == "__main__":
    main()
