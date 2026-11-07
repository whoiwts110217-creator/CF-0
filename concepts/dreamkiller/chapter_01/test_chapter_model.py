"""Dreamkiller Chapter One source-level consistency tests.

These validate proposed records, NOT Game Boy hardware/emulator or actual gameplay.
"""
import itertools
import json
import unittest
from pathlib import Path

DATA = json.loads(Path(__file__).with_name("BRANCH_AND_GLITCH_MODEL.json").read_text(encoding="utf-8"))
MAP = {node["id"]: node for node in DATA["locations"]}

def reachable(start):
    seen = {start}
    todo = [start]
    while todo:
        node = todo.pop()
        for destination in MAP[node]["exits"].values():
            if destination not in seen:
                seen.add(destination)
                todo.append(destination)
    return seen

class DreamkillerChapterOneDesignTests(unittest.TestCase):
    def test_credit_and_scope(self):
        self.assertEqual(DATA["creator"], "David Smith")
        self.assertEqual(DATA["designated_owner"], "Kiara Lynn Rose Smith")
        self.assertFalse(DATA["rom_implemented"])
        self.assertFalse(DATA["emulator_gameplay_verified"])

    def test_unique_entities_and_locations(self):
        self.assertEqual(len(MAP), len(DATA["locations"]))
        self.assertEqual(len(DATA["entity_ids"]), len(set(DATA["entity_ids"])))

    def test_all_exits_have_known_targets(self):
        for node in DATA["locations"]:
            for direction, dest in node["exits"].items():
                with self.subTest(place=node["id"], direction=direction):
                    self.assertIn(dest, MAP)

    def test_every_place_can_eventually_return_to_town(self):
        for place in MAP:
            with self.subTest(place=place):
                self.assertIn("S02", reachable(place))

    def test_two_alternative_approaches_to_dungeon(self):
        self.assertEqual(MAP["D00"]["exits"]["east"], "D01")
        self.assertEqual(MAP["W01"]["exits"]["east"], "D01")

    def test_glitch_is_forced_and_not_quest_gated(self):
        g = DATA["glitch_B001"]
        self.assertEqual(g["id"], "B-001")
        self.assertFalse(g["requires_quest"])
        self.assertFalse(g["uses_rng"])
        self.assertFalse(g["requires_undefined_behavior"])
        for answer in DATA["branches"]["pip"]:
            with self.subTest(pip=answer):
                self.assertEqual(MAP[g["from"]]["exits"][g["direction"]], g["destination"])

    def test_shared_sign_object_is_not_duplicated(self):
        self.assertEqual(MAP["S01"]["sign_object_id"], "OBJ_SIGN_037")
        self.assertEqual(MAP["E01"]["sign_object_id"], "OBJ_SIGN_037")
        self.assertEqual(DATA["glitch_B001"]["sign_object_id"], "OBJ_SIGN_037")

    def test_atlas_claim_is_distinct_from_observation(self):
        claim = DATA["recorded_atlas_claim"]
        self.assertEqual(claim["from"], DATA["glitch_B001"]["from"])
        self.assertEqual(claim["direction"], DATA["glitch_B001"]["direction"])
        self.assertNotEqual(claim["destination"], DATA["glitch_B001"]["destination"])
        self.assertEqual(claim["status"], "fallible_map_claim")

    def test_prediction_requires_independent_record(self):
        pred = DATA["prediction_P001"]
        self.assertEqual(pred["kind"], "fallible_machine_prediction")
        self.assertTrue(pred["must_be_recorded_before_rescue"])
        self.assertIn("NPC_CAIRN_A", DATA["entity_ids"])
        self.assertIn("NPC_CAIRN_B", DATA["entity_ids"])

    def test_observation_and_interpretation_are_different_fields(self):
        f = set(DATA["journal_fields"])
        self.assertTrue({"event_id", "world_tick", "conditions", "observation", "interpretation"}.issubset(f))

    def test_branch_combinations_cannot_softlock_geography(self):
        choices = itertools.product(*DATA["branches"].values())
        scenarios = 0
        for values in choices:
            scenarios += 1
            with self.subTest(choices=values):
                self.assertIn("S02", reachable("D02"))
                self.assertEqual(MAP["S01"]["exits"]["east"], "E01")
        self.assertEqual(scenarios, 72)

if __name__ == "__main__":
    unittest.main()
