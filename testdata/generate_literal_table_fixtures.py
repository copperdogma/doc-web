#!/usr/bin/env python3
"""Render exact source-authored literal tables; source JSON owns goldens."""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import subprocess
from functools import partial
from pathlib import Path
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle


def generate(source: Path, out: Path) -> dict:
    payload = json.loads(source.read_text())
    out.mkdir(parents=True, exist_ok=True)
    rows = payload['rows']
    grid, commands, html_rows = [], [], []
    pending = {}
    for row_index, row in enumerate(rows):
        cells, rendered, col = [], [], 0
        for cell in row:
            while pending.get((row_index, col)):
                rendered.append('')
                col += 1
            text = cell['text']
            colspan, rowspan = cell.get('colspan', 1), cell.get('rowspan', 1)
            tag = 'th' if cell.get('header') else 'td'
            attrs = ''.join(f' {k}="{v}"' for k, v in [('colspan', colspan), ('rowspan', rowspan)] if v != 1)
            cells.append(f'<{tag}{attrs}>{html.escape(text)}</{tag}>')
            rendered.append(text)
            rendered.extend([''] * (colspan - 1))
            if colspan > 1 or rowspan > 1:
                commands.append(('SPAN', (col, row_index), (col + colspan - 1, row_index + rowspan - 1)))
            for next_row in range(row_index + 1, row_index + rowspan):
                for next_col in range(col, col + colspan):
                    pending[(next_row, next_col)] = True
            col += colspan
        while col < len(payload['widths']):
            rendered.append('')
            col += 1
        if col != len(payload['widths']):
            raise ValueError('Source row width mismatch')
        grid.append(rendered)
        html_rows.append('<tr>' + ''.join(cells) + '</tr>')
    golden = '<h1>' + html.escape(payload['title']) + '</h1>\n<table>\n' + '\n'.join(html_rows) + '\n</table>\n'
    (out / 'golden.html').write_text(golden)
    pdf = out / 'native.pdf'
    # Single bounded table; fixed-width columns preserve cell ownership.
    title = Table([[payload['title']]], colWidths=[504])
    title.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), payload['font']), ('FONTSIZE', (0, 0), (-1, -1), 17)]))
    table = Table(grid, colWidths=payload['widths'], rowHeights=[34] * len(grid))
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), payload['font']),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.7, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDEDED')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        *commands,
    ]))
    SimpleDocTemplate(str(pdf), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=60).build([title, Spacer(1, 24), table], canvasmaker=partial(Canvas, invariant=1))
    subprocess.run(['pdftoppm', '-r', '200', '-singlefile', '-png', str(pdf), str(out / 'page')], check=True, capture_output=True)
    with Image.open(out / 'page.png') as image:
        image.convert('RGB').save(out / 'image-only.pdf', 'PDF', resolution=200)
    native_text = subprocess.check_output(['pdftotext', str(pdf), '-'], text=True)
    image_text = subprocess.check_output(['pdftotext', str(out / 'image-only.pdf'), '-'], text=True)
    if image_text.strip():
        raise ValueError('Image-only PDF unexpectedly contains text')
    for row in rows:
        for cell in row:
            if cell['text'] and cell['text'] not in native_text:
                raise ValueError('Native text failed source literal witness')
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [source, out / 'golden.html', pdf, out / 'page.png', out / 'image-only.pdf']}
    metadata = {'source': str(source), 'font': payload['font'], 'rows': len(rows), 'columns': len(payload['widths']), 'pages': 1, 'raster_dpi': 200, 'native_literal_witness_checked': True, 'image_only_text_chars': len(image_text.strip()), 'sha256': hashes}
    (out / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    generate(args.source, args.out)
    print('Rendered source, golden, native and image-only forms; text witnesses passed.')
