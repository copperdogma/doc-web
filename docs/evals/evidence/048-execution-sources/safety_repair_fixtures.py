"""Deterministic synthetic source/crop pairs; no inference or scan editing."""

import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "benchmarks/input/safety-repair-048"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"


def rect(x, y, w, h, fill="#d7e7f4", stroke="#14263d", width=5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{stroke}"/><rect x="{x + width}" y="{y + width}" width="{w - 2 * width}" height="{h - 2 * width}" fill="{fill}"/>'


def text(x, y, value, size=30):
    return f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" fill="#14263d">{value}</text>'


def diagram(x, y, w, h):
    return (
        rect(x, y, w, h)
        + f'<circle cx="{x + w / 2}" cy="{y + h / 2}" r="{min(w, h) / 4}" fill="#426e91"/>'
    )


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    cases = {
        "S1": (
            rect(100, 180, 800, 470, "#eff5f8")
            + diagram(140, 220, 280, 380)
            + diagram(580, 220, 280, 380)
            + '<polygon points="440,404 528,404 528,390 550,410 528,430 528,416 440,416" fill="#14263d"/>'
            + text(260, 730, "Figure A: connected stages"),
            (100, 180, 900, 650),
            "pass",
            "source-unified outer frame, connection, shared caption",
        ),
        "S2": (
            diagram(100, 180, 330, 470)
            + diagram(570, 180, 330, 470)
            + text(135, 730, "Figure A: sample")
            + text(600, 730, "Figure B: sample"),
            (100, 180, 900, 650),
            "fail",
            "separate framed/captioned neighbor, no leaked caption",
        ),
        "S3": (
            '<path d="M230 225 L475 225 L495 450 L475 675 L230 675 L250 455 Z" fill="#c7d7de"/><path d="M525 225 L770 225 L750 455 L770 675 L525 675 L505 450 Z" fill="#c7d7de"/>'
            + '<polygon points="242,250 257,250 478,640 463,640" fill="#526c78"/><polygon points="257,620 272,620 473,280 458,280" fill="#526c78"/><polygon points="527,280 542,280 743,620 728,620" fill="#526c78"/><polygon points="522,640 537,640 758,250 743,250" fill="#526c78"/><path d="M465 390 L535 485 M460 490 L540 395" stroke="#c7d7de" stroke-width="3" opacity="0.22"/>',
            (220, 200, 780, 700),
            "fail",
            "policy-defined ownership uncertainty; no grouping, caption, connector or enclosing visual frame",
        ),
        "S4": (
            rect(250, 220, 500, 500, "#dfedd5")
            + '<circle cx="500" cy="415" r="120" fill="#598150"/>'
            + text(292, 600, "FIELD STATION", 43)
            + text(320, 820, "Figure C: badge"),
            (250, 220, 750, 720),
            "pass",
            "badge text integral; external caption excluded",
        ),
        "S5": (
            diagram(250, 220, 500, 400)
            + text(305, 688, "Figure D: separate caption", 28),
            (250, 220, 750, 710),
            "fail",
            "external caption visible in crop",
        ),
        "S6": (
            diagram(400, 400, 200, 200),
            (100, 100, 900, 900),
            "fail",
            "93.75 percent blank page margin",
        ),
    }
    inventory = {
        "fixture_class": "new synthetic diagrams; no provider-generated content",
        "renderer": subprocess.check_output(
            ["magick", "-version"], text=True
        ).splitlines()[0],
        "cases": [],
    }
    previews = []
    for key, (content, bounds, verdict, reason) in cases.items():
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000"><rect width="1000" height="1000" fill="white"/>'
            + content
            + "</svg>"
        )
        source = DEST / f"{key}-source.svg"
        source.write_text(svg)
        png = DEST / f"{key}-source.png"
        subprocess.run(
            ["magick", "-font", FONT, str(source), str(png)],
            check=True,
            capture_output=True,
        )
        image = Image.open(png).convert("RGB")
        image.save(png)
        crop = image.crop(bounds)
        crop_path = DEST / f"{key}-crop.png"
        crop.save(crop_path)
        white = sum(1 for rgb in crop.getdata() if min(rgb) >= 250) / (
            crop.width * crop.height
        )
        if key == "S3":
            assert white < 0.4, "uncertainty fixture has excessive blank confound"
        if key == "S6":
            assert white > 0.9
        record = {
            "key": key,
            "verdict": verdict,
            "reason": reason,
            "crop_bounds": bounds,
            "near_white_fraction": white,
            "category": "uncertainty-policy" if key == "S3" else "physical-quality",
            "files": [],
        }
        for f in (source, png, crop_path):
            record["files"].append(
                {
                    "path": str(f.relative_to(ROOT)),
                    "bytes": f.stat().st_size,
                    "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                }
            )
        inventory["cases"].append(record)
        previews.append((key, verdict, image, crop))
    sheet = Image.new("RGB", (1500, 3 * 540), "white")
    draw = ImageDraw.Draw(sheet)
    for i, (key, verdict, source, crop) in enumerate(previews):
        x, y = (i % 2) * 750, (i // 2) * 540
        draw.text((x + 10, y + 5), f"{key} {verdict}: SOURCE | CROP", fill="black")
        for j, im in enumerate((source, crop)):
            thumb = ImageOps.contain(im, (360, 495))
            sheet.paste(
                thumb,
                (
                    x + j * 375 + (360 - thumb.width) // 2,
                    y + 30 + (495 - thumb.height) // 2,
                ),
            )
    sheet.save(DEST / "contact-sheet.png")
    (DEST / "inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
    print(
        json.dumps(
            {
                "contact_sheet": str(DEST / "contact-sheet.png"),
                "cases": [
                    {
                        "key": x["key"],
                        "verdict": x["verdict"],
                        "near_white_fraction": x["near_white_fraction"],
                    }
                    for x in inventory["cases"]
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
