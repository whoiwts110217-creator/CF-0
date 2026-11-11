import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


class OwnerActionOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "owner-actions.json").read_text(encoding="utf-8"))
        cls.links = json.loads((ROOT / "links.json").read_text(encoding="utf-8"))
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.script = (ROOT / "owner-actions.js").read_text(encoding="utf-8")
        cls.sw = (ROOT / "sw.js").read_text(encoding="utf-8")
        cls.enhance = (ROOT / "enhance.js").read_text(encoding="utf-8")

    def test_one_view_not_authoritative_registry(self):
        d = self.data
        self.assertEqual(d["schema"], "cf.link.vault.owner_view.v1")
        self.assertIn("not the authoritative task registry", d["source_note"])
        self.assertGreaterEqual(len(d["actions"]), 10)
        self.assertLessEqual(len(d["actions"]), 75)
        ids = [a["id"] for a in d["actions"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(re.fullmatch(r"CF-ACT-\d{3}", i) for i in ids))
        for action in d["actions"]:
            self.assertIn(action["zone"], {"now", "soon", "ready", "conditional", "optional", "waiting", "assistant"})
            self.assertIn(action["owner"], {"owner", "assistant"})
            for key in ("title", "detail", "action", "priority", "proof", "caution", "label"):
                self.assertTrue(action[key].strip())
            for key in ("link", "source"):
                parsed = urlparse(action[key])
                self.assertEqual(parsed.scheme, "https")
                self.assertTrue(parsed.hostname)
                self.assertFalse(parsed.username or parsed.password)

    def test_integrated_into_existing_launcher(self):
        self.assertIn('href="#owner-actions"', self.html)
        self.assertIn('href="./owner-actions.css"', self.html)
        self.assertIn('src="./owner-actions.js"', self.html)
        self.assertIn('id="owner-actions"', self.script)
        self.assertIn('id="oa-items"', self.script)
        self.assertIn("checkedLocally", self.script)
        self.assertIn("cf-spider-view", self.script)
        self.assertIn("core.connect", self.script)
        self.assertIn("indexed-chat", (ROOT / "spider-core.js").read_text(encoding="utf-8"))
        self.assertIn("oa-clear-private", self.script)
        self.assertIn("link-vault/spider-hp/README.md", self.script)
        self.assertNotIn("Spider-HP.ps1 -Execute", self.script)
        self.assertIn("oa-project-select", self.script)
        self.assertIn("Project link set locally", self.script)
        self.assertIn("privateActions=[]", self.script)
        self.assertIn("I checked — add to My turn", self.script)
        self.assertIn('if(a.source&&urlOK(a.source))', self.script)

        self.assertIn('id="oa-cf200"', self.script)
        self.assertIn("/main/automation_200/registry.json", self.script)
        self.assertIn("not HP/payment proof", self.script)
        self.assertNotIn('method:"POST"', self.script)
        self.assertIn('src="./spider-core.js"', self.html)
        self.assertIn('src="./spider-shell.js"', self.html)
        self.assertIn("ownerActionChecks", self.enhance)
        self.assertIn("cf-owner-checks-updated", self.enhance)

    def test_directory_and_offline_assets(self):
        self.assertEqual(len(self.links["links"]), len({x["id"] for x in self.links["links"]}))
        matched = [x for x in self.links["links"] if x["url"].endswith("/link-vault/#owner-actions")]
        self.assertEqual(len(matched), 1)
        for name in ("owner-actions.js", "spider-core.js", "spider-shell.js", "owner-actions.css", "owner-actions.json"):
            self.assertTrue((ROOT / name).is_file())
            self.assertIn("./" + name, self.sw)
        self.assertIn("cf-link-vault-v7", self.sw)

    def test_public_data_excludes_private_tokens_and_raw_chat_links(self):
        for item in self.data["actions"]:
            for key in ("link", "source"):
                url = item[key].lower()
                self.assertNotIn("chatgpt.com/c/", url)
                self.assertNotIn("access_token=", url)
                self.assertNotIn("password=", url)
                self.assertNotIn("token=", url)
            self.assertNotIn("@gmail.com", json.dumps(item).lower())


if __name__ == "__main__":
    unittest.main()
