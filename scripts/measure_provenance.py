#!/usr/bin/env python3
"""Measure provenance completeness across a pipeline run.

Checks every JSONL artifact and the final gamebook.json for required
provenance fields, per the spec: "Every output traces to source page,
OCR engine, confidence score, and processing step."

Usage:
    python scripts/measure_provenance.py output/runs/<run_id>
    python scripts/measure_provenance.py output/runs/<run_id> --verbose
"""

import argparse
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field


# ── Provenance field requirements per schema ────────────────────────────

# Every JSONL artifact record must have these (the "envelope")
ENVELOPE_FIELDS = ["schema_version", "module_id", "run_id", "created_at"]

# Page-level artifacts must additionally have page tracing
PAGE_FIELDS = ["page"]

# OCR output artifacts (page_html_v1) must have quality/confidence
OCR_FIELDS = ["ocr_quality", "ocr_integrity", "source"]

# Gamebook section provenance must have these
GAMEBOOK_SECTION_PROVENANCE = [
    "source_pages", "source_images", "module_id", "run_id", "confidence"
]

# Schemas that are page-level artifacts (have a page field)
PAGE_SCHEMAS = {
    "page_image_v1", "page_html_v1", "page_html_blocks_v1",
    "image_crop_v1", "clean_page_v1", "pagelines_v1",
}

# Schemas that are OCR output (have quality metadata)
OCR_SCHEMAS = {"page_html_v1"}


@dataclass
class StageResult:
    stage_dir: str
    schema: str = "unknown"
    total_records: int = 0
    envelope_present: int = 0
    envelope_missing: dict = field(default_factory=dict)
    page_present: int = 0
    page_applicable: int = 0
    page_missing: int = 0
    ocr_present: int = 0
    ocr_applicable: int = 0
    ocr_missing: dict = field(default_factory=dict)

    @property
    def envelope_score(self) -> float:
        if self.total_records == 0:
            return 1.0
        return self.envelope_present / self.total_records

    @property
    def page_score(self) -> float:
        if self.page_applicable == 0:
            return 1.0  # N/A
        return self.page_present / self.page_applicable

    @property
    def ocr_score(self) -> float:
        if self.ocr_applicable == 0:
            return 1.0  # N/A
        return self.ocr_present / self.ocr_applicable

    @property
    def overall_score(self) -> float:
        scores = [self.envelope_score]
        if self.page_applicable > 0:
            scores.append(self.page_score)
        if self.ocr_applicable > 0:
            scores.append(self.ocr_score)
        return sum(scores) / len(scores)


@dataclass
class GamebookResult:
    total_sections: int = 0
    sections_with_provenance: int = 0
    provenance_complete: int = 0
    missing_fields: dict = field(default_factory=dict)

    @property
    def has_provenance_score(self) -> float:
        if self.total_sections == 0:
            return 1.0
        return self.sections_with_provenance / self.total_sections

    @property
    def completeness_score(self) -> float:
        if self.sections_with_provenance == 0:
            return 0.0
        return self.provenance_complete / self.sections_with_provenance

    @property
    def overall_score(self) -> float:
        if self.total_sections == 0:
            return 1.0
        return self.provenance_complete / self.total_sections


