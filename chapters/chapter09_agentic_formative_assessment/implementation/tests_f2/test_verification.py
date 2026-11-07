import unittest
from fractions import Fraction
from chapter9_system.contracts import Case
from chapter9_f2.verification import (
    find_target_region,check_target_quote,inspect_diagnosis,inspect_calculation,
    result_claims,inspect_feedback
)

C=Case('SYN_A','Nora has 6 pencils and 2 more. How many pencils does Nora have?',
 'Nora thinks 6 + 2 = 9 and writes that 9 pencils remain.')

def d(**kw):
    obj={'target_quote':'How many pencils does Nora have?',
         'error_status':'possible','evidence_quote':'6 + 2 = 9',
         'diagnosis':'The student may have added incorrectly.',
         'strategy':'step_check','arithmetic_expression':'6+2'}
    obj.update(kw);return obj

def f(**kw):
    obj={'teacher_draft':'Check the student addition step involving Nora pencils.',
         'scaffold_question':'Can you recount the pencils and explain the sum?'}
    obj.update(kw);return obj

class TargetTests(unittest.TestCase):
    def test_terminal_target(self):self.assertEqual(find_target_region(C.question),'How many pencils does Nora have?')
    def test_question_missing_uses_last_sentence(self):self.assertIn('calculate',find_target_region('There are 3. Now calculate a total.'))
    def test_empty_target_rejected(self):self.assertIn('TARGET_QUOTE_MISSING',check_target_quote(C.question,''))
    def test_unsupported_quote_rejected(self):self.assertIn('TARGET_QUOTE_NOT_GROUNDED',check_target_quote(C.question,'How many cars arrived?'))
    def test_intermediate_quote_rejected(self):self.assertIn('TARGET_QUOTE_NOT_IN_FINAL_QUESTION',check_target_quote(C.question,'Nora has 6 pencils and 2 more.'))
    def test_true_final_question_accepted(self):self.assertEqual(check_target_quote(C.question,'How many pencils does Nora have?'),[])
    def test_short_number_not_target(self):self.assertIn('TARGET_QUOTE_NOT_GROUNDED',check_target_quote(C.question,'6'))
    def test_trailing_question_last(self):self.assertIn('pencils',find_target_region('What is 2+3? How many pencils does Nora have?'))

class DiagnosisTests(unittest.TestCase):
    def test_supported(self):self.assertEqual(inspect_diagnosis(C,d()),[])
    def test_no_evidence_for_possible(self):self.assertIn('DIAGNOSIS_MISSING_STUDENT_EVIDENCE',inspect_diagnosis(C,d(evidence_quote='')))
    def test_quote_hallucination(self):self.assertIn('DIAGNOSIS_EVIDENCE_NOT_IN_STUDENT_WORK',inspect_diagnosis(C,d(evidence_quote='I added 99')))
    def test_none_without_evidence_ok(self):self.assertNotIn('DIAGNOSIS_MISSING_STUDENT_EVIDENCE',inspect_diagnosis(C,d(error_status='none',evidence_quote='')))
    def test_none_conflicts_error_narrative(self):self.assertIn('STATUS_NONE_CONFLICTS_WITH_ERROR_NARRATIVE',inspect_diagnosis(C,d(error_status='none',diagnosis='The student incorrectly adds the values.')))
    def test_none_neutral_ok(self):self.assertNotIn('STATUS_NONE_CONFLICTS_WITH_ERROR_NARRATIVE',inspect_diagnosis(C,d(error_status='none',diagnosis='The student arrives at 8.')))
    def test_invalid_enum_guard(self):self.assertIn('DIAGNOSIS_CONTRACT_INVALID',inspect_diagnosis(C,d(error_status='invalid')))
    def test_quote_from_student_not_question(self):self.assertIn('DIAGNOSIS_EVIDENCE_NOT_IN_STUDENT_WORK',inspect_diagnosis(C,d(evidence_quote='Nora has 6 pencils')))

