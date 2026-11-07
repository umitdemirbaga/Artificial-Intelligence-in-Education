"""F2 inference: diagnosis -> bounded arithmetic check -> feedback -> conservative audit.

Results are NEVER certified as mathematically correct by this code; reviews are
mandatory. Any malformed model output fails closed. Raw user content is data.
"""
import time
from chapter9_system.contracts import Case, Diagnosis, Feedback
from chapter9_system.gates import SAFE_HINTS
from . import VERSION, SYSTEM_ID
from .prompts import diagnosis_messages, feedback_messages
from .verification import inspect_diagnosis, inspect_calculation, inspect_feedback


def _baseline(case):
    return {
        'system_id':SYSTEM_ID,'version':VERSION,'case_id':case.case_id,
        'input_sha256':case.input_hash,'model_calls':0,'diagnosis':None,
        'calculation':{'status':'not_attempted','semantic_correctness_verified':False},
        'feedback_draft':None,'draft_status':'NOT_GENERATED',
        'target_quote':'','target_quote_verified':False,
        'guard_flags':[],'review_reasons':[],
        'route':'TEACHER_REVIEW_REQUIRED',
        'automated_personalised_feedback_authorised':False,
        'semantic_correctness_verified':False,
        'neutral_scaffold_for_review':SAFE_HINTS['target_check'],
        'diagnosis_runtime':None,'feedback_runtime':None,
    }


def assess(case,client):
    if not isinstance(case,Case): raise TypeError('Expected Case')
    started=time.perf_counter()
    out=_baseline(case)
    try:
        # Count the attempted call, even when Ollama fails.
        out['model_calls']+=1
        response=client.ask(diagnosis_messages(case))
        payload=response['parsed']
        if not isinstance(payload,dict) or not isinstance(payload.get('target_quote'),str):
            raise ValueError('TARGET_QUOTE_SCHEMA_MISSING')
        diagnosis=Diagnosis.parse(payload)
        out['diagnosis']=diagnosis.as_dict()
        out['target_quote']=payload['target_quote'].strip()
        out['diagnosis_runtime']={k:response.get(k) for k in ('seconds','tokens_in','tokens_out')}
        pre=inspect_diagnosis(case,payload)
        out['target_quote_verified']=not any(x.startswith('TARGET_QUOTE') for x in pre)
        calculation,calc_flags=inspect_calculation(diagnosis.arithmetic_expression,case.question,case.student_solution)
        out['calculation']=calculation
        pre.extend(calc_flags)
        out['guard_flags']=list(dict.fromkeys(pre))
        out['neutral_scaffold_for_review']=SAFE_HINTS[diagnosis.strategy]
        # Feedback receives explicit caution flags and the candidate target quote.
        # A draft can still be useful to a human reviewer even when pre-checks fail.
        try:
            out['model_calls']+=1
            response=client.ask(feedback_messages(case,payload,out['target_quote'],calculation,out['guard_flags']))
            feedback=Feedback.parse(response['parsed'])
            out['feedback_draft']=feedback.as_dict()
            out['feedback_runtime']={k:response.get(k) for k in ('seconds','tokens_in','tokens_out')}
            flags=inspect_feedback(case,payload,feedback.as_dict(),calculation)
            out['guard_flags']=list(dict.fromkeys(out['guard_flags']+flags))
            out['draft_status']='QUARANTINED_FOR_TEACHER_REVIEW' if out['guard_flags'] else 'TEACHER_REVIEW_ONLY'
        except Exception as e:
            out['draft_status']='INVALID_FEEDBACK_DRAFT'
            out['guard_flags'].append('FEEDBACK_MODEL_OR_SCHEMA_FAILURE:'+type(e).__name__)
    except Exception as e:
        out['guard_flags'].append('DIAGNOSIS_MODEL_OR_SCHEMA_FAILURE:'+type(e).__name__)
    out['guard_flags']=list(dict.fromkeys(out['guard_flags']))
    out['review_reasons']=list(dict.fromkeys(out['guard_flags']+['SEMANTIC_CORRECTNESS_NOT_VERIFIED']))
    out['wall_seconds']=round(time.perf_counter()-started,3)
    return out
