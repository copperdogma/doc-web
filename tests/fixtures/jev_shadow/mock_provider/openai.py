"""Offline provider for synthetic driver verification, never used by runtime."""

import json
import os
from pathlib import Path
from types import SimpleNamespace


class OpenAI:
    def __init__(self, *args, **kwargs):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        payload = {
            "analysis_summary": {"default_note_policy": "Keep row ownership"},
            "pattern_families": [
                {
                    "pattern_id": "synthetic",
                    "member_chapters": ["chapter-001.html"],
                    "canonical_headers": [
                        "NAME",
                        "BORN",
                        "MARRIED",
                        "SPOUSE",
                        "BOY",
                        "GIRL",
                        "DIED",
                    ],
                    "document_local_conventions": {
                        "table_fragmentation": "One main table",
                        "subgroup_context_rows": "Full width family row",
                    },
                }
            ],
            "chapter_findings": [
                {
                    "chapter_basename": "chapter-001.html",
                    "pattern_id": "synthetic",
                    "status": "conformant",
                    "issue_types": [],
                }
            ],
        }
        if os.environ.get("DOC_WEB_TEST_PLANNER_PAYLOAD_PATH"):
            payload = json.loads(
                Path(os.environ["DOC_WEB_TEST_PLANNER_PAYLOAD_PATH"]).read_text()
            )
        return SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))
            ],
            usage=SimpleNamespace(prompt_tokens=100, completion_tokens=100),
            model=kwargs["model"],
        )
