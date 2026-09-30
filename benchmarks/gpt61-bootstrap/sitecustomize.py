"""Install the GPT-6.1 evaluation guard in actual driver processes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "providers"))
import gpt61_guard
gpt61_guard.install()
