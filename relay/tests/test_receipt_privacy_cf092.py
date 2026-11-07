"""CF-092: public receipts cannot contain local paths or arbitrary handler output.

Synthetic-only tests. No GitHub write, no physical HP, no real private paths.
"""
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay


class InMemoryRepo:
    def __init__(self, job):
        self.job = job
        self.writes = []

    def files(self):
        return [self.job['id'] + '.json']

    def load(self, name):
        assert name == self.job['id'] + '.json'
        return self.job

    def publish(self, jid, receipt):
        self.writes.append((jid, receipt))
        return True


class SafeReceiptTests(unittest.TestCase):
    def test_all_existing_action_outputs_remain_supported(self):
        for action in sorted(relay.ALLOWED):
            with self.subTest(action=action):
                result = relay.execute(relay.make_job(action))
                self.assertIsNone(relay.validate_public_result(result, action))

    def test_rejects_private_path_and_identity_fields_even_if_result_has_valid_keys(self):
        private = r'C:\Users\Someone\Documents\secret-project\file.txt'
        samples = [
            ('ping', {'pong': True, 'protocol': 1, 'path': private}),
            ('hp_status', {'worker': private, 'policy': 'public-safe', 'commands': sorted(relay.ALLOWED)}),
            ('hp_status', {'worker': 'online', 'policy': 'public-safe', 'commands': sorted(relay.ALLOWED), 'user': 'Someone'}),
            ('sidecar_verify', {'verified': False, 'reason': private}),
            ('sidecar_verify', {'verified': True, 'events': 1, 'cwd': private}),
            ('sidecar_verify', {'verified': True, 'events': {'path': private}}),
            ('sidecar_verify', {'verified': False, 'reason': 'verify_failed', 'stderr': private}),
            ('ping', {'pong': 1, 'protocol': True}),
        ]
        for action, value in samples:
            with self.subTest(action=action, result=value):
                with self.assertRaisesRegex(relay.RelayError, '^unsafe_public_result$') as caught:
                    relay.validate_public_result(value, action)
                self.assertNotIn(private, str(caught.exception))

    def test_bad_action_result_never_becomes_local_or_public_receipt(self):
        private = '/home/private-user/Projects/secret-material'
        job = relay.make_job('ping')
        repo = InMemoryRepo(job)
        with tempfile.TemporaryDirectory() as folder:
            db = pathlib.Path(folder) / 'relay.sqlite3'
            with patch.object(relay, 'execute', return_value={'pong': True, 'protocol': 1, 'cwd': private}):
                first = relay.tick(repo, relay.State(db))
                self.assertEqual(first['executed'], 0)
                self.assertEqual(first['public_receipts'], 0)
                self.assertEqual(first['errors'][0]['error'], 'unsafe_public_result')
                self.assertNotIn(private, str(first))
                self.assertEqual(relay.State(db).count(), 0)
                self.assertEqual(relay.State(db).unknown_count(), 1)
                self.assertEqual(repo.writes, [])
                second = relay.tick(repo, relay.State(db))
            self.assertEqual(second['executed'], 0)
            self.assertEqual(second['uncertain'], 1)
            self.assertEqual(repo.writes, [])

    def test_v2_replay_publication_rejects_unsafe_payload_before_network(self):
        private = r'C:\Users\Someone\AppData\Private'
        job = relay.make_job('ping')
        result = {'pong': True, 'protocol': 1, 'private_path': private}
        receipt = {
            'v': 2, 'id': job['id'], 'request_sha256': relay.sha(job),
            'status': 'completed', 'result': result, 'response_sha256': relay.sha(result),
        }
        mailbox = relay.HttpRepo(token='synthetic-token')
        with patch.object(mailbox, 'request') as request:
            with self.assertRaisesRegex(relay.RelayError, '^unsafe_public_result$'):
                mailbox.publish(job['id'], receipt)
            request.assert_not_called()

    def test_legacy_valid_receipts_remain_compatible(self):
        job = relay.make_job('ping')
        receipt = {
            'v': 1, 'id': job['id'], 'request_sha256': relay.sha(job),
            'status': 'completed', 'result': {'pong': True, 'protocol': 1},
        }
        self.assertIsInstance(relay.validate_receipt(receipt, job['id']), str)
        mailbox = relay.HttpRepo(token='synthetic-token')
        with patch.object(mailbox, 'request', return_value=None) as request:
            self.assertTrue(mailbox.publish(job['id'], receipt))
            self.assertEqual([call.args[0] for call in request.call_args_list], ['GET', 'PUT'])


if __name__ == '__main__':
    unittest.main()
