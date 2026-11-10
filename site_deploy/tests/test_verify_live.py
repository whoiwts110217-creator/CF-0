import json
import tempfile
import unittest
from urllib.parse import urlparse

from site_deploy.verify_live import SCHEMA, ROUTES, write_manifest, verify_once, verify_with_retry


BASE = "https://whoiwts110217-creator.github.io/CF-0/"
SHA = "a" * 40
RUN = "42767535240"
CATALOG = json.dumps({"schema": "cf.link.vault.public.v2", "revision": "test-v2",
                      "links": [{"id": str(i), "url": "https://example.org/" + str(i)}
                                for i in range(78)]}, sort_keys=True).encode()


def fixture_fetch(url):
    path = urlparse(url).path.removeprefix("/CF-0/")
    if path == "deployment-manifest.json":
        return json.dumps({"schema": SCHEMA, "source_commit": SHA, "workflow_run_id": RUN}).encode()
    if path == "link-vault/links.json":
        return CATALOG
    if path in ROUTES:
        return ("<!doctype html><html><body>" + ROUTES[path] + "</body></html>").encode()
    raise ValueError(f"Unexpected route: {path}")


class PagesVerifierTest(unittest.TestCase):
    def test_manifest_generated_from_exact_source_and_run(self):
        with tempfile.TemporaryDirectory() as d:
            path = write_manifest(d, SHA, RUN)
            manifest = json.loads(path.read_text())
            self.assertEqual(manifest, {"schema": SCHEMA, "source_commit": SHA, "workflow_run_id": RUN})

    def test_manifest_refuses_invalid_source_or_run(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                write_manifest(d, "not-a-sha", RUN)
            with self.assertRaises(ValueError):
                write_manifest(d, SHA, "abc")

    def test_live_routes_and_matching_release(self):
        verify_once(BASE, SHA, RUN, fetch=fixture_fetch)

    def test_live_link_vault_catalog_must_match_checkout(self):
        verify_once(BASE, SHA, RUN, fetch=fixture_fetch, expected_catalog=CATALOG)
        with self.assertRaisesRegex(ValueError, "stale or mismatched"):
            verify_once(BASE, SHA, RUN, fetch=fixture_fetch, expected_catalog=b"{}")

    def test_live_link_vault_catalog_invalid_schema_is_rejected(self):
        def broken(url):
            if url.endswith("link-vault/links.json"):
                return b'{"schema":"wrong","links":[]}'
            return fixture_fetch(url)
        with self.assertRaisesRegex(ValueError, "schema or entries"):
            verify_once(BASE, SHA, RUN, fetch=broken,
                        expected_catalog=b'{"schema":"wrong","links":[]}')

    def test_mismatched_release_refused(self):
        with self.assertRaisesRegex(ValueError, "mismatched"):
            verify_once(BASE, "b"*40, RUN, fetch=fixture_fetch)
        with self.assertRaisesRegex(ValueError, "mismatched"):
            verify_once(BASE, SHA, "999", fetch=fixture_fetch)

    def test_missing_html_marker_refused(self):
        def missing(url):
            if url.endswith("clarity-card/"):
                return b"<html>404 Not Found</html>"
            return fixture_fetch(url)
        with self.assertRaisesRegex(ValueError, "Clarity Card"):
            verify_once(BASE, SHA, RUN, fetch=missing)

    def test_retry_recovers_delayed_cdn(self):
        attempts = []
        delays = []
        def fetch(url):
            if url.endswith("deployment-manifest.json"):
                attempts.append(url)
                if len(attempts) == 1:
                    return json.dumps({"schema": SCHEMA, "source_commit": "b"*40, "workflow_run_id": RUN}).encode()
            return fixture_fetch(url)
        verify_with_retry(BASE, SHA, RUN, fetch=fetch, sleep=delays.append, attempts=3, delay=0)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(delays, [0])

    def test_bounded_failure_clear(self):
        with self.assertRaisesRegex(RuntimeError, "not verified after 2 attempts"):
            verify_with_retry(BASE, SHA, RUN, fetch=lambda u: b"garbage", sleep=lambda _: None,
                              attempts=2, delay=0)

    def test_https_required(self):
        with self.assertRaisesRegex(ValueError, "https"):
            verify_once("http://example.com/CF-0/", SHA, RUN, fetch=fixture_fetch)


if __name__ == "__main__":
    unittest.main()
