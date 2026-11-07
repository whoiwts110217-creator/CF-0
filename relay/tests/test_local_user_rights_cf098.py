"""CF-098: prove source user-rights policy detects privilege escalation attempts.

These tests only inspect public PowerShell source; no local Task Scheduler
commands, Windows user rights or HP device configuration are changed.
"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "relay"))
import local_user_rights_guard as guard


class LocalUserRightsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.install = guard.INSTALL.read_text(encoding="utf-8")
        cls.writeback = guard.WRITEBACK.read_text(encoding="utf-8")
        cls.health = guard.HEALTH.read_text(encoding="utf-8")

    def audit(self, install=None, rw=None, health=None):
        return guard.audit(install if install is not None else self.install,
                           rw if rw is not None else self.writeback,
                           health if health is not None else self.health)

    def test_existing_current_user_limited_install_and_writeback(self):
        self.assertEqual([], self.audit())
        self.assertEqual(guard.main(), 0)

    def test_privileged_installer_principal_is_rejected(self):
        changed = self.install.replace("-RunLevel Limited", "-RunLevel Highest", 1)
        self.assertNotEqual(changed, self.install)
        problems = self.audit(install=changed)
        self.assertTrue(any("principal missing" in msg or "elevated" in msg for msg in problems))

    def test_system_user_impersonation_is_rejected(self):
        changed = self.install.replace("-UserId $user", "-UserId 'SYSTEM'", 1)
        self.assertNotEqual(changed, self.install)
        self.assertTrue(self.audit(install=changed))

    def test_writeback_cannot_swap_principal_or_elevate(self):
        changed = self.writeback.replace(
            "Set-ScheduledTask -TaskName $TaskName -Action $action",
            "Set-ScheduledTask -TaskName $TaskName -Principal $elevated -Action $action",
            1)
        self.assertNotEqual(changed, self.writeback)
        self.assertTrue(self.audit(rw=changed))
        more = self.writeback + "\nStart-Process powershell.exe -Verb RunAs\n"
        self.assertTrue(self.audit(rw=more))

    def test_health_flag_cannot_replace_schedule(self):
        changed = self.health + "\nSet-ScheduledTask -TaskName $TaskName -Principal $elevated\n"
        self.assertTrue(self.audit(health=changed))

    def test_comment_cannot_fool_auditor_as_real_principal(self):
        changed = self.install.replace(
            "$principal=New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited",
            "# $principal=New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited",
            1)
        self.assertNotEqual(changed, self.install)
        self.assertTrue(self.audit(install=changed))


if __name__ == "__main__":
    unittest.main()
