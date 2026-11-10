"""Owner wrapper continuation with exactly one temporary evaluation key override."""

import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from doc_web.env import parse_dotenv

if __name__ == "__main__":
    env = dict(os.environ)
    values = parse_dotenv(Path(__file__).resolve().parents[2] / ".env")
    assert set(values) == {"DOC_WEB_OPENROUTER_API_KEY"}
    env["OPENROUTER_API_KEY"] = values["DOC_WEB_OPENROUTER_API_KEY"]
    env["DOC_WEB_OPENROUTER_API_KEY"] = values["DOC_WEB_OPENROUTER_API_KEY"]
    raise SystemExit(subprocess.run(sys.argv[1:], env=env).returncode)
