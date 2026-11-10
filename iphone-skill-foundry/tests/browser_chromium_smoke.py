"""Real Chromium smoke tests for the existing iPhone Skill Foundry.

This test uses an ephemeral loopback HTTP server and synthetic SKILL.md fixtures.
It performs actual browser clicks/downloads; unlike a fake DOM harness, it runs
in a real browser engine. It does NOT test physical iOS Safari or external agents.
The test fails closed if Chrome or Playwright is unavailable in the runner.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import threading
import unittest
import zipfile
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

APP = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class ChromiumSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium")
        if not cls.chrome:
            raise RuntimeError("Chrome/Chromium not installed; cannot claim real-browser verification")
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(APP)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/index.html"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory(prefix="cf0-real-chrome-")
        self.addCleanup(self.dir.cleanup)
        self.p = sync_playwright().start()
        self.addCleanup(self.p.stop)
        self.browser = self.p.chromium.launch(
            executable_path=self.chrome, headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        self.addCleanup(self.browser.close)
        self.context = self.browser.new_context(
            viewport={"width": 390, "height": 844}, device_scale_factor=3,
            is_mobile=True, has_touch=True, accept_downloads=True
        )
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.errors = []
        self.external = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.on("request", lambda r: self.external.append(r.url) if not r.url.startswith(self.url.rsplit("/", 1)[0] + "/") else None)
        self.page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(self.url.rsplit("/", 1)[0] + "/") else route.abort())
        self.page.goto(self.url, wait_until="load", timeout=15000)
        expect(self.page.locator("#runStatus")).to_have_text("DRAFT")
        self.assertFalse(self.errors, f"Browser JavaScript exceptions: {self.errors}")

    def test_actual_zip_download_and_help_panel(self):
        help_button = self.page.locator('button[aria-controls="action-help-downloadZip"]')
        help_panel = self.page.locator("#action-help-downloadZip")
        self.assertFalse(help_panel.is_visible())
        help_button.click()
        self.assertTrue(help_panel.is_visible())

        self.page.locator("#name").fill("Synthetic Browser ZIP Test")
        self.page.locator("#skillForm button[type=submit]").click()
        expect(self.page.locator("#runStatus")).to_have_text("DRAFT")
        with self.page.expect_download(timeout=12000) as info:
            self.page.locator("#downloadZip").click()
        download = info.value
        out = Path(self.dir.name) / download.suggested_filename
        download.save_as(out)
        self.assertIn("zip", out.suffix)
        self.assertIn("download requested", self.page.locator("#feedback").inner_text().lower())
        self.assertNotIn("saved successfully", self.page.locator("#feedback").inner_text().lower())
        with zipfile.ZipFile(out) as archive:
            names = archive.namelist()
            self.assertTrue(any(n.endswith("/SKILL.md") for n in names))
            self.assertTrue(any(n.endswith("EVALS.json") for n in names))
            self.assertIsNone(archive.testzip())
            for name in names:
                if name.endswith("EVALS.json"):
                    content = json.loads(archive.read(name))
                    self.assertTrue(all(x["status"] == "not_run" for x in content["scenarios"]))
        self.assertFalse(self.errors, self.errors)
        self.assertFalse(self.external, f"External network requests not expected: {self.external}")

    def test_local_skill_comparison_and_unrun_packet(self):
        initial = Path(self.dir.name) / "older-SKILL.md"
        initial_bytes = b"---\nname: old-version\n---\nUnverified baseline skill.\n"
        initial.write_bytes(initial_bytes)
        self.page.locator("#reviewBaseline").set_input_files(str(initial))
        skill_options = self.page.locator("#previewFile option").evaluate_all(
            "(els) => els.map(e => e.value).filter(v => v.endsWith('/SKILL.md'))"
        )
        self.assertTrue(skill_options)
        self.page.locator("#previewFile").select_option(skill_options[0])
        self.page.locator("#reviewCompareGenerated").click()
        expect(self.page.locator("#reviewResults")).to_contain_text("TWO DISTINCT FILES", timeout=12000)
        with self.page.expect_download(timeout=12000) as info:
            self.page.locator("#reviewDownload").click()
        download = info.value
        dst = Path(self.dir.name) / download.suggested_filename
        download.save_as(dst)
        packet = json.loads(dst.read_text(encoding="utf-8"))
        self.assertEqual(packet["baseline_sha256"], hashlib.sha256(initial_bytes).hexdigest())
        self.assertEqual(packet["status"], "needs_evidence")
        self.assertEqual(packet["hard_gates"], {})
        self.assertEqual(packet["judges"], [])
        self.assertEqual({t["kind"] for t in packet["test_runs"]}, {"normal", "ambiguous", "failure"})
        self.assertTrue(all(t["mode"] == "not_run" and t["candidate_pass"] is None for t in packet["test_runs"]))
        self.assertNotIn("Unverified baseline skill.", dst.read_text(encoding="utf-8"))

        generated = self.page.locator("#preview").text_content()
        other = Path(self.dir.name) / "same-SKILL.md"
        other.write_text(generated, encoding="utf-8")
        self.page.locator("#reviewBaseline").set_input_files(str(other))
        self.page.locator("#reviewCandidate").set_input_files(str(other))
        self.page.locator("#reviewCompareFiles").click()
        expect(self.page.locator("#reviewResults")).to_contain_text("SAME FILE CONTENT", timeout=12000)
        self.assertFalse(self.errors, self.errors)
        self.assertFalse(self.external, self.external)


if __name__ == "__main__":
    unittest.main()
