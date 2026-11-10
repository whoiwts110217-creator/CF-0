"""Open every ZIP emitted by the real Foundry generator, not just its ZIP header.

The test extracts the local inline JavaScript in Node, writes synthetic archives
to a disposable directory, and uses Python's standard zipfile reader to check
the central directory, CRCs, filenames and byte-for-byte content. No accounts,
network, paid services or real customer data are involved.
"""
import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE_SCRIPT = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('iphone-skill-foundry/index.html', 'utf8');
const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
if (scripts.length !== 2) throw Error('Expected original inline generator and UI scripts');
const context = {module: {exports: {}}, TextEncoder, TextDecoder, Uint8Array, Uint32Array, DataView, Blob};
vm.runInNewContext(scripts[0], context, {filename: 'foundry-generator.js'});
const mode = process.argv[3];
const input = {
  name: mode === 'pack' ? 'Caveman Focus — ZIP integrity' : 'Résumé / UTF-8 skill',
  philosophy: 'Test UTF-8 round trip: 科学 ⚙️ 🧠',
  goal: 'Keep evidence separate from unverified outputs.',
  trigger: 'Use when testing ZIP archives.',
  principles: 'Protect continuity | Record real versions | Verify checks\nNo fake claims | Label simulations | Preserve honest evidence',
  examples: 'Situation: Test a local draft\nAction: Check that the ZIP is readable\nOutcome: Synthetic testing only\nEvidence: unverified',
  mode,
  source: 'Local synthetic test, not external evidence'
};
const built = context.module.exports.build(input);
(async () => {
  const bytes = new Uint8Array(await context.module.exports.zip(built.files).arrayBuffer());
  fs.writeFileSync(process.argv[1], bytes);
  fs.writeFileSync(process.argv[2], JSON.stringify(built.files), 'utf8');
})().catch(err => { console.error(err); process.exitCode = 1; });
"""


class ZipRoundTripTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("node"):
            raise RuntimeError("Node is required: ZIP roundtrip test cannot silently skip")

    def exercise(self, mode):
        with tempfile.TemporaryDirectory(prefix="cf0-zip-test-") as tmp:
            archive = Path(tmp) / "generated.zip"
            manifest = Path(tmp) / "expected.json"
            completed = subprocess.run(
                ["node", "-e", NODE_SCRIPT, str(archive), str(manifest), mode],
                cwd=ROOT.parent,
                capture_output=True,
                text=True,
                timeout=25,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            expected = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(expected), 4)
            self.assertTrue(archive.is_file())
            with zipfile.ZipFile(archive, "r") as zf:
                names = zf.namelist()
                self.assertEqual(len(names), len(set(names)), "Duplicate ZIP paths")
                self.assertEqual(set(names), set(expected), "Central directory does not match generated files")
                self.assertIsNone(zf.testzip(), "Invalid ZIP CRC or truncated member")
                self.assertTrue(any(p.endswith("/SKILL.md") for p in names))
                self.assertTrue(any(p.endswith("/EVALS.json") for p in names))
                for member in zf.infolist():
                    self.assertEqual(member.compress_type, zipfile.ZIP_STORED)
                    self.assertFalse(member.filename.startswith("/"))
                    self.assertNotIn("..", Path(member.filename).parts)
                    self.assertLess(member.file_size, 30_000_000)
                    self.assertEqual(zf.read(member), expected[member.filename].encode("utf-8"))
                    if member.filename.endswith("EVALS.json"):
                        obj = json.loads(zf.read(member))
                        self.assertEqual(obj["automated_pass_count"], 0)
                        self.assertTrue(all(s["status"] == "not_run" for s in obj["scenarios"]))

    def test_pack_roundtrip_with_unicode(self):
        self.exercise("pack")

    def test_single_roundtrip_with_unicode(self):
        self.exercise("single")


if __name__ == "__main__":
    unittest.main()
