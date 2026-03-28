import argparse
import base64
import json
from pathlib import Path
from typing import List

from modules.common.openai_client import OpenAI
from modules.common.utils import ensure_dir, read_jsonl, save_jsonl
from modules.intake.intake_plan_utils import (
    choose_maintained_recipe,
    merge_unique_strings,
    normalize_book_type,
    normalize_signal_evidence,
    resolve_source_images_dir,
)


def parse_json_relaxed(text: str):
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            return None
    return None


def encode_image_file(path: Path, detail: str):
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}", "detail": detail}}


def main():
    parser = argparse.ArgumentParser(description="Zoom refinement for intake plan")
    parser.add_argument("--plan-in", "--plan_in", dest="plan_in", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max_zoom_pages", type=int, default=5)
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--vision_detail", default="low", choices=["low", "high"])
    parser.add_argument("--source_images_dir", default=None)
    parser.add_argument("--mock_output", default=None, help="Path to JSON to use instead of LLM")
    parser.add_argument("--boost_model", default="gpt-5")
    args, _unknown = parser.parse_known_args()

    plan_rows = list(read_jsonl(args.plan_in))
    plan = plan_rows[0] if plan_rows else {}

    zooms = [str(item) for item in plan.get("zoom_requests", [])]
    if len(zooms) > args.max_zoom_pages:
        plan["zoom_requests"] = zooms[: args.max_zoom_pages]
        plan.setdefault("warnings", []).append(f"zoom_requests truncated to {args.max_zoom_pages}")
    else:
        plan["zoom_requests"] = zooms

    source_images_dir = resolve_source_images_dir(plan, args.source_images_dir)
    if plan.get("zoom_requests"):
        if args.mock_output:
            data = json.load(open(args.mock_output, "r", encoding="utf-8"))
        else:
            contents: List = []
            if source_images_dir:
                for name in plan.get("zoom_requests", [])[: args.max_zoom_pages]:
                    image_path = source_images_dir / name
                    if image_path.exists():
                        contents.append(encode_image_file(image_path, args.vision_detail))
            if not contents:
                contents = [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "zoom_requests": plan.get("zoom_requests", []),
                                "signals": plan.get("signals", []),
                                "source_input": ((plan.get("meta") or {}).get("source_input") or {}),
                            }
                        ),
                    }
                ]
            prompt = (
                "Refine the draft intake classification using the requested page zooms. "
                "Return JSON with keys: book_type, type_confidence, signals, signal_evidence, zoom_requests, warnings. "
                "book_type must be one of novel, cyoa, genealogy, textbook, mixed, other. "
                "Use mixed only when the document truly blends families; otherwise prefer other with a low confidence. "
                "signals may only contain: tables, formulas, images, cyoa, maps, sheet_music, forms, comics. "
                "signal_evidence must use page image filenames or display-number-like strings exactly as provided."
            )
            client = OpenAI()
            response = client.chat.completions.create(
                model=args.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": contents},
                ],
                temperature=0.0,
                max_tokens=400,
            )
            data = parse_json_relaxed(response.choices[0].message.content) or {}

        if data.get("book_type") is not None:
            plan["book_type"] = normalize_book_type(data.get("book_type"), fallback=plan.get("book_type") or "other")
        if data.get("type_confidence") is not None:
            plan["type_confidence"] = data.get("type_confidence")
        plan["signals"] = merge_unique_strings(plan.get("signals", []), data.get("signals", []))
        if data.get("signal_evidence"):
            plan["signal_evidence"] = normalize_signal_evidence(data.get("signal_evidence", []))
        if data.get("zoom_requests"):
            plan["zoom_requests"] = [str(item) for item in data.get("zoom_requests", [])[: args.max_zoom_pages]]
        plan.setdefault("warnings", []).extend(data.get("warnings", []))

    plan["recommended_recipe"] = choose_maintained_recipe(plan) or "no-recipe-needed"
    ensure_dir(Path(args.out).parent)
    save_jsonl(args.out, [plan])
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
