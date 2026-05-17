import argparse
import json
import time
from pathlib import Path

from doc_web.runtime_contract import build_runtime_contract


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="doc-web runtime utility surface")
    subparsers = parser.add_subparsers(dest="command")

    contract_parser = subparsers.add_parser(
        "contract",
        help="Emit the machine-readable runtime contract for pinned consumers.",
    )
    contract_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON only.",
    )

    preview_parser = subparsers.add_parser(
        "preview",
        help="Build a latency-bound, non-final doc-web preview bundle.",
    )
    preview_parser.add_argument(
        "--input", required=True, help="Raw source document path."
    )
    preview_parser.add_argument(
        "--out-dir", required=True, help="Output preview bundle directory."
    )
    preview_parser.add_argument(
        "--max-sample-units",
        type=int,
        default=3,
        help="Maximum pages or entries to sample.",
    )
    preview_parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=8.0,
        help="Hard synchronous timeout.",
    )
    preview_parser.add_argument(
        "--usable-deadline-seconds",
        type=float,
        default=3.0,
        help="Target deadline for usable or honestly deferred preview output.",
    )
    preview_parser.add_argument("--max-chars-per-block", type=int, default=1200)
    preview_parser.add_argument(
        "--content-hint-mode",
        choices=["auto", "ai", "deterministic"],
        default="auto",
        help=(
            "How to produce high-level content hints. 'auto' uses a bounded "
            "cheap-model pass when DOC_WEB_OPENAI_API_KEY is configured, then "
            "falls back to deterministic hints."
        ),
    )
    preview_parser.add_argument(
        "--content-hint-model",
        default="gpt-4.1-nano",
        help="OpenAI model for ai/auto content hints.",
    )
    preview_parser.add_argument(
        "--content-hint-timeout-seconds",
        type=float,
        default=0.75,
        help="Timeout for the optional AI content-hint call.",
    )
    preview_parser.add_argument("--run-id", default=None)
    preview_parser.add_argument(
        "--json", action="store_true", help="Emit JSON summary only."
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "contract":
        payload = build_runtime_contract()
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            return
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return

    if args.command == "preview":
        from doc_web.preview import build_preview
        from doc_web.preview_support import PreviewTimeout, STATUS_PATH

        started_at = time.perf_counter()
        try:
            payload = build_preview(
                input_path=Path(args.input),
                out_dir=Path(args.out_dir),
                max_sample_units=args.max_sample_units,
                timeout_seconds=args.timeout_seconds,
                usable_deadline_seconds=args.usable_deadline_seconds,
                max_chars_per_block=args.max_chars_per_block,
                content_hint_mode=args.content_hint_mode,
                content_hint_model=args.content_hint_model,
                content_hint_timeout_seconds=args.content_hint_timeout_seconds,
                run_id=args.run_id,
            )
        except PreviewTimeout as exc:
            out_dir = Path(args.out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            failure_reason = getattr(exc, "failure_reason", "timeout")
            failed_event = {
                "stage": "failed",
                "elapsed_ms": round((time.perf_counter() - started_at) * 1000, 3),
                "message": str(exc),
                "artifact": None,
                "detail": {"reason": failure_reason},
            }
            (out_dir / STATUS_PATH).write_text(
                json.dumps(failed_event, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            payload = {
                "status": "failed",
                "error": str(exc),
                "status_path": STATUS_PATH,
            }
            print(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=None if args.json else 2,
                )
            )
            raise SystemExit(1) from None
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            return
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
