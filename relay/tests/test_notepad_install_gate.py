"""Prevent a deceptive Notepad installation success or uncontrolled source overwrite."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "relay" / "INSTALL_NOTEPAD_CONTROL.ps1"


class NotepadInstallGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.code = "\n".join(
            line for line in cls.script.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )

    def test_explicitly_reports_unavailable_and_nonzero_exit(self):
        self.assertIn("NOTEPAD_ACTION=BLOCKED_NOT_SUPPORTED", self.code)
        self.assertIn("LOCAL_CHANGES=NONE", self.code)
        self.assertIn("exit 2", self.code)
        self.assertNotIn("NOTEPAD_ACTION=INSTALLED_AND_OPTED_IN", self.code)

    def test_has_no_local_mutation_or_mutable_branch_download(self):
        for disallowed in (
            "Invoke-WebRequest", "Invoke-RestMethod", "Set-Content",
            "New-Item", "Set-ScheduledTask", "Register-ScheduledTask",
            "Start-Process", "Remove-Item", "Copy-Item",
        ):
            with self.subTest(operation=disallowed):
                self.assertNotIn(disallowed, self.code)

    def test_does_not_contain_hidden_remote_command_loader(self):
        for disallowed in ("iex", "Invoke-Expression", "EncodedCommand", "DownloadString"):
            with self.subTest(token=disallowed):
                self.assertNotIn(disallowed, self.code)


if __name__ == "__main__":
    unittest.main()
