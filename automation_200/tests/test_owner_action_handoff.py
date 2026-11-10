"""Public-source-only owner-action contract regression checks (no account or HP access)."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = (
    "automation_200/MASTER_OPERATOR_PROMPT.md",
    "automation_200/MASTER_CONTINUITY_PROMPT.md",
    "automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md",
)

class OwnerActionHandoffTests(unittest.TestCase):
    def test_canonical_prompts_and_bootstrap_link_one_contract(self):
        for path in (*PROMPTS, "docs/CHATGPT_MEMORY_BOOTSTRAP.md",
                     "docs/PUBLIC_THREE_CHAT_CONTINUITY_MESH.md"):
            with self.subTest(path=path):
                self.assertIn("OWNER_ACTION_HANDOFF_PROTOCOL.md",
                              (ROOT / path).read_text(encoding="utf-8"))

    def test_action_contract_has_clear_gates_evidence_and_safety(self):
        content = (ROOT / "docs/OWNER_ACTION_HANDOFF_PROTOCOL.md").read_text(
            encoding="utf-8")
        for term in ("NONE", "OPTIONAL", "REQUIRED_BEFORE_GATE",
                     "REQUIRED_NOW", "UNSAFE_OR_UNSUPPORTED",
                     "ACTION REQUIRED", "Success looks like:",
                     "How we verify:", "Rollback:",
                     "never ask the owner to paste passwords"):
            with self.subTest(term=term):
                self.assertIn(term.lower(), content.lower())

    def test_graph_references_existing_contract_and_dependencies(self):
        data = json.loads((ROOT / "docs/PUBLIC_CONTEXT_GRAPH.json").read_text(
            encoding="utf-8"))
        nodes = {n["id"]: n for n in data["nodes"]}
        node = nodes["CF-OWNER-HANDOFF-001"]
        self.assertEqual(node["parent"], "CF-MESH-001")
        self.assertIn("UCC-001", node["depends_on"])
        self.assertTrue((ROOT / node["source"]).is_file())
        self.assertIn(node["id"], nodes["CF-MESH-001"]["related"])

if __name__ == "__main__":
    unittest.main()
