# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Static release checks. Real Windows scheduling must still be tested on HP."""
import pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
class LauncherChecks(unittest.TestCase):
    def test_launchers_exist(self):
        archive = ROOT / 'archive' / 'launchers'
        for x in ('RUN_CF0_RELAY.bat','INSTALL_CF0_RELAY.bat','STOP_CF0_RELAY.bat','STATUS_CF0_RELAY.bat'):
            self.assertTrue((archive/x).is_file(),x)
            self.assertFalse((ROOT/x).exists(),x)
        self.assertTrue((ROOT/'SETUP_CF0.bat').is_file())
        self.assertEqual(sorted(p.name for p in ROOT.glob('*.bat')), ['SETUP_CF0.bat'])
    def test_no_tokens_in_launchers(self):
        files = list((ROOT/'archive'/'launchers').glob('*.bat'))
        files.append(ROOT/'SETUP_CF0.bat')
        files.append(ROOT/'scripts'/'setup_cf0.ps1')
        for x in files:
            s=x.read_text(encoding='utf-8')
            self.assertNotIn('CF_RELAY_GITHUB_TOKEN=',s)
            self.assertNotIn('ghp_',s)
            self.assertNotIn('github_pat_',s)
            self.assertNotIn('curl -X POST',s)
    def test_schedule_has_stop_and_no_admin_privilege(self):
        s=(ROOT/'relay/install_task.ps1').read_text()
        self.assertIn('Unregister-ScheduledTask',s)
        self.assertIn('New-ScheduledTaskTrigger',s)
        self.assertIn('-RunLevel Limited',s)
        self.assertIn('MultipleInstances IgnoreNew',s)
    def test_relay_command_file_is_owner_reviewable(self):
        s=(ROOT/'relay/cf_public_relay.py').read_text()
        self.assertIn("ALLOWED = frozenset(('ping', 'hp_status', 'sidecar_verify', 'open_notepad'))",s)
        self.assertNotIn('shell=True',s)
if __name__=='__main__': unittest.main()
