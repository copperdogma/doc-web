#!/usr/bin/env python3
"""Deterministically author the synthetic Argon literal-table campaign sources."""
from __future__ import annotations

import html
import json
import hashlib
import math
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as ReportLabTTFont
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont as FontToolsTTFont

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
SOURCE = ROOT / "source"
GOLD = ROOT / "gold"
PROOF = ROOT / "proof"
PAGE_W, PAGE_H = letter
SOURCE_FONT = Path("/System/Library/Fonts/Supplemental/Andale Mono.ttf")
ALIAS_FONT = BUILD / "argon-ambiguity-mono.ttf"
AMBIGUOUS_CODEPOINT = "\ue000"
COLORS = {
    "navy": (0.12, 0.20, 0.31), "teal": (0.10, 0.42, 0.43),
    "slate": (0.27, 0.34, 0.40), "rust": (0.56, 0.27, 0.18),
}


def c(text: str, tag: str = "td", colspan: int = 1, rowspan: int = 1,
      fill: str | None = None) -> dict[str, Any]:
    return {"text": text, "tag": tag, "colspan": colspan, "rowspan": rowspan, "fill": fill}


def table(title: str, widths: list[int], rows: list[list[dict[str, Any]]],
          *, font: str, size: int, header_fill: str = "navy", rule: str = "teal",
          top: int = 0, footnote: str = "") -> dict[str, Any]:
    for cell in rows[0]:
        cell["tag"] = "th"
        cell["fill"] = cell.get("fill") or header_fill
    return {"title": title, "widths": widths, "rows": rows, "font": font,
            "size": size, "rule": rule, "header_fill": header_fill,
            "top": top, "footnote": footnote}


