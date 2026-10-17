# ruff: noqa: E402
import sys
import io
from PIL import Image, ImageDraw

sys.path.insert(0, "benchmarks/scripts")
import scout097_safety as s
from scout097_reading import google, save

im = Image.new("RGB", (300, 150), "white")
ImageDraw.Draw(im).text((30, 30), "TEST", fill="black")
f = io.BytesIO()
im.save(f, format="PNG")
schema = s.body("page-012-001", "candidate")["response_format"]["json_schema"]["schema"]
raw, d = google(
    s.MODEL,
    "",
    "Inspect the supplied image; return a crop verdict using the specified schema.",
    f.getvalue(),
    schema=schema,
    stage="native-safety",
)
err = s.old.helper.owner._contract_error(raw, "page_context_validation")
assert not err, err
save(
    s.E / "native-safety.json",
    {"raw": raw, "served": d["model"], "provider": d["provider"], "finish": "stop"},
)
print("qualified safety schema")
