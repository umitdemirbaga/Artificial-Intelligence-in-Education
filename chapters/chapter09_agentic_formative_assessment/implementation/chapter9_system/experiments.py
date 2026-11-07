"""Versioned, append-only experiment recording with guard against silent reruns."""
from pathlib import Path
import json
import os
import csv
from .contracts import Case, canonical_json, fingerprint, ContractError
from .pipeline import assess, SYSTEM_ID
from .prompts import PROMPT_VERSION


class ExperimentError(RuntimeError): pass


def read_cases(path):
    path=Path(path)
    cases=[]
    if path.suffix.lower()==".csv":
        with path.open("r",encoding="utf-8-sig",newline="") as f:
            for r in csv.DictReader(f):
                if not {"case_id","question"}.issubset(r):
                    raise ContractError("CSV requires case_id and question")
                sol=r.get("student_incorrect_solution",r.get("student_solution", ""))
                cases.append(Case(r["case_id"],r["question"],sol))
    elif path.suffix.lower()==".jsonl":
        with path.open("r",encoding="utf-8-sig") as f:
            for line in f:
                if line.strip():
                    r=json.loads(line)
                    cases.append(Case(r["case_id"],r["question"],r.get("student_solution",r.get("student_incorrect_solution",""))))
    else: raise ExperimentError("Only CSV or JSONL inputs")
    if len({c.case_id for c in cases})!=len(cases):
        raise ExperimentError("DUPLICATE_CASE_ID")
    return cases


def records(path):
    if not Path(path).exists(): return {}
    result={}
    with open(path,encoding="utf-8",newline="") as f:
        for line in f:
            if not line.strip():continue
            r=json.loads(line)
            cid=r["case_id"]
            if cid in result: raise ExperimentError("DUPLICATE_STORED_CASE")
            result[cid]=r
    return result


def append_immutable(path, obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf-8",newline="\n") as f:
        f.write(canonical_json(obj)+"\n"); f.flush(); os.fsync(f.fileno())


def run_cases(cases, client, out_dir, *, max_cases=None):
    """Resume only if full input manifest (ordered hashes + configuration) unchanged."""
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    cases=list(cases)
    if not cases: raise ExperimentError("EMPTY_INPUT")
    all_ids=[c.case_id for c in cases]
    if len(set(all_ids))!=len(all_ids): raise ExperimentError("DUPLICATE_CASE_ID")
    config={"schema_version":1,"system_id":SYSTEM_ID,"prompt_version":PROMPT_VERSION,
            "model":str(getattr(client,"model","unspecified")),
            "cases":[{"case_id":c.case_id,"input_sha256":c.input_hash} for c in cases]}
    manifest=out/"manifest.json"
    current=canonical_json(config)+"\n"
    if manifest.exists():
        if manifest.read_text(encoding="utf-8") != current:
            raise ExperimentError("EXPERIMENT_MANIFEST_CHANGED_USE_NEW_DIRECTORY")
    else:
        # Refuse to graft new manifest onto unknown pre-existing records.
        if (out/"case_records.jsonl").exists():
            raise ExperimentError("RECORDS_EXIST_WITHOUT_MANIFEST")
        manifest.write_text(current,encoding="utf-8",newline="\n")
    prev=records(out/"case_records.jsonl")
    known={c.case_id:c.input_hash for c in cases}
    for cid,r in prev.items():
        if cid not in known or r.get("input_sha256")!=known[cid]:
            raise ExperimentError("STORED_RECORD_INPUT_CHANGED")
    selected=cases if max_cases is None else cases[:max_cases]
    n_calls=0
    for i,c in enumerate(selected,1):
        if c.case_id in prev:
            print(f"[{i}/{len(selected)}] {c.case_id}: cached")
            continue
        result=assess(c,client)
        append_immutable(out/"case_records.jsonl",result)
        prev[c.case_id]=result
        n_calls+=result["model_calls"]
        print(f"[{i}/{len(selected)}] {c.case_id}: {result['route']} | calls={result['model_calls']}")
    summary={"system_id":SYSTEM_ID,"total_input_cases":len(cases),
             "recorded_cases":len(prev),"new_model_calls":n_calls,
             "review_required":sum(r["route"]=="TEACHER_REVIEW_REQUIRED" for r in prev.values()),
             "confident_feedback_authorized":0,
             "semantic_correctness_verified":False,
             "notes":"These counts are operational only. No independent reference-answer adjudication."}
    (out/"run_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    return summary
