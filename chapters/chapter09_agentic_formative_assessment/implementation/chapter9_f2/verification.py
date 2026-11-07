"""Deterministic *risk detection*, not a mathematical truth oracle.

All flags here are review triggers. Avoid claiming that text pattern matching
independently establishes the correctness of the mathematical relation.
"""
import re
from fractions import Fraction
from chapter9_system.calculator import calculate, CalculationError
from chapter9_system.contracts import Diagnosis, Feedback
from chapter9_system.gates import feedback_gate

_TARGET = re.compile(r"\b(?:how|what|which)\b[^?]{6,300}\?",re.I)
_STOP = frozenset(('the','a','an','are','is','of','to','in','on','at','with','from','for',
  'by','this','that','these','those','and','or','after','before','does','do','did',
  'would','should','could','will','have','has','many','much','how','what','which',
  'total','number','amount','all','altogether','altogether','them','their','there'))
_WORD = re.compile(r"[a-zA-Z]{3,}")


def find_target_region(question):
    """Return last question clause, or final imperative as a *heuristic* (never ground truth)."""
    found=list(_TARGET.finditer(question))
    if found:
        return found[-1].group().strip()
    sentences=[s.strip() for s in re.split(r"(?<=[.!?])\s+",question) if s.strip()]
    return sentences[-1] if sentences else question


def check_target_quote(question, quote):
    if not isinstance(quote,str) or not quote.strip():
        return ['TARGET_QUOTE_MISSING']
    if len(quote.strip())<12 or quote not in question:
        return ['TARGET_QUOTE_NOT_GROUNDED']
    # Restrict the quote to the actual target clause where a question exists.
    region=find_target_region(question)
    if quote not in region:
        return ['TARGET_QUOTE_NOT_IN_FINAL_QUESTION']
    return []


def inspect_diagnosis(case, diag):
    flags=check_target_quote(case.question,diag.get('target_quote',''))
    try:
        parsed=Diagnosis.parse(diag)
    except Exception:
        return list(dict.fromkeys(flags+['DIAGNOSIS_CONTRACT_INVALID']))
    if parsed.error_status in ('identified','possible') and not parsed.evidence_quote:
        flags.append('DIAGNOSIS_MISSING_STUDENT_EVIDENCE')
    if parsed.evidence_quote and parsed.evidence_quote not in case.student_solution:
        flags.append('DIAGNOSIS_EVIDENCE_NOT_IN_STUDENT_WORK')
    if parsed.error_status=='none' and _declares_error(parsed.diagnosis):
        flags.append('STATUS_NONE_CONFLICTS_WITH_ERROR_NARRATIVE')
    return list(dict.fromkeys(flags))


def _declares_error(text):
    t=text.lower()
    return bool(re.search(
        r"\b(?:student|learner|they)\s+(?:incorrectly|mistakenly|wrongly)\b"
        r"|\b(?:student|learner)[’']s\s+(?:error|mistake)\b"
        r"|\b(?:student|learner)[’']s\s+(?:solution|work|result|conclusion)\s+(?:incorrectly|mistakenly|wrongly|is\s+(?:wrong|incorrect))\b",
        t
    ))


def inspect_calculation(expression, question, student_solution):
    if not expression:
        return {'status':'not_proposed','semantic_correctness_verified':False,'provenance':'none'}, []
    try:
        c=calculate(expression,question)
        c['provenance']='question_only'
        c['target_alignment_verified']=False
        return c, ['ARITHMETIC_NOT_TARGET_VERIFIED']
    except CalculationError as e:
        original=str(e)
        # A student's intermediate numeric result is legitimate input to a
        # provisional arithmetic CHECK, but not an independent source of truth.
        if not original.startswith('UNSUPPORTED_LITERAL:'):
            return {'status':'rejected','reason':original,'semantic_correctness_verified':False},['ARITHMETIC_REJECTED']
        try:
            c=calculate(expression,question+'\n'+student_solution)
        except CalculationError:
            return {'status':'rejected','reason':original,'semantic_correctness_verified':False},['ARITHMETIC_REJECTED']
        c['provenance']='question_plus_student_untrusted'
        c['target_alignment_verified']=False
        return c,['STUDENT_DERIVED_LITERALS_UNVERIFIED','ARITHMETIC_NOT_TARGET_VERIFIED']

