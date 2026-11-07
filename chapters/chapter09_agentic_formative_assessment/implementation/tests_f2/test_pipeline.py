import unittest
from chapter9_system.contracts import Case
from chapter9_f2.pipeline import assess
from chapter9_f2.prompts import diagnosis_messages,feedback_messages

CASE=Case('SYN_01','Nora has 6 pencils and 2 more. How many pencils does Nora have?',
          'Nora wrote 6 + 2 = 9.')
D={'target_quote':'How many pencils does Nora have?','error_status':'possible',
   'evidence_quote':'6 + 2 = 9','diagnosis':'The student adds incorrectly.',
   'strategy':'step_check','arithmetic_expression':'6+2'}
F={'teacher_draft':'The student may have added pencils incorrectly; check the counting.',
   'scaffold_question':'Can Nora recount the pencils to check the total?'}
class Client:
    model='FAKE'
    def __init__(self,d=None,f=None,error_at=None):
        self.d=D.copy() if d is None else d
        self.f=F.copy() if f is None else f
        self.error_at=error_at;self.count=0;self.messages=[]
    def ask(self,messages):
        self.count+=1;self.messages.append(messages)
        if self.error_at==self.count:raise RuntimeError('simulated failure')
        return {'parsed':self.d if self.count==1 else self.f,'seconds':0.02}

class PipelineTests(unittest.TestCase):
    def test_two_calls_and_review(self):
        c=Client();r=assess(CASE,c)
        self.assertEqual(c.count,2);self.assertEqual(r['model_calls'],2)
        self.assertEqual(r['route'],'TEACHER_REVIEW_REQUIRED')
        self.assertFalse(r['automated_personalised_feedback_authorised'])
        self.assertFalse(r['semantic_correctness_verified'])
    def test_target_is_verified(self):self.assertTrue(assess(CASE,Client())['target_quote_verified'])
    def test_correct_expression_not_certified(self):
        r=assess(CASE,Client());self.assertEqual(r['calculation']['value_fraction'],'8')
        self.assertIn('ARITHMETIC_NOT_TARGET_VERIFIED',r['guard_flags'])
    def test_bad_target_quarantined(self):
        c=Client(d={**D,'target_quote':'6 pencils'})
        r=assess(CASE,c)
        self.assertIn('TARGET_QUOTE_NOT_GROUNDED',r['guard_flags'])
        self.assertEqual(r['draft_status'],'QUARANTINED_FOR_TEACHER_REVIEW')
    def test_unsupported_student_quote_quarantined(self):
        c=Client(d={**D,'evidence_quote':'invented quote'})
        self.assertIn('DIAGNOSIS_EVIDENCE_NOT_IN_STUDENT_WORK',assess(CASE,c)['guard_flags'])
    def test_invalid_diagnosis_fails_closed(self):
        r=assess(CASE,Client(d={'target_quote':'bad'}))
        self.assertEqual(r['model_calls'],1)
        self.assertIsNone(r['feedback_draft'])
        self.assertTrue(any(x.startswith('DIAGNOSIS_MODEL_OR_SCHEMA_FAILURE') for x in r['review_reasons']))
    def test_bad_feedback_fails_closed(self):
        r=assess(CASE,Client(f={'teacher_draft':'bad'}))
        self.assertEqual(r['model_calls'],2)
        self.assertEqual(r['draft_status'],'INVALID_FEEDBACK_DRAFT')
    def test_ollama_failure_diagnosis(self):
        r=assess(CASE,Client(error_at=1))
        self.assertEqual(r['model_calls'],1)
        self.assertEqual(r['route'],'TEACHER_REVIEW_REQUIRED')
    def test_ollama_failure_feedback(self):
        r=assess(CASE,Client(error_at=2))
        self.assertEqual(r['model_calls'],2)
        self.assertEqual(r['draft_status'],'INVALID_FEEDBACK_DRAFT')
    def test_status_none_cross_conflict(self):
        c=Client(d={**D,'error_status':'none','diagnosis':'The student incorrectly multiplies.'})
        r=assess(CASE,c)
        self.assertIn('STATUS_NONE_CONFLICTS_WITH_ERROR_NARRATIVE',r['guard_flags'])
    def test_no_final_answer_in_suggestions(self):
        r=assess(CASE,Client())
        self.assertNotIn('the final answer is',r['neutral_scaffold_for_review'].lower())
    def test_no_reference_in_prompts(self):
        c=Client();assess(CASE,c)
        s=str(c.messages).lower()
        for banned in ('reference_answer','gold_answer','mathematical_ground_truth','adjudicated_mathematical_answer'):
            self.assertNotIn(banned,s)
    def test_teacher_review_flags_not_auto_clear(self):
        r=assess(CASE,Client(d={**D,'error_status':'identified'}))
        self.assertEqual(r['route'],'TEACHER_REVIEW_REQUIRED')
        self.assertFalse(r['automated_personalised_feedback_authorised'])
    def test_missing_target_quote_contract(self):
        r=assess(CASE,Client(d={k:v for k,v in D.items() if k!='target_quote'}))
        self.assertEqual(r['model_calls'],1)
    def test_arithmetic_reject_does_not_crash(self):
        r=assess(CASE,Client(d={**D,'arithmetic_expression':'6+99'}))
        self.assertEqual(r['calculation']['status'],'rejected')
        self.assertIn('ARITHMETIC_REJECTED',r['guard_flags'])
