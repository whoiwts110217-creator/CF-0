"""CF-0 prompt-change governance checks: source integrity and regression examples."""
import json
import tempfile
import unittest
from pathlib import Path

from automation_200.prompt_change_guard import ROOT, audit, PROMPTS, LOG, BIN


class PromptChangeGuardTests(unittest.TestCase):
    def fixture(self, root):
        for path in (*PROMPTS, LOG, BIN):
            dest = root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT / path).read_bytes())

    def test_committed_public_prompts_are_tracked(self):
        self.assertEqual(audit(ROOT), [])

    def test_windows_crlf_checkout_does_not_look_like_unlogged_edit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            for path in PROMPTS:
                prompt = root / path
                raw = prompt.read_bytes().replace(b"\r\n", b"\n")
                prompt.write_bytes(raw.replace(b"\n", b"\r\n"))
            self.assertEqual(audit(root), [], "Only checkout line endings changed")

    def test_missing_priority_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            prompt = root / PROMPTS[0]
            prompt.write_text(prompt.read_text(encoding="utf-8").replace("P2 — Financial operations", "P2 removed"), encoding="utf-8")
            problems = audit(root)
            self.assertTrue(any("P2 — Financial operations" in p for p in problems))
            self.assertTrue(any("latest recorded blob" in p for p in problems))

    def test_silent_edit_and_missing_log_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            prompt = root / PROMPTS[2]
            prompt.write_bytes(prompt.read_bytes() + b"\n# Unrecorded change\n")
            self.assertTrue(any("latest recorded blob" in p for p in audit(root)))
            (root / LOG).unlink()
            self.assertTrue(any("Missing append-only" in p for p in audit(root)))


    def test_multipath_integrity_rejects_invalid_subcommits_and_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            log = root / LOG
            original = log.read_text(encoding="utf-8").splitlines()
            rows = [json.loads(line) for line in original]
            index = next(i for i, event in enumerate(rows) if event["id"] == "PCE-012")
            self.assertEqual(len(rows[index]["paths"]), 3)
            for problem, mutate in (
                ("Invalid nested commit SHA", lambda record: record["paths"][0].update(commit="not-a-sha")),
                ("Invalid nested result blob SHA", lambda record: record["paths"][0].update(after_blob_sha="bad")),
                ("Unknown or duplicated prompt path", lambda record: record["paths"][1].update(path=record["paths"][0]["path"])),
            ):
                with self.subTest(problem=problem):
                    changed = [json.loads(line) for line in original]
                    mutate(changed[index])
                    log.write_text("\n".join(json.dumps(v, separators=(",", ":")) for v in changed)+"\n", encoding="utf-8")
                    self.assertTrue(any(problem in p for p in audit(root)))
            log.write_text("\n".join(original)+"\n", encoding="utf-8")
            self.assertEqual(audit(root), [], "Unmodified multi-prompt history must be accepted")

    def test_multipath_must_not_claim_extra_authority_or_hide_missing_records(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            log = root / LOG
            rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
            index = next(i for i, event in enumerate(rows) if event["id"] == "PCE-012")
            rows[index]["paths"] = []
            log.write_text("\n".join(json.dumps(v) for v in rows)+"\n", encoding="utf-8")
            self.assertTrue(any("Invalid multi-path change record" in p for p in audit(root)))


if __name__ == "__main__":
    unittest.main()
