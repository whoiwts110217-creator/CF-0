"""Offline registry schema and priority dependency guard regression tests."""
import copy,json,pathlib,sys,unittest
import hashlib
import subprocess
from contextlib import redirect_stdout
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import checkpoints
from validate_registry import check_registry,RegistryValidationError
DATA=json.loads((ROOT/'registry.json').read_text(encoding='utf-8'))

class RegistryTests(unittest.TestCase):
    def test_current_registry(self):
        self.assertEqual(check_registry(DATA)['target'],200)
    def test_dependency_graph(self):
        x=copy.deepcopy(DATA);x['tasks'][0]['depends_on']=['CF-999']
        with self.assertRaisesRegex(RegistryValidationError,'invalid_dependencies'):check_registry(x)
        x=copy.deepcopy(DATA);x['tasks'][0]['depends_on']=['CF-002']
        x['tasks'][1]['depends_on']=['CF-001']
        with self.assertRaisesRegex(RegistryValidationError,'dependency_cycle'):check_registry(x)
    def test_authority_and_hp_gate(self):
        x=copy.deepcopy(DATA);x['tasks'][0]['authority']=''
        with self.assertRaisesRegex(RegistryValidationError,'missing_authority'):check_registry(x)
        x=copy.deepcopy(DATA);x['tasks'][0]['physical_hp_required']='false'
        with self.assertRaisesRegex(RegistryValidationError,'missing_hp_gate'):check_registry(x)
    def test_status_and_count(self):
        x=copy.deepcopy(DATA);x['tasks'][0]['status']='finished'
        with self.assertRaisesRegex(RegistryValidationError,'invalid_status'):check_registry(x)
        x=copy.deepcopy(DATA);x['completed']+=1
        with self.assertRaisesRegex(RegistryValidationError,'completed_mismatch'):check_registry(x)
    def test_evidence_required(self):
        x=copy.deepcopy(DATA);x['tasks'][0]['evidence']=''
        with self.assertRaisesRegex(RegistryValidationError,'missing_evidence'):check_registry(x)

    def test_complete_rejects_unverified_dependency_without_writing(self):
        initial = copy.deepcopy(DATA)
        initial['completed'] = 0
        for task in initial['tasks']:
            task.update(status='planned', evidence=None)
        evidence = 'specific acceptance test'
        with TemporaryDirectory() as folder:
            registry = pathlib.Path(folder) / 'registry.json'
            events = pathlib.Path(folder) / 'events.jsonl'
            original = json.dumps(initial).encode()
            registry.write_bytes(original)
            events.write_bytes(b'{"prior":true}\n')
            with patch.multiple(checkpoints, SRC=registry, EVENTS=events):
                with self.assertRaisesRegex(RegistryValidationError, 'unverified_dependency:CF-002'):
                    checkpoints.complete(['CF-002'], evidence)
                with self.assertRaisesRegex(ValueError, 'distinct items'):
                    checkpoints.complete(['CF-001', 'CF-001'], evidence)
                self.assertEqual(registry.read_bytes(), original)
                self.assertEqual(events.read_bytes(), b'{"prior":true}\n')

                updated = checkpoints.complete(['CF-001', 'CF-002'], evidence)
                self.assertEqual(check_registry(updated)['verified'], 2)
                records = [json.loads(line) for line in events.read_text().splitlines()]
                self.assertEqual(records[0], {'prior': True})
                self.assertEqual([event['task'] for event in records[1:]], ['CF-001', 'CF-002'])

    def test_git_checkpoint_is_scoped_and_preserves_earlier_batches(self):
        initial = copy.deepcopy(DATA)
        initial["completed"] = 0
        for task in initial["tasks"]:
            task.update(status="planned", evidence=None)
        evidence = "specific synthetic acceptance test"
        with TemporaryDirectory() as folder:
            repo = pathlib.Path(folder)
            root = repo / "automation_200"
            root.mkdir()
            registry = root / "registry.json"
            events = root / "events.jsonl"
            snapshots = root / "checkpoints"
            first_snapshot = snapshots / "checkpoint_004.json"
            registry.write_bytes(json.dumps(initial).encode())
            events.write_bytes(b"")

            def git(*args):
                return subprocess.run(
                    ["git", *args], cwd=repo, check=True, text=True, capture_output=True, timeout=40
                ).stdout.strip()

            git("init", "--quiet")
            git("config", "user.name", "CF-0 checkpoint test")
            git("config", "user.email", "checkpoint-test@localhost")
            git("config", "commit.gpgSign", "false")
            git("config", "core.autocrlf", "false")
            git("add", "automation_200/registry.json", "automation_200/events.jsonl")
            git("commit", "--quiet", "-m", "Synthetic registry baseline")
            (repo / "unrelated.txt").write_text("staged outside the checkpoint\n", encoding="utf-8")
            git("add", "unrelated.txt")

            with (
                patch.multiple(checkpoints, ROOT=root, SRC=registry, EVENTS=events, CHECKPOINTS=snapshots),
                redirect_stdout(StringIO()),
            ):
                checkpoints.complete(["CF-001", "CF-002", "CF-003"], evidence)
                with self.assertRaisesRegex(ValueError, "requires 4 verified tasks"):
                    checkpoints.git_checkpoint()
                self.assertFalse(snapshots.exists())

                checkpoints.complete(["CF-004"], evidence)
                checkpoints.git_checkpoint()
                first_head = git("rev-parse", "HEAD")
                first_bytes = first_snapshot.read_bytes()
                first = json.loads(first_bytes)
                self.assertEqual(first["evidence_ids"], ["CF-001", "CF-002", "CF-003", "CF-004"])
                self.assertEqual(first["registry_sha256"], hashlib.sha256(registry.read_bytes()).hexdigest())
                committed = git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").splitlines()
                self.assertEqual(set(committed), {
                    "automation_200/checkpoints/checkpoint_004.json",
                    "automation_200/events.jsonl",
                    "automation_200/registry.json",
                })
                self.assertEqual(git("diff", "--cached", "--name-only"), "unrelated.txt")
                checkpoints.git_checkpoint()
                self.assertEqual(git("rev-parse", "HEAD"), first_head)

                checkpoints.complete(["CF-005", "CF-006", "CF-007", "CF-008"], evidence)
                checkpoints.git_checkpoint()
                second = json.loads((snapshots / "checkpoint_008.json").read_bytes())
                self.assertEqual(second["evidence_ids"], [f"CF-{n:03d}" for n in range(1, 9)])
                self.assertEqual(second["registry_sha256"], hashlib.sha256(registry.read_bytes()).hexdigest())
                self.assertEqual(first_snapshot.read_bytes(), first_bytes)
                self.assertEqual(git("diff", "--cached", "--name-only"), "unrelated.txt")
if __name__=='__main__':unittest.main()
