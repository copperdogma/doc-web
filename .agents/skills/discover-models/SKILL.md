---
name: discover-models
description: Discover available AI models across all configured providers and compare against eval registry.
user-invocable: true
---

# /discover-models

> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md` and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

Query OpenAI, Anthropic, and Google model catalogs, compare exact identity references in recorded scores, and identify candidates for further investigation. Catalog presence does not prove inference access, modality, quality or task qualification.

## Steps

1. **Run the discovery script**:

```bash
python scripts/discover-models.py --check-new
```

2. **Analyze the output**:
   - Which providers have API keys configured?
   - Which catalog IDs lack a matching score-name reference?
   - Are there new SOTA models since our last eval run?
   - Are there new cheap models that might be cost-effective alternatives?

3. **Report to user**:
   - Summarize observed candidates, provider errors and missing API keys; check existing retry triggers before recommending an eval
   - Highlight models that are likely interesting for eval work (new SOTA, new cheap tier)
   - Preserve exact dated snapshots, previews and sibling identities in evidence; do not treat aliases as equivalent without separate evidence

4. **Optionally cache results**:

```bash
python scripts/discover-models.py --cache
```

This writes to `docs/evals/models-available.yaml` for other skills to reference.

## Notes

- The script uses repo-scoped `DOC_WEB_OPENAI_API_KEY`, `DOC_WEB_ANTHROPIC_API_KEY` and `DOC_WEB_GEMINI_API_KEY` through `doc_web.env`; never print credential values
- If a key is missing, the script reports setup instructions
- Catalog filters and tiers are heuristics, not capability or quality measurements
- `[SCORE REF]` means the ID matches a model-name reference in registry scores; `[NO SCORE REF]` means no such match, not proof it was never evaluated
- Complete Google/Anthropic pagination is bounded to20pages. A failed, malformed or incomplete traversal contributes no certified models; there is no static-success fallback
- Error reports contain safe categories/status codes, never raw exception messages or URLs. Google authentication uses a header
- `--cache --summary` writes structured YAML and prints the summary; every report keeps skipped/error/empty-success states distinct
