# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Static safety and installation tests; real Windows behavior needs HP evidence."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

class ReadWriteSetupTests(unittest.TestCase):
    def test_one_click_scripts_exist(self):
        for name in ("ENABLE_CF0_READ_WRITE.bat","READ_WRITE_STATUS_CF0.bat","DISABLE_CF0_WRITEBACK.bat"):
            p=ROOT/name
            self.assertTrue(p.is_file(),name)
            self.assertIn("relay\\cf_public_relay_rw.ps1",p.read_text())

    def test_no_literal_credentials(self):
        s=(ROOT/"relay/cf_public_relay_rw.ps1").read_text()
        self.assertIn("Read-Host 'GitHub fine-grained token (input hidden)' -AsSecureString",s)
        self.assertIn("ConvertFrom-SecureString",s)
        self.assertIn("ConvertTo-SecureString",s)
        self.assertIn("Env:CF_RELAY_GITHUB_TOKEN",s)
        self.assertNotIn("ghp_" ,s)
        self.assertNotIn("shell=True",s)

    def test_actual_write_proof_before_schedule_change(self):
        s=(ROOT/"relay/cf_public_relay_rw.ps1").read_text()
        self.assertIn("Invoke-RestMethod -Method Put",s)
        self.assertIn("kind='cf0_hp_writeback_probe'",s)
        self.assertLess(s.index("$probeId=New-WriteProbe $secret"),s.index("Set-ScheduledTask -TaskName $TaskName -Action $action | Out-Null",s.index("$probeId=New-WriteProbe $secret")))

    def test_existing_schedule_reused_and_disable_restores_reader(self):
        s=(ROOT/"relay/cf_public_relay_rw.ps1").read_text()
        self.assertIn("Set-ScheduledTask",s)
        self.assertNotIn("Register-ScheduledTask",s)
        self.assertIn("Remove-Item -LiteralPath $SecretFile -Force",s)
        self.assertIn("cf_public_relay.py",s)
        self.assertIn("CavemanFocusCF0Relay",s)

if __name__=="__main__":
    unittest.main()
