#!/usr/bin/env python3
"""Discover available AI models across providers.

Checks environment for API keys, queries each provider's model endpoint,
and outputs a structured report of available models for eval work.

Usage:
    python scripts/discover-models.py              # Full report to stdout
    python scripts/discover-models.py --yaml       # YAML output (machine-readable)
    python scripts/discover-models.py --cache      # Write to docs/evals/models-available.yaml
    python scripts/discover-models.py --check-new  # Compare against registry, flag untested models
    python scripts/discover-models.py --summary    # Quick-glance tier summary for /improve-eval
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from doc_web.env import build_doc_web_env

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Run: pip install httpx", file=sys.stderr)
    sys.exit(1)

try:
    import yaml
except ImportError:
    yaml = None


# Each entry is (pattern, tier). Patterns are matched in order.
TIER_PATTERNS: list[tuple[str, str]] = [
    (r"^o1\b", "reasoning"),
    (r"^o1-", "reasoning"),
    (r"^o3\b", "reasoning"),
    (r"^o3-", "reasoning"),
    (r"^o4\b", "reasoning"),
    (r"^o4-", "reasoning"),
    (r"[-_]mini\b", "cheap"),
    (r"[-_]nano\b", "cheap"),
    (r"flash-lite", "cheap"),
    (r"flash-8b", "cheap"),
    (r"claude-haiku", "cheap"),
    (r"^gpt-5\.2", "sota"),
    (r"^gpt-5-2", "sota"),
    (r"^gpt-5\b", "sota"),
    (r"^gpt-5-", "sota"),
    (r"^gpt-4\.1\b", "mid"),
    (r"^gpt-4\.1-", "mid"),
    (r"^gpt-4-1\b", "mid"),
    (r"^gpt-4-1-", "mid"),
    (r"^gpt-4o", "legacy"),
    (r"^gpt-4\b", "legacy"),
    (r"^gpt-4-", "legacy"),
    (r"^chatgpt-4o", "legacy"),
    (r"claude-opus", "sota"),
    (r"claude-sonnet", "mid"),
    (r"claude-3\b", "legacy"),
    (r"claude-3-", "legacy"),
    (r"claude-2", "legacy"),
    (r"gemini-3-pro", "sota"),
    (r"gemini-3\.1-pro", "sota"),
    (r"gemini-2\.5-pro", "sota"),
    (r"gemini-2-5-pro", "sota"),
    (r"gemini-3-flash\b", "mid"),
    (r"gemini-3\.1-flash\b", "mid"),
    (r"gemini-2\.5-flash\b", "mid"),
    (r"gemini-2-5-flash\b", "mid"),
    (r"gemini-flash", "mid"),
    (r"gemini-2\.0", "legacy"),
    (r"gemini-2-0", "legacy"),
    (r"gemini-1\.", "legacy"),
    (r"gemini-1-", "legacy"),
]

TIER_LABELS = {
    "sota": "SOTA      (flagship/frontier)",
    "mid": "MID       (strong mid-tier)",
    "cheap": "CHEAP     (budget/fast)",
    "reasoning": "REASONING (chain-of-thought)",
    "legacy": "LEGACY    (older generation)",
}

TIER_ORDER = ["sota", "mid", "cheap", "reasoning", "legacy"]


def classify_tier(model_id: str) -> str:
    """Return the tier for a model ID."""
    lower = model_id.lower()
    for pattern, tier in TIER_PATTERNS:
        if re.search(pattern, lower):
            return tier
    return "mid"


PROVIDERS = {
    "openai": {
        "env_key": "DOC_WEB_OPENAI_API_KEY",
        "display": "OpenAI",
        "setup_url": "https://platform.openai.com/api-keys",
        "setup_hint": "set DOC_WEB_OPENAI_API_KEY in .env",
    },
    "anthropic": {
        "env_key": "DOC_WEB_ANTHROPIC_API_KEY",
        "display": "Anthropic",
        "setup_url": "https://console.anthropic.com/settings/keys",
        "setup_hint": "set DOC_WEB_ANTHROPIC_API_KEY in .env",
    },
    "google": {
        "env_key": "DOC_WEB_GEMINI_API_KEY",
        "display": "Google (Gemini)",
        "setup_url": "https://aistudio.google.com/app/apikey",
        "setup_hint": "set DOC_WEB_GEMINI_API_KEY in .env",
    },
}

OPENAI_CHAT_PATTERNS = [
    r"^gpt-",
    r"^o[134](?:-|$)",
    r"^chatgpt-",
]

OPENAI_SKIP_PATTERNS = [
    r"-instruct",
    r"^gpt-3\.5",
    r"^gpt-4-\d{4}",
    r"-realtime",
    r"-audio",
    r"-transcribe",
    r"-tts",
    r"-search-",
    r"-image",
    r"-codex",
    r"^chatgpt-image",
    r"-deep-research",
]

GOOGLE_SKIP_PATTERNS = [
    r"^gemma-",
    r"-tts",
    r"-image",
    r"-robotics-",
    r"^deep-research-",
    r"-customtools",
    r"^nano-banana",
    r"^gemini-2\.0-",
    r"^gemini-1\.",
]


def query_openai(api_key: str) -> list[dict]:
    """Query OpenAI /v1/models for chat-capable models."""
    resp = httpx.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    records = _catalog_rows(data, "data", "id")
    if data.get("has_more") or data.get("next_page") or data.get("nextPageToken"):
        raise CatalogError("inconsistent_catalog")
    if len({row["id"] for row in records}) != len(records):
        raise CatalogError("inconsistent_catalog")

    models = []
    for model in records:
        model_id = model["id"]
        if not any(re.match(pattern, model_id) for pattern in OPENAI_CHAT_PATTERNS):
            continue
        if any(re.search(pattern, model_id) for pattern in OPENAI_SKIP_PATTERNS):
            continue
        models.append(
            {
                "id": model_id,
                "provider": "openai",
                "created": datetime.fromtimestamp(
                    model.get("created", 0), tz=timezone.utc
                ).strftime("%Y-%m-%d"),
                "tier": classify_tier(model_id),
            }
        )

    models.sort(key=lambda item: item["created"], reverse=True)
    return models


MAX_MODEL_PAGES = 20
CACHE_PATH = Path(__file__).resolve().parents[1] / "docs/evals/models-available.yaml"


class CatalogError(ValueError):
    """A catalog cannot be certified complete; details never contain provider data."""


def _catalog_rows(data: dict, field: str, id_field: str) -> list[dict]:
    if not isinstance(data, dict) or "error" in data:
        raise CatalogError("invalid_catalog")
    rows = data.get(field, [] if field == "models" else None)
    if not isinstance(rows, list) or any(
        not isinstance(row, dict) or not isinstance(row.get(id_field), str)
        or not row[id_field].strip() for row in rows
    ):
        raise CatalogError("invalid_catalog")
    return rows


def _paged_catalog(provider: str, api_key: str) -> list[dict]:
    google = provider == "google"
    url = ("https://generativelanguage.googleapis.com/v1beta/models" if google
           else "https://api.anthropic.com/v1/models")
    headers = ({"x-goog-api-key": api_key} if google else
               {"x-api-key": api_key, "anthropic-version": "2023-06-01"})
    params = {"pageSize": 1000} if google else {"limit": 1000}
    cursors: set[str] = set()
    identifiers: set[str] = set()
    all_rows = []
    for _ in range(MAX_MODEL_PAGES):
        response = httpx.get(url, headers=headers, params=dict(params), timeout=15)
        response.raise_for_status()
        data = response.json()
        rows = _catalog_rows(data, "models" if google else "data", "name" if google else "id")
        for row in rows:
            identifier = row["name" if google else "id"]
            if identifier in identifiers:
                raise CatalogError("inconsistent_catalog")
            identifiers.add(identifier)
        all_rows.extend(rows)
        if google:
            cursor = data.get("nextPageToken")
            if cursor is None or cursor == "":
                return all_rows
        else:
            if type(data.get("has_more")) is not bool:
                raise CatalogError("invalid_catalog")
            if not data["has_more"]:
                return all_rows
            cursor = data.get("last_id")
        if not isinstance(cursor, str) or not cursor.strip():
            raise CatalogError("invalid_cursor")
        if cursor in cursors:
            raise CatalogError("pagination_cycle")
        cursors.add(cursor)
        params["pageToken" if google else "after_id"] = cursor
    raise CatalogError("pagination_limit")


def query_anthropic(api_key: str) -> list[dict]:
    """Return observed models only after complete bounded cursor traversal."""
    models = []
    for model in _paged_catalog("anthropic", api_key):
        model_id = model["id"]
        created_raw = model.get("created_at")
        if isinstance(created_raw, str):
            created = created_raw[:10]
        elif isinstance(created_raw, (int, float)) and created_raw > 0:
            created = datetime.fromtimestamp(created_raw, tz=timezone.utc).strftime("%Y-%m-%d")
        else:
            created = "unknown"
        models.append({
            "id": model_id, "provider": "anthropic",
            "display_name": model.get("display_name", model_id),
            "created": created, "tier": classify_tier(model_id),
        })
    models.sort(key=lambda item: item.get("created", ""), reverse=True)
    return models


def query_google(api_key: str) -> list[dict]:
    """Return filtered generation catalog entries after complete traversal."""
    models = []
    for model in _paged_catalog("google", api_key):
        model_id = model["name"].removeprefix("models/")
        methods = model.get("supportedGenerationMethods", [])
        if not isinstance(methods, list):
            raise CatalogError("invalid_catalog")
        if "generateContent" not in methods:
            continue
        if "embedding" in model_id or "aqa" in model_id:
            continue
        if any(re.search(pattern, model_id) for pattern in GOOGLE_SKIP_PATTERNS):
            continue
        models.append({
            "id": model_id, "provider": "google",
            "display_name": model.get("displayName", model_id),
            "input_token_limit": model.get("inputTokenLimit"),
            "output_token_limit": model.get("outputTokenLimit"),
            "tier": classify_tier(model_id),
        })
    models.sort(key=lambda item: item["id"])
    return models


QUERY_FUNCS = {
    "openai": query_openai,
    "anthropic": query_anthropic,
    "google": query_google,
}


def _extract_canonical_models(text: str) -> set[str]:
    """Extract score-name references without erasing variants or snapshots.

    Only conventional display spelling is normalized. Arbitrary aliases and
    descriptive suffixes are not evidence that two API identities are equal.
    """
    normalized = re.sub(r"\s+", " ", text.lower().replace("_", "-")).strip()
    normalized = re.sub(
        r"\b(gpt-\d+(?:\.\d+)?)[ ]+(pro|mini|nano|astra|sol|terra|luna|instant)\b",
        lambda match: match[1] + "-" + match[2], normalized,
    )
    normalized = re.sub(
        r"\bclaude[ -]([a-z]+)[ -](\d+(?:[.-]\d+)?)",
        lambda match: "claude-" + match[1] + "-" + match[2].replace(".", "-"), normalized,
    )
    normalized = re.sub(
        r"\bgemini[ -](\d+(?:\.\d+)?)[ -](flash[ -]lite|flash|pro|computer[ -]use)\b",
        lambda match: "gemini-" + match[1] + "-" + match[2].replace(" ", "-"), normalized,
    )
    pattern = (
        r"\b(?:gpt-\d[a-z0-9.]*(?:-[a-z0-9.]+)*|o[134](?:-[a-z0-9.]+)*|"
        r"chatgpt-[a-z0-9]+(?:-[a-z0-9.]+)*|claude-[a-z0-9]+(?:-[a-z0-9.]+)*|"
        r"gemini-[a-z0-9.]+(?:-[a-z0-9.]+)*)\b"
    )
    tokens = set(re.findall(pattern, normalized))
    return tokens or ({normalized} if normalized else set())


def _matches_registry(model_id: str, display_name: str, registry_models: set[str]) -> bool:
    """Match an API ID to score-name references; display names cannot broaden it."""
    return bool(_extract_canonical_models(model_id) & registry_models)


def load_registry_models(registry_path: Path) -> set[str] | None:
    """Extract score references, preserving unavailable versus empty history."""
    if yaml is None:
        print("Registry score references unavailable (PyYAML missing)", file=sys.stderr)
        return None
    try:
        data = yaml.safe_load(registry_path.read_text())
        if not isinstance(data, dict) or not isinstance(data.get("evals"), list):
            raise ValueError
        models = set()
        for eval_entry in data["evals"]:
            if not isinstance(eval_entry, dict):
                raise ValueError
            scores = eval_entry.get("scores", [])
            if not isinstance(scores, list):
                raise ValueError
            for score in scores:
                if not isinstance(score, dict):
                    raise ValueError
                model_name = score.get("model", "")
                if not isinstance(model_name, str):
                    raise ValueError
                if model_name:
                    models |= _extract_canonical_models(model_name)
        return models
    except (OSError, ValueError, yaml.YAMLError):
        print("Registry score references unavailable (unreadable or invalid registry)", file=sys.stderr)
        return None


def group_by_tier(all_models: list[dict]) -> dict[str, list[dict]]:
    """Group a flat list of model dicts by tier."""
    groups: dict[str, list[dict]] = {tier: [] for tier in TIER_ORDER}
    for model in all_models:
        tier = model.get("tier", "mid")
        if tier not in groups:
            tier = "mid"
        groups[tier].append(model)
    return groups


def collect_all_models(results: dict) -> list[dict]:
    """Flatten all provider results into a single list."""
    all_models = []
    for provider_id in PROVIDERS:
        models = results.get(provider_id)
        if models and not isinstance(models, str):
            all_models.extend(models)
    return all_models


def newest_model_in_tier(models: list[dict]) -> str | None:
    """Return the ID of the model with the most recent created date."""
    dated = [model for model in models if model.get("created") and model["created"] != "unknown"]
    if not dated:
        return models[0]["id"] if models else None
    return max(dated, key=lambda model: model["created"])["id"]


def format_text_report(results: dict, registry_models: set[str] | None = None) -> str:
    """Human-readable text report."""
    env = build_doc_web_env()
    lines = []
    lines.append("=" * 60)
    lines.append("Catalog observations only; tiers are heuristic, task/inference access is unassessed.")
    lines.append("  AI Model Discovery Report")
    lines.append(f"  {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("=" * 60)
    if registry_models is None:
        lines.append("Registry score references not assessed.")

    lines.append("\n## API Key Status\n")
    for provider_id, provider in PROVIDERS.items():
        key = env.get(provider["env_key"], "")
        status = "SET" if key else "NOT SET"
        icon = "+" if key else "-"
        lines.append(
            f"  [{icon}] {provider['display']:20s} ({provider['env_key']}): {status}"
        )
        if not key:
            lines.append(f"      Setup: {provider['setup_url']}")
            lines.append(f"      {provider['setup_hint']}")

    for provider_id in PROVIDERS:
        models = results.get(provider_id)
        if models is None:
            lines.append(f"\n## {PROVIDERS[provider_id]['display']}: SKIPPED (no key)")
            continue
        if isinstance(models, str):
            lines.append(f"\n## {PROVIDERS[provider_id]['display']}: ERROR\n")
            lines.append(f"  {models}")
            continue

        lines.append(
            f"\n## {PROVIDERS[provider_id]['display']} — {len(models)} filtered catalog entries\n"
        )

        tier_groups: dict[str, list[dict]] = {tier: [] for tier in TIER_ORDER}
        for model in models:
            tier = model.get("tier", "mid")
            tier_groups.setdefault(tier, []).append(model)

        for tier in TIER_ORDER:
            tier_models = tier_groups.get(tier, [])
            if not tier_models:
                continue
            lines.append(f"  [{tier.upper()}]")
            for model in tier_models:
                model_id = model["id"]
                extra = ""
                if "display_name" in model and model["display_name"] != model_id:
                    extra = f" ({model['display_name']})"
                created = model.get("created", "")
                if created and created != "unknown":
                    extra += f"  [created: {created}]"
                if "input_token_limit" in model and model["input_token_limit"]:
                    extra += f"  [ctx: {model['input_token_limit']:,}]"
                in_registry = ""
                if registry_models is not None:
                    matched = _matches_registry(
                        model_id, model.get("display_name", ""), registry_models
                    )
                    in_registry = "  [SCORE REF]" if matched else "  [NO SCORE REF]"
                lines.append(f"    {model_id}{extra}{in_registry}")

    return "\n".join(lines)


def format_yaml_report(results: dict) -> str:
    """Machine-readable YAML report."""
    env = build_doc_web_env()
    report = {
        "discovered": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scope": "filtered catalog; inference access and task quality not assessed",
        "tiers": "heuristic",
        "providers": {},
    }

    for provider_id in PROVIDERS:
        key_set = bool(env.get(PROVIDERS[provider_id]["env_key"], ""))
        models = results.get(provider_id)
        entry = {
            "api_key_set": key_set,
            "env_key": PROVIDERS[provider_id]["env_key"],
        }

        if models is None:
            entry["status"] = "skipped"
            entry["complete"] = False
            entry["models"] = []
        elif isinstance(models, str):
            entry["status"] = "error"
            entry["complete"] = False
            entry["error"] = models
            entry["models"] = []
        else:
            entry["status"] = "ok"
            entry["complete"] = True
            entry["model_count"] = len(models)
            entry["models"] = models

        report["providers"][provider_id] = entry

    if yaml:
        return yaml.dump(report, default_flow_style=False, sort_keys=False)
    return json.dumps(report, indent=2)


def format_summary_report(results: dict, registry_models: set[str] | None = None) -> str:
    """Quick-glance tier summary."""
    all_models = collect_all_models(results)

    groups = group_by_tier(all_models)

    lines = []
    lines.append("=" * 60)
    lines.append("  Model Tier Summary")
    lines.append(f"  {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(
        f"  {len(all_models)} total models across "
        f"{sum(1 for value in results.values() if isinstance(value, list))} observed providers"
    )
    lines.append("=" * 60)
    lines.append("")
    lines.append("  Catalog observations only; tiers are heuristic, task/inference access is unassessed.")
    if registry_models is None:
        lines.append("  Registry score references not assessed.")
    for provider_id, provider in PROVIDERS.items():
        result = results.get(provider_id)
        status = ("skipped (no key)" if result is None else
                  f"error ({result})" if isinstance(result, str) else f"ok ({len(result)} entries)")
        lines.append(f"  {provider['display']}: {status}")
    lines.append("")

    for tier in TIER_ORDER:
        tier_models = groups.get(tier, [])
        if not tier_models:
            continue
        label = TIER_LABELS[tier]
        newest = newest_model_in_tier(tier_models)
        untested: list[str] = []
        if registry_models is not None:
            for model in tier_models:
                if not _matches_registry(
                    model["id"], model.get("display_name", ""), registry_models
                ):
                    untested.append(model["id"])

        lines.append(f"  {label}")
        lines.append(f"    Count   : {len(tier_models)}")
        if newest:
            lines.append(f"    Newest  : {newest}")
        if registry_models is not None:
            if untested:
                lines.append(
                    f"    No score reference: {len(untested)} ID(s) — {', '.join(untested)}"
                )
            else:
                lines.append("    No unmatched score-reference IDs")
        lines.append("")

    if registry_models is not None:
        all_untested = [
            model
            for model in all_models
            if not _matches_registry(
                model["id"], model.get("display_name", ""), registry_models
            )
        ]
        if all_untested:
            lines.append(
                f"  {len(all_untested)} catalog ID(s) have no matching score-name reference; "
                "inspect retry triggers before recommending an eval."
            )
        elif all_models:
            lines.append("  All catalog IDs have score-name references; this does not qualify any task.")

    return "\n".join(lines)


def _safe_provider_error(error: Exception) -> str:
    """Never serialize exception text, request URLs/headers or response bodies."""
    if isinstance(error, httpx.HTTPStatusError):
        return f"Discovery failed: HTTP {error.response.status_code} (no certified catalog)"
    if isinstance(error, httpx.TimeoutException):
        return "Discovery failed: request timeout (no certified catalog)"
    if isinstance(error, httpx.RequestError):
        return "Discovery failed: transport error (no certified catalog)"
    if isinstance(error, CatalogError):
        codes = {"invalid_catalog", "inconsistent_catalog", "invalid_cursor",
                 "pagination_cycle", "pagination_limit", "sensitive_response"}
        code = str(error) if str(error) in codes else "invalid_catalog"
        return f"Catalog unavailable or incomplete: {code}"
    if isinstance(error, (ValueError, TypeError, KeyError)):
        return "Discovery failed: invalid catalog response"
    return "Discovery failed: unexpected error"


def discover_models() -> dict:
    """Query all configured providers and return results."""
    env = build_doc_web_env()
    secrets = [env.get(provider["env_key"]) for provider in PROVIDERS.values()]
    results = {}
    for provider_id, provider in PROVIDERS.items():
        api_key = env.get(provider["env_key"], "")
        if not api_key:
            results[provider_id] = None
            continue

        print(f"Querying {provider['display']}...", file=sys.stderr)
        try:
            models = QUERY_FUNCS[provider_id](api_key)
            serialized = json.dumps(models, ensure_ascii=False)
            if any(secret and secret in serialized for secret in secrets):
                raise CatalogError("sensitive_response")
            results[provider_id] = models
            print(f"  Found {len(models)} models", file=sys.stderr)
        except Exception as exc:
            results[provider_id] = _safe_provider_error(exc)
            print(f"  {results[provider_id]}", file=sys.stderr)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover available AI models across providers"
    )
    parser.add_argument(
        "--yaml", action="store_true", help="Output as YAML (machine-readable)"
    )
    parser.add_argument(
        "--cache",
        action="store_true",
        help="Write to docs/evals/models-available.yaml",
    )
    parser.add_argument(
        "--check-new",
        action="store_true",
        help="Flag models not yet in eval registry",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Quick-glance tier summary (for /improve-eval)",
    )
    args = parser.parse_args()

    results = discover_models()

    registry_models = None
    if args.check_new or args.summary:
        registry_path = Path(__file__).parent.parent / "docs" / "evals" / "registry.yaml"
        registry_models = load_registry_models(registry_path)
        if registry_models:
            print(
                "\nRegistry contains "
                f"{len(registry_models)} score-name references: {', '.join(sorted(registry_models))}",
                file=sys.stderr,
            )

    if args.summary:
        output = format_summary_report(results, registry_models)
    elif args.yaml or args.cache:
        output = format_yaml_report(results)
    else:
        output = format_text_report(results, registry_models)

    if args.cache:
        cache_path = CACHE_PATH
        cache_path.write_text(format_yaml_report(results))
        print(f"\nWritten to {cache_path}", file=sys.stderr)
        if not args.summary:
            return

    print(output)


if __name__ == "__main__":
    main()
