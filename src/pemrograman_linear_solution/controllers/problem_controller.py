from rich.table import Table
from rich.prompt import Prompt

from pemrograman_linear_solution.models.problem import LinearProgram, Relation
from pemrograman_linear_solution.models.result import PivotStep, SolveStatus
from pemrograman_linear_solution.services.solver import SolverService
from pemrograman_linear_solution.views.console import ConsoleView
from pemrograman_linear_solution.views.prompts import ProblemPrompts


class ProblemController:
    def __init__(self, view: ConsoleView, solver: SolverService | None = None) -> None:
        self.view = view
        self.prompts = ProblemPrompts(view)
        self.solver = solver or SolverService()

    def create_and_solve(self) -> None:
        while True:
            problem = self.prompts.create_problem()
            self.view.begin_screen("REVIEW MODEL", "CHECK THE MODEL BEFORE SOLVING")
            direction = problem.direction.value
            expression = " + ".join(
                f"{coefficient:g}*{variable.name}"
                for variable, coefficient in zip(problem.variables, problem.objective)
            )
            self.view.message(f"{direction} Z = {expression}", "bright_cyan")
            self.prompts.show_problem(problem)
            self.view.footer("1=SOLVE  |  2=RE-ENTER MODEL  |  0=MAIN MENU")
            choice = self._choice("SELECT AN ACTION", ("1", "2", "0"))
            if choice == "0":
                return
            if choice == "2":
                continue
            result = self.solver.solve(problem)
            self._show_result(
                problem,
                result.status,
                result.objective_value,
                result.variable_values,
                result.pivot_count,
                result.message,
                result.steps,
            )
            self.view.footer("PRESS ENTER TO RETURN TO MAIN MENU")
            Prompt.ask("PRESS ENTER TO CONTINUE", default="", show_default=False, console=self.view.console)
            return

    def _choice(self, prompt: str, choices: tuple[str, ...]) -> str:
        return Prompt.ask(prompt, choices=choices, console=self.view.console)

    def _show_result(
        self,
        problem: LinearProgram,
        status: SolveStatus,
        objective_value: float | None,
        variable_values: tuple[float, ...],
        pivot_count: int,
        message: str,
        steps: tuple[PivotStep, ...],
    ) -> None:
        self.view.begin_screen("SOLUTION RESULT", status.value)
        color = "green" if status is SolveStatus.OPTIMAL else "yellow"
        self.view.message(message, color)
        if status is SolveStatus.OPTIMAL and objective_value is not None:
            self.view.message(f"OPTIMAL OBJECTIVE VALUE: {objective_value:.10g}", "bright_cyan")
            table = Table(title="DECISION VARIABLES", expand=True)
            table.add_column("VARIABLE")
            table.add_column("VALUE", justify="right")
            for variable, value in zip(problem.variables, variable_values):
                table.add_row(variable.name, f"{value:.10g}")
            self.view.console.print(table)
            constraint_table = Table(title="CONSTRAINT CHECK", expand=True)
            constraint_table.add_column("CONSTRAINT")
            constraint_table.add_column("LHS", justify="right")
            constraint_table.add_column("RELATION", justify="center")
            constraint_table.add_column("RHS", justify="right")
            constraint_table.add_column("SLACK / SURPLUS", justify="right")
            for index, constraint in enumerate(problem.constraints, start=1):
                lhs = sum(
                    coefficient * value
                    for coefficient, value in zip(constraint.coefficients, variable_values)
                )
                if constraint.relation is Relation.LESS_EQUAL:
                    margin = constraint.rhs - lhs
                elif constraint.relation is Relation.GREATER_EQUAL:
                    margin = lhs - constraint.rhs
                else:
                    margin = abs(lhs - constraint.rhs)
                constraint_table.add_row(
                    f"C{index}",
                    f"{lhs:.10g}",
                    constraint.relation.value,
                    f"{constraint.rhs:.10g}",
                    f"{margin:.10g}",
                )
            self.view.console.print(constraint_table)
            self.view.message(f"SIMPLEX PIVOTS: {pivot_count}", "dim")
            self._show_pivot_steps(steps)

    def _show_pivot_steps(self, steps: tuple[PivotStep, ...]) -> None:
        table = Table(title="SIMPLEX PIVOT STEPS", expand=True)
        table.add_column("PHASE")
        table.add_column("ENTERING")
        table.add_column("LEAVING")
        table.add_column("PIVOT", justify="right")
        for step in steps[:50]:
            table.add_row(
                step.phase,
                step.entering_variable,
                step.leaving_variable,
                f"{step.pivot_value:.10g}",
            )
        self.view.console.print(table)
        if len(steps) > 50:
            self.view.message(f"SHOWING 50 OF {len(steps)} PIVOT STEPS.", "dim")
