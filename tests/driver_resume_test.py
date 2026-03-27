import json
import os
import sys
import tempfile
import unittest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from driver import artifact_schema_matches, finalize_run_state


class ResumeTests(unittest.TestCase):
    def test_artifact_schema_matches_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "a.jsonl")
            rows = [
                {"schema_version": "clean_page_v1", "foo": 1},
                {"schema_version": "clean_page_v1", "foo": 2},
            ]
            with open(path, "w", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
            self.assertTrue(artifact_schema_matches(path, "clean_page_v1"))

    def test_artifact_schema_matches_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "a.jsonl")
            rows = [
                {"schema_version": "other_v1", "foo": 1},
            ]
            with open(path, "w", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
            self.assertFalse(artifact_schema_matches(path, "clean_page_v1"))

    def test_finalize_run_state_clears_stale_status_reason_on_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "pipeline_state.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "status": "failed",
                        "status_reason": "stage portionize_toc failed",
                        "ended_at": "2026-03-27T01:36:38.764081Z",
                    },
                    f,
                )

            finalize_run_state(path, run_validation_failed=False)

            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            self.assertEqual(state["status"], "done")
            self.assertNotIn("status_reason", state)
            self.assertIn("ended_at", state)

    def test_finalize_run_state_sets_validation_failure_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "pipeline_state.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"status": "done"}, f)

            finalize_run_state(path, run_validation_failed=True)

            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            self.assertEqual(state["status"], "failed")
            self.assertEqual(state["status_reason"], "game_ready_validation_failed")
            self.assertIn("ended_at", state)


if __name__ == "__main__":
    unittest.main()
