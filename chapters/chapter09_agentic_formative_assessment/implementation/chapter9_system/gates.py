"""Conservative routing: no arithmetic check certifies mathematical semantics."""
from .contracts import Diagnosis, Feedback

SAFE_HINTS = {
    "target_check": "What quantity is the question asking you to find, and where is it identified in your work?",
    "unit_check": "What units should each quantity have, and do the units agree with your operations?",
    "step_check": "Could you check each step against the information given before moving to the next one?",
    "relation_check": "Which quantities are related in the problem, and how could you show that relationship?",
}


def evidence_gate(student_solution, diagnosis):
    if not diagnosis.evidence_quote:
        return ["MISSING_EXACT_STUDENT_EVIDENCE"] if diagnosis.error_status=="identified" else []
    if diagnosis.evidence_quote not in student_solution:
        return ["UNSUPPORTED_STUDENT_QUOTE"]
    return []


def feedback_gate(feedback):
    issues=[]
    t=feedback.teacher_draft
    if len(t)>1200: issues.append("LONG_FEEDBACK_DRAFT")
    if any(s in t.lower() for s in ("the correct answer is", "the final answer is", "the answer is")):
        issues.append("POSSIBLE_PREMATURE_ANSWER")
    if len(feedback.scaffold_question)>400 or "?" not in feedback.scaffold_question:
        issues.append("NON_QUESTION_SCAFFOLD")
    return issues


def review_route(diagnosis, calc, issues):
    reasons=list(issues)
    if diagnosis.error_status in ("uncertain","possible","none"):
        reasons.append("DIAGNOSIS_NOT_CERTAIN")
    if calc.get("status")!="arithmetic_evaluated":
        reasons.append("ARITHMETIC_NOT_VERIFIED")
    reasons.append("SEMANTIC_CORRECTNESS_NOT_VERIFIED")
    return {"route":"TEACHER_REVIEW_REQUIRED", "reasons":list(dict.fromkeys(reasons)),
            "automated_personalised_feedback_authorised":False,
            "neutral_scaffold_for_review":SAFE_HINTS[diagnosis.strategy]}
