"""Only loaded by the offline verification subprocess's explicit PYTHONPATH."""

import io
import json
import os
import urllib.request


def offline_open(self, request, *args, **kwargs):
    if request.full_url != "https://api.typesafe.ai/v1/systemone":
        raise RuntimeError("Offline verifier forbids network")
    if os.environ.get("DOC_WEB_TEST_SHADOW_FAILURE") == "yes":
        raise TimeoutError("synthetic provider failure")
    payload = json.loads(request.data)
    assert payload["model"] == "jev-1.13.0"
    probs = {
        k: int(k == "uncertain") for k in payload["questions"]["status"]["criteria"]
    }
    raw = {
        "model": "jev-1.13.0",
        "usage": {"input_tokens": 500, "output_tokens": 30},
        "answers": {
            "status": {
                "type": "choice",
                "choice": "uncertain",
                "confidence": 0.1,
                "probabilities": probs,
            }
        },
    }
    response = io.BytesIO(json.dumps(raw).encode())
    response.status = 200
    return response


urllib.request.OpenerDirector.open = offline_open
