"""Campaign-only metered adapter; maintained Anthropic schema and prompt."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sonnet55_guard as guard
import anthropic_opus48_messages as owner


def call_api(prompt, options, context):
    guard.install()
    os.environ["ANTHROPIC_MESSAGES_INPUT_PRICE_PER_1M"] = "2"
    os.environ["ANTHROPIC_MESSAGES_OUTPUT_PRICE_PER_1M"] = "10"
    return owner.call_api(prompt, options, context)
