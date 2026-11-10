"""Universal public-source freshness routing and privacy boundaries."""
import tempfile
import unittest
from pathlib import Path

from continuity.public_freshness import (
    ROOT, audit_catalog, git_blob_sha, latest_public_url,
    safe_public_file, source_freshness, tracked_public_files,
)


class UniversalFreshnessTests(unittest.TestCase):
    def test_every_known_topic_graph_node_has_a_current_source_route(self):
        result = audit_catalog()
        self.assertGreaterEqual(result["catalog_topics"], 29)
        self.assertGreaterEqual(result["public_topic_graph_nodes"], 13)
        self.assertGreaterEqual(result["git_tracked_public_paths"], 100)
        self.assertTrue(result["generic_main_resolver"])
        self.assertFalse(result["private_origins_auto_discovered"])
        self.assertFalse(result["runtime_and_payment_status_attested"])

    def test_any_present_public_source_gets_a_moving_main_link(self):
        url = latest_public_url("docs/OWNER_JUNGLE_MAP.md")
        self.assertEqual(
            url,
            "https://github.com/whoiwts110217-creator/CF-0/"
            "blob/main/docs/OWNER_JUNGLE_MAP.md",
        )
        self.assertIn("docs/PROJECTS.md", tracked_public_files())

    def test_matching_bytes_are_not_mistaken_for_live_execution(self):
        path = "docs/PROJECTS.md"
        blob = git_blob_sha((ROOT / path).read_bytes())
        report = source_freshness(path, blob)
        self.assertEqual(report["snapshot_state"], "same_source_bytes_in_this_checkout")
        self.assertFalse(report["live_operation_proven"])

    def test_stale_snapshot_redirects_to_moving_main(self):
        report = source_freshness("docs/PROJECTS.md", "a" * 40)
        self.assertEqual(report["snapshot_state"], "stale_source_snapshot")
        self.assertIn("/blob/main/docs/PROJECTS.md", report["latest_public_url"])

    def test_unknown_age_never_silently_claims_current(self):
        self.assertEqual(
            source_freshness("docs/PROJECTS.md", None)["snapshot_state"],
            "snapshot_age_unknown",
        )
        self.assertEqual(
            source_freshness("docs/PROJECTS.md", "not-a-sha")["snapshot_state"],
            "unverifiable_snapshot_id",
        )

    def test_invalid_outside_and_missing_paths_fail_closed(self):
        for path in ("", "../private.txt", "/etc/passwd", "docs/../../outside",
                     "http://site.invalid/test", "docs/\\windows", "docs/not-here.txt"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                latest_public_url(path)

    def test_symlink_is_not_presented_as_a_normal_public_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "original.txt").write_text("test", encoding="utf-8")
            link = root / "shortcut.txt"
            link.symlink_to(root / "original.txt")
            with self.assertRaisesRegex(ValueError, "SYMLINK"):
                safe_public_file("shortcut.txt", root)

    def test_synthetic_file_change_is_detected_without_external_network(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "source.md"
            src.write_text("old", encoding="utf-8")
            old_blob = git_blob_sha(src.read_bytes())
            self.assertEqual(source_freshness("source.md", old_blob, root)["snapshot_state"],
                             "same_source_bytes_in_this_checkout")
            src.write_text("new", encoding="utf-8")
            self.assertEqual(source_freshness("source.md", old_blob, root)["snapshot_state"],
                             "stale_source_snapshot")

    def test_catalog_never_elevates_private_archives_into_public_sources(self):
        import json
        catalog = json.loads((ROOT / "docs/FRESHNESS_CATALOG.json").read_text(encoding="utf-8"))
        private = [e for e in catalog["entries"]
                   if e["source_type"] == "private_originals_not_published"]
        self.assertGreaterEqual(len(private), 4)
        for entry in private:
            self.assertTrue(entry["public_anchor"].startswith("docs/"))
            self.assertNotIn("private_path", entry)
            self.assertEqual(entry["status_origin"], "read_on_demand")


    def test_all_owner_entrypoints_link_old_sources_to_current_gateway(self):
        routes = {
            "README.md": "docs/CURRENT_SOURCE_GATEWAY.md",
            "docs/OWNER_JUNGLE_MAP.md": "CURRENT_SOURCE_GATEWAY.md",
            "docs/PROJECTS.md": "CURRENT_SOURCE_GATEWAY.md",
            "docs/START_HERE.md": "CURRENT_SOURCE_GATEWAY.md",
            "docs/PROJECT_STATUS.md": "CURRENT_SOURCE_GATEWAY.md",
            "docs/mesh/START_HERE.md": "../CURRENT_SOURCE_GATEWAY.md",
            "docs/UNIVERSAL_CONTINUITY_CONTRACT.md": "CURRENT_SOURCE_GATEWAY.md",
            "automation_200/mission_control/dist/index.html": "/blob/main/docs/CURRENT_SOURCE_GATEWAY.md",
        }
        for path, expected in routes.items():
            with self.subTest(path=path):
                content = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn(expected, content)
        gateway = (ROOT / "docs/CURRENT_SOURCE_GATEWAY.md").read_text(encoding="utf-8")
        self.assertIn("https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/CURRENT_SOURCE_GATEWAY.md", gateway)
        self.assertIn("Mission Control", gateway)
        self.assertIn("private", gateway.lower())

    def test_contract_does_not_install_a_scheduled_status_collector(self):
        source = (ROOT / "docs/UNIVERSAL_FRESHNESS_CONTRACT.md").read_text(encoding="utf-8")
        self.assertIn("No new scheduler", source)
        self.assertIn("A source", source)
        self.assertIn("EVERY", source)


if __name__ == "__main__":
    unittest.main()
