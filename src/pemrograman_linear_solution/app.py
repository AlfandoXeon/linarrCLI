from rich.prompt import Prompt

from pemrograman_linear_solution.controllers.problem_controller import ProblemController
from pemrograman_linear_solution.views.console import ConsoleView


class Application:
    def __init__(self, view: ConsoleView | None = None) -> None:
        self.view = view or ConsoleView()
        self.problem_controller = ProblemController(self.view)

    def run(self) -> None:
        while True:
            self.view.begin_screen("MAIN MENU", "A PRACTICAL LINEAR PROGRAMMING SOLVER")
            self.view.message("1. CREATE AND SOLVE A LINEAR PROGRAM", "bright_white")
            self.view.message("0. EXIT", "bright_white")
            self.view.footer("SELECT AN OPTION")
            choice = Prompt.ask("OPTION", choices=("1", "0"), console=self.view.console)
            if choice == "0":
                self.view.begin_screen("GOODBYE", "THANK YOU FOR USING THE APPLICATION")
                self.view.footer()
                return
            self.problem_controller.create_and_solve()


def main() -> None:
    app = Application()
    try:
        app.run()
    except (EOFError, KeyboardInterrupt):
        app.view.console.print("\n[DIM]SESSION ENDED.[/DIM]")
