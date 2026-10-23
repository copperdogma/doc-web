"""Only activated by campaign's explicit eval subprocess PYTHONPATH."""

import atexit
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runtime_support
import openai
import urllib.request

openai.OpenAI = runtime_support.EvalOpenAI
urllib.request.OpenerDirector.open = runtime_support.candidate_open
if os.environ.get("PPLX_SHADOW_TRANSPORT_MODE") == "offline":
    import datetime

    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return (
                cls(2026, 10, 6, 12, 0, 0, tzinfo=datetime.timezone.utc).astimezone(tz)
                if tz
                else cls(2026, 10, 6, 12, 0, 0)
            )

        @classmethod
        def utcnow(cls):
            return cls(2026, 10, 6, 12, 0, 0)

    datetime.datetime = FixedDateTime

atexit.register(runtime_support.settle_threads)
