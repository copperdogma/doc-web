import base64
import io
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "providers"))
import sonnet55_messages as p

img = Image.new("RGB", (32, 32), "black")
b = io.BytesIO()
img.save(b, format="PNG")
uri = "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
prompt = json.dumps(
    [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Find the single black square. Return one crop bbox as integers 0-1000.",
                },
                {"type": "image_url", "image_url": {"url": uri}},
            ],
        }
    ]
)
cfg = {
    "config": {
        "model": "claude-sonnet-5-5",
        "output_contract": "crop_regions_integer",
        "max_tokens": 4096,
        "thinking": "adaptive",
        "effort": "medium",
    }
}
r = p.call_api(prompt, cfg, {})
path = (
    Path(__file__).resolve().parents[1]
    / "results/sonnet55-20260928/native-detector.json"
)
path.write_text(json.dumps(r, indent=2))
print(json.dumps({k: v for k, v in r.items() if k != "output"}))
assert not r.get("error")
