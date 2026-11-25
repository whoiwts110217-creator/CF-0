"""Offline source invariants for the existing one-hub CF-0 pathway filters."""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def routes():
    source = (ROOT / "project-paths.js").read_text(encoding="utf-8")
    m = re.search(r"const ROUTES=Object\.freeze\((\[.*?\])\);", source, re.S)
    if m is None:
        raise AssertionError("Missing static public route table")
    return json.loads(m.group(1))


class ProjectPathsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "links.json").read_text(encoding="utf-8"))
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.script = (ROOT / "project-paths.js").read_text(encoding="utf-8")
        cls.routes = routes()

    def test_existing_hub_is_reused(self):
        self.assertIn('id="cf-project-paths"', self.html)
        self.assertIn('src="./project-paths.js"', self.html)
        self.assertIn('id="q"', self.html)
        self.assertIn('id="owner-actions"', (ROOT / "owner-actions.js").read_text(encoding="utf-8"))
        self.assertNotIn("another-dashboard.html", self.html)

    def test_purpose_buttons_are_source_resolvable(self):
        self.assertEqual(len(self.routes), len({r["id"] for r in self.routes}))
        self.assertGreaterEqual(len(self.routes), 7)
        links = self.data["links"]
        for route in self.routes:
            with self.subTest(route=route["id"]):
                self.assertTrue(route["title"].strip())
                self.assertTrue(route["hint"].strip())
                if route["mode"] == "category":
                    self.assertTrue(any(x["category"] == route["category"] for x in links))
                elif route["mode"] == "search":
                    needle = route["query"].lower()
                    self.assertTrue(any(needle in
                                        " ".join([x["title"], x["category"], x["note"]]).lower()
                                        for x in links))
                else:
                    self.assertEqual(route["mode"], "actions")

    def test_public_routes_and_spider_are_discoverable(self):
        links = self.data["links"]
        self.assertEqual(len(links), len({x["id"] for x in links}))
        self.assertGreaterEqual(len(links), 90)
        self.assertTrue(any("spider" in x["title"].lower() for x in links))
        for x in links:
            self.assertTrue(x["url"].startswith("https://"))
            self.assertNotIn("drive.google.com", x["url"])
            self.assertNotIn("mail.google.com", x["url"])
            self.assertNotIn("chatgpt.com/c/", x["url"])
        for number in range(84, 92):
            item = next(x for x in links if x["id"] == str(number))
            self.assertEqual(item["status"], "source")

    def test_offline_fallback_matches_public_catalog(self):
        m = re.search(r"let DIRECTORY=(\[.*?\]);\s*const STORAGE=", self.html, re.S)
        self.assertIsNotNone(m)
        self.assertEqual(json.loads(m.group(1)), self.data["links"])
        sw = (ROOT / "sw.js").read_text(encoding="utf-8")
        self.assertIn("cf-link-vault-v8", sw)
        self.assertIn('./project-paths.js', sw)
        self.assertIn('project-paths\\.js', sw)

    def test_mobile_keyboard_and_no_untrusted_html(self):
        for phrase in ["prefers-reduced-motion", "aria-labelledby",
                       'document.createElement(', 'addEventListener("keydown"',
                       "event.preventDefault()", 'search.dispatchEvent(']:
            self.assertIn(phrase, self.script)
        self.assertNotIn("innerHTML", self.script)
        self.assertIn("Private archives stay private.", self.script)


if __name__ == "__main__":
    unittest.main()
