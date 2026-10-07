from rich.prompt import Prompt
from rich.table import Table

from pemrograman_linear_solution.models.problem import (
    Constraint,
    LinearProgram,
    ObjectiveDirection,
    Relation,
    Variable,
    VariableDomain,
)
from pemrograman_linear_solution.validation.inputs import (
    parse_count,
    parse_finite_number,
    parse_unique_name,
)
from pemrograman_linear_solution.views.console import ConsoleView


class ProblemPrompts:
    def __init__(self, view: ConsoleView) -> None:
        self.view = view

    def _read(self, prompt: str, choices: tuple[str, ...] | None = None) -> str:
        return Prompt.ask(prompt.upper(), choices=choices, console=self.view.console).strip()

    def _count(self, label: str, maximum: int) -> int:
        while True:
            raw = self._read(f"NUMBER OF {label} [1-{maximum}]")
            try:
                return parse_count(raw, label, maximum)
            except ValueError as error:
                self.view.message(str(error), "yellow")

    def _number(self, prompt: str) -> float:
        while True:
            raw = self._read(prompt)
            try:
                return parse_finite_number(raw)
            except ValueError as error:
                self.view.message(str(error), "yellow")

    def create_problem(self) -> LinearProgram:
        self.view.begin_screen("CREATE A LINEAR PROGRAM", "ENTER YOUR MODEL DATA")
        self.view.footer("ENTER ALL MODEL VALUES  |  INVALID INPUTS CAN BE CORRECTED")
        variable_count = self._count("VARIABLES", 20)
        variables: list[Variable] = []
        names: set[str] = set()
        for index in range(variable_count):
            while True:
                raw_name = self._read(f"NAME OF VARIABLE X{index + 1}")
                try:
                    name = parse_unique_name(raw_name, names)
                    break
                except ValueError as error:
                    self.view.message(str(error), "yellow")
            names.add(name)
            domain_choice = self._read(
                f"DOMAIN FOR {name} (1=NON-NEGATIVE, 2=UNRESTRICTED)",
                choices=("1", "2"),
            )
            domain = VariableDomain.NON_NEGATIVE if domain_choice == "1" else VariableDomain.UNRESTRICTED
            variables.append(Variable(name, domain))

        direction_choice = self._read("OBJECTIVE (1=MAXIMIZE, 2=MINIMIZE)", choices=("1", "2"))
        direction = ObjectiveDirection.MAXIMIZE if direction_choice == "1" else ObjectiveDirection.MINIMIZE
        variable_sequence = tuple(variables)
        self.view.message("ENTER THE OBJECTIVE COEFFICIENTS.", "cyan")
        objective = tuple(
            self._number(f"COEFFICIENT FOR {variable.name}")
            for variable in variable_sequence
        )

        constraint_count = self._count("CONSTRAINTS", 50)
        constraints: list[Constraint] = []
        for constraint_index in range(constraint_count):
            self.view.message(f"CONSTRAINT {constraint_index + 1} OF {constraint_count}", "cyan")
            coefficients = tuple(
                self._number(f"COEFFICIENT OF {variable.name}")
                for variable in variable_sequence
            )
            relation = self._read("RELATION (<=, >=, =)", choices=("<=", ">=", "="))
            rhs = self._number("RIGHT-HAND SIDE")
            constraints.append(Constraint(coefficients, Relation(relation), rhs))

        return LinearProgram(variable_sequence, objective, direction, tuple(constraints))

    def show_problem(self, problem: LinearProgram) -> None:
        table = Table(title="MODEL REVIEW", expand=True)
        table.add_column("VARIABLE")
        table.add_column("OBJECTIVE COEFFICIENT", justify="right")
        table.add_column("DOMAIN")
        for variable, coefficient in zip(problem.variables, problem.objective):
            table.add_row(variable.name, f"{coefficient:g}", variable.domain.value.replace("_", " "))
        self.view.console.print(table)

        constraints = Table(title="CONSTRAINTS", expand=True)
        for variable in problem.variables:
            constraints.add_column(variable.name, justify="right")
        constraints.add_column("RELATION", justify="center")
        constraints.add_column("RHS", justify="right")
        for constraint in problem.constraints:
            constraints.add_row(
                *(f"{value:g}" for value in constraint.coefficients),
                constraint.relation.value,
                f"{constraint.rhs:g}",
            )
        self.view.console.print(constraints)
