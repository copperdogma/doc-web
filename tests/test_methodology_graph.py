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


def test_parse_story_extracts_blocker_sections(tmp_path):
    module = load_module()
    module.ROOT = tmp_path
    story_path = tmp_path / "stories" / "story-001-blocked.md"
    story_path.parent.mkdir()
    story_path.write_text(
        textwrap.dedent(
            """\
            ---
            title: Blocked Story
            status: Blocked
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

            # Story 001 — Blocked Story

            ## Blocker Summary

            Missing upstream workflow seam.

            ## Blocker Evidence

            - Checked the target skill and compiler surface.
            - No blocking hook exists yet.

            ## Unblock Condition

            Land the shared workflow seam first.
            """
        ),
        encoding="utf-8",
    )

    story = module.parse_story(story_path)

    assert story["blocker_summary"] == "Missing upstream workflow seam."
    assert "No blocking hook exists yet." in story["blocker_evidence"]
    assert story["unblock_condition"] == "Land the shared workflow seam first."


def test_validate_graph_requires_blocker_sections_for_blocked_story():
    module = load_module()
    stories = [
        {
            "id": "001",
            "title": "Blocked Story",
            "path": "docs/stories/story-001-blocked.md",
            "status": "Blocked",
            "priority": "High",
            "ideal_refs": [],
            "spec_refs": [],
            "decision_refs": [],
            "adr_ids": [],
            "depends_on": [],
            "category_refs": [],
            "compromise_refs": [],
            "input_coverage_refs": [],
            "architecture_domains": [],
            "roadmap_tags": [],
            "blocker_summary": "",
            "blocker_evidence": "Checked the repo and the blocker is real.",
            "unblock_condition": "",
            "legacy_build_map_refs": "",
            "metadata_source": "frontmatter",
            "missing_frontmatter_keys": [],
        }
    ]

    validation = module.validate_graph(
        state={"categories": {}, "roadmap": {}, "architecture_audits": {"domains": {}, "cadence": {}}},
        spec={"categories": [], "compromises": []},
        stories=stories,
        adrs=[],
        evals=[],
        coverage={"formats": []},
    )

    assert validation["errors"] == [
        "story 001 is Blocked but missing sections: Blocker Summary, Unblock Condition"
    ]


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


def test_parse_eval_registry_uses_explicit_lineage_fields_only(tmp_path):
    module = load_module()
    module.ROOT = tmp_path
    module.EVALS_PATH = tmp_path / "docs" / "evals" / "registry.yaml"
    module.EVALS_PATH.parent.mkdir(parents=True)
    module.EVALS_PATH.write_text(
        textwrap.dedent(
            """\
            evals:
              - id: explicit-lineage
                name: Explicit Lineage
                type: quality
                command: python -m example
                spec_refs:
                  - spec:8
                story_refs:
                  - "123"
                compromise_refs:
                  - B8
                category_refs:
                  - spec:9
                note: "Body mentions Story 999, spec:1, and C1 but those should not be parsed."
            """
        ),
        encoding="utf-8",
    )

    records = module.parse_eval_registry()

    assert len(records) == 1
    assert records[0]["spec_refs"] == ["spec:8"]
    assert records[0]["story_refs"] == ["123"]
    assert records[0]["compromise_refs"] == ["B8"]
    assert records[0]["category_refs"] == ["spec:9"]
    assert records[0]["explicit_lineage"] is True


def test_validate_graph_requires_explicit_eval_lineage():
    module = load_module()

    validation = module.validate_graph(
        state={"categories": {}, "roadmap": {}, "architecture_audits": {"domains": {}, "cadence": {}}},
        spec={
            "categories": [{"id": "spec:8", "sections": []}],
            "compromises": [{"id": "B8", "category_id": "spec:8"}],
        },
        stories=[],
        adrs=[],
        evals=[
            {
                "id": "missing-lineage",
                "spec_refs": [],
                "story_refs": [],
                "compromise_refs": [],
                "category_refs": [],
                "explicit_lineage": False,
            }
        ],
        coverage={"formats": []},
    )

    assert validation["errors"] == ["eval missing-lineage missing explicit lineage refs"]


def test_validate_graph_rejects_coverage_score_source_drift():
    module = load_module()

    validation = module.validate_graph(
        state={"categories": {}, "roadmap": {}, "architecture_audits": {"domains": {}, "cadence": {}}},
        spec={
            "categories": [{"id": "spec:4", "sections": []}],
            "compromises": [{"id": "C4", "category_id": "spec:4"}],
        },
        stories=[],
        adrs=[],
        evals=[
            {
                "id": "image-crop-extraction",
                "spec_refs": ["spec:4"],
                "story_refs": [],
                "compromise_refs": ["C4"],
                "category_refs": ["spec:4"],
                "explicit_lineage": True,
                "scores": [
                    {
                        "metrics": {"overall": 0.9703, "pass_rate": 1.0},
                        "measured": "2026-04-10",
                    }
                ],
            }
        ],
        coverage={
            "formats": [
                {
                    "id": "image-directory-scans",
                    "scores": {
                        "illustration_extraction": 0.9,
                        "measured": "2026-03-11",
                    },
                    "score_sources": {
                        "illustration_extraction": {
                            "eval_id": "image-crop-extraction",
                            "metric": "overall",
                        }
                    },
                }
            ]
        },
    )

    assert validation["errors"] == [
        "coverage row image-directory-scans score illustration_extraction=0.9000 drifts from eval image-crop-extraction.overall=0.9703",
        "coverage row image-directory-scans measured date 2026-03-11 drifts from eval image-crop-extraction measured date 2026-04-10",
    ]


