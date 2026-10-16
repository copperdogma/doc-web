"""Budget/custody regressions using no network and disposable ledgers."""

import json
import importlib.util
import unittest
import tempfile
import os
from pathlib import Path
import httpx

SPEC = importlib.util.spec_from_file_location(
    "scout096_guard",
    Path(__file__).parents[1] / "benchmarks/providers/scout096_guard.py",
)
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name)
        self.old = (g.RESULTS, g.ROOT)
        g.RESULTS = g.ROOT = self.p
        os.environ["SCOUT096_STAGE"] = "test"
        g.save(
            self.p / "ledger.json",
            {"cap_usd": 15, "spent_usd": 0, "calls": [], "closed": False},
        )

    def tearDown(self):
        g.RESULTS, g.ROOT = self.old
        self.tmp.cleanup()

    def req(self):
        return httpx.Request(
            "POST",
            "https://api.openai.com/v1/responses",
            json={
                "model": "gpt-5.5",
                "max_output_tokens": 2048,
                "input": [
                    {
                        "type": "input_image",
                        "image_url": "data:image/png;base64,lossless",
                    }
                ],
            },
        )

    def test_unknown_reservation_blocks(self):
        g.save(
            self.p / "ledger.json",
            {
                "cap_usd": 15,
                "spent_usd": 14.7,
                "calls": [{"reserved_usd": 0.3, "cost_usd": None}],
                "closed": False,
            },
        )
        with self.assertRaisesRegex(RuntimeError, "cap admission"):
            g.send(lambda *a, **k: self.fail("network dispatched"), None, self.req())

    def test_error_retained_unknown_duplicate_denied(self):
        payload = b'{"error":{"message":"capacity","code":500}}'

        def original(c, r, **k):
            return httpx.Response(500, content=payload, request=r)

        g.send(original, None, self.req())
        d = json.loads((self.p / "ledger.json").read_text())
        self.assertIsNone(d["calls"][0]["cost_usd"])
        self.assertEqual((self.p / "response-001.json").read_bytes(), payload)
        self.assertEqual(
            json.loads((self.p / "request-001.json").read_text()),
            json.loads(self.req().content),
        )
        with self.assertRaisesRegex(RuntimeError, "duplicate"):
            g.send(original, None, self.req())


if __name__ == "__main__":
    unittest.main()
