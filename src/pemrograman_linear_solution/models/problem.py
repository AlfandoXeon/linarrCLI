from dataclasses import dataclass
from enum import Enum
import math


class ObjectiveDirection(str, Enum):
    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"


class VariableDomain(str, Enum):
    NON_NEGATIVE = "NON_NEGATIVE"
    UNRESTRICTED = "UNRESTRICTED"


class Relation(str, Enum):
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    EQUAL = "="


@dataclass(frozen=True)
class Variable:
    name: str
    domain: VariableDomain = VariableDomain.NON_NEGATIVE


@dataclass(frozen=True)
class Constraint:
    coefficients: tuple[float, ...]
    relation: Relation
    rhs: float


@dataclass(frozen=True)
class LinearProgram:
    variables: tuple[Variable, ...]
    objective: tuple[float, ...]
    direction: ObjectiveDirection
    constraints: tuple[Constraint, ...]

    def validate(self) -> None:
        variable_count = len(self.variables)
        if not 1 <= variable_count <= 20:
            raise ValueError("A MODEL MUST HAVE BETWEEN 1 AND 20 VARIABLES.")
        if len(self.objective) != variable_count:
            raise ValueError("THE OBJECTIVE MUST HAVE ONE COEFFICIENT PER VARIABLE.")
        if not 1 <= len(self.constraints) <= 50:
            raise ValueError("A MODEL MUST HAVE BETWEEN 1 AND 50 CONSTRAINTS.")
        names = [variable.name for variable in self.variables]
        folded_names = {name.casefold() for name in names}
        if any(not name.strip() for name in names) or len(folded_names) != len(names):
            raise ValueError("VARIABLE NAMES MUST BE NON-EMPTY AND UNIQUE.")
        values = list(self.objective)
        for constraint in self.constraints:
            if len(constraint.coefficients) != variable_count:
                raise ValueError("EACH CONSTRAINT MUST HAVE ONE COEFFICIENT PER VARIABLE.")
            values.extend(constraint.coefficients)
            values.append(constraint.rhs)
        if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in values):
            raise ValueError("ALL COEFFICIENTS AND RIGHT-HAND SIDES MUST BE FINITE NUMBERS.")
