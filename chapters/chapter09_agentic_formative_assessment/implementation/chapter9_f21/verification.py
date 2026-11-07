"""Incremental F2.1 flags: risk signals only, not semantic truth claims."""
import re
from chapter9_f2.verification import inspect_feedback

_AFFIRMS_MATH = re.compile(
    r'(?:arithmetic|calculation|computation|equation|expression|math(?:ematical)?)'
    r'.{0,105}?(?:mathematically\s+valid|valid|correct|accurate|checks\s+out)',
    re.I | re.S,
)
_FINAL_EQ = re.compile(r'\b(?:correct|actual|final)\b.{0,110}?\d+\s*=\s*\d+',re.I | re.S)

def check_unverified_arithmetic_assertions(feedback,calculation):
    text=feedback.get('teacher_draft','')
    if calculation.get('status')=='arithmetic_evaluated':
        return []  # Semantic truth still unverified by the ordinary F2 gate.
    if _AFFIRMS_MATH.search(text) or _FINAL_EQ.search(text):
        return ['UNVERIFIED_ARITHMETIC_CLAIM_IN_DRAFT']
    return []

def inspect_feedback_f21(case,diag,feedback,calculation):
    return list(dict.fromkeys(inspect_feedback(case,diag,feedback,calculation)
             +check_unverified_arithmetic_assertions(feedback,calculation)))
