import unittest
import tempfile
import json
from pathlib import Path
from chapter9_system.contracts import Case
from chapter9_system.experiments import read_cases,run_cases,records,ExperimentError
from tests.test_pipeline import Fake

class ExperimentsTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.base=Path(self.t.name)
    def tearDown(self):self.t.cleanup()
    def test_idempotent_resume(self):
        cases=[Case("S1","2 plus 2 apples","2 + 2 = 5")]
        c=Fake();s1=run_cases(cases,c,self.base)
        self.assertEqual(c.count,2)
        c2=Fake();s2=run_cases(cases,c2,self.base)
        self.assertEqual(c2.count,0)
        self.assertEqual(s1["recorded_cases"],s2["recorded_cases"])
        self.assertEqual(len(records(self.base/"case_records.jsonl")),1)
    def test_manifest_detects_changed_input(self):
        c=Case("S1","2 plus 2 apples","2 + 2 = 5")
        run_cases([c],Fake(),self.base)
        with self.assertRaisesRegex(ExperimentError,"MANIFEST_CHANGED"):
            run_cases([Case("S1","A changed problem","2 + 2 = 5")],Fake(),self.base)
    def test_manifest_detects_changed_model(self):
        c=Case("S1","2 plus 2 apples","2 + 2 = 5")
        run_cases([c],Fake(),self.base)
        other=Fake();other.model="OTHER_MODEL"
        with self.assertRaisesRegex(ExperimentError,"MANIFEST_CHANGED"):
            run_cases([c],other,self.base)
    def test_partial_resume(self):
        cases=[Case("S1","2 plus 2 apples","2 + 2 = 5"),Case("S2","2 plus 2 apples","2 + 2 = 5")]
        run_cases(cases,Fake(),self.base,max_cases=1)
        c=Fake();s=run_cases(cases,c,self.base)
        self.assertEqual(s["recorded_cases"],2)
        self.assertEqual(c.count,2)
    def test_duplicate_rejected(self):
        c=Case("S1","2 plus 2 apples","2 + 2 = 5")
        with self.assertRaises(ExperimentError):run_cases([c,c],Fake(),self.base)
    def test_csv_parsing_ignores_reference(self):
        path=self.base/"data.csv"
        path.write_text('case_id,question,student_incorrect_solution,adjudicated_mathematical_answer\nS1,2 plus 2,2 plus 2 equals 5,4\n',encoding='utf8')
        c=read_cases(path)
        self.assertEqual(len(c),1)
        self.assertNotIn("adjudicated",str(c[0].inference_dict()))
    def test_jsonl_parsing(self):
        path=self.base/"data.jsonl"
        path.write_text(json.dumps({"case_id":"S1","question":"2 plus 2?","student_solution":"5"})+"\n")
        self.assertEqual(read_cases(path)[0].student_solution,"5")
    def test_unmanaged_records_rejected(self):
        (self.base/"case_records.jsonl").write_text('{}\n')
        with self.assertRaisesRegex(ExperimentError,"WITHOUT_MANIFEST"):
            run_cases([Case("S1","2 plus 2","3")],Fake(),self.base)
