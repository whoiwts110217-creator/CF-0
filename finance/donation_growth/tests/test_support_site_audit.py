"""Offline support-site probe tests, without network requests."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from support_site_audit import inspect_html, SameHostHTTPSRedirect, TARGET
from urllib.error import URLError
from urllib.request import Request

class SiteAuditTest(unittest.TestCase):
    def test_static_html_fields(self):
        page = """<!doctype html><html lang="en"><head><title>Caveman Focus Support</title>
        <meta name="viewport" content="width=device-width, initial-scale=1"></head>
        <body>Caveman Focus <a href="https://cash.app/$LAZYBLACKBEAN">Support</a>
        If you don't want to give, don't.</body></html>"""
        v = inspect_html(page)
        self.assertTrue(v["title_present"])
        self.assertEqual(v["html_lang"], "en")
        self.assertTrue(v["viewport_meta_present"])
        self.assertTrue(v["static_cash_app_anchor_present"])
        self.assertTrue(v["static_caveman_focus_text_present"])
        self.assertTrue(v["static_voluntary_support_text_present"])

    def test_js_mention_is_not_a_static_anchor(self):
        v = inspect_html('<html><script>let link="https://cash.app/$LAZYBLACKBEAN"</script></html>')
        self.assertFalse(v["static_cash_app_anchor_present"])
        self.assertTrue(v["static_html_only"])

    def test_cash_app_impostor_not_accepted(self):
        v = inspect_html('<a href="https://cash.app.attacker.example/pay">Support</a>')
        self.assertFalse(v["static_cash_app_anchor_present"])

    def test_external_redirect_disallowed(self):
        with self.assertRaises(URLError):
            SameHostHTTPSRedirect().redirect_request(
                Request(TARGET), None, 302, "redirect", {}, "https://cash.app/"
            )

if __name__ == "__main__":
    unittest.main()
