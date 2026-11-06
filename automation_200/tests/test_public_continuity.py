"""CI regression checks for the published CF-0 continuity status.

Read only; each mutation test runs in an isolated temporary mirror and never
modifies GitHub, source files, the owner's HP or the private archive.
"""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from automation_200.public_continuity_check import ROOT, ContinuityError, check

FILES = (
    "docs/PUBLIC_CONTINUITY_STATE.json",
    "docs/PROJECT_STATUS.md",
    "docs/CONTINUITY.md",
    "README.md",
    "automation_200/MASTER_MISSION_BOARD.md",
    "automation_200/MASTER_OPERATOR_PROMPT.md",
    "automation_200/OWNER_CAPABILITY_CONTRACT.json",
    "automation_200/registry.json",
    "relay/cf_public_relay.py",
    "relay/INSTALL_NOTEPAD_CONTROL.ps1",
    "command_queue/inbox/aeccc8a2-217f-4786-aaaf-19b2fc9ff35a.json",
    "command_queue/receipts/aeccc8a2-217f-4786-aaaf-19b2fc9ff35a.json",
)


class PublicContinuityTests(unittest.TestCase):
    def test_live_repository_continuity(self):
        status = check()
        self.assertTrue(status["passed"])
        self.assertEqual(status["registry_verified"], 54)
        self.assertEqual(status["latest_checkpoint"], 52)
        self.assertTrue(status["ping_digest_matched"])
        self.assertFalse(status["notepad_restored"])
        self.assertFalse(status["hp_hardware_attestation"])

    def prepare(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        for f in FILES:
            (root / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / f, root / f)
        cp = root / "automation_200/checkpoints"
        cp.mkdir(parents=True, exist_ok=True)
        for f in (ROOT / "automation_200/checkpoints").glob("checkpoint_*.json"):
            shutil.copyfile(f, cp / f.name)
        self.addCleanup(td.cleanup)
        return root

    def test_stale_registry_count_is_rejected(self):
        root = self.prepare()
        p = root / "docs/PUBLIC_CONTINUITY_STATE.json"
        j = json.loads(p.read_text())
        j["cf200"]["verified"] = 52
        p.write_text(json.dumps(j))
        with self.assertRaisesRegex(ContinuityError, "public_work_order_count_stale"):
            check(root)

    def test_old_public_board_heading_is_rejected(self):
        root = self.prepare()
        p = root / "automation_200/MASTER_MISSION_BOARD.md"
        p.write_text(p.read_text().replace("54/200", "52/200", 1))
        with self.assertRaisesRegex(ContinuityError, "public_mission_board_header_stale"):
            check(root)

    def test_fake_ping_receipt_is_rejected(self):
        root = self.prepare()
        p = root / "command_queue/receipts/aeccc8a2-217f-4786-aaaf-19b2fc9ff35a.json"
        j = json.loads(p.read_text())
        j["request_sha256"] = "0" * 64
        p.write_text(json.dumps(j))
        with self.assertRaisesRegex(ContinuityError, "public_ping_digest_or_receipt_mismatch"):
            check(root)

    def test_fabricated_hp_identity_or_owner_enforcement_is_rejected(self):
        for field, value, message in (
            (("hp", "physical_device_and_scheduler_correlation"), "verified", "unproven_hp_origin_claim"),
            (("hp", "fully_unattended_7_days"), "verified", "unproven_week_claim"),
            (("governance", "owner_review_enforced_by_github"), "verified", "owner_review_false_claim"),
        ):
            with self.subTest(field=field):
                root = self.prepare()
                p = root / "docs/PUBLIC_CONTINUITY_STATE.json"
                j = json.loads(p.read_text())
                j[field[0]][field[1]] = value
                p.write_text(json.dumps(j))
                with self.assertRaisesRegex(ContinuityError, message):
                    check(root)

    def test_original_project_list_is_not_pretended_recovered(self):
        root = self.prepare()
        p = root / "docs/PUBLIC_CONTINUITY_STATE.json"
        j = json.loads(p.read_text())
        j["archive"]["original_project_count_proven"] = True
        p.write_text(json.dumps(j))
        with self.assertRaisesRegex(ContinuityError, "false_original_project_count_claim"):
            check(root)


if __name__ == "__main__":
    unittest.main()