PAGES: list[dict[str, Any]] = [
    {"id": "N1", "group": "native", "density": "sparse", "page_title": "Field station intake | cycle 8",
     "prose": "Record labels as printed. A dash denotes a measured zero; an empty box means no reading was supplied.",
     "tables": [table("Crate register", [145, 145, 165], [
         [c("Crate", "th"), c("Seal", "th"), c("Condition", "th")],
         [c("North-4"), c("nQ/17"), c("re-sealed")],
         [c("East-2"), c("EQ/17"), c("scuffed")],
         [c("Hold for review", colspan=3)],
     ], font="Helvetica", size=13, top=520, footnote="1. Seal spellings retain case.")]},
    {"id": "N2", "group": "native", "density": "medium", "page_title": "Workshop ledger | issue 14",
     "prose": "Copy the stamped values verbatim, including the shop's original spelling and punctuation.",
     "tables": [table("Calibration records", [105, 120, 105, 125], [
         [c("Bench", "th"), c("Reference", "th"), c("Offset", "th"), c("Disposition", "th")],
         [c("A-03"), c("R8l/24"), c("+0.04"), c("checked")],
         [c("A-04"), c("R81/24"), c("-0.00"), c("recheck!")],
         [c("B-11", rowspan=2), c("um-6"), c("—"), c("no drift")],
         [c("β-2"), c("0.00"), c("pending")],
         [c("Source < & code", colspan=2), c("reciept"), c("keep literal")],
     ], font="Times-Roman", size=12, header_fill="slate", rule="rust", top=520,
        footnote="2. The long dash in the Offset column is not a minus sign.")]},
    {"id": "N3", "group": "native", "density": "dense", "page_title": "Canal survey | sheet 6",
     "prose": "Survey notes follow the map grid. Table order is left panel, then right panel.",
     "tables": [
       table("Gate measurements", [90, 98, 98, 95, 100], [
         [c("Gate", "th"), c("Chainage", "th"), c("Rise", "th"), c("Flow", "th"), c("Flag", "th")],
         [c("G-1"), c("0+00"), c("1.2 m"), c("4.0"), c("open")],
         [c("G-2"), c("0+85"), c("1.0 m"), c("3.8"), c("inspect")],
         [c("G-3"), c("1+70"), c("0.8 m"), c(""), c("—")],
         [c("Reference datum: MSL-2", colspan=5)],
       ], font="Courier", size=10, header_fill="navy", rule="teal", top=555,
          footnote="a. Blank Flow at G-3 is unreported, not zero."),
       table("Sample tags", [125, 125, 125, 106], [
         [c("Collection", "th", colspan=2), c("Review", "th", colspan=2)],
         [c("Station", "th"), c("Sample ID", "th"), c("pH", "th"), c("Seal", "th")],
         [c("C-09"), c("c-09/a"), c("7.01"), c("intact")],
       ], font="Helvetica", size=10, header_fill="slate", rule="rust", top=250,
          footnote="b. The slash and case are part of each sample ID."),
     ]},
    {"id": "R1", "group": "raster", "density": "sparse", "page_title": "Archive cart | slip 3",
     "prose": "The clerk transcribed labels from the sealed cart; handwritten additions are outside this table.",
     "tables": [table("Shelf moves", [150, 155, 150], [
         [c("Shelf", "th"), c("Move code", "th"), c("State", "th")],
         [c("L-2"), c("0O-6"), c("awaiting")],
         [c("L-3"), c("00-6"), c("complete")],
         [c("Lock & pin retained", colspan=3)],
     ], font="Helvetica", size=13, header_fill="teal", rule="slate", top=520,
        footnote="1. Letter O and digit zero both occur in the codes.")]},
    {"id": "R2", "group": "raster", "density": "medium", "page_title": "Orchard inventory | block C",
     "prose": "Fruit counts are per bin. A blank cell was left unmarked on the source sheet.",
     "tables": [table("Picking summary", [106, 105, 105, 105], [
         [c("Row", "th"), c("Variety", "th"), c("Grade", "th"), c("Count", "th")],
         [c("C-1"), c("Moro"), c("A+"), c("18")],
         [c("C-2"), c("Moro"), c("B"), c("—")],
         [c("C-3"), c("Pera"), c("A"), c("")],
         [c("C-4"), c("Pera"), c("A"), c("23")],
         [c("Totals checked", colspan=2), c("not signed"), c("41")],
     ], font="Times-Roman", size=12, header_fill="rust", rule="teal", top=520,
        footnote="2. Dash means none picked; blank Count means not entered.")]},
    {"id": "R3", "group": "raster", "density": "dense", "page_title": "Rail depot handover | form 27",
     "prose": "Read both panels in order. Values with a plus sign include the printed modifier.",
     "tables": [
       table("Track inspection", [105, 105, 105, 105, 106], [
         [c("Track", "th"), c("Marker", "th"), c("Wear", "th"), c("Limit", "th"), c("Result", "th")],
         [c("T-7"), c("km 08+4"), c("0.7"), c("1.0"), c("pass")],
         [c("T-8"), c("km 09+1"), c("1.1"), c("1.0"), c("repair")],
         [c("T-9"), c("km 10+0"), c("0.0"), c("1.0"), c("pass")],
       ], font="Courier", size=10, header_fill="slate", rule="rust", top=555,
          footnote="a. Marker strings are copied as printed."),
       table("Parts returned", [150, 145, 145, 86], [
         [c("Part", "th"), c("Bin", "th"), c("Qty", "th"), c("Seal", "th")],
         [c("coupler"), c("r-14"), c("2"), c("ok")],
         [c("washer"), c("R-14"), c("—"), c("open")],
       ], font="Helvetica", size=10, header_fill="teal", rule="navy", top=265,
          footnote="b. 1+ means one plus an uncounted partial."),
     ]},
    {"id": "A1", "group": "hold", "density": "sparse", "page_title": "Container dispatch | card 5",
     "prose": "Codes are copied from the dispatch card before each container is sealed.",
     "tables": [table("Container check", [150, 150, 165], [
         [c("Container", "th"), c("Code", "th"), c("Seal", "th")],
         [c("Jar-5"), c(f"K8{AMBIGUOUS_CODEPOINT}4"), c("intact")],
         [c("Jar-6"), c("K84"), c("intact")],
         [c("Review mark", colspan=3)],
     ], font="AliasMono", size=13, header_fill="rust", rule="slate", top=520,
        footnote="1. Keep printed separators in the order shown.")]},
    {"id": "A2", "group": "hold", "density": "medium", "page_title": "Meter return | damaged copy",
     "prose": "The photocopy is abraded in one cell. Do not reconstruct a value from the neighboring row.",
     "tables": [table("Return readings", [120, 125, 120, 100], [
         [c("Meter", "th"), c("Route", "th"), c("Reading", "th"), c("Check", "th")],
         [c("M-4"), c("west/3"), c("14.62"), c("ok")],
         [c("M-5"), c("west/3"), c("?"), c("hold")],
         [c("M-6"), c("west/4"), c("14.67"), c("ok")],
         [c("Copy damaged", colspan=4)],
     ], font="Times-Roman", size=12, header_fill="slate", rule="rust", top=520,
        footnote="2. M-5 Reading is an abraded patch; its digits cannot be recovered." )]},
]


