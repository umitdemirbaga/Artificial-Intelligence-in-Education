import unittest
from fractions import Fraction
from chapter9_system.calculator import calculate,evidence_values,CalculationError

class CalculatorTests(unittest.TestCase):
    def test_field_trip(self):
        c=calculate("50 + 20 * 5 - 20 * 7", "The class has $50 plus 20 students each pay $5 and 20 people cost $7.")
        self.assertEqual(c["value_fraction"],"10")
        self.assertFalse(c["semantic_correctness_verified"])
    def test_half_word(self):
        self.assertEqual(calculate("5*0.5", "Five students receive half of the total, 5.")["value_fraction"],"5/2")
    def test_percent(self):
        self.assertEqual(calculate("20*0.2", "A group of 20 receives 20%.")["value_fraction"],"4")
    def test_word_three(self):
        self.assertEqual(calculate("72/12*3", "72 inches cut into 12 pieces, ties three together.")["value_fraction"],"18")
    def test_fraction(self):
        self.assertEqual(calculate("7/2", "7 of an item and 2 portions.")["value_fraction"],"7/2")
    def test_reject_invented_literal(self):
        with self.assertRaisesRegex(CalculationError,"UNSUPPORTED_LITERAL"):
            calculate("5+99","The original amount is 5")
    def test_reject_function(self):
        with self.assertRaisesRegex(CalculationError,"DISALLOWED_AST"):
            calculate("__import__('os').system('echo unsafe')", "1 and 2")
    def test_reject_power(self):
        with self.assertRaisesRegex(CalculationError,"DISALLOWED_AST"):
            calculate("2**12","2 and 12")
    def test_reject_div_zero(self):
        with self.assertRaisesRegex(CalculationError,"DIVISION_BY_ZERO"):
            calculate("2/0","2 and 0")
    def test_reject_variable(self):
        with self.assertRaisesRegex(CalculationError,"DISALLOWED_AST"):
            calculate("x+2","2 apples")
    def test_missing_expression(self):
        with self.assertRaisesRegex(CalculationError,"EMPTY_OR_LONG_EXPRESSION"):
            calculate("", "2 apples")
    def test_no_unqualified_an_one(self):
        self.assertNotIn(Fraction(1),evidence_values("A teacher asked a question."))
    def test_arithmetic_semantics_not_claimed(self):
        self.assertFalse(calculate("30/(2*3*2)","30 minutes, twice, three times, and two riders.")["semantic_correctness_verified"])
