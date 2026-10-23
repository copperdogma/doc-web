import importlib.util
import json
import sys

import httpx
import pytest
import yaml


SECRET = "synthetic-discovery-secret-not-a-real-key"


@pytest.fixture
def discovery(monkeypatch):
    spec = importlib.util.spec_from_file_location("discovery_under_test", "scripts/discover-models.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "build_doc_web_env", lambda: {})
    return module


def _response(url, body, status=200):
    return httpx.Response(status, request=httpx.Request("GET", url), json=body)


def _configure(discovery, monkeypatch, provider):
    monkeypatch.setattr(discovery, "build_doc_web_env", lambda: {
        discovery.PROVIDERS[provider]["env_key"]: SECRET,
    })


def _model(provider, name):
    if provider == "google":
        return {"name": "models/" + name, "supportedGenerationMethods": ["generateContent"]}
    return {"id": name, "created_at": "2026-10-01T00:00:00Z"}


def test_google_authentication_never_puts_key_in_url(discovery, monkeypatch):
    calls = []

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return _response(url, {"models": []})

    monkeypatch.setattr(discovery.httpx, "get", get)
    assert discovery.query_google(SECRET) == []
    assert SECRET not in calls[0][0]
    assert SECRET not in json.dumps(calls[0][1].get("params"))
    assert calls[0][1]["headers"]["x-goog-api-key"] == SECRET


@pytest.mark.parametrize("provider", ["google", "anthropic", "openai"])
@pytest.mark.parametrize("failure", ["http", "transport", "parse", "unexpected"])
def test_failed_discovery_never_exposes_key_or_invents_models(discovery, monkeypatch, capsys, provider, failure):
    _configure(discovery, monkeypatch, provider)

    def get(url, **kwargs):
        unsafe_url = "https://example.invalid/models?key=" + SECRET
        if failure == "http":
            return _response(unsafe_url, {"error": SECRET}, 403)
        if failure == "transport":
            raise httpx.ConnectError(SECRET, request=httpx.Request("GET", unsafe_url))
        if failure == "parse":
            raise ValueError(SECRET)
        raise RuntimeError(SECRET)

    monkeypatch.setattr(discovery.httpx, "get", get)
    results = discovery.discover_models()
    assert isinstance(results[provider], str)
    reports = [discovery.format_text_report(results), discovery.format_yaml_report(results),
               discovery.format_summary_report(results)]
    captured = capsys.readouterr()
    assert SECRET not in json.dumps(results) + "".join(reports) + captured.out + captured.err
    entry = yaml.safe_load(reports[1])["providers"][provider]
    assert entry["status"] == "error" and entry["models"] == []
    assert provider in reports[2].lower()
    assert "error" in reports[2].lower()


@pytest.mark.parametrize("provider", ["google", "anthropic"])
def test_catalog_traverses_all_pages(discovery, monkeypatch, provider):
    calls = []
    names = ["gemini-3-pro", "gemini-3-flash"] if provider == "google" else ["claude-opus-5", "claude-sonnet-5"]

    def get(url, **kwargs):
        calls.append(kwargs)
        index = len(calls) - 1
        if provider == "google":
            body = {"models": [_model(provider, names[index])]}
            if index == 0:
                body["nextPageToken"] = "next-page"
        else:
            body = {"data": [_model(provider, names[index])], "has_more": index == 0,
                    "last_id": names[index]}
        return _response(url, body)

    monkeypatch.setattr(discovery.httpx, "get", get)
    result = discovery.QUERY_FUNCS[provider](SECRET)
    assert {row["id"] for row in result} == set(names)
    assert len(calls) == 2
    field = "pageToken" if provider == "google" else "after_id"
    assert calls[1]["params"][field] == ("next-page" if provider == "google" else names[0])


@pytest.mark.parametrize("provider", ["google", "anthropic"])
@pytest.mark.parametrize("failure", ["cycle", "limit", "invalid-cursor", "later-http", "invalid-shape"])
def test_incomplete_catalog_is_error_not_partial_success(discovery, monkeypatch, provider, failure):
    _configure(discovery, monkeypatch, provider)
    monkeypatch.setattr(discovery, "MAX_MODEL_PAGES", 2, raising=False)
    calls = []

    def get(url, **kwargs):
        calls.append(kwargs)
        if failure == "later-http" and len(calls) > 1:
            return _response(url, {"error": SECRET}, 503)
        base = "gemini-3-pro" if provider == "google" else "claude-opus-5"
        name = base + f"-{len(calls)}"
        cursor = "repeated" if failure == "cycle" else name
        if failure == "invalid-cursor":
            cursor = 123 if provider == "google" else None
        body = ({"models": [_model(provider, name)], "nextPageToken": cursor}
                if provider == "google" else
                {"data": [_model(provider, name)], "has_more": True, "last_id": cursor})
        if failure == "invalid-shape":
            body["models" if provider == "google" else "data"] = {"unexpected": "mapping"}
        return _response(url, body)

    monkeypatch.setattr(discovery.httpx, "get", get)
    results = discovery.discover_models()
    assert isinstance(results[provider], str)
    assert discovery.collect_all_models(results) == []
    assert len(calls) <= 2
    expected = {"cycle": "pagination_cycle", "limit": "pagination_limit",
                "invalid-cursor": "invalid_cursor", "invalid-shape": "invalid_catalog",
                "later-http": "HTTP 503"}[failure]
    assert expected in results[provider]
    assert SECRET not in discovery.format_yaml_report(results)


def test_successful_response_cannot_echo_credentials_into_reports(discovery, monkeypatch):
    _configure(discovery, monkeypatch, "google")
    monkeypatch.setattr(discovery.httpx, "get", lambda url, **kw: _response(url, {
        "models": [_model("google", "gemini-" + SECRET)],
    }))
    results = discovery.discover_models()
    assert isinstance(results["google"], str)
    assert SECRET not in discovery.format_yaml_report(results)


def test_openai_keeps_bare_reasoning_ids_and_filters_other_products(discovery, monkeypatch):
    monkeypatch.setattr(discovery.httpx, "get", lambda url, **kw: _response(url, {
        "data": [{"id": name} for name in ["o3", "o3-mini", "text-embedding-3-small", "gpt-6-sol"]],
    }))
    assert {row["id"] for row in discovery.query_openai(SECRET)} == {"o3", "o3-mini", "gpt-6-sol"}


@pytest.mark.parametrize("body", [
    {"data": [{"id": "gpt-6-sol"}], "has_more": True},
    {"data": [{"id": "gpt-6-sol"}, {"id": "gpt-6-sol"}]},
])
def test_openai_inconsistent_catalog_is_not_certified(discovery, monkeypatch, body):
    _configure(discovery, monkeypatch, "openai")
    monkeypatch.setattr(discovery.httpx, "get", lambda url, **kw: _response(url, body))
    assert isinstance(discovery.discover_models()["openai"], str)


@pytest.mark.parametrize("model,recorded,display", [
    ("gpt-6-astra", "GPT-6 Sol Responses (none)", "GPT-6"),
    ("gpt-5.6-terra", "GPT-5.6 Luna Responses", "GPT-5.6"),
    ("gpt-6.1-sol", "GPT-6", "GPT-6"),
    ("gpt-4.1-2025-04-14", "gpt-4.1", "GPT-4.1"),
    ("gemini-3-pro-preview", "Gemini 3 Pro", "Gemini 3 Pro"),
    ("gemini-3-flash-lite", "Gemini 3 Flash", "Gemini 3 Flash"),
    ("unknown-exact-id", "GPT-6 Sol", "GPT-6 Sol"),
])
def test_distinct_identity_does_not_inherit_registry_reference(discovery, model, recorded, display):
    registry = discovery._extract_canonical_models(recorded)
    assert not discovery._matches_registry(model, display, registry)


@pytest.mark.parametrize("model,recorded", [
    ("gpt-6.1-sol", "GPT-6.1 Sol low fresh public LOC image-entry (Attempt046)"),
    ("gpt-5.6-terra", "GPT-5.6 Terra Responses (none)"),
    ("claude-sonnet-5-5", "claude-sonnet-5-5 fresh matched public LOC"),
    ("claude-opus-4-6", "Claude Opus 4.6"),
    ("gemini-3.1-flash-lite", "Gemini 3.1 Flash Lite (caption-focus prompt)"),
    ("gpt-4.1-2025-04-14", "gpt-4.1-2025-04-14 narrow status projection"),
])
def test_same_identity_with_score_annotations_can_match(discovery, model, recorded):
    assert discovery._matches_registry(model, "", discovery._extract_canonical_models(recorded))


def test_cache_is_yaml_even_with_summary_and_never_claims_qualification(discovery, monkeypatch, tmp_path, capsys):
    cache = tmp_path / "docs/evals/models-available.yaml"
    cache.parent.mkdir(parents=True)
    monkeypatch.setattr(discovery, "__file__", str(tmp_path / "scripts/discover-models.py"))
    monkeypatch.setattr(discovery, "CACHE_PATH", cache, raising=False)
    monkeypatch.setattr(discovery, "discover_models", lambda: {"openai": [{
        "id": "gpt-6-sol", "provider": "openai", "tier": "mid",
    }], "google": "HTTP 403", "anthropic": None})
    monkeypatch.setattr(discovery, "load_registry_models", lambda path: {"gpt-6-sol"})
    monkeypatch.setattr(sys, "argv", ["discover-models.py", "--cache", "--summary"])
    discovery.main()
    report = yaml.safe_load(cache.read_text())
    assert isinstance(report, dict)
    assert report["providers"]["google"]["status"] == "error"
    output = capsys.readouterr().out
    assert "Summary" in output and "covered by existing evals" not in output


def test_empty_success_and_missing_key_remain_distinct(discovery):
    report = yaml.safe_load(discovery.format_yaml_report({"google": [], "openai": None}))
    assert report["providers"]["google"]["status"] == "ok"
    assert report["providers"]["google"]["model_count"] == 0
    assert report["providers"]["openai"]["status"] == "skipped"
    summary = discovery.format_summary_report({"google": [], "openai": None})
    assert "google" in summary.lower() and "skipped" in summary.lower()


def test_registry_without_parser_does_not_promote_attempt_to_score(discovery, monkeypatch, tmp_path, capsys):
    registry = tmp_path / "registry.yaml"
    registry.write_text("evals:\n- scores: []\n  attempts:\n  - requested_model: gpt-6-astra\n")
    monkeypatch.setattr(discovery, "yaml", None)
    references = discovery.load_registry_models(registry)
    assert references is None
    results = {"openai": [{"id": "gpt-6-astra", "tier": "high"}]}
    report = discovery.format_text_report(results, references)
    assert "[SCORE REF]" not in report and "[NO SCORE REF]" not in report
    assert "Registry score references not assessed" in report
    assert "Registry score references unavailable" in capsys.readouterr().err


@pytest.mark.parametrize("content", [None, "evals: [", "evals: wrong", "evals:\n- scores: wrong"])
def test_unavailable_registry_does_not_claim_empty_score_history(discovery, tmp_path, capsys, content):
    registry = tmp_path / "registry.yaml"
    if content is not None:
        registry.write_text(content)
    assert discovery.load_registry_models(registry) is None
    assert "Registry score references unavailable" in capsys.readouterr().err


def test_registry_references_only_recorded_scores(discovery, tmp_path):
    registry = tmp_path / "registry.yaml"
    registry.write_text("evals:\n- scores:\n  - model: GPT-6 Sol\n  attempts:\n  - requested_model: gpt-6-astra\n")
    assert discovery.load_registry_models(registry) == {"gpt-6-sol"}
    registry.write_text("evals: []\n")
    assert discovery.load_registry_models(registry) == set()
