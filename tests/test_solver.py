import unittest

from pemrograman_linear_solution.models.problem import (
    Constraint,
    LinearProgram,
    ObjectiveDirection,
    Relation,
    Variable,
    VariableDomain,
)
from pemrograman_linear_solution.models.result import SolveStatus
from pemrograman_linear_solution.services.simplex import TwoPhaseSimplex


class TwoPhaseSimplexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.solver = TwoPhaseSimplex()

    def solve(
        self,
        objective: tuple[float, ...],
        constraints: tuple[Constraint, ...],
        direction: ObjectiveDirection = ObjectiveDirection.MAXIMIZE,
        domains: tuple[VariableDomain, ...] | None = None,
    ):
        if domains is None:
            domains = (VariableDomain.NON_NEGATIVE,) * len(objective)
        variables = tuple(Variable(f"x{index + 1}", domain) for index, domain in enumerate(domains))
        return self.solver.solve(LinearProgram(variables, objective, direction, constraints))

    def test_maximization_with_less_equal_constraints(self) -> None:
        result = self.solve(
            (3, 2),
            (
                Constraint((1, 1), Relation.LESS_EQUAL, 4),
                Constraint((1, 0), Relation.LESS_EQUAL, 2),
                Constraint((0, 1), Relation.LESS_EQUAL, 3),
            ),
        )
        self.assertEqual(result.status, SolveStatus.OPTIMAL)
        self.assertAlmostEqual(result.objective_value, 10)
        self.assertAlmostEqual(result.variable_values[0], 2)
        self.assertAlmostEqual(result.variable_values[1], 2)
        self.assertTrue(result.steps)
        self.assertTrue(all(step.phase == "PHASE II" for step in result.steps))

    def test_greater_equal_and_equality_constraints(self) -> None:
        result = self.solve(
            (1, 1),
            (
                Constraint((1, 1), Relation.GREATER_EQUAL, 4),
                Constraint((1, 0), Relation.EQUAL, 2),
                Constraint((0, 1), Relation.LESS_EQUAL, 3),
            ),
            ObjectiveDirection.MINIMIZE,
        )
        self.assertEqual(result.status, SolveStatus.OPTIMAL)
        self.assertAlmostEqual(result.objective_value, 4)
        self.assertAlmostEqual(result.variable_values[0], 2)
        self.assertAlmostEqual(result.variable_values[1], 2)

    def test_minimization_with_lower_bound(self) -> None:
        result = self.solve(
            (1, 1),
            (
                Constraint((1, 1), Relation.GREATER_EQUAL, 4),
                Constraint((1, 0), Relation.LESS_EQUAL, 3),
                Constraint((0, 1), Relation.LESS_EQUAL, 3),
            ),
            ObjectiveDirection.MINIMIZE,
        )
        self.assertEqual(result.status, SolveStatus.OPTIMAL)
        self.assertAlmostEqual(result.objective_value, 4)
        self.assertAlmostEqual(sum(result.variable_values), 4)

    def test_infeasible_model(self) -> None:
        result = self.solve(
            (1,),
            (
                Constraint((1,), Relation.GREATER_EQUAL, 2),
                Constraint((1,), Relation.LESS_EQUAL, 1),
            ),
        )
        self.assertEqual(result.status, SolveStatus.INFEASIBLE)

    def test_unbounded_model(self) -> None:
        result = self.solve((1,), (Constraint((1,), Relation.GREATER_EQUAL, 1),))
        self.assertEqual(result.status, SolveStatus.UNBOUNDED)

    def test_iteration_limit_is_reported(self) -> None:
        solver = TwoPhaseSimplex(iteration_limit=1)
        problem = LinearProgram(
            (Variable("x"), Variable("y")),
            (3, 2),
            ObjectiveDirection.MAXIMIZE,
            (
                Constraint((1, 1), Relation.LESS_EQUAL, 4),
                Constraint((1, 0), Relation.LESS_EQUAL, 2),
                Constraint((0, 1), Relation.LESS_EQUAL, 3),
            ),
        )
        result = solver.solve(problem)
        self.assertEqual(result.status, SolveStatus.ITERATION_LIMIT)
        self.assertEqual(result.pivot_count, 1)

    def test_unrestricted_variable(self) -> None:
        result = self.solve(
            (1,),
            (Constraint((1,), Relation.EQUAL, -3),),
            domains=(VariableDomain.UNRESTRICTED,),
        )
        self.assertEqual(result.status, SolveStatus.OPTIMAL)
        self.assertAlmostEqual(result.objective_value, -3)
        self.assertAlmostEqual(result.variable_values[0], -3)

    def test_negative_rhs_is_normalized(self) -> None:
        result = self.solve(
            (1,),
            (
                Constraint((-1,), Relation.LESS_EQUAL, -2),
                Constraint((1,), Relation.LESS_EQUAL, 5),
            ),
        )
        self.assertEqual(result.status, SolveStatus.OPTIMAL)
        self.assertAlmostEqual(result.variable_values[0], 5)

    def test_model_rejects_non_finite_values(self) -> None:
        with self.assertRaises(ValueError):
            self.solve((float("inf"),), (Constraint((1,), Relation.LESS_EQUAL, 1),))

    def test_overflow_is_reported_as_numerical_failure(self) -> None:
        result = self.solve(
            (1e308,),
            (Constraint((1,), Relation.LESS_EQUAL, 2),),
        )
        self.assertEqual(result.status, SolveStatus.NUMERICAL_FAILURE)


if __name__ == "__main__":
    unittest.main()
