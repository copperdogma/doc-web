"""Local environment handling for doc-web runnable tools.

Reusable library code should prefer explicit clients or config. This module is
the repo-local boundary for command-line tools that need doc-web-scoped keys and
for subprocesses that require provider-standard environment variable names.
"""

from __future__ import annotations

import os
import shlex
from pathlib import Path
from typing import Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = REPO_ROOT / ".env"

DOC_WEB_KEY_BY_PROVIDER = {
    "openai": "DOC_WEB_OPENAI_API_KEY",
    "anthropic": "DOC_WEB_ANTHROPIC_API_KEY",
    "gemini": "DOC_WEB_GEMINI_API_KEY",
}

CHILD_KEY_BY_PROVIDER = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

STALE_GOOGLE_KEY = "GOOGLE_API_KEY"


def parse_dotenv(path: Path) -> dict[str, str]:
    """Parse a small dotenv file without executing shell code."""
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for lineno, raw in enumerate(path.read_text().splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        lexer = shlex.shlex(line, posix=True)
        lexer.whitespace_split = True
        lexer.commenters = "#"
        tokens = list(lexer)
        if tokens and tokens[0] == "export":
            tokens = tokens[1:]

        if len(tokens) != 1 or "=" not in tokens[0]:
            raise ValueError(f"{path}:{lineno}: expected KEY=VALUE")

        key, value = tokens[0].split("=", 1)
        key = key.strip()
        if not key or not key.replace("_", "A").isalnum() or key[0].isdigit():
            raise ValueError(f"{path}:{lineno}: invalid env var name {key!r}")
        values[key] = value

    return values


def build_doc_web_env(
    env: Mapping[str, str] | None = None,
    env_file: Path = DEFAULT_ENV_FILE,
) -> dict[str, str]:
    """Return env plus repo-local .env defaults, without provider remapping."""
    merged = dict(os.environ if env is None else env)
    for key, value in parse_dotenv(env_file).items():
        merged.setdefault(key, value)
    return merged


def get_doc_web_api_key(
    provider: str,
    *,
    env: Mapping[str, str] | None = None,
    env_file: Path = DEFAULT_ENV_FILE,
) -> str | None:
    """Return the doc-web-scoped API key for a provider, if configured."""
    key_name = DOC_WEB_KEY_BY_PROVIDER[provider]
    return build_doc_web_env(env=env, env_file=env_file).get(key_name) or None


def build_child_env(env_file: Path = DEFAULT_ENV_FILE) -> dict[str, str]:
    """Map doc-web-scoped keys to child-process provider keys."""
    child_env = build_doc_web_env(env_file=env_file)

    for provider, local_key in DOC_WEB_KEY_BY_PROVIDER.items():
        local_value = child_env.get(local_key)
        if local_value:
            child_env[CHILD_KEY_BY_PROVIDER[provider]] = local_value

    # Avoid an old global/deleted Google key shadowing the doc-web Gemini key in
    # code paths that prefer Google's broader environment variable first.
    if child_env.get(DOC_WEB_KEY_BY_PROVIDER["gemini"]):
        child_env.pop(STALE_GOOGLE_KEY, None)

    return child_env
