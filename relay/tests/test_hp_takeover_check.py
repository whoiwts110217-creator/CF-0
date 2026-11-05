# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Source and CI checks; never claim these run on the owner's physical HP."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class HPTakeoverChecks(unittest.TestCase):
    def test_owner_launcher_calls_diagnostic(self):
        launcher = (ROOT / 'RUN_HP_TAKEOVER_CHECK.bat').read_text(encoding='utf-8')
        self.assertIn('hp_takeover_check.ps1', launcher)
        self.assertIn('-RunPoll', launcher)
        self.assertIn('pause', launcher.lower())
        self.assertNotIn('github_pat_', launcher)

    def test_diagnostic_no_escalation_or_unrestricted_commands(self):
        script = (ROOT / 'relay/hp_takeover_check.ps1').read_text(encoding='utf-8')
        self.assertIn('ping-demo', script)
        self.assertIn('Get-ScheduledTask', script)
        self.assertIn('WRITEBACK_CONFIGURED=', script)
        self.assertIn('ENABLE_CF0_READ_WRITE.bat', script)
        self.assertIn('INSTALL_CF0_RELAY.bat', script)
        self.assertIn('cf_public_relay_rw.ps1', script)
        self.assertIn('$hasWriteback', script)
        self.assertNotIn('Invoke-Expression', script)
        self.assertNotIn('Start-Process -Verb RunAs', script)
        self.assertNotIn('Register-ScheduledTask', script)
        self.assertNotIn('Set-ScheduledTask', script)

if __name__ == '__main__':
    unittest.main()