# High-precision target-result claim patterns (not general sentence interpretation).
_RESULT_CUES = re.compile(
    r"\b(?:leav(?:es|ing)|remain(?:s|ing)?|left(?:over)?|final\s+(?:answer|result)|correct\s+(?:answer|total)|answer\s+should\s+be|total\s+(?:amount|number|length|cost)\s+(?:is|equals?)|should\s+be)\s*(?:of|is|are|equals?|at)?\s*[:=]?\s*(?:\$\s*)?(-?\d+(?:,\d{3})*(?:\.\d+)?)",
    re.I
)
_FINAL_EXPRESSION = re.compile(
    r"\b(?:final|correct|actual)\s+(?:total|count|number|value|balance|answer|result)\b[^.!?\n]{0,130}?\s=\s*\$?\s*(-?\d+(?:,\d{3})*(?:\.\d+)?)",
    re.I
)
_RESULT_VALUE_PRECEDES = re.compile(
    r"(?:\$\s*)?(-?\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:\w+\s+){0,2}(?:left\b|remaining\b|in\s+total\b)",
    re.I
)


def result_claims(text):
    """Extract candidate result numbers for *review only*, without interpreting units."""
    result=set()
    for regex in (_RESULT_CUES,_RESULT_VALUE_PRECEDES,_FINAL_EXPRESSION):
        for m in regex.finditer(text or ''):
            try: result.add(Fraction(m.group(1).replace(',','')))
            except (ValueError,ZeroDivisionError): pass
    return result


def _numeric_status_flags(diagnosis_text, feedback_text, calculation):
    """Detect possible target-result inconsistencies without asserting truth."""
    d=result_claims(diagnosis_text)
    f=result_claims(feedback_text)
    flags=[]
    if d and f and d.isdisjoint(f):
        flags.append('POSSIBLE_CROSS_AGENT_RESULT_CONFLICT')
    if calculation.get('status')=='arithmetic_evaluated':
        try:
            v=Fraction(calculation['value_fraction'])
        except (KeyError,ValueError,ZeroDivisionError):
            return flags
        if d and v not in d:
            flags.append('POSSIBLE_DIAGNOSIS_ARITHMETIC_CONFLICT')
        if f and v not in f:
            flags.append('POSSIBLE_FEEDBACK_ARITHMETIC_CONFLICT')
    return flags


def inspect_feedback(case, diagnosis, feedback, calculation):
    flags=feedback_gate(Feedback.parse(feedback))
    flags+=_numeric_status_flags(diagnosis.get('diagnosis',''),feedback.get('teacher_draft',''),calculation)
    if diagnosis.get('error_status')=='none' and _declares_error(feedback.get('teacher_draft','')):
        flags.append('STATUS_NONE_FEEDBACK_CONFLICT')
    if diagnosis.get('error_status')=='none' and re.search(
            r'\b(?:final\s+(?:answer|step)|solution)\s+(?:is|was)\s+(?:missing|incomplete)\b',
            feedback.get('teacher_draft',''),re.I):
        flags.append('STATUS_NONE_INCOMPLETE_TARGET_REVIEW')
    target=diagnosis.get('target_quote','')
    # A lexical *coverage* signal, not a correctness guarantee.
    target_terms={w.lower() for w in _WORD.findall(target) if w.lower() not in _STOP and len(w)>3}
    text=feedback.get('teacher_draft','')+' '+feedback.get('scaffold_question','')
    fb_terms=set(w.lower() for w in _WORD.findall(text))
    if target_terms and not target_terms.intersection(fb_terms):
        flags.append('TARGET_NOT_LEXICALLY_REFERENCED_IN_FEEDBACK')
    return list(dict.fromkeys(flags))
