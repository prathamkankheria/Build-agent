# calculator/pkg/calculator.py

import math
from collections.abc import Callable


class Calculator:
    def __init__(self) -> None:
        self.operators: dict[str, Callable[[float, float], float]] = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
        }
        self.precedence: dict[str, int] = {
            "+": 1,
            "-": 1,
            "*": 2,
            "/": 2,
        }
        # Postfix unary operators (e.g. "5 !").
        self.postfix_operators: dict[str, Callable[[float], float]] = {
            "!": self._factorial,
        }

    @staticmethod
    def _factorial(value: float) -> float:
        if value < 0 or not value.is_integer():
            raise ValueError(f"factorial is undefined for {value}")
        return float(math.factorial(int(value)))

    def evaluate(self, expression: str) -> float | None:
        if not expression or expression.isspace():
            return None
        tokens = expression.strip().split()
        return self._evaluate_infix(tokens)

    def _evaluate_infix(self, tokens: list[str]) -> float:
        values: list[float] = []
        operators: list[str] = []

        for token in tokens:
            if token in self.postfix_operators:
                if not values:
                    raise ValueError(f"not enough operands for postfix operator {token}")
                values.append(self.postfix_operators[token](values.pop()))
            elif token in self.operators:
                while (
                    operators
                    and operators[-1] in self.operators
                    and self.precedence[operators[-1]] >= self.precedence[token]
                ):
                    self._apply_operator(operators, values)
                operators.append(token)
            else:
                try:
                    values.append(float(token))
                except ValueError:
                    raise ValueError(f"invalid token: {token}")

        while operators:
            self._apply_operator(operators, values)

        if len(values) != 1:
            raise ValueError("invalid expression")

        return values[0]

    def _apply_operator(self, operators: list[str], values: list[float]) -> None:
        if not operators:
            return

        operator = operators.pop()
        if len(values) < 2:
            raise ValueError(f"not enough operands for operator {operator}")

        b = values.pop()
        a = values.pop()
        values.append(self.operators[operator](a, b))