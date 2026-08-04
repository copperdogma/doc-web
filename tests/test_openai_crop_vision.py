from types import SimpleNamespace

import pytest

from modules.common.openai_crop_vision import (
    CAPTION_RESPONSE_FORMAT,
    DETECTOR_RESPONSE_FORMAT,
    call_openai_crop_vision,
    uses_strict_crop_responses,
)


class _FakeResponses:
    def __init__(self, response):
        self.response = response
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.response


class _FakeClient:
    def __init__(self, response):
        self.responses = _FakeResponses(response)


def _response(output_text: str, **overrides):
    values = {
        "id": "resp-crop-123",
        "model": "gpt-5.6-luna",
        "status": "completed",
        "incomplete_details": None,
        "usage": SimpleNamespace(input_tokens=100, output_tokens=25),
        "output_text": output_text,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_strict_route_is_scoped_to_gpt56_models():
    assert uses_strict_crop_responses("gpt-5.6-luna") is True
    assert uses_strict_crop_responses("gpt-5.6-terra") is True
    assert uses_strict_crop_responses("gpt-5.1") is False
    assert uses_strict_crop_responses("gemini-3-flash-preview") is False


def test_detector_request_is_strict_private_and_has_no_temperature():
    response = _response(
        '{"regions":[{"image_box":{"x0":0.1,"y0":0.2,"x1":0.8,"y1":0.9},'
        '"caption_box":null,"image_description":"portrait","contains_text":false,'
        '"text_reason":null,"caption_text":null,"source_issues":null}]}'
    )
    client = _FakeClient(response)

    result = call_openai_crop_vision(
        client=client,
        model="gpt-5.6-luna",
        system_prompt="detect",
        user_text="one box",
        image_data="data:image/jpeg;base64,abc",
        max_output_tokens=800,
        contract="detector",
    )

    assert result.raw_json_array.startswith('[{"image_box"')
    assert result.request_id == "resp-crop-123"
    assert client.responses.kwargs["store"] is False
    assert client.responses.kwargs["reasoning"] == {"effort": "none"}
    assert client.responses.kwargs["text"]["format"] == DETECTOR_RESPONSE_FORMAT
    assert "temperature" not in client.responses.kwargs


def test_caption_request_uses_caption_schema_and_normalizes_array():
    client = _FakeClient(_response('{"boxes":[{"x0":0.1,"y0":0.2,"x1":0.8,"y1":0.3}]}'))

    result = call_openai_crop_vision(
        client=client,
        model="gpt-5.6-luna",
        system_prompt="captions",
        user_text="one caption",
        image_data="data:image/jpeg;base64,abc",
        max_output_tokens=400,
        contract="captions",
    )

    assert result.raw_json_array == '[{"x0":0.1,"y0":0.2,"x1":0.8,"y1":0.3}]'
    assert client.responses.kwargs["text"]["format"] == CAPTION_RESPONSE_FORMAT


def test_caption_contract_accepts_explicit_no_caption_zero_box():
    client = _FakeClient(_response('{"boxes":[{"x0":0,"y0":0,"x1":0,"y1":0}]}'))

    result = call_openai_crop_vision(
        client=client,
        model="gpt-5.6-luna",
        system_prompt="captions",
        user_text="no caption",
        image_data="data:image/jpeg;base64,abc",
        max_output_tokens=400,
        contract="captions",
    )

    assert result.raw_json_array == '[{"x0":0,"y0":0,"x1":0,"y1":0}]'


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"status": "incomplete"}, "did not complete"),
        ({"incomplete_details": {"reason": "max_output_tokens"}}, "incomplete"),
        ({"model": "gpt-5.6-terra"}, "expected exact"),
        ({"usage": None}, "usage evidence"),
        ({"id": None}, "request id"),
    ],
)
def test_response_identity_status_and_usage_fail_closed(overrides, message):
    client = _FakeClient(_response('{"regions":[]}', **overrides))

    with pytest.raises(RuntimeError, match=message):
        call_openai_crop_vision(
            client=client,
            model="gpt-5.6-luna",
            system_prompt="detect",
            user_text="none",
            image_data="data:image/jpeg;base64,abc",
            max_output_tokens=800,
            contract="detector",
        )


def test_contract_validation_rejects_invalid_boxes():
    client = _FakeClient(
        _response(
            '{"regions":[{"image_box":{"x0":0.9,"y0":0.2,"x1":0.1,"y1":0.8},'
            '"caption_box":null,"image_description":"bad","contains_text":false,'
            '"text_reason":null,"caption_text":null,"source_issues":null}]}'
        )
    )

    with pytest.raises(RuntimeError, match="x0 < x1"):
        call_openai_crop_vision(
            client=client,
            model="gpt-5.6-luna",
            system_prompt="detect",
            user_text="one",
            image_data="data:image/jpeg;base64,abc",
            max_output_tokens=800,
            contract="detector",
        )
