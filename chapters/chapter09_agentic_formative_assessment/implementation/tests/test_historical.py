import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from chapter9_system.historical import analyze

ROOT=Path(__file__).resolve().parents[1]

class HistoricalTests(unittest.TestCase):
    @unittest.skipUnless(all((ROOT/"data/restricted_local"/f).exists() for f in ("Chapter9_12case_AI_preliminary_ratings.csv", "Chapter9_critical_cases_detailed.csv", "four_system_12case_reference_audit_reviewed.csv")), "archival CSVs are not distributed in public-source build")
    def test_full_archival_analysis(self):
        with TemporaryDirectory() as t:
            x=analyze(ROOT/"data/restricted_local",t)
            self.assertEqual(x["rated_outputs"],48)
            self.assertEqual(x["critical_paired_A1_vs_A0"], {"A1_gt_A0":4,"A1_eq_A0":1,"A1_lt_A0":0})
            s={r["system"]:r for r in x["critical_subset"]}
            self.assertEqual(s["A1"]["mean_pedagogical_0_8"],"5.00")
            self.assertEqual(s["A2"]["mean_pedagogical_0_8"],"0.00")
            self.assertEqual(x["reference_audit"]["unambiguous_reference_consistent_development_cases"],9)
            self.assertIn("neither blinded independent",x["provenance"])
            self.assertTrue((Path(t)/"historical_dev_report.html").exists())
