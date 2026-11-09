"""No-network tests for conservative create-only task claim requests."""
import json
import unittest
from datetime import datetime, timedelta, timezone

from claim_envelope import create_only_claim_payload
from parallel_guard import Claim, ConflictError

NOW = datetime(2026, 11, 7, 20, 0, tzinfo=timezone.utc)
SHA = "a" * 40


def claim(task="CF-097", worker="operator-a", sha=SHA, paths=("docs/a.md",), lifetime=600):
    return Claim(task, worker, sha, paths, NOW + timedelta(seconds=lifetime))


class ClaimEnvelopeTests(unittest.TestCase):
    def test_valid_claim_is_deterministic_and_sorted(self):
        a = claim(paths=("docs/b.md", "docs/a.md"))
        p, content = create_only_claim_payload(a, NOW)
        p2, content2 = create_only_claim_payload(a, NOW)
        self.assertEqual((p, content), (p2, content2))
        self.assertEqual(p, "experiments/parallel_coordination/claims/CF-097.json")
        self.assertEqual(json.loads(content)["paths"], ["docs/a.md", "docs/b.md"])
        self.assertEqual(json.loads(content)["status"], "pending_unverified")

    def test_different_workers_cannot_change_path_for_same_task(self):
        p, _ = create_only_claim_payload(claim(worker="worker-a"), NOW)
        p2, _ = create_only_claim_payload(claim(worker="worker-b"), NOW)
        self.assertEqual(p, p2)

    def test_different_task_uses_different_path(self):
        a, _ = create_only_claim_payload(claim(task="CF-097"), NOW)
        b, _ = create_only_claim_payload(claim(task="CF-098"), NOW)
        self.assertNotEqual(a, b)

    def test_expired_claim_rejected(self):
        with self.assertRaisesRegex(ConflictError, "invalid_claim_lifetime"):
            create_only_claim_payload(claim(lifetime=0), NOW)

    def test_overlong_claim_rejected(self):
        with self.assertRaisesRegex(ConflictError, "invalid_claim_lifetime"):
            create_only_claim_payload(claim(lifetime=3601), NOW)

    def test_invalid_ids_rejected(self):
        for task in ("CF-000", "CF-201", "CF-1", "../../CF-097", "CF-097.json"):
            with self.subTest(task=task), self.assertRaises(ValueError):
                create_only_claim_payload(claim(task=task), NOW)

    def test_invalid_worker_rejected(self):
        with self.assertRaises(ValueError):
            create_only_claim_payload(claim(worker="../worker"), NOW)

    def test_noncanonical_relative_path_rejected(self):
        with self.assertRaisesRegex(ValueError, "canonical repository paths"):
            create_only_claim_payload(claim(paths=("docs/./a.md",)), NOW)

    def test_unverified_source_sha_rejected(self):
        with self.assertRaises(ValueError):
            create_only_claim_payload(claim(sha="abc"), NOW)

    def test_local_time_is_normalized_to_utc(self):
        local = NOW.astimezone(timezone(timedelta(hours=-5)))
        p, content = create_only_claim_payload(claim(), local)
        self.assertEqual(json.loads(content)["created_at"], NOW.isoformat())
        self.assertTrue(p.endswith("CF-097.json"))

    def test_automatic_reclaim_not_authorized(self):
        _, content = create_only_claim_payload(claim(), NOW)
        self.assertEqual(json.loads(content)["release_policy"],
                         "no_automatic_reclaim_or_remote_execution")


if __name__ == "__main__":
    unittest.main()
