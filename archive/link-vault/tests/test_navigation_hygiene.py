"""CF-0 public Link Vault privacy, path, and keyboard-navigation regression tests."""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BANNED = (
    re.compile(r"https?://chatgpt\.com/c/", re.I),
    re.compile(r"https?://(?:docs|drive)\.google\.com/(?:document|spreadsheets|file|drive/folders)/", re.I),
    re.compile(r"\b(?:ghp_[0-9A-Za-z]{20,}|sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{20,})\b"),
    re.compile(r"(?i)\b(?:access_token|recovery_code)\s*[:=]\s*[A-Za-z0-9_-]{20,}"),
)


class NavigationHygieneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.script = (ROOT / "owner-actions.js").read_text(encoding="utf-8")
        cls.links = json.loads((ROOT / "links.json").read_text(encoding="utf-8"))
        cls.actions = json.loads((ROOT / "owner-actions.json").read_text(encoding="utf-8"))

    def test_compass_routes_unique(self):
        urls = re.findall(r'<a class="route" href="([^"]+)"', self.html)
        self.assertGreaterEqual(len(urls), 7)
        self.assertEqual(len(urls), len(set(urls)))
        self.assertTrue(any("spider-hp/README.md" in u for u in urls))

    def test_relative_assets_exist_on_disk(self):
        urls = re.findall(r'\b(?:src|href)="(\./[^"?#]+)"', self.html)
        self.assertGreaterEqual(len(urls), 9)
        for url in urls:
            with self.subTest(url=url):
                path = (ROOT / url[2:]).resolve()
                self.assertTrue(path.is_relative_to(ROOT.resolve()))
                self.assertTrue(path.is_file(), f"Missing asset {url}")

    def test_no_sensitive_urls_or_tokens_in_both_public_catalogs(self):
        for name, records in (("links.json", self.links), ("owner-actions.json", self.actions)):
            raw = json.dumps(records, ensure_ascii=False)
            for pat in BANNED:
                with self.subTest(file=name, pattern=pat.pattern):
                    self.assertIsNone(pat.search(raw), f"Potential private URL/token in {name}")
        self.assertEqual(len({x["id"] for x in self.links["links"]}), len(self.links["links"]))
        self.assertEqual(len({x["id"] for x in self.actions["actions"]}), len(self.actions["actions"]))

    def test_semantic_breadcrumb_and_keyboard_tablist(self):
        self.assertIn('aria-label="Breadcrumb"', self.html)
        self.assertIn('id="cf-breadcrumb-zone"', self.html)
        self.assertIn('role="tablist"', self.script)
        self.assertIn('role="tab"', self.script)
        self.assertIn('role="tabpanel"', self.script)
        for word in ("ArrowRight", "ArrowLeft", "Home", "End", "aria-selected"):
            self.assertIn(word, self.script)

    def test_dated_status_is_explicit_and_source_link_remains_available(self):
        self.assertIn('ageStamp(catalogDate)', self.script)
        self.assertIn("STALE (", self.script)
        self.assertIn("Offline / not checked now", self.script)
        self.assertIn("CURRENT_SOURCE_GATEWAY.md", self.script)


if __name__ == "__main__":
    unittest.main()
