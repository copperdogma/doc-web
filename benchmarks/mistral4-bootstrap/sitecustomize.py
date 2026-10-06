import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"providers"))
import mistral4_guard
mistral4_guard.install()
