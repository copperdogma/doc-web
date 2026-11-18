"""Source-backed scores for admitted Scout116 native outputs."""
from __future__ import annotations

import base64
from io import BytesIO
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from benchmarks.scorers import handwritten_notes_transcription as htr
from benchmarks.scorers.image_crop_scorer import get_assert, _parse_json
from doc_web.literal_fidelity import SourcePageReview
from doc_web.literal_tables import compare_tables
from modules.extract.ocr_ai_gpt51_v1.main import _extract_ocr_metadata, sanitize_html

E = ROOT / "docs/evals/evidence/097-astra62"


def score_ocr(case, raw):
    clean, metadata, tag, warning = _extract_ocr_metadata(raw)
    text = htr.html_to_text(sanitize_html(clean))
    expected, = htr.load_transcript_pages(ROOT / f"testdata/handwritten-notes-{case}-real.txt")
    return {**htr.score_text_pair(expected,text), "html_metadata":metadata,
            "metadata_first":bool(tag and not warning), "recognized_text":text}


def score_table(case, raw):
    result = SourcePageReview.model_validate_json(raw)
    golden = ROOT / "testdata/literal-table-fidelity/confirmation-v2" / case / "golden.html"
    score = compare_tables(golden.read_text(), "".join(table.html for table in result.tables))
    return {**score,"source_table_count":result.source_table_count,"uncertainties":[
        [{"row":c.row,"cell":c.cell,"reason":c.reason,"alternatives":c.alternatives} for c in table.uncertain_cells]
        for table in result.tables
    ]}


def score_crop(case, raw, arm):
    structural = get_assert(raw, {"vars":{"golden_key":case}})
    image_bytes = base64.b64decode((ROOT / f"benchmarks/input/source-pages-b64/{case}.b64.txt").read_text().strip().split(",")[-1])
    source = Image.open(BytesIO(image_bytes)).convert("RGB")
    w,h = source.size
    boxes = [p["bbox"] for p in _parse_json(raw)["images"]]
    normalized = all(len(b)==4 and all(0<=v<=1 for v in b) and b[0]<b[2] and b[1]<b[3] for b in boxes)
    result = {"structural":structural,"fixed_normalized_xyxy":normalized,"boxes":boxes}
    if not normalized:
        return result
    dark = np.array(source.convert("L")) < 100
    covered = np.zeros((h,w),dtype=bool)
    for n, box in enumerate(boxes):
        b = [int(x * (w if j%2==0 else h)) for j,x in enumerate(box)]
        x0,y0,x1,y1=b
        covered[y0:y1,x0:x1]=True
        source.crop(b).save(E/f"{case}-{arm}-crop-{n}.png")
    old=json.loads((ROOT/"docs/evals/evidence/089-carbon/source-review-crops.json").read_text())
    if case in old["cases"]:
        loss={}
        for roi in old["cases"][case]["arms"]["candidate"]["rois"]:
            x0,y0,x1,y1=roi["roi_half_open_xyxy"]
            loss[roi["name"]] = int(np.count_nonzero(dark[y0:y1,x0:x1]&~covered[y0:y1,x0:x1]))
        result["frozen_dark_pixel_roi_losses"]=loss
    return result


def score(name):
    raw=json.loads((E/(name+".answer.json")).read_text())["raw"]
    lane, rest=name.split("-",1)
    case, arm=rest.rsplit("-",1)
    if lane=="ocr":
        output=score_ocr(case,raw)
    elif lane=="table":
        output=score_table(case,raw)
    else:
        output=score_crop(case,raw,arm)
    (E/f"{name}.score.json").write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in output.items() if k not in ("recognized_text",)},ensure_ascii=False))


if __name__=="__main__":
    for name in sys.argv[1:]:
        score(name)
