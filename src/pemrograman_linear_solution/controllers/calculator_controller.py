from __future__ import annotations

from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from pemrograman_linear_solution.services.calculator import CalculatorService
from pemrograman_linear_solution.views.console import ConsoleView


class CalculatorController:
    def __init__(
        self,
        view: ConsoleView,
        calculator: CalculatorService | None = None,
    ) -> None:
        self.view = view
        self.calculator = calculator or CalculatorService()
        self._last_alert: tuple[str, str, str] | None = None

    def run(self) -> None:
        while True:
            self.view.begin_screen(
                "KALKULATOR MATEMATIKA CEPAT",
                "ALAT BANTU HITUNG ARITMATIKA, PECAHAN & FUNGSI MATEMATIKA",
                active_tab="CALC",
                breadcrumb="KALKULATOR",
            )

            # Display alert from previous operation if any
            if self._last_alert:
                lvl, title, msg = self._last_alert
                self.view.alert(lvl, title, msg)
                self.view.console.print()
                self._last_alert = None

            # Quick guide banner
            guide_table = Table.grid(expand=True)
            guide_table.add_column("left", ratio=1)
            guide_table.add_column("right", ratio=1)

            left_text = Text()
            left_text.append("OPERATOR MATEMATIKA:\n", style="bold bright_cyan")
            left_text.append(" • Tambah / Kurang : +  ,  -\n", style="white")
            left_text.append(" • Kali / Bagi     : * (atau x)  ,  / (atau :)\n", style="white")
            left_text.append(" • Pangkat / Mod   : ** (atau ^)  ,  %\n", style="white")
            left_text.append(" • Pembagian Bulat : //\n", style="white")

            right_text = Text()
            right_text.append("FUNGSI & VARIABEL MEMORI:\n", style="bold bright_yellow")
            right_text.append(" • Fungsi Utama : sqrt(x), cbrt(x), abs(x), round(x, n)\n", style="white")
            right_text.append(" • Lanjutan     : log(x), exp(x), sin(x), cos(x), factorial(n)\n", style="white")
            right_text.append(" • Memori 'ans' : Menyimpan hasil perhitungan sebelumnya\n", style="white")
            right_text.append(" • Konstanta    : pi, e, tau\n", style="white")

            guide_table.add_row(
                Panel(left_text, box=box.ROUNDED, border_style="cyan", padding=(0, 1)),
                Panel(right_text, box=box.ROUNDED, border_style="bright_yellow", padding=(0, 1)),
            )
            self.view.console.print(guide_table)
            self.view.console.print()

            # KPI Card if there is at least one result
            history = self.calculator.get_history()
            if history:
                latest = history[-1]
                kpi_cards = [
                    {
                        "title": "EKSPRESI TERAKHIR",
                        "value": latest.expression,
                        "subtitle": "INPUT PENGGUNA",
                        "color": "bright_cyan",
                    },
                    {
                        "title": "HASIL DESIMAL",
                        "value": latest.formatted_result,
                        "subtitle": "NILAI NUMERIK (FLOAT/INT)",
                        "color": "bright_green",
                    },
                    {
                        "title": "BENTUK PECAHAN (FRACTION)",
                        "value": latest.fraction_str,
                        "subtitle": "RASIO SIMPLEX (P/Q)",
                        "color": "gold1",
                    },
                ]
                self.view.console.print(self.view.render_kpi_cards(kpi_cards))
                self.view.console.print()

            # History Table
            history_table = Table(
                box=box.ROUNDED,
                border_style="bright_cyan",
                expand=True,
                header_style="bold bright_cyan",
            )
            history_table.add_column("NO", justify="center", style="bold gold1", width=5)
            history_table.add_column("EKSPRESI MATEMATIKA", style="bold white", ratio=3)
            history_table.add_column("HASIL DESIMAL", style="bold bright_green", ratio=2)
            history_table.add_column("BENTUK PECAHAN (FRACTION)", style="bold bright_yellow", ratio=2)

            if history:
                start_idx = max(0, len(history) - 8)
                for idx, item in enumerate(history[start_idx:], start=start_idx + 1):
                    history_table.add_row(
                        str(idx),
                        item.expression,
                        item.formatted_result,
                        item.fraction_str,
                    )
            else:
                history_table.add_row(
                    "-",
                    "BELUM ADA RIWAYAT PERHITUNGAN. KETIK EKSPRESI DI BAWAH INI.",
                    "-",
                    "-",
                )

            self.view.console.print(
                Panel(
                    history_table,
                    title="[bold bright_cyan]RIWAYAT PERHITUNGAN (CALCULATION LOG)[/bold bright_cyan]",
                    border_style="bright_cyan",
                    box=box.ROUNDED,
                    padding=(0, 0),
                )
            )

            self.view.footer(
                hints=[
                    ("EKSPRESI", "HITUNG"),
                    ("H", "BANTUAN"),
                    ("C", "RESET RIWAYAT"),
                    ("0", "KEMBALI"),
                ],
                status="KALKULATOR SIAP",
                status_color="bright_cyan",
            )

            raw = Prompt.ask(
                "MASUKKAN EKSPRESI MATEMATIKA ATAU PERINTAH",
                default="",
                show_default=False,
                console=self.view.console,
            ).strip()

            if not raw:
                continue

            lowered = raw.lower()
            if lowered in ("0", "exit", "quit", "kembali", "q"):
                return
            elif lowered in ("c", "clear", "cls", "reset"):
                self.calculator.clear_history()
                self._last_alert = (
                    "info",
                    "RIWAYAT DIRESET",
                    "SEMUA RIWAYAT KALKULASI DAN MEMORI 'ANS' BERHASIL DIBERSIHKAN.",
                )
            elif lowered in ("h", "help", "?", "bantuan"):
                self._show_help()
            else:
                try:
                    item = self.calculator.evaluate(raw)
                    self._last_alert = (
                        "success",
                        "HASIL PERHITUNGAN",
                        f"{item.expression} = {item.formatted_result}  [PECAHAN: {item.fraction_str}]",
                    )
                except ValueError as exc:
                    self._last_alert = ("error", "KESALAHAN PERHITUNGAN", str(exc))

    def _show_help(self) -> None:
        self.view.begin_screen(
            "PANDUAN LENGKAP KALKULATOR",
            "SINTAKS, FUNGSI, DAN REKOMENDASI PENGGUNAAN",
            active_tab="CALC",
            breadcrumb="PANDUAN KALKULATOR",
        )

        content = Text()
        content.append("MANFAAT KALKULATOR DALAM PEMROGRAMAN LINEAR:\n", style="bold gold1")
        content.append(
            " • Rasio Uji Minimum (Min-Ratio Test): Menghitung b_i / a_ij untuk menentukan baris pivot keluar.\n"
            " • Normalisasi Baris Pivot: Menghitung pembagian seluruh baris dengan elemen pivot.\n"
            " • Operasi Baris Elementer (OBE): Menghitung nilai sel baru (New = Old - Factor * Pivot).\n"
            " • Presisi Pecahan (Fractions): Menampilkan pecahan eksak dan campuran untuk akurasi Simplex.\n\n",
            style="white",
        )

        content.append("DAFTAR OPERATOR YANG DIDUKUNG:\n", style="bold bright_cyan")
        content.append(" • +  : Penjumlahan (contoh: 25 + 14)\n", style="white")
        content.append(" • -  : Pengurangan (contoh: 100 - 32.5)\n", style="white")
        content.append(" • *  : Perkalian (atau gunakan 'x', contoh: 12 * 8 atau 12 x 8)\n", style="white")
        content.append(" • /  : Pembagian (atau gunakan ':', contoh: 15 / 4 atau 15 : 4)\n", style="white")
        content.append(" • // : Pembagian bulat (contoh: 17 // 5 -> 3)\n", style="white")
        content.append(" • %  : Sisa bagi / Modulo (contoh: 17 % 5 -> 2)\n", style="white")
        content.append(" • ** : Perpangkatan (atau gunakan '^', contoh: 2 ** 5 atau 2 ^ 5 -> 32)\n\n", style="white")

        content.append("FUNGSI MATEMATIKA:\n", style="bold bright_yellow")
        content.append(" • sqrt(x)         : Akar kuadrat (contoh: sqrt(144) -> 12)\n", style="white")
        content.append(" • cbrt(x)         : Akar tiga / kubik (contoh: cbrt(27) -> 3)\n", style="white")
        content.append(" • abs(x)          : Nilai mutlak (contoh: abs(-25) -> 25)\n", style="white")
        content.append(" • round(x, n)     : Pembulatan ke n desimal (contoh: round(3.14159, 2) -> 3.14)\n", style="white")
        content.append(" • ceil(x), floor(x): Pembulatan ke atas / ke bawah\n", style="white")
        content.append(" • log(x), log10(x): Logaritma natural dan basis 10\n", style="white")
        content.append(" • exp(x)          : Eksponensial e^x\n", style="white")
        content.append(" • factorial(n)    : Faktorial bilangan bulat n! (contoh: factorial(5) -> 120)\n", style="white")
        content.append(" • gcd(a, b)       : Faktor Persekutuan Terbesar (FPB)\n", style="white")
        content.append(" • min(...), max(...): Nilai minimum dan maksimum kumpulan angka\n\n", style="white")

        content.append("VARIABEL MEMORI & KONSTANTA:\n", style="bold bright_green")
        content.append(" • ans : Hasil kalkulasi terakhir. Memungkinkan perhitungan berantai seperti 'ans * 2'.\n", style="white")
        content.append(" • pi  : Nilai pi (3.14159265...)\n", style="white")
        content.append(" • e   : Bilangan Euler (2.71828182...)\n", style="white")
        content.append(" • tau : Nilai 2*pi (6.28318530...)\n", style="white")

        panel = Panel(
            content,
            box=box.ROUNDED,
            border_style="bright_cyan",
            padding=(1, 2),
        )
        self.view.console.print(panel)
        self.view.footer(hints=[("ENTER", "KEMBALI KE KALKULATOR")], status="BANTUAN")
        Prompt.ask("TEKAN ENTER UNTUK KEMBALI", default="", show_default=False, console=self.view.console)