class CalculationTests(unittest.TestCase):
    def test_question_only_provenance(self):
        v,flags=inspect_calculation('6+2',C.question,C.student_solution)
        self.assertEqual(v['provenance'],'question_only');self.assertEqual(v['value_fraction'],'8')
        self.assertFalse(v['semantic_correctness_verified'])
    def test_student_literal_allowed_but_flagged(self):
        v,flags=inspect_calculation('6+9',C.question,C.student_solution)
        self.assertEqual(v['provenance'],'question_plus_student_untrusted')
        self.assertIn('STUDENT_DERIVED_LITERALS_UNVERIFIED',flags)
    def test_unseen_literal_rejected(self):
        v,flags=inspect_calculation('6+999',C.question,C.student_solution)
        self.assertEqual(v['status'],'rejected');self.assertIn('ARITHMETIC_REJECTED',flags)
    def test_unsafe_expression_rejected(self):
        v,flags=inspect_calculation("__import__('os').system('bad')",C.question,C.student_solution)
        self.assertEqual(v['status'],'rejected')
    def test_division_by_zero_rejected(self):
        v,flags=inspect_calculation('6/0',C.question,C.student_solution)
        self.assertEqual(v['status'],'rejected')
    def test_blank_is_not_proposed(self):
        v,flags=inspect_calculation('',C.question,C.student_solution)
        self.assertEqual(v['status'],'not_proposed');self.assertEqual(flags,[])
    def test_semantics_not_certified_for_student_literal(self):
        v,_=inspect_calculation('6+9',C.question,C.student_solution)
        self.assertFalse(v['target_alignment_verified'])
    def test_question_arithmetic_not_target_checked(self):
        v,flags=inspect_calculation('6+2',C.question,C.student_solution)
        self.assertIn('ARITHMETIC_NOT_TARGET_VERIFIED',flags)

class CrossChecks(unittest.TestCase):
    def test_dev003_leaving_conflict_detected(self):
        r=inspect_feedback(C,d(diagnosis='The amount is leaving $0.'),f(),
            {'status':'arithmetic_evaluated','value_fraction':'10'})
        self.assertIn('POSSIBLE_DIAGNOSIS_ARITHMETIC_CONFLICT',r)
    def test_paired_result_claims(self):
        self.assertIn(Fraction(0),result_claims('leaving $0'))
        self.assertIn(Fraction(10),result_claims('leaves $10'))
    def test_conflicting_agents(self):
        r=inspect_feedback(C,d(diagnosis='The final answer is 8.'),
            f(teacher_draft='The final answer is 9; check the pencils.'),
            {'status':'not_proposed'})
        self.assertIn('POSSIBLE_CROSS_AGENT_RESULT_CONFLICT',r)
    def test_shared_values_not_flagged(self):
        r=inspect_feedback(C,d(diagnosis='The final answer is 8.'),
            f(teacher_draft='The final answer is 8; check the pencils.'),
            {'status':'not_proposed'})
        self.assertNotIn('POSSIBLE_CROSS_AGENT_RESULT_CONFLICT',r)
    def test_status_none_feedback_conflict(self):
        r=inspect_feedback(C,d(error_status='none'),
            f(teacher_draft='The student incorrectly added the pencils.'),{'status':'not_proposed'})
        self.assertIn('STATUS_NONE_FEEDBACK_CONFLICT',r)
    def test_premature_disclosure_flag(self):
        r=inspect_feedback(C,d(),f(teacher_draft='The correct answer is 8.'),{'status':'not_proposed'})
        self.assertIn('POSSIBLE_PREMATURE_ANSWER',r)
    def test_no_target_lexical_match_flag(self):
        r=inspect_feedback(C,d(),f(teacher_draft='Reevaluate subtraction.',scaffold_question='What operation is needed?'),{'status':'not_proposed'})
        self.assertIn('TARGET_NOT_LEXICALLY_REFERENCED_IN_FEEDBACK',r)
    def test_target_lexical_match(self):
        r=inspect_feedback(C,d(),f(),{'status':'not_proposed'})
        self.assertNotIn('TARGET_NOT_LEXICALLY_REFERENCED_IN_FEEDBACK',r)
    def test_no_final_assertion_does_not_contradict(self):
        r=inspect_feedback(C,d(diagnosis='The learner may have mixed the units.'),f(),
            {'status':'arithmetic_evaluated','value_fraction':'8'})
        self.assertNotIn('POSSIBLE_DIAGNOSIS_ARITHMETIC_CONFLICT',r)
    def test_two_different_finite_results(self):
        self.assertEqual(result_claims('We have 400 people and 600 more.'),set())
    def test_none_declares_error_in_student_solution(self):
        x=inspect_feedback(C,d(error_status='none'),
             f(teacher_draft='The student’s solution incorrectly adds the quantities.'),{'status':'not_proposed'})
        self.assertIn('STATUS_NONE_FEEDBACK_CONFLICT',x)
    def test_final_expression_end_value(self):
        self.assertIn(Fraction(720),result_claims('The final count is 400 - 80 + 400 = 720 trees.'))
    def test_incomplete_target_after_none(self):
        x=inspect_feedback(C,d(error_status='none'),
           f(teacher_draft='The final answer is missing from the student solution.'),{'status':'not_proposed'})
        self.assertIn('STATUS_NONE_INCOMPLETE_TARGET_REVIEW',x)
    def test_feedback_invalid_syntax_raises(self):
        with self.assertRaises(Exception):
            inspect_feedback(C,d(),f(scaffold_question=2),{'status':'not_proposed'})
