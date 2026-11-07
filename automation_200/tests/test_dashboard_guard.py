"""Offline regression tests for the public CF-0 dashboard consistency audit."""
import json
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dashboard_guard import check, git_blob_sha


def fixture():
    data = {
        "target": 2, "completed": 1,
        "tasks": [
            {"id": "CF-001", "status": "verified", "stream": "security", "physical_hp_required": False, "depends_on": []},
            {"id": "CF-002", "status": "planned", "stream": "security", "physical_hp_required": False, "depends_on": ["CF-001"]},
        ],
    }
    raw = json.dumps(data).encode()
    board = f"""# Example
## Status at a glance
| CF-200 work orders | **1 verified / 2 total**; 1 planned |
| Open GitHub issues | **1** returned |
**Evidence:** source blob \`{git_blob_sha(raw)}\`.
## What is being worked on next?
| Priority | Task | What | Status |
| P0 | **CF-002** | Source task | Planned |
## Open GitHub Issues
- [#1](https://github.com/whoiwts110217-creator/CF-0/issues/1)
## How regular updates work
Example
"""
    return data, raw, board


class DashboardGuardTests(unittest.TestCase):
    def test_matching(self):
        _, raw, board = fixture()
        self.assertEqual(check(raw, board), [])

    def test_stale_count_and_blob(self):
        data, raw, board = fixture()
        data["tasks"][1]["status"] = "verified"
        data["completed"] = 2
        errors = check(json.dumps(data).encode(), board)
        self.assertTrue(any("counts" in e for e in errors))
        self.assertTrue(any("blob" in e for e in errors))
        self.assertTrue(any("completed/unplanned" in e for e in errors))

    def test_candidate_with_unverified_dependency(self):
        data, raw, board = fixture()
        data["tasks"][0]["status"] = "planned"
        data["completed"] = 0
        updated = board.replace("**1 verified / 2 total**; 1 planned", "**0 verified / 2 total**; 2 planned")
        updated = updated.replace(git_blob_sha(raw), git_blob_sha(json.dumps(data).encode()))
        self.assertTrue(any("dependencies" in e for e in check(json.dumps(data).encode(), updated)))

    def test_private_hp_candidate_cannot_be_promoted(self):
        data, raw, board = fixture()
        data["tasks"][1]["physical_hp_required"] = True
        updated = board.replace(git_blob_sha(raw), git_blob_sha(json.dumps(data).encode()))
        self.assertTrue(any("device/owner-only" in e for e in check(json.dumps(data).encode(), updated)))

    def test_unverified_issue_not_silently_counted_zero(self):
        _, raw, board = fixture()
        broken = board.replace("**1** returned", "**0** returned")
        self.assertTrue(any("issue count" in e for e in check(raw, broken)))

    def test_corrupt_registry_fails_closed(self):
        _, _, board = fixture()
        self.assertTrue(check(b"{bad", board))


if __name__ == "__main__":
    unittest.main()
