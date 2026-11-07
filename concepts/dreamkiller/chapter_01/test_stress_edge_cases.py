"""Adversarial regressions for the Chapter One reference model.

The first test targets a real gap: 'rescue neither' must be a final decision
for that encounter, not permission to choose a new outcome repeatedly.
These are SIMULATOR tests, not Game Boy cartridge execution tests.
"""
import unittest
from stress_reference import ReferenceWorld

class StressAdversarialRegressions(unittest.TestCase):
    def in_archive(self):
        w=ReferenceWorld()
        for direction in ("east", "east", "north", "east", "east"):
            self.assertTrue(w.move(direction))
        self.assertEqual(w.location, "D02")
        self.assertTrue(w.p001_recorded)
        return w

    def test_neither_outcome_cannot_be_rewritten_into_both(self):
        w=self.in_archive()
        self.assertTrue(w.select_rescue("neither"))
        before=len(w.events)
        self.assertFalse(w.select_rescue("both"))
        self.assertEqual(len(w.events),before)
        self.assertEqual(w.escorting,[])
        self.assertTrue(w.move("west"))
        self.assertFalse(w.p001_falsified)

    def test_rescue_decision_cannot_be_repeated_after_save_restore(self):
        w=self.in_archive()
        self.assertTrue(w.select_rescue("neither"))
        saved=ReferenceWorld.restore(w.snapshot())
        self.assertFalse(saved.select_rescue("A_only"))
        self.assertFalse(saved.select_rescue("both"))
        self.assertTrue(saved.move("west"))
        self.assertFalse(saved.p001_falsified)

    def test_single_identity_cannot_be_promoted_to_two_after_selection(self):
        w=self.in_archive()
        self.assertTrue(w.select_rescue("A_only"))
        self.assertFalse(w.select_rescue("B_only"))
        self.assertTrue(w.move("west"))
        self.assertEqual(w.exited,["A"])
        self.assertFalse(w.p001_falsified)
