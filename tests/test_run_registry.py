import os
from types import SimpleNamespace
from pathlib import Path

from modules.common.run_registry import (
    analyze_page_html_artifact,
    build_run_health_entry,
    check_run_reuse,
    record_run_assessment,
    record_run_manifest,
    resolve_output_root,
)
from modules.common.utils import save_json, save_jsonl
import tools.run_registry as run_registry_tool


def test_resolve_output_root_prefers_real_shared_output_for_symlinked_runs(tmp_path: Path) -> None:
    shared_output = tmp_path / "shared" / "output"
    run_dir = shared_output / "runs" / "story137-onward-verify"
    run_dir.mkdir(parents=True, exist_ok=True)

    worktree_root = tmp_path / "worktree" / "repo"
    worktree_root.mkdir(parents=True, exist_ok=True)
    os.symlink(shared_output, worktree_root / "output")

    linked_run_dir = worktree_root / "output" / "runs" / "story137-onward-verify"
    assert resolve_output_root(str(linked_run_dir)) == str(shared_output.resolve())


def test_record_run_manifest_uses_run_output_root_when_run_is_under_output_runs(tmp_path: Path) -> None:
    shared_output = tmp_path / "shared" / "output"
    run_dir = shared_output / "runs" / "registry-smoke"
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest_path, entry = record_run_manifest(
        run_id="registry-smoke",
        run_dir=str(run_dir),
        recipe={
            "name": "registry-smoke-recipe",
            "input": {"pdf": "/tmp/books/onward.pdf"},
        },
        snapshots={"recipe": str(run_dir / "snapshots" / "recipe.yaml")},
    )

    assert manifest_path == str(shared_output / "run_manifest.jsonl")
    assert entry is not None
    assert entry["path"] == "runs/registry-smoke"
    assert entry["snapshots"]["recipe"] == "runs/registry-smoke/snapshots/recipe.yaml"


def test_resolve_output_root_prefers_git_common_dir_output_when_run_dir_unknown(
    tmp_path: Path, monkeypatch
) -> None:
    shared_repo = tmp_path / "shared" / "repo"
    shared_output = shared_repo / "output"
    shared_output.mkdir(parents=True, exist_ok=True)

    worktree_root = tmp_path / "worktree" / "repo"
    worktree_root.mkdir(parents=True, exist_ok=True)
    (worktree_root / "output").mkdir(parents=True, exist_ok=True)

    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout=str(shared_repo / ".git") + "\n")

    monkeypatch.setattr("modules.common.run_registry.subprocess.run", fake_run)

    assert resolve_output_root(cwd=str(worktree_root)) == str(shared_output.resolve())


