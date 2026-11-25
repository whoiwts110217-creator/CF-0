# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Static checks for the one CF-0 Windows setup. They do not schedule a task."""
import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SETUP_PS1 = ROOT / "scripts" / "setup_cf0.ps1"
SETUP_BAT = ROOT / "SETUP_CF0.bat"
ARCHIVED = (
    "CHECK_CF0_MAINTENANCE_READ_ONLY.bat",
    "DISABLE_CF0_HEALTH_REPORT.bat",
    "DISABLE_CF0_WRITEBACK.bat",
    "ENABLE_CF0_HEALTH_REPORT.bat",
    "ENABLE_CF0_READ_WRITE.bat",
    "HP_BRIDGE_STATUS.bat",
    "INSTALL_CF0_RELAY.bat",
    "READ_WRITE_STATUS_CF0.bat",
    "RUN_CF0_RELAY.bat",
    "RUN_HP_BRIDGE_DEMO.bat",
    "RUN_HP_BRIDGE_ONCE.bat",
    "RUN_HP_TAKEOVER_CHECK.bat",
    "SETUP_HP_BRIDGE_WINDOWS.bat",
    "STATUS_CF0_HEALTH_REPORT.bat",
    "STATUS_CF0_RELAY.bat",
    "STOP_CF0_RELAY.bat",
    "STOP_HP_BRIDGE_WINDOWS.bat",
)


class SetupCf0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.setup = SETUP_PS1.read_text(encoding="utf-8")
        cls.bat = SETUP_BAT.read_text(encoding="utf-8")
        cls.installer = (ROOT / "relay" / "install_task.ps1").read_text(encoding="utf-8")
        cls.writeback = (ROOT / "relay" / "cf_public_relay_rw.ps1").read_text(encoding="utf-8")
        start = cls.setup.index("function Remove-Cf0RelayTask")
        end = cls.setup.index("# end Remove-Cf0RelayTask")
        cls.uninstall = cls.setup[start:end]

    def test_double_click_bat_calls_script_and_passes_uninstall(self):
        self.assertIn(r"scripts\setup_cf0.ps1", self.bat)
        self.assertIn("%*", self.bat)
        self.assertIn("pause", self.bat.lower())
        self.assertNotIn("CF_RELAY_GITHUB_TOKEN=", self.bat)
        self.assertIn("[switch]$Uninstall", self.setup)

    def test_reuses_existing_five_minute_installer(self):
        self.assertIn(r"relay\install_task.ps1", self.setup)
        self.assertIn("install", self.setup)
        self.assertIn("CavemanFocusCF0Relay", self.setup)
        self.assertIn("every 5 minutes", self.setup)
        self.assertIn("New-TimeSpan -Minutes 5", self.installer)
        for invented in ("New-ScheduledTaskTrigger", "New-ScheduledTaskPrincipal", "Register-ScheduledTask"):
            self.assertNotIn(invented, self.setup)
        for line in self.setup.splitlines():
            if "Set-ScheduledTask" in line:
                self.assertNotIn("-Principal", line)
                self.assertNotIn("-UserId", line)

    def test_uninstall_removes_the_task_only(self):
        self.assertIn("Unregister-ScheduledTask", self.uninstall)
        self.assertIn("$TaskName", self.uninstall)
        self.assertIn("no local history deleted", self.uninstall)
        self.assertNotIn("Remove-Item", self.uninstall)
        self.assertNotIn("write_token", self.uninstall)
        self.assertNotIn("sqlite", self.uninstall.lower())
        self.assertNotIn("git ", self.uninstall.lower())

    def test_token_matches_existing_dpapi_writeback(self):
        self.assertIn(r"CavemanFocus\CF0Relay", self.setup)
        self.assertIn("write_token.dpapi", self.setup)
        self.assertIn("write_token.dpapi", self.writeback)
        self.assertIn("1444521490", self.setup)
        self.assertIn("1444521490", self.writeback)
        self.assertIn("ConvertFrom-SecureString", self.setup)
        self.assertIn("-AsSecureString", self.setup)
        self.assertIn("this repository only", self.setup)
        self.assertIn("whoiwts110217-creator/CF-0", self.setup)
        self.assertIn("fine-grained", self.setup)
        self.assertIn("Windows DPAPI", self.setup)
        self.assertIn("kind = 'cf0_hp_writeback_probe'", self.setup)
        probe = self.setup.split("function New-WriteProbe", 1)[1].split("function Save-DpapiToken", 1)[0]
        self.assertLess(probe.index("Assert-RepositoryIdentity"), probe.index("Invoke-RestMethod -Method Put"))
        self.assertNotIn("ghp_", self.setup)
        self.assertNotIn("github_pat_", self.setup)
        self.assertNotIn("CF_RELAY_GITHUB_TOKEN=", self.setup)

    def test_clone_is_idempotent_and_does_not_delete(self):
        self.assertIn(r"CavemanFocus\CF-0", self.setup)
        self.assertIn("pull --ff-only", self.setup)
        self.assertIn("Nothing was deleted", self.setup)
        self.assertNotIn("reset --hard", self.setup)
        self.assertNotIn("clean -", self.setup)
        self.assertIn("cf_public_relay.py", self.setup)
        self.assertIn("$worker status", self.setup)
        self.assertIn('make_job("hp_status")', self.setup)
        self.assertIn("OVERALL", self.setup)

    def test_no_elevation(self):
        for forbidden in ("-RunLevel Highest", "Start-Process -Verb RunAs", "Invoke-Expression",
                          "/ru SYSTEM", "schtasks"):
            self.assertNotIn(forbidden, self.setup)

    def test_archived_launchers_moved_not_deleted(self):
        archive = ROOT / "archive" / "launchers"
        self.assertEqual(sorted(p.name for p in archive.glob("*.bat")), sorted(ARCHIVED))
        for name in ARCHIVED:
            self.assertFalse((ROOT / name).exists(), name)
            text = (archive / name).read_text(encoding="utf-8")
            self.assertIn("SETUP_CF0.bat", text)

    def test_powershell_parser_accepts_setup_script(self):
        pwsh = shutil.which("pwsh") or shutil.which("powershell")
        if not pwsh:
            self.skipTest("PowerShell is not installed on this machine; Windows CI parses the script")
        script = (
            "$tokens=$null; $errors=$null; "
            "[System.Management.Automation.Language.Parser]::ParseFile("
            f"'{SETUP_PS1}', [ref]$tokens, [ref]$errors) | Out-Null; "
            "if ($errors.Count -ne 0) { $errors | Format-List | Out-String | Write-Error; exit 1 }"
        )
        result = subprocess.run([pwsh, "-NoProfile", "-NonInteractive", "-Command", script],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
