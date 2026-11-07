"""Bounded arithmetic evaluator, NOT a mathematical-semantic verifier.

Numeric provenance is checked against the question: exact numeric literals and
limited, unambiguous lexical number words. This deliberately rejects many valid
expressions rather than silently licensing an invented quantity.
"""
import ast
import re
from fractions import Fraction

_WORDS = {
    "zero": 0, "one": 1, "a": 1, "an": 1, "two": 2, "twice": 2, "three": 3,
    "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,
    "hundred": 100, "half": Fraction(1, 2), "quarter": Fraction(1, 4),
}
_NUM = re.compile(r"(?<![A-Za-z0-9_])(?:\d+(?:,\d{3})*(?:\.\d+)?|\.\d+)(?![A-Za-z0-9_])")
_WORD = re.compile(r"\b[A-Za-z]+\b")
_ALLOWED = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd)


class CalculationError(ValueError):
    pass


def evidence_values(text):
    vals = set()
    for m in _NUM.finditer(text):
        vals.add(Fraction(m.group().replace(",", "")))
        if text[m.end():].lstrip().startswith("%"):
            vals.add(Fraction(m.group().replace(",", "")) / 100)
    words = [m.group().lower() for m in _WORD.finditer(text)]
    for i, word in enumerate(words):
        if word in _WORDS and word not in ("a", "an"):
            vals.add(Fraction(_WORDS[word]))
        if word in ("a", "an") and i+1 < len(words) and words[i+1] in ("additional", "extra", "single"):
            vals.add(Fraction(1))
    # Do not implicitly use 'hundred' as 100 in a compound number unless it appears.
    return vals


def calculate(expression, question, *, max_nodes=60, max_abs=10**12):
    """Return exact fraction and referenced literals. Raises on unsafe expressions.

    Important: semantic correctness is deliberately NEVER inferred from this.
    """
    if not expression or len(expression) > 240:
        raise CalculationError("EMPTY_OR_LONG_EXPRESSION")
    if not isinstance(question, str):
        raise CalculationError("INVALID_QUESTION")
    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError) as e:
        raise CalculationError("INVALID_SYNTAX") from e
    nodes = list(ast.walk(tree))
    if len(nodes) > max_nodes or any(not isinstance(n, _ALLOWED) for n in nodes):
        raise CalculationError("DISALLOWED_AST")
    seen = []
    def visit(n, depth=0):
        if depth > 20:
            raise CalculationError("TOO_DEEP")
        if isinstance(n, ast.Expression):
            return visit(n.body, depth+1)
        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
            # Using repr(float) avoids binary floating-point inaccuracies.
            value = Fraction(str(n.value))
            seen.append(value)
            return value
        if isinstance(n, ast.UnaryOp):
            a = visit(n.operand, depth+1)
            return -a if isinstance(n.op, ast.USub) else a
        if isinstance(n, ast.BinOp):
            a, b = visit(n.left, depth+1), visit(n.right, depth+1)
            if isinstance(n.op, ast.Add):
                r = a+b
            elif isinstance(n.op, ast.Sub):
                r = a-b
            elif isinstance(n.op, ast.Mult):
                r = a*b
            elif isinstance(n.op, ast.Div):
                if not b:
                    raise CalculationError("DIVISION_BY_ZERO")
                r = a/b
            else:
                raise CalculationError("DISALLOWED_OPERATOR")
            if abs(r) > max_abs or r.numerator.bit_length()>120 or r.denominator.bit_length()>120:
                raise CalculationError("VALUE_OUT_OF_BOUNDS")
            return r
        raise CalculationError("UNSUPPORTED_NODE")
    result = visit(tree)
    allowed = evidence_values(question)
    missing = sorted({str(v) for v in seen if v not in allowed})
    if missing:
        raise CalculationError("UNSUPPORTED_LITERAL:" + ",".join(missing))
    return {"status": "arithmetic_evaluated", "value_fraction": str(result),
            "value_decimal": round(float(result), 8), "literal_provenance_checked": True,
            "semantic_correctness_verified": False, "expression": expression}
