"""Honest reanalysis of existing *development* records; no fresh model calls.

The 48 candidate IDs are not fully unblinded in available inputs; only the
five selected critical cases have A0/A1/A2/A3 labels. Never impute missing
system labels for the remaining seven development cases.
"""
from pathlib import Path
import csv
import statistics
import hashlib
import json
import html
from .contracts import canonical_json

REQUIRED = ["Chapter9_12case_AI_preliminary_ratings.csv",
            "Chapter9_critical_cases_detailed.csv",
            "four_system_12case_reference_audit_reviewed.csv"]
METRICS=("diagnosis_accuracy","mathematical_consistency","strategy_appropriateness","scaffolding_quality")


def _read_csv(file):
    with open(file,encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path, cols, rows):
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)


def _fmt(v): return f"{v:.2f}"


def _html_table(columns, rows):
    return "<table><thead><tr>"+"".join("<th>"+html.escape(str(c))+"</th>" for c in columns)+"</tr></thead><tbody>"+"".join("<tr>"+"".join("<td>"+html.escape(str(r.get(c,"")))+"</td>" for c in columns)+"</tr>" for r in rows)+"</tbody></table>"


def analyze(data_dir, out_dir):
    src=Path(data_dir);out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    for f in REQUIRED:
        if not (src/f).is_file():raise FileNotFoundError(src/f)
    ratings=_read_csv(src/REQUIRED[0]);critical=_read_csv(src/REQUIRED[1]);audit=_read_csv(src/REQUIRED[2])
    if len(ratings)!=48 or len(critical)!=20 or len(audit)!=12:
        raise ValueError("UNEXPECTED_DATASET_CARDINALITY")
    if len(set(r["candidate_id"] for r in ratings))!=48:
        raise ValueError("DUPLICATED_CANDIDATE_ID")
    by_id={r["candidate_id"]:r for r in ratings}
    if len({r["case_id"] for r in audit})!=12:
        raise ValueError("AUDIT_CASE_ID_MISMATCH")
    case_to_flags={r["case_id"]:r for r in audit}
    if {r["case_id"] for r in ratings}!={r["case_id"] for r in audit}:
        raise ValueError("RATINGS_CASE_MISMATCH")
    expected={"A0","A1","A2","A3"}
    cases=set(r["case_id"] for r in critical)
    if len(cases)!=5:
        raise ValueError("UNEXPECTED_CRITICAL_SUBSET")
    for cid in cases:
        if {r["system"] for r in critical if r["case_id"]==cid}!=expected:
            raise ValueError("MISSING_CRITICAL_SYSTEM")
    if any(r["assessment_provenance"]!="ChatGPT preliminary assessment - not human reviewer" for r in ratings):
        raise ValueError("ASSESSMENT_PROVENANCE_NOT_AS_EXPECTED")
    for r in critical:
        source=by_id[r["candidate_id"]]
        if source["case_id"]!=r["case_id"]:
            raise ValueError("CRITICAL_MAPPING_MISMATCH")
        for m in METRICS:
            if int(source[m])!=int(r[m]):
                raise ValueError("CRITICAL_RATING_CONTRADICTION")
        total=sum(int(r[m]) for m in METRICS)
        if total!=int(r["pedagogical_total"]):
            raise ValueError("PEDAGOGICAL_TOTAL_NOT_REPRODUCIBLE")
    summary=[]
    for system in sorted(expected):
        rows=[r for r in critical if r["system"]==system]
        clear=[r for r in rows if case_to_flags[r["case_id"]]["question_ambiguity"]=="no" and case_to_flags[r["case_id"]]["reference_consistency"]=="consistent"]
        def score(r):return sum(int(r[m]) for m in METRICS)
        summary.append({"system":system,"n_critical":len(rows),
            "mean_pedagogical_0_8":_fmt(statistics.mean(score(r) for r in rows)),
            "n_unambiguous":len(clear),
            "mean_unambiguous_0_8":_fmt(statistics.mean(score(r) for r in clear)) if clear else "",
            "mean_math_consistency_0_2":_fmt(statistics.mean(int(r["mathematical_consistency"]) for r in rows)),
            "rating_source":"AI preliminary, not independent human"})
    case_details=[]
    for cid in sorted(cases):
        row={"case_id":cid, "question_ambiguity":case_to_flags[cid]["question_ambiguity"],
            "reference_consistency":case_to_flags[cid]["reference_consistency"]}
        for sys in sorted(expected):
            rr=next(r for r in critical if r["case_id"]==cid and r["system"]==sys)
            row[sys+"_score_0_8"]=sum(int(rr[m]) for m in METRICS)
        row["A1_minus_A0"]=row["A1_score_0_8"]-row["A0_score_0_8"]
        case_details.append(row)
    pairs={"A1_gt_A0":sum(r["A1_minus_A0"]>0 for r in case_details),
           "A1_eq_A0":sum(r["A1_minus_A0"]==0 for r in case_details),
           "A1_lt_A0":sum(r["A1_minus_A0"]<0 for r in case_details)}
    by_case={}
    for r in ratings:
        by_case[r["case_id"]]=by_case.get(r["case_id"],0)+1
    if set(by_case.values())!={4}:
        raise ValueError("NOT_FOUR_RATINGS_PER_CASE")
    pooled_scores=[sum(int(r[m]) for m in METRICS) for r in ratings]
    flags={"unambiguous_reference_consistent_development_cases":sum(r["question_ambiguity"]=="no" and r["reference_consistency"]=="consistent" for r in audit),
           "ambiguous_or_reference_inconsistent_development_cases":sum(r["question_ambiguity"]!="no" or r["reference_consistency"]!="consistent" for r in audit)}
    sha={f:hashlib.sha256((src/f).read_bytes()).hexdigest() for f in REQUIRED}
    artifact={"study_type":"retrospective exploratory analysis of 12 MathDial development cases",
        "rated_outputs":48,"rated_cases":12,"paired_system_labeled_subset":5,
        "provenance":"AI preliminary review; neither blinded independent human ratings nor held-out evaluation",
        "all_48_pooled_mean_score_0_8":_fmt(statistics.mean(pooled_scores)),
        "critical_subset":summary,"critical_paired_A1_vs_A0":pairs,"reference_audit":flags,
        "limitations":["Only 5 selected cases have verifiable A0-A3 labels in the supplied files.",
            "Selection of critical subset makes cross-system estimates nonrepresentative.",
            "AI-generated ratings are not independent human judgments.",
            "No 76-case held-out test-set outcomes have been supplied or run.",
            "Historical model outputs are not evidence of new F1 implementation performance."],
        "source_sha256":sha}
    _write_csv(out/"historical_critical_system_summary.csv",list(summary[0]),summary)
    _write_csv(out/"historical_critical_paired_cases.csv",list(case_details[0]),case_details)
    (out/"historical_dev_summary.json").write_text(json.dumps(artifact,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    page="""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Chapter 9 | Archived development analysis</title><style>
:root{font-family:Inter,Segoe UI,Arial,sans-serif;color:#18283b;background:#f3f6fb}body{margin:0}main{max-width:1040px;margin:32px auto;padding:0 24px 56px}.hero{background:linear-gradient(110deg,#182e48,#294e76);color:#fff;border-radius:16px;padding:30px}.hero p{opacity:.8;max-width:800px}h1{margin-top:0}h2{margin-top:40px} .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:22px 0}.stat{background:#fff;border:1px solid #dbe3ed;border-radius:12px;padding:18px}.stat strong{display:block;font-size:27px;margin:3px 0}.stat span{font-size:13px;color:#5b6778}.note{border-left:4px solid #c68235;padding:12px 16px;background:#fff8ed;border-radius:5px}.panel{background:#fff;border:1px solid #dbe3ed;border-radius:12px;padding:18px;overflow:auto}table{width:100%;border-collapse:collapse;text-align:left;font-size:14px}th{color:#49637d;background:#f1f5f9}th,td{padding:12px;border-bottom:1px solid #e4e9f0}li{margin:7px 0}footer{color:#53677d;font-size:12px;margin-top:25px}</style></head><body><main><div class="hero"><h1>Chapter 9 · Development Evidence</h1><p>Archived, reproducible exploratory analysis. This report does not include newly run F1 model evaluations or held-out results.</p></div>"""
    page+=f'<div class="stats"><div class="stat"><span>Development cases</span><strong>12</strong></div><div class="stat"><span>Rated historical outputs</span><strong>48</strong></div><div class="stat"><span>System-unblinded critical cases</span><strong>5</strong></div><div class="stat"><span>Unambiguous audit cases</span><strong>{flags["unambiguous_reference_consistent_development_cases"]}</strong></div></div>'
    page+='<div class="note"><strong>Not an independent performance claim.</strong> Scores were generated by a preliminary AI review, not independently judged by human educators. Critical cases were selected and must not stand for all development cases.</div>'
    page+='<h2>Exploratory paired critical subset</h2><div class="panel">'+_html_table(list(summary[0]),summary)+'</div>'
    page+='<h2>Paired case scores</h2><div class="panel">'+_html_table(list(case_details[0]),case_details)+'</div>'
    page+='<h2>Interpretation and limits</h2><div class="panel"><p>A1 exceeds A0 on '+str(pairs["A1_gt_A0"])+"/5 cases and ties on "+str(pairs["A1_eq_A0"])+"/5. These are descriptive observations, not effect-size estimates for a population.</p><ul>"+"".join('<li>'+html.escape(s)+'</li>' for s in artifact["limitations"])+"</ul></div>"
    page+='<footer>Source hashes and complete formula checks are recorded in historical_dev_summary.json. No held-out data were processed.</footer></main></body></html>'
    (out/"historical_dev_report.html").write_text(page,encoding="utf-8")
    return artifact
