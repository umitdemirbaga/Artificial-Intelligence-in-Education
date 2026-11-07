import unittest, tempfile, json
from pathlib import Path
from fractions import Fraction
from unittest.mock import patch
from chapter9_system.contracts import Case
from chapter9_system.experiments import records
from chapter9_f21.client import StructuredOllamaClient,DIAGNOSIS_SCHEMA,FEEDBACK_SCHEMA
from chapter9_f21.pipeline import assess
from chapter9_f21.verification import check_unverified_arithmetic_assertions,inspect_feedback_f21
from chapter9_f21.experiments import run_f21,F21ExperimentError
from chapter9_f21.prompts import diagnosis_messages, feedback_messages

C=Case('SYN_01','Nora has 6 pencils and 2 more. How many pencils does Nora have?',
       'Nora wrote 6 + 2 = 9.')
D={'target_quote':'How many pencils does Nora have?','error_status':'possible',
   'evidence_quote':'6 + 2 = 9','diagnosis':'The student may have misadded 6+2.',
   'strategy':'step_check','arithmetic_expression':'6+2'}
F={'teacher_draft':'The student may have misadded; check the count.',
   'scaffold_question':'Can Nora check the number of pencils again?'}

class Fake:
    model='FAKE-QWEN'
    def __init__(self,d=None,f=None,fail=False):self.d=d or D;self.f=f or F;self.fail=fail;self.count=0;self.messages=[]
    def ask(self,m):
        self.count+=1;self.messages.append(m)
        if self.fail:raise RuntimeError('network down')
        return {'parsed':self.d if self.count==1 else self.f,'seconds':0.01}

class Tests(unittest.TestCase):
    def test_schema_diagnosis(self):
        self.assertEqual(len(DIAGNOSIS_SCHEMA['required']),6)
        self.assertEqual(DIAGNOSIS_SCHEMA['properties']['strategy']['enum'],
                         ['target_check','unit_check','step_check','relation_check'])
    def test_schema_feedback(self):self.assertEqual(len(FEEDBACK_SCHEMA['required']),2)
    def test_local_only(self):
        with self.assertRaises(ValueError):StructuredOllamaClient(url='https://evil.com')
    def test_client_json_schema_request(self):
        class Response:
            def __init__(self,data):self.data=data
            def __enter__(self):return self
            def __exit__(self,*a):return False
            def read(self):return self.data
        sent=[]
        def mock_open(req, timeout):
            request=json.loads(req.data.decode('utf-8'));sent.append(request)
            return Response(json.dumps({'message':{'content':json.dumps(D)},'eval_count':12}).encode())
        with patch('chapter9_f21.client.urlopen',mock_open):
            got=StructuredOllamaClient().ask(diagnosis_messages(C))
        self.assertEqual(got['parsed'],D)
        self.assertEqual(sent[0]['format'],DIAGNOSIS_SCHEMA)
        self.assertFalse(sent[0]['stream'])
        self.assertEqual(sent[0]['options']['temperature'],0)
    def test_client_rejects_wrong_schema(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*a):return False
            def read(self):return json.dumps({'message':{'content':json.dumps({'bogus':1})}}).encode()
        with patch('chapter9_f21.client.urlopen',lambda req,timeout: Response()):
            with self.assertRaises(Exception):StructuredOllamaClient().ask(diagnosis_messages(C))
    def test_assess_two_calls(self):
        f=Fake();r=assess(C,f)
        self.assertEqual(f.count,2);self.assertEqual(r['model_calls'],2)
        self.assertEqual(r['calculation']['value_fraction'],'8')
        self.assertEqual(r['route'],'TEACHER_REVIEW_REQUIRED')
    def test_assess_failure_safe(self):
        f=Fake(fail=True);r=assess(C,f)
        self.assertEqual(r['model_calls'],1)
        self.assertIsNone(r['feedback_draft'])
        self.assertEqual(r['draft_status'],'NOT_GENERATED')
    def test_no_reference_answers_in_messages(self):
        f=Fake();assess(C,f)
        self.assertTrue(all('reference_answer' not in str(m) for m in f.messages))
    def test_claim_invalid_calc(self):
        draft={'teacher_draft':'The arithmetic computation (60% of 800 = 480) is mathematically valid.'}
        self.assertIn('UNVERIFIED_ARITHMETIC_CLAIM_IN_DRAFT',
                 check_unverified_arithmetic_assertions(draft,{'status':'rejected'}))
    def test_valid_calc_not_claimed_verified(self):
        self.assertEqual(check_unverified_arithmetic_assertions(F,{'status':'arithmetic_evaluated'}),[])
    def test_plain_question_not_falsely_flagged(self):
        self.assertEqual(check_unverified_arithmetic_assertions(F,{'status':'rejected'}),[])
    def test_review_flag_in_pipeline(self):
        f=Fake(d={**D,'arithmetic_expression':'6 = 2'},
               f={**F,'teacher_draft':'The arithmetic calculation is mathematically valid.'})
        r=assess(C,f)
        self.assertIn('UNVERIFIED_ARITHMETIC_CLAIM_IN_DRAFT',r['guard_flags'])
        self.assertEqual(r['calculation']['status'],'rejected')
    def test_manifest_cache(self):
        with tempfile.TemporaryDirectory() as d:
            f=Fake();r=run_f21([C],f,d)
            self.assertEqual(r['recorded_cases'],1);self.assertEqual(f.count,2)
            snap=(Path(d)/'case_records.jsonl').read_bytes()
            r2=run_f21([C],Fake(fail=True),d)
            self.assertEqual(r2['new_model_calls'],0)
            self.assertEqual(snap,(Path(d)/'case_records.jsonl').read_bytes())
    def test_manifest_modified_question_reject(self):
        with tempfile.TemporaryDirectory() as d:
            run_f21([C],Fake(),d)
            other=Case(C.case_id,C.question+' x',C.student_solution)
            with self.assertRaises(F21ExperimentError):run_f21([other],Fake(),d)
    def test_manifest_modified_model_reject(self):
        with tempfile.TemporaryDirectory() as d:
            run_f21([C],Fake(),d)
            f=Fake();f.model='OTHER'
            with self.assertRaises(F21ExperimentError):run_f21([C],f,d)
    def test_stored_record_integrity(self):
        with tempfile.TemporaryDirectory() as d:
            run_f21([C],Fake(),d)
            rec=records(Path(d)/'case_records.jsonl')
            self.assertEqual(rec['SYN_01']['input_sha256'],C.input_hash)
            self.assertFalse(rec['SYN_01']['semantic_correctness_verified'])
            self.assertFalse(rec['SYN_01']['automated_personalised_feedback_authorised'])
    def test_schema_enum_guard(self):
        r=assess(C,Fake(d={**D,'error_status':'verified'}))
        self.assertEqual(r['draft_status'],'NOT_GENERATED')
        self.assertEqual(r['model_calls'],1)
    def test_feedback_schema_bad_safe(self):
        r=assess(C,Fake(f={'teacher_draft':'yes'}))
        self.assertEqual(r['draft_status'],'INVALID_FEEDBACK_DRAFT')
        self.assertEqual(r['model_calls'],2)
    def test_repeat_only_stage1_failed_is_immutable(self):
        with tempfile.TemporaryDirectory() as d:
            run_f21([C],Fake(fail=True),d)
            r2=run_f21([C],Fake(),d)
            self.assertEqual(r2['new_model_calls'],0)
            self.assertEqual(r2['drafts_generated'],0)
