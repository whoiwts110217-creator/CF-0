"""CF-0 prompt-change governance checks: source integrity and regression examples."""
import tempfile
import unittest
from pathlib import Path

from automation_200.prompt_change_guard import ROOT, audit, PROMPTS, LOG, BIN


class PromptChangeGuardTests(unittest.TestCase):
    def fixture(self, root):
        for path in (*PROMPTS, LOG, BIN):
            dest = root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT / path).read_bytes())

    def test_committed_public_prompts_are_tracked(self):
        self.assertEqual(audit(ROOT), [])

    def test_missing_priority_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            prompt = root / PROMPTS[0]
            prompt.write_text(prompt.read_text(encoding="utf-8").replace("P2 — Financial operations", "P2 removed"), encoding="utf-8")
            problems = audit(root)
            self.assertTrue(any("P2 — Financial operations" in p for p in problems))
            self.assertTrue(any("latest recorded blob" in p for p in problems))

    def test_silent_edit_and_missing_log_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            prompt = root / PROMPTS[2]
            prompt.write_bytes(prompt.read_bytes() + b"\n# Unrecorded change\n")
            self.assertTrue(any("latest recorded blob" in p for p in audit(root)))
            (root / LOG).unlink()
            self.assertTrue(any("Missing append-only" in p for p in audit(root)))


if __name__ == "__main__":
    unittest.main()
