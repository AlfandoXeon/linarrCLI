from __future__ import annotations

import ast
from dataclasses import dataclass
import fractions
import math
import operator
from typing import Any, Callable


@dataclass
class CalculationItem:
    expression: str
    result: float | int
    formatted_result: str
    fraction_str: str


class CalculatorService:
    ALLOWED_OPERATORS: dict[type[ast.AST], Callable[..., Any]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    ALLOWED_UNARY: dict[type[ast.AST], Callable[..., Any]] = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    ALLOWED_FUNCTIONS: dict[str, Callable[..., Any]] = {
        "abs": abs,
        "round": round,
        "sqrt": math.sqrt,
        "cbrt": math.cbrt,
        "ceil": math.ceil,
        "floor": math.floor,
        "log": math.log,
        "log10": math.log10,
        "log2": math.log2,
        "exp": math.exp,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "factorial": math.factorial,
        "gcd": math.gcd,
        "lcm": math.lcm,
        "min": min,
        "max": max,
    }

    ALLOWED_CONSTANTS: dict[str, float] = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    def __init__(self) -> None:
        self.history: list[CalculationItem] = []
        self.last_ans: float | int = 0

    def clear_history(self) -> None:
        self.history.clear()
        self.last_ans = 0

    def get_history(self) -> list[CalculationItem]:
        return list(self.history)

    def evaluate(self, raw_expression: str) -> CalculationItem:
        cleaned = self._preprocess(raw_expression)
        if not cleaned:
            raise ValueError("EKSPRESI TIDAK BOLEH KOSONG.")

        try:
            tree = ast.parse(cleaned, mode="eval")
        except SyntaxError as error:
            raise ValueError(f"SINTAKS EKSPRESI TIDAK VALID: {error.msg.upper()}.") from error

        numeric_result = self._eval_node(tree.body)

        if not isinstance(numeric_result, (int, float)):
            raise ValueError("HASIL EKSPRESI HARUS BERUPA BILANGAN NUMERIK.")

        if not math.isfinite(numeric_result):
            raise ValueError("HASIL TIDAK BERHINGGA (TIDAK FINIT).")

        # Normalize negative zero and integer-valued floats
        if numeric_result == 0.0 or numeric_result == 0:
            numeric_result = 0
        elif isinstance(numeric_result, float) and abs(numeric_result - round(numeric_result)) < 1e-12:
            numeric_result = int(round(numeric_result))

        formatted_result = self._format_result(numeric_result)
        fraction_str = self._format_fraction(numeric_result)

        item = CalculationItem(
            expression=raw_expression.strip(),
            result=numeric_result,
            formatted_result=formatted_result,
            fraction_str=fraction_str,
        )

        self.last_ans = numeric_result
        self.history.append(item)
        if len(self.history) > 50:
            self.history.pop(0)

        return item

    def _preprocess(self, expr: str) -> str:
        s = expr.strip()
        if not s:
            return ""
        # Support colon ':' as division symbol if not part of something else
        s = s.replace(":", "/")
        # Support '^' as exponentiation
        s = s.replace("^", "**")
        # Support multiplication symbol 'x' surrounded by spaces or numbers (e.g. 5 x 4)
        parts = s.split()
        if len(parts) > 1:
            for i in range(len(parts)):
                if parts[i] in ("x", "X"):
                    parts[i] = "*"
            s = " ".join(parts)
        return s

    def _eval_node(self, node: ast.AST) -> float | int:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"KONSTANTA TIDAK VALID: {node.value}.")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_OPERATORS:
                raise ValueError(f"OPERATOR {op_type.__name__.upper()} TIDAK DIDUKUNG.")

            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            if op_type in (ast.Div, ast.FloorDiv, ast.Mod):
                if right == 0:
                    raise ValueError("TIDAK BISA DIBAGI DENGAN NOL (DIVISION BY ZERO).")

            if op_type is ast.Pow:
                if abs(right) > 500 or (abs(left) > 1 and right > 500):
                    raise ValueError("PANGKAT TERLALU BESAR (POTENSI OVERFLOW).")
                try:
                    res = left**right
                except OverflowError as error:
                    raise ValueError("HASIL PERPANGKATAN MELEBIHI BATAS (OVERFLOW).") from error
                if isinstance(res, complex):
                    raise ValueError("HASIL PERPANGKATAN ADALAH BILANGAN KOMPLEKS/IMAJINER.")
                return res

            op_fn = self.ALLOWED_OPERATORS[op_type]
            try:
                res = op_fn(left, right)
            except OverflowError as error:
                raise ValueError("NILAI OPERASI MELEBIHI BATAS MAKSIMUM (OVERFLOW).") from error
            return res

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_UNARY:
                raise ValueError("OPERATOR UNARY TIDAK DIDUKUNG.")
            operand = self._eval_node(node.operand)
            return self.ALLOWED_UNARY[op_type](operand)

        if isinstance(node, ast.Name):
            name = node.id.lower()
            if name == "ans":
                return self.last_ans
            if name in self.ALLOWED_CONSTANTS:
                return self.ALLOWED_CONSTANTS[name]
            raise ValueError(f"VARIABEL ATAU KONSTANTA '{node.id.upper()}' TIDAK DIKENAL.")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("PEMANGGILAN FUNGSI TIDAK VALID.")
            func_name = node.func.id.lower()
            if func_name not in self.ALLOWED_FUNCTIONS:
                raise ValueError(f"FUNGSI '{node.func.id.upper()}' TIDAK TERDAFTAR ATAU TIDAK DIIZINKAN.")
            if node.keywords:
                raise ValueError("ARGUMEN KATA KUNCI (KEYWORD ARGUMENTS) TIDAK DIIZINKAN.")

            args = [self._eval_node(arg) for arg in node.args]

            # Domain and constraint validation for specific functions
            if func_name == "factorial":
                if len(args) != 1:
                    raise ValueError("FUNGSI FACTORIAL HANYA MENERIMA 1 ARGUMEN.")
                arg = args[0]
                if not isinstance(arg, int) and not (isinstance(arg, float) and arg.is_integer()):
                    raise ValueError("FAKTORIAL MEMERLUKAN BILANGAN BULAT.")
                int_arg = int(arg)
                if int_arg < 0:
                    raise ValueError("FAKTORIAL TIDAK DIDEFINISIKAN UNTUK BILANGAN NEGATIF.")
                if int_arg > 100:
                    raise ValueError("FAKTORIAL MAKSIMAL HINGGA NILAI 100.")
                return math.factorial(int_arg)

            if func_name == "sqrt":
                if len(args) != 1:
                    raise ValueError("FUNGSI SQRT HANYA MENERIMA 1 ARGUMEN.")
                if args[0] < 0:
                    raise ValueError("NILAI DI DALAM AKAR KUADRAT HARUS NON-NEGATIF (>= 0).")

            if func_name in ("log", "log10", "log2"):
                if args[0] <= 0:
                    raise ValueError("ARGUMEN LOGARITMA HARUS POSITIF (> 0).")

            fn = self.ALLOWED_FUNCTIONS[func_name]
            try:
                res = fn(*args)
            except TypeError as error:
                raise ValueError(f"ARGUMEN FUNGSI '{func_name.upper()}' TIDAK COCOK.") from error
            except ValueError as error:
                raise ValueError(f"KESALAHAN NILAI PADA FUNGSI '{func_name.upper()}': {str(error).upper()}.") from error

            return res

        raise ValueError(f"ELEMEN SINTAKS {type(node).__name__.upper()} TIDAK DIIZINKAN.")

    def _format_result(self, value: float | int) -> str:
        if isinstance(value, int):
            return str(value)
        # Format float cleanly without excessive floating point noise
        s = f"{value:.8f}".rstrip("0").rstrip(".")
        return s

    def _format_fraction(self, value: float | int) -> str:
        if isinstance(value, int):
            return str(value)

        try:
            frac = fractions.Fraction(value).limit_denominator(100000)
        except (ValueError, OverflowError):
            return "-"

        if frac.denominator == 1:
            return str(frac.numerator)

        numerator = frac.numerator
        denominator = frac.denominator
        whole = abs(numerator) // denominator
        rem = abs(numerator) % denominator
        sign = "-" if numerator < 0 else ""

        if whole > 0:
            return f"{numerator}/{denominator}  [{sign}{whole} {rem}/{denominator}]"
        return f"{numerator}/{denominator}"
