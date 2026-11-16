# ruff: noqa: E402
import sys
import json
import os
import subprocess
import shutil
from pathlib import Path
from types import SimpleNamespace
import yaml
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from modules.common.utils import read_jsonl, save_jsonl
from modules.common.crop_review import require
from modules.common.crop_safety_custody import prepare_custody
from modules.common.crop_review_setup import write_templates
from benchmarks.scripts import hydrogen_native as transport

native = SimpleNamespace(save=transport.guard.save)


# Materialized established caller preparation; source preserved in attempt provenance.
def prepare_case(arm, case, variant="live"):
    run, fixture, out = paths(arm, case, variant)
    require(
        not fixture.exists() and not out.exists(), "Fresh native caller run required"
    )
    fixture.mkdir(parents=True, mode=0o700)
    original = fixture / "input"
    original.mkdir()
    (original / "images").mkdir()
    baseline = ROOT / "tests/fixtures/crop_review_offline/approved"
    source = baseline / f"{case}-source.png"
    crop = baseline / "images" / f"{case}.png"
    shutil.copyfile(source, original / source.name)
    shutil.copyfile(crop, original / "images" / crop.name)
    row = next(
        r for r in read_jsonl(baseline / "manifest.jsonl") if r["filename"] == crop.name
    )
    row.update(
        source_page=1,
        source_image=str(original / source.name),
        run_id="source-owned-hydrogen094-input",
        source_dimensions=[1000, 1000],
        coordinate_system="source_pixels",
        crop_transform="rectangle_and_encode",
    )
    save_jsonl(original / "manifest.jsonl", [row])
    textonly = original / "text-only-page.png"
    im = Image.new("RGB", (1000, 1000), "white")
    ImageDraw.Draw(im).text(
        (120, 120), "Text-only source page: no illustration", fill="black"
    )
    im.save(textonly)
    source_map = [
        {"source_page": 1, "source_image": str(original / source.name)},
        {"source_page": 2, "source_image": str(textonly)},
    ]
    native.save(original / "source-map.json", source_map)
    pages = [
        {
            "schema_version": "page_html_v1",
            "page": 1,
            "page_number": 1,
            "html": f'<h1>Hydrogen094 public synthetic {case}</h1><p>Selected original source page.</p><img alt="Reviewed synthetic source visual">',
        },
        {
            "schema_version": "page_html_v1",
            "page": 2,
            "page_number": 2,
            "html": "<p>Text-only source page: no illustration.</p>",
        },
    ]
    save_jsonl(original / "pages.ndjson", pages)
    save_jsonl(
        original / "portions.ndjson",
        [
            {
                "schema_version": "portion_hypothesis_v1",
                "title": "Hydrogen094 synthetic review mechanics",
                "page_start": 1,
                "page_end": 2,
            }
        ],
    )
    custody = fixture / "custody"
    prepare_custody(
        original / "manifest.jsonl",
        original / "pages.ndjson",
        original / "portions.ndjson",
        original / "source-map.json",
        original,
        custody,
        run,
    )
    write_templates(custody, run)
    recipe = yaml.safe_load(
        (ROOT / "configs/recipes/story-242-sol-crop-safety-offline.yaml").read_text()
    )
    recipe["input"]["text_glob"] = str(original / "source-map.json")
    for stage in recipe["stages"]:
        for key, value in list(stage.get("params", {}).items()):
            if isinstance(value, str) and value.startswith(
                "output/runs/story242-crop-safety-fixture"
            ):
                stage["params"][key] = str(
                    fixture
                    / Path(value).relative_to(
                        "output/runs/story242-crop-safety-fixture"
                    )
                )
        if stage["id"] == "propose_safety":
            stage["params"].update(
                mode="live",
                cap_usd=0.31476 if arm == "candidate" else 0.155960,
                max_calls=1,
            )
            stage["params"].pop("replay_manifest", None)
        if stage["id"] == "build_reviewed":
            stage["params"]["crop_review_release"] = str(
                out / "05_release_reviewed_crops_v1/crop_review_release.json"
            )
            stage["params"]["book_title"] = (
                "Hydrogen094 evaluation - synthetic operator mechanics only"
            )
    (fixture / "recipe.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False))
    return run, fixture, out, recipe


def paths(arm, case, variant="live"):
    run = f"hydrogen094-{arm}-{case}-{variant}-transport2"
    return run, ROOT / "output/runs" / (run + "-fixture"), ROOT / "output/runs" / run


arm = sys.argv[1]
case = "S3"
run, fixture, out, _ = prepare_case(arm, case)
startup = transport.guard.RESULTS / "caller-startup"
startup.mkdir(exist_ok=True)
(startup / "sitecustomize.py").write_text(
    "import sys;sys.path.insert(0,"
    + repr(str(ROOT))
    + ");from benchmarks.scripts.hydrogen_caller import install;install()\n"
)
env = dict(
    os.environ, HYDROGEN_CALLER_ARM=arm, PYTHONPATH=str(startup) + ":" + str(ROOT)
)
with (fixture / "driver.log").open("w") as log:
    rc = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            str(fixture / "recipe.yaml"),
            "--run-id",
            run,
            "--output-dir",
            str(out),
            "--end-at",
            "propose_safety",
        ],
        cwd=ROOT,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
    ).returncode
p = out / "03_propose_crop_safety_v1/proposals.jsonl"
rows = list(read_jsonl(p)) if p.exists() else []
result = {
    "arm": arm,
    "case": case,
    "driver_exit": rc,
    "proposals": str(p.relative_to(ROOT)),
    "rows": rows,
    "operator_action": False,
}
native.save(transport.guard.E / f"caller-S3-{arm}-result.json", result)
print(json.dumps(result, indent=2))
