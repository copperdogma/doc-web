"""Attempt036 heartbeat1 owner adapter binding; same frozen request contract."""
import sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parent))
import deepseek_v41_budgeted as campaign

def call_api(prompt, options, context):
    if datetime.now(timezone.utc) >= datetime.fromisoformat("2026-09-13T23:54:06+00:00"):
        return {"error": "Authorized retry deadline elapsed"}
    campaign.RESULTS = Path(__file__).resolve().parents[1] / "results/deepseek-v41-20260912-heartbeat1"
    return campaign.call_api(prompt, options, context)
