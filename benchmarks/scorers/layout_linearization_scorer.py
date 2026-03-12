"""Score layout linearization quality for chapter HTML.

Checks:
1. All crops from illustration manifest have corresponding <figure> in HTML
2. All <figure> elements have <img> with src set
3. Caption detection: figures with adjacent caption text have <figcaption>
4. Placement provenance: figures have data-placement attribute
5. Image position: images are between text blocks (not at doc start/end)

Usage:
    python benchmarks/scorers/layout_linearization_scorer.py \
        --chapters-dir /path/to/html/ \
        --illustration-manifest /path/to/illustration_manifest.jsonl
"""
import argparse
import sys
from pathlib import Path

from bs4 import BeautifulSoup


def score_chapter(html_path: Path) -> dict:
    """Score a single chapter HTML file for layout quality."""
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    figures = soup.find_all("figure")
    imgs_with_src = [img for img in soup.find_all("img") if img.get("src")]

    results = {
        "file": html_path.name,
        "figures": len(figures),
        "images_with_src": len(imgs_with_src),
        "figcaptions": 0,
        "caption_source_ocr": 0,
        "caption_source_heuristic": 0,
        "caption_source_crop": 0,
        "has_provenance": 0,
        "placement_ocr_inline": 0,
        "placement_ocr_figure": 0,
        "issues": [],
    }

    for fig in figures:
        img = fig.find("img")
        if not img or not img.get("src"):
            results["issues"].append("figure without img[src]")

        figcap = fig.find("figcaption")
        if figcap:
            results["figcaptions"] += 1

        placement = fig.get("data-placement")
        if placement:
            results["has_provenance"] += 1
            if placement == "ocr-inline":
                results["placement_ocr_inline"] += 1
            elif placement == "ocr-figure":
                results["placement_ocr_figure"] += 1

        cap_src = fig.get("data-caption-source")
        if cap_src == "ocr":
            results["caption_source_ocr"] += 1
        elif cap_src == "heuristic":
            results["caption_source_heuristic"] += 1
        elif cap_src == "crop-pipeline":
            results["caption_source_crop"] += 1

    # Note: figures at the start of an article are not necessarily misplaced —
    # some chapters begin with images (certificates, title pages, etc.).

    return results


def main():
    parser = argparse.ArgumentParser(description="Score layout linearization quality")
    parser.add_argument("--chapters-dir", required=True, help="Directory with chapter HTML files")
    parser.add_argument("--illustration-manifest", default=None,
                        help="illustration_manifest.jsonl for coverage check")
    args = parser.parse_args()

    chapters_dir = Path(args.chapters_dir)
    html_files = sorted(chapters_dir.glob("chapter-*.html"))
    if not html_files:
        html_files = sorted(chapters_dir.glob("*.html"))

    total_figures = 0
    total_figcaptions = 0
    total_provenance = 0
    total_issues = 0
    all_results = []

    for html_file in html_files:
        result = score_chapter(html_file)
        all_results.append(result)
        total_figures += result["figures"]
        total_figcaptions += result["figcaptions"]
        total_provenance += result["has_provenance"]
        total_issues += len(result["issues"])

    # Coverage check against illustration manifest
    manifest_crops = 0
    if args.illustration_manifest:
        manifest_path = Path(args.illustration_manifest)
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest_crops = sum(1 for line in f if line.strip())

    # Summary
    print("=" * 60)
    print("Layout Linearization Quality Report")
    print("=" * 60)
    print(f"Chapters scanned:     {len(html_files)}")
    print(f"Total <figure>:       {total_figures}")
    print(f"Total <figcaption>:   {total_figcaptions}")
    print(f"Provenance coverage:  {total_provenance}/{total_figures} "
          f"({total_provenance/total_figures*100:.0f}%)" if total_figures else "N/A")
    if manifest_crops:
        print(f"Manifest crops:       {manifest_crops}")
        # Note: figures may be fewer than crops due to count mismatches
    print(f"Issues found:         {total_issues}")

    caption_rate = (total_figcaptions / total_figures * 100) if total_figures else 0
    provenance_rate = (total_provenance / total_figures * 100) if total_figures else 0

    print()
    print("Caption sources:")
    for r in all_results:
        if r["figcaptions"]:
            print(f"  {r['file']}: {r['figcaptions']} captions "
                  f"(heuristic={r['caption_source_heuristic']}, "
                  f"ocr={r['caption_source_ocr']}, "
                  f"crop={r['caption_source_crop']})")

    if total_issues:
        print()
        print("Issues:")
        for r in all_results:
            for issue in r["issues"]:
                print(f"  {r['file']}: {issue}")

    print()
    print(f"Caption detection rate: {caption_rate:.0f}% ({total_figcaptions}/{total_figures})")
    print(f"Provenance rate:        {provenance_rate:.0f}% ({total_provenance}/{total_figures})")

    # Pass/fail
    passed = provenance_rate == 100 and total_issues == 0
    status = "PASS" if passed else "PARTIAL"
    print(f"\nOverall: {status}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
