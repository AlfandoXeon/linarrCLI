from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

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
            raw = self._read(f"JUMLAH {label} [1-{maximum}]")
            try:
                return parse_count(raw, label, maximum)
            except ValueError as error:
                self.view.alert("warning", "INPUT TIDAK VALID", str(error))

    def _number(self, prompt: str) -> float:
        while True:
            raw = self._read(prompt)
            try:
                return parse_finite_number(raw)
            except ValueError as error:
                self.view.alert("warning", "ANGKA TIDAK VALID", str(error))

    def create_problem(self) -> LinearProgram:
        self.view.begin_screen(
            "BUAT MODEL PEMROGRAMAN LINEAR",
            "TAHAP 1: PENDEFINISIAN VARIABEL KEPUTUSAN",
            active_tab="BUILDER",
            breadcrumb="WIZARD (1/3)",
        )

        step1_banner = Panel(
            Text.from_markup(
                "[bold cyan]TAHAP 1 / 3:[/bold cyan] [bold white]PENDEFINISIAN VARIABEL KEPUTUSAN[/bold white]\n"
                "[dim]Tentukan jumlah variabel (maks 20), nama pengenal, dan domain non-negativitas.[/dim]"
            ),
            box=box.ROUNDED,
            border_style="cyan",
        )
        self.view.console.print(step1_banner)

        variable_count = self._count("VARIABEL", 20)
        variables: list[Variable] = []
        names: set[str] = set()

        self.view.message("\nMASUKKAN IDENTITAS TIAP VARIABEL KEPUTUSAN:", "bold bright_yellow")
        for index in range(variable_count):
            default_name = f"x{index + 1}"
            while True:
                prompt_str = f"NAMA VARIABEL KE-{index + 1} (KOSONGKAN UNTUK DEFAULT '{default_name}')"
                raw_name = self._read(prompt_str)
                if not raw_name:
                    raw_name = default_name
                try:
                    name = parse_unique_name(raw_name, names)
                    break
                except ValueError as error:
                    self.view.alert("warning", "NAMA TIDAK VALID", str(error))
            names.add(name)

            self.view.console.print(
                f"[dim]PILIHAN DOMAIN UNTUK [bold cyan]{name}[/bold cyan]: 1=Non-Negatif (x >= 0, Umum), 2=Bebas/Unrestricted[/dim]"
            )
            domain_choice = self._read(
                f"DOMAIN NILAI {name} (1=NON-NEGATIF [>= 0], 2=BEBAS/UNRESTRICTED)",
                choices=("1", "2"),
            )
            domain = VariableDomain.NON_NEGATIVE if domain_choice == "1" else VariableDomain.UNRESTRICTED
            variables.append(Variable(name, domain))

        variable_sequence = tuple(variables)

        # Tahap 2: Fungsi Tujuan
        self.view.begin_screen(
            "BUAT MODEL PEMROGRAMAN LINEAR",
            "TAHAP 2: FUNGSI TUJUAN (OBJECTIVE FUNCTION - Z)",
            active_tab="BUILDER",
            breadcrumb="WIZARD (2/3)",
        )
        step2_banner = Panel(
            Text.from_markup(
                "[bold gold1]TAHAP 2 / 3:[/bold gold1] [bold white]FUNGSI TUJUAN (OBJECTIVE FUNCTION - Z)[/bold white]\n"
                "[dim]Tentukan arah optimasi (Maksimasi keuntungan / Minimasi biaya) serta koefisiennya.[/dim]"
            ),
            box=box.ROUNDED,
            border_style="gold1",
        )
        self.view.console.print(step2_banner)

        direction_choice = self._read("ARAH OPTIMASI (1=MAKSIMALKAN [MAX], 2=MINIMALKAN [MIN])", choices=("1", "2"))
        direction = ObjectiveDirection.MAXIMIZE if direction_choice == "1" else ObjectiveDirection.MINIMIZE

        self.view.message("MASUKKAN KOEFISIEN FUNGSI TUJUAN UNTUK MASING-MASING VARIABEL:", "bold bright_cyan")
        objective_list = []
        for variable in variable_sequence:
            coef = self._number(f"KOEFISIEN UNTUK {variable.name}")
            objective_list.append(coef)
        objective = tuple(objective_list)

        # Tahap 3: Kendala
        self.view.begin_screen(
            "BUAT MODEL PEMROGRAMAN LINEAR",
            "TAHAP 3: SISTEM KENDALA (CONSTRAINTS)",
            active_tab="BUILDER",
            breadcrumb="WIZARD (3/3)",
        )
        step3_banner = Panel(
            Text.from_markup(
                "[bold bright_magenta]TAHAP 3 / 3:[/bold bright_magenta] [bold white]SISTEM KENDALA (CONSTRAINTS)[/bold white]\n"
                "[dim]Tentukan batas-batas alokasi sumber daya, operator (<=, >=, =), dan kapasitas ruas kanan (RHS).[/dim]"
            ),
            box=box.ROUNDED,
            border_style="bright_magenta",
        )
        self.view.console.print(step3_banner)

        constraint_count = self._count("KENDALA", 50)
        constraints: list[Constraint] = []

        for constraint_index in range(constraint_count):
            self.view.console.print()
            self.view.console.rule(
                f"[bold bright_yellow]KENDALA KE-{constraint_index + 1} DARI {constraint_count}[/bold bright_yellow]"
            )
            coefficients = tuple(
                self._number(f"KOEFISIEN {variable.name} PADA KENDALA {constraint_index + 1}")
                for variable in variable_sequence
            )
            relation = self._read(
                f"RELASI OPERATOR KENDALA {constraint_index + 1} (<=, >=, =)",
                choices=("<=", ">=", "="),
            )
            rhs = self._number(f"KAPASITAS RUAS KANAN (RHS) KENDALA {constraint_index + 1}")
            constraints.append(Constraint(coefficients, Relation(relation), rhs))

        return LinearProgram(variable_sequence, objective, direction, tuple(constraints))

    def show_problem(self, problem: LinearProgram) -> None:
        equation_text = self._format_algebraic_representation(problem)
        equation_panel = Panel(
            equation_text,
            title="[bold gold1]NOTASI MATEMATIS PERSAMAAN LENGKAP[/bold gold1]",
            box=box.ROUNDED,
            border_style="gold1",
            padding=(1, 2),
        )
        self.view.console.print(equation_panel)

        table = Table(
            title="TABEL VARIABEL & KOEFISIEN OBJEKTIF",
            box=box.ROUNDED,
            border_style="bright_cyan",
            expand=True,
            header_style="bold bright_cyan",
        )
        table.add_column("VARIABEL", style="bold white")
        table.add_column("KOEFISIEN FUNGSI TUJUAN", justify="right", style="bold bright_green")
        table.add_column("BATASAN DOMAIN NILAI", justify="center", style="italic")

        for variable, coefficient in zip(problem.variables, problem.objective):
            domain_label = "x >= 0 (Non-Negatif)" if variable.domain == VariableDomain.NON_NEGATIVE else "Bebas (Unrestricted)"
            table.add_row(variable.name, f"{coefficient:g}", domain_label)
        self.view.console.print(table)

        constraints_table = Table(
            title="TABEL KENDALA SISTEM (CONSTRAINTS MATRIX)",
            box=box.ROUNDED,
            border_style="bright_magenta",
            expand=True,
            header_style="bold bright_magenta",
        )
        constraints_table.add_column("KENDALA", style="bold gold1", justify="center", width=8)
        for variable in problem.variables:
            constraints_table.add_column(f"KOEF {variable.name}", justify="right")
        constraints_table.add_column("RELASI", justify="center", style="bold bright_yellow")
        constraints_table.add_column("KAPASITAS (RHS)", justify="right", style="bold bright_white")

        for index, constraint in enumerate(problem.constraints, start=1):
            constraints_table.add_row(
                f"C{index}",
                *(f"{value:g}" for value in constraint.coefficients),
                constraint.relation.value,
                f"{constraint.rhs:g}",
            )
        self.view.console.print(constraints_table)

    def _format_algebraic_representation(self, problem: LinearProgram) -> Text:
        text = Text()
        dir_label = "MAKSIMALKAN (MAXIMIZE)" if problem.direction == ObjectiveDirection.MAXIMIZE else "MINIMALKAN (MINIMIZE)"
        text.append(f"{dir_label} FUNGSI TUJUAN:\n", style="bold bright_yellow")

        obj_terms = []
        for variable, coef in zip(problem.variables, problem.objective):
            if coef >= 0 and obj_terms:
                obj_terms.append(f"+ {coef:g} {variable.name}")
            elif coef < 0 and obj_terms:
                obj_terms.append(f"- {abs(coef):g} {variable.name}")
            else:
                obj_terms.append(f"{coef:g} {variable.name}")

        text.append(f"   Z = {' '.join(obj_terms)}\n\n", style="bold bright_green")
        text.append("DENGAN MEMENUHI KENDALA-KENDALA:\n", style="bold bright_cyan")

        for index, constraint in enumerate(problem.constraints, start=1):
            terms = []
            for variable, coef in zip(problem.variables, constraint.coefficients):
                if coef >= 0 and terms:
                    terms.append(f"+ {coef:g} {variable.name}")
                elif coef < 0 and terms:
                    terms.append(f"- {abs(coef):g} {variable.name}")
                else:
                    terms.append(f"{coef:g} {variable.name}")
            lhs_str = " ".join(terms) if terms else "0"
            text.append(f"   [C{index}]  {lhs_str}  {constraint.relation.value}  {constraint.rhs:g}\n", style="white")

        non_negative_vars = [v.name for v in problem.variables if v.domain == VariableDomain.NON_NEGATIVE]
        unrestricted_vars = [v.name for v in problem.variables if v.domain == VariableDomain.UNRESTRICTED]

        text.append("\nBATASAN DOMAIN VARIABEL:\n", style="bold gold1")
        if non_negative_vars:
            text.append(f"   {', '.join(non_negative_vars)} >= 0 (Non-Negatif)\n", style="italic white")
        if unrestricted_vars:
            text.append(f"   {', '.join(unrestricted_vars)} adalah Unrestricted (Bebas)\n", style="italic yellow")

        return text
