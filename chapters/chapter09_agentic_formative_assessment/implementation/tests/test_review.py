import unittest
import json
import csv
from tempfile import TemporaryDirectory
from pathlib import Path
from chapter9_system.review import create_review_sheet,score_review_sheet

class ReviewTests(unittest.TestCase):
    def test_review_form_is_empty_and_human_scored(self):
        with TemporaryDirectory() as d:
            d=Path(d)
            (d/"case_records.jsonl").write_text(json.dumps({"case_id":"C1","input_sha256":"x",
                "system_id":"F1","feedback_draft":{"teacher_draft":"draft","scaffold_question":"why?"}})+"\n")
            self.assertEqual(create_review_sheet(d/"case_records.jsonl",d/"human.csv"),1)
            with open(d/"human.csv",newline="") as f:
                rows=list(csv.DictReader(f)); cols=rows[0].keys()
            self.assertEqual(rows[0]["diagnosis_accuracy"],"")
            self.assertEqual(rows[0]["reviewer_id"],"")
            rows[0].update({"reviewer_id":"reviewer_X", "diagnosis_accuracy":"2",
                    "mathematical_consistency":"1","strategy_appropriateness":"2",
                    "scaffolding_quality":"2","premature_revelation_flag_0_1":"0"})
            with open(d/"filled.csv","w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
            x=score_review_sheet(d/"filled.csv",d/"human_summary.json")
            self.assertEqual(x["mean_score_0_8"],7)
    def test_review_empty_cannot_claim_human_score(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"r.csv"
            p.write_text('candidate_id,case_id,reviewer_id,diagnosis_accuracy,mathematical_consistency,strategy_appropriateness,scaffolding_quality,premature_revelation_flag_0_1\nF1,C1,,,,,,\n')
            with self.assertRaisesRegex(ValueError,"NO_COMPLETED_HUMAN_REVIEWS"):
                score_review_sheet(p,Path(d)/"out.json")
    def test_invalid_score_rejected(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"r.csv"
            p.write_text('candidate_id,case_id,reviewer_id,diagnosis_accuracy,mathematical_consistency,strategy_appropriateness,scaffolding_quality,premature_revelation_flag_0_1\nF1,C1,reviewer,3,2,2,2,0\n')
            with self.assertRaisesRegex(ValueError,"INVALID_REVIEW_SCORE"):
                score_review_sheet(p,Path(d)/"out.json")
