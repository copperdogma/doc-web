import argparse
import json
import os
import sys
from pathlib import Path


if "tools" in os.path.dirname(__file__):
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.common.run_registry import (
    registry_paths,
    check_run_reuse,
    record_run_assessment,
    record_run_health,
    resolve_output_root,
)


def _print(payload):
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _candidate_output_roots(raw_output_root: str | None) -> list[str]:
    candidates: list[str] = []
    if raw_output_root:
        raw = Path(raw_output_root)
        resolved = raw.resolve(strict=False) if raw.is_absolute() else (Path.cwd() / raw).resolve(strict=False)
        candidates.append(str(resolved))

    auto_root = str(Path(resolve_output_root(cwd=os.getcwd())).resolve(strict=False))
    if auto_root not in candidates:
        candidates.append(auto_root)
    return candidates


def _resolve_run_dir(args) -> str | None:
    if args.run_dir:
        return args.run_dir
    if not args.run_id:
        return None
    for output_root in _candidate_output_roots(args.output_root):
        candidate = Path(output_root) / "runs" / args.run_id
        if candidate.exists():
            return str(candidate.resolve(strict=False))
    return None


def _resolve_output_root_arg(args, run_dir: str | None) -> str:
    if run_dir:
        return resolve_output_root(run_dir=run_dir, cwd=os.getcwd())

    candidates = _candidate_output_roots(args.output_root)
    if args.run_id:
        for output_root in candidates:
            if (Path(output_root) / "runs" / args.run_id).exists():
                return output_root

    for output_root in candidates:
        paths = registry_paths(output_root)
        if any(Path(path).exists() for path in paths.values()):
            return output_root

    return candidates[0]


def main():
    parser = argparse.ArgumentParser(description="Manage shared run health and assessment registries.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    health_parser = subparsers.add_parser("record-health", help="Compute and append run health for a run.")
    health_parser.add_argument("--run-id", required=True)
    health_parser.add_argument("--run-dir")
    health_parser.add_argument("--output-root")

    assess_parser = subparsers.add_parser("record-assessment", help="Append an AI review assessment for a run.")
    assess_parser.add_argument("--run-id", required=True)
    assess_parser.add_argument("--run-dir")
    assess_parser.add_argument("--output-root")
    assess_parser.add_argument("--scope", required=True)
    assess_parser.add_argument("--status", required=True, choices=["known_good", "partial", "unsafe", "superseded"])
    assess_parser.add_argument("--summary", required=True)
    assess_parser.add_argument("--document")
    assess_parser.add_argument("--source-story")
    assess_parser.add_argument("--source-issue")
    assess_parser.add_argument("--author", default="ai")
    assess_parser.add_argument("--finding", action="append", default=[])
    assess_parser.add_argument("--evidence", action="append", default=[])
    assess_parser.add_argument("--supersedes", action="append", default=[])

    check_parser = subparsers.add_parser("check-reuse", help="Check whether a run is safe to reuse for a scope.")
    check_parser.add_argument("--run-id", required=True)
    check_parser.add_argument("--scope", required=True)
    check_parser.add_argument("--run-dir")
    check_parser.add_argument("--output-root")

    args = parser.parse_args()
    run_dir = _resolve_run_dir(args)
    output_root = _resolve_output_root_arg(args, run_dir)

    if args.command == "record-health":
        if not run_dir:
            parser.error("record-health requires --run-dir or an existing --output-root/--run-id pair")
        path, entry = record_run_health(args.run_id, run_dir, state_path=os.path.join(run_dir, "pipeline_state.json"))
        _print({"registry_path": path, "entry": entry})
        return

    if args.command == "record-assessment":
        path, entry = record_run_assessment(
            run_id=args.run_id,
            run_dir=run_dir,
            output_root=output_root,
            scope=args.scope,
            status=args.status,
            summary=args.summary,
            document=args.document,
            source_story=args.source_story,
            source_issue=args.source_issue,
            author=args.author,
            findings=args.finding,
            evidence_paths=args.evidence,
            supersedes=args.supersedes,
        )
        _print({"registry_path": path, "entry": entry})
        return

    if args.command == "check-reuse":
        result = check_run_reuse(
            run_id=args.run_id,
            scope=args.scope,
            output_root=output_root,
            run_dir=run_dir,
        )
        _print(result)
        return


if __name__ == "__main__":
    main()
