# Opt-in Sol 6.2 literal table review

Use this review recipe on public or authored synthetic, text/table-only sources. It keeps the existing initial OCR and source-agreement/export requirements. Select the alternate recipe in a checkout containing the patch, with the project's driver environment and normal Doc Web credential wrapper.

```bash
python scripts/run_with_doc_web_env.py python driver.py \
  --recipe configs/recipes/recipe-pdf-literal-tables-html-sol62.yaml \
  --input-pdf /absolute/path/to/eligible-source.pdf \
  --run-id reviewed-sol62-tables
```

The reader sends the source page with original detail to Standard native Responses at medium effort, requests a strict source-table schema, and binds the served identity and source to the final publication record. The three-page review reserves $0.50 per page and refuses counts above 26,000 input tokens before inference. An ambiguous glyph or conflicting OCR evidence holds the page. Inspect the page review report to resolve a hold. Initial OCR retains its own existing budget.

For rollback, select `configs/recipes/recipe-pdf-literal-tables-html.yaml` with a fresh run ID. The original Astra default and existing opt-in Astra 6.2 and Argon recipes still interpret their own records. The measured economics cover only the strict source-reader stage. [Attempt 098](../evals/attempts/098-gpt62-sol-source-fidelity.md)
