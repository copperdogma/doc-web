"""Explicit Scout107 caller evaluation; offline by default, never real authority.

--execute requests exactly the two approved native subjects through the parent
combined wallet. Saved live pairs can then be replayed for mechanics variants.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules.common import crop_safety as safety  # noqa: E402
from modules.common.crop_safety_fable_eval import CONTRACT, ENV  # noqa: E402
from modules.common.crop_review import digest, require  # noqa: E402
from modules.common.utils import read_jsonl  # noqa: E402
from tools.prepare_crop_safety_runtime_fixture import prepare  # noqa: E402


def synthetic_envelope(arm, case):
    answer = {
        "verdict": "fail" if case == "S3" else "pass",
        "has_page_text": False,
        "excessive_blank": False,
        "reason": "Synthetic uncertain ownership requires review"
        if case == "S3"
        else "Synthetic badge lettering is integral",
    }
    if arm == "fable":
        return {
            "id": "msg_synthetic_test_only_" + case,
            "type": "message",
            "role": "assistant",
            "model": "claude-fable-5-2",
            "stop_reason": "end_turn",
            "content": [{"type": "text", "text": json.dumps(answer)}],
            "usage": {
                "input_tokens": 100,
                "output_tokens": 100,
                "service_tier": "standard",
                "speed": "standard",
            },
        }
    value = json.loads(
        (ROOT / "tests/fixtures/crop_review_offline/saved-S3-pass.json").read_text()
    )
    value["id"] = "resp_synthetic_test_only_" + case
    value["service_tier"] = "default"
    next(x for x in value["output"] if x["type"] == "message")["content"][0]["text"] = (
        json.dumps(answer)
    )
    return value


def contract_environment(arm, *, execute=False, saved_live=False):
    env = dict(os.environ)
    for key in (
        ENV,
        "DOC_WEB_SAFETY_QUAL_088_TRANSPORT",
        "DOC_WEB_SAFETY_QUAL_088_REPLAY_LIVE",
        "DOC_WEB_SAFETY_QUAL_088_CONTEXT",
        "DOC_WEB_SAFETY_QUAL_088_REQUIRE_ANCHOR",
    ):
        env.pop(key, None)
    env["DOC_WEB_SAFETY_QUAL_088_CONTEXT"] = "1"
    if arm == "fable":
        env[ENV] = CONTRACT
    if execute or saved_live:
        env["DOC_WEB_SAFETY_QUAL_088_REQUIRE_ANCHOR"] = "1"
    if execute:
        env["DOC_WEB_SAFETY_QUAL_088_TRANSPORT"] = "1"
    if saved_live:
        env["DOC_WEB_SAFETY_QUAL_088_REPLAY_LIVE"] = "1"
    return env


def make_mapping(fixture, arm, disposition, saved_live):
    """Retain genuine pairs unchanged, except a labelled synthetic error variant."""
    custody = fixture / "custody"
    directory = fixture / "qualification-replay"
    directory.mkdir()
    entries = []
    rows = list(read_jsonl(custody / "manifest.jsonl"))
    for i, row in enumerate(rows, 1):
        case = "S3" if row["source_page"] == 1 else "S4"
        request = directory / f"request-{i:03d}.json"
        response = directory / f"response-{i:03d}.json"
        expected = safety.build_request(
            custody / row["source_image"],
            custody / "images" / row["filename"],
            live=bool(saved_live),
        )
        if saved_live:
            source = Path(saved_live) / "custody/native-receipts"
            shutil.copyfile(source / request.name, request)
            shutil.copyfile(source / response.name, response)
            require(
                json.loads(request.read_text()) == expected,
                "Saved-live request is not exact current contract",
            )
        else:
            request.write_text(json.dumps(expected, sort_keys=True))
            response.write_text(json.dumps(synthetic_envelope(arm, case)))
        if disposition == "error" and i == 1:
            value = json.loads(response.read_text())
            if arm == "fable":
                value["stop_reason"] = "max_tokens"
            else:
                value["status"] = "incomplete"
                value["incomplete_details"] = {"reason": "max_output_tokens"}
            response.write_text(json.dumps(value))
        entries.append(
            {
                "filename": row["filename"],
                "request_path": request.name,
                "request_sha256": digest(request),
                "response_path": response.name,
                "response_sha256": digest(response),
                "status_code": 200,
            }
        )
    mode = "mock" if disposition == "error" or not saved_live else "replay"
    mapping = directory / "mapping.json"
    mapping.write_text(json.dumps({"mode": mode, "entries": entries}, indent=2) + "\n")
    return mode, mapping


def run(arm, run_id, *, execute=False, disposition="approved", saved_live=None):
    require(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", run_id) is not None,
        "Safe fresh caller run identity required",
    )
    if saved_live:
        saved_path = Path(saved_live).absolute()
        require(
            saved_path.resolve().is_relative_to(ROOT / "output/runs")
            and not any(p.is_symlink() for p in (saved_path, *saved_path.parents)),
            "Saved-live fixture must remain in owner run custody",
        )
    require(
        not (execute and (saved_live or disposition != "approved")),
        "Only baseline approved mechanics may dispatch subjects",
    )
    fixture = ROOT / "output/runs" / (run_id + "-fixture")
    out = ROOT / "output/runs" / run_id
    require(
        not fixture.exists() and not out.exists(),
        "Fresh caller evaluation paths required",
    )
    env = contract_environment(arm, execute=execute, saved_live=bool(saved_live))
    # Request construction below reads the same explicit subprocess contract.
    previous = dict(os.environ)
    try:
        os.environ.clear()
        os.environ.update(env)
        prepare(fixture, run_id, disposition="approved")
        review_path = fixture / "synthetic-review.json"
        review = json.loads(review_path.read_text())
        if disposition in ("held", "recrop"):
            review["decisions"][0].update(
                action="unresolved_ownership"
                if disposition == "held"
                else "require_recrop",
                reason="Synthetic mechanics veto; not model quality or Cam authority",
            )
            review_path.write_text(json.dumps(review, indent=2) + "\n")
        mode, mapping = (
            ("live", None)
            if execute
            else make_mapping(fixture, arm, disposition, saved_live)
        )
        recipe = yaml.safe_load(
            (
                ROOT / "configs/recipes/story-242-sol-crop-safety-offline.yaml"
            ).read_text()
        )
        recipe["input"]["text_glob"] = str(fixture / "synthetic-authority.json")
        for stage in recipe["stages"]:
            for key, value in stage.get("params", {}).items():
                if isinstance(value, str) and value.startswith(
                    "output/runs/story242-crop-safety-fixture"
                ):
                    stage["params"][key] = str(
                        fixture
                        / Path(value).relative_to(
                            "output/runs/story242-crop-safety-fixture"
                        )
                    )
            if stage["id"] == "propose_safety":
                stage["params"].update(
                    mode=mode, cap_usd=2 * safety.reservation_usd(), max_calls=2
                )
                stage["params"].pop("replay_manifest", None)
                if mapping:
                    stage["params"]["replay_manifest"] = str(mapping)
            if stage["id"] == "build_reviewed":
                stage["params"]["crop_review_release"] = str(
                    out / "05_release_reviewed_crops_v1/crop_review_release.json"
                )
        config = fixture / "recipe.yaml"
        config.write_text(yaml.safe_dump(recipe, sort_keys=False))
    finally:
        os.environ.clear()
        os.environ.update(previous)
    base = [
        sys.executable,
        "driver.py",
        "--recipe",
        str(config),
        "--run-id",
        run_id,
        "--output-dir",
        str(out),
    ]
    with (fixture / "driver-proposals.log").open("w") as log:
        first = subprocess.run(
            base + ["--end-at", "propose_safety"],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        ).returncode
    proposal_file = out / "03_propose_crop_safety_v1/proposals.jsonl"
    rows = list(read_jsonl(proposal_file)) if proposal_file.exists() else []
    require(
        not (fixture / "custody/authority.json").exists(),
        "Operator intervention preceded model scoring",
    )
    policy = []
    for row in rows:
        case = "S3" if row["binding"]["source_page"] == 1 else "S4"
        answer = row.get("answer")
        policy.append(
            {
                "case": case,
                "expected_model_verdict": "fail" if case == "S3" else "pass",
                "answer_before_operator": answer,
                "status": row["status"],
                "verdict_and_flags_pass": bool(
                    answer
                    and answer["verdict"] == ("fail" if case == "S3" else "pass")
                    and answer["has_page_text"] is False
                    and answer["excessive_blank"] is False
                ),
                "grounded_reason_review": "manual source-first review required; no operator action can repair model semantics",
            }
        )
    (fixture / "model-policy-before-operator.json").write_text(
        json.dumps(
            {
                "arm": arm,
                "live_subjects": execute,
                "saved_live_replay": bool(saved_live),
                "synthetic_authority_only": True,
                "cases": policy,
            },
            indent=2,
        )
        + "\n"
    )
    final = first
    if first == 0:
        # Explicitly reuse already captured proposals. No provider invocation is
        # repeated when the real driver resumes at finalization.
        resume_env = dict(env)
        resume_env.pop("DOC_WEB_SAFETY_QUAL_088_TRANSPORT", None)
        with (fixture / "driver-review-build.log").open("w") as log:
            final = subprocess.run(
                base + ["--allow-run-id-reuse", "--start-from", "finalize_review"],
                cwd=ROOT,
                env=resume_env,
                stdout=log,
                stderr=subprocess.STDOUT,
            ).returncode
    html = out / "output/html/chapter-001.html"
    manifest = out / "05_release_reviewed_crops_v1/illustration_manifest.jsonl"
    expected_success = disposition == "approved"
    require(
        (final == 0) == expected_success,
        "Actual driver disposition differs from expected mechanics",
    )
    if expected_success:
        require(
            html.is_file() and manifest.is_file(), "Driver omitted approved artifacts"
        )
        text = html.read_text()
        require(
            text.count('src="images/S3.png"') == 1
            and text.count('src="images/S4.png"') == 1
            and "Text-only source page" in text,
            "Actual built HTML lost assets or zero-candidate source",
        )
        for name in ("S3.png", "S4.png"):
            require(
                digest(out / "output/html/images" / name)
                == digest(fixture / "custody/images" / name),
                "Built image pixels differ from native crop",
            )
    else:
        require(
            not html.exists() and not manifest.exists(),
            "Held/error mechanics published assets",
        )
    summary = {
        "arm": arm,
        "run_id": run_id,
        "fixture": str(fixture),
        "output": str(out),
        "mode": mode,
        "disposition": disposition,
        "first_driver_exit": first,
        "final_driver_exit": final,
        "synthetic_authority_only": True,
        "model_policy": str(fixture / "model-policy-before-operator.json"),
        "mechanics_pass": True,
    }
    (fixture / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--arm", choices=("fable", "sol"), required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--execute", action="store_true")
    p.add_argument(
        "--disposition",
        choices=("approved", "held", "recrop", "error"),
        default="approved",
    )
    p.add_argument("--saved-live-fixture")
    args = p.parse_args()
    print(
        json.dumps(
            run(
                args.arm,
                args.run_id,
                execute=args.execute,
                disposition=args.disposition,
                saved_live=args.saved_live_fixture,
            ),
            indent=2,
        )
    )
