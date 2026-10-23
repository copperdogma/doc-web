#!/usr/bin/env python3
"""Run a command with doc-web-local provider keys mapped for child tools.

Library code should accept explicit clients/config. This script is only the
repo-local app boundary for CLIs such as promptfoo that require provider-standard
environment variable names.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from doc_web.env import (
    CHILD_KEY_BY_PROVIDER,
    DEFAULT_ENV_FILE,
    DOC_WEB_KEY_BY_PROVIDER,
    build_child_env,
)


def main(argv: list[str]) -> int:
    if not argv:
        mappings = ", ".join(
            f"{local_key}->{CHILD_KEY_BY_PROVIDER[provider]}"
            for provider, local_key in DOC_WEB_KEY_BY_PROVIDER.items()
        )
        print(
            "Usage: scripts/run_with_doc_web_env.py <command> [args...]\n"
            f"Loads {DEFAULT_ENV_FILE} and maps: {mappings}",
            file=sys.stderr,
        )
        return 2

    try:
        child_env = build_child_env()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    return subprocess.run(argv, env=child_env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
