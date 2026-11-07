"""F2.1 append-only experiment records, frozen prompt/model/code and dataset hashes."""
from pathlib import Path
import json, os, hashlib
from chapter9_system.contracts import canonical_json,fingerprint
from chapter9_system.experiments import records
from . import VERSION,SYSTEM_ID
from .pipeline import assess
from .prompts import DIAGNOSIS_SYSTEM,FEEDBACK_SYSTEM

class F21ExperimentError(RuntimeError): pass

def code_fingerprint():
    files=[]
    local=Path(__file__).parent
    for p in sorted(local.glob('*.py')):files.append(p)
    root=local.parent
    for name in ('chapter9_system/contracts.py','chapter9_system/calculator.py',
                 'chapter9_system/gates.py','chapter9_f2/verification.py'):
        files.append(root/name)
    return fingerprint({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})

def run_f21(cases,client,output,max_cases=2):
    cases=list(cases)
    if not cases or len({c.case_id for c in cases})!=len(cases):
        raise F21ExperimentError('EMPTY_OR_DUPLICATE_CASES')
    if max_cases is not None and (type(max_cases) is not int or max_cases<1):
        raise ValueError('max_cases must be positive integer or None')
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    manifest={'schema_version':1,'system_id':SYSTEM_ID,'version':VERSION,
       'model':str(getattr(client,'model','unspecified')),
       'llm_interface':{'mode':'json_schema','temperature':0,'num_predict':1100},
       'code_sha256':code_fingerprint(),
       'prompt_sha256':fingerprint({'diagnosis':DIAGNOSIS_SYSTEM,'feedback':FEEDBACK_SYSTEM}),
       'cases':[{'case_id':c.case_id,'input_sha256':c.input_hash} for c in cases]}
    manifest_path=out/'manifest.json'
    text=canonical_json(manifest)+'\n'
    if manifest_path.exists():
        if manifest_path.read_bytes()!=text.encode('utf-8'):
            raise F21ExperimentError('EXPERIMENT_MANIFEST_CHANGED_USE_NEW_DIRECTORY')
    else:
        if (out/'case_records.jsonl').exists():
            raise F21ExperimentError('RECORDS_EXIST_WITHOUT_MANIFEST')
        with manifest_path.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
    seen=records(out/'case_records.jsonl')
    hashes={c.case_id:c.input_hash for c in cases}
    for cid,r in seen.items():
        if cid not in hashes or r.get('input_sha256')!=hashes[cid] or r.get('system_id')!=SYSTEM_ID:
            raise F21ExperimentError('MISMATCHING_STORED_RECORD')
    chosen=cases if max_cases is None else cases[:max_cases]
    new_calls=0
    for i,c in enumerate(chosen,1):
        if c.case_id in seen:
            print(f'[{i}/{len(chosen)}] {c.case_id}: cached')
            continue
        r=assess(c,client)
        with (out/'case_records.jsonl').open('a',encoding='utf-8',newline='\n') as f:
            f.write(canonical_json(r)+'\n');f.flush();os.fsync(f.fileno())
        seen[c.case_id]=r;new_calls+=r['model_calls']
        print(f'[{i}/{len(chosen)}] {c.case_id}: {r["draft_status"]} | calls={r["model_calls"]}')
    summary={'system_id':SYSTEM_ID,'recorded_cases':len(seen),
          'new_model_calls':new_calls,'drafts_generated':sum(bool(x.get('feedback_draft')) for x in seen.values()),
          'diagnosis_failures':sum(x.get('diagnosis') is None for x in seen.values()),
          'arithmetic_rejections':sum(x.get('calculation',{}).get('status')=='rejected' for x in seen.values()),
          'teacher_review_required':len(seen),'automatic_student_feedback_released':0,
          'semantic_correctness_verified':False, 'heldout_accessed':False}
    (out/'run_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return summary
