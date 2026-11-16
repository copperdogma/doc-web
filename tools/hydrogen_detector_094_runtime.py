"""Isolated Attempt093 real-driver transport harness; default mode is offline."""

import base64
import contextlib
import hashlib
import json
import os
import shutil
import importlib.util
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import yaml
from google import genai
from google.genai import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from benchmarks.scripts import hydrogen_native as ember_native  # noqa: E402

MODELS = {"candidate": "gemini-4-hydrogen", "control": "gemini-3-flash-preview"}
URLS = {
    k: "https://generativelanguage.googleapis.com/v1beta/models/"
    + v
    + ":generateContent"
    for k, v in MODELS.items()
}


def wire(body):
    return json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode()  # noqa: E402


from modules.common import google_client, openai_crop_vision  # noqa: E402
from modules.extract.crop_illustrations_guided_v1 import main as crop  # noqa: E402
from scripts.prepare_story231_crop_fixture import CASES, prepare  # noqa: E402

# These are the same original high-resolution pages used by the owner recipe.
HIGHRES = Path(
    "/Users/cam/Documents/Projects/doc-web/input/onward-to-the-unknown-images"
)
FIXTURE = ROOT / "output/fixtures/hydrogen-detector-094-runtime"
SCHEMA = openai_crop_vision.DETECTOR_RESPONSE_FORMAT["schema"]
MODEL = MODELS["candidate"]
GEMINI = MODELS["control"]
FAKE_KEY = "offline-no-credentials"
MODEL_NAME = "PP-DocLayout_plus-L"
LAYOUT_SOURCE = (
    Path("/Users/cam/.codex/worktrees/gpt6-sol-luna-eval-20260926/doc-web")
    / "output/model-cache-story236/official_models"
    / MODEL_NAME
)
LAYOUT_SHA = "24ca3e2e442164505e250deef59f7ee9a54ea12dd32875c9cd6155d959dc97da"
LAYOUT_CACHE = FIXTURE / "paddle-cache"


