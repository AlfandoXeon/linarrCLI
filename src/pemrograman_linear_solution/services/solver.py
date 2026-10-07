from pemrograman_linear_solution.models.problem import LinearProgram
from pemrograman_linear_solution.models.result import SolveResult
from pemrograman_linear_solution.services.simplex import TwoPhaseSimplex


class SolverService:
    def __init__(self, solver: TwoPhaseSimplex | None = None) -> None:
        self._solver = solver or TwoPhaseSimplex()

    def solve(self, problem: LinearProgram) -> SolveResult:
        return self._solver.solve(problem)
