import argparse
import json

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

    parser.print_help()
