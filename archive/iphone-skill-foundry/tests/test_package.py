"""Static checks for public iPhone Skill Foundry; no account or HP access."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SkillFoundryPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.sw = (ROOT / "sw.js").read_text(encoding="utf-8")
        cls.manifest = json.loads((ROOT / "manifest.webmanifest").read_text(encoding="utf-8"))

    def test_ios_viewport(self):
        self.assertIn("viewport-fit=cover", self.html)
        self.assertIn("apple-mobile-web-app-capable", self.html)

    def test_help_buttons_reference_explanations(self):
        controls = re.findall(r'aria-controls="([^"]+)"', self.html)
        self.assertGreaterEqual(len(controls), 10)
        ids = set(re.findall(r'id="([^"]+)"', self.html))
        self.assertTrue(set(controls) <= ids)
        self.assertIn('class="help-toggle', self.html)

    def test_generator_and_exports_present(self):
        for token in ("id=\"skillForm\"", "id=\"downloadZip\"", "id=\"shareZip\"", "id=\"preview\""):
            self.assertIn(token, self.html)
        self.assertIn("Copy AI synthesis prompt", self.html)

    def test_standalone_manifest_is_relative(self):
        self.assertEqual(self.manifest["start_url"], "./")
        self.assertEqual(self.manifest["scope"], "./")
        self.assertEqual(self.manifest["display"], "standalone")

    def test_serviceworker_cache_is_local(self):
        self.assertIn("'./index.html'", self.sw)
        self.assertIn("'./manifest.webmanifest'", self.sw)
        self.assertIn("'./icon.svg'", self.sw)

    def test_external_scripts_absent(self):
        self.assertNotIn("<script src=", self.html)
        self.assertNotIn("https://cdn.", self.html.lower())

if __name__ == "__main__":
    unittest.main()
