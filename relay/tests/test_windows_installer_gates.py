# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""CF-026..028 regression gates: source/CI tests are not physical HP proof."""
import pathlib, subprocess, tempfile, unittest, sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
class InstallerGates(unittest.TestCase):
    def test_cf026_spaces_in_python_path(self):
        with tempfile.TemporaryDirectory(prefix="CF 0 folder with spaces ") as d:
            folder=pathlib.Path(d)/"relay source";folder.mkdir()
            script=folder/"cf_public_relay.py"
            script.write_bytes((ROOT/"relay/cf_public_relay.py").read_bytes())
            p=subprocess.run([sys.executable,str(script),"ping-demo"],cwd=str(folder),capture_output=True,text=True,timeout=30)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertIn('"pong": true',p.stdout)
    def test_cf027_nonadmin_design_only(self):
        s=(ROOT/"relay/install_task.ps1").read_text()
        self.assertIn("-RunLevel Limited",s)
        self.assertIn("-LogonType Interactive",s)
        self.assertNotIn("-RunLevel Highest",s)
    def test_cf028_five_minute_trigger_design(self):
        s=(ROOT/"relay/install_task.ps1").read_text()
        self.assertIn("New-TimeSpan -Minutes 5",s)
        self.assertIn("MultipleInstances IgnoreNew",s)
if __name__=="__main__":unittest.main()
