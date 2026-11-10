"""Source-level regression tests for the public-safe CF Link Vault PWA."""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
class LinkVaultSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/"index.html").read_text(encoding="utf-8")
        cls.script=(ROOT/"enhance.js").read_text(encoding="utf-8")
        cls.sw=(ROOT/"sw.js").read_text(encoding="utf-8")
        cls.catalog=json.loads((ROOT/"links.json").read_text(encoding="utf-8"))
        cls.manifest=json.loads((ROOT/"manifest.webmanifest").read_text(encoding="utf-8"))

    def test_public_catalog_schema_and_stable_ids(self):
        self.assertEqual(self.catalog["schema"],"cf.link.vault.public.v2")
        self.assertGreaterEqual(len(self.catalog["links"]),78)
        self.assertEqual(len({x["id"] for x in self.catalog["links"]}),len(self.catalog["links"]))
        self.assertEqual(len({x["url"] for x in self.catalog["links"]}),len(self.catalog["links"]))
        self.assertRegex(self.catalog["revision"],r"^20\d\d-\d\d-\d\d\.")

    def test_public_catalog_has_safe_url_and_content(self):
        for link in self.catalog["links"]:
            with self.subTest(link=link["id"]):
                parsed=urlparse(link["url"])
                self.assertEqual(parsed.scheme,"https")
                self.assertTrue(parsed.netloc)
                self.assertFalse(parsed.username or parsed.password)
                self.assertIn(link["status"],{"source","live","unverified","external"})
                self.assertTrue(link["title"] and link["category"])
                self.assertLessEqual(len(link["note"]),260)
                self.assertNotRegex(link["url"],r"(?:chatgpt\.com/c/|/conversation/|token=|api_key=)")

    def test_moving_current_routes_exist(self):
        urls=[x["url"] for x in self.catalog["links"]]
        for tail in ("CURRENT_SOURCE_GATEWAY.md","OWNER_JUNGLE_MAP.md","UNIVERSAL_FRESHNESS_CONTRACT.md","CHATGPT_MEMORY_BOOTSTRAP.md"):
            self.assertTrue(any(u.endswith(tail) and "/blob/main/" in u for u in urls),tail)

    def test_compass_and_refresh_ui(self):
        for label in ("compass-title","catalog-status","refresh","return-trail","save-link","add-dialog","resume"):
            self.assertIn('id="'+label+'"',self.html)
        for phrase in ("Where am I?","Continue my work","What's current?","Make money","Build something"):
            self.assertIn(phrase,self.html)
        self.assertIn('src="./enhance.js"',self.html)
        self.assertEqual(self.html.count("<style>"),1)
        self.assertEqual(self.html.count("</style>"),1)

    def test_offline_and_live_refresh_boundaries(self):
        self.assertIn("fetch(\"./links.json?check=\"+Date.now()",self.script)
        self.assertIn("cache:\"no-store\"",self.script)
        self.assertIn("state.overrides",self.script)
        self.assertIn("state.lastOpened",self.script)
        self.assertIn("CF-Link-Vault-Personal-Backup.json",self.script)
        self.assertIn("Offline / not checked now",self.script)
        self.assertIn("cf-link-vault-v6",self.sw)
        self.assertIn("./links.json",self.sw)
        self.assertIn("if(hot)",self.sw)
        self.assertIn("cache.match(req,{ignoreSearch:true})",self.sw)
        self.assertNotIn("chatgpt.com/c/",self.html)

    def test_home_screen_registration(self):
        self.assertEqual(self.manifest["display"],"standalone")
        self.assertEqual(self.manifest["start_url"],"./")
        self.assertIn("apple-mobile-web-app-capable",self.html)
        self.assertIn('navigator.serviceWorker.register("./sw.js")',self.html)

if __name__=="__main__":
    unittest.main()
