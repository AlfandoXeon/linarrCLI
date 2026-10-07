from dataclasses import dataclass
import math

from pemrograman_linear_solution.models.problem import LinearProgram, Relation, VariableDomain
from pemrograman_linear_solution.models.result import PivotStep, SolveResult, SolveStatus

EPSILON = 1e-9
MAX_ITERATIONS = 10000


class _SimplexStop(Exception):
    def __init__(self, status: SolveStatus, message: str, pivot_count: int = 0) -> None:
        self.status = status
        self.message = message
        self.pivot_count = pivot_count


@dataclass
class _Tableau:
    rows: list[list[float]]
    basis: list[int]
    artificial: set[int]
    variable_map: list[tuple[int, float]]
    original_variable_count: int
    column_labels: list[str]
    steps: list[PivotStep]
    pivots: int = 0


class TwoPhaseSimplex:
    """Two-phase simplex solver using a maximization tableau convention."""

    def __init__(self, tolerance: float = EPSILON, iteration_limit: int = MAX_ITERATIONS) -> None:
        if not math.isfinite(tolerance) or tolerance <= 0:
            raise ValueError("THE NUMERICAL TOLERANCE MUST BE A POSITIVE FINITE NUMBER.")
        if iteration_limit < 1:
            raise ValueError("THE ITERATION LIMIT MUST BE AT LEAST ONE.")
        self.tolerance = tolerance
        self.iteration_limit = iteration_limit

    def solve(self, problem: LinearProgram) -> SolveResult:
        problem.validate()
        try:
            tableau, objective = self._build_tableau(problem)
            phase_one = [0.0] * len(objective)
            for artificial_column in tableau.artificial:
                phase_one[artificial_column] = -1.0
            self._set_objective(tableau, phase_one)
            self._run_simplex(tableau, "PHASE I")

            if tableau.rows[-1][-1] < -self.tolerance:
                return SolveResult(
                    SolveStatus.INFEASIBLE,
                    pivot_count=tableau.pivots,
                    message="PHASE ONE COULD NOT FIND A FEASIBLE SOLUTION.",
                )

            self._remove_artificial_variables(tableau)
            objective = objective[:len(tableau.rows[0]) - 1]
            self._set_objective(tableau, objective)
            self._run_simplex(tableau, "PHASE II")
            return self._make_result(problem, tableau)
        except _SimplexStop as stop:
            return SolveResult(stop.status, pivot_count=stop.pivot_count, message=stop.message)
        except (ArithmeticError, IndexError, ValueError) as error:
            return SolveResult(
                SolveStatus.NUMERICAL_FAILURE,
                message=f"THE SOLVER COULD NOT RELIABLY PROCESS THIS MODEL: {error}",
            )

    def _build_tableau(self, problem: LinearProgram) -> tuple[_Tableau, list[float]]:
        variable_map: list[tuple[int, float]] = []
        transformed_objective: list[float] = []
        column_labels: list[str] = []
        objective_sign = -1.0 if problem.direction.value == "MINIMIZE" else 1.0
        for index, variable in enumerate(problem.variables):
            transformed_objective.append(objective_sign * problem.objective[index])
            variable_map.append((index, 1.0))
            column_labels.append(variable.name if variable.domain is VariableDomain.NON_NEGATIVE else f"{variable.name} (+)")
            if variable.domain is VariableDomain.UNRESTRICTED:
                transformed_objective.append(-objective_sign * problem.objective[index])
                variable_map.append((index, -1.0))
                column_labels.append(f"{variable.name} (-)")

        transformed_rows: list[tuple[list[float], Relation, float]] = []
        for constraint in problem.constraints:
            coefficients: list[float] = []
            for index, variable in enumerate(problem.variables):
                coefficients.append(constraint.coefficients[index])
                if variable.domain is VariableDomain.UNRESTRICTED:
                    coefficients.append(-constraint.coefficients[index])
            relation = constraint.relation
            rhs = constraint.rhs
            if rhs < -self.tolerance:
                coefficients = [-value for value in coefficients]
                rhs = -rhs
                relation = {
                    Relation.LESS_EQUAL: Relation.GREATER_EQUAL,
                    Relation.GREATER_EQUAL: Relation.LESS_EQUAL,
                    Relation.EQUAL: Relation.EQUAL,
                }[relation]
            transformed_rows.append((coefficients, relation, rhs))

        decision_count = len(transformed_objective)
        slack_count = sum(relation is not Relation.EQUAL for _, relation, _ in transformed_rows)
        artificial_count = sum(relation is not Relation.LESS_EQUAL for _, relation, _ in transformed_rows)
        total_columns = decision_count + slack_count + artificial_count
        rows: list[list[float]] = []
        basis: list[int] = []
        artificial: set[int] = set()
        slack_labels: list[str] = []
        artificial_labels: list[str] = []
        next_slack = decision_count
        next_artificial = decision_count + slack_count

        for row_index, (coefficients, relation, rhs) in enumerate(transformed_rows, start=1):
            row = coefficients + [0.0] * (slack_count + artificial_count) + [rhs]
            if relation is Relation.LESS_EQUAL:
                row[next_slack] = 1.0
                basis.append(next_slack)
                slack_labels.append(f"SLACK C{row_index}")
                next_slack += 1
            elif relation is Relation.GREATER_EQUAL:
                row[next_slack] = -1.0
                slack_labels.append(f"SURPLUS C{row_index}")
                next_slack += 1
                row[next_artificial] = 1.0
                basis.append(next_artificial)
                artificial.add(next_artificial)
                artificial_labels.append(f"ARTIFICIAL C{row_index}")
                next_artificial += 1
            else:
                row[next_artificial] = 1.0
                basis.append(next_artificial)
                artificial.add(next_artificial)
                artificial_labels.append(f"ARTIFICIAL C{row_index}")
                next_artificial += 1
            if len(row) != total_columns + 1:
                raise ArithmeticError("INTERNAL TABLEAU DIMENSION MISMATCH.")
            rows.append(row)
        column_labels.extend(slack_labels)
        column_labels.extend(artificial_labels)
        rows.append([0.0] * (total_columns + 1))
        return (
            _Tableau(rows, basis, artificial, variable_map, len(problem.variables), column_labels, []),
            transformed_objective + [0.0] * (slack_count + artificial_count),
        )

    def _set_objective(self, tableau: _Tableau, coefficients: list[float]) -> None:
        objective_row = [-value for value in coefficients] + [0.0]
        for row_index, basic_column in enumerate(tableau.basis):
            basic_cost = coefficients[basic_column]
            if abs(basic_cost) > self.tolerance:
                objective_row = [
                    value + basic_cost * tableau.rows[row_index][column]
                    for column, value in enumerate(objective_row)
                ]
        tableau.rows[-1] = objective_row

    def _run_simplex(self, tableau: _Tableau, phase: str) -> None:
        while True:
            objective = tableau.rows[-1]
            entering = next(
                (column for column, value in enumerate(objective[:-1]) if value < -self.tolerance),
                None,
            )
            if entering is None:
                return

            candidates = [
                (row[-1] / row[entering], tableau.basis[index], index)
                for index, row in enumerate(tableau.rows[:-1])
                if row[entering] > self.tolerance and row[-1] >= -self.tolerance
            ]
            if not candidates:
                raise _SimplexStop(
                    SolveStatus.UNBOUNDED,
                    "THE OBJECTIVE CAN IMPROVE WITHOUT BOUND.",
                    tableau.pivots,
                )
            _, _, leaving_row = min(candidates)
            leaving_column = tableau.basis[leaving_row]
            tableau.steps.append(
                PivotStep(
                    phase,
                    tableau.column_labels[entering],
                    tableau.column_labels[leaving_column],
                    tableau.rows[leaving_row][entering],
                )
            )
            self._pivot(tableau, leaving_row, entering)
            tableau.pivots += 1
            if tableau.pivots >= self.iteration_limit:
                raise _SimplexStop(
                    SolveStatus.ITERATION_LIMIT,
                    "THE ITERATION LIMIT WAS REACHED.",
                    tableau.pivots,
                )

    def _pivot(self, tableau: _Tableau, pivot_row: int, pivot_column: int) -> None:
        pivot = tableau.rows[pivot_row][pivot_column]
        if abs(pivot) <= self.tolerance:
            raise ArithmeticError("A PIVOT WAS TOO CLOSE TO ZERO.")
        tableau.rows[pivot_row] = [value / pivot for value in tableau.rows[pivot_row]]
        for row_index, row in enumerate(tableau.rows):
            if row_index == pivot_row:
                continue
            factor = row[pivot_column]
            if abs(factor) > self.tolerance:
                tableau.rows[row_index] = [
                    value - factor * tableau.rows[pivot_row][column]
                    for column, value in enumerate(row)
                ]
        if any(not math.isfinite(value) for row in tableau.rows for value in row):
            raise ArithmeticError("NON-FINITE VALUES OCCURRED DURING A SIMPLEX PIVOT.")
        tableau.basis[pivot_row] = pivot_column

    def _remove_artificial_variables(self, tableau: _Tableau) -> None:
        redundant_rows: set[int] = set()
        for row_index, basic_column in enumerate(tuple(tableau.basis)):
            if basic_column not in tableau.artificial:
                continue
            row = tableau.rows[row_index]
            entering = next(
                (
                    column
                    for column in range(len(row) - 1)
                    if column not in tableau.artificial and abs(row[column]) > self.tolerance
                ),
                None,
            )
            if entering is None:
                if abs(row[-1]) > self.tolerance:
                    raise _SimplexStop(
                        SolveStatus.INFEASIBLE,
                        "AN ARTIFICIAL BASIC VARIABLE REMAINS POSITIVE.",
                        tableau.pivots,
                    )
                redundant_rows.add(row_index)
            else:
                self._pivot(tableau, row_index, entering)

        if redundant_rows:
            tableau.rows = [
                row for index, row in enumerate(tableau.rows[:-1]) if index not in redundant_rows
            ] + [tableau.rows[-1]]
            tableau.basis = [
                basic for index, basic in enumerate(tableau.basis) if index not in redundant_rows
            ]

        keep_columns = [
            column for column in range(len(tableau.rows[0]) - 1)
            if column not in tableau.artificial
        ]
        remap = {old: new for new, old in enumerate(keep_columns)}
        tableau.rows = [
            [row[column] for column in keep_columns] + [row[-1]]
            for row in tableau.rows
        ]
        tableau.basis = [remap[basic] for basic in tableau.basis]
        tableau.column_labels = [tableau.column_labels[column] for column in keep_columns]
        tableau.artificial.clear()

    def _make_result(self, problem: LinearProgram, tableau: _Tableau) -> SolveResult:
        transformed_values = [0.0] * len(tableau.rows[0][:-1])
        for row_index, basic_column in enumerate(tableau.basis):
            transformed_values[basic_column] = tableau.rows[row_index][-1]

        variable_values = [0.0] * tableau.original_variable_count
        for transformed_index, (original_index, sign) in enumerate(tableau.variable_map):
            variable_values[original_index] += sign * transformed_values[transformed_index]
        variable_values = [
            0.0 if abs(value) <= self.tolerance else value for value in variable_values
        ]
        objective_value = sum(
            coefficient * value
            for coefficient, value in zip(problem.objective, variable_values)
        )
        if not math.isfinite(objective_value) or any(
            not math.isfinite(value) for value in variable_values
        ):
            return SolveResult(
                SolveStatus.NUMERICAL_FAILURE,
                pivot_count=tableau.pivots,
                message="THE COMPUTED RESULT CONTAINS NON-FINITE VALUES.",
            )
        if not self._satisfies_problem(problem, variable_values):
            return SolveResult(
                SolveStatus.NUMERICAL_FAILURE,
                pivot_count=tableau.pivots,
                message="THE COMPUTED VALUES DO NOT SATISFY THE ORIGINAL MODEL WITHIN TOLERANCE.",
            )
        return SolveResult(
            SolveStatus.OPTIMAL,
            objective_value=objective_value,
            variable_values=tuple(variable_values),
            pivot_count=tableau.pivots,
            message="AN OPTIMAL SOLUTION WAS FOUND.",
            steps=tuple(tableau.steps),
        )

    def _satisfies_problem(self, problem: LinearProgram, values: list[float]) -> bool:
        for variable, value in zip(problem.variables, values):
            if variable.domain is VariableDomain.NON_NEGATIVE and value < -self.tolerance * 10:
                return False
        for constraint in problem.constraints:
            lhs = sum(coefficient * value for coefficient, value in zip(constraint.coefficients, values))
            if constraint.relation is Relation.LESS_EQUAL and lhs > constraint.rhs + self.tolerance * 10:
                return False
            if constraint.relation is Relation.GREATER_EQUAL and lhs < constraint.rhs - self.tolerance * 10:
                return False
            if constraint.relation is Relation.EQUAL and abs(lhs - constraint.rhs) > self.tolerance * 10:
                return False
        return True
