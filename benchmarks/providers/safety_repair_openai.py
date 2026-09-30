"""GPT-6.1 Sol campaign wrapper around the owner Responses adapter."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import safety_repair_guard as guard
import openai_responses_model as owner


def call_api(prompt, options, context):
    os.environ["SAFETY_REPAIR_RECOVERY"] = (
        "1" if context.get("vars", {}).get("safety_recovery") is True else "0"
    )
    os.environ["SAFETY_REPAIR_CASE"] = str(
        context.get("vars", {}).get(
            "safety_case_id", context.get("vars", {}).get("crop_key", "unknown")
        )
    )
    guard.install()
    model = owner._request_settings(options)["model"]
    for name, value in zip(
        ("INPUT", "CACHED_INPUT", "CACHE_WRITE", "OUTPUT"), guard.PRICES[model]
    ):
        os.environ[f"OPENAI_RESPONSES_{name}_PRICE_PER_1M"] = str(value)
    return owner.call_api(prompt, options, context)
