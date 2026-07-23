import json

from modules.adapter.table_rescue_html_loop_v1.main import _json_safe


class _NestedUsage:
    def __init__(self) -> None:
        self.cached_tokens = 3


class _Usage:
    def model_dump(self):
        return {
            "input_tokens": 12,
            "output_tokens": 7,
            "details": _NestedUsage(),
            "modalities": ("text", "image"),
        }


def test_json_safe_recursively_converts_sdk_usage_objects():
    converted = _json_safe(_Usage())

    assert converted == {
        "input_tokens": 12,
        "output_tokens": 7,
        "details": {"cached_tokens": 3},
        "modalities": ["text", "image"],
    }
    assert json.loads(json.dumps(converted)) == converted
