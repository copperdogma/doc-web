import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "providers"))
import sonnet55_guard

sonnet55_guard.install()
