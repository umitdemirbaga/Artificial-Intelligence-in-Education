import tempfile
import unittest
import json
from pathlib import Path
from chapter9_system.contracts import Case
from chapter9_f2.experiments import run_f2,F2ExperimentError,code_fingerprint
from chapter9_system.experiments import records
from tests_f2.test_pipeline import CASE,Client

CASE2=Case('SYN_02','Nora has 6 pencils and 2 more. How many pencils does Nora have?',
  'Nora wrote 6 + 2 = 9. The same example.')

class ExperimentTests(unittest.TestCase):
    def test_run_and_resume_calls_only_missing(self):
        with tempfile.TemporaryDirectory() as td:
            c=Client();a=run_f2([CASE,CASE2],c,td,max_cases=1)
            self.assertEqual(a['recorded_cases'],1);self.assertEqual(c.count,2)
            c2=Client();b=run_f2([CASE,CASE2],c2,td,max_cases=1)
            self.assertEqual(b['new_model_calls'],0);self.assertEqual(c2.count,0)
            c3=Client();e=run_f2([CASE,CASE2],c3,td,max_cases=2)
            self.assertEqual(e['recorded_cases'],2);self.assertEqual(c3.count,2)
    def test_different_model_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            run_f2([CASE],Client(),td)
            c=Client();c.model='FAKE-OTHER'
            with self.assertRaises(F2ExperimentError):run_f2([CASE],c,td)
    def test_different_inputs_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            run_f2([CASE],Client(),td)
            x=Case(CASE.case_id,CASE.question,CASE.student_solution+' changed')
            with self.assertRaises(F2ExperimentError):run_f2([x],Client(),td)
    def test_refuse_preexisting_records_without_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/'case_records.jsonl').write_text('{}\n')
            with self.assertRaises(F2ExperimentError):run_f2([CASE],Client(),td)
    def test_no_duplicate_case_ids(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(F2ExperimentError):run_f2([CASE,CASE],Client(),td)
    def test_no_zero_limit(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):run_f2([CASE],Client(),td,max_cases=0)
    def test_no_auto_feedback_release_in_summary(self):
        with tempfile.TemporaryDirectory() as td:
            summary=run_f2([CASE],Client(),td)
            self.assertEqual(summary['automatic_student_feedback_released'],0)
            self.assertFalse(summary['independent_semantic_correctness_verified'])
    def test_source_fingerprint_is_hex(self):
        fp=code_fingerprint();self.assertEqual(len(fp),64)
        self.assertEqual(fp,code_fingerprint())
    def test_record_hash_auditable(self):
        with tempfile.TemporaryDirectory() as td:
            run_f2([CASE],Client(),td)
            r=records(Path(td)/'case_records.jsonl')
            self.assertEqual(r['SYN_01']['input_sha256'],CASE.input_hash)
    def test_record_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            run_f2([CASE],Client(),td)
            p=Path(td)/'case_records.jsonl'
            obj=json.loads(p.read_text());obj['input_sha256']='bad'
            p.write_text(json.dumps(obj)+'\n')
            with self.assertRaises(F2ExperimentError):run_f2([CASE],Client(),td)
    def test_two_records_immutable_after_resume(self):
        with tempfile.TemporaryDirectory() as td:
            run_f2([CASE],Client(),td)
            p=Path(td)/'case_records.jsonl';data=p.read_bytes()
            run_f2([CASE],Client(),td)
            self.assertEqual(data,p.read_bytes())
    def test_manifest_records_no_reference_answer(self):
        with tempfile.TemporaryDirectory() as td:
            run_f2([CASE],Client(),td)
            s=(Path(td)/'manifest.json').read_text()
            self.assertNotIn('gold_answer',s)
            self.assertNotIn('student_solution',s)
