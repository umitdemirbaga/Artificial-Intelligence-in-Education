"""Immutable run manifest and JSONL records independent from F1 experiments."""
from pathlib import Path
import json
import os
import hashlib
from chapter9_system.contracts import canonical_json, fingerprint
from chapter9_system.experiments import records
from . import VERSION,SYSTEM_ID
from .prompts import DIAGNOSIS_SYSTEM,FEEDBACK_SYSTEM
from .pipeline import assess

class F2ExperimentError(RuntimeError): pass


def code_fingerprint():
    """Reject reuse of old results after changing any F2 source file."""
    root=Path(__file__).parent
    names=('__init__.py','prompts.py','verification.py','pipeline.py','experiments.py')
    return fingerprint({n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names})


def _immutable_manifest(out,contents):
    manifest=out/'manifest.json'
    expected=canonical_json(contents)+'\n'
    if manifest.exists():
        if manifest.read_bytes()!=expected.encode('utf-8'):
            raise F2ExperimentError('F2_MANIFEST_CHANGED_USE_NEW_DIRECTORY')
    else:
        if (out/'case_records.jsonl').exists():
            raise F2ExperimentError('F2_RECORDS_EXIST_WITHOUT_MANIFEST')
        # Create exclusively (never overwrite existing records in races).
        with manifest.open('x',encoding='utf-8',newline='\n') as f: f.write(expected)


def run_f2(cases,client,out_dir,*,max_cases=2):
    cases=list(cases)
    if not cases or len({c.case_id for c in cases})!=len(cases):
        raise F2ExperimentError('EMPTY_OR_DUPLICATE_CASES')
    if max_cases is not None and (type(max_cases)!=int or max_cases<1):
        raise ValueError('max_cases must be positive int or None')
    out=Path(out_dir)
    out.mkdir(parents=True,exist_ok=True)
    manifest={'schema_version':2,'system_id':SYSTEM_ID,'version':VERSION,
       'model':str(getattr(client,'model','unknown')),
       'llm_inference_options':{'temperature':0,'num_predict':750},
       'code_sha256':code_fingerprint(),
       'prompt_sha256':fingerprint({'diagnosis':DIAGNOSIS_SYSTEM,'feedback':FEEDBACK_SYSTEM}),
       'cases':[{'case_id':c.case_id,'input_sha256':c.input_hash} for c in cases]}
    _immutable_manifest(out,manifest)
    seen=records(out/'case_records.jsonl')
    valid={c.case_id:c.input_hash for c in cases}
    for cid,r in seen.items():
        if cid not in valid or valid[cid]!=r.get('input_sha256') or r.get('system_id')!=SYSTEM_ID:
            raise F2ExperimentError('F2_STORED_RECORD_INPUT_CHANGED')
    chosen=cases if max_cases is None else cases[:max_cases]
    calls=0
    for i,c in enumerate(chosen,1):
        if c.case_id in seen:
            print(f'[{i}/{len(chosen)}] {c.case_id}: F2 cached')
            continue
        r=assess(c,client)
        record_path=out/'case_records.jsonl'
        with record_path.open('a',encoding='utf-8',newline='\n') as f:
            f.write(canonical_json(r)+'\n')
            f.flush()
            os.fsync(f.fileno())
        seen[c.case_id]=r
        calls+=r['model_calls']
        print(f'[{i}/{len(chosen)}] {c.case_id}: {r["draft_status"]} | model_calls={r["model_calls"]}')
    summary={'system_id':SYSTEM_ID,'recorded_cases':len(seen),'requested_case_count':len(chosen),
       'new_model_calls':calls,'drafts_generated':sum(bool(r.get('feedback_draft')) for r in seen.values()),
       'quarantined_drafts':sum(r.get('draft_status')=='QUARANTINED_FOR_TEACHER_REVIEW' for r in seen.values()),
       'teacher_review_required':len(seen),'automatic_student_feedback_released':0,
       'independent_semantic_correctness_verified':False,
       'evaluation':'Operational counts only; human semantic and pedagogical review required',
       'case_ids':sorted(seen)}
    with (out/'run_summary.json').open('w',encoding='utf-8',newline='\n') as f:
        json.dump(summary,f,indent=2,ensure_ascii=False);f.write('\n')
    return summary
