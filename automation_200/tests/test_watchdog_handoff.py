"""Exercise the Work handoff with synthetic GitHub responses and no HP access."""
import base64
import io
import hashlib
import json
import unittest
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from automation_200 import watchdog_handoff as handoff
from relay import channel_audit, health_watch
from relay.cf_public_relay import make_job, sha

COMMIT = "a" * 40
NOW = 1_790_000_000
REGISTRY = json.loads((handoff.ROOT / "registry.json").read_text(encoding="utf-8"))


class WatchdogHandoffTests(unittest.TestCase):
    def test_live_cli_outputs_flow_into_one_pinned_record(self):
        job = make_job("ping", now=NOW)
        name = job["id"] + ".json"
        result = {"pong": True, "protocol": 1}
        receipt = {
            "v": 2, "id": job["id"], "status": "completed", "result": result,
            "request_sha256": sha(job), "response_sha256": sha(result),
        }
        listing = [{"type": "file", "name": name}]
        suffix = "?ref=" + COMMIT
        inbox_url = channel_audit.folder_url("inbox")
        receipts_url = channel_audit.folder_url("receipts")

        def encoded(data):
            return {"encoding": "base64", "content": base64.b64encode(json.dumps(data).encode()).decode()}

        responses = {
            inbox_url + suffix: listing, receipts_url + suffix: listing,
            inbox_url + "/" + name + suffix: encoded(job),
            receipts_url + "/" + name + suffix: encoded(receipt),
        }
        health_url = health_watch.URL.removesuffix("main") + COMMIT
        missing = urllib.error.HTTPError(health_url, 404, "Not Found", None, None)
        queue = io.StringIO()
        with patch.object(channel_audit, "github_json", side_effect=responses.__getitem__) as fetch:
            with redirect_stdout(queue):
                self.assertEqual(channel_audit.main(["--live", "--commit", COMMIT]), 0)
            self.assertEqual([call.args[0] for call in fetch.call_args_list], list(responses))
        health = io.StringIO()
        with patch.object(health_watch, "github_json", side_effect=missing) as fetch:
            with redirect_stdout(health):
                self.assertEqual(health_watch.main(["--live", "--commit", COMMIT]), 0)
            fetch.assert_called_once_with(health_url)

        with TemporaryDirectory() as directory:
            queue_path = Path(directory) / "queue.json"
            health_path = Path(directory) / "health.json"
            queue_path.write_text(queue.getvalue(), encoding="utf-8")
            health_path.write_text(health.getvalue(), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(handoff.main([
                    "--queue", str(queue_path), "--health", str(health_path),
                    "--commit", COMMIT, "--event", "schedule",
                ]), 0)
        proposal_text, line, digest_line = output.getvalue().strip().rsplit("\n", 2)
        self.assertEqual(digest_line, "CF0_WORK_HANDOFF_SHA256=" + handoff.handoff_digest(json.loads(line.split("=", 1)[1])))
        self.assertTrue(line.startswith("CF0_WORK_HANDOFF="))
        record = json.loads(line.split("=", 1)[1])
        proposal = json.loads(proposal_text)
        self.assertEqual(record["source_commit"], COMMIT)
        self.assertEqual(record["watchdog_event"], "schedule")
        self.assertEqual(record["registry"]["verified"], REGISTRY["completed"])
        self.assertEqual(record["public_queue"]["matching_execution_receipts"], 1)
        self.assertEqual(record["hp"]["health_state"], "not_published")
        self.assertEqual(proposal["hp_health_state"], record["hp"]["health_state"])
        self.assertEqual(record["hp"]["scheduled_receipt_origin"], "unverified")
        self.assertFalse(record["execution_authorized"])
        self.assertNotIn(job["id"], line)
        self.assertTrue(record["next_source_proposals"])
        self.assertNotIn("CF-077", record["next_source_proposals"])
        self.assertNotIn("CF-184", record["next_source_proposals"])

    def test_unavailable_queue_does_not_hide_health_or_echo_diagnostics(self):
        private = "example-secret-diagnostic"
        queue = {"audit": "unavailable", "source_commit": COMMIT, "error": private}
        health = {**health_watch.status("fresh_public_report"), "source_commit": COMMIT,
                  "detail": private}
        record, proposal = handoff.build_handoff(
            REGISTRY, queue, health, commit=COMMIT, event="push", now=NOW,
        )
        self.assertEqual(record["public_queue"], {"state": "unavailable"})
        self.assertEqual(proposal["hp_health_state"], "fresh_public_report")
        self.assertFalse(record["hp"]["identity_attested"])
        self.assertEqual(record["hp"]["scheduled_receipt_origin"], "unverified")
        self.assertNotIn(private, json.dumps(record))

    def test_bad_counts_and_different_source_commits_are_unavailable(self):
        queue = {"audit": "read_only", "repo": channel_audit.REPO,
                 "source_commit": COMMIT, **dict.fromkeys(handoff.QUEUE_COUNTS, 0)}
        health = {**health_watch.status("fresh_public_report"), "source_commit": "b" * 40}
        for changed in ({"matching_execution_receipts": True}, {"source_commit": "b" * 40}):
            with self.subTest(changed=changed):
                record, _ = handoff.build_handoff(
                    REGISTRY, {**queue, **changed}, health,
                    commit=COMMIT, event="push", now=NOW,
                )
                self.assertEqual(record["public_queue"], {"state": "unavailable"})
                self.assertEqual(record["hp"]["health_state"], "unavailable")

    def test_digest_is_canonical_and_not_an_authority_token(self):
        packet, _ = handoff.build_handoff(
            REGISTRY, {}, {}, commit=COMMIT, event="schedule", now=NOW,
        )
        reordered = dict(reversed(list(packet.items())))
        self.assertEqual(handoff.handoff_digest(packet), handoff.handoff_digest(reordered))
        self.assertEqual(len(handoff.handoff_digest(packet)), 64)
        self.assertNotIn("execution_authorized", handoff.handoff_digest(packet))
        changed = {**packet, "source_commit": "b" * 40}
        self.assertNotEqual(handoff.handoff_digest(packet), handoff.handoff_digest(changed))
        self.assertFalse(packet["execution_authorized"])

    def test_missing_and_malformed_report_files(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            self.assertEqual(handoff.read_report(path), {})
            for content in ("[]", "{", " " * handoff.MAX_INPUT_BYTES + "{}"):
                with self.subTest(size=len(content)):
                    path.write_text(content, encoding="utf-8")
                    self.assertEqual(handoff.read_report(path), {})


if __name__ == "__main__":
    unittest.main()
