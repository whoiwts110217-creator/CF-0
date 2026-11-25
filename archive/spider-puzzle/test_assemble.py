"""Assembly acceptance: reproducibility, source provenance, tampering and real objects."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

SPEC = importlib.util.spec_from_file_location("spider_assembly_builder", Path(__file__).with_name("assemble.py"))
assembly = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assembly)


class AssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = assembly.read_catalog()

    def test_complete_original_sources_and_all_piece_hashes(self):
        files = assembly.verify_catalog(self.data)
        self.assertEqual(len(files), 94)
        self.assertIn("spider/brain.py", files)
        self.assertIn("spider/gui_live.py", files)
        self.assertEqual(sum(p.startswith("tests/") for p in files), 42)

    def test_changed_original_source_fails_before_packaging(self):
        data = copy.deepcopy(self.data)
        data["sources"]["spider/brain.py"] += "\n# tampered\n"
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            assembly.package_files(data)

    def test_rehashing_tampered_source_manifest_does_not_reauthorize_source(self):
        data = copy.deepcopy(self.data)
        data["sources"][assembly.SOURCE_MANIFEST] += " "
        with self.assertRaisesRegex(ValueError, "manifest changed"):
            assembly.package_files(data)

    def test_changed_symbol_excerpt_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["pieces"][200]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Piece hash/length mismatch"):
            assembly.package_files(data)

    def test_wrong_source_and_duplicate_identity_fail(self):
        data = copy.deepcopy(self.data)
        data["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            assembly.package_files(data)
        data = copy.deepcopy(self.data)
        data["pieces"][1] = data["pieces"][0]
        with self.assertRaisesRegex(ValueError, "Duplicate or unstable"):
            assembly.package_files(data)

    def test_windows_and_posix_path_aliases_are_rejected(self):
        for path in ["../outside.py", "/outside.py", "C:/outside.py", "spider\\evil.py",
                     "./a.py", "a//b.py", "NUL.txt", "a./b.py", "a /b.py", "a\x00.py"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                assembly.validate_paths([path])
        for paths in [["A.py", "a.py"], ["spider", "spider/main.py"]]:
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                assembly.validate_paths(paths)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            json.loads('{"sources":{},"sources":{}}', object_pairs_hook=assembly.unique_object)

    def test_deterministic_archive_and_preserved_whole_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / "first.zip", Path(tmp) / "second.zip"
            one, two = assembly.build(first), assembly.build(second)
            self.assertEqual(one["sha256"], two["sha256"])
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(len(archive.namelist()), 98)
                for name, text in self.data["sources"].items():
                    self.assertEqual(archive.read("runtime/" + name), text.encode("utf-8"), name)
                manifest = json.loads(archive.read(assembly.MANIFEST))
                self.assertEqual(len(manifest["requested_table_piece_ids"]), 500)
                self.assertEqual(len(set(manifest["requested_table_piece_ids"])), 500)
                self.assertEqual(manifest["runtime_patches"], [])

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "owner.zip"
            output.write_bytes(b"preserve existing archive")
            with self.assertRaises(FileExistsError):
                assembly.build(output)
            self.assertEqual(output.read_bytes(), b"preserve existing archive")

    def extracted(self, tmp):
        output = Path(tmp) / "candidate.zip"
        assembly.build(output)
        folder = Path(tmp) / "candidate"
        with zipfile.ZipFile(output) as archive:
            archive.extractall(folder)
        return folder

    def run_check(self, folder):
        return subprocess.run([sys.executable, "-B", "assembled_spider.py", "--check"], cwd=folder,
                              capture_output=True, text=True, timeout=30)

    def test_clean_extraction_runs_real_ledger_and_stop_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.extracted(tmp)
            result = self.run_check(folder)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "LOCAL_SMOKE_PASSED")
            self.assertIn("ledger append/reload/hash chain", report["checks"])
            self.assertIn("stale task rejected", report["checks"])
            self.assertIn("Windows HP behavior unverified", report["evidence"])
            self.assertFalse((folder / "assembly_runtime_data").exists())

    def test_runtime_source_tamper_blocks_before_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.extracted(tmp)
            (folder / "runtime/spider/brain.py").write_text("raise RuntimeError('SHOULD_NOT_IMPORT')\n")
            result = self.run_check(folder)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Assembly hash mismatch", result.stderr)
            self.assertNotIn("SHOULD_NOT_IMPORT", result.stderr)

    def test_added_executable_source_blocks_launch(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.extracted(tmp)
            (folder / "runtime/spider/extra.py").write_text("raise RuntimeError('SHOULD_NOT_IMPORT')\n")
            result = self.run_check(folder)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unmanifested executable source", result.stderr)

    def test_original_preflight_and_upgrader_accept_after_launcher_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.extracted(tmp)
            result = self.run_check(folder)
            self.assertEqual(result.returncode, 0, result.stderr)
            script = """from pathlib import Path
import FRESH_PREFLIGHT as preflight
import APPLY_AND_START_SPIDER as upgrader
print(preflight._verify_source())
upgrader.verify_manifest(Path.cwd())
assert len(upgrader.list_tracked_files(Path.cwd())) == 93
print('ORIGINAL_PREFLIGHT_AND_UPGRADER_PASS')
"""
            result = subprocess.run([sys.executable, "-B", "-c", script], cwd=folder / "runtime",
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("ORIGINAL_PREFLIGHT_AND_UPGRADER_PASS", result.stdout)

    def test_no_display_does_not_fall_back_to_fake_gui(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.extracted(tmp)
            script = """import runpy,sys,types
m=runpy.run_path('assembled_spider.py')
def unavailable(): raise RuntimeError('TEST_NO_DISPLAY')
sys.modules['tkinter']=types.SimpleNamespace(Tk=unavailable)
m['desktop'](m['ROOT']/'unused')
"""
            result = subprocess.run([sys.executable, "-B", "-c", script], cwd=folder,
                                    capture_output=True, text=True, timeout=20)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TEST_NO_DISPLAY", result.stderr)
            self.assertFalse((folder / "unused").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
