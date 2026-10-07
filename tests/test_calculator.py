import math
import unittest

from pemrograman_linear_solution.services.calculator import CalculatorService


class CalculatorServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.calc = CalculatorService()

    def test_basic_arithmetic(self) -> None:
        self.assertEqual(self.calc.evaluate("10 + 5").result, 15)
        self.assertEqual(self.calc.evaluate("20 - 8").result, 12)
        self.assertEqual(self.calc.evaluate("6 * 7").result, 42)
        self.assertEqual(self.calc.evaluate("15 / 3").result, 5)
        self.assertEqual(self.calc.evaluate("17 // 5").result, 3)
        self.assertEqual(self.calc.evaluate("17 % 5").result, 2)
        self.assertEqual(self.calc.evaluate("2 ** 4").result, 16)
        self.assertEqual(self.calc.evaluate("2 ^ 3").result, 8)

    def test_division_and_colon(self) -> None:
        item = self.calc.evaluate("12 : 4")
        self.assertEqual(item.result, 3)

    def test_multiplication_x(self) -> None:
        item = self.calc.evaluate("7 x 8")
        self.assertEqual(item.result, 56)

    def test_fractions_and_mixed_representation(self) -> None:
        item = self.calc.evaluate("7 / 2")
        self.assertEqual(item.result, 3.5)
        self.assertIn("7/2", item.fraction_str)
        self.assertIn("3 1/2", item.fraction_str)

        neg_item = self.calc.evaluate("-7 / 3")
        self.assertIn("-7/3", neg_item.fraction_str)
        self.assertIn("-2 1/3", neg_item.fraction_str)

        proper_item = self.calc.evaluate("3 / 4")
        self.assertEqual(proper_item.fraction_str, "3/4")

    def test_math_functions(self) -> None:
        self.assertEqual(self.calc.evaluate("sqrt(144)").result, 12)
        self.assertEqual(self.calc.evaluate("cbrt(27)").result, 3)
        self.assertEqual(self.calc.evaluate("abs(-45)").result, 45)
        self.assertEqual(self.calc.evaluate("round(3.14159, 2)").result, 3.14)
        self.assertEqual(self.calc.evaluate("ceil(4.2)").result, 5)
        self.assertEqual(self.calc.evaluate("floor(4.9)").result, 4)
        self.assertEqual(self.calc.evaluate("factorial(5)").result, 120)
        self.assertEqual(self.calc.evaluate("gcd(24, 36)").result, 12)
        self.assertEqual(self.calc.evaluate("min(10, 5, 20)").result, 5)
        self.assertEqual(self.calc.evaluate("max(10, 5, 20)").result, 20)

    def test_constants_and_case_insensitivity(self) -> None:
        item_pi = self.calc.evaluate("PI * 2")
        self.assertAlmostEqual(item_pi.result, math.pi * 2)

        item_e = self.calc.evaluate("e + 1")
        self.assertAlmostEqual(item_e.result, math.e + 1)

        item_sqrt_case = self.calc.evaluate("SQRT(25)")
        self.assertEqual(item_sqrt_case.result, 5)

    def test_ans_memory_chaining(self) -> None:
        self.calc.evaluate("25 * 4")  # 100
        self.assertEqual(self.calc.last_ans, 100)

        step2 = self.calc.evaluate("ans + 50")
        self.assertEqual(step2.result, 150)

        step3 = self.calc.evaluate("ANS / 3")
        self.assertEqual(step3.result, 50)

    def test_history_and_clear(self) -> None:
        self.calc.evaluate("1 + 1")
        self.calc.evaluate("2 + 2")
        self.assertEqual(len(self.calc.get_history()), 2)

        self.calc.clear_history()
        self.assertEqual(len(self.calc.get_history()), 0)
        self.assertEqual(self.calc.last_ans, 0)

    def test_error_handling(self) -> None:
        with self.assertRaises(ValueError):
            self.calc.evaluate("")

        with self.assertRaises(ValueError):
            self.calc.evaluate("10 / 0")

        with self.assertRaises(ValueError):
            self.calc.evaluate("sqrt(-9)")

        with self.assertRaises(ValueError):
            self.calc.evaluate("log(0)")

        with self.assertRaises(ValueError):
            self.calc.evaluate("factorial(-1)")

        with self.assertRaises(ValueError):
            self.calc.evaluate("factorial(105)")

        with self.assertRaises(ValueError):
            self.calc.evaluate("unknown_func(10)")

        with self.assertRaises(ValueError):
            self.calc.evaluate("2 ** 999999")

        # Security checks
        with self.assertRaises(ValueError):
            self.calc.evaluate("__import__('os').system('dir')")

        with self.assertRaises(ValueError):
            self.calc.evaluate("[x for x in (1, 2)]")


class CalculatorControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        import io
        from rich.console import Console
        from pemrograman_linear_solution.controllers.calculator_controller import CalculatorController
        from pemrograman_linear_solution.views.console import ConsoleView

        self.output = io.StringIO()
        self.console = Console(file=self.output, force_terminal=True, color_system=None)
        self.view = ConsoleView(console=self.console)
        self.controller = CalculatorController(self.view)

    def test_controller_evaluates_and_exits(self) -> None:
        from unittest.mock import patch

        with patch("os.system"), patch("rich.prompt.Prompt.ask", side_effect=["10 + 5", "0"]):
            self.controller.run()

        history = self.controller.calculator.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].result, 15)

    def test_controller_reset_history(self) -> None:
        from unittest.mock import patch

        with patch("os.system"), patch("rich.prompt.Prompt.ask", side_effect=["20 * 2", "c", "0"]):
            self.controller.run()

        self.assertEqual(len(self.controller.calculator.get_history()), 0)

    def test_controller_help_and_no_emojis(self) -> None:
        from unittest.mock import patch

        with patch("os.system"), patch("rich.prompt.Prompt.ask", side_effect=["h", "", "0"]):
            self.controller.run()

        rendered = self.output.getvalue()
        self.assertIn("PANDUAN LENGKAP KALKULATOR", rendered)

        for ch in rendered:
            cp = ord(ch)
            self.assertFalse(0x1F000 <= cp <= 0x1FAFF, f"Found emoji: {ch} ({hex(cp)})")
            self.assertFalse(0x2600 <= cp <= 0x27BF, f"Found symbol: {ch} ({hex(cp)})")

    def test_application_navigates_to_calculator(self) -> None:
        from unittest.mock import patch
        from pemrograman_linear_solution.app import Application

        app = Application(view=self.view)
        # Choose 4 (Calculator), calculate 3 * 3, exit calculator (0), exit app (0)
        with patch("os.system"), patch("rich.prompt.Prompt.ask", side_effect=["4", "3 * 3", "0", "0"]):
            app.run()

        history = app.calculator_controller.calculator.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].result, 9)


if __name__ == "__main__":
    unittest.main()
