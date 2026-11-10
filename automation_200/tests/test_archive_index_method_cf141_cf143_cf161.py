"""CF-141/142/143/161 public archive/method acceptance (source-only).

These assertions protect traceable public navigation and provenance boundaries.
They cannot attest the HP, private-original recovery, income, or RH proof.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "docs" / "PROJECTS.md"
RULEBOOK = ROOT / "CAVEMAN_FOCUS_RULEBOOK_v0.1.md"


class ArchiveIndexMethodAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = INDEX.read_text(encoding="utf-8")
        cls.rulebook = RULEBOOK.read_text(encoding="utf-8")

    def test_cf141_public_master_index_covers_distinct_domains(self):
        for marker in (
            "### Operating system and continuity",
            "### Science, philosophy and inventions",
            "### Stories, worlds and games",
            "### Business, delivery and funding",
            "## CF-200 archive and method acceptance map",
            "Single-Dot Universe Book I",
            "Mushroomhead",
            "Domino Sidecar",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.index)
        self.assertTrue(INDEX.is_file())

    def test_cf142_unrecovered_original_gap_not_silently_closed(self):
        for marker in (
            "17 named older rows",
            "18-entry reference",
            "approximately 37-project list",
            "62-entry reconstructed atlas",
            "not recovered",
            "secondary_reconstruction",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.index)

    def test_cf143_source_grades_have_specific_linked_examples(self):
        for grade in (
            "`public_source_present`",
            "`secondary_reconstruction`",
            "`private_primary_source_not_published`",
            "`hypothesis_or_experiment`",
            "`public_receipt_matched__origin_unverified`",
            "`public_source_and_limited_tests`",
        ):
            with self.subTest(grade=grade):
                self.assertIn(grade, self.index)
        for relative in (
            "docs/CONTINUITY.md",
            "docs/SOURCE_TRUTH_RECONSTRUCTION_PROTOCOL.md",
            "docs/UNIVERSAL_CONTINUITY_CONTRACT.md",
            "docs/RESEARCH.md",
            "concepts/dreamkiller/rom_v0_2/README.md",
        ):
            with self.subTest(source=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)
        self.assertIn("No private transcripts, credentials", self.index)
        self.assertIn("not a verified payment", self.index)

    def test_cf161_guess_hypothesis_evidence_proof_preserved_without_overclaim(self):
        method = "guess → hypothesis → evidence → proof"
        self.assertIn(method, self.rulebook)
        self.assertIn(method, self.index)
        self.assertIn("A method definition is not proof", self.index)
        self.assertIn("Label uncertainty", self.rulebook)


if __name__ == "__main__":
    unittest.main()