class TransportStop(BaseException):
    """Abort before the runtime's ordinary catch-and-fallback can mask transport failure."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sdk_client(handler):
    """Actual owner's SDK with only its outbound HTTP client replaced."""
    gc = google_client.GeminiVisionClient.__new__(google_client.GeminiVisionClient)
    gc._client = genai.Client(
        api_key=FAKE_KEY,
        http_options=types.HttpOptions(
            api_version="v1beta",
            httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )
    return gc


def fake_google():
    return {
        "modelVersion": GEMINI,
        "responseId": "offline-fixture",
        "candidates": [
            {
                "content": {"role": "model", "parts": [{"text": "[]"}]},
                "finishReason": "STOP",
            }
        ],
    }


def emitter(pipeline, emit, capture=False):
    """Bind the native production parser and caller to a budgeted or offline sender."""
    by_hash = {digest((HIGHRES / (c["key"] + ".jpg")).read_bytes()): c for c in CASES}
    seen = set()

    def send(role, arm, source, count, url, body):
        case = by_hash[digest(source)]
        page = case["page"]
        if page == 1 or url != URLS[arm]:
            raise RuntimeError("cover bypass/URL contract violated")
        group = (page, pipeline, role)
        if not capture and group in seen:
            raise RuntimeError("second dispatch for the same runtime stage")
        seen.add(group)
        return emit(
            {
                "slot": f"runtime-{page}-{pipeline}-{role}-{count}",
                "role": role,
                "page": page,
                "pipeline": pipeline,
                "arm": arm,
                "url": url,
                "source_sha256": digest(source),
                "body_bytes": body,
            }
        )

    def google(request):
        try:
            body = json.loads(request.content)
            system = body["systemInstruction"]["parts"][0]["text"]
            config = body["generationConfig"]
            if system == crop._BBOX_PROMPT and pipeline == "control":
                role, maximum = "detector", 8192
            elif system == crop._CAPTION_PROMPT:
                role, maximum = "caption", 400
            else:
                raise ValueError("unexpected Google system prompt or route")
            if config != {
                "temperature": 0.0,
                "maxOutputTokens": maximum,
                "responseMimeType": "text/plain",
            }:
                raise ValueError("Google request config drift")
            text, image = body["contents"][0]["parts"]
            count = int(text["text"].split()[3])
            source = base64.b64decode(
                image["inlineData"]["data"], altchars=b"-_", validate=True
            )
            raw = send(
                role, "control", source, count, str(request.url), request.content
            )
            return httpx.Response(200, content=raw)
        except Exception as exc:
            raise TransportStop(str(exc)) from exc

    def meta(**kwargs):
        try:
            if kwargs["model"] != MODEL or kwargs["contract"] != "detector":
                raise ValueError("unexpected routed candidate role")
            if (
                kwargs["system_prompt"] != crop._BBOX_PROMPT
                or kwargs["reasoning_effort"] != "high"
                or kwargs["max_output_tokens"] != 32768
            ):
                raise ValueError("candidate detector settings drift")
            source, mime = google_client._decode_data_uri(kwargs["image_data"])
            user_text = kwargs["user_text"]
            count = int(user_text.split()[3])
            body = ember_native.body(
                MODEL, kwargs["system_prompt"], user_text, [(source, mime)], SCHEMA
            )
            raw = json.loads(
                send(
                    "detector",
                    "candidate",
                    source,
                    count,
                    URLS["candidate"],
                    wire(body),
                )
            )
            if capture:
                return SimpleNamespace(
                    raw_json_array="[]", usage=None, request_id="offline-fixture"
                )
            text = ember_native.parse(raw, MODEL, SCHEMA)
            return SimpleNamespace(
                raw_json_array=openai_crop_vision._normalize_contract(text, "detector"),
                usage=SimpleNamespace(
                    prompt_token_count=raw["usageMetadata"]["promptTokenCount"],
                    candidates_token_count=raw["usageMetadata"]["candidatesTokenCount"],
                ),
                request_id=raw["responseId"],
            )
        except Exception as exc:
            raise TransportStop(str(exc)) from exc

    stack = contextlib.ExitStack()
    # This eval-only candidate hook supplies normalized strict regions at the
    # existing strict detector seam. Gemini continues through its actual SDK.
    stack.enter_context(
        patch.object(crop, "GeminiVisionClient", lambda: sdk_client(google))
    )
    original_is_gemini = crop._is_gemini_model
    stack.enter_context(
        patch.object(
            crop,
            "_is_gemini_model",
            lambda m: False if m == MODEL else original_is_gemini(m),
        )
    )
    stack.enter_context(
        patch.object(crop, "OpenAI", lambda **_: SimpleNamespace(responses=True))
    )
    stack.enter_context(
        patch.object(crop, "uses_strict_crop_responses", lambda model: model == MODEL)
    )
    stack.enter_context(patch.object(crop, "call_openai_crop_vision", meta))
    return stack


def matrix():
    rows = []

    def collect(row):
        rows.append(row)
        return json.dumps(fake_google() if row["arm"] == "control" else {}).encode()

    for pipeline, model in MODELS.items():
        with emitter(pipeline, collect, capture=True):
            for case in CASES:
                if case["page"] != 12:
                    continue
                image_data = crop._encode_image(str(HIGHRES / (case["key"] + ".jpg")))
                hints = [img["alt"] for img in case["images"]]
                crop._call_vlm_boxes(
                    model,
                    image_data,
                    len(hints),
                    hints,
                    0.0,
                    32768 if model == MODEL else 8192,
                    None,
                    reasoning_effort="high" if model == MODEL else "none",
                )
                for count in range(1, len(hints) + 1):
                    crop._call_vlm_caption_boxes(
                        GEMINI, image_data, count, hints, 0.0, 400, None
                    )
    return rows


def prepare_driver():
    from driver import load_registry

    if FIXTURE.exists():
        raise ValueError("refuse to overwrite a previous runtime preflight")
    weights = LAYOUT_SOURCE / "inference.pdiparams"
    if digest(weights.read_bytes()) != LAYOUT_SHA:
        raise ValueError("official layout model weights do not match qualified source")
    path = prepare(FIXTURE)
    shutil.copytree(LAYOUT_SOURCE, LAYOUT_CACHE / "official_models" / MODEL_NAME)
    # The original runtime infers provider identity from a two-provider switch.
    # Extend that one expression in the isolated eval copy before any crops are
    # emitted. Original candidate/control source inputs and driver stay intact.
    original = Path(crop.__file__).read_text()
    existing = '"google" if _is_gemini_model(rescue_model) else "openai"'
    if original.count(existing) != 1:
        raise RuntimeError("detector provenance expression changed")
    projected = original.replace(
        existing, f'"Google" if rescue_model == "{MODEL}" else ({existing})'
    )
    (FIXTURE / "guided_with_meta_provenance.py").write_text(projected)
    registry = load_registry(str(ROOT / "modules"))["modules"]
    used = {
        key: registry[key]
        for key in ("load_artifact_v1", "crop_illustrations_guided_v1")
    }
    used["crop_illustrations_guided_v1"]["entrypoint"] = (
        "tools/hydrogen_detector_094_runtime.py"
    )
    (FIXTURE / "registry.yaml").write_text(yaml.safe_dump({"modules": used}))
    for pipeline, model in MODELS.items():
        recipe = yaml.safe_load(
            (
                ROOT / "configs/recipes/story-231-gemini-crop-runtime-validate.yaml"
            ).read_text()
        )
        recipe["stages"][0]["params"]["path"] = str(path)
        params = recipe["stages"][1]["params"]
        params["highres_images_dir"] = str(HIGHRES)
        if pipeline == "candidate":
            params.update(
                rescue_model=model,
                rescue_max_tokens=32768,
                rescue_reasoning_effort="high",
                rescue_caption_model=GEMINI,
            )
        (FIXTURE / f"{pipeline}.yaml").write_text(
            yaml.safe_dump(recipe, sort_keys=False)
        )


def driver(pipeline, run_id, page):
    env = dict(
        os.environ,
        HYDROGEN_094_RUNTIME_ARM=pipeline,
        CROP_EVAL_DISABLE_SDK_RETRIES="1",
        DISABLE_MODEL_SOURCE_CHECK="True",
        PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK="True",
        PADDLE_PDX_CACHE_HOME=str(LAYOUT_CACHE),
        PADDLE_PDX_MODEL_SOURCE="bos",
    )
    if int(page) not in (12, 122, 125):
        raise ValueError("source page is outside the qualified set")
    recipe = yaml.safe_load((FIXTURE / f"{pipeline}.yaml").read_text())
    recipe["stages"][1]["params"]["only_pages"] = (
        f"1,{page}" if int(page) == 12 else str(page)
    )
    recipe_path = FIXTURE / f"{pipeline}-p{page}.yaml"
    published = yaml.safe_dump(recipe, sort_keys=False)
    if recipe_path.exists() and recipe_path.read_text() != published:
        raise ValueError("existing page recipe changed")
    recipe_path.write_text(published)
    command = [
        sys.executable,
        "driver.py",
        "--recipe",
        str(recipe_path),
        "--registry",
        str(FIXTURE / "registry.yaml"),
        "--run-id",
        run_id,
        "--output-dir",
        "output/runs",
    ]
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def stage():
    global crop
    from paddleocr import LayoutDetection
    import paddleocr
    from benchmarks.scripts.hydrogen_runtime_transport import send_runtime

    def send(row):
        return send_runtime(row["slot"], row["arm"], row["url"], row["body_bytes"])

    # Prevent the module's ordinary recoverable layout errors from becoming a
    # green adoption run when the real layout gate did not run.
    class StrictLayout:
        def __init__(self, *args, **kwargs):
            try:
                self.engine = LayoutDetection(*args, **kwargs)
            except Exception as exc:
                raise TransportStop(
                    f"required layout initialization failed: {exc}"
                ) from exc

        def predict(self, *args, **kwargs):
            try:
                result = self.engine.predict(*args, **kwargs)
                if len(result) != 1 or "boxes" not in result[0]:
                    raise ValueError("layout result missing boxes")
                return result
            except Exception as exc:
                raise TransportStop(
                    f"required layout prediction failed: {exc}"
                ) from exc

    path = FIXTURE / "guided_with_meta_provenance.py"
    spec = importlib.util.spec_from_file_location("ember093_guided", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    crop = module
    with (
        patch.object(paddleocr, "LayoutDetection", StrictLayout),
        emitter(os.environ["HYDROGEN_094_RUNTIME_ARM"], send),
    ):
        # Actual module CLI, including all guidance, fallback, trimming, image
        # encoding and source-pixel lineage, followed by original driver stamping.
        crop.main()


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare_driver()
    elif sys.argv[1:] == ["matrix"]:
        print(
            json.dumps(
                [
                    {k: v if k != "body_bytes" else digest(v) for k, v in r.items()}
                    for r in matrix()
                ],
                indent=2,
            )
        )
    elif len(sys.argv) == 5 and sys.argv[1] == "driver" and sys.argv[2] in MODELS:
        driver(sys.argv[2], sys.argv[3], sys.argv[4])
    elif "--ocr-manifest" in sys.argv:
        stage()
    else:
        raise SystemExit(
            "expected prepare, matrix, or driver <arm> <new run id> <page>"
        )