def html_cell(cell: dict[str, Any]) -> str:
    attrs = ""
    if cell["colspan"] != 1:
        attrs += f' colspan="{cell["colspan"]}"'
    if cell["rowspan"] != 1:
        attrs += f' rowspan="{cell["rowspan"]}"'
    return f'<{cell["tag"]}{attrs}>{html.escape(cell["text"], quote=False)}</{cell["tag"]}>'


def table_html(t: dict[str, Any], case_id: str) -> str:
    rendered_rows = []
    for ri, row in enumerate(t["rows"]):
        cells = []
        for ci, cell in enumerate(row):
            shown = dict(cell)
            if case_id == "A1" and ri == 1 and ci == 1:
                shown["text"] = "K814"  # diagnostic only; the l/1 choice remains unresolved
            if case_id == "A2" and ri == 2 and ci == 2:
                shown["text"] = ""  # no exact cell text is established by the damaged source
            cells.append(html_cell(shown))
        rendered_rows.append("<tr>" + "".join(cells) + "</tr>")
    return "<table>" + "".join(rendered_rows) + "</table>"


def layout_rows(rows: list[list[dict[str, Any]]], ncols: int):
    occupied = [[False] * ncols for _ in rows]
    placed = []
    for ri, row in enumerate(rows):
        ci = 0
        for cell in row:
            while ci < ncols and occupied[ri][ci]:
                ci += 1
            cs, rs = cell["colspan"], cell["rowspan"]
            if ci + cs > ncols or ri + rs > len(rows):
                raise ValueError("invalid span")
            for rr in range(ri, ri + rs):
                for cc in range(ci, ci + cs):
                    if occupied[rr][cc]:
                        raise ValueError("overlapping span")
                    occupied[rr][cc] = True
            placed.append((ri, ci, cell))
            ci += cs
    return placed


