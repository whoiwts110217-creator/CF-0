#!/usr/bin/env python3
"""Dreamkiller Chapter 1 stress reference v0.1.

This is a deterministic, inspectable MODEL SIMULATOR, not a Game Boy ROM.
It reads the original Chapter 1 design JSON unchanged. Missing production
rules are represented by explicit test-only hypotheses, never by claims
that the game implements them.

Run: python -m unittest discover -s . -p 'test_*.py'
Or: python stress_reference.py  (prints an evidence-graded design audit).
"""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
import random
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL = json.loads((HERE / "BRANCH_AND_GLITCH_MODEL.json").read_text(encoding="utf-8"))
MAP = {loc["id"]: loc for loc in MODEL["locations"]}
BRANCHES = MODEL["branches"]

# These are TEST HYPOTHESES where the master design is not yet precise:
# The town entrance is closed during phases 2/3 of a four-action cycle.
# The closed gate applies symmetrically and can be bypassed by the two
# documented alternate cave routes. Blocked attempts advance one tick.
# Mill/nursery water shares sum to 2; supply changes take 3 world ticks.
# If unharvested and undisturbed, fruit falls at tick 20, decomposes at
# tick 40 and supports one seedling at tick 60 under suitable soil conditions.
# These numbers are NOT yet owner-approved canon or ROM mechanics.
GATE_EDGES = {("S02", "south", "D01"), ("D01", "south", "S02")}
PHASES_OPEN = {0, 1}
GATE_PERIOD = 4
WATER_SHARES = {"unchanged": (1, 1), "surface": (2, 0), "underdeep": (0, 2)}
FRUIT_THRESHOLDS = (20, 40, 60)
MAX_SAVE_EVENTS = None  # reference is unbounded; cartridge storage remains unspecified

def issues_in_source_model(model=MODEL):
    """Real gaps in the source JSON, not bugs falsely blamed on a ROM."""
    issues = []
    if "conditional_exits" not in model and "conditional_gates" not in model:
        issues.append("SPEC-001 cave entrance phase has no executable gate rule")
    if not {"save_schema", "event_storage"}.intersection(model):
        issues.append("SPEC-002 no bounded event journal/save encoding or overflow policy")
    if "economy" not in model and "water_budget" not in model:
        issues.append("SPEC-003 no quantified water transfer, lag or price mechanics")
    if "fruit_lifecycle" not in model:
        issues.append("SPEC-004 fruit/seed lifecycle lacks exact event conditions")
    if "cairn_identity_rule" not in model:
        issues.append("SPEC-005 P-001 quantifier/identity definition remains ambiguous")
    if "DK-000" not in str(model):
        issues.append("SPEC-006 true ending has no executable transition in chapter model")
    if model.get("rom_implemented") is False:
        issues.append("TECH-001 no working Dreamkiller ROM, only an emulator diagnostic")
    return issues

def reachability(map_data=MAP, disabled_edges=()):
    blocked = set(disabled_edges)
    result = {}
    for start in map_data:
        seen = {start}
        todo = [start]
        while todo:
            at = todo.pop()
            for direction, dest in map_data[at]["exits"].items():
                if (at, direction, dest) not in blocked and dest not in seen:
                    seen.add(dest)
                    todo.append(dest)
        result[start] = seen
    return result

def audit_contract(model=MODEL):
    """Return detected mutations and structural gaps."""
    errors = []
    places = {loc["id"]: loc for loc in model["locations"]}
    if len(places) != len(model["locations"]):
        errors.append("DUPLICATE_LOCATION_ID")
    for loc in model["locations"]:
        for direction, target in loc["exits"].items():
            if target not in places:
                errors.append("DANGLING_EXIT")
    g = model["glitch_B001"]
    if places[g["from"]]["exits"].get(g["direction"]) != g["destination"]:
        errors.append("B001_NO_LONGER_DETERMINISTIC")
    if places.get("S01", {}).get("sign_object_id") != places.get("E01", {}).get("sign_object_id"):
        errors.append("SIGN_IDENTITY_FORK")
    if "S02" in places and all(t in places for t in (x["id"] for x in model["locations"])):
        try:
            if any("S02" not in v for v in reachability(places).values()):
                errors.append("UNRECOVERABLE_LOCATION")
        except KeyError:
            errors.append("DANGLING_EXIT")
    if model["creator"] != "David Smith":
        errors.append("WRONG_CREATOR")
    return sorted(set(errors))

