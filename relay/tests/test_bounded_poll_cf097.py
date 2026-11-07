"""CF-097: bounded poll-work regression tests, no network or HP required.

Tests use in-memory fake queue plus temporary SQLite; no public commands sent.
"""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay


def job(number):
    item = relay.make_job("ping")
    item["id"] = f"{number:08x}-0000-4000-8000-{number:012x}"
    return item


class FakeRepo:
    def __init__(self, jobs):
        self.jobs = {j["id"] + ".json": j for j in jobs}
        self.published = []

    def files(self):
        return sorted(self.jobs)

    def load(self, name):
        return self.jobs[name]

    def publish(self, jid, receipt):
        self.published.append(jid)
        return True


class BoundedPollWorkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = relay.State(pathlib.Path(self.tmp.name) / "state.sqlite3")

    def test_at_most_four_actions_in_one_poll(self):
        repo = FakeRepo([job(i) for i in range(1, 15)])
        result = relay.tick(repo, self.state)
        self.assertEqual(result["executed"], relay.MAX_ACTIONS)
        self.assertEqual(result["scanned"], relay.MAX_ACTIONS)
        self.assertEqual(len(repo.published), relay.MAX_ACTIONS)
        self.assertEqual(self.state.count(), relay.MAX_ACTIONS)

    def test_at_most_eighty_scans_when_every_job_invalid(self):
        repo = FakeRepo([job(i) for i in range(1, 95)])
        for value in repo.jobs.values():
            value["expires"] = value["issued"] - 1
        result = relay.tick(repo, self.state)
        self.assertEqual(result["scanned"], relay.MAX_SCAN)
        self.assertEqual(result["executed"], 0)
        self.assertEqual(len(result["errors"]), relay.MAX_SCAN)
        self.assertEqual(self.state.count(), 0)

    def test_cursor_allows_next_poll_to_advance_without_duplicate_execution(self):
        repo = FakeRepo([job(i) for i in range(1, 9)])
        first = relay.tick(repo, self.state)
        second = relay.tick(repo, self.state)
        self.assertEqual((first["executed"], second["executed"]), (4, 4))
        self.assertEqual(self.state.count(), 8)
        self.assertEqual(len(set(repo.published)), 8)

    def test_uncertain_attempt_does_not_execute_again(self):
        item = job(1)
        digest = relay.sha(item)
        self.assertTrue(self.state.begin(item["id"], digest))
        repo = FakeRepo([item])
        result = relay.tick(repo, self.state)
        self.assertEqual(result["uncertain"], 1)
        self.assertEqual(result["executed"], 0)
        self.assertEqual(self.state.count(), 0)
        self.assertEqual(repo.published, [])


if __name__ == "__main__":
    unittest.main()
