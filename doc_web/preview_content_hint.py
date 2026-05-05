from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any, Mapping

from doc_web import __version__
from doc_web.env import get_doc_web_api_key


PROMPT_VERSION = "doc-web-preview-content-hint-v2"
DEFAULT_AI_MODEL = "gpt-4.1-nano"
MAX_AI_EVIDENCE_CHARS = 3200


_KIND_PATTERNS = [
    (
        "game rulebook",
        re.compile(
            r"\b(game|rulebook|round|players?|cards?|tokens?|board|robot|programming)\b",
            re.I,
        ),
    ),
    (
        "family history",
        re.compile(
            r"\b(genealogy|biography|family|ancestor|descendant|born|married|children)\b",
            re.I,
        ),
    ),
    (
        "form",
        re.compile(r"\b(form|application|signature|required|applicant)\b", re.I),
    ),
]


def build_content_hint(
    *,
    facts: dict[str, Any],
    parsed_units: list[dict[str, Any]],
    coverage_state: str,
    warnings: list[str],
    mode: str = "auto",
    ai_model: str = DEFAULT_AI_MODEL,
    ai_timeout_seconds: float = 0.75,
    source_sha256: str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build a non-final high-level content hint.

    `mode=auto` uses a bounded cheap-model pass when a doc-web OpenAI key is
    configured, then falls back to deterministic heuristics if the model is
    unavailable, slow, or returns unusable JSON.
    """
    texts = [
        str(unit.get("text") or "").strip()
        for unit in parsed_units
        if str(unit.get("text") or "").strip()
    ]
    sample_text = " ".join(texts)
    quality_score = _text_quality_score(sample_text)
    title_guess = _title_guess(facts, texts)
    kind = _kind_hint(" ".join([str(title_guess or ""), sample_text]))
    hint_warnings = list(warnings)

    sample_sha256 = _sample_sha256(texts)
    cache_key = _cache_key(
        source_sha256=source_sha256,
        sample_sha256=sample_sha256,
        mode=mode,
        model=ai_model,
    )

    if not sample_text:
        hint = {
            "status": "deferred",
            "title_guess": title_guess,
            "document_kind_hint": kind,
            "high_level_summary": _deferred_summary(title_guess=title_guess, kind=kind),
            "basis": ["structural_facts"],
            "evidence": [],
            "warnings": hint_warnings,
            "text_quality_score": 0.0,
            "summary_prompt_version": PROMPT_VERSION,
            "sample_sha256": sample_sha256,
            "cache_key": cache_key,
        }
        return hint

    if _looks_like_noisy_ocr(facts, sample_text, quality_score):
        status = "low_quality"
        hint_warnings.append(
            "Preview text appears sparse or noisy; the high-level hint is based primarily on metadata and visible title text."
        )
    else:
        status = "available"

    deterministic = {
        "status": status,
        "title_guess": title_guess,
        "document_kind_hint": kind,
        "high_level_summary": _summary(title_guess=title_guess, kind=kind, texts=texts),
        "basis": [*_basis(facts, texts), "deterministic_fallback"],
        "evidence": _evidence(texts),
        "warnings": hint_warnings,
        "text_quality_score": round(quality_score, 3),
        "coverage_state": coverage_state,
        "summary_prompt_version": PROMPT_VERSION,
        "sample_sha256": sample_sha256,
        "cache_key": cache_key,
    }
    if mode == "deterministic":
        return deterministic
    if mode not in {"auto", "ai"}:
        raise ValueError("content hint mode must be 'auto', 'ai', or 'deterministic'")
    return _ai_content_hint(
        deterministic=deterministic,
        facts=facts,
        texts=texts,
        coverage_state=coverage_state,
        mode=mode,
        model=ai_model,
        timeout_seconds=ai_timeout_seconds,
        env=env,
    )


def _ai_content_hint(
    *,
    deterministic: dict[str, Any],
    facts: dict[str, Any],
    texts: list[str],
    coverage_state: str,
    mode: str,
    model: str,
    timeout_seconds: float,
    env: Mapping[str, str] | None,
) -> dict[str, Any]:
    api_key = get_doc_web_api_key("openai", env=env)
    if not api_key:
        return _fallback(
            deterministic,
            fallback_reason="DOC_WEB_OPENAI_API_KEY is not configured.",
            hard_failure=mode == "ai",
        )

    started_at = time.perf_counter()
    try:
        client = _make_openai_client(
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            max_retries=0,
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write concise document preview summaries from sampled text. "
                        "Return only a JSON object with keys: title_guess, "
                        "document_kind_hint, high_level_summary. The summary must be one "
                        "direct sentence under 35 words. Do not use hedging words such as "
                        "likely, appears, seems, may, or suggests. Do not write 'document "
                        "titled' or 'headed'. Do not use slash labels or joined synonym "
                        "alternatives like 'genealogy or family history'. Use one concrete "
                        "type such as game rulebook, family history, application form, "
                        "historical biography, technical manual, report, or letter. Do not "
                        "invent details beyond the metadata and evidence."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "title_guess": deterministic.get("title_guess"),
                            "document_kind_hint": deterministic.get(
                                "document_kind_hint"
                            ),
                            "coverage_state": coverage_state,
                            "status": deterministic.get("status"),
                            "warnings": deterministic.get("warnings", []),
                            "structural_facts": _prompt_facts(facts),
                            "evidence": _prompt_evidence(texts),
                            "fallback_summary": deterministic.get("high_level_summary"),
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            temperature=0,
            max_tokens=220,
            response_format={"type": "json_object"},
        )
        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 3)
        raw = response.choices[0].message.content or ""
        data = _parse_json_object(raw)
        ai_hint = _normalize_ai_hint(data, fallback=deterministic)
    except Exception as exc:
        return _fallback(
            deterministic,
            fallback_reason=f"{type(exc).__name__}: {exc}",
            hard_failure=mode == "ai",
        )

    ai_hint.update(
        {
            "status": deterministic["status"],
            "basis": [
                basis
                for basis in deterministic["basis"]
                if basis != "deterministic_fallback"
            ]
            + [f"ai_summary:openai:{model}"],
            "evidence": deterministic["evidence"],
            "warnings": deterministic["warnings"],
            "text_quality_score": deterministic.get("text_quality_score"),
            "coverage_state": coverage_state,
            "summary_provider": "openai",
            "summary_model": model,
            "summary_ms": elapsed_ms,
            "summary_prompt_version": PROMPT_VERSION,
            "sample_sha256": deterministic.get("sample_sha256"),
            "cache_key": deterministic.get("cache_key"),
        }
    )
    return ai_hint


def _make_openai_client(
    *, api_key: str, timeout_seconds: float, max_retries: int
) -> Any:
    from openai import OpenAI

    return OpenAI(api_key=api_key, timeout=timeout_seconds, max_retries=max_retries)


def _fallback(
    deterministic: dict[str, Any], *, fallback_reason: str, hard_failure: bool
) -> dict[str, Any]:
    hint = dict(deterministic)
    hint["fallback_reason"] = fallback_reason
    if hard_failure:
        hint["warnings"] = [
            *hint.get("warnings", []),
            f"AI content hint failed; deterministic fallback used: {fallback_reason}",
        ]
    return hint


def _normalize_ai_hint(
    data: dict[str, Any], *, fallback: dict[str, Any]
) -> dict[str, Any]:
    title = _clean_title(str(data.get("title_guess") or "").strip())
    kind = _clean_kind(str(data.get("document_kind_hint") or "").strip())
    summary = _clean_summary(str(data.get("high_level_summary") or "").strip())
    if not title:
        title = fallback.get("title_guess")
    if summary and title:
        summary = _replace_generic_subject(summary, title)
        summary = _trim_long_title_prefix(summary, title)
    if not kind or _contains_joined_alternatives(kind):
        kind = fallback.get("document_kind_hint") or "unknown"
    if not summary or _contains_banned_summary_language(summary):
        summary = fallback["high_level_summary"]
    return {
        "title_guess": title,
        "document_kind_hint": kind,
        "high_level_summary": summary,
    }


def _parse_json_object(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("AI content hint did not return a JSON object")
    return data


def _prompt_facts(facts: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "format",
        "page_count",
        "image_count",
        "sampled_page_count",
        "sampled_image_count",
        "metadata_title",
        "metadata_creator",
        "text_layer_available",
        "ocr_needed",
        "ocr_engine",
    }
    return {key: facts[key] for key in allowed if key in facts}


def _prompt_evidence(texts: list[str]) -> list[str]:
    evidence = []
    remaining = MAX_AI_EVIDENCE_CHARS
    for text in _evidence(texts):
        if remaining <= 0:
            break
        excerpt = text[:remaining]
        evidence.append(excerpt)
        remaining -= len(excerpt)
    return evidence


def _title_guess(facts: dict[str, Any], texts: list[str]) -> str | None:
    metadata_title = str(facts.get("metadata_title") or "").strip()
    if metadata_title and facts.get("format") != "image_directory":
        return _clean_title(metadata_title)

    candidates: list[str] = []
    for text in texts[:8]:
        cleaned = re.sub(r"\s+", " ", text).strip(" -|")
        if not cleaned or len(cleaned) < 3:
            continue
        if len(cleaned) <= 90:
            candidates.append(cleaned)
        if len(candidates) >= 4:
            break
    if not candidates:
        if facts.get("format") == "image_directory":
            return None
        return _clean_title(metadata_title) or None
    return _clean_title(" ".join(candidates[:3])[:160])


def _clean_title(title: str) -> str:
    cleaned = re.sub(r"\s+", " ", title).strip()
    cleaned = re.sub(r"\s+-\s+[A-Za-z0-9.-]+\.[A-Za-z]{2,}\s*$", "", cleaned)
    return cleaned.strip()


def _clean_kind(kind: str) -> str:
    cleaned = re.sub(r"\s+", " ", kind).strip(" .")
    return cleaned[:80]


def _clean_summary(summary: str) -> str:
    cleaned = re.sub(r"\s+", " ", summary).strip()
    cleaned = cleaned.strip("\"'")
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned[:260]


def _replace_generic_subject(summary: str, title: str) -> str:
    return re.sub(
        r"^(the|this) document\b",
        title,
        summary,
        count=1,
        flags=re.I,
    )


def _trim_long_title_prefix(summary: str, title: str) -> str:
    if len(title) < 60:
        return summary
    prefix = f"{title} is "
    if not summary.lower().startswith(prefix.lower()):
        return summary
    trimmed = summary[len(prefix) :].strip()
    if not trimmed:
        return summary
    return f"{trimmed[:1].upper()}{trimmed[1:]}"


def _kind_hint(text: str) -> str:
    for label, pattern in _KIND_PATTERNS:
        if pattern.search(text):
            return label
    if (
        re.search(r"\b\d{4}\s*[-–]\s*\d{4}\b", text)
        and len(_capitalized_words(text)) >= 2
    ):
        return "family history"
    return "unknown"


def _summary(*, title_guess: str | None, kind: str, texts: list[str]) -> str:
    if title_guess and kind != "unknown":
        family_summary = _family_history_summary_from_title(title_guess, kind)
        if family_summary:
            return family_summary
        game_summary = _game_rulebook_summary_from_text(title_guess, texts, kind)
        if game_summary:
            return game_summary
        return f"{title_guess} is {_indefinite_article(kind)} {kind}."
    if title_guess:
        return f"Preview title: {title_guess}."
    if kind != "unknown":
        return f"This is {_indefinite_article(kind)} {kind}."
    evidence = _evidence(texts)
    if evidence:
        return f"Preview text begins with: {evidence[0]}"
    return "No reliable high-level content hint is available from the preview sample."


def _deferred_summary(*, title_guess: str | None, kind: str) -> str:
    if title_guess and kind != "unknown":
        return (
            f"Structural metadata identifies {title_guess} "
            f"as {_indefinite_article(kind)} {kind}."
        )
    if title_guess:
        return f"Structural metadata title: {title_guess}."
    return "No preview text was available inside the preview budget."


def _family_history_summary_from_title(title: str, kind: str) -> str | None:
    if kind != "family history":
        return None
    dated_match = re.match(
        r"^(?P<title>.+?)\s+(?P<dates>\d{4}\s*[-–]\s*\d{4})\s+(?P<people>.+)$",
        title,
    )
    if dated_match:
        short_title = dated_match.group("title").strip()
        dates = re.sub(r"\s*[-–]\s*", "-", dated_match.group("dates").strip())
        people = dated_match.group("people").strip()
        return f"{short_title} {dates} is a family history about {people}."

    family_match = re.search(
        (
            r"\b(?:genealogy|biography|history)\b.{0,100}?\bof\s+"
            r"(?:the\s+)?(?P<subject>[A-Z][^:.;,]{2,80}?\bfamily)\b"
        ),
        title,
        re.I,
    )
    if not family_match:
        return None
    short_title = title.split(":", 1)[0].strip() or title
    subject = re.sub(r"\s+", " ", family_match.group("subject")).strip()
    subject = re.sub(r"\bFamily\b$", "family", subject)
    return f"{short_title} is a family history about the {subject}."


def _game_rulebook_summary_from_text(
    title: str, texts: list[str], kind: str
) -> str | None:
    if kind != "game rulebook":
        return None
    sample = " ".join(texts).lower()
    topics: list[str] = []
    if re.search(r"\b(contents?|components?|tokens?|cards?|gameboards?)\b", sample):
        topics.append("components")
    if re.search(r"\bsetup|start board\b", sample):
        topics.append("setup")
    if re.search(r"\b(round|phase|turn|gameplay)\b", sample):
        topics.append("gameplay phases")
    if re.search(r"\brobot|programming\b", sample):
        topics.append("robot programming")
    if re.search(r"\bupgrades?\b", sample):
        topics.append("upgrades")
    if len(topics) < 2:
        return None
    return f"{title} is a game rulebook covering {_join_phrase(topics[:4])}."


def _join_phrase(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _indefinite_article(phrase: str) -> str:
    return "an" if phrase[:1].lower() in {"a", "e", "i", "o", "u"} else "a"


def _contains_joined_alternatives(text: str) -> bool:
    return bool(re.search(r"\b(or|/)\b", text, re.I))


def _contains_banned_summary_language(text: str) -> bool:
    return bool(
        re.search(
            r"\b(likely|appears?|seems?|may|suggests?)\b|titled or headed|document titled|document headed",
            text,
            re.I,
        )
    )


def _sample_sha256(texts: list[str]) -> str:
    payload = json.dumps(texts, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _cache_key(
    *,
    source_sha256: str | None,
    sample_sha256: str,
    mode: str,
    model: str,
) -> str:
    payload = {
        "doc_web_version": __version__,
        "mode": mode,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "sample_sha256": sample_sha256,
        "source_sha256": source_sha256,
    }
    digest = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return f"sha256:{digest}"


def _basis(facts: dict[str, Any], texts: list[str]) -> list[str]:
    basis = ["structural_facts"]
    if facts.get("metadata_title"):
        basis.append("metadata_title")
    if texts:
        basis.append("sample_text")
    if facts.get("ocr_engine"):
        basis.append(f"preview_ocr:{facts['ocr_engine']}")
    return basis


def _evidence(texts: list[str]) -> list[str]:
    evidence = []
    for text in texts:
        cleaned = re.sub(r"\s+", " ", text).strip()
        if len(cleaned) < 3:
            continue
        evidence.append(cleaned[:220])
        if len(evidence) >= 5:
            break
    return evidence


def _text_quality_score(text: str) -> float:
    compact = re.sub(r"\s+", "", text or "")
    if not compact:
        return 0.0
    tokens = re.findall(r"[A-Za-z][A-Za-z'’-]{2,}", text)
    if not tokens:
        return 0.0
    alpha_ratio = sum(ch.isalpha() for ch in compact) / max(len(compact), 1)
    vowel_ratio = sum(
        1 for token in tokens if re.search(r"[aeiouyAEIOUY]", token)
    ) / len(tokens)
    volume = min(len(tokens) / 40, 1.0)
    return max(0.0, min(1.0, 0.5 * alpha_ratio + 0.3 * vowel_ratio + 0.2 * volume))


def _looks_like_noisy_ocr(
    facts: dict[str, Any], text: str, quality_score: float
) -> bool:
    if not text:
        return True
    if quality_score < 0.55:
        return True
    if "tesseract" in str(facts.get("metadata_creator") or "").lower():
        return len(text) < 800
    return False


def _capitalized_words(text: str) -> list[str]:
    return re.findall(r"\b[A-Z][a-zA-Z'’-]{2,}\b", text)
