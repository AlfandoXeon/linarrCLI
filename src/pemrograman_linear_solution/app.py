from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from pemrograman_linear_solution.controllers.calculator_controller import CalculatorController
from pemrograman_linear_solution.controllers.problem_controller import ProblemController
from pemrograman_linear_solution.views.console import ConsoleView
from pemrograman_linear_solution.views.guide import GuideView


class Application:
    def __init__(self, view: ConsoleView | None = None) -> None:
        self.view = view or ConsoleView()
        self.problem_controller = ProblemController(self.view)
        self.calculator_controller = CalculatorController(self.view)
        self.guide_view = GuideView(self.view)

    def run(self) -> None:
        while True:
            self.view.begin_screen(
                "MENU UTAMA EKSEKUTIF",
                "SISTEM PEMECAH MASALAH PEMROGRAMAN LINEAR PROFESIONAL",
                active_tab="MENU",
                breadcrumb="HOME",
            )

            # Highlight banner
            banner_text = Text()
            banner_text.append("SELAMAT DATANG DI PEMROGRAMAN LINEAR SOLUTION\n", style="bold gold1")
            banner_text.append(
                "Solusi cerdas, akurat, dan transparan untuk perumusan serta analisis matematis Linear Programming.\n",
                style="italic bright_white",
            )
            banner_text.append("DIBANGUN DENGAN ALGORITMA DUA FASE SIMPLEKS MANDIRI OLEH ", style="dim")
            banner_text.append("ALFANDOXEON", style="bold bright_cyan")

            self.view.console.print(
                Panel(
                    Align.center(banner_text),
                    box=box.DOUBLE,
                    border_style="bright_cyan",
                    padding=(1, 2),
                )
            )
            self.view.console.print()

            # Feature cards
            feature_table = Table.grid(expand=True)
            feature_table.add_column(ratio=1)
            feature_table.add_column(ratio=1)
            feature_table.add_column(ratio=1)

            feature_table.add_row(
                Panel(
                    Align.center(
                        Text.from_markup(
                            "[bold bright_green]SOLVER DUA FASE[/bold bright_green]\n"
                            "[white]Mendukung <=, >=, =, dan variabel Unrestricted secara presisi.[/white]"
                        )
                    ),
                    box=box.ROUNDED,
                    border_style="bright_green",
                ),
                Panel(
                    Align.center(
                        Text.from_markup(
                            "[bold gold1]ANALISIS BISNIS[/bold gold1]\n"
                            "[white]Deteksi kendala kritis (bottleneck) dan utilisasi sumber daya.[/white]"
                        )
                    ),
                    box=box.ROUNDED,
                    border_style="gold1",
                ),
                Panel(
                    Align.center(
                        Text.from_markup(
                            "[bold bright_magenta]JEJAK TRANSPARAN[/bold bright_magenta]\n"
                            "[white]Riwayat tabel pivot lengkap dan langkah iterasi bertahap.[/white]"
                        )
                    ),
                    box=box.ROUNDED,
                    border_style="bright_magenta",
                ),
            )
            self.view.console.print(feature_table)
            self.view.console.print()

            # Navigation Menu Table
            menu = Table(
                box=box.ROUNDED,
                border_style="bright_cyan",
                expand=True,
                header_style="bold bright_cyan",
            )
            menu.add_column("KODE", justify="center", style="bold black on bright_cyan", width=8)
            menu.add_column("MODUL & TINDAKAN", style="bold white", ratio=2)
            menu.add_column("DESKRIPSI", style="dim white", ratio=3)

            menu.add_row(
                " [1] ",
                "BUAT MODEL BARU (CREATE & SOLVE LP)",
                "Wizard interaktif memasukkan variabel, fungsi tujuan, dan kendala baru",
            )
            menu.add_row(
                " [2] ",
                "PRESET PERPUSTAKAAN KASUS (EXAMPLE PRESETS)",
                "Uji coba 5 studi kasus nyata (Furnitur, Diet, Blending, Infeasible, Unbounded)",
            )
            menu.add_row(
                " [3] ",
                "PANDUAN TEORI & FORMULA (LP TUTORIAL)",
                "Pelajari teori dasar LP, bentuk standar, metode dua fase, dan interpretasi",
            )
            menu.add_row(
                " [4] ",
                "KALKULATOR MATEMATIKA CEPAT (QUICK CALCULATOR)",
                "Kalkulator pembantu perhitungan aritmatika, pecahan, dan fungsi matematika",
            )
            menu.add_row(
                " [5] ",
                "TENTANG APLIKASI & SISTEM (ABOUT & SPECS)",
                "Informasi teknis mesin solver, spesifikasi algoritma, dan profil developer",
            )
            menu.add_row(
                " [0] ",
                "KELUAR DARI APLIKASI (EXIT)",
                "Tutup dan akhiri sesi pemrograman linear",
            )

            self.view.console.print(menu)
            self.view.footer(
                hints=[("1-5", "PILIH MENU"), ("0", "KELUAR")],
                status="STANDBY",
            )

            choice = Prompt.ask(
                "MASUKKAN PILIHAN MENU [0-5]",
                choices=("0", "1", "2", "3", "4", "5"),
                console=self.view.console,
            )

            if choice == "0":
                self._show_goodbye()
                return
            elif choice == "1":
                self.problem_controller.create_and_solve()
            elif choice == "2":
                self.problem_controller.load_preset_case()
            elif choice == "3":
                self.guide_view.open_guide()
            elif choice == "4":
                self.calculator_controller.run()
            elif choice == "5":
                self._show_about()

    def _show_about(self) -> None:
        self.view.begin_screen(
            "TENTANG SISTEM & DEVELOPER",
            "SPESIFIKASI DAN INFORMASI LENGKAP APLIKASI",
            active_tab="ABOUT",
            breadcrumb="ABOUT",
        )

        content = Text()
        content.append("IDENTITAS PERANGKAT LUNAK:\n", style="bold bright_cyan")
        content.append(" • Nama Produk     : PEMROGRAMAN LINEAR SOLUTION (PRO SUITE v2.0)\n", style="white")
        content.append(" • Pengembang       : ALFANDOXEON\n", style="bold gold1")
        content.append(" • GitHub           : https://github.com/ALFANDOXEON\n", style="bright_cyan")
        content.append(" • Bahasa & Runtime : Python 3.10+ (Rich Terminal Graphics Engine)\n\n", style="white")

        content.append("FITUR DAN KEUNGGULAN UTAMA:\n", style="bold bright_yellow")
        content.append(" • Algoritma Dua Fase Simplex mandiri (Two-Phase Simplex Method) tanpa library eksternal black-box.\n", style="white")
        content.append(" • Penanganan kendala pertidaksamaan campuran (<=, >=) dan persamaan ketat (=).\n", style="white")
        content.append(" • Variabel bebas (Unrestricted) otomatis dipecah menjadi selisih dua variabel non-negatif.\n", style="white")
        content.append(" • Verifikasi mandiri keabsahan solusi terhadap model matematis awal.\n", style="white")
        content.append(" • Analisis otomatis kendala kritis (Bottleneck / Binding Constraints) dan utilisasi kapasitas.\n\n", style="white")

        content.append("PARAMETER KOMPUTASI & TOLERANSI:\n", style="bold bright_green")
        content.append(" • Toleransi Numerik Float : 1e-9 (Epsilon)\n", style="white")
        content.append(" • Batas Iterasi Pivot     : 10.000 Iterasi (Perlindungan terhadap Cycling/Degenerasi)\n", style="white")
        content.append(" • Skala Model             : Hingga 20 Variabel Keputusan & 50 Kendala\n", style="white")

        panel = Panel(
            content,
            box=box.ROUNDED,
            border_style="bright_cyan",
            padding=(1, 2),
        )
        self.view.console.print(panel)
        self.view.footer(hints=[("ENTER", "KEMBALI KE MENU UTAMA")], status="INFO SISTEM")
        Prompt.ask("TEKAN ENTER UNTUK KEMBALI", default="", show_default=False, console=self.view.console)

    def _show_goodbye(self) -> None:
        self.view.begin_screen(
            "TERIMA KASIH",
            "SESI APLIKASI TELAH BERAKHIR",
            active_tab="MENU",
            breadcrumb="KELUAR",
        )
        farewell = Text()
        farewell.append("TERIMA KASIH TELAH MENGGUNAKAN PEMROGRAMAN LINEAR SOLUTION\n", style="bold gold1")
        farewell.append("Semoga sukses dalam memecahkan masalah optimasi dan riset operasi Anda!\n\n", style="white")
        farewell.append("Dikembangkan dengan dedikasi oleh ", style="dim")
        farewell.append("ALFANDOXEON", style="bold bright_cyan")
        self.view.console.print(
            Panel(
                Align.center(farewell),
                box=box.DOUBLE,
                border_style="bright_cyan",
                padding=(1, 2),
            )
        )
        self.view.footer(hints=[("EXIT", "PROGRAM SELESAI")], status="OFFLINE", status_color="dim white")


def main() -> None:
    app = Application()
    try:
        app.run()
    except (EOFError, KeyboardInterrupt):
        app.view.console.print("\n[DIM]SESI TELAH DIAKHIRI OLEH PENGGUNA.[/DIM]")


if __name__ == "__main__":
    main()
