# CF-090: deterministic command lifetime boundary tests, no HP execution.
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay


class CommandTTLTests(unittest.TestCase):
    def check(self, job, now, valid):
        name = job["id"] + ".json"
        if valid:
            self.assertEqual(relay.validate(job, name, now=now), job)
        else:
            with self.assertRaisesRegex(relay.RelayError, "expired_or_future"):
                relay.validate(job, name, now=now)

    def test_exact_expiry_and_first_second_after(self):
        job = relay.make_job("ping", now=1000)
        self.check(job, job["expires"] - 1, True)
        self.check(job, job["expires"], True)
        self.check(job, job["expires"] + 1, False)

    def test_future_clock_skew_boundary(self):
        job = relay.make_job("ping", now=1000)
        self.check(job, 820, True)
        self.check(job, 819, False)

    def test_maximum_lifetime_boundary(self):
        job = relay.make_job("ping", now=1000)
        job["expires"] = 1000 + 86400
        self.check(job, 1000, True)
        job["expires"] += 1
        self.check(job, 1000, False)

    def test_zero_and_negative_lifetime(self):
        job = relay.make_job("ping", now=1000)
        for expires in (1000, 999):
            with self.subTest(expires=expires):
                job["expires"] = expires
                self.check(job, 1000, False)

    def test_timestamp_types_are_not_coerced(self):
        for field, value in (("issued", True), ("expires", False),
                             ("issued", "1000"), ("expires", 8200.0),
                             ("issued", None)):
            with self.subTest(field=field, value=value):
                job = relay.make_job("ping", now=1000)
                job[field] = value
                self.check(job, 1000, False)

    def test_all_allowed_actions_share_ttl_rules(self):
        for action in ("ping", "hp_status", "sidecar_verify"):
            with self.subTest(action=action):
                job = relay.make_job(action, now=1000)
                self.check(job, 1000, True)
                self.check(job, job["expires"] + 1, False)


if __name__ == "__main__":
    unittest.main()
