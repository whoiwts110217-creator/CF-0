"""Synthetic, no-network tests against the existing relay's v1/v2 contract."""
from __future__ import annotations

import json
import unittest
from actual_relay_pair import inspect_actual_relay_pair
from evidence_packet import BlobEvidence, git_blob_sha
import cf_public_relay as relay

JOB_ID = "00000000-0000-4000-8000-000000000001"
REQ_PATH = f"command_queue/inbox/{JOB_ID}.json"
REC_PATH = f"command_queue/receipts/{JOB_ID}.json"


def blob(path, data):
    raw = relay.dump(data) if not isinstance(data, bytes) else data
    return BlobEvidence(path, git_blob_sha(raw), raw)


def job(action="ping"):
    return {"v": 1, "id": JOB_ID, "action": action,
            "issued": 1762549200, "expires": 1762552800, "args": {}}


def receipt(request=None, version=2, result=None):
    request = request or job()
    if result is None:
        result = {"pong": True, "protocol": 1}
    r = {"v": version, "id": JOB_ID, "request_sha256": relay.sha(request),
         "status": "completed", "result": result}
    if version == 2:
        r["response_sha256"] = relay.sha(result)
    return r


def check(request=None, response=None):
    request = job() if request is None else request
    response = receipt(request) if response is None else response
    return inspect_actual_relay_pair(job_id=JOB_ID,
                                     request=blob(REQ_PATH, request),
                                     receipt=blob(REC_PATH, response))


