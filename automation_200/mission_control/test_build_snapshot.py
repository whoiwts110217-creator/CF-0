"""Source-level regression tests for the public Mission Control fallback."""
import importlib.util
import json
import pathlib
import tempfile
import unittest

MODULE = pathlib.Path(__file__).with_name("build_snapshot.py")
spec = importlib.util.spec_from_file_location("cf0_snapshot", MODULE)
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        (self.root / "automation_200").mkdir()
        (self.root / "docs").mkdir()
        registry = {
            "schema": "CF200.1", "target": 200, "completed": 1,
            "tasks": [{"status": "verified" if n == 0 else "planned"} for n in range(200)],
        }
        state = {"schema": "cf0.public_continuity.v1", "hp": {}}
        (self.root / "automation_200/registry.json").write_text(json.dumps(registry))
        (self.root / "docs/PUBLIC_CONTINUITY_STATE.json").write_text(json.dumps(state))

    def test_commit_pinned_baseline_and_no_private_sources(self):
        data = snapshot.build(self.root, "a" * 40)
        self.assertEqual(data["registry"]["completed"], 1)
        self.assertEqual(data["health"], "not_published")
        self.assertNotIn("ping", data)
        self.assertEqual(set(data), {"commit", "registry", "state", "health"})

    def test_rejects_invalid_sha_and_count(self):
        with self.assertRaises(ValueError):
            snapshot.build(self.root, "main")
        path = self.root / "automation_200/registry.json"
        data = json.loads(path.read_text())
        data["completed"] = 2
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            snapshot.build(self.root, "a" * 40)

    def test_only_fixed_uuid_receipt_paths_are_read(self):
        path = self.root / "docs/PUBLIC_CONTINUITY_STATE.json"
        state = json.loads(path.read_text())
        state["hp"]["public_ping_request_id"] = "../../private"
        path.write_text(json.dumps(state))
        self.assertNotIn("ping", snapshot.build(self.root, "b" * 40))


if __name__ == "__main__":
    unittest.main()
