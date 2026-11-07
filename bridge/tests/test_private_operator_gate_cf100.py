"""CF-100: design-only authorization gates remain explicit and inoperative.

No private repo, credential, local computer, external request or scheduler
is created or contacted by these tests.
"""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = ROOT / "bridge/PRIVATE_OPERATOR_GATE_CF100.md"
PRIVATE_WORKER = ROOT / "bridge/cf_hp_bridge.py"
PUBLIC_WORKER = ROOT / "relay/cf_public_relay.py"


def constant_assignment(path, target):
    source = ast.parse(path.read_text(encoding="utf-8"))
    for node in source.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == target for t in node.targets):
            return ast.literal_eval(node.value)
    return None


class PrivateOperatorDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DOC.read_text(encoding="utf-8")

    def test_no_new_action_is_activated(self):
        self.assertEqual(constant_assignment(PRIVATE_WORKER, "ALLOWED_ACTIONS"),
                         {"ping", "sidecar_verify"})
        self.assertIn("DESIGN ONLY", self.text)
        self.assertIn("not approved", self.text)
        self.assertIn("do not activate", self.text.lower())

    def test_owner_local_approval_is_a_separate_gate(self):
        for fragment in ("PCA-004", "explicit owner-local opt-in",
                         "manifest_sha256", "approval_id", "revocation",
                         "separate physical HP opt-in", "current manifest"):
            self.assertIn(fragment.lower(), self.text.lower())

    def test_security_boundaries_not_assumed_implemented(self):
        for fragment in ("PRIVATE", "Default deny", "no wildcard",
                         "fail-closed", "uncertain", "local", "rollback",
                         "private-vNext rehearsal", "unverified",
                         "no general command interpreter"):
            self.assertIn(fragment.lower(), self.text.lower())
        self.assertIn("not implemented", self.text.lower())

    def test_original_public_allowlist_untouched(self):
        body = PUBLIC_WORKER.read_text(encoding="utf-8")
        self.assertIn("ALLOWED = frozenset(('ping', 'hp_status', 'sidecar_verify'))", body)
        self.assertIn("existing allowlisted public", self.text)

    def test_reviewer_can_find_existing_operator_and_evidence_contracts(self):
        self.assertIn("../automation_200/PROMPT_CHANGE_BIN.md", self.text)
        self.assertIn("../automation_200/OWNER_CAPABILITY_CONTRACT.json", self.text)
        self.assertIn("../relay/URGENT_STOP_AND_RESUME.md", self.text)
        self.assertIn("No gate is auto-approved", self.text)


if __name__ == "__main__":
    unittest.main()