class ActualRelayReceiptTests(unittest.TestCase):
    def test_current_v2_public_pair_matches_without_authority(self):
        result = check()
        self.assertEqual(result.status, "CONSISTENT_PUBLIC_PAIR_ONLY")
        self.assertTrue(result.public_pair_consistent)
        self.assertEqual(result.request_digest, relay.sha(job()))
        self.assertFalse(result.physical_hp_proven)
        self.assertFalse(result.unattended_schedule_proven)
        self.assertFalse(result.automatic_retry_allowed)
        self.assertFalse(result.task_verified)

    def test_legacy_v1_requires_manual_review(self):
        result = check(response=receipt(version=1))
        self.assertEqual(result.status, "LEGACY_REVIEW_REQUIRED")
        self.assertFalse(result.public_pair_consistent)

    def test_tampered_response_digest_holds(self):
        altered = receipt()
        altered["response_sha256"] = "0" * 64
        self.assertEqual(check(response=altered).status, "HOLD_EVIDENCE")

    def test_request_digest_mismatch_holds(self):
        altered = receipt()
        altered["request_sha256"] = "0" * 64
        self.assertIn("receipt_invalid_or_unmatched", check(response=altered).blockers)

    def test_pong_false_does_not_pass(self):
        altered = receipt(result={"pong": False, "protocol": 1})
        self.assertEqual(check(response=altered).status, "HOLD_EVIDENCE")

    def test_extra_metadata_not_accepted(self):
        altered = receipt(result={"pong": True, "protocol": 1, "hostname": "private"})
        self.assertEqual(check(response=altered).status, "HOLD_EVIDENCE")

    def test_canonical_digest_is_independent_of_json_order(self):
        j = job()
        r = receipt(j)
        reordered = json.dumps({k: j[k] for k in reversed(list(j))}).encode()
        result = inspect_actual_relay_pair(job_id=JOB_ID,
                 request=blob(REQ_PATH, reordered), receipt=blob(REC_PATH, r))
        self.assertEqual(result.status, "CONSISTENT_PUBLIC_PAIR_ONLY")

    def test_wrong_request_path_holds(self):
        result = inspect_actual_relay_pair(
            job_id=JOB_ID, request=blob("command_queue/inbox/other.json", job()),
            receipt=blob(REC_PATH, receipt()))
        self.assertIn("request_wrong_path", result.blockers)

    def test_wrong_receipt_path_holds(self):
        result = inspect_actual_relay_pair(
            job_id=JOB_ID, request=blob(REQ_PATH, job()),
            receipt=blob("command_queue/receipts/other.json", receipt()))
        self.assertIn("receipt_wrong_path", result.blockers)

    def test_tampered_request_blob_holds(self):
        req = blob(REQ_PATH, job())
        altered = BlobEvidence(req.path, req.blob_sha, req.content + b" ")
        result = inspect_actual_relay_pair(
            job_id=JOB_ID, request=altered, receipt=blob(REC_PATH, receipt()))
        self.assertIn("request_blob_mismatch", result.blockers)

    def test_tampered_receipt_blob_holds(self):
        rec = blob(REC_PATH, receipt())
        altered = BlobEvidence(rec.path, rec.blob_sha, rec.content + b" ")
        result = inspect_actual_relay_pair(
            job_id=JOB_ID, request=blob(REQ_PATH, job()), receipt=altered)
        self.assertIn("receipt_blob_mismatch", result.blockers)

    def test_missing_receipt_holds(self):
        result = inspect_actual_relay_pair(
            job_id=JOB_ID, request=blob(REQ_PATH, job()), receipt=None)
        self.assertIn("receipt_missing_readback", result.blockers)

    def test_missing_request_holds(self):
        result = inspect_actual_relay_pair(
            job_id=JOB_ID, request=None, receipt=blob(REC_PATH, receipt()))
        self.assertIn("request_missing_readback", result.blockers)

    def test_malformed_or_expired_shape_does_not_get_authenticated(self):
        invalid = job()
        invalid["expires"] = invalid["issued"] + 90000
        result = check(request=invalid)
        self.assertIn("request_invalid_schema", result.blockers)

    def test_illegal_action_holds(self):
        invalid = job(action="python_eval")
        result = check(request=invalid)
        self.assertEqual(result.status, "HOLD_EVIDENCE")

    def test_receipt_wrong_action_shape_holds(self):
        j = job(action="hp_status")
        res = receipt(j)
        result = check(request=j, response=res)
        self.assertEqual(result.status, "HOLD_EVIDENCE")

    def test_v2_hp_status_canned_result_matches(self):
        j = job(action="hp_status")
        res = receipt(j, result={"worker": "online", "policy": "public-safe",
                                 "commands": sorted(relay.ALLOWED)})
        self.assertEqual(check(request=j, response=res).status,
                         "CONSISTENT_PUBLIC_PAIR_ONLY")

    def test_v2_sidecar_unconfigured_matches(self):
        j = job(action="sidecar_verify")
        res = receipt(j, result={"verified": False, "reason": "not_configured"})
        self.assertEqual(check(request=j, response=res).status,
                         "CONSISTENT_PUBLIC_PAIR_ONLY")

    def test_unexpected_receipt_fields_rejected(self):
        r = receipt()
        r["account"] = "should not be public"
        self.assertEqual(check(response=r).status, "HOLD_EVIDENCE")

    def test_wrong_uuid_is_rejected_before_reading(self):
        with self.assertRaises(ValueError):
            inspect_actual_relay_pair(job_id="../evil", request=None, receipt=None)


    def test_duplicate_top_level_request_key_rejected(self):
        raw = relay.dump(job())
        raw = raw[:-1] + b',"v":1}'
        result = inspect_actual_relay_pair(
            job_id=JOB_ID, request=blob(REQ_PATH, raw),
            receipt=blob(REC_PATH, receipt()))
        self.assertIn("request_invalid_json", result.blockers)

    def test_duplicate_nested_result_key_rejected(self):
        raw = relay.dump(receipt())
        raw = raw.replace(b'"pong":true', b'"pong":true,"pong":true')
        result = inspect_actual_relay_pair(
            job_id=JOB_ID, request=blob(REQ_PATH, job()),
            receipt=blob(REC_PATH, raw))
        self.assertIn("receipt_invalid_json", result.blockers)

    def test_nonfinite_json_constant_rejected(self):
        raw = relay.dump(receipt()).replace(b'"protocol":1', b'"protocol":NaN')
        result = inspect_actual_relay_pair(
            job_id=JOB_ID, request=blob(REQ_PATH, job()),
            receipt=blob(REC_PATH, raw))
        self.assertIn("receipt_invalid_json", result.blockers)


    def test_duplicate_nested_request_args_key_rejected(self):
        raw = relay.dump(job()).replace(b'"args":{}', b'"args":{"x":1,"x":2}')
        result = inspect_actual_relay_pair(
            job_id=JOB_ID, request=blob(REQ_PATH, raw),
            receipt=blob(REC_PATH, receipt()))
        self.assertIn("request_invalid_json", result.blockers)

    def test_infinity_json_constant_rejected(self):
        for constant in (b"Infinity", b"-Infinity"):
            with self.subTest(constant=constant):
                raw = relay.dump(receipt()).replace(b'"protocol":1',
                                                    b'"protocol":' + constant)
                result = inspect_actual_relay_pair(
                    job_id=JOB_ID, request=blob(REQ_PATH, job()),
                    receipt=blob(REC_PATH, raw))
                self.assertIn("receipt_invalid_json", result.blockers)

    def test_invalid_utf8_receipt_rejected(self):
        raw = relay.dump(receipt()) + b"\\xff"
        result = inspect_actual_relay_pair(
            job_id=JOB_ID, request=blob(REQ_PATH, job()),
            receipt=blob(REC_PATH, raw))
        self.assertIn("receipt_invalid_json", result.blockers)


if __name__ == "__main__":
    unittest.main()
