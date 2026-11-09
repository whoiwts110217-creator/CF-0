"""CF-120: offline, no-write acceptance checks for registry HTML renderer."""
import copy
import hashlib
from html import escape
import json
from pathlib import Path
import unittest

from automation_200.registry_view import render
from automation_200.validate_registry import RegistryValidationError

ROOT = Path(__file__).resolve().parents[1]

class RegistryViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "registry.json").read_bytes()
        cls.registry = json.loads(cls.source)

    def test_all_200_ids_once_and_authoritative_counts(self):
        page = render(self.source)
        self.assertEqual(page.count("<tbody><tr>"), 1)
        self.assertEqual(page.split("<tbody>", 1)[1].split("</tbody>", 1)[0].count("<tr>"), 200)
        self.assertIn(f'{self.registry["completed"]} verified / 200 total; {200 - self.registry["completed"]} planned', page)
        for task in self.registry["tasks"]:
            self.assertEqual(page.count("<td>" + task["id"] + "</td>"), 1)
        self.assertIn(hashlib.sha256(self.source).hexdigest(), page)

    def test_escapes_untrusted_text_and_does_not_mutate_source(self):
        data = copy.deepcopy(self.registry)
        data["tasks"][-1]["title"] = '<script>alert("x")</script>'
        original = json.dumps(data, sort_keys=True).encode()
        page = render(original)
        self.assertNotIn("<script>", page)
        self.assertIn(escape(data["tasks"][-1]["title"], quote=True), page)
        self.assertEqual(original, json.dumps(data, sort_keys=True).encode())

    def test_rejects_corrupt_registry_before_render(self):
        data = copy.deepcopy(self.registry)
        data["tasks"].pop()
        with self.assertRaises(RegistryValidationError):
            render(json.dumps(data).encode())

    def test_repeatable_snapshot(self):
        self.assertEqual(render(self.source), render(self.source))

if __name__ == "__main__":
    unittest.main()
