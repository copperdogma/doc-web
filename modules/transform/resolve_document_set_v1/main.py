"""Driver adapter for the same public offline related-set operation."""
import argparse
import json
import sys
import uuid
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from doc_web.related_documents import resolve_document_set


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--run-id", "--run_id")
    parser.add_argument("--state-file")
    parser.add_argument("--progress-file")
    args = parser.parse_args()
    output = Path(args.out)
    destination = output.parent / "related-set"
    if destination.exists() or destination.is_symlink():
        # Resumption retains the starting stage directory. Keep earlier proof
        # immutable and let the result locator select the fresh derivative.
        destination = output.parent / f"related-set-{uuid.uuid4().hex}"
    result = resolve_document_set(args.input, destination)
    # The driver result is a locator; the portable receipt lives inside the set.
    result["schema_version"] = "doc_web_related_set_result_v1"
    result["run_id"] = args.run_id
    output.write_text(json.dumps(result) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
