"""Source-only public credibility gate: no network, payments, or HP access."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PublicFrontDoorTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_free_method_precedes_support_on_home(self):
        home = self.read("index.html")
        free = 'Try the free 60-second exercise'
        support = 'Support voluntarily — First Drop'
        self.assertIn(free, home)
        self.assertIn(support, home)
        self.assertLess(home.index(free), home.index(support))
        self.assertIn('https://github.com/whoiwts110217-creator/CF-0/issues/21', home)
        self.assertIn('not the same as a deployed autonomous system', home)

    def test_donor_and_contributor_credit_are_distinct(self):
        first_drop = self.read("first-drop/index.html")
        campaign = self.read("docs/FIRST_DROP_CAMPAIGN_2026-11-09.md")
        hall = self.read("docs/HALL_OF_FAME.md")
        self.assertIn('Contributors &amp; Discoveries', first_drop)
        self.assertIn('payment is verified', first_drop)
        self.assertIn('chosen display name is confirmed as consensual', first_drop)
        self.assertIn('no verified public supporter names', first_drop.lower())
        self.assertIn('Contributors & Discoveries', campaign)
        self.assertIn('recognizes reviewed contributions, not donations', hall)
        self.assertNotIn("Give any amount and you're in.", campaign)
        self.assertIn('not tax-deductible charitable donations', first_drop)

    def test_free_route_and_translation_exist(self):
        first_drop = self.read("first-drop/index.html")
        translation = self.read("i18n/home.mjs")
        self.assertIn('Try the free 60-second exercise', first_drop)
        self.assertIn('https://github.com/whoiwts110217-creator/CF-0/issues/21', first_drop)
        for label in ('Try the free 60-second exercise',
                      'Support voluntarily — First Drop'):
            self.assertIn('"' + label + '": {', translation)
        for locale in ('"es":', '"fr":', '"pt":'):
            self.assertIn(locale, translation)

if __name__ == "__main__":
    unittest.main()
