import argparse
import json
import shutil
import os
from datetime import datetime
from pathlib import Path


def _stamp_envelope(path: str, run_id: str) -> None:
    """Overwrite run_id and created_at on each JSONL record with current run context."""
    if not path.endswith(".jsonl"):
        return
    try:
        rows = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if run_id:
                    row["run_id"] = run_id
                row["created_at"] = datetime.utcnow().isoformat() + "Z"
                rows.append(row)
        with open(path, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass  # Not a valid JSONL file; skip stamping


def _copy_sibling_dirs(source_artifact: str, out_path: str, sibling_dirs: list[str]) -> None:
    source_parent = Path(source_artifact).parent
    dest_parent = Path(out_path).parent
    for sibling in sibling_dirs:
        name = (sibling or "").strip().strip("/\\")
        if not name:
            continue
        src_dir = source_parent / name
        if not src_dir.is_dir():
            continue
        dst_dir = dest_parent / name
        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
        print(f"Copied sibling directory {src_dir} to {dst_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--out")
    parser.add_argument("--outdir")
    parser.add_argument("--schema-version", dest="schema_version")
    parser.add_argument("--schema_version", dest="schema_version")
    parser.add_argument("--copy-sibling-dir", dest="copy_sibling_dirs", action="append", default=[],
                        help="Optional sibling directory beside the source artifact to copy beside the output artifact; repeatable.")
    parser.add_argument("--run-id")
    parser.add_argument("--state-file")
    parser.add_argument("--progress-file")
    args, unknown = parser.parse_known_args()

    out_path = args.out
    if out_path and args.outdir and not os.path.isabs(out_path):
        out_path = os.path.join(args.outdir, out_path)

    if not out_path and args.outdir:
        # If --out is not provided but --outdir is, use the filename from --path
        out_path = os.path.join(args.outdir, os.path.basename(args.path))

    if not out_path:
        raise ValueError("Either --out or --outdir must be provided")

    if not os.path.exists(args.path):
        raise FileNotFoundError(f"Source artifact not found: {args.path}")

    if os.path.abspath(args.path) != os.path.abspath(out_path):
        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        shutil.copy2(args.path, out_path)
        print(f"Copied {args.path} to {out_path}")
    else:
        print(f"Artifact already at {out_path}")

    if args.copy_sibling_dirs:
        _copy_sibling_dirs(args.path, out_path, args.copy_sibling_dirs)

    # Stamp current run's envelope on copied JSONL records
    _stamp_envelope(out_path, args.run_id)

if __name__ == "__main__":
    main()
