#!/usr/bin/env python3
"""Source-only abstaining table reread prototype; never receives goldens/OCR."""
import argparse
import base64
import json
from pathlib import Path
from types import SimpleNamespace

from openai import OpenAI
from PIL import Image

from benchmarks.scripts.run_literal_table_fidelity import RecordingResponses, digest
from doc_web.env import build_child_env
from modules.extract.ocr_ai_gpt51_v1.main import _call_vision_model, _extract_code_fence

POLICY = """Read every table directly from the supplied source page image. This is literal transcription, not correction of what the author intended. Preserve exact character case, punctuation, apparent typos, empty cells, dashes, modifiers, repeated values and row/column spans. Do not infer identifiers/references or copy repeated values to resolve a glyph. If character interpretations cannot be distinguished from the visible pixels in this font, mark that cell uncertain; do not force a guess. Blur, cropping and unclear cell ownership also require uncertainty. State visually plausible alternatives if possible. A confident-looking token or coherent wording is not source evidence.
Return ONLY one JSON object with exactly: {"source_table_count":integer,"tables":[{"bbox":[left,top,right,bottom],"html":"one complete minimal HTML table","uncertain_cells":[{"row":zero-based row index,"cell":zero-based explicit cell index,"reason":"source ambiguity","alternatives":["possible complete cell text"]}]}]}. Include every visible table once in source reading order, including table headers and spanning cells. Bbox coordinates are source image pixels. HTML includes table/thead/tbody/tr/th/td and safe positive rowspan/colspan; preserve literal entities with HTML escaping. For an uncertain cell retain a best observed transcription in HTML solely as diagnostic, and list uncertainty explicitly. No comments, Markdown or outside-table prose. If the image contains no tables return source_table_count0 and emptytables. Never return an uncertain cell as verified by choosing the most plausible spelling."""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--ledger', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise RuntimeError('Fresh result required; no favorable reruns')
    ledger = json.loads(args.ledger.read_text())
    reserve = .85
    if ledger['calls'] >= ledger['call_cap'] or round(ledger['reserved_usd']+reserve,4) > ledger['reserve_cap_usd']:
        raise RuntimeError('Phase cap reached before dispatch')
    ledger['calls'] += 1
    ledger['reserved_usd'] = round(ledger['reserved_usd']+reserve,4)
    ledger['entries'].append({'variant':'source-review-probe','image_sha256':digest(args.image.read_bytes()),'out':str(args.out),'reserve_usd':reserve})
    args.ledger.write_text(json.dumps(ledger,indent=2)+'\n')
    client = OpenAI(api_key=build_child_env()['OPENAI_API_KEY'], max_retries=0,timeout=180)
    record = {'image_sha256':digest(args.image.read_bytes()),'prompt_sha256':digest(POLICY.encode())}
    with Image.open(args.image) as im:
        size = im.size
    try:
        raw, _, _ = _call_vision_model('gpt-6-astra',POLICY,
            f'Source image dimensions: {size[0]} x {size[1]} pixels. Read source tables; return JSON only.',
            'data:image/png;base64,'+base64.b64encode(args.image.read_bytes()).decode(),0,8192,
            openai_client=SimpleNamespace(responses=RecordingResponses(client,record,'original')))
        record['raw'] = raw
        record['parsed'] = json.loads(_extract_code_fence(raw))
    finally:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'tables':record['parsed'].get('source_table_count'),
        'uncertainties':sum(len(t.get('uncertain_cells',[])) for t in record['parsed']['tables'])}),flush=True)


if __name__ == '__main__':
    main()