def check_jsonl_stage(stage_dir: Path) -> StageResult | None:
    """Check provenance completeness for a stage's JSONL artifacts."""
    jsonl_files = list(stage_dir.glob("*.jsonl"))
    if not jsonl_files:
        return None

    result = StageResult(stage_dir=stage_dir.name)

    for jf in jsonl_files:
        if jf.name in ("pipeline_events.jsonl", "instrumentation_calls.jsonl"):
            continue
        try:
            for line in jf.open():
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                result.total_records += 1
                schema = record.get("schema_version", "unknown")
                result.schema = schema

                # Check envelope fields
                envelope_ok = True
                for f in ENVELOPE_FIELDS:
                    val = record.get(f)
                    if val is None or val == "":
                        envelope_ok = False
                        result.envelope_missing[f] = result.envelope_missing.get(f, 0) + 1
                if envelope_ok:
                    result.envelope_present += 1

                # Check page fields
                if schema in PAGE_SCHEMAS or "page" in record:
                    result.page_applicable += 1
                    if record.get("page") is not None:
                        result.page_present += 1
                    else:
                        result.page_missing += 1

                # Check OCR fields
                if schema in OCR_SCHEMAS:
                    result.ocr_applicable += 1
                    ocr_ok = True
                    for f in OCR_FIELDS:
                        val = record.get(f)
                        if val is None or (isinstance(val, list) and len(val) == 0):
                            ocr_ok = False
                            result.ocr_missing[f] = result.ocr_missing.get(f, 0) + 1
                    if ocr_ok:
                        result.ocr_present += 1
        except Exception as e:
            print(f"  Warning: error reading {jf}: {e}", file=sys.stderr)

    return result if result.total_records > 0 else None


def check_gamebook(run_dir: Path) -> GamebookResult | None:
    """Check provenance completeness in gamebook.json."""
    gb_path = run_dir / "gamebook.json"
    if not gb_path.exists():
        return None

    gb = json.loads(gb_path.read_text())
    result = GamebookResult()

    # Check top-level provenance
    sections = gb.get("sections", [])
    if isinstance(sections, dict):
        sections = list(sections.values())

    for section in sections:
        if not isinstance(section, dict):
            continue
        prov = section.get("provenance")
        # Stub sections (source not found) have provenance.stub=True — they
        # genuinely have no source pages, so exclude from completeness scoring.
        if prov and isinstance(prov, dict) and prov.get("stub"):
            continue
        result.total_sections += 1
        if prov and isinstance(prov, dict):
            result.sections_with_provenance += 1
            complete = True
            for f in GAMEBOOK_SECTION_PROVENANCE:
                val = prov.get(f)
                if val is None or (isinstance(val, list) and len(val) == 0):
                    complete = False
                    result.missing_fields[f] = result.missing_fields.get(f, 0) + 1
            if complete:
                result.provenance_complete += 1
        else:
            # All fields count as missing
            for f in GAMEBOOK_SECTION_PROVENANCE:
                result.missing_fields[f] = result.missing_fields.get(f, 0) + 1

    return result


