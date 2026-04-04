from __future__ import annotations

import importlib.util
from pathlib import Path


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
