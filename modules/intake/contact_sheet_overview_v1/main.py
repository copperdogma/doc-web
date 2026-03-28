import argparse
import base64
import json
from pathlib import Path

from modules.common.openai_client import OpenAI
from modules.common.utils import ensure_dir, read_jsonl, save_jsonl
from modules.intake.intake_plan_utils import (
    choose_maintained_recipe,
    load_contact_sheet_build_meta,
    merge_unique_strings,
    normalize_book_type,
    normalize_signal_evidence,
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


def summarize_manifest(manifest_path: Path):
    sheets = {}
    display_order = []
    tile_map = []
    for tile in read_jsonl(str(manifest_path)):
        sheets.setdefault(tile["sheet_id"], 0)
        sheets[tile["sheet_id"]] += 1
        if tile.get("tile_index") == 0:
            display_order.append(tile.get("display_number"))
        tile_map.append(
            {
                "display_number": tile.get("display_number"),
                "source_image": tile.get("source_image"),
                "sheet_id": tile.get("sheet_id"),
                "tile_index": tile.get("tile_index"),
            }
        )
    return {
        "sheet_count": len(sheets),
        "tile_count": len(tile_map),
        "sheets": list(sheets.keys()),
        "display_order": display_order,
        "tile_map": tile_map,
    }


def encode_image(path: Path) -> str:
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def prompt_document_overview(client: OpenAI, sheet_paths, summary, source_input, model: str, vision_detail: str) -> dict:
    content = [
        {
            "type": "text",
            "text": json.dumps(
                {
                    "source_input": source_input,
                    "tile_map": summary.get("tile_map", []),
                }
            ),
        }
    ]
    for sheet_path in sheet_paths:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": encode_image(sheet_path), "detail": vision_detail},
            }
        )

    system_prompt = (
        "Classify this document from its contact sheets and page map. "
        "Return JSON with keys: book_type, type_confidence, signals, signal_evidence, zoom_requests, warnings, notes. "
        "book_type must be one of novel, cyoa, genealogy, textbook, mixed, other. "
        "Use mixed only when the document clearly combines incompatible families; use other for forms, letters, programs, cards, proposals, manuals, or anything outside the named families. "
        "type_confidence must be between 0 and 1. "
        "signals may only contain: tables, formulas, images, cyoa, maps, sheet_music, forms, comics. "
        "signal_evidence must be an array of objects with signal, pages, and reason, using display_number values from tile_map. "
        "Only request zooms when a small set of pages would materially improve classification. "
        "Prefer a low-confidence answer over falling back to mixed without evidence."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.0,
        max_tokens=600,
    )
    raw = response.choices[0].message.content
    data = parse_json_relaxed(raw) or {}
    data.setdefault("signals", [])
    data.setdefault("signal_evidence", [])
    data.setdefault("warnings", [])
    data.setdefault("zoom_requests", [])
    return data


def main():
    parser = argparse.ArgumentParser(description="Overview classifier from contact sheets")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--sheets_dir", required=False)
    parser.add_argument("--out", required=True)
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--max_sheets", type=int, default=0)
    parser.add_argument("--vision_detail", default="low", choices=["low", "high"])
    parser.add_argument("--mock_output", default=None, help="Path to JSON to use instead of LLM")
    parser.add_argument("--boost_model", default="gpt-5")
    args, _unknown = parser.parse_known_args()

    ensure_dir(Path(args.out).parent)
    summary = summarize_manifest(Path(args.manifest))
    build_meta = load_contact_sheet_build_meta(Path(args.manifest), Path(args.sheets_dir) if args.sheets_dir else None)

    sheet_paths = []
    for row in read_jsonl(args.manifest):
        sheet_path = row.get("sheet_path")
        if sheet_path:
            candidate = Path(sheet_path)
            if candidate.exists() and candidate not in sheet_paths:
                sheet_paths.append(candidate)
    selected_sheets = sheet_paths if args.max_sheets <= 0 else sheet_paths[: args.max_sheets]

    if args.mock_output:
        llm_plan = json.load(open(args.mock_output, "r", encoding="utf-8"))
    else:
        client = OpenAI()
        llm_plan = prompt_document_overview(
            client=client,
            sheet_paths=selected_sheets,
            summary=summary,
            source_input=build_meta,
            model=args.model,
            vision_detail=args.vision_detail,
        )

    warnings = list(llm_plan.get("warnings", []))
    raw_book_type = llm_plan.get("book_type")
    book_type = normalize_book_type(raw_book_type, fallback="other")
    if raw_book_type is None:
        warnings.append("overview omitted book_type; defaulted to other")

    type_confidence = llm_plan.get("type_confidence")
    if type_confidence is None:
        type_confidence = 0.0 if book_type == "other" else 0.15

    plan = {
        "schema_version": "intake_plan_v1",
        "book_type": book_type,
        "type_confidence": type_confidence,
        "sections": [],
        "zoom_requests": [str(item) for item in llm_plan.get("zoom_requests", [])],
        "recommended_recipe": None,
        "sectioning_strategy": "contact-sheet overview",
        "assumptions": ["No web lookup; vision from contact sheets"],
        "warnings": warnings,
        "notes": llm_plan.get("notes"),
        "signals": merge_unique_strings(llm_plan.get("signals", [])),
        "signal_evidence": normalize_signal_evidence(llm_plan.get("signal_evidence", [])),
        "sheets": summary.get("sheets", []),
        "manifest_path": str(Path(args.manifest)),
        "meta": {
            "summary": summary,
            "model": args.model,
            "source_input": build_meta,
        },
    }
    plan["recommended_recipe"] = choose_maintained_recipe(plan)
    if not plan["recommended_recipe"]:
        plan["recommended_recipe"] = "no-recipe-needed"
        plan["warnings"].append("No maintained recipe recommendation available from source input metadata")

    save_jsonl(args.out, [plan])
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
