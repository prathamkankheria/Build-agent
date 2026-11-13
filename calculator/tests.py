# calculator/tests.py

import unittest
from pkg.calculator import Calculator


class TestCalculator(unittest.TestCase):
    def setUp(self) -> None:
        self.calculator = Calculator()

    def test_addition(self) -> None:
        result = self.calculator.evaluate("3 + 5")
        self.assertEqual(result, 8)

    def test_subtraction(self) -> None:
        result = self.calculator.evaluate("10 - 4")
        self.assertEqual(result, 6)

    def test_multiplication(self) -> None:
        result = self.calculator.evaluate("3 * 4")
        self.assertEqual(result, 12)

    def test_division(self) -> None:
        result = self.calculator.evaluate("10 / 2")
        self.assertEqual(result, 5)

    def test_nested_expression(self) -> None:
        result = self.calculator.evaluate("3 * 4 + 5")
        self.assertEqual(result, 17)

    def test_complex_expression(self) -> None:
        result = self.calculator.evaluate("2 * 3 - 8 / 2 + 5")
        self.assertEqual(result, 7)

    def test_empty_expression(self) -> None:
        result = self.calculator.evaluate("")
        self.assertIsNone(result)

    def test_invalid_operator(self) -> None:
        with self.assertRaises(ValueError):
            self.calculator.evaluate("$ 3 5")

    def test_not_enough_operands(self) -> None:
        with self.assertRaises(ValueError):
            self.calculator.evaluate("+ 3")

    def test_factorial(self) -> None:
        result = self.calculator.evaluate("5 !")
        self.assertEqual(result, 120)

    def test_factorial_of_zero(self) -> None:
        result = self.calculator.evaluate("0 !")
        self.assertEqual(result, 1)

    def test_factorial_in_expression(self) -> None:
        result = self.calculator.evaluate("3 + 5 !")
        self.assertEqual(result, 123)

    def test_factorial_with_multiplication(self) -> None:
        result = self.calculator.evaluate("5 ! * 2")
        self.assertEqual(result, 240)

    def test_factorial_invalid_operand(self) -> None:
        with self.assertRaises(ValueError):
            self.calculator.evaluate("2.5 !")

    def test_factorial_negative_operand(self) -> None:
        # Test that factorial raises error for negative numbers
        # (This tests the internal _factorial method directly since
        # the expression parser doesn't support negative literals)
        with self.assertRaises(ValueError):
            self.calculator._factorial(-5.0)


if __name__ == "__main__":
    unittest.main()