class ReferenceWorld:
    """A deliberately minimal executable specification used ONLY for stress testing."""

    def __init__(self, seed=0):
        self.seed = seed
        self.location = "S00"
        self.tick = 0
        self.events = []
        self.sign_marked = False
        self.chalk = 1
        self.pip = "not_decided"
        self.fruit = "attached"
        self.seedlings = 0
        self.sluice = "unchanged"
        self.sluice_tick = None
        self.water = WATER_SHARES["unchanged"]
        self.escorting = []
        self.exited = []
        self.p001_recorded = False
        self.p001_falsified = False
        self.road_repaired = False
        self.b001_count = 0

    def record(self, kind, **fields):
        self.events.append({"id": len(self.events) + 1, "world_tick": self.tick,
                            "kind": kind, **fields})

    def _update_world(self):
        if self.fruit == "attached" and self.tick >= FRUIT_THRESHOLDS[0]:
            self.fruit = "fallen"
            self.record("fruit_fell", object_id="OBJ_FRUIT_001")
        if self.fruit == "fallen" and self.tick >= FRUIT_THRESHOLDS[1]:
            self.fruit = "decomposed"
            self.record("fruit_decomposed", object_id="OBJ_FRUIT_001")
        if self.fruit == "decomposed" and self.tick >= FRUIT_THRESHOLDS[2]:
            self.fruit = "seedling"
            self.seedlings = 1
            self.record("seedling_emerged", source="OBJ_FRUIT_001", object_id="OBJ_SEED_001")
        if self.sluice_tick is not None and self.tick >= self.sluice_tick + 3:
            target = WATER_SHARES[self.sluice]
            if self.water != target:
                self.water = target
                self.record("water_delivery", mill=target[0], nursery=target[1],
                            source="archive_sluice", total=sum(target))

    def step(self, count=1):
        if not isinstance(count, int) or count < 0:
            raise ValueError("invalid step count")
        for _ in range(count):
            self.tick += 1
            self._update_world()

    def move(self, direction):
        source = self.location
        target = MAP[source]["exits"].get(direction)
        if target is None:
            return False
        if (source, direction, target) in GATE_EDGES and self.tick % GATE_PERIOD not in PHASES_OPEN:
            phase = self.tick % GATE_PERIOD
            self.step()
            self.record("cave_gate_blocked", source=source, direction=direction, phase=phase)
            return False
        if self.road_repaired and source == "S01" and direction == "east":
            target = "S02"
        self.location = target
        self.step()
        self.record("travel", source=source, direction=direction, destination=target)
        if source == "S01" and direction == "east" and not self.road_repaired:
            self.b001_count += 1
            self.record("B-001", atlas_claim="S02", observed="E01",
                        sign_mark=self.sign_marked, conditions={"from":"S01","action":"east"})
        if target == "D02" and not self.p001_recorded:
            self.p001_recorded = True
            self.record("P-001", prediction="ONE CAIRN MAY EXIT THE ARCHIVE",
                        authority="fallible_Continuum_model")
        if source == "D02" and direction == "west" and self.escorting:
            if not self.p001_recorded:
                raise AssertionError("unrecorded P-001 before rescue")
            names = sorted(self.escorting)
            self.exited = names
            self.escorting = []
            self.record("cairn_archive_exit", individuals=names)
            if names == ["A", "B"]:
                self.p001_falsified = True
                self.record("P-001_falsified", individuals=names, observed_count=2,
                            note="falsifies an explicit machine prediction, not logic")
        return True

    def mark_sign(self):
        if self.location not in ("S01", "E01") or not self.chalk or self.sign_marked:
            return False
        self.chalk -= 1
        self.sign_marked = True
        self.step()
        self.record("sign_marked", object_id="OBJ_SIGN_037", remaining_chalk=self.chalk)
        return True

    def choose_pip(self, answer):
        if answer not in BRANCHES["pip"] or self.pip != "not_decided":
            return False
        self.pip = answer
        self.step()
        self.record("pip_decision", decision=answer, relation_id="NPC_PIP")
        return True

    def harvest_fruit(self):
        if self.location != "S00" or self.fruit != "attached":
            return False
        self.fruit = "carried"
        self.step()
        self.record("fruit_harvested", object_id="OBJ_FRUIT_001")
        return True

    def set_sluice(self, route):
        if self.location != "D02" or route not in BRANCHES["sluice"]:
            return False
        self.sluice = route
        self.step()
        self.sluice_tick = self.tick
        self.record("watergate_set", route=route)
        return True

    def select_rescue(self, outcome):
        if self.location != "D02" or not self.p001_recorded or outcome not in BRANCHES["rescue"]:
            return False
        if self.escorting or self.exited:
            return False
        escorts = {"A_only": ["A"], "B_only": ["B"], "both": ["A", "B"], "neither": []}[outcome]
        self.escorting = escorts
        self.step()
        self.record("rescue_choice", choice=outcome, escorts=list(escorts))
        return True

    def repair_road_in_future(self, stage=3):
        """Counterfactual Act III fixture; not available in Chapter One play."""
        if stage < 3 or self.road_repaired:
            return False
        self.road_repaired = True
        self.step()
        self.record("road_repaired", reason="future_Act_III_fixture", prior_B001=self.b001_count)
        return True

    def validate(self):
        assert self.chalk in (0, 1)
        assert self.seedlings in (0, 1)
        assert self.fruit in ("attached", "fallen", "decomposed", "seedling", "carried")
        assert self.seedlings == (1 if self.fruit == "seedling" else 0)
        assert sum(self.water) == 2, "water created or destroyed by diversion"
        assert self.location in MAP
        assert [e["id"] for e in self.events] == list(range(1, len(self.events) + 1))
        assert all(a["world_tick"] <= b["world_tick"] for a,b in zip(self.events, self.events[1:]))
        assert all(e["world_tick"] <= self.tick for e in self.events)
        assert (not self.exited or self.p001_recorded)
        assert (not self.p001_falsified or self.exited == ["A", "B"])
        if self.sign_marked:
            assert any(e["kind"] == "sign_marked" and e["object_id"] == "OBJ_SIGN_037" for e in self.events)
        if self.fruit == "carried":
            assert any(e["kind"] == "fruit_harvested" for e in self.events)

    def snapshot(self):
        data = {k: copy.deepcopy(v) for k,v in vars(self).items()}
        payload = json.dumps(data, sort_keys=True, separators=(",",":"))
        checksum = hashlib.sha256(payload.encode()).hexdigest()
        return json.dumps({"schema":"dk_stress_reference_save_v1","payload":data,"sha256":checksum},
                          sort_keys=True, separators=(",",":"))

    @classmethod
    def restore(cls, snapshot):
        outer = json.loads(snapshot)
        if outer.get("schema") != "dk_stress_reference_save_v1":
            raise ValueError("unknown reference state format")
        data = outer["payload"]
        raw = json.dumps(data, sort_keys=True, separators=(",",":"))
        if hashlib.sha256(raw.encode()).hexdigest() != outer["sha256"]:
            raise ValueError("reference state checksum mismatch")
        obj = cls()
        for key,value in data.items():
            setattr(obj,key,value)
        obj.validate()
        return obj