def test_cli_resolution_prefers_shared_output_root_for_relative_output_arg(
    tmp_path: Path, monkeypatch
) -> None:
    shared_output = tmp_path / "shared" / "output"
    run_dir = shared_output / "runs" / "story139-safe"
    run_dir.mkdir(parents=True, exist_ok=True)
    save_jsonl(str(shared_output / "run_manifest.jsonl"), [{"run_id": "story139-safe", "path": "runs/story139-safe"}])

    worktree_root = tmp_path / "worktree" / "repo"
    worktree_root.mkdir(parents=True, exist_ok=True)
    (worktree_root / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(worktree_root)
    monkeypatch.setattr(run_registry_tool, "resolve_output_root", lambda run_dir=None, cwd=None: str(shared_output))

    args = SimpleNamespace(run_id="story139-safe", run_dir=None, output_root="output")
    resolved_run_dir = run_registry_tool._resolve_run_dir(args)
    resolved_output_root = run_registry_tool._resolve_output_root_arg(args, resolved_run_dir)

    assert resolved_run_dir == str(run_dir.resolve())
    assert resolved_output_root == str(shared_output.resolve())


def test_analyze_page_html_artifact_flags_empty_printed_pages_and_gaps(tmp_path: Path) -> None:
    pages_path = tmp_path / "pages_html.jsonl"
    save_jsonl(
        str(pages_path),
        [
            {"page_number": 14, "printed_page_number": 5, "html": "<p>Page 5</p>"},
            {"page_number": 15, "printed_page_number": 6, "html": ""},
            {"page_number": 16, "printed_page_number": 7, "html": "<p>Page 7</p>"},
            {"page_number": 17, "printed_page_number": 8, "html": "   "},
            {"page_number": 18, "printed_page_number": 9, "html": "<p>Page 9</p>"},
        ],
    )

    summary = analyze_page_html_artifact(str(pages_path))

    assert summary["page_count"] == 5
    assert summary["empty_html_pages"] == 2
    assert summary["empty_html_page_numbers"] == [15, 17]
    assert summary["empty_html_printed_pages"] == [6, 8]
    assert summary["empty_html_with_printed_number_pages"] == [15, 17]
    assert summary["empty_html_between_nonempty_pages"] == [15, 17]
    assert summary["fatal_signals"] == [
        "empty_html_with_printed_number_pages",
        "empty_html_between_nonempty_pages",
    ]


def test_build_run_health_entry_summarizes_page_health_and_chapter_counts(tmp_path: Path) -> None:
    output_root = tmp_path / "shared" / "output"
    run_dir = output_root / "runs" / "health-smoke"
    stage_dir = run_dir / "07_table_fix_continuations_v1"
    build_dir = run_dir / "09_build_chapter_html_v1"
    stage_dir.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    pages_path = stage_dir / "pages_html.jsonl"
    save_jsonl(
        str(pages_path),
        [
            {"page_number": 1, "printed_page_number": 1, "html": "<p>One</p>"},
            {"page_number": 2, "printed_page_number": 2, "html": "<p>Two</p>"},
        ],
    )

    chapters_path = build_dir / "chapters_manifest.jsonl"
    save_jsonl(
        str(chapters_path),
        [
            {"kind": "chapter", "file": "chapter-001.html", "title": "Alpha"},
            {"kind": "page", "file": "page-001.html", "title": "Alpha page"},
            {"kind": "chapter", "file": "chapter-002.html", "title": "Beta"},
        ],
    )

    save_json(
        str(run_dir / "pipeline_state.json"),
        {
            "status": "done",
            "stages": {
                "table_fix_continuations": {
                    "status": "done",
                    "artifact": "output/runs/health-smoke/07_table_fix_continuations_v1/pages_html.jsonl",
                    "schema_version": "page_html_v1",
                },
                "build_chapter_html": {
                    "status": "done",
                    "artifact": "output/runs/health-smoke/09_build_chapter_html_v1/chapters_manifest.jsonl",
                    "schema_version": "chapter_manifest_v1",
                },
            },
        },
    )

    record_run_manifest(
        run_id="health-smoke",
        run_dir=str(run_dir),
        recipe={"name": "onward-health", "input": {"pdf": "/tmp/books/onward.pdf"}},
    )

    entry = build_run_health_entry(
        "health-smoke",
        str(run_dir),
        state_path=str(run_dir / "pipeline_state.json"),
    )

    assert entry["document"] == "onward"
    assert entry["recipe"] == "onward-health"
    assert entry["page_html_stage_id"] == "table_fix_continuations"
    assert entry["page_html_artifact"] == "runs/health-smoke/07_table_fix_continuations_v1/pages_html.jsonl"
    assert entry["page_count"] == 2
    assert entry["empty_html_pages"] == 0
    assert entry["chapter_manifest_artifact"] == "runs/health-smoke/09_build_chapter_html_v1/chapters_manifest.jsonl"
    assert entry["chapter_count"] == 2
    assert entry["page_file_count"] == 1


def test_check_run_reuse_marks_fatal_page_loss_unsafe_even_with_known_good_assessment(tmp_path: Path) -> None:
    output_root = tmp_path / "shared" / "output"
    run_dir = output_root / "runs" / "unsafe-onward"
    stage_dir = run_dir / "05_extract_page_numbers_html_v1"
    stage_dir.mkdir(parents=True, exist_ok=True)

    pages_path = stage_dir / "pages_html.jsonl"
    save_jsonl(
        str(pages_path),
        [
            {"page_number": 14, "printed_page_number": 5, "html": "<p>Page 5</p>"},
            {"page_number": 15, "printed_page_number": 6, "html": ""},
            {"page_number": 16, "printed_page_number": 7, "html": "<p>Page 7</p>"},
        ],
    )
    save_json(
        str(run_dir / "pipeline_state.json"),
        {
            "status": "done",
            "stages": {
                "extract_page_numbers_html": {
                    "status": "done",
                    "artifact": "output/runs/unsafe-onward/05_extract_page_numbers_html_v1/pages_html.jsonl",
                    "schema_version": "page_html_v1",
                }
            },
        },
    )

    record_run_manifest(
        run_id="unsafe-onward",
        run_dir=str(run_dir),
        recipe={"name": "unsafe-onward", "input": {"pdf": "/tmp/books/onward.pdf"}},
    )
    record_run_assessment(
        run_id="unsafe-onward",
        run_dir=str(run_dir),
        scope="page_presence",
        status="known_good",
        summary="Older manual note before the upstream page-loss regression was noticed.",
    )

    result = check_run_reuse(
        run_id="unsafe-onward",
        run_dir=str(run_dir),
        scope="page_presence",
    )

    assert result["recommendation"] == "unsafe"
    assert result["assessment"]["status"] == "known_good"
    assert result["health"]["fatal_signals"] == [
        "empty_html_with_printed_number_pages",
        "empty_html_between_nonempty_pages",
    ]
    assert any("health flags:" in reason for reason in result["reasons"])


def test_check_run_reuse_marks_clean_scoped_assessment_safe(tmp_path: Path) -> None:
    output_root = tmp_path / "shared" / "output"
    run_dir = output_root / "runs" / "safe-onward"
    stage_dir = run_dir / "07_table_fix_continuations_v1"
    stage_dir.mkdir(parents=True, exist_ok=True)

    pages_path = stage_dir / "pages_html.jsonl"
    save_jsonl(
        str(pages_path),
        [
            {"page_number": 1, "printed_page_number": 1, "html": "<p>Page 1</p>"},
            {"page_number": 2, "printed_page_number": 2, "html": "<p>Page 2</p>"},
        ],
    )
    save_json(
        str(run_dir / "pipeline_state.json"),
        {
            "status": "done",
            "stages": {
                "table_fix_continuations": {
                    "status": "done",
                    "artifact": "output/runs/safe-onward/07_table_fix_continuations_v1/pages_html.jsonl",
                    "schema_version": "page_html_v1",
                }
            },
        },
    )

    record_run_manifest(
        run_id="safe-onward",
        run_dir=str(run_dir),
        recipe={"name": "safe-onward", "input": {"pdf": "/tmp/books/onward.pdf"}},
    )
    record_run_assessment(
        run_id="safe-onward",
        run_dir=str(run_dir),
        scope="page_presence",
        status="known_good",
        summary="Verified there are no missing printed pages in the source page HTML.",
    )

    result = check_run_reuse(
        run_id="safe-onward",
        run_dir=str(run_dir),
        scope="page_presence",
    )

    assert result["recommendation"] == "safe"
    assert result["health"]["fatal_signals"] == []
    assert any("known_good" in reason for reason in result["reasons"])
