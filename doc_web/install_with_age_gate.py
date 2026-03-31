from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import Sequence

DEFAULT_MIN_RELEASE_AGE_DAYS = 7
MIN_RELEASE_AGE_ENV_VAR = "DOC_WEB_MIN_RELEASE_AGE_DAYS"


def cutoff_timestamp(age_days: int, *, now: datetime | None = None) -> str:
    if age_days < 0:
        raise ValueError("age_days must be non-negative")
    current = now or datetime.now(timezone.utc)
    cutoff = current - timedelta(days=age_days)
    return cutoff.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pip_supports_uploaded_prior_to(
    python_executable: str = sys.executable,
) -> bool:
    result = subprocess.run(
        [python_executable, "-m", "pip", "help", "install"],
        check=False,
        capture_output=True,
        text=True,
    )
    help_text = "\n".join(part for part in (result.stdout, result.stderr) if part)
    return "--uploaded-prior-to" in help_text


def build_install_command(
    install_args: Sequence[str],
    *,
    installer: str = "auto",
    age_days: int = DEFAULT_MIN_RELEASE_AGE_DAYS,
    python_executable: str = sys.executable,
    uv_path: str | None = None,
    pip_has_uploaded_prior_to: bool | None = None,
) -> list[str]:
    if not install_args:
        raise ValueError("provide at least one package or install flag")

    cutoff = cutoff_timestamp(age_days)

    if installer not in {"auto", "uv", "pip"}:
        raise ValueError(f"unsupported installer: {installer}")

    if installer in {"auto", "uv"}:
        resolved_uv = uv_path or shutil.which("uv")
        if resolved_uv:
            return [resolved_uv, "pip", "install", "--exclude-newer", cutoff, *install_args]
        if installer == "uv":
            raise RuntimeError("uv is not installed or not on PATH")

    pip_supported = (
        pip_has_uploaded_prior_to
        if pip_has_uploaded_prior_to is not None
        else pip_supports_uploaded_prior_to(python_executable)
    )
    if pip_supported:
        return [
            python_executable,
            "-m",
            "pip",
            "install",
            "--uploaded-prior-to",
            cutoff,
            *install_args,
        ]

    raise RuntimeError(
        "no supported age-gated installer found; install uv or upgrade pip to a version "
        "that supports --uploaded-prior-to"
    )


def parse_args(argv: Sequence[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description=(
            "Install Python dependencies with a minimum release-age cutoff. "
            "Unknown arguments are forwarded to the underlying installer."
        )
    )
    parser.add_argument(
        "--age-days",
        type=int,
        default=int(os.environ.get(MIN_RELEASE_AGE_ENV_VAR, DEFAULT_MIN_RELEASE_AGE_DAYS)),
        help=(
            "Reject releases newer than this many days. "
            f"Defaults to ${MIN_RELEASE_AGE_ENV_VAR} or {DEFAULT_MIN_RELEASE_AGE_DAYS}."
        ),
    )
    parser.add_argument(
        "--installer",
        choices=("auto", "uv", "pip"),
        default="auto",
        help="Choose uv, pip, or auto-detect. Auto prefers uv when available.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved installer command instead of executing it.",
    )
    return parser.parse_known_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args, install_args = parse_args(argv or sys.argv[1:])

    try:
        command = build_install_command(
            install_args,
            installer=args.installer,
            age_days=args.age_days,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(shlex.join(command))
        return 0

    result = subprocess.run(command, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
