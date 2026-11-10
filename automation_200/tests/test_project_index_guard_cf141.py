"""CF-141: public index paths and archive-honesty regression tests."""
import unittest

from automation_200.project_index_guard import ROOT, INDEX, check_index

SOURCE = (ROOT / INDEX).read_text(encoding="utf-8")


class ProjectIndexCF141Tests(unittest.TestCase):
    def test_published_index_has_valid_local_links_and_truthful_archive_gap(self):
        result = check_index()
        self.assertEqual(result["schema"], "cf0.project_index_guard.v1")
        self.assertGreaterEqual(result["links_checked"], 25)
        self.assertEqual(result["archive_completeness"], "unverified")
        self.assertFalse(result["installed_extension_verified"])
        self.assertFalse(result["hp_identity_attested"])

    def test_broken_link_is_not_mistaken_for_publicly_available_source(self):
        broken = SOURCE + "\n[bad local reference](MISSING_CF141_FILE.md)\n"
        with self.assertRaisesRegex(ValueError, "BROKEN_PROJECT_LINK"):
            check_index(source=broken)

    def test_repository_escape_is_denied(self):
        broken = SOURCE + "\n[outside repo](../../../../untrusted.txt)\n"
        with self.assertRaisesRegex(ValueError, "UNSAFE_PROJECT_LINK"):
            check_index(source=broken)

    def test_escaped_newline_or_lost_workstream_fails(self):
        with self.assertRaisesRegex(ValueError, "LITERAL_ESCAPED_NEWLINES"):
            check_index(source=SOURCE + r"\n\n")
        with self.assertRaisesRegex(ValueError, "MISSING_PROJECT_WORKSTREAM"):
            check_index(source=SOURCE.replace("AUTO-08", "not-auto08"))

    def test_original_37_and_reconstructed_62_stay_distinct(self):
        with self.assertRaisesRegex(ValueError, "ORIGINAL_PROJECT_GAP_MISSING"):
            check_index(source=SOURCE.replace("37 projects", "37 projects recovered"))
        with self.assertRaisesRegex(ValueError, "RECONSTRUCTION_GAP_MISSING"):
            check_index(source=SOURCE.replace("62-entry reconstruction", "uncited inventory"))

    def test_no_network_or_private_transcript_access_is_necessary(self):
        self.assertTrue((ROOT / INDEX).is_file())
        self.assertNotIn("private transcript dump", SOURCE.lower())


if __name__ == "__main__":
    unittest.main()
