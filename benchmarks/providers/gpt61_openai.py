"""GPT-6.1 Sol campaign wrapper around the owner Responses adapter."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gpt61_guard as guard
import openai_responses_model as owner

def call_api(prompt, options, context):
    guard.install()
    model = owner._request_settings(options)["model"]
    for name, value in zip(("INPUT", "CACHED_INPUT", "CACHE_WRITE", "OUTPUT"), guard.PRICES[model]):
        os.environ[f"OPENAI_RESPONSES_{name}_PRICE_PER_1M"] = str(value)
    return owner.call_api(prompt, options, context)
