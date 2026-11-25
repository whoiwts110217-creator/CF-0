"""open_notepad launches notepad.exe only, and never from job arguments.

The process start is mocked. These tests do not prove a visible Notepad
window on the owner's HP.
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay


class Inbox:
    def __init__(self, job):
        self.job = job

    def files(self):
        return [self.job["id"] + ".json"]

    def load(self, name):
        assert name == self.job["id"] + ".json"
        return self.job

    def publish(self, jid, receipt):
        return False


class OpenNotepadTests(unittest.TestCase):
    def test_non_windows_returns_unsupported_without_starting_a_process(self):
        with patch.object(relay, "_windows_host", return_value=False), patch("subprocess.Popen") as popen:
            result = relay.execute(relay.make_job("open_notepad"))
        self.assertEqual(result, {"launched": False, "detail": "unsupported_platform"})
        relay.validate_public_result(result, "open_notepad")
        popen.assert_not_called()

    def test_windows_launches_notepad_exe_with_no_job_arguments(self):
        with patch.object(relay, "_windows_host", return_value=True), patch("subprocess.Popen") as popen:
            result = relay.execute(relay.make_job("open_notepad"))
        self.assertEqual(result, {
            "launched": True,
            "detail": "process_started_not_visual_confirmation",
        })
        relay.validate_public_result(result, "open_notepad")
        popen.assert_called_once_with(
            ["notepad.exe"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )

    def test_windows_launch_failure_stays_a_fixed_public_receipt(self):
        secret = r"C:\Users\Someone\AppData\notepad.exe"
        with patch.object(relay, "_windows_host", return_value=True), patch("subprocess.Popen", side_effect=OSError(secret)):
            result = relay.execute(relay.make_job("open_notepad"))
        self.assertEqual(result, {"launched": False, "detail": "windows_launch_failed"})
        self.assertNotIn("Someone", str(result))
        self.assertNotIn(secret, str(result))
        relay.validate_public_result(result, "open_notepad")

    def test_job_arguments_cannot_select_a_program_or_file(self):
        job = relay.make_job("open_notepad")
        job["args"] = {"command": "cmd.exe", "file": "secret.txt"}
        with self.assertRaisesRegex(relay.RelayError, "invalid_arguments"):
            relay.validate(job, job["id"] + ".json")

    def test_replay_does_not_launch_notepad_twice(self):
        job = relay.make_job("open_notepad")
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(relay, "_windows_host", return_value=True), \
                patch("subprocess.Popen") as popen:
            state = relay.State(pathlib.Path(folder) / "relay.sqlite3")
            first = relay.tick(Inbox(job), state)
            second = relay.tick(Inbox(job), state)
        self.assertEqual(first["executed"], 1)
        self.assertEqual(first["errors"], [])
        self.assertEqual(second["executed"], 0)
        self.assertEqual(second["replayed"], 1)
        popen.assert_called_once_with(
            ["notepad.exe"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )

    def test_public_result_rejects_paths_pids_and_freeform_notes(self):
        samples = (
            {"launched": True, "detail": "process_started_not_visual_confirmation", "pid": 42},
            {"launched": True, "detail": r"C:\Windows\notepad.exe"},
            {"launched": False, "detail": "unsupported_platform", "stderr": "secret"},
            {"launched": "yes", "detail": "unsupported_platform"},
            {"launched": False, "detail": "local_opt_in_required"},
        )
        for result in samples:
            with self.subTest(result=result):
                with self.assertRaisesRegex(relay.RelayError, "^unsafe_public_result$"):
                    relay.validate_public_result(result, "open_notepad")


if __name__ == "__main__":
    unittest.main()
