import unittest
from chapter9_system.contracts import Case,Diagnosis,Feedback,ContractError,fingerprint

class ContractsTests(unittest.TestCase):
    def test_bad_case_empty_question(self):
        with self.assertRaises(ContractError):Case("x"," ","a")
    def test_bad_id(self):
        with self.assertRaises(ContractError):Case("a/b","q","s")
    def test_hash_reproducible(self):
        self.assertEqual(Case("1","question","answer").input_hash,Case("1","question","answer").input_hash)
    def test_hash_changes(self):
        self.assertNotEqual(Case("1","question","answer").input_hash,Case("1","question","answer2").input_hash)
    def test_strict_enums(self):
        with self.assertRaises(ContractError):Diagnosis.parse({"error_status":"always wrong", "evidence_quote":"a", "diagnosis":"b", "strategy":"unit_check", "arithmetic_expression":""})
    def test_missing_field(self):
        with self.assertRaises(ContractError):Diagnosis.parse({"error_status":"none"})
    def test_feedback_empty(self):
        with self.assertRaises(ContractError):Feedback.parse({"teacher_draft":" ","scaffold_question":"OK?"})
