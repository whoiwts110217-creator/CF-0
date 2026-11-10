import unittest
from automation_200.watchdog_consumer_ack import verify_consumer_ack


class ConsumerAckTests(unittest.TestCase):
    def setUp(self):
        self.producer = {"schema": "cf0.work_handoff_readback.v1",
                         "watchdog_run_id": 42689054389, "watchdog_run_attempt": 1,
                         "packet_sha256": "a" * 64, "execution_authorized": False}
        self.ack = {"schema": "cf0.executor_packet_decision.v1",
                    "watchdog_run_id": 42689054389, "watchdog_run_attempt": 1,
                    "packet_sha256": "a" * 64, "executor_run_id": "synthetic-test-1",
                    "decision": "deferred", "execution_authorized": False}

    def test_matching_synthetic_decision_is_only_source_correlation(self):
        result = verify_consumer_ack(self.producer, self.ack)
        self.assertTrue(result["correlated"])
        self.assertFalse(result["acknowledgement_origin_verified"])
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["hp_identity_attested"])
        self.assertEqual(result["decision"], "deferred")

    def test_producer_readback_integrity_fail_closed(self):
        for patch in ({"schema": "unknown"}, {"watchdog_run_id": True},
                      {"watchdog_run_attempt": 0}, {"packet_sha256": "A" * 64},
                      {"packet_sha256": "x" * 64},
                      {"packet_sha256": None},
                      {"execution_authorized": None}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                verify_consumer_ack({**self.producer, **patch}, self.ack)
        for invalid in (None, [], "not-a-readback"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                verify_consumer_ack(invalid, self.ack)

    def test_mismatch_and_authority_drift_fail_closed(self):
        for patch in ({"watchdog_run_id": 1}, {"watchdog_run_attempt": 2},
                      {"packet_sha256": "b" * 64}, {"executor_run_id": "../bad"},
                      {"decision": "execute_hp"}, {"execution_authorized": True},
                      {"schema": "unknown"}, {"watchdog_run_id": True}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                verify_consumer_ack(self.producer, {**self.ack, **patch})
        with self.assertRaises(ValueError):
            verify_consumer_ack({**self.producer, "execution_authorized": True}, self.ack)
        with self.assertRaises(ValueError):
            verify_consumer_ack(self.producer, {**self.ack, "unexpected": "data"})


    def test_untrusted_acknowledgement_shapes_fail_closed(self):
        for invalid in (None, [], "not-an-ack", 0, False):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                verify_consumer_ack(self.producer, invalid)
        for key in self.ack:
            with self.subTest(missing=key), self.assertRaises(ValueError):
                verify_consumer_ack(self.producer, {k: v for k, v in self.ack.items() if k != key})

    def test_all_permitted_decisions_remain_non_authorizing(self):
        for decision in ("accepted_source_only", "rejected", "deferred"):
            with self.subTest(decision=decision):
                result = verify_consumer_ack(self.producer, {**self.ack, "decision": decision})
                self.assertEqual(result["decision"], decision)
                self.assertFalse(result["acknowledgement_origin_verified"])
                self.assertFalse(result["execution_authorized"])
                self.assertFalse(result["hp_identity_attested"])


    def test_identity_type_confusion_and_replay_fail_closed(self):
        for key in ("watchdog_run_id", "watchdog_run_attempt"):
            for invalid in (True, False, 1.0, "1", 0, -1, None):
                with self.subTest(side="producer", key=key, invalid=invalid), self.assertRaises(ValueError):
                    verify_consumer_ack({**self.producer, key: invalid}, self.ack)
                with self.subTest(side="executor", key=key, invalid=invalid), self.assertRaises(ValueError):
                    verify_consumer_ack(self.producer, {**self.ack, key: invalid})
        for invalid in ("A" * 64, "g" * 64, "a" * 63, "a" * 65, None, 0):
            with self.subTest(digest=invalid), self.assertRaises(ValueError):
                verify_consumer_ack(self.producer, {**self.ack, "packet_sha256": invalid})
        for invalid in ("", " spaced ", "../traversal", "a" * 129, None, 7):
            with self.subTest(executor=invalid), self.assertRaises(ValueError):
                verify_consumer_ack(self.producer, {**self.ack, "executor_run_id": invalid})


if __name__ == "__main__":
    unittest.main()
