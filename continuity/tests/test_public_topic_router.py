"""Source-only tests for CF-MESH-001 public topic routing."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from continuity.public_topic_router import (
    BOOT, GRAPH_PATH, ROOT, GraphError, route_topic, validate_graph,
)


def graph():
    return json.loads(GRAPH_PATH.read_text(encoding="utf-8"))


class PublicTopicRouterTests(unittest.TestCase):
    def test_real_public_graph_and_source_paths(self):
        data = graph()
        nodes = validate_graph(data, root=ROOT)
        self.assertGreaterEqual(len(nodes), 10)
        self.assertIn("CF-MESH-001", nodes)
        self.assertIn("CF-200", nodes)

    def test_cold_start_does_not_switch_topic(self):
        out = route_topic(graph(), "spiderweb", root=ROOT)
        self.assertEqual(out["selected_topic"], "CF-MESH-001")
        self.assertTrue(out["focus_preserved"])
        self.assertFalse(out["execution_authorized"])
        self.assertEqual(out["read_order"][:3], BOOT)
        self.assertIn("docs/PUBLIC_THREE_CHAT_CONTINUITY_MESH.md", out["read_order"])
        self.assertIn("CF-200", [x["id"] for x in out["related_context_only"]])
        self.assertIn("UCC-001", [x["id"] for x in out["related_context_only"]])

    def test_related_topic_cannot_take_over(self):
        out = route_topic(graph(), "AUTO-08", root=ROOT)
        self.assertEqual(out["selected_topic"], "AUTO-08")
        self.assertIn("CF-MESH-001", [x["id"] for x in out["related_context_only"]])
        self.assertNotEqual(out["selected_topic"], out["related_context_only"][0]["id"])

    def test_alias_normalization_and_determinism(self):
        a = route_topic(graph(), "  THREE   CHATS  ")
        b = route_topic(graph(), "CF-MESH-001")
        self.assertEqual(a, b)
        self.assertEqual(route_topic(graph(), "Dreamkiller")["selected_topic"],
                         "CF-CONCEPT-DREAMKILLER-001")

    def test_limit_zero_and_dependent_inbound_link(self):
        out = route_topic(graph(), "UCC-001", limit=0)
        self.assertEqual(out["related_context_only"], [])
        out = route_topic(graph(), "UCC-001", limit=32)
        self.assertIn("AUTO-08", [x["id"] for x in out["related_context_only"]])

    def test_unknown_topic_fails_closed(self):
        with self.assertRaisesRegex(GraphError, "unknown_or_ambiguous_topic"):
            route_topic(graph(), "some old private chat")
        with self.assertRaisesRegex(GraphError, "invalid_neighbor_limit"):
            route_topic(graph(), "CF-MESH-001", limit=1000)

    def test_missing_dependency_fails_closed(self):
        data = graph()
        data["nodes"][2]["related"].append("MISSING_PROJECT")
        with self.assertRaisesRegex(GraphError, "missing_or_self_referential_node_link"):
            validate_graph(data)

    def test_parent_cycle_fails_closed(self):
        data = graph()
        data["nodes"][0]["parent"] = "CF-MESH-001"
        with self.assertRaisesRegex(GraphError, "cycle_in_parent_or_dependency_links"):
            validate_graph(data)

    def test_ambiguous_alias_fails_closed(self):
        data = graph()
        data["nodes"][1]["aliases"].append("spiderweb")
        with self.assertRaisesRegex(GraphError, "ambiguous_topic_alias"):
            validate_graph(data)

    def test_unsafe_file_path_fails_closed(self):
        for bad in ("../secret.json", "/tmp/private.md", "docs/../../secret.json", "docs/hidden.txt"):
            data = graph()
            data["nodes"][0]["source"] = bad
            with self.subTest(path=bad), self.assertRaises(GraphError):
                validate_graph(data)

    def test_boot_order_is_not_silently_changed(self):
        data = graph()
        data["boot_sources"].reverse()
        with self.assertRaisesRegex(GraphError, "boot_sequence_changed"):
            validate_graph(data)

    def test_missing_source_detected(self):
        data = graph()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in BOOT:
                f = root / path
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text("test", encoding="utf-8")
            with self.assertRaisesRegex(GraphError, "missing_public_source"):
                validate_graph(data, root=root)

    def test_read_only_no_undocumented_mutation(self):
        before = GRAPH_PATH.read_bytes()
        data = graph()
        original = copy.deepcopy(data)
        route_topic(data, "CF-MESH-001", root=ROOT)
        self.assertEqual(data, original)
        self.assertEqual(GRAPH_PATH.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
