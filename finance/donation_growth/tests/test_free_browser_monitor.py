"""Offline tests for the no-cost, read-only browser monitor.

No network, browser, login, payment or public social posting is run here.
"""
import importlib.util
from pathlib import Path
import unittest


MODULE = Path(__file__).resolve().parents[1] / "free_browser_monitor.py"
spec = importlib.util.spec_from_file_location("free_browser_monitor", MODULE)
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


class FreePromotionMonitorTests(unittest.TestCase):
    def test_only_known_public_https_get_targets(self):
        self.assertEqual(len(monitor.TARGETS), 4)
        self.assertEqual(len(set(monitor.TARGETS)), 4)
        for _, url in monitor.TARGETS:
            self.assertTrue(url.startswith("https://"))
            self.assertNotIn("/submit", url)
            self.assertNotIn("cash.app", url)
            self.assertNotIn("token", url)

    def test_owned_pages_are_only_reachable_with_correct_copy(self):
        self.assertEqual(
            monitor.classify_owned_site(
                200, "Clarity Card", "One hard question. One clear next step.", "clarity_card"
            ),
            "reachable",
        )
        self.assertEqual(
            monitor.classify_owned_site(200, "Verify you are human", "", "clarity_card"),
            "unverified",
        )
        self.assertEqual(
            monitor.classify_owned_site(
                200, "First Drop", "Get in before the world knows what it is.", "first_drop"
            ),
            "reachable",
        )
        self.assertEqual(
            monitor.classify_owned_site(200, "Caveman Focus", "", "support_campaign"),
            "reachable",
        )
        self.assertEqual(
            monitor.classify_owned_site(404, "Unavailable", "", "clarity_card"),
            "unavailable",
        )
        self.assertEqual(
            monitor.classify_owned_site(429, "Rate limited", "", "first_drop"),
            "unverified",
        )

    def test_approved_external_listing_needs_real_canonical_link(self):
        self.assertEqual(
            monitor.classify_listing(
                200,
                "Caveman Focus | Hype Star",
                "Caveman Focus — free clarity worksheet",
                [monitor.CLARITY_URL, "https://hypestar.org/"],
            ),
            "public_listing_observed",
        )
        self.assertEqual(
            monitor.classify_listing(
                200, "Caveman Focus | Hype Star",
                "Caveman Focus Clarity Card awaiting review", ["https://example.com/"]
            ),
            "unverified",
        )
        self.assertEqual(
            monitor.classify_listing(
                200, "Other project", "Caveman Focus mentioned", [monitor.CLARITY_URL]
            ),
            "public_listing_observed",
        )  # only matching name+link, not independent endorsement
        self.assertEqual(
            monitor.classify_listing(404, "Not Found", "", []),
            "not_public_as_checked",
        )

    def test_rate_limits_and_challenges_are_unknown_not_rejections(self):
        for status in (None, 401, 403, 429, 500, 503):
            with self.subTest(status=status):
                self.assertEqual(
                    monitor.classify_listing(status, "Caveman Focus", "", [monitor.CLARITY_URL]),
                    "unverified",
                )

    def test_summary_does_not_infer_income_or_posting(self):
        report = {
            "checks": {
                "clarity_card": {"status": "reachable"},
                "first_drop": {"status": "reachable"},
                "support_campaign": {"status": "unverified"},
                "hype_star_listing": {"status": "not_public_as_checked"},
            }
        }
        summary = monitor.summarize(report)
        self.assertIn("No accounts, posts, submissions", summary)
        self.assertIn("PromoteIndex ticket #097", summary)
        self.assertNotIn("donation received", summary)
        self.assertIn("not_public_as_checked", summary)

    def test_script_has_no_form_or_outbound_post_mechanism(self):
        source = MODULE.read_text(encoding="utf-8")
        self.assertIn("page.goto(", source)
        for forbidden in (
            "page.click(",
            "page.fill(",
            "page.locator(\"button\").click(",
            "request.post(",
            "requests.post(",
            "urllib.request.urlopen(",
            "storage_state=",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
