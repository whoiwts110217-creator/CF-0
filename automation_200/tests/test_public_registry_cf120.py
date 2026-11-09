"""CF-120: full public registry and read-only dashboard publication coverage."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

from automation_200.validate_registry import check_registry, RegistryValidationError
from automation_200.mission_control.build_snapshot import build

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "automation_200/registry.json"
CONTINUITY = ROOT / "docs/PUBLIC_CONTINUITY_STATE.json"
GUIDE = ROOT / "docs/CF200_FULL_REGISTRY.md"


def blob_sha(raw: bytes) -> str:
    raw = raw.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


class FullPublicRegistryTests(unittest.TestCase):
    def test_exactly_200_canonical_ids_with_individual_evidence(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(check_registry(registry)["target"], 200)
        self.assertEqual([t["id"] for t in registry["tasks"]],
                         [f"CF-{n:03d}" for n in range(1, 201)])
        self.assertEqual(registry["completed"],
                         sum(t["status"] == "verified" for t in registry["tasks"]))
        self.assertTrue(all(t.get("title") and t.get("stream")
                            and isinstance(t.get("depends_on"), list)
                            for t in registry["tasks"]))

    def test_public_fingerprint_matches_exact_registry_bytes(self):
        state = json.loads(CONTINUITY.read_text(encoding="utf-8"))
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(state["cf200"]["registry_git_blob_sha1"], blob_sha(REGISTRY.read_bytes()))
        self.assertEqual(state["cf200"]["verified"], registry["completed"])
        self.assertEqual(state["cf200"]["target"], 200)

    def test_mission_control_receives_all_restricted_and_planned_tasks(self):
        data = build(ROOT, "a" * 40)
        tasks = data["registry"]["tasks"]
        self.assertEqual(len(tasks), 200)
        self.assertEqual({t["id"] for t in tasks},
                         {f"CF-{n:03d}" for n in range(1, 201)})
        self.assertTrue(any(t["stream"] == "hp_install" for t in tasks))
        self.assertTrue(any(t.get("physical_hp_required") for t in tasks))
        self.assertTrue(any(t["status"] == "planned" for t in tasks))
        self.assertEqual(data["registry"]["completed"],
                         data["state"]["cf200"]["verified"])
        self.assertNotIn("execution_authorized", data)

    def test_missing_or_duplicate_task_does_not_pass_validation(self):
        source = json.loads(REGISTRY.read_text(encoding="utf-8"))
        missing = copy.deepcopy(source)
        missing["tasks"].pop()
        with self.assertRaises(RegistryValidationError):
            check_registry(missing)
        duplicate = copy.deepcopy(source)
        duplicate["tasks"][-1]["id"] = duplicate["tasks"][-2]["id"]
        with self.assertRaises(RegistryValidationError):
            check_registry(duplicate)

    def test_public_guide_links_canonical_source_and_preserves_boundaries(self):
        guide = GUIDE.read_text(encoding="utf-8")
        self.assertIn("raw.githubusercontent.com/whoiwts110217-creator/CF-0/main/automation_200/registry.json", guide)
        self.assertIn("../automation_200/registry.json", guide)
        self.assertIn("Show restricted", guide)
        self.assertIn("not a second registry", guide)
        self.assertIn("not proof of physical HP operation", guide)
        self.assertNotIn("LOCALAPPDATA", guide)


if __name__ == "__main__":
    unittest.main()