def main():
    parser = argparse.ArgumentParser(description="Measure provenance completeness")
    parser.add_argument("run_dir", type=Path, help="Path to pipeline run directory")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
    args = parser.parse_args()

    if not args.run_dir.is_dir():
        print(f"Error: {args.run_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Find all stage directories (numbered prefix)
    stage_dirs = sorted(
        d for d in args.run_dir.iterdir()
        if d.is_dir() and d.name[:2].isdigit()
    )

    stage_results = []
    for sd in stage_dirs:
        result = check_jsonl_stage(sd)
        if result:
            stage_results.append(result)

    gamebook_result = check_gamebook(args.run_dir)

    # Compute aggregate score
    all_envelope = sum(r.envelope_present for r in stage_results)
    all_records = sum(r.total_records for r in stage_results)
    all_page_present = sum(r.page_present for r in stage_results)
    all_page_applicable = sum(r.page_applicable for r in stage_results)
    all_ocr_present = sum(r.ocr_present for r in stage_results)
    all_ocr_applicable = sum(r.ocr_applicable for r in stage_results)

    envelope_score = all_envelope / all_records if all_records > 0 else 1.0
    page_score = all_page_present / all_page_applicable if all_page_applicable > 0 else 1.0
    ocr_score = all_ocr_present / all_ocr_applicable if all_ocr_applicable > 0 else 1.0

    # Gamebook score
    gb_score = gamebook_result.overall_score if gamebook_result else None

    # Overall: average of applicable dimensions
    dimensions = [envelope_score, page_score]
    if all_ocr_applicable > 0:
        dimensions.append(ocr_score)
    if gb_score is not None:
        dimensions.append(gb_score)
    overall = sum(dimensions) / len(dimensions)

    if args.json:
        output = {
            "run_dir": str(args.run_dir),
            "overall_provenance_completeness": round(overall, 4),
            "dimensions": {
                "envelope": round(envelope_score, 4),
                "page_tracing": round(page_score, 4),
                "ocr_confidence": round(ocr_score, 4) if all_ocr_applicable > 0 else None,
                "gamebook_provenance": round(gb_score, 4) if gb_score is not None else None,
            },
            "totals": {
                "total_records": all_records,
                "stages_checked": len(stage_results),
                "gamebook_sections": gamebook_result.total_sections if gamebook_result else 0,
            },
            "stages": [
                {
                    "stage": r.stage_dir,
                    "schema": r.schema,
                    "records": r.total_records,
                    "envelope_score": round(r.envelope_score, 4),
                    "page_score": round(r.page_score, 4) if r.page_applicable > 0 else None,
                    "ocr_score": round(r.ocr_score, 4) if r.ocr_applicable > 0 else None,
                    "missing": {
                        **({"envelope": r.envelope_missing} if r.envelope_missing else {}),
                        **({"ocr": r.ocr_missing} if r.ocr_missing else {}),
                    } or None,
                }
                for r in stage_results
            ],
        }
        if gamebook_result:
            output["gamebook"] = {
                "sections": gamebook_result.total_sections,
                "with_provenance": gamebook_result.sections_with_provenance,
                "fully_complete": gamebook_result.provenance_complete,
                "score": round(gb_score, 4),
                "missing_fields": gamebook_result.missing_fields or None,
            }
        print(json.dumps(output, indent=2))
    else:
        # Text report
        print(f"\n{'='*60}")
        print(f"PROVENANCE COMPLETENESS — {args.run_dir.name}")
        print(f"{'='*60}\n")

        print(f"Overall Score: {overall:.1%}")
        print(f"  Envelope (module_id, run_id, created_at, schema): {envelope_score:.1%}")
        print(f"  Page tracing (page number present): {page_score:.1%}")
        if all_ocr_applicable > 0:
            print(f"  OCR confidence (quality, integrity, source): {ocr_score:.1%}")
        if gb_score is not None:
            print(f"  Gamebook section provenance: {gb_score:.1%}")
        print(f"\n  Records checked: {all_records} across {len(stage_results)} stages")
        if gamebook_result:
            print(f"  Gamebook sections: {gamebook_result.total_sections}")

        if args.verbose:
            print(f"\n{'─'*60}")
            print("STAGE DETAILS")
            print(f"{'─'*60}")
            for r in stage_results:
                score_parts = [f"envelope={r.envelope_score:.0%}"]
                if r.page_applicable > 0:
                    score_parts.append(f"page={r.page_score:.0%}")
                if r.ocr_applicable > 0:
                    score_parts.append(f"ocr={r.ocr_score:.0%}")
                scores = ", ".join(score_parts)
                print(f"\n  {r.stage_dir} ({r.total_records} records, {r.schema})")
                print(f"    {scores}")
                if r.envelope_missing:
                    print(f"    Missing envelope: {r.envelope_missing}")
                if r.ocr_missing:
                    print(f"    Missing OCR: {r.ocr_missing}")

            if gamebook_result:
                print(f"\n  gamebook.json ({gamebook_result.total_sections} sections)")
                print(f"    Has provenance: {gamebook_result.sections_with_provenance}/{gamebook_result.total_sections}")
                print(f"    Fully complete: {gamebook_result.provenance_complete}/{gamebook_result.sections_with_provenance}")
                if gamebook_result.missing_fields:
                    print(f"    Missing fields: {gamebook_result.missing_fields}")

        print()


if __name__ == "__main__":
    main()
