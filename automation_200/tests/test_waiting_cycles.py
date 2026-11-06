"""Pure offline tests for waiting-cycle persistence semantics."""
import unittest
from automation_200.waiting_cycles import advance

def t(i, status="planned", dep=(), hp=False):
    return {"id":i,"status":status,"depends_on":list(dep),"physical_hp_required":hp}

class WaitingCycleTests(unittest.TestCase):
    def test_selected_resets_while_eligible_unselected_ages(self):
        r={"tasks":[t("A"),t("B"),t("C",hp=True)]}
        self.assertEqual(advance(r,{"A":8,"B":3},["B"]),{"A":9,"B":0})
    def test_blocked_and_unverified_not_aged(self):
        r={"tasks":[t("A"),t("B",dep=["C"]),t("C",status="verified")]}
        self.assertEqual(advance(r,{},["A"],blocked_ids=["B"]),{"A":0})
    def test_bounded_counter(self):
        self.assertEqual(advance({"tasks":[t("A")]},{"A":100000},[]),{"A":100000})
    def test_rejects_untrusted_state_and_ineligible_selection(self):
        r={"tasks":[t("A"),t("B",hp=True)]}
        for bad in ({"A":True},{"A":-1},{"Z":1},[],{"A":"3"}):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                advance(r,bad,[])
        with self.assertRaises(ValueError):
            advance(r,{},["B"])
        with self.assertRaises(ValueError):
            advance(r,{},["A","A"])
    def test_does_not_mutate_registry_or_previous(self):
        r={"tasks":[t("A"),t("B")]}
        before={"A":4}
        advance(r,before,["B"])
        self.assertEqual(before,{"A":4})
        self.assertEqual(r["tasks"][0]["status"],"planned")

if __name__=="__main__":
    unittest.main()