def draw_table(pdf: canvas.Canvas, t: dict[str, Any], case_id: str, bounds: dict[str, list[int]],
               page_index: int, ambiguity: list[dict[str, Any]]) -> None:
    top = t["top"]
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColorRGB(*COLORS[t["rule"]])
    pdf.drawString(52, top + 17, t["title"])
    ncols = len(t["widths"])
    row_h = 34 if t["size"] >= 12 else 28
    grid_top = top
    placed = layout_rows(t["rows"], ncols)
    all_x = [52]
    for w in t["widths"]:
        all_x.append(all_x[-1] + w)
    x0, x1 = all_x[0], all_x[-1]
    bounds[t["title"]] = [round(x0), round(PAGE_H - grid_top), round(x1), round(PAGE_H - (grid_top - len(t["rows"]) * row_h))]
    pdf.setStrokeColorRGB(*COLORS[t["rule"]])
    pdf.setLineWidth(0.75)
    # Draw row boundaries in segments, leaving a gap under active row spans.
    for boundary in range(len(t["rows"]) + 1):
        y = grid_top - boundary * row_h
        blocked = set()
        for r0, c0, cell in placed:
            if r0 < boundary < r0 + cell["rowspan"]:
                blocked.update(range(c0, c0 + cell["colspan"]))
        for col in range(ncols):
            if col not in blocked:
                pdf.line(all_x[col], y, all_x[col + 1], y)
    # Draw column boundaries in segments, leaving a gap through active col spans.
    for boundary in range(ncols + 1):
        x = all_x[boundary]
        for row in range(len(t["rows"])):
            blocked = False
            for r0, c0, cell in placed:
                if r0 <= row < r0 + cell["rowspan"] and c0 < boundary < c0 + cell["colspan"]:
                    blocked = True
                    break
            if not blocked:
                y0 = grid_top - row * row_h
                pdf.line(x, y0, x, y0 - row_h)
    for ri, ci, cell in placed:
        cs, rs = cell["colspan"], cell["rowspan"]
        x = all_x[ci]
        y_top = grid_top - ri * row_h
        width = sum(t["widths"][ci:ci+cs])
        if cell.get("fill"):
            pdf.setFillColorRGB(*COLORS[cell["fill"]])
            pdf.rect(x + 0.5, y_top - row_h * rs + 0.5, width - 1, row_h * rs - 1, fill=1, stroke=0)
        label = cell["text"]
        if case_id == "A2" and ri == 2 and ci == 2:
            label = "14.6?"
        pdf.setFillColorRGB(0.12, 0.15, 0.18)
        font = "Helvetica-Bold" if cell["tag"] == "th" else t["font"]
        pdf.setFont(font, t["size"])
        tx = x + 7
        ty = y_top - row_h * rs / 2 - t["size"] * 0.35
        if case_id == "A1" and ri == 1 and ci == 1:
            pdf.drawString(tx, ty, label)
            ambiguity.append({"table_index": len(bounds)-1, "row": ri, "cell": ci,
                              "bbox_points": [round(tx), round(PAGE_H - (ty + t["size"])), round(tx+stringWidth(label, font, t["size"])), round(PAGE_H - ty)],
                              "alternatives": ["K8l4", "K814"], "reason": "the lowercase l and digit 1 in this cell use the same glyph and the same advance in the printed font"})
        elif case_id == "A2" and ri == 2 and ci == 2:
            pdf.setFillColorRGB(0.72, 0.72, 0.72)
            pdf.rect(tx, ty - 3, 66, t["size"] + 7, fill=1, stroke=0)
            pdf.setStrokeColorRGB(0.55, 0.55, 0.55)
            for k in range(6):
                yy = ty - 2 + k * 3
                pdf.line(tx - 1, yy, tx + 67, yy + 1)
            ambiguity.append({"table_index": len(bounds)-1, "row": ri, "cell": ci,
                              "bbox_points": [round(tx+17), round(PAGE_H-(ty+t["size"]+5)), round(tx+46), round(PAGE_H-(ty-4))],
                              "alternatives": [], "reason": "photocopy abrasion removes the remaining cell digits; no exact value is recoverable"})
        else:
            shown = label
            # Keep all content in bounds; clip exceptionally long merged labels naturally.
            pdf.drawString(tx, ty, shown)
    if t["footnote"]:
        pdf.setFillColorRGB(0.25, 0.28, 0.31)
        pdf.setFont("Helvetica-Oblique", 9)
        pdf.drawString(52, grid_top - len(t["rows"]) * row_h - 20, t["footnote"])


def draw_page(pdf: canvas.Canvas, page: dict[str, Any], pidx: int) -> dict[str, Any]:
    pdf.setFillColorRGB(0.96, 0.96, 0.93)
    pdf.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    pdf.setFillColorRGB(*COLORS["navy"])
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(52, PAGE_H - 47, page["page_title"])
    pdf.setFillColorRGB(0.25, 0.28, 0.31)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(52, PAGE_H - 64, f"Synthetic survey sheet   |   source page {pidx+1:02d}")
    pdf.setFont("Times-Roman", 10)
    pdf.drawString(52, PAGE_H - 88, page["prose"])
    bounds: dict[str, list[int]] = {}
    uncertainty: list[dict[str, Any]] = []
    for ti, t in enumerate(page["tables"]):
        # table index is the order in which a source reader encounters each panel
        draw_table(pdf, t, page["id"], bounds, pidx, uncertainty)
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.setFillColorRGB(0.3, 0.32, 0.34)
    pdf.drawRightString(PAGE_W - 52, 28, f"FORM {page['id']}  •  {pidx+1}")
    return {"table_bounds_points": bounds, "uncertain_cells": uncertainty}


def write_group(group: str, pages: list[dict[str, Any]]) -> Path:
    path = SOURCE / f"{group}.pdf"
    pdf = canvas.Canvas(str(path), pagesize=letter, pageCompression=1)
    pdf.setTitle(f"Synthetic {group.title()} Table Sources")
    pdf.setAuthor("Synthetic fixture generator")
    for i, page in enumerate(pages):
        page["layout"] = draw_page(pdf, page, i)
        pdf.showPage()
    pdf.save()
    return path


