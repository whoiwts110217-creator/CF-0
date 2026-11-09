"""Synthetic, no-network reconciliation cases; never execute writes."""
import unittest

from reconcile_writes import WriteIntent, reconcile_writes


def intent(path, before="old", after="new"):
    return WriteIntent(path, before, after)


class ReconcileTests(unittest.TestCase):
    def test_complete(self):
        r = reconcile_writes([intent("a"), intent("b")], {"a": "new", "b": "new"})
        self.assertEqual(r.status, "COMPLETE")
        self.assertEqual(r.applied, ("a", "b"))
        self.assertFalse(r.automatic_retry_allowed)

    def test_nothing_applied(self):
        r = reconcile_writes([intent("a"), intent("b")], {"a": "old", "b": "old"})
        self.assertEqual(r.status, "NO_APPLIED_WRITES")
        self.assertFalse(r.automatic_retry_allowed)

    def test_partial_write_not_automatically_retried(self):
        r = reconcile_writes([intent("a"), intent("b")], {"a": "new", "b": "old"})
        self.assertEqual(r.status, "PARTIAL")
        self.assertEqual(r.applied, ("a",))
        self.assertEqual(r.untouched, ("b",))
        self.assertFalse(r.automatic_retry_allowed)

    def test_third_party_divergence(self):
        r = reconcile_writes([intent("a"), intent("b")], {"a": "new", "b": "other"})
        self.assertEqual(r.status, "CONFLICT")
        self.assertEqual(r.drifted, ("b",))

    def test_missing_observation_unknown_not_absence(self):
        r = reconcile_writes([intent("a"), intent("b")], {"a": "new"})
        self.assertEqual(r.status, "UNKNOWN")
        self.assertEqual(r.unknown, ("b",))

    def test_create_intent_observed_missing_is_untouched(self):
        r = reconcile_writes([intent("a", None, "created")], {"a": None})
        self.assertEqual(r.status, "NO_APPLIED_WRITES")

    def test_create_intent_existing_conflicting_content(self):
        r = reconcile_writes([intent("a", None, "created")], {"a": "other"})
        self.assertEqual(r.status, "CONFLICT")

    def test_create_intent_confirmed_created(self):
        r = reconcile_writes([intent("a", None, "created")], {"a": "created"})
        self.assertEqual(r.status, "COMPLETE")

    def test_unknown_takes_precedence_over_drift(self):
        r = reconcile_writes([intent("a"), intent("b")], {"a": "other"})
        self.assertEqual(r.status, "UNKNOWN")
        self.assertEqual(r.drifted, ("a",))

    def test_duplicate_paths_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_writes([intent("a"), intent("a")], {"a": "new"})

    def test_parent_path_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_writes([intent("../secret")], {})

    def test_dot_path_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_writes([intent("docs/./a")], {})

    def test_noop_intent_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_writes([intent("a", "same", "same")], {})

    def test_empty_intents_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_writes([], {})

    def test_extra_observation_is_ignored(self):
        r = reconcile_writes([intent("a")], {"a": "new", "unrelated": "other"})
        self.assertEqual(r.status, "COMPLETE")
        self.assertEqual(r.applied, ("a",))


if __name__ == "__main__":
    unittest.main()
