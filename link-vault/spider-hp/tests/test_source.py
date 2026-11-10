"""Synthetic source-only validation for the free HP native Spider plan format."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class FreeHpSpiderSourceTests(unittest.TestCase):
    def test_three_sample_plans_are_bounded_and_free(self):
        for file in ("notepad-inspect.json","notepad-type-safe.json","calculator-inspect.json"):
            plan=json.loads((ROOT/file).read_text(encoding="utf-8"))
            self.assertEqual(plan["schema"],"cf0.spider.hp_plan.v1")
            self.assertIn(plan["app"],("notepad","calculator"))
            self.assertTrue(1<=len(plan["steps"])<=12)
            for step in plan["steps"]:
                self.assertIn(step["op"],("launch","inspect","wait","read","invoke","type_safe","assert_contains"))
                self.assertFalse(any(k in step for k in ("shell","command","url","powershell")))
    def test_source_requires_local_owner_opt_in_and_stops(self):
        source=(ROOT/"Spider-HP.ps1").read_text(encoding="utf-8")
        self.assertIn("switch]$OwnerOptIn",source)
        self.assertIn("switch]$Execute",source)
        self.assertIn("CheckStop",source)
        self.assertIn("SPIDER_STOP_REQUESTED",source)
        self.assertIn("DRY_RUN=NO_UI_ACTIONS",source)
        self.assertIn("REFUSE_TO_OVERWRITE_NONEMPTY_NOTEPAD",source)
        self.assertIn("NOTEPAD_NOT_FOREGROUND_REFUSE_TYPING",source)
        self.assertIn("TYPE_OUTCOME_NOT_CONFIRMED",source)
        self.assertIn("TARGET_WINDOW_COUNT_",source)
        self.assertIn("SELECTOR_COUNT_",source)
        self.assertNotIn("Invoke-Expression",source)
        self.assertNotIn("DownloadString",source)
        self.assertNotIn("Invoke-RestMethod",source)
    def test_multi_app_chain_is_fixed_and_stop_safe(self):
        queue=json.loads((ROOT/"spider-multi-demo.json").read_text(encoding="utf-8"))
        self.assertEqual(queue["schema"],"cf0.spider.hp_queue.v1")
        self.assertEqual(queue["plans"],["notepad-inspect.json","calculator-inspect.json"])
        self.assertEqual(len(queue["plans"]),len(set(queue["plans"])))
        source=(ROOT/"Spider-Multi.ps1").read_text(encoding="utf-8")
        self.assertIn("PLAN_NOT_ALLOWLISTED",source)
        self.assertIn("DUPLICATE_PLAN_REFUSED",source)
        self.assertIn("PLAN_FAILED_STOP_CHAIN_",source)
        self.assertIn("DRY_RUN=NO_UI_ACTIONS",source)
        self.assertIn("MODEL_COST=ZERO",source)
        self.assertIn("Stop",source)
        self.assertNotIn("Invoke-Expression",source)
        self.assertNotIn("Start-ScheduledTask",source)
        self.assertNotIn("Register-ScheduledTask",source)

    def test_no_schedule_or_relay_permission_broadening(self):
        source=(ROOT/"Spider-HP.ps1").read_text(encoding="utf-8")
        for forbidden in ("Register-ScheduledTask","Start-ScheduledTask","New-ScheduledTask",
                          "Set-ScheduledTask","Win32_Service","CreateService","-Verb RunAs"):
            self.assertNotIn(forbidden,source)
        self.assertIn("HP_LOCAL_ACTIONS=NOT_STARTED",source)

if __name__=="__main__":
    unittest.main()