def image_only_pdf(native_path: Path, target: Path) -> None:
    from pdf2image import convert_from_path
    raster_pages = convert_from_path(str(native_path), dpi=300, fmt="png", use_cropbox=False)
    pdf = canvas.Canvas(str(target), pagesize=letter, pageCompression=1)
    pdf.setTitle("Synthetic image-only table sources")
    for i, image in enumerate(raster_pages, start=1):
        temp = BUILD / f"page-render-{i:02d}.png"
        image.save(temp, format="PNG", optimize=False)
        pdf.drawImage(str(temp), 0, 0, width=PAGE_W, height=PAGE_H, preserveAspectRatio=False, mask=None)
        pdf.showPage()
    pdf.save()
    for image in raster_pages:
        image.close()


def cell_count(t: dict[str, Any]) -> int:
    return sum(t["colspan"] * t["rowspan"] for row in t["rows"] for t in row)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_alias_font_and_counterfactuals() -> dict[str, Any]:
    """Alias l, 1, and a neutral marker to the same embedded Andale Mono glyph."""
    PROOF.mkdir(parents=True, exist_ok=True)
    font = FontToolsTTFont(str(SOURCE_FONT))
    unicode_tables = [subtable for subtable in font["cmap"].tables if subtable.isUnicode()]
    if not unicode_tables:
        raise RuntimeError("source font has no Unicode cmap")
    glyph_name = unicode_tables[0].cmap[ord("1")]
    original_l = unicode_tables[0].cmap[ord("l")]
    if glyph_name == original_l:
        raise RuntimeError("source font unexpectedly already aliases lowercase l and digit 1")
    for subtable in unicode_tables:
        subtable.cmap[ord("l")] = glyph_name
        subtable.cmap[ord("1")] = glyph_name
        subtable.cmap[ord(AMBIGUOUS_CODEPOINT)] = glyph_name
    font.save(str(ALIAS_FONT))
    font.close()
    pdfmetrics.registerFont(ReportLabTTFont("AliasMono", str(ALIAS_FONT)))

    test_font = ImageFont.truetype(str(ALIAS_FONT), 64)
    variants = {"lowercase-l": "K8l4", "digit-one": "K814"}
    images: dict[str, Image.Image] = {}
    for key, value in variants.items():
        image = Image.new("L", (240, 100), 255)
        ImageDraw.Draw(image).text((8, 10), value, fill=0, font=test_font)
        image.save(PROOF / f"A1-{key}.png", format="PNG", optimize=False)
        images[key] = image
    same_pixels = images["lowercase-l"].tobytes() == images["digit-one"].tobytes()
    if not same_pixels or test_font.getlength("K8l4") != test_font.getlength("K814"):
        raise RuntimeError("counterfactual ambiguity glyphs are not optically identical")
    difference = Image.new("L", images["lowercase-l"].size, 255)
    pixels_a, pixels_b, pixels_d = images["lowercase-l"].load(), images["digit-one"].load(), difference.load()
    for y in range(difference.height):
        for x in range(difference.width):
            pixels_d[x, y] = abs(pixels_a[x, y] - pixels_b[x, y])
    difference.save(PROOF / "A1-difference.png", format="PNG", optimize=False)
    for image in images.values():
        image.close()
    difference.close()
    result = {"case_id": "A1", "table_index": 0, "row": 1, "cell": 1,
              "alternatives": list(variants.values()), "font_family": "Andale Mono",
              "source_font_path": str(SOURCE_FONT), "source_font_sha256": sha(SOURCE_FONT),
              "aliased_glyph_name": glyph_name, "original_l_glyph_name": original_l,
              "font_input_sha256": sha(SOURCE_FONT), "aliased_font_sha256": sha(ALIAS_FONT),
              "counterfactual_render_size_px": [240, 100], "pixel_arrays_identical": same_pixels,
              "advance_widths_px": {key: test_font.getlength(value) for key, value in variants.items()},
              "counterfactual_png_sha256": {key: sha(PROOF / f"A1-{key}.png") for key in variants},
              "difference_png_sha256": sha(PROOF / "A1-difference.png"),
              "interpretation": "Both allowed source readings use the same font glyph and advance at this location; neither is designated as the intended literal."}
    (PROOF / "A1-counterfactual-proof.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    for d in (BUILD, SOURCE, GOLD, PROOF):
        d.mkdir(parents=True, exist_ok=True)
    create_alias_font_and_counterfactuals()
    groups = {g: [p for p in PAGES if p["group"] == g] for g in ("native", "raster", "hold")}
    native = write_group("native", groups["native"])
    raster_design = write_group("raster-layout-source", groups["raster"])
    hold_design = write_group("hold-layout-source", groups["hold"])
    image_only_pdf(raster_design, SOURCE / "raster.pdf")
    image_only_pdf(hold_design, SOURCE / "holds.pdf")
    (SOURCE / "raster-layout-source.pdf").unlink()
    (SOURCE / "hold-layout-source.pdf").unlink()

    manifest_pages = []
    for group in groups.values():
        for page in group:
            tid = page["id"]
            tables = []
            for ti, t in enumerate(page["tables"]):
                bboxpt = page["layout"]["table_bounds_points"][t["title"]]
                scale = 300 / 72
                bbox = [round(bboxpt[0]*scale), round(bboxpt[1]*scale),
                        round(bboxpt[2]*scale), round(bboxpt[3]*scale)]
                uncertain = []
                for u in page["layout"]["uncertain_cells"]:
                    if u["table_index"] == ti:
                        uncertain.append({"row": u["row"], "cell": u["cell"],
                                          "reason": u["reason"], "alternatives": u["alternatives"]})
                tables.append({"bbox": bbox, "html": table_html(t, tid), "uncertain_cells": uncertain})
            record = {"source_table_count": len(tables), "tables": tables}
            (GOLD / f"{tid}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
            manifest_pages.append({"case_id": tid, "source_group": page["group"], "density": page["density"],
                                   "disposition": "hold" if page["group"] == "hold" else "clear",
                                   "source_pdf_page": list(groups[page["group"]]).index(page)+1,
                                   "tables": len(tables), "cell_slots": sum(cell_count(t) for t in page["tables"]),
                                   "explicit_cells": sum(len(row) for t in page["tables"] for row in t["rows"]),
                                   "spans": [{"table_index": ti, "row": ri, "cell": ci,
                                              "rowspan": cell["rowspan"], "colspan": cell["colspan"]}
                                             for ti, t in enumerate(page["tables"])
                                             for ri, row in enumerate(t["rows"])
                                             for ci, cell in enumerate(row)
                                             if cell["rowspan"] > 1 or cell["colspan"] > 1],
                                   "uncertain_cells": sum(len(t["uncertain_cells"]) for t in tables),
                                   "source_pdf": {"native": "source/native.pdf", "raster": "source/raster.pdf", "hold": "source/holds.pdf"}[page["group"]],
                                   "gold": f"gold/{tid}.json"})
    files = sorted([p for p in SOURCE.glob("*.pdf")] + [p for p in GOLD.glob("*.json")])
    manifest = {"fixture_id": "argon-literal-qualification-v1", "eligibility": "new synthetic campaign material; no real people, private records, copyrighted source documents, provider outputs, or upstream Ingester inputs",
                "source_policy": "gold records preserve visible source characters and structural ownership; A1/A2 uncertainty is explicit and has no exact-cell gold where pixels do not establish it",
                "renderer_target": {"module": "extract_pdf_images_capped_v1", "dpi_cap": 300, "min_dpi": 300, "baseline_dpi": 300, "sample_count": 0, "image_format": "png"},
                "pages": manifest_pages,
                "input_hashes": {str(p.relative_to(ROOT)): sha(p) for p in files}}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"pdfs": [str(p.relative_to(ROOT)) for p in SOURCE.glob("*.pdf")],
                      "cases": [{"id": x["case_id"], "tables": x["tables"], "cells": x["explicit_cells"], "slots": x["cell_slots"], "spans": len(x["spans"]), "uncertain": x["uncertain_cells"]} for x in manifest_pages]}, indent=2))


if __name__ == "__main__":
    main()
