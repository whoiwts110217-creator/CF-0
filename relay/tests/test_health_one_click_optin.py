"""Static gates for the optional owner-local HP health report activation.

These prove the reviewed source shape, not execution on the physical HP.
"""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "relay" / "configure_health_reporting.ps1"


class HealthOptInTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")

    def test_launchers_use_single_local_script(self):
        for mode in ("enable", "disable", "status"):
            name = mode.upper() + "_CF0_HEALTH_REPORT.bat"
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("relay\\configure_health_reporting.ps1", text)
            self.assertIn("-Mode " + mode, text)
            self.assertNotIn("CF_RELAY_GITHUB_TOKEN", text)
            self.assertNotIn("Set-ScheduledTask", text)

    def test_requires_same_checkout_existing_wrapper_and_token(self):
        text = self.source
        self.assertIn("Get-ScheduledTask -TaskName $TaskName", text)
        self.assertIn("WildcardPattern", text)
        self.assertIn("$ready.wrapper_current", text)
        self.assertIn("$ready.token_file_present", text)
        self.assertLess(text.index("if (-not $ready.task_present)"), text.index("Set-Content -LiteralPath $HealthFlag"))

    def test_preflight_before_opt_in_write(self):
        text = self.source
        self.assertIn("cf_hp_health_snapshot.py", text)
        self.assertIn("cf_hp_health_publish.py", text)
        self.assertIn("ConvertFrom-Json", text)
        self.assertIn("cf0.hp_health.v1", text)
        self.assertLess(text.index("ConvertFrom-Json"), text.index("Set-Content -LiteralPath $HealthFlag"))

    def test_never_mutates_existing_schedule_or_credentials(self):
        text = self.source
        for forbidden in ("Register-ScheduledTask", "Set-ScheduledTask", "Unregister-ScheduledTask",
                          "Remove-Item -LiteralPath $SecretFile", "Invoke-RestMethod", "CF_RELAY_GITHUB_TOKEN="):
            self.assertNotIn(forbidden, text)
        self.assertIn("Remove-Item -LiteralPath $HealthFlag -Force", text)


    def test_public_relay_has_no_gui_opt_in_path(self):
        worker = (ROOT / "relay" / "cf_public_relay.py").read_text(encoding="utf-8")
        wrapper = (ROOT / "relay" / "cf_public_relay_rw.ps1").read_text(encoding="utf-8")
        self.assertIn("ALLOWED = frozenset(('ping', 'hp_status', 'sidecar_verify'))", worker)
        for forbidden in ("open_notepad", "CF_ALLOW_NOTEPAD", "allow_notepad.flag"):
            self.assertNotIn(forbidden, worker)
            self.assertNotIn(forbidden, wrapper)


if __name__ == "__main__":
    unittest.main()
