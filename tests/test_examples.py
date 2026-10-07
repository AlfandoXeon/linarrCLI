import unittest

from pemrograman_linear_solution.models.result import SolveStatus
from pemrograman_linear_solution.services.examples import get_example_cases
from pemrograman_linear_solution.services.simplex import TwoPhaseSimplex


class ExampleCasesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.solver = TwoPhaseSimplex()

    def test_all_examples_load_and_solve_properly(self) -> None:
        cases = {case.case_id: case for case in get_example_cases()}
        self.assertEqual(len(cases), 5)

        # Case 1: Furniture Mix
        res1 = self.solver.solve(cases["1"].problem)
        self.assertEqual(res1.status, SolveStatus.OPTIMAL)
        self.assertAlmostEqual(res1.objective_value, 16000.0)
        self.assertAlmostEqual(res1.variable_values[0], 40.0)
        self.assertAlmostEqual(res1.variable_values[1], 20.0)

        # Case 2: Diet Problem
        res2 = self.solver.solve(cases["2"].problem)
        self.assertEqual(res2.status, SolveStatus.OPTIMAL)
        self.assertIsNotNone(res2.objective_value)

        # Case 3: Chemical Blending
        res3 = self.solver.solve(cases["3"].problem)
        self.assertEqual(res3.status, SolveStatus.OPTIMAL)
        self.assertAlmostEqual(sum(res3.variable_values), 100.0)

        # Case 4: Infeasible
        res4 = self.solver.solve(cases["4"].problem)
        self.assertEqual(res4.status, SolveStatus.INFEASIBLE)

        # Case 5: Unbounded
        res5 = self.solver.solve(cases["5"].problem)
        self.assertEqual(res5.status, SolveStatus.UNBOUNDED)


if __name__ == "__main__":
    unittest.main()
