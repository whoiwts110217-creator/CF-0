"""Authenticated GET budget must not enable optional receipt publication.

Synthetic tokens, mocked transport and a temporary SQLite ledger only.
No GitHub requests or credentials are used by these tests.
"""
import base64
import io
import json
import os
import pathlib
import sys
import tempfile
import traceback
import unittest
import urllib.error
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay

READ_TOKEN = 'synthetic-CF0-read-secret-never-for-logs'
WRITE_TOKEN = 'synthetic-CF0-write-secret-never-for-logs'
READ_PATH = f'/repos/{relay.REPO}/contents/command_queue/inbox?ref=main'
JOB_ID = '00000000-0000-4000-8000-000000000001'
WRITE_PATH = f'/repos/{relay.REPO}/contents/command_queue/receipts/{JOB_ID}.json'


class Response:
    def __init__(self, value):
        self.data = json.dumps(value).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, count):
        return self.data[:count]


class ReadOnlyGitHubAuthTests(unittest.TestCase):
    def test_read_token_is_get_only_and_not_a_url_or_body_parameter(self):
        repo = relay.HttpRepo(read_token=READ_TOKEN)
        with patch.object(relay.urllib.request, 'urlopen', return_value=Response([])) as send:
            self.assertEqual(repo.request('GET', READ_PATH), [])
            repo.request('PUT', WRITE_PATH, {'synthetic': True})
        get, put = (call.args[0] for call in send.call_args_list)
        self.assertEqual(get.get_header('Authorization'), 'Bearer ' + READ_TOKEN)
        self.assertNotIn(READ_TOKEN, get.full_url)
        self.assertIsNone(get.data)
        self.assertIsNone(put.get_header('Authorization'))
        self.assertNotIn(READ_TOKEN, put.full_url)
        self.assertNotIn(READ_TOKEN.encode(), put.data)

    def test_read_only_publish_never_calls_transport_even_for_valid_receipt(self):
        result = {'pong': True, 'protocol': 1}
        receipt = {'v': 2, 'id': JOB_ID, 'request_sha256': '0' * 64,
                   'status': 'completed', 'result': result,
                   'response_sha256': relay.sha(result)}
        with patch.object(relay.urllib.request, 'urlopen') as send:
            self.assertFalse(relay.HttpRepo(read_token=READ_TOKEN).publish(JOB_ID, receipt))
        send.assert_not_called()

    def test_writer_still_authenticates_get_and_put_without_read_token(self):
        repo = relay.HttpRepo(token=WRITE_TOKEN)
        with patch.object(relay.urllib.request, 'urlopen', return_value=Response({})) as send:
            repo.request('GET', READ_PATH)
            repo.request('PUT', WRITE_PATH, {})
        for call in send.call_args_list:
            self.assertEqual(call.args[0].get_header('Authorization'), 'Bearer ' + WRITE_TOKEN)

    def test_distinct_read_and_write_tokens_stay_on_their_methods(self):
        repo = relay.HttpRepo(token=WRITE_TOKEN, read_token=READ_TOKEN)
        with patch.object(relay.urllib.request, 'urlopen', return_value=Response({})) as send:
            repo.request('GET', READ_PATH)
            repo.request('PUT', WRITE_PATH, {})
        self.assertEqual(send.call_args_list[0].args[0].get_header('Authorization'), 'Bearer ' + READ_TOKEN)
        self.assertEqual(send.call_args_list[1].args[0].get_header('Authorization'), 'Bearer ' + WRITE_TOKEN)

    def test_no_credentials_preserves_anonymous_reads(self):
        with patch.object(relay.urllib.request, 'urlopen', return_value=Response([])) as send:
            self.assertEqual(relay.HttpRepo().files(), [])
        self.assertIsNone(send.call_args.args[0].get_header('Authorization'))

    def test_cli_read_token_authenticates_jobs_but_receipts_stay_local(self):
        job = relay.make_job('ping')
        filename = job['id'] + '.json'
        calls = []

        def transport(request, timeout):
            calls.append((request.method, request.full_url))
            self.assertEqual(request.method, 'GET')
            self.assertEqual(request.get_header('Authorization'), 'Bearer ' + READ_TOKEN)
            self.assertEqual(timeout, relay.NETWORK_TIMEOUT_SECONDS)
            if request.full_url == relay.API + READ_PATH:
                return Response([{'name': filename, 'type': 'file'}])
            self.assertEqual(request.full_url, relay.API + f'/repos/{relay.REPO}/contents/command_queue/inbox/{filename}?ref=main')
            return Response({'encoding': 'base64', 'content': base64.b64encode(relay.dump(job)).decode()})

        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(os.environ, {'CF_RELAY_GITHUB_TOKEN': '', 'CF_RELAY_GITHUB_READ_TOKEN': READ_TOKEN}):
                with patch.object(relay.urllib.request, 'urlopen', side_effect=transport):
                    output = io.StringIO()
                    with redirect_stdout(output):
                        self.assertEqual(relay.main(['once', '--state-dir', folder]), 0)
                        self.assertEqual(relay.main(['once', '--state-dir', folder]), 0)
            first, replay = map(json.loads, output.getvalue().splitlines())
            self.assertEqual((first['executed'], replay['replayed']), (1, 1))
            self.assertEqual((first['public_receipts'], replay['public_receipts']), (0, 0))
            self.assertEqual(first['errors'] + replay['errors'], [])
            self.assertEqual(relay.State(pathlib.Path(folder) / 'relay.sqlite3').count(), 1)
        self.assertEqual(len(calls), 3, 'two inbox reads and one job read; no receipt lookup or PUT')
        self.assertNotIn(READ_TOKEN, output.getvalue())

    def test_read_token_never_appears_in_repr_or_transport_failure_logs(self):
        repo = relay.HttpRepo(token=WRITE_TOKEN, read_token=READ_TOKEN)
        self.assertNotIn(READ_TOKEN, repr(repo))
        self.assertNotIn(WRITE_TOKEN, repr(repo))
        failures = (
            (urllib.error.URLError(READ_TOKEN), 'github_unreachable'),
            (urllib.error.HTTPError(relay.API + '/' + READ_TOKEN, 403, READ_TOKEN,
                                    {'X-RateLimit-Remaining': '0'}, None),
             'github_http_403_rate_budget_zero'),
        )
        for failure, expected in failures:
            with self.subTest(reason=expected):
                with patch.object(relay.urllib.request, 'urlopen', side_effect=failure) as send:
                    with self.assertRaises(relay.RelayError) as caught:
                        repo.request('GET', READ_PATH)
                self.assertEqual(str(caught.exception), expected)
                self.assertEqual(send.call_count, 1)
                trace = ''.join(traceback.format_exception(caught.exception))
                self.assertNotIn(READ_TOKEN, trace)
                self.assertNotIn(WRITE_TOKEN, trace)

    def test_workflow_scopes_read_token_to_external_smoke_and_keeps_write_removed(self):
        text = (pathlib.Path(__file__).resolve().parents[2] / '.github/workflows/cf0-relay-tests.yml').read_text()
        before, smoke = text.split('      - name: External Windows read-only relay smoke test without GitHub CLI\n', 1)
        smoke, _, after = smoke.partition('\n      - name:')
        self.assertNotIn('CF_RELAY_GITHUB_READ_TOKEN', before + after)
        self.assertIn('CF_RELAY_GITHUB_READ_TOKEN: ${{ github.token }}', smoke)
        self.assertIn('Remove-Item Env:CF_RELAY_GITHUB_TOKEN -ErrorAction SilentlyContinue', smoke)
        self.assertIn('contents: read', before)
        self.assertNotIn('contents: write', text)


if __name__ == '__main__':
    unittest.main()
