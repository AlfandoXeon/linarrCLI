from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from pemrograman_linear_solution.models.problem import LinearProgram, Relation, VariableDomain
from pemrograman_linear_solution.models.result import PivotStep, SolveResult, SolveStatus
from pemrograman_linear_solution.services.examples import ExampleCase, get_example_cases
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
            should_exit = self._review_and_solve_flow(problem)
            if should_exit:
                return

    def load_preset_case(self) -> None:
        cases = get_example_cases()
        while True:
            self.view.begin_screen(
                "PRESET PERPUSTAKAAN KASUS NYATA",
                "PILIH STUDI KASUS PRAKTIK UNTUK DISIMULASIKAN",
                active_tab="PRESETS",
                breadcrumb="PRESET",
            )

            table = Table(
                box=box.ROUNDED,
                border_style="bright_cyan",
                expand=True,
                header_style="bold bright_cyan",
            )
            table.add_column("NO", justify="center", style="bold gold1", width=5)
            table.add_column("JUDUL STUDI KASUS", style="bold white", ratio=2)
            table.add_column("KATEGORI", style="bold bright_yellow", ratio=1)
            table.add_column("RINGKASAN", style="dim white", ratio=3)

            for case in cases:
                table.add_row(
                    case.case_id,
                    case.title,
                    case.category,
                    case.notes,
                )
            table.add_row("0", "KEMBALI KE MENU UTAMA", "NAVIGASI", "Kembali ke menu utama")

            self.view.console.print(table)
            self.view.footer(hints=[("1-5", "PILIH KASUS"), ("0", "KEMBALI")], status="PILIH PRESET")

            valid_choices = ["0"] + [c.case_id for c in cases]
            choice = Prompt.ask("PILIH NOMOR STUDI KASUS [0-5]", choices=valid_choices, console=self.view.console)
            if choice == "0":
                return

            selected_case = next(c for c in cases if c.case_id == choice)
            self._display_case_detail(selected_case)

    def _display_case_detail(self, case: ExampleCase) -> None:
        self.view.begin_screen(case.title, case.category, active_tab="PRESETS", breadcrumb="DETAIL KASUS")

        story_panel = Panel(
            Text(case.story, style="white"),
            title="[bold bright_yellow]SKENARIO MASALAH (STORY BACKGROUND)[/bold bright_yellow]",
            border_style="bright_yellow",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        self.view.console.print(story_panel)
        self.view.console.print()

        self.prompts.show_problem(case.problem)
        self.view.footer(
            hints=[("1", "SELESAIKAN MODEL INI"), ("2", "PILIH KASUS LAIN"), ("0", "MENU UTAMA")],
            status="SIAP DIUJI",
        )

        action = Prompt.ask("PILIH TINDAKAN [1=SOLVE, 2=KASUS LAIN, 0=MENU]", choices=["1", "2", "0"], console=self.view.console)
        if action == "1":
            result = self.solver.solve(case.problem)
            self._handle_solution_dashboard(case.problem, result)
        elif action == "2":
            return
        elif action == "0":
            return

    def _review_and_solve_flow(self, problem: LinearProgram) -> bool:
        while True:
            self.view.begin_screen(
                "TINJAU & VERIFIKASI MODEL",
                "PERIKSA FORMULASI MODEL SEBELUM MENJALANKAN SOLVER",
                active_tab="BUILDER",
                breadcrumb="VERIFIKASI",
            )
            self.prompts.show_problem(problem)
            self.view.footer(
                hints=[("1", "SELESAIKAN (SOLVE)"), ("2", "INPUT ULANG MODEL"), ("0", "MENU UTAMA")],
                status="MENUNGGU KONFIRMASI",
            )

            choice = Prompt.ask("PILIH TINDAKAN", choices=("1", "2", "0"), console=self.view.console)
            if choice == "0":
                return True
            if choice == "2":
                return False

            result = self.solver.solve(problem)
            self._handle_solution_dashboard(problem, result)
            return True

    def _handle_solution_dashboard(self, problem: LinearProgram, result: SolveResult) -> None:
        while True:
            self._show_result(
                problem,
                result.status,
                result.objective_value,
                result.variable_values,
                result.pivot_count,
                result.message,
                result.steps,
            )

            hints = [("0", "MENU UTAMA")]
            if result.status == SolveStatus.OPTIMAL:
                hints.insert(0, ("2", "INTERPRETASI MANAJERIAL"))
                hints.insert(0, ("1", "DETAIL LANGKAH PIVOT"))

            self.view.footer(hints=hints, status=f"SOLVER {result.status.value}")

            if result.status == SolveStatus.OPTIMAL:
                action = Prompt.ask(
                    "PILIH TINDAKAN [1=PIVOT TRACE, 2=INTERPRETASI BISNIS, 0=SELESAI/MENU]",
                    choices=["1", "2", "0"],
                    console=self.view.console,
                )
                if action == "1":
                    self._show_pivot_steps_page(result.steps)
                elif action == "2":
                    self._show_business_interpretation(problem, result)
                elif action == "0":
                    break
            else:
                Prompt.ask("TEKAN ENTER UNTUK KEMBALI KE MENU", default="", show_default=False, console=self.view.console)
                break

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
        self.view.begin_screen(
            "HASIL SOLUSI PEMROGRAMAN LINEAR",
            f"STATUS: {status.value}",
            active_tab="BUILDER",
            breadcrumb="DASHBOARD SOLUSI",
        )

        status_color = "spring_green2" if status == SolveStatus.OPTIMAL else "bright_red"
        status_card_title = "STATUS SOLUSI"
        status_card_val = f"[OK] {status.value}" if status == SolveStatus.OPTIMAL else f"[X] {status.value}"

        z_val_str = f"{objective_value:,.4f}" if objective_value is not None else "TIDAK ADA"

        cards = [
            {"title": status_card_title, "value": status_card_val, "subtitle": "HASIL VERIFIKASI DUA FASE", "color": status_color},
            {"title": "NILAI OBJEKTIF OPTIMAL (Z*)", "value": z_val_str, "subtitle": f"{problem.direction.value}", "color": "gold1"},
            {"title": "TOTAL PIVOT SIMPLEKS", "value": f"{pivot_count} LANGKAH", "subtitle": f"{len(steps)} TERCATAT", "color": "bright_cyan"},
            {"title": "DIMENSI MODEL", "value": f"{len(problem.variables)} VAR / {len(problem.constraints)} KND", "subtitle": "UKURAN MATRIKS", "color": "bright_magenta"},
        ]
        self.view.console.print(self.view.render_kpi_cards(cards))
        self.view.console.print()

        msg_panel = Panel(
            Text(message.upper(), style="bold white"),
            title="[bold]PESAN DIAGNOSTIK SOLVER[/bold]",
            border_style=status_color,
            box=box.ROUNDED,
            padding=(0, 1),
        )
        self.view.console.print(msg_panel)

        if status is SolveStatus.OPTIMAL and objective_value is not None:
            self.view.console.print()
            var_table = Table(
                title="TABEL VARIABEL KEPUTUSAN & KONTRIBUSI OPTIMAL",
                box=box.ROUNDED,
                border_style="bright_cyan",
                expand=True,
                header_style="bold bright_cyan",
            )
            var_table.add_column("VARIABEL", style="bold gold1")
            var_table.add_column("DOMAIN", style="dim white")
            var_table.add_column("NILAI OPTIMAL (x*)", justify="right", style="bold spring_green2")
            var_table.add_column("KOEFISIEN (c)", justify="right", style="white")
            var_table.add_column("KONTRIBUSI KE Z", justify="right", style="bold bright_yellow")
            var_table.add_column("SHARE (%)", justify="right", style="cyan")

            for variable, val, coef in zip(problem.variables, variable_values, problem.objective):
                contribution = coef * val
                share = (abs(contribution) / abs(objective_value) * 100) if abs(objective_value) > 1e-9 else 0.0
                domain_desc = "x >= 0" if variable.domain == VariableDomain.NON_NEGATIVE else "Unrestricted"
                var_table.add_row(
                    variable.name,
                    domain_desc,
                    f"{val:,.6g}",
                    f"{coef:g}",
                    f"{contribution:,.6g}",
                    f"{share:.1f}%",
                )
            self.view.console.print(var_table)

            self.view.console.print()
            res_table = Table(
                title="ANALISIS EVALUASI KENDALA & PEMANFAATAN SUMBER DAYA",
                box=box.ROUNDED,
                border_style="bright_magenta",
                expand=True,
                header_style="bold bright_magenta",
            )
            res_table.add_column("KENDALA", style="bold white", justify="center")
            res_table.add_column("PEMAKAIAN (LHS)", justify="right", style="bold bright_white")
            res_table.add_column("RELASI", justify="center", style="bold gold1")
            res_table.add_column("BATAS (RHS)", justify="right", style="white")
            res_table.add_column("SLACK / SURPLUS", justify="right", style="bold cyan")
            res_table.add_column("UTILISASI (%)", justify="right", style="bold yellow")
            res_table.add_column("STATUS SUMBER DAYA", justify="center")

            for index, constraint in enumerate(problem.constraints, start=1):
                lhs = sum(coef * val for coef, val in zip(constraint.coefficients, variable_values))
                if constraint.relation is Relation.LESS_EQUAL:
                    margin = constraint.rhs - lhs
                elif constraint.relation is Relation.GREATER_EQUAL:
                    margin = lhs - constraint.rhs
                else:
                    margin = abs(lhs - constraint.rhs)

                is_binding = abs(margin) <= 1e-7
                status_badge = "[bold red on grey15] BINDING (HABIS) [/bold red on grey15]" if is_binding else "[bold green on grey15] IDLE (SISA) [/bold green on grey15]"

                util_str = "-"
                if abs(constraint.rhs) > 1e-9:
                    util = (lhs / constraint.rhs) * 100
                    util_str = f"{util:.1f}%"

                res_table.add_row(
                    f"C{index}",
                    f"{lhs:,.6g}",
                    constraint.relation.value,
                    f"{constraint.rhs:,.6g}",
                    f"{margin:,.6g}",
                    util_str,
                    status_badge,
                )
            self.view.console.print(res_table)

    def _show_business_interpretation(self, problem: LinearProgram, result: SolveResult) -> None:
        self.view.begin_screen(
            "RINGKASAN & INTERPRETASI MANAJERIAL",
            "WAWASAN EKSEKUTIF PENGAMBILAN KEPUTUSAN",
            active_tab="BUILDER",
            breadcrumb="MANAJERIAL",
        )

        opt_z = result.objective_value if result.objective_value is not None else 0.0
        var_values = result.variable_values

        content = Text()
        content.append("1. KEPUTUSAN ALOKASI OPTIMAL:\n", style="bold bright_cyan")
        for var, val in zip(problem.variables, var_values):
            if val > 1e-7:
                content.append(f" • Alokasikan / Produksi [bold gold1]{var.name}[/bold gold1] sebanyak [bold spring_green2]{val:,.4f}[/bold spring_green2] unit.\n")
            else:
                content.append(f" • [dim]{var.name}: Tidak dialokasikan (0 unit) karena tidak meningkatkan efisiensi Z.[/dim]\n")

        content.append("\n2. IDENTIFIKASI BOTTLENECK / KENDALA KRITIS:\n", style="bold bright_cyan")
        binding_count = 0
        for index, constraint in enumerate(problem.constraints, start=1):
            lhs = sum(coef * val for coef, val in zip(constraint.coefficients, var_values))
            margin = abs(constraint.rhs - lhs)
            if margin <= 1e-7:
                binding_count += 1
                content.append(
                    f" • [bold red]Kendala C{index} ADALAH BOTTLENECK UTAMA[/bold red] (Kapasitas {constraint.rhs:g} terpakai 100%). "
                    "Menambah kapasitas pada kendala ini akan langsung berpotensi mendongkrak keuntungan Z!\n",
                    style="white",
                )
        if binding_count == 0:
            content.append(" • Tidak terdapat kendala dengan batas ketat yang mengikat secara eksklusif.\n", style="dim")

        content.append("\n3. ANALISIS KAPASITAS MENGANGGUR (SLACK / IDLE):\n", style="bold bright_cyan")
        for index, constraint in enumerate(problem.constraints, start=1):
            lhs = sum(coef * val for coef, val in zip(constraint.coefficients, var_values))
            if constraint.relation == Relation.LESS_EQUAL and constraint.rhs - lhs > 1e-7:
                slack = constraint.rhs - lhs
                content.append(
                    f" • Kendala C{index} memiliki sisa kapasitas sebesar [bold bright_green]{slack:,.4f}[/bold bright_green] unit. "
                    "Sumber daya ini belum termanfaatkan secara penuh.\n",
                    style="white",
                )

        panel = Panel(
            content,
            box=box.ROUNDED,
            border_style="bright_cyan",
            padding=(1, 2),
        )
        self.view.console.print(panel)
        self.view.footer(hints=[("ENTER", "KEMBALI KE DASHBOARD SOLUSI")], status="INTERPRETASI")
        Prompt.ask("TEKAN ENTER UNTUK KEMBALI", default="", show_default=False, console=self.view.console)

    def _show_pivot_steps_page(self, steps: tuple[PivotStep, ...]) -> None:
        self.view.begin_screen(
            "JEJAK LANGKAH PIVOT SIMPLEKS (PIVOT TRACE)",
            f"TOTAL {len(steps)} LANGKAH TRANSFORMASI TABEL DUA FASE",
            active_tab="BUILDER",
            breadcrumb="PIVOT TRACE",
        )

        if not steps:
            self.view.alert("info", "TIDAK ADA PIVOT", "Solusi basis awal langsung memenuhi kriteria optimalitas tanpa pivot.")
            Prompt.ask("TEKAN ENTER UNTUK KEMBALI", default="", show_default=False, console=self.view.console)
            return

        table = Table(
            box=box.ROUNDED,
            border_style="gold1",
            expand=True,
            header_style="bold gold1",
        )
        table.add_column("NO", justify="center", style="dim", width=5)
        table.add_column("FASE", style="bold", justify="center", width=12)
        table.add_column("VARIABEL MASUK (ENTERING)", style="bold bright_cyan", justify="left")
        table.add_column("VARIABEL KELUAR (LEAVING)", style="bold bright_yellow", justify="left")
        table.add_column("ELEMEN PIVOT", justify="right", style="bold spring_green2")

        for index, step in enumerate(steps, start=1):
            phase_color = "bright_yellow" if "I" in step.phase and "II" not in step.phase else "bright_green"
            phase_styled = f"[{phase_color}]{step.phase}[/{phase_color}]"
            table.add_row(
                str(index),
                phase_styled,
                step.entering_variable,
                step.leaving_variable,
                f"{step.pivot_value:,.6g}",
            )

        self.view.console.print(table)
        self.view.footer(hints=[("ENTER", "KEMBALI KE DASHBOARD SOLUSI")], status="PIVOT DETAIL")
        Prompt.ask("TEKAN ENTER UNTUK KEMBALI", default="", show_default=False, console=self.view.console)
