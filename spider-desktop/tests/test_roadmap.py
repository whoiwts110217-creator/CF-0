"""CF-SPIDER-001: verify the standalone Spider capability graph without external packages."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "ARCHITECTURE.md"
GRAPH = ROOT / "ROADMAP.json"

class TestSpiderRoadmap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(GRAPH.read_text(encoding="utf-8"))
        cls.docs = DOC.read_text(encoding="utf-8")
        cls.nodes = cls.data["nodes"]
        cls.by_id = {n["id"]: n for n in cls.nodes}

    def test_schema_identity_and_prior_release_are_honest(self):
        g = self.data
        self.assertEqual(g["schema"], "cf0.spider.architecture_graph.v1")
        self.assertEqual(g["project_id"], "CF-SPIDER-001")
        self.assertTrue(g["classification"].startswith("public-safe"))
        b = g["source_baseline"]
        self.assertFalse(b["physical_hp_tested"])
        self.assertFalse(b["real_chatgpt_tested"])
        self.assertFalse(b["cloud_model_bundled"])
        self.assertEqual(len(b["sha256"]), 64)

    def test_distinct_usable_capability_records(self):
        self.assertGreaterEqual(len(self.nodes), 18)
        self.assertEqual(len(self.nodes), len(self.by_id))
        statuses = set(self.data["capability_statuses"])
        for n in self.nodes:
            self.assertRegex(n["id"], r"^SPDR-[0-9]{2}$")
            self.assertIn(n["status"], statuses)
            self.assertGreaterEqual(len(n["purpose"]), 24)
            self.assertGreaterEqual(len(n["acceptance"]), 20)
            self.assertIsInstance(n["depends_on"], list)
            self.assertEqual(len(n["depends_on"]), len(set(n["depends_on"])))
            self.assertNotIn(n["id"], n["depends_on"])

    def test_dependencies_exist_and_graph_acyclic(self):
        seen = {}
        def visit(task_id):
            state = seen.get(task_id, 0)
            self.assertNotEqual(state, 1, "capability dependency cycle: " + task_id)
            if state == 2:
                return
            seen[task_id] = 1
            for dep in self.by_id[task_id]["depends_on"]:
                self.assertIn(dep, self.by_id, "unknown dependency: " + dep)
                visit(dep)
            seen[task_id] = 2
        for key in self.by_id:
            visit(key)

    def test_phases_reference_existing_capabilities(self):
        phases = self.data["phases"]
        self.assertEqual([p["id"] for p in phases], [f"P{i}" for i in range(8)])
        for phase in phases:
            self.assertGreaterEqual(len(phase["acceptance"]), 24)
            self.assertTrue(phase["capability_ids"])
            for item in phase["capability_ids"]:
                self.assertIn(item, self.by_id)

    def test_no_false_authority_or_external_cost(self):
        rules = self.data["rules"]
        self.assertIn("approved", rules["agent_spawn"])
        self.assertIn("parent permissions", rules["agent_spawn"])
        self.assertIn("send_submitted", rules["no_false_results"])
        self.assertIn("AUTO-08", rules["one_browser_writer"])
        self.assertIn("no-cost", self.data["constraints"]["budget"])
        self.assertIn("STOP", self.docs)
        self.assertIn("Skill Forge", self.docs)
        self.assertIn("Mouse", self.docs)
        self.assertIn("PowerShell", self.docs)
        self.assertIn("Python", self.docs)
        self.assertIn("Google", self.docs)
        self.assertIn("~~~mermaid", self.docs)
        for node in self.nodes:
            self.assertIn(node["id"][:4], self.docs)

if __name__ == "__main__":
    unittest.main()
