"""Offline registry schema and priority dependency guard regression tests."""
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
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
if __name__=='__main__':unittest.main()
