"""Public operator-source continuity contract tests; evidence of files, not AI obedience."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def content(path):
    return (ROOT / path).read_text(encoding="utf-8")

class MasterContinuityTests(unittest.TestCase):
    def test_public_master_is_first_before_project_decisions(self):
        master = content("automation_200/MASTER_OPERATOR_PROMPT.md")
        first_section = master[:1400]
        self.assertIn("MANDATORY FIRST STEP", first_section)
        self.assertIn("MASTER_CONTINUITY_PROMPT.md", first_section)
        self.assertIn("before", first_section.lower())
        self.assertIn("CF-0", first_section)

    def test_public_master_has_complete_continuity_protocol(self):
        prompt = content("automation_200/MASTER_CONTINUITY_PROMPT.md")
        for required in (
            "STANDING USER DIRECTIVE",
            "Source recovery",
            "Canonical project graph",
            "Merge algorithm",
            "Events and decisions",
            "Operational truth",
            "Change-protection",
            "Starting each future run",
            "BOOK",  # project identity must not be erased (case-insensitive)
        ):
            with self.subTest(required=required):
                self.assertIn(required.lower(), prompt.lower())

    def test_no_public_conversation_export_order(self):
        prompt = content("automation_200/MASTER_CONTINUITY_PROMPT.md")
        self.assertIn("never publish raw contents automatically", prompt.lower())
        self.assertIn("private library", prompt.lower())
        self.assertIn("do not claim full review", prompt.lower())

    def test_public_navigation_mentions_continuity(self):
        for path in ("README.md", "docs/CONTINUITY.md", "docs/PROVENANCE.md"):
            with self.subTest(path=path):
                text = content(path)
                self.assertIn("MASTER_OPERATOR_PROMPT.md", text)
                self.assertIn("MASTER_CONTINUITY_PROMPT.md", text)

    def test_preserve_owner_priority_and_broader_goal(self):
        prompt = content("automation_200/MASTER_CONTINUITY_PROMPT.md").lower()
        for required in ("sustainable generational wealth", "automation", "priority",
                         "legitimate income", "book machine", "mushroomhead",
                         "synapse", "single-dot", "original", "37-project", "62-entry"):
            with self.subTest(required=required):
                self.assertIn(required, prompt)

if __name__ == "__main__":
    unittest.main()
