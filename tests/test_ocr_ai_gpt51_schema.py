import json
from html.parser import HTMLParser
from pathlib import Path

from modules.extract.ocr_ai_gpt51_v1.main import ALLOWED_TAGS, RUNNING_HEAD_CLASS, PAGE_NUMBER_CLASS


class HtmlSchemaValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []

    def handle_starttag(self, tag, attrs):
        self._validate_tag(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._validate_tag(tag, attrs)

    def _validate_tag(self, tag, attrs):
        tag = tag.lower()
        if tag not in ALLOWED_TAGS:
            self.errors.append(f"disallowed tag: {tag}")
            return

        attrs_dict = {k.lower(): v for k, v in attrs}

        if tag == "img":
            # only allow alt (may be empty)
            extra = [k for k in attrs_dict.keys() if k != "alt"]
            if extra:
                self.errors.append(f"img has extra attrs: {extra}")
            return

        if tag == "p":
            if not attrs_dict:
                return
            cls = attrs_dict.get("class")
            if cls not in (RUNNING_HEAD_CLASS, PAGE_NUMBER_CLASS):
                self.errors.append(f"p has invalid class: {cls}")
            extra = [k for k in attrs_dict.keys() if k != "class"]
            if extra:
                self.errors.append(f"p has extra attrs: {extra}")
            return

        if attrs_dict:
            self.errors.append(f"{tag} has unexpected attrs: {list(attrs_dict.keys())}")


def test_fixture_html_conforms_to_schema():
    fixture_path = Path("testdata/html-blocks-fixtures/pages_html.jsonl")
    assert fixture_path.exists(), f"missing fixture: {fixture_path}"

    rows = [
        json.loads(line)
        for line in fixture_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows, "no HTML fixture rows found"

    for row in rows:
        parser = HtmlSchemaValidator()
        parser.feed(row["html"])
        assert not parser.errors, f"page {row.get('page')}: {parser.errors}"
