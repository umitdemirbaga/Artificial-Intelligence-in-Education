"""F2.1 conservative pipeline: no automatic student release, no semantic certification."""
import time
from chapter9_system.contracts import Case, Diagnosis, Feedback
from chapter9_system.gates import SAFE_HINTS
from chapter9_f2.verification import inspect_diagnosis, inspect_calculation
from . import SYSTEM_ID,VERSION
from .prompts import diagnosis_messages,feedback_messages
from .verification import inspect_feedback_f21


def assess(case, client):
    if not isinstance(case,Case): raise TypeError('Expected Case')
    t0=time.perf_counter()
    out={'system_id':SYSTEM_ID,'version':VERSION,'case_id':case.case_id,
         'input_sha256':case.input_hash,'model_calls':0,'diagnosis':None,
         'calculation':{'status':'not_attempted','semantic_correctness_verified':False},
         'feedback_draft':None,'draft_status':'NOT_GENERATED',
         'target_quote':'','target_quote_verified':False,'guard_flags':[],
         'review_reasons':[],'route':'TEACHER_REVIEW_REQUIRED',
         'automated_personalised_feedback_authorised':False,
         'semantic_correctness_verified':False,
         'neutral_scaffold_for_review':SAFE_HINTS['target_check']}
    try:
        out['model_calls']+=1
        response=client.ask(diagnosis_messages(case))
        payload=response['parsed']
        if not isinstance(payload,dict) or not isinstance(payload.get('target_quote'),str):
            raise ValueError('BAD_TARGET_QUOTE_FIELD')
        diag=Diagnosis.parse(payload)
        out['diagnosis']=diag.as_dict()
        out['target_quote']=payload['target_quote'].strip()
        out['diagnosis_runtime']={k:response.get(k) for k in ('seconds','tokens_in','tokens_out')}
        pre=inspect_diagnosis(case,payload)
        out['target_quote_verified']=not any(k.startswith('TARGET_QUOTE') for k in pre)
        calc,extra=inspect_calculation(diag.arithmetic_expression,case.question,case.student_solution)
        out['calculation']=calc
        pre.extend(extra)
        out['guard_flags']=list(dict.fromkeys(pre))
        out['neutral_scaffold_for_review']=SAFE_HINTS[diag.strategy]
        try:
            out['model_calls']+=1
            response=client.ask(feedback_messages(case,payload,out['target_quote'],calc,pre))
            feedback=Feedback.parse(response['parsed'])
            out['feedback_draft']=feedback.as_dict()
            out['feedback_runtime']={k:response.get(k) for k in ('seconds','tokens_in','tokens_out')}
            fflags=inspect_feedback_f21(case,payload,feedback.as_dict(),calc)
            out['guard_flags']=list(dict.fromkeys(pre+fflags))
            out['draft_status']='QUARANTINED_FOR_TEACHER_REVIEW' if out['guard_flags'] else 'TEACHER_REVIEW_ONLY'
        except Exception as exc:
            out['draft_status']='INVALID_FEEDBACK_DRAFT'
            out['guard_flags'].append('FEEDBACK_MODEL_OR_SCHEMA_FAILURE:'+type(exc).__name__)
    except Exception as exc:
        out['guard_flags'].append('DIAGNOSIS_MODEL_OR_SCHEMA_FAILURE:'+type(exc).__name__)
    out['guard_flags']=list(dict.fromkeys(out['guard_flags']))
    out['review_reasons']=list(dict.fromkeys(out['guard_flags']+['SEMANTIC_CORRECTNESS_NOT_VERIFIED']))
    out['wall_seconds']=round(time.perf_counter()-t0,3)
    return out
