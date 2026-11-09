"""Regression tests for reversible, non-executing CF-0 focus switches."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from automation_200.decision_engine import propose
from automation_200.resumable_focus import (
    SCHEMA, default_state, plan_handoff, save_local_state,
)


def task(id_, stream="receipt", status="planned", deps=(), hp=False):
    return {"id": id_, "title": id_, "stream": stream, "status": status,
            "depends_on": list(deps), "physical_hp_required": hp,
            "priority": 1, "authority": "owner-reviewed"}


def registry():
    return {"tasks": [
        task("AUTO", "receipt"), task("GOV", "priority_logic"),
        task("MONEY", "public_finance"), task("IDEA", "research"),
        task("LOCAL", "hp_install"), task("DEVICE", "real_operations", hp=True),
        task("BLOCKED", "receipt", deps=["DEVICE"]),
    ]}


def decision(r, **kwargs):
    return propose(r, now=1000, limit=20, **kwargs)


class ResumableFocusTests(unittest.TestCase):
    def test_first_start_and_no_mutation(self):
        r = registry()
        d = decision(r)
        before = copy.deepcopy((r, d))
        out = plan_handoff(r, d)
        self.assertEqual((out["transition"], out["proposed_next_id"]), ("start", "AUTO"))
        self.assertEqual(out["next_state"]["active"]["task_id"], "AUTO")
        self.assertEqual((r, d), before)
        self.assertFalse(out["execution_authorized"])

    def test_same_tier_stickiness_to_avoid_thrashing(self):
        r = registry()
        r["tasks"].insert(0, task("A_NEW", "receipt"))
        s = {"schema": SCHEMA, "active": {"task_id": "AUTO", "checkpoint_ref": "private/auto#1"}, "paused": []}
        out = plan_handoff(r, decision(r), s)
        self.assertEqual(out["transition"], "continue")
        self.assertEqual(out["proposed_next_id"], "AUTO")

    def test_owner_override_switch_and_resume(self):
        r = registry()
        start = plan_handoff(r, decision(r))["next_state"]
        requested = decision(r, owner_preference_ids=["MONEY"])
        no_checkpoint = plan_handoff(r, requested, start)
        self.assertFalse(no_checkpoint["ready"])
        self.assertEqual(no_checkpoint["transition"], "checkpoint_required")
        self.assertEqual(no_checkpoint["next_state"], start)
        switched = plan_handoff(r, requested, start, checkpoint_ref="private/snapshots/auto-1.json")
        self.assertEqual(switched["transition"], "switch")
        self.assertEqual(switched["next_state"]["paused"],
                         [{"task_id": "AUTO", "checkpoint_ref": "private/snapshots/auto-1.json"}])
        self.assertEqual(switched["proposed_next_id"], "MONEY")
        resumed = plan_handoff(
            r, decision(r, owner_preference_ids=["AUTO"]),
            switched["next_state"], checkpoint_ref="private/snapshots/money-2.json")
        self.assertEqual(resumed["transition"], "resume")
        self.assertEqual(resumed["next_state"]["active"]["checkpoint_ref"],
                         "private/snapshots/auto-1.json")
        self.assertEqual(resumed["next_state"]["paused"],
                         [{"task_id": "MONEY", "checkpoint_ref": "private/snapshots/money-2.json"}])

    def test_higher_tier_preempts_with_checkpoint(self):
        r = registry()
        state = {"schema": SCHEMA, "active": {"task_id": "IDEA", "checkpoint_ref": "private/idea#2"}, "paused": []}
        out = plan_handoff(r, decision(r), state)
        self.assertEqual((out["transition"], out["proposed_next_id"]), ("switch", "AUTO"))
        self.assertEqual(out["next_state"]["paused"][0]["task_id"], "IDEA")

    def test_blocked_current_requires_checkpoint_and_chooses_safe_alternate(self):
        r = registry()
        start = plan_handoff(r, decision(r))["next_state"]
        d = decision(r, blocked_ids=["AUTO"])
        held = plan_handoff(r, d, start)
        self.assertEqual(held["transition"], "checkpoint_required")
        moved = plan_handoff(r, d, start, checkpoint_ref="private/auto#3")
        self.assertEqual(moved["proposed_next_id"], "GOV")
        self.assertEqual(moved["next_state"]["paused"][0]["task_id"], "AUTO")

    def test_verified_current_does_not_need_checkpoint(self):
        r = registry()
        r["tasks"][0]["status"] = "verified"
        state = {"schema": SCHEMA, "active": {"task_id": "AUTO", "checkpoint_ref": None}, "paused": []}
        out = plan_handoff(r, decision(r), state)
        self.assertTrue(out["ready"])
        self.assertEqual(out["proposed_next_id"], "GOV")
        self.assertEqual(out["next_state"]["paused"], [])

    def test_owner_cannot_bypass_hp_or_dependency(self):
        r = registry()
        d = decision(r, owner_preference_ids=["LOCAL", "DEVICE", "BLOCKED", "MONEY"])
        out = plan_handoff(r, d)
        self.assertEqual(out["proposed_next_id"], "MONEY")
        self.assertNotIn("LOCAL", out["alternatives"])
        self.assertNotIn("DEVICE", out["alternatives"])
        self.assertNotIn("BLOCKED", out["alternatives"])

    def test_invalid_state_fails_closed(self):
        r = registry()
        d = decision(r)
        for bad in (
            {}, {"schema": SCHEMA, "active": None, "paused": ["AUTO"]},
            {"schema": SCHEMA, "active": {"task_id": "UNKNOWN", "checkpoint_ref": None}, "paused": []},
            {"schema": SCHEMA, "active": None, "paused": [{"task_id": "AUTO", "checkpoint_ref": None}]},
            {"schema": SCHEMA, "active": {"task_id": "AUTO", "checkpoint_ref": None},
             "paused": [{"task_id": "AUTO", "checkpoint_ref": "private/a"}]},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                plan_handoff(r, d, bad)

    def test_checkpoint_reference_rejects_control_characters(self):
        with self.assertRaises(ValueError):
            plan_handoff(registry(), decision(registry()), checkpoint_ref="secret\ninjected")

    def test_local_atomic_state_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "focus.json"
            state = default_state()
            save_local_state(path, state)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), state)
            self.assertEqual(list(Path(folder).iterdir()), [path])
            state["active"] = {"task_id": "AUTO", "checkpoint_ref": None}
            save_local_state(path, state)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), state)

    def test_real_registry_safe_proposal(self):
        root = Path(__file__).resolve().parents[1]
        r = json.loads((root / "registry.json").read_text(encoding="utf-8"))
        out = plan_handoff(r, decision(r))
        self.assertTrue(out["ready"])
        self.assertFalse(out["execution_authorized"])
        self.assertEqual(out["schema"], SCHEMA)


if __name__ == "__main__":
    unittest.main()
