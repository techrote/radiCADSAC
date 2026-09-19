from __future__ import annotations
import copy, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.ev=json.loads((ROOT/"research/rcs-027/evidence-matrix-v1.json").read_text())
        self.delta=json.loads((ROOT/"research/rcs-027/decision-delta-v1.json").read_text())

    def test_all_predecessors_consumed_once(self):
        self.assertEqual([x["id"] for x in self.ev["items"]],[f"RCS-{i:03d}" for i in range(18,27)])

    def test_layer_d_cannot_be_promoted_by_synthesis(self):
        r22=next(x for x in self.ev["items"] if x["id"]=="RCS-022")
        self.assertEqual(r22["qualification_status"],"interoperability_unqualified")
        bad=copy.deepcopy(r22); bad["qualification_status"]="interoperability_qualified"
        self.assertNotEqual(bad["qualification_status"],r22["qualification_status"])

    def test_all_decisions_classified(self):
        self.assertEqual([x["decision"] for x in self.delta["decisions"]],[f"DR-{i:04d}" for i in range(1,24)])

    def test_protected_source_audio_and_provenance(self):
        p=set(self.delta["protected_semantics"])
        self.assertIn("source/audio identity",p)
        self.assertIn("provenance",p)

    def test_windows_closure_is_fail_closed(self):
        d=json.loads((ROOT/"research/rcs-027/windows-step-qualification-v1.json").read_text())
        if d["status"]=="pending_ci":
            self.assertFalse(d["gate5_closure"])
        else:
            self.assertEqual(d["status"],"accepted")
            self.assertTrue(d["gate5_closure"])
            self.assertEqual(d["qualification_status"],"interoperability_unqualified")
            self.assertEqual(d["negative_controls_passed"],7)
            self.assertEqual(d["live_repetitions"],3)

if __name__=="__main__": unittest.main()
