"""Preparation and strict aggregation of independently entered human review scores."""
from pathlib import Path
import csv
import json
import statistics
from .experiments import records
from .historical import METRICS, _write_csv

REVIEW_COLS=["candidate_id","case_id","system","teacher_draft","scaffold_question",
             "reviewer_id",*METRICS,"premature_revelation_flag_0_1","reviewer_notes"]


def create_review_sheet(records_path, out_path):
    cases=records(records_path)
    if not cases:raise ValueError("NO_CASE_RECORDS")
    out=Path(out_path)
    if out.exists():raise FileExistsError("Do not overwrite a partially filled review sheet")
    rows=[]
    for cid,r in sorted(cases.items()):
        fb=r.get("feedback_draft") or {}
        rows.append({"candidate_id":"F1_"+cid,"case_id":cid,"system":r["system_id"],
                     "teacher_draft":fb.get("teacher_draft", ""),
                     "scaffold_question":fb.get("scaffold_question", ""),
                     "reviewer_id":"",**{m:"" for m in METRICS},
                     "premature_revelation_flag_0_1":"", "reviewer_notes":""})
    out.parent.mkdir(parents=True,exist_ok=True)
    _write_csv(out,REVIEW_COLS,rows)
    return len(rows)


def score_review_sheet(input_path, out_path):
    with open(input_path,encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    if not rows:raise ValueError("NO_REVIEW_ROWS")
    scored=[]; ids=set()
    for r in rows:
        values=[r.get(m,"").strip() for m in METRICS]
        if not r.get("reviewer_id","").strip() or not all(values):
            continue
        if any(x not in ("0","1","2") for x in values):raise ValueError("INVALID_REVIEW_SCORE")
        flag=r.get("premature_revelation_flag_0_1","").strip()
        if flag not in ("0","1"):raise ValueError("INVALID_REVELATION_FLAG")
        key=(r.get("candidate_id"),r["reviewer_id"])
        if key in ids:raise ValueError("DUPLICATE_REVIEWER_CANDIDATE")
        ids.add(key)
        scored.append({"candidate_id":r["candidate_id"],"case_id":r["case_id"],
                       "reviewer_id":r["reviewer_id"],"score_0_8":sum(map(int,values)),
                       "premature_revelation":int(flag)})
    if not scored:raise ValueError("NO_COMPLETED_HUMAN_REVIEWS")
    result={"source":"explicitly entered human-review scores, not AI preliminary",
           "input_rows":len(rows),"completed_reviews":len(scored),
           "distinct_reviewers":len(set(r["reviewer_id"] for r in scored)),
           "distinct_cases_reviewed":len(set(r["case_id"] for r in scored)),
           "mean_score_0_8":round(statistics.mean(r["score_0_8"] for r in scored),3),
           "premature_revelation_flags":sum(r["premature_revelation"] for r in scored),
           "note":"Incomplete cases excluded; report coverage and any pairing separately."}
    Path(out_path).parent.mkdir(parents=True,exist_ok=True)
    Path(out_path).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return result