class StressReferenceTests(unittest.TestCase):
    def test_source_structure_as_published(self):
        self.assertEqual(audit_contract(), [])
        self.assertEqual(MODEL["creator"], "David Smith")
        self.assertFalse(MODEL["rom_implemented"])

    def test_gap_detector_finds_missing_actual_behaviors(self):
        gaps = issues_in_source_model()
        self.assertEqual(len(gaps), 7, gaps)

    def test_mutation_guards_are_not_vacuous(self):
        changes = [
            ("bad_route", lambda x: x["locations"][1]["exits"].update(east="S02"),
             "B001_NO_LONGER_DETERMINISTIC"),
            ("split_sign", lambda x: x["locations"][2].update(sign_object_id="DUPLICATE_SIGN"),
             "SIGN_IDENTITY_FORK"),
            ("deleted_exit", lambda x: x["locations"][4]["exits"].update(south="NO_SUCH_LOCATION"),
             "DANGLING_EXIT"),
            ("wrong_creator", lambda x: x.update(creator="Kiara Lynn Rose Smith"),
             "WRONG_CREATOR"),
        ]
        for label,mutate,expected in changes:
            with self.subTest(mutation=label):
                clone = copy.deepcopy(MODEL)
                mutate(clone)
                self.assertIn(expected,audit_contract(clone))

    def test_b001_forced_across_narrative_and_fruit_branches(self):
        for pip,fruit in itertools.product(BRANCHES["pip"],BRANCHES["fruit"]):
            with self.subTest(pip=pip,fruit=fruit):
                w = ReferenceWorld()
                self.assertTrue(w.choose_pip(pip))
                if fruit == "harvest":
                    self.assertTrue(w.harvest_fruit())
                self.assertTrue(w.move("east"))  # S00 -> S01
                self.assertTrue(w.mark_sign())
                self.assertTrue(w.move("east"))  # S01 -> E01
                self.assertEqual(w.location,"E01")
                self.assertEqual(w.b001_count,1)
                self.assertTrue(w.sign_marked)
                self.assertTrue(w.move("west"))  # E01 -> S01
                self.assertTrue(w.move("east"))  # again same B-001
                self.assertEqual(w.b001_count,2)
                w.validate()

    def test_all_72_branch_combinations_have_real_state_changes(self):
        runs=0
        states=set()
        for pip,fruit,sluice,rescue in itertools.product(*BRANCHES.values()):
            w=ReferenceWorld()
            self.assertTrue(w.choose_pip(pip))
            if fruit=="harvest": self.assertTrue(w.harvest_fruit())
            for d in ("east","east","north","east","east"): # S00 S01 E01 D00 D01 D02
                self.assertTrue(w.move(d))
            self.assertEqual(w.location,"D02")
            self.assertTrue(w.p001_recorded)
            self.assertTrue(w.set_sluice(sluice))
            self.assertTrue(w.select_rescue(rescue))
            self.assertTrue(w.move("west")) # D02 exit with escorted individuals
            self.assertTrue(w.move("north"))
            self.assertTrue(w.move("south")) # W01 -> town
            self.assertEqual(w.location,"S02")
            w.step(4)
            self.assertEqual(w.water,WATER_SHARES[sluice])
            self.assertEqual(w.p001_falsified,rescue=="both")
            self.assertEqual(len(w.exited),{"A_only":1,"B_only":1,"both":2,"neither":0}[rescue])
            w.validate()
            states.add((w.pip,w.fruit,w.sluice,tuple(w.exited)))
            runs+=1
        self.assertEqual(runs,72)
        self.assertEqual(len(states),72,"narrative branches collapsed into same state")

    def test_entrance_closure_cannot_trap_player_in_the_cave(self):
        for phase in range(GATE_PERIOD):
            w=ReferenceWorld()
            w.location="D01"
            w.tick=phase
            if phase not in PHASES_OPEN:
                self.assertFalse(w.move("south"))
                self.assertEqual(w.location,"D01")
            else:
                self.assertTrue(w.move("south"))
                self.assertEqual(w.location,"S02")
            w.location="D01"
            self.assertTrue(w.move("north"))
            self.assertTrue(w.move("south"))
            self.assertEqual(w.location,"S02")
            w.validate()

    def test_night_is_not_wall_clock_and_entry_never_required(self):
        for phase in range(4):
            w=ReferenceWorld()
            w.location="S02"
            w.tick=phase
            if phase not in PHASES_OPEN:
                self.assertFalse(w.move("south"))
                self.assertEqual(w.location,"S02")
            else:
                self.assertTrue(w.move("south"))
                self.assertEqual(w.location,"D01")
            # Alternate entry doesn't depend on phase.
            w.location="S02"
            self.assertTrue(w.move("north"))
            self.assertTrue(w.move("east"))
            self.assertEqual(w.location,"D01")

    def test_save_load_is_bitwise_stable_for_reference_history(self):
        w=ReferenceWorld(seed=109)
        self.assertTrue(w.move("east"))
        self.assertTrue(w.mark_sign())
        self.assertTrue(w.move("east"))
        w.step(80)
        self.assertEqual(w.fruit,"seedling")
        original_events=copy.deepcopy(w.events)
        saved=w.snapshot()
        restored=ReferenceWorld.restore(saved)
        self.assertEqual(restored.snapshot(),saved)
        self.assertEqual(restored.events,original_events)
        self.assertTrue(restored.sign_marked)
        self.assertEqual(restored.seedlings,1)
        self.assertTrue(restored.move("west"))
        self.assertEqual(w.events,original_events,"restoring and changing a clone mutated the original")

    def test_corrupted_reference_save_is_rejected(self):
        w=ReferenceWorld()
        payload=json.loads(w.snapshot())
        payload["payload"]["location"]="NOWHERE"
        with self.assertRaises(ValueError):
            ReferenceWorld.restore(json.dumps(payload))

    def test_fruit_harvest_prevents_unearned_new_cactus(self):
        harvested=ReferenceWorld()
        self.assertTrue(harvested.harvest_fruit())
        harvested.step(200)
        self.assertEqual(harvested.fruit,"carried")
        self.assertEqual(harvested.seedlings,0)
        abandoned=ReferenceWorld()
        abandoned.step(200)
        self.assertEqual(abandoned.fruit,"seedling")
        self.assertEqual(abandoned.seedlings,1)
        self.assertFalse(abandoned.harvest_fruit())
        harvested.validate();abandoned.validate()

    def test_prediction_must_exist_before_the_exit_it_is_said_to_predict(self):
        w=ReferenceWorld()
        w.location="D02"   # invalid artificial entry; must be caught by rescue gate
        self.assertFalse(w.select_rescue("both"))
        w.location="D01"
        self.assertTrue(w.move("east"))
        self.assertTrue(w.select_rescue("both"))
        self.assertFalse(w.p001_falsified)
        self.assertTrue(w.move("west"))
        self.assertTrue(w.p001_falsified)
        pred_idx=next(i for i,e in enumerate(w.events) if e["kind"]=="P-001")
        exit_idx=next(i for i,e in enumerate(w.events) if e["kind"]=="cairn_archive_exit")
        self.assertLess(pred_idx,exit_idx)

    def test_no_automatic_truth_from_a_single_rescue(self):
        for outcome in ("A_only","B_only","neither"):
            w=ReferenceWorld()
            w.location="D01"
            self.assertTrue(w.move("east"))
            self.assertTrue(w.select_rescue(outcome))
            self.assertTrue(w.move("west"))
            self.assertFalse(w.p001_falsified)
            self.assertFalse(any(e["kind"]=="P-001_confirmed" for e in w.events))

    def test_road_repair_does_not_rewrite_old_b001_evidence(self):
        w=ReferenceWorld()
        w.move("east"); w.move("east")
        prior=copy.deepcopy(w.events)
        self.assertFalse(w.repair_road_in_future(stage=1))
        self.assertTrue(w.repair_road_in_future(stage=3))
        w.move("west") # E01 -> S01
        w.move("east") # now direct town
        self.assertEqual(w.location,"S02")
        self.assertEqual(w.b001_count,1)
        self.assertEqual(w.events[:len(prior)],prior)
        w.validate()

    def test_randomized_38400_action_long_runs(self):
        actions=("east","west","north","south","wait","chalk","harvest","pip")
        for seed in range(96):
            rnd=random.Random(seed)
            w=ReferenceWorld(seed=seed)
            for i in range(400):
                action=rnd.choice(actions)
                if action=="wait": w.step()
                elif action=="chalk": w.mark_sign()
                elif action=="harvest": w.harvest_fruit()
                elif action=="pip": w.choose_pip(rnd.choice(BRANCHES["pip"]))
                else: w.move(action)
                if i%53==0:
                    w.validate()
                if i%97==0:
                    w=ReferenceWorld.restore(w.snapshot())
            w.validate()
            self.assertTrue(all(e["world_tick"]<=w.tick for e in w.events))
            self.assertEqual(w.seedlings in (0,1),True)

if __name__=="__main__":
    print("DREAMKILLER SOURCE-MODEL GAPS")
    for issue in issues_in_source_model():
        print("OPEN:",issue)
    print("THIS IS A REFERENCE-SIMULATION TEST, NOT A ROM TEST.")
    unittest.main(argv=["stress_reference.py","-v"],exit=False)
