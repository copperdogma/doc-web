from __future__ import annotations

import importlib.util
from pathlib import Path
import textwrap


def load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "methodology_graph.py"
    spec = importlib.util.spec_from_file_location("methodology_graph", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_build_graph_has_no_validation_errors():
    module = load_module()
    graph = module.build_graph()
    assert graph["validation"]["errors"] == []
    assert graph["validation"]["warnings"] == []
    assert graph["spec"]["categories"]
    assert graph["coverage"]["path"] == "tests/fixtures/formats/_coverage-matrix.json"
    assert any(story["id"] == "187" for story in graph["stories"])


def test_render_stories_index_is_generated_view():
    module = load_module()
    graph = module.build_graph()
    rendered = module.render_stories_index(graph)
    assert rendered.startswith("# Stories")
    assert "Do not edit manually." in rendered
    assert "story-187" in rendered


def test_parse_stories_ignores_companion_docs(tmp_path):
    module = load_module()
    module.ROOT = tmp_path
    module.STORIES_DIR = tmp_path / "stories"
    module.STORIES_DIR.mkdir()
    (module.STORIES_DIR / "story-001-alpha.md").write_text(
        textwrap.dedent(
            """\
            ---
            title: Alpha
            status: Done
            priority: High
            ideal_refs: []
            spec_refs: []
            adr_refs: []
            depends_on: []
            category_refs: []
            compromise_refs: []
            input_coverage_refs: []
            architecture_domains: []
            roadmap_tags: []
            ---

            # Story 001 — Alpha
            """
        ),
        encoding="utf-8",
    )
    (module.STORIES_DIR / "story-001-alpha.research.md").write_text("# Companion\n", encoding="utf-8")
    (module.STORIES_DIR / "story-001-SUMMARY.md").write_text("# Summary\n", encoding="utf-8")

    stories = module.parse_stories()

    assert [story["id"] for story in stories] == ["001"]
    assert stories[0]["path"] == "stories/story-001-alpha.md"


def test_parse_story_frontmatter_wins_over_legacy_headers(tmp_path):
    module = load_module()
    module.ROOT = tmp_path
    story_path = tmp_path / "stories" / "story-001-frontmatter-wins.md"
    story_path.parent.mkdir()
    story_path.write_text(
        textwrap.dedent(
            """\
            ---
            title: Frontmatter Wins
            status: Done
            priority: High
            ideal_refs:
              - Execution Ideal
            spec_refs:
              - spec:9
            adr_refs: []
            depends_on:
              - "123"
            category_refs: []
            compromise_refs: []
            input_coverage_refs: []
            architecture_domains: []
            roadmap_tags: []
            ---

            # Story 001 — Frontmatter Wins

            **Status**: Open
            **Ideal Refs**: Legacy Ideal
            **Spec Refs**: spec:1.1
            **Decision Refs**: ADR-999, docs/example.md
            **Depends On**: Story 555
            """
        ),
        encoding="utf-8",
    )

    story = module.parse_story(story_path)

    assert story["title"] == "Frontmatter Wins"
    assert story["status"] == "Done"
    assert story["spec_refs"] == ["spec:9"]
    assert story["depends_on"] == ["123"]
    assert story["adr_ids"] == []


def test_parse_adr_frontmatter_wins_over_body_inference(tmp_path):
    module = load_module()
    module.ROOT = tmp_path
    adr_path = tmp_path / "docs" / "decisions" / "adr-001-test" / "adr.md"
    adr_path.parent.mkdir(parents=True)
    adr_path.write_text(
        textwrap.dedent(
            """\
            ---
            title: Test ADR
            status: accepted
            ideal_refs: []
            spec_refs:
              - spec:8
            story_refs:
              - "123"
            compromise_refs: []
            related_adrs: []
            ---

            # ADR-001: Test ADR

            This body mentions spec:9, Story 555, and ADR-999 but frontmatter should win.
            """
        ),
        encoding="utf-8",
    )

    adr = module.parse_adr(adr_path)

    assert adr["spec_refs"] == ["spec:8"]
    assert adr["story_refs"] == ["123"]
    assert adr["related_adrs"] == []
