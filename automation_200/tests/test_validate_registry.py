"""Offline registry schema and priority dependency guard regression tests."""
import copy,json,pathlib,sys,unittest
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
if __name__=='__main__':unittest.main()
