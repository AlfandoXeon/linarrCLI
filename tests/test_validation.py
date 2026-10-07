import unittest

from pemrograman_linear_solution.validation.inputs import (
    parse_count,
    parse_finite_number,
    parse_unique_name,
)


class InputValidationTests(unittest.TestCase):
    def test_count_limits(self) -> None:
        self.assertEqual(parse_count("2", "VARIABLES", 20), 2)
        with self.assertRaises(ValueError):
            parse_count("0", "VARIABLES", 20)

    def test_finite_number(self) -> None:
        self.assertEqual(parse_finite_number("-2.5"), -2.5)
        with self.assertRaises(ValueError):
            parse_finite_number("nan")

    def test_unique_names(self) -> None:
        self.assertEqual(parse_unique_name("x", set()), "x")
        with self.assertRaises(ValueError):
            parse_unique_name("x", {"x"})
        with self.assertRaises(ValueError):
            parse_unique_name("X", {"x"})


if __name__ == "__main__":
    unittest.main()