def test_validate_graph_rejects_active_campaign_with_only_terminal_story_refs():
    module = load_module()
    stories = [
        {
            "id": "001",
            "title": "Finished Story",
            "path": "docs/stories/story-001-finished.md",
            "status": "Done",
            "priority": "High",
            "ideal_refs": [],
            "spec_refs": [],
            "decision_refs": [],
            "adr_ids": [],
            "depends_on": [],
            "category_refs": [],
            "compromise_refs": [],
            "input_coverage_refs": [],
            "architecture_domains": [],
            "roadmap_tags": [],
            "blocker_summary": "",
            "blocker_evidence": "",
            "unblock_condition": "",
            "legacy_build_map_refs": "",
            "metadata_source": "frontmatter",
            "missing_frontmatter_keys": [],
        },
        {
            "id": "002",
            "title": "Superseded Story",
            "path": "docs/stories/story-002-superseded.md",
            "status": "Obsolete",
            "priority": "High",
            "ideal_refs": [],
            "spec_refs": [],
            "decision_refs": [],
            "adr_ids": [],
            "depends_on": [],
            "category_refs": [],
            "compromise_refs": [],
            "input_coverage_refs": [],
            "architecture_domains": [],
            "roadmap_tags": [],
            "blocker_summary": "",
            "blocker_evidence": "",
            "unblock_condition": "",
            "legacy_build_map_refs": "",
            "metadata_source": "frontmatter",
            "missing_frontmatter_keys": [],
        },
    ]

    validation = module.validate_graph(
        state={
            "categories": {},
            "roadmap": {
                "campaigns": [{"id": "stale-campaign", "status": "active", "story_refs": ["001", "002"]}]
            },
            "architecture_audits": {"domains": {}, "cadence": {}},
        },
        spec={"categories": [], "compromises": []},
        stories=stories,
        adrs=[],
        evals=[],
        coverage={"formats": []},
    )

    assert validation["errors"] == [
        "state.roadmap.campaign stale-campaign is active but only references terminal stories: 001, 002"
    ]


def test_validate_graph_flags_live_build_map_language_in_active_surface(tmp_path):
    module = load_module()
    module.ROOT = tmp_path
    active_path = tmp_path / "docs" / "example.md"
    active_path.parent.mkdir(parents=True)
    active_path.write_text("Use the build map as the current planning surface.\n", encoding="utf-8")
    module.ACTIVE_SURFACE_PATHS = [active_path]

    validation = module.validate_graph(
        state={"categories": {}, "roadmap": {}, "architecture_audits": {"domains": {}, "cadence": {}}},
        spec={"categories": [], "compromises": []},
        stories=[],
        adrs=[],
        evals=[],
        coverage={"formats": []},
    )

    assert validation["errors"] == ["docs/example.md:1 still treats build-map language as live"]


def test_validate_graph_flags_unqualified_generated_view_language_in_active_surface(tmp_path):
    module = load_module()
    module.ROOT = tmp_path
    active_path = tmp_path / "docs" / "example.md"
    active_path.parent.mkdir(parents=True)
    active_path.write_text("Read docs/stories.md to decide what is in flight.\n", encoding="utf-8")
    module.ACTIVE_SURFACE_PATHS = [active_path]

    validation = module.validate_graph(
        state={"categories": {}, "roadmap": {}, "architecture_audits": {"domains": {}, "cadence": {}}},
        spec={"categories": [], "compromises": []},
        stories=[],
        adrs=[],
        evals=[],
        coverage={"formats": []},
    )

    assert validation["errors"] == [
        "docs/example.md:1 references docs/stories.md without generated-view framing"
    ]


def test_active_surface_paths_cover_methodology_hardening_surfaces():
    module = load_module()
    root = Path(__file__).resolve().parents[1]
    rel_paths = {path.relative_to(root).as_posix() for path in module.ACTIVE_SURFACE_PATHS}

    assert "docs/ideal.md" in rel_paths
    assert "docs/spec.md" in rel_paths
    assert "docs/evals/README.md" in rel_paths
    assert "docs/methodology-artifact-audit-and-migration.md" in rel_paths
    assert ".agents/skills/setup-methodology/references/modes.md" in rel_paths
    assert ".gemini/commands/create-story.toml" in rel_paths
