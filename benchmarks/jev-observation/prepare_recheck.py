"""Freeze revised planner inputs from unchanged original anonymous HTML and gold."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from modules.validate.plan_onward_document_consistency_v1 import main as p  # noqa: E402

BASE = ROOT / "docs/evals/artifacts/story234-anonymized-observation"
OUT = ROOT / "docs/evals/artifacts/story234-evidence-contract-recheck"


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    chapters = [
        json.loads(s) for s in (BASE / "chapters.jsonl").read_text().splitlines()
    ]
    pages = {
        r["page_number"]: r
        for r in map(json.loads, (BASE / "pages.jsonl").read_text().splitlines())
    }
    dossier = p.build_document_dossier(
        chapters,
        pages,
        chapters_path=str(BASE / "chapters.jsonl"),
        pages_path=str(BASE / "pages.jsonl"),
        flag_threshold=25,
    )
    payload = {
        "model": "gpt-4.1",
        "messages": [
            {"role": "system", "content": p.SYSTEM_PROMPT},
            {"role": "user", "content": p._build_prompt(dossier)},
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 6000,
        "temperature": 0.0,
    }
    for name, obj in [("dossier.json", dossier), ("planner.request.json", payload)]:
        (OUT / name).write_text(json.dumps(obj, indent=2) + "\n")
    cost = (
        (len(json.dumps(payload, ensure_ascii=False).encode()) + 2048) * 2 / 1e6
        + 6000 * 8 / 1e6
        + 6 * 0.002688
    )
    assert cost <= 0.15
    (OUT / "plan.md").write_text(
        f"""# Story234 evidence-contract recheck\n\nUnchanged original six HTML files and gold: ../story234-anonymized-observation/.\nRevised prompt/code/compact input identified by freeze.json. Same actual full\nplanner contract and native runtime shadow (one + at most6calls), no retries,\nmaximum$0.15; conservative reservation${cost:.8f}.\n\nReport original five conditional cases directly before/after. Historical case6\neligibility stays unchanged; evaluate its now-visible ambiguous note separately\n(expected uncertain), plus descriptive six-case pipeline status. Preserve raw\nplanner versus normalized pipeline status and dependent JEV outputs/routes. Gold\nis never passed to providers. Compare direct coverage and false-clean counts;\nno thresholds or gold tuning. Two three-chapter shadow batches retain actual\n2second caller deadline and conflict/layout guards; skip conflicting conventions\ninstead of creating extra calls. Full planner PLUS shadow cost is added overhead.\n\nOriginal sample is one48-row real DOM with all text fictional, five injected\nmutations. Not representative production traffic. Prior evidence remains frozen;\nsource-code hashes at prior commits identify historical runtime. No private data.\n"""
    )
    paths = (
        list(OUT.glob("*"))
        + list(BASE.glob("chapter-*.html"))
        + [BASE / "gold.json", BASE / "chapters.jsonl", BASE / "pages.jsonl"]
    )
    paths += [
        ROOT / x
        for x in [
            "benchmarks/jev-observation/recheck.py",
            "benchmarks/jev-observation/prepare_recheck.py",
            "modules/validate/plan_onward_document_consistency_v1/main.py",
            "modules/validate/plan_onward_document_consistency_v1/jev_shadow.py",
            "modules/validate/validate_onward_genealogy_consistency_v1/main.py",
            "tests/test_consistency_evidence_contract.py",
            "scripts/verify_consistency_evidence_contract.py",
            "tests/fixtures/jev_shadow/mock_provider/openai.py",
        ]
    ]
    manifest = {
        str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest()
        for f in paths
    }
    (OUT / "freeze.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(
            {
                "max_reserved_usd": cost,
                "freeze_sha256": hashlib.sha256(
                    (OUT / "freeze.json").read_bytes()
                ).hexdigest(),
            }
        )
    )


if __name__ == "__main__":
    main()
