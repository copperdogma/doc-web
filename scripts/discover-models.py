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
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

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
        "env_key": "OPENAI_API_KEY",
        "display": "OpenAI",
        "setup_url": "https://platform.openai.com/api-keys",
        "setup_hint": "export OPENAI_API_KEY='sk-...'",
    },
    "anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "display": "Anthropic",
        "setup_url": "https://console.anthropic.com/settings/keys",
        "setup_hint": "export ANTHROPIC_API_KEY='sk-ant-...'",
    },
    "google": {
        "env_key": "GEMINI_API_KEY",
        "display": "Google (Gemini)",
        "setup_url": "https://aistudio.google.com/app/apikey",
        "setup_hint": "export GEMINI_API_KEY='AI...'",
    },
}

OPENAI_CHAT_PATTERNS = [
    r"^gpt-",
    r"^o[134]-",
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

    models = []
    for model in data.get("data", []):
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


def query_anthropic(api_key: str) -> list[dict]:
    """Query Anthropic /v1/models for available models."""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    try:
        resp = httpx.get(
            "https://api.anthropic.com/v1/models",
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        models = []
        for model in data.get("data", []):
            model_id = model["id"]
            created_raw = model.get("created_at")
            if isinstance(created_raw, str):
                created = created_raw[:10]
            elif isinstance(created_raw, (int, float)) and created_raw > 0:
                created = datetime.fromtimestamp(
                    created_raw, tz=timezone.utc
                ).strftime("%Y-%m-%d")
            else:
                created = "unknown"
            models.append(
                {
                    "id": model_id,
                    "provider": "anthropic",
                    "display_name": model.get("display_name", model_id),
                    "created": created,
                    "tier": classify_tier(model_id),
                }
            )

        models.sort(key=lambda item: item.get("created", ""), reverse=True)
        return models
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        print(
            f"  Note: /v1/models returned {exc}. Using known model list.",
            file=sys.stderr,
        )
        return _anthropic_fallback()


def _anthropic_fallback() -> list[dict]:
    """Known Anthropic models when the API endpoint is unavailable."""
    known = [
        {
            "id": "claude-opus-4-6",
            "provider": "anthropic",
            "display_name": "Claude Opus 4.6",
            "created": "2025-12-01",
        },
        {
            "id": "claude-sonnet-4-6",
            "provider": "anthropic",
            "display_name": "Claude Sonnet 4.6",
            "created": "2025-12-01",
        },
        {
            "id": "claude-sonnet-4-5-20241022",
            "provider": "anthropic",
            "display_name": "Claude Sonnet 4.5",
            "created": "2025-10-01",
        },
        {
            "id": "claude-haiku-4-5-20251001",
            "provider": "anthropic",
            "display_name": "Claude Haiku 4.5",
            "created": "2025-10-01",
        },
    ]
    for model in known:
        model["tier"] = classify_tier(model["id"])
    return known


def query_google(api_key: str) -> list[dict]:
    """Query Google Gemini /v1beta/models for generative models."""
    resp = httpx.get(
        f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    models = []
    for model in data.get("models", []):
        name = model.get("name", "")
        model_id = name.replace("models/", "")
        methods = model.get("supportedGenerationMethods", [])
        if "generateContent" not in methods:
            continue
        if "embedding" in model_id or "aqa" in model_id:
            continue
        if any(re.search(pattern, model_id) for pattern in GOOGLE_SKIP_PATTERNS):
            continue
        models.append(
            {
                "id": model_id,
                "provider": "google",
                "display_name": model.get("displayName", model_id),
                "input_token_limit": model.get("inputTokenLimit"),
                "output_token_limit": model.get("outputTokenLimit"),
                "tier": classify_tier(model_id),
            }
        )

    models.sort(key=lambda item: item["id"])
    return models


QUERY_FUNCS = {
    "openai": query_openai,
    "anthropic": query_anthropic,
    "google": query_google,
}


def _normalize_model_text(text: str) -> str:
    """Normalize freeform model text while preserving version dots."""
    normalized = text.lower().replace("_", "-").replace(" ", "-")
    normalized = re.sub(r"[^a-z0-9.+-]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized


def _strip_alias_suffixes(text: str) -> str:
    """Trim common alias suffixes so dated snapshots match canonical IDs."""
    patterns = [
        r"-(\d{4}-\d{2}-\d{2}|\d{8})$",
        r"-chat-latest$",
        r"-latest$",
        r"-preview(?:-[a-z0-9.-]+)?$",
    ]
    stripped = text
    changed = True
    while changed:
        changed = False
        for pattern in patterns:
            updated = re.sub(pattern, "", stripped)
            if updated != stripped:
                stripped = updated
                changed = True
    return stripped


def _extract_canonical_models(text: str) -> set[str]:
    """Extract canonical model-family identifiers from freeform text."""
    normalized = _strip_alias_suffixes(_normalize_model_text(text))
    tokens: set[str] = set()

    patterns = [
        (
            re.compile(r"\bgpt-(\d+)(?:[.-](\d+))?(?:-(pro|mini|nano))?\b"),
            lambda m: "gpt-"
            + m.group(1)
            + (f".{m.group(2)}" if m.group(2) else "")
            + (f"-{m.group(3)}" if m.group(3) else ""),
        ),
        (
            re.compile(r"\b(o[134])(?:-(mini|pro))?\b"),
            lambda m: m.group(1) + (f"-{m.group(2)}" if m.group(2) else ""),
        ),
        (
            re.compile(r"\bchatgpt-4o\b"),
            lambda m: "chatgpt-4o",
        ),
        (
            re.compile(r"\bclaude-(opus|sonnet|haiku)-(\d+)(?:[.-](\d+))?\b"),
            lambda m: "claude-"
            + m.group(1)
            + "-"
            + m.group(2)
            + (f".{m.group(3)}" if m.group(3) else ""),
        ),
        (
            re.compile(
                r"\bgemini-(\d+)(?:[.-](\d+))?(?:-(pro|flash-lite|flash|computer-use))?\b"
            ),
            lambda m: "gemini-"
            + m.group(1)
            + (f".{m.group(2)}" if m.group(2) else "")
            + (f"-{m.group(3)}" if m.group(3) else ""),
        ),
        (
            re.compile(r"\bgemini-(pro|flash-lite|flash)\b"),
            lambda m: "gemini-" + m.group(1),
        ),
    ]

    for pattern, builder in patterns:
        for match in pattern.finditer(normalized):
            tokens.add(builder(match))

    if not tokens and normalized:
        tokens.add(normalized)
    return tokens


def _matches_registry(model_id: str, display_name: str, registry_models: set[str]) -> bool:
    """Check if a discovered model matches any canonical registry entry."""
    discovered = _extract_canonical_models(model_id)
    if display_name:
        discovered |= _extract_canonical_models(display_name)
    return bool(discovered & registry_models)


def load_registry_models(registry_path: Path) -> set[str]:
    """Extract canonical model identifiers mentioned in the eval registry."""
    if not registry_path.exists():
        return set()
    if yaml is None:
        text = registry_path.read_text()
        models = set()
        for line in text.splitlines():
            if "model:" not in line:
                continue
            model_name = line.split("model:")[-1].strip().strip('"').strip("'")
            models |= _extract_canonical_models(model_name)
        return models

    data = yaml.safe_load(registry_path.read_text())
    models = set()
    for eval_entry in data.get("evals", []):
        for score in eval_entry.get("scores", []):
            model_name = score.get("model", "")
            if model_name:
                models |= _extract_canonical_models(model_name)
    return models


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
    lines = []
    lines.append("=" * 60)
    lines.append("  AI Model Discovery Report")
    lines.append(f"  {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("=" * 60)

    lines.append("\n## API Key Status\n")
    for provider_id, provider in PROVIDERS.items():
        key = os.environ.get(provider["env_key"], "")
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
            continue
        if isinstance(models, str):
            lines.append(f"\n## {PROVIDERS[provider_id]['display']}: ERROR\n")
            lines.append(f"  {models}")
            continue

        lines.append(
            f"\n## {PROVIDERS[provider_id]['display']} — {len(models)} chat models\n"
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
                    in_registry = "  [TESTED]" if matched else "  [NEW]"
                lines.append(f"    {model_id}{extra}{in_registry}")

    return "\n".join(lines)


def format_yaml_report(results: dict) -> str:
    """Machine-readable YAML report."""
    report = {
        "discovered": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "providers": {},
    }

    for provider_id in PROVIDERS:
        key_set = bool(os.environ.get(PROVIDERS[provider_id]["env_key"], ""))
        models = results.get(provider_id)
        entry = {
            "api_key_set": key_set,
            "env_key": PROVIDERS[provider_id]["env_key"],
        }

        if models is None:
            entry["status"] = "skipped"
            entry["models"] = []
        elif isinstance(models, str):
            entry["status"] = "error"
            entry["error"] = models
            entry["models"] = []
        else:
            entry["status"] = "ok"
            entry["model_count"] = len(models)
            entry["models"] = models

        report["providers"][provider_id] = entry

    if yaml:
        return yaml.dump(report, default_flow_style=False, sort_keys=False)
    return json.dumps(report, indent=2)


def format_summary_report(results: dict, registry_models: set[str] | None = None) -> str:
    """Quick-glance tier summary."""
    all_models = collect_all_models(results)
    if not all_models:
        return "No models discovered (check API keys)."

    groups = group_by_tier(all_models)

    lines = []
    lines.append("=" * 60)
    lines.append("  Model Tier Summary")
    lines.append(f"  {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(
        f"  {len(all_models)} total models across "
        f"{sum(1 for value in results.values() if value and not isinstance(value, str))} providers"
    )
    lines.append("=" * 60)
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
                    f"    Untested: {len(untested)} model(s) — {', '.join(untested)}"
                )
            else:
                lines.append("    Untested: none")
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
                f"  ** {len(all_untested)} untested model(s) found — "
                "consider running /improve-eval **"
            )
        else:
            lines.append("  All discovered models are covered by existing evals.")

    return "\n".join(lines)


def discover_models() -> dict:
    """Query all configured providers and return results."""
    results = {}
    for provider_id, provider in PROVIDERS.items():
        api_key = os.environ.get(provider["env_key"], "")
        if not api_key:
            results[provider_id] = None
            continue

        print(f"Querying {provider['display']}...", file=sys.stderr)
        try:
            models = QUERY_FUNCS[provider_id](api_key)
            results[provider_id] = models
            print(f"  Found {len(models)} models", file=sys.stderr)
        except Exception as exc:
            results[provider_id] = f"Error: {exc}"
            print(f"  Error: {exc}", file=sys.stderr)

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
                f"{len(registry_models)} tested models: {', '.join(sorted(registry_models))}",
                file=sys.stderr,
            )

    if args.summary:
        output = format_summary_report(results, registry_models)
    elif args.yaml or args.cache:
        output = format_yaml_report(results)
    else:
        output = format_text_report(results, registry_models)

    if args.cache:
        cache_path = Path(__file__).parent.parent / "docs" / "evals" / "models-available.yaml"
        cache_path.write_text(output)
        print(f"\nWritten to {cache_path}", file=sys.stderr)
        return

    print(output)


if __name__ == "__main__":
    main()
