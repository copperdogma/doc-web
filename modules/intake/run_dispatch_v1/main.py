import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

if __package__ in (None, ""):
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from modules.common.utils import save_jsonl
from modules.intake.intake_plan_utils import load_artifact_row, prepare_confirmed_handoff


REPO_ROOT = Path(__file__).resolve().parents[3]


def resolve_plan_path(plan_path: str | None, dispatch_hint_path: str | None) -> str:
    if plan_path:
        return plan_path
    if not dispatch_hint_path:
        raise SystemExit("Must provide --plan or --dispatch-hint")
    with open(dispatch_hint_path, "r", encoding="utf-8") as handle:
        hint = json.load(handle)
    resolved = str(hint.get("plan_path") or "").strip()
    if not resolved:
        raise SystemExit("dispatch_hint is missing plan_path")
    return resolved


def main():
    parser = argparse.ArgumentParser(description="Launch a maintained explicit recipe from an approved intake plan")
    parser.add_argument("--plan", default=None)
    parser.add_argument("--dispatch-hint", "--dispatch_hint", dest="dispatch_hint", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--outdir", default=None)
    parser.add_argument("--run-id", dest="run_id", default=None)
    parser.add_argument("--downstream-run-id", dest="downstream_run_id", default=None)
    parser.add_argument("--downstream-end-at", dest="downstream_end_at", default=None)
    parser.add_argument("--allow-run-id-reuse", action="store_true")
    parser.add_argument("--dry-run", "--dry_run", dest="dry_run", action="store_true", help="Write the handoff artifact but do not execute the downstream recipe")
    parser.add_argument("--state-file", dest="state_file", default=None)
    parser.add_argument("--progress-file", dest="progress_file", default=None)
    args, _unknown = parser.parse_known_args()

    out_path = args.out
    if not out_path and args.outdir:
        out_path = str(Path(args.outdir) / "intake_handoff.jsonl")
    if not out_path:
        raise SystemExit("Must provide --out or --outdir")

    plan_path = resolve_plan_path(args.plan, args.dispatch_hint)
    plan = load_artifact_row(plan_path)
    handoff_row, driver_command, should_launch = prepare_confirmed_handoff(
        plan,
        plan_path=plan_path,
        upstream_run_id=args.run_id,
        downstream_run_id=args.downstream_run_id,
        downstream_end_at=args.downstream_end_at,
        dry_run=args.dry_run,
        allow_run_id_reuse=args.allow_run_id_reuse,
    )

    exit_code = 0
    if should_launch:
        print("Dispatching:", " ".join(driver_command))
        result = subprocess.run(driver_command, cwd=str(REPO_ROOT))
        handoff_row["exit_code"] = result.returncode
        if result.returncode == 0:
            handoff_row["terminal_outcome"] = "launched"
        else:
            handoff_row["terminal_outcome"] = "failed"
            handoff_row["terminal_reason"] = f"downstream_exit_{result.returncode}"
            exit_code = result.returncode
    elif driver_command:
        print("Dispatching:", " ".join(driver_command))
        if args.dry_run:
            print("Dry run: not executing downstream recipe")
        else:
            print(f"Handoff {handoff_row['terminal_outcome']}: {handoff_row['terminal_reason']}")
    else:
        print(f"Handoff {handoff_row['terminal_outcome']}: {handoff_row['terminal_reason']}")

    save_jsonl(out_path, [handoff_row])
    print(json.dumps(handoff_row, indent=2))
    if exit_code:
        raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
