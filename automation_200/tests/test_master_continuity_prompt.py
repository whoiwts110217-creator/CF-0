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

    def test_public_work_self_reference_and_preflight_order(self):
        """A public prompt exists; this test does not establish Work compliance."""
        work = content("automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md")
        url = ("https://github.com/whoiwts110217-creator/CF-0/blob/main/"
               "automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md")
        self.assertIn(url, work)
        self.assertIn("THEN FETCH AND READ THIS VERY FILE FROM PUBLIC GITHUB", work)
        first = work.index("MASTER_OPERATOR_PROMPT.md")
        second = work.index("MASTER_CONTINUITY_PROMPT.md")
        third = work.index("THEN FETCH AND READ THIS VERY FILE FROM PUBLIC GITHUB")
        self.assertLess(first, second)
        self.assertLess(second, third)
        self.assertIn("Do not require the owner to re-paste this prompt", work)
        self.assertIn("A prompt cannot initiate or schedule itself", work)

    def test_work_prompt_preserves_hp_and_privacy_boundaries(self):
        work = content("automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md")
        for action in ("ping", "hp_status", "sidecar_verify"):
            self.assertIn(action, work)
        for phrase in (
            "No remote shell",
            "Private v1/v2 archives remain private",
            "not proof of scheduled HP execution",
            "Do not add duplicate schedulers",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), work.lower())

    def test_preserve_owner_priority_and_broader_goal(self):
        prompt = content("automation_200/MASTER_CONTINUITY_PROMPT.md").lower()
        for required in ("sustainable generational wealth", "automation", "priority",
                         "legitimate income", "book machine", "mushroomhead",
                         "synapse", "single-dot", "original", "37-project", "62-entry"):
            with self.subTest(required=required):
                self.assertIn(required, prompt)

if __name__ == "__main__":
    unittest.main()
