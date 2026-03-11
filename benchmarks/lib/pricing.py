"""Model pricing table and cost estimation.

Ported from Dossier's benchmarking.py. Prices are per 1M tokens (input, output).
"""

CHARS_PER_TOKEN = 4

# (input_price_per_1M, output_price_per_1M)
MODEL_PRICING: dict[str, tuple[float, float]] = {
    # Anthropic
    "claude-opus-4-6": (15.0, 75.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-sonnet-4-20250514": (3.0, 15.0),
    "claude-haiku-4-5-20251001": (0.80, 4.0),
    # OpenAI
    "gpt-5.1": (2.0, 8.0),
    "gpt-4o": (2.50, 10.0),
    "gpt-4.1": (2.0, 8.0),
    "gpt-4.1-mini": (0.40, 1.60),
    # Google
    "gemini-2.5-pro": (1.25, 10.0),
    "gemini-2.5-flash": (0.15, 0.60),
    "gemini-3-pro-preview": (1.25, 10.0),
}


def estimate_cost(model: str, input_chars: int, output_chars: int) -> float | None:
    """Estimate cost in USD from character counts and known pricing."""
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return None
    input_tokens = input_chars / CHARS_PER_TOKEN
    output_tokens = output_chars / CHARS_PER_TOKEN
    input_cost = (input_tokens / 1_000_000) * pricing[0]
    output_cost = (output_tokens / 1_000_000) * pricing[1]
    return round(input_cost + output_cost, 6)


def estimate_cost_from_tokens(
    model: str, input_tokens: int, output_tokens: int
) -> float | None:
    """Estimate cost in USD from token counts and known pricing."""
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return None
    input_cost = (input_tokens / 1_000_000) * pricing[0]
    output_cost = (output_tokens / 1_000_000) * pricing[1]
    return round(input_cost + output_cost, 6)


def pricing_label(model: str) -> str:
    """Format pricing as a compact label: '$input/output'."""
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return ""
    return f"${pricing[0]}/{pricing[1]}"
