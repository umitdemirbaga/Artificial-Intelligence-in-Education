"""A1-inspired two-stage model/tool/review orchestration (F1, not original A1 code)."""
from .contracts import Case, Diagnosis, Feedback, ContractError
from .calculator import calculate, CalculationError
from .prompts import PROMPT_VERSION, diagnosis_messages, feedback_messages
from .gates import evidence_gate, feedback_gate, review_route, SAFE_HINTS
from .client import ModelError
import time

SYSTEM_ID = "F1_A1_INSPIRED_INTEGRATED_V1"


def _no_feedback(reason, case):
    return {"system_id":SYSTEM_ID,"prompt_version":PROMPT_VERSION,
            "case_id":case.case_id,"input_sha256":case.input_hash,"model_calls":0,
            "diagnosis":None,"calculation":{"status":"not_attempted"},
            "feedback_draft":None,"route":"TEACHER_REVIEW_REQUIRED",
            "automated_personalised_feedback_authorised":False,
            "neutral_scaffold_for_review":SAFE_HINTS["target_check"],
            "review_reasons":[reason],"semantic_correctness_verified":False}


def assess(case, client):
    """Produce an auditable teacher-review case. Never release generated feedback automatically."""
    if not isinstance(case,Case): raise ContractError("Expected Case")
    t0=time.perf_counter()
    output=_no_feedback("NOT_EVALUATED",case)
    output["review_reasons"]=[]
    try:
        d_call=client.ask(diagnosis_messages(case))
        output["model_calls"]+=1
        diagnosis=Diagnosis.parse(d_call["parsed"])
        output["diagnosis"]=diagnosis.as_dict()
        issues=evidence_gate(case.student_solution,diagnosis)
        expression=diagnosis.arithmetic_expression
        try:
            calculation=calculate(expression,case.question) if expression else {"status":"not_proposed","semantic_correctness_verified":False}
        except CalculationError as err:
            calculation={"status":"rejected","reason":str(err),"semantic_correctness_verified":False}
        output["calculation"]=calculation
        output["diagnosis_runtime"]={"seconds":d_call.get("seconds"),"tokens_in":d_call.get("tokens_in"),"tokens_out":d_call.get("tokens_out")}
        try:
            f_call=client.ask(feedback_messages(case,diagnosis,calculation))
            output["model_calls"]+=1
            feedback=Feedback.parse(f_call["parsed"])
            output["feedback_draft"]=feedback.as_dict()
            output["feedback_runtime"]={"seconds":f_call.get("seconds"),"tokens_in":f_call.get("tokens_in"),"tokens_out":f_call.get("tokens_out")}
            issues.extend(feedback_gate(feedback))
        except (ModelError,ContractError,KeyError,ValueError,TypeError) as e:
            issues.append("FEEDBACK_MODEL_OR_SCHEMA_FAILURE:"+type(e).__name__)
        routing=review_route(diagnosis,calculation,issues)
        output.update({"route":routing["route"],
                "review_reasons":routing["reasons"],
                "neutral_scaffold_for_review":routing["neutral_scaffold_for_review"]})
    except (ModelError,ContractError,KeyError,ValueError,TypeError) as e:
        output["review_reasons"].append("DIAGNOSIS_MODEL_OR_SCHEMA_FAILURE:"+type(e).__name__)
    output["wall_seconds"]=round(time.perf_counter()-t0,3)
    return output
