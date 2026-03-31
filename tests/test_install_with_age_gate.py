from __future__ import annotations

from datetime import datetime, timezone

import pytest

from doc_web.install_with_age_gate import build_install_command, cutoff_timestamp


def test_cutoff_timestamp_uses_utc_and_truncates_microseconds() -> None:
    now = datetime(2026, 3, 31, 18, 4, 5, 987654, tzinfo=timezone.utc)

    assert cutoff_timestamp(7, now=now) == "2026-03-24T18:04:05Z"


def test_build_install_command_prefers_uv_when_available() -> None:
    command = build_install_command(
        ["-r", "requirements.txt"],
        installer="auto",
        age_days=7,
        uv_path="/opt/homebrew/bin/uv",
    )

    assert command[:4] == [
        "/opt/homebrew/bin/uv",
        "pip",
        "install",
        "--exclude-newer",
    ]
    assert command[-2:] == ["-r", "requirements.txt"]


def test_build_install_command_falls_back_to_supported_pip() -> None:
    command = build_install_command(
        [".", ".[driver]"],
        installer="pip",
        age_days=7,
        pip_has_uploaded_prior_to=True,
        python_executable="/usr/bin/python3",
    )

    assert command[:5] == [
        "/usr/bin/python3",
        "-m",
        "pip",
        "install",
        "--uploaded-prior-to",
    ]
    assert command[-2:] == [".", ".[driver]"]


def test_build_install_command_rejects_missing_supported_installer() -> None:
    with pytest.raises(RuntimeError, match="no supported age-gated installer found"):
        build_install_command(
            ["."],
            installer="pip",
            age_days=7,
            pip_has_uploaded_prior_to=False,
        )


def test_build_install_command_requires_install_arguments() -> None:
    with pytest.raises(ValueError, match="provide at least one package"):
        build_install_command([], installer="auto")
