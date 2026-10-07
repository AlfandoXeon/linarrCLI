from dataclasses import dataclass
from enum import Enum


class SolveStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    INFEASIBLE = "INFEASIBLE"
    UNBOUNDED = "UNBOUNDED"
    ITERATION_LIMIT = "ITERATION LIMIT"
    NUMERICAL_FAILURE = "NUMERICAL FAILURE"


@dataclass(frozen=True)
class PivotStep:
    phase: str
    entering_variable: str
    leaving_variable: str
    pivot_value: float


@dataclass(frozen=True)
class SolveResult:
    status: SolveStatus
    objective_value: float | None = None
    variable_values: tuple[float, ...] = ()
    pivot_count: int = 0
    message: str = ""
    steps: tuple[PivotStep, ...] = ()
