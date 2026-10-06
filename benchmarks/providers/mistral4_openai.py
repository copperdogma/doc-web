import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mistral4_guard as guard
import openai_responses_model as owner


def call_api(prompt, options, context):
    os.environ["MISTRAL_CASE"] = str(context.get("vars", {}).get("crop_key", "native"))
    guard.install()
    for name, value in zip(
        ("INPUT", "CACHED_INPUT", "CACHE_WRITE", "OUTPUT"), guard.PRICES["gpt-5.5"]
    ):
        os.environ[f"OPENAI_RESPONSES_{name}_PRICE_PER_1M"] = str(value)
    return owner.call_api(prompt, options, context)
