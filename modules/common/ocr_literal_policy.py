"""Generic literal transcription policy, shared by runtime and evaluation."""

LITERAL_POLICY = """Literal transcription policy:
- Treat every visible character as source data. Preserve letter case, punctuation,
  spelling and visually similar letters/digits exactly as printed.
- Do not silently correct apparent typos, identifiers, references or unusual
  wording using context, common sense or what the document probably intended.
- Recheck table cells against their visible source. Preserve empty cells, dashes,
  modifiers, repeated values and cell ownership. Preserve visible row/column spans.
- Linking or structuring a reference must never change its printed characters.
"""
