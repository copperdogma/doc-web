import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import haiku55_guard as guard
import anthropic_opus48_messages as owner


def call_api(prompt, options, context):
    vs = context.get("vars", {})
    if vs:
        os.environ["HAIKU55_CASE"] = str(
            vs.get("golden_key", vs.get("crop_key", "native"))
        )
    guard.install()
    os.environ["ANTHROPIC_MESSAGES_INPUT_PRICE_PER_1M"] = "0.1"
    os.environ["ANTHROPIC_MESSAGES_OUTPUT_PRICE_PER_1M"] = "0.5"
    return owner.call_api(prompt, options, context)
