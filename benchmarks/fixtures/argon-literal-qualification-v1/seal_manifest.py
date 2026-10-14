#!/usr/bin/env python3
"""Seal exact fixture and maintained renderer inputs/outputs into manifest.json."""
import hashlib
import platform
import json
import subprocess
import sys
from pathlib import Path
from importlib.metadata import version

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    data = json.loads((ROOT / "manifest.json").read_text())
    gold_by_id = {p.stem: json.loads(p.read_text()) for p in (ROOT / "gold").glob("*.json")}
    pages = []
    for case_id in ("N1", "N2", "N3", "R1", "R2", "R3", "A1", "A2"):
        g = gold_by_id[case_id]
        spec = next(p for p in data["pages"] if p["case_id"] == case_id)
        image = ROOT / "renders" / f"{case_id}.png"
        with Image.open(image) as im:
            dimensions = list(im.size)
        pages.append({**spec, "gold_schema_keys": list(g), "gold": f"gold/{case_id}.json",
                      "gold_sha256": digest(ROOT / "gold" / f"{case_id}.json"),
                      "render": f"renders/{case_id}.png", "render_dimensions_px": dimensions,
                      "render_sha256": digest(image)})

    pdfs = {
        "native": ROOT / "source/native.pdf",
        "raster": ROOT / "source/raster.pdf",
        "holds": ROOT / "source/holds.pdf",
    }
    pdf_metadata = {}
    for group, path in pdfs.items():
        reader = PdfReader(str(path))
        pdf_metadata[group] = {
            "path": rel(path), "sha256": digest(path), "pages": len(reader.pages),
            "page_dimensions_points": [[float(p.mediabox.width), float(p.mediabox.height)] for p in reader.pages],
            "extracted_text_characters_per_page": [len(p.extract_text() or "") for p in reader.pages],
        }
    root_inputs = {
        "generator": ROOT / "generate_fixture.py",
        "manifest_sealer": ROOT / "seal_manifest.py",
        "renderer_module": REPO / "modules/extract/extract_pdf_images_capped_v1/main.py",
        "renderer_recipe": REPO / "configs/recipes/recipe-pdf-literal-tables-html.yaml",
        "pdf_skill": Path("/Users/cam/.codex/plugins/cache/openai-primary-runtime/pdf/26.1011.11113/skills/pdf/SKILL.md"),
        "source_font": Path("/System/Library/Fonts/Supplemental/Andale Mono.ttf"),
        "aliased_font": ROOT / "build/argon-ambiguity-mono.ttf",
    }
    runtime_packages = {name: version(package) for name, package in {
        "Pillow": "Pillow", "reportlab": "reportlab", "pypdf": "pypdf",
        "numpy": "numpy", "pdf2image": "pdf2image", "PyYAML": "PyYAML",
        "fonttools": "fonttools",
    }.items()}
    poppler = subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True, check=False)
    poppler_version = (poppler.stderr or poppler.stdout).splitlines()[0]
    renderer_prefix = f"PYTHONPATH={REPO} /Users/cam/miniconda3/bin/python"
    manifest = {
        "fixture_id": "argon-literal-qualification-v1",
        "eligibility": "new synthetic campaign material; no real people, private records, copyrighted source documents, provider outputs, or downstream Ingester inputs",
        "source_policy": "gold records preserve visible source characters and structural ownership; A1/A2 uncertainty is explicit and has no exact-cell gold where pixels do not establish it",
        "gold_contract": "source_table_count and tables[{bbox,html,uncertain_cells}] only; safe-HTML visible text and ownership define the clear truth",
        "renderer": {"module": "extract_pdf_images_capped_v1", "dpi_cap": 300, "min_dpi": 300,
                     "baseline_dpi": 300, "sample_count": 0, "image_format": "png",
                     "page_size": "US Letter", "expected_pixels": [2550, 3300],
                     "composition": "full page rendered by maintained PDF renderer; no crop or native text insertion"},
        "runtime": {"invoked_python": "/Users/cam/miniconda3/bin/python",
                    "resolved_executable": str(Path(sys.executable).resolve()),
                    "python_version": sys.version, "platform": platform.platform(),
                    "packages": runtime_packages, "poppler": poppler_version},
        "dependencies": {"driver_runtime": "/Users/cam/miniconda3/bin/python",
                         "renderer_imports": ["numpy", "Pillow", "pdf2image", "pypdf", "PyYAML"]},
        "generation_command": f"{renderer_prefix} benchmarks/fixtures/argon-literal-qualification-v1/generate_fixture.py",
        "render_commands": [
            f"{renderer_prefix} modules/extract/extract_pdf_images_capped_v1/main.py --pdf benchmarks/fixtures/argon-literal-qualification-v1/source/native.pdf --outdir benchmarks/fixtures/argon-literal-qualification-v1/build/render-native --dpi-cap 300 --baseline-dpi 300 --min-dpi 300 --sample-count 0 --image-format png --start 1 --end 3",
            f"{renderer_prefix} modules/extract/extract_pdf_images_capped_v1/main.py --pdf benchmarks/fixtures/argon-literal-qualification-v1/source/raster.pdf --outdir benchmarks/fixtures/argon-literal-qualification-v1/build/render-raster --dpi-cap 300 --baseline-dpi 300 --min-dpi 300 --sample-count 0 --image-format png --start 1 --end 3",
            f"{renderer_prefix} modules/extract/extract_pdf_images_capped_v1/main.py --pdf benchmarks/fixtures/argon-literal-qualification-v1/source/holds.pdf --outdir benchmarks/fixtures/argon-literal-qualification-v1/build/render-holds --dpi-cap 300 --baseline-dpi 300 --min-dpi 300 --sample-count 0 --image-format png --start 1 --end 2",
        ],
        "ambiguity_proof": json.loads((ROOT / "proof/A1-counterfactual-proof.json").read_text()),
        "source_pdfs": pdf_metadata,
        "inputs_sha256": {key: digest(path) for key, path in root_inputs.items()},
        "pages": pages,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    corpus = {
        "corpus_id": manifest["fixture_id"],
        "source_policy": manifest["source_policy"],
        "cases": [
            {key: page[key] for key in (
                "case_id", "source_group", "density", "disposition", "source_pdf",
                "source_pdf_page", "gold", "render", "tables", "explicit_cells",
                "cell_slots", "spans", "uncertain_cells", "gold_sha256",
                "render_sha256", "render_dimensions_px")}
            for page in pages
        ],
    }
    (ROOT / "corpus.json").write_text(json.dumps(corpus, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"manifest": str(ROOT / "manifest.json"),
                      "page_count": len(pages),
                      "render_sha256": {p["case_id"]: p["render_sha256"] for p in pages},
                      "pdf_text_characters": {k: v["extracted_text_characters_per_page"] for k, v in pdf_metadata.items()}}, indent=2))


if __name__ == "__main__":
    main()
