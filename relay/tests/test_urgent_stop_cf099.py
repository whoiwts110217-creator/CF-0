"""CF-099: stop instructions match existing non-destructive/local-only controls.

These assertions examine repository text only. They do not stop or restart
Windows tasks, revoke credentials, or access an HP computer.
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class EmergencyStopDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = (ROOT / "relay/URGENT_STOP_AND_RESUME.md").read_text(encoding="utf-8")
        cls.stop = (ROOT / "STOP_CF0_RELAY.bat").read_text(encoding="utf-8")
        cls.installer = (ROOT / "relay/install_task.ps1").read_text(encoding="utf-8")
        cls.health_disable = (ROOT / "DISABLE_CF0_HEALTH_REPORT.bat").read_text(encoding="utf-8")
        cls.health = (ROOT / "relay/configure_health_reporting.ps1").read_text(encoding="utf-8")
        cls.write_disable = (ROOT / "DISABLE_CF0_WRITEBACK.bat").read_text(encoding="utf-8")
        cls.writeback = (ROOT / "relay/cf_public_relay_rw.ps1").read_text(encoding="utf-8")
        cls.bridge_stop = (ROOT / "STOP_HP_BRIDGE_WINDOWS.bat").read_text(encoding="utf-8")

    def test_document_tells_owner_disable_and_end_running_task_locally(self):
        for phrase in ("CavemanFocusCF0Relay", "**Disable**", "**End**",
                       "Ctrl+C", "Task Scheduler", "in_progress", "relay.sqlite3",
                       "owner-local", "not an immediate kill switch"):
            self.assertIn(phrase.lower(), self.doc.lower())

    def test_stop_batch_unregisters_only_the_public_task(self):
        self.assertIn('install_task.ps1', self.stop)
        self.assertRegex(self.stop, r'install_task\.ps1\" remove')
        self.assertIn('Unregister-ScheduledTask', self.installer)
        self.assertIn("'CavemanFocusCF0Relay'", self.installer)
        self.assertNotIn('del relay.sqlite3', self.stop.lower())
        self.assertIn("does not delete the SQLite ledger", self.doc)

    def test_health_and_writeback_disables_do_not_claim_stopping_work(self):
        self.assertIn("configure_health_reporting.ps1", self.health_disable)
        self.assertIn("-Mode disable", self.health_disable)
        self.assertIn("Remove-Item -LiteralPath $HealthFlag", self.health)
        self.assertIn("cf_public_relay_rw.ps1", self.write_disable)
        self.assertIn("disable", self.write_disable)
        self.assertIn("Set-ScheduledTask -TaskName $TaskName -Action $action", self.writeback)
        self.assertIn("does not stop polling", self.doc.lower())

    def test_bridge_is_separate_and_only_a_local_action(self):
        self.assertIn("bridge\\setup_windows.ps1", self.bridge_stop.lower())
        self.assertIn("CavemanFocusHPBridge", self.doc)
        self.assertIn("STOP_HP_BRIDGE_WINDOWS.bat", self.doc)
        self.assertIn("may not remotely disable or kill HP processes", self.doc)

    def test_restart_safety_requires_real_evidence(self):
        self.assertIn("INSTALL_CF0_RELAY.bat", self.doc)
        self.assertIn("pending public jobs", self.doc)
        self.assertIn("unexpired requests", self.doc)
        self.assertIn("scheduled-task evidence", self.doc)
        self.assertIn("not prove HP scheduler origin", self.doc)
        self.assertIn("No token revocation", self.doc)


if __name__ == "__main__":
    unittest.main()
