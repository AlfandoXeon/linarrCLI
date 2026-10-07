from rich import box
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from pemrograman_linear_solution.views.console import ConsoleView


class GuideView:
    def __init__(self, view: ConsoleView) -> None:
        self.view = view

    def open_guide(self) -> None:
        while True:
            self.view.begin_screen(
                "PANDUAN TEORI & FORMULA PEMROGRAMAN LINEAR",
                "PUSAT EDUKASI DAN REFERENSI METODE SIMPLEKS",
                active_tab="GUIDE",
                breadcrumb="PANDUAN",
            )

            menu_table = Table(
                box=box.ROUNDED,
                border_style="bright_cyan",
                expand=True,
                show_header=True,
                header_style="bold bright_cyan",
            )
            menu_table.add_column("NO", justify="center", style="bold gold1", width=6)
            menu_table.add_column("TOPIK PEMBELAJARAN", style="bold white", ratio=2)
            menu_table.add_column("RINGKASAN MATERI", style="dim white", ratio=3)

            menu_table.add_row(
                "1",
                "DASAR PEMROGRAMAN LINEAR (LP)",
                "Fungsi Tujuan, Variabel Keputusan, Kendala, & Asumsi Linearitas",
            )
            menu_table.add_row(
                "2",
                "STANDARISASI MODEL & VARIABEL",
                "Konversi Slack (<=), Surplus (>=), Artifisial (=, >=), & Unrestricted",
            )
            menu_table.add_row(
                "3",
                "METODE SIMPLEKS DUA FASE",
                "Cara Kerja Fase I (Solusi Layak Awal) & Fase II (Optimasi)",
            )
            menu_table.add_row(
                "4",
                "INTERPRETASI BISNIS & SENSITIVITAS",
                "Memahami Kendala Kritis (Binding / Bottleneck) vs Kapasitas Menganggur",
            )
            menu_table.add_row(
                "5",
                "DIAGNOSA STATUS SOLVER",
                "Penjelasan Mendalam Kasus Infeasible, Unbounded, & Iteration Limit",
            )
            menu_table.add_row(
                "0",
                "KEMBALI KE MENU UTAMA",
                "Keluar dari Pusat Panduan Teori",
            )

            self.view.console.print(menu_table)
            self.view.footer(hints=[("1-5", "PILIH MATERI"), ("0", "KEMBALI")], status="PANDUAN TEORI")

            choice = Prompt.ask(
                "PILIH NOMOR TOPIK [0-5]",
                choices=["0", "1", "2", "3", "4", "5"],
                console=self.view.console,
            )

            if choice == "0":
                break
            elif choice == "1":
                self._topic_basics()
            elif choice == "2":
                self._topic_standard_form()
            elif choice == "3":
                self._topic_two_phase_simplex()
            elif choice == "4":
                self._topic_sensitivity()
            elif choice == "5":
                self._topic_statuses()

    def _topic_basics(self) -> None:
        self.view.begin_screen("TOPIK 1: DASAR PEMROGRAMAN LINEAR", "KONSEP INTI & ANATOMI MODEL", active_tab="GUIDE")
        content = Text()
        content.append("1. PENGERTIAN\n", style="bold bright_cyan")
        content.append(
            "Pemrograman Linear (Linear Programming / LP) adalah teknik optimasi matematika untuk memaksimalkan "
            "atau meminimalkan fungsi tujuan linear di bawah sekumpulan batasan (kendala) linear.\n\n",
            style="white",
        )
        content.append("2. TIGA KOMPONEN UTAMA MODEL LP:\n", style="bold bright_cyan")
        content.append(" • VARIABEL KEPUTUSAN (x₁, x₂, ..., xₙ):\n", style="bold gold1")
        content.append("   Besaran atau kuantitas yang dapat dikendalikan dan ingin dicari nilainya oleh pengambil keputusan.\n", style="white")
        content.append(" • FUNGSI TUJUAN (OBJECTIVE FUNCTION - Z):\n", style="bold gold1")
        content.append("   Persamaan matematis yang ingin dioptimalkan:\n", style="white")
        content.append("   Maks / Min Z = c₁x₁ + c₂x₂ + ... + cₙxₙ\n", style="bold bright_green")
        content.append(" • KENDALA (CONSTRAINTS):\n", style="bold gold1")
        content.append("   Keterbatasan sumber daya (waktu, modal, bahan, kapasitas) yang dirumuskan sebagai:\n", style="white")
        content.append("   aᵢ₁x₁ + aᵢ₂x₂ + ... + aᵢₙxₙ (<= / >= / =) bᵢ\n\n", style="bold bright_green")
        content.append("3. ASUMSI-ASUMSI LINEARITAS:\n", style="bold bright_cyan")
        content.append(" • Proportionality: Kontribusi tiap variabel terhadap Z dan kendala berbanding lurus dengan nilainya.\n", style="white")
        content.append(" • Additivity: Total nilai fungsi adalah penjumlahan langsung dari kontribusi masing-masing aktivitas.\n", style="white")
        content.append(" • Divisibility: Nilai variabel keputusan boleh berupa pecahan/desimal non-bilangan bulat.\n", style="white")
        content.append(" • Deterministic: Semua parameter koefisien diketahui pasti dan bersifat konstan.\n", style="white")

        self.view.console.print(Panel(content, box=box.ROUNDED, border_style="bright_cyan", padding=(1, 2)))
        self.view.footer(hints=[("ENTER", "KEMBALI KE DAFTAR MATERI")], status="BACA MATERI")
        Prompt.ask("TEKAN ENTER UNTUK KEMBALI", default="", show_default=False, console=self.view.console)

    def _topic_standard_form(self) -> None:
        self.view.begin_screen("TOPIK 2: STANDARISASI MODEL & VARIABEL", "TRANSFORMASI ALGEBRAIK UNTUK SIMPLEKS", active_tab="GUIDE")
        table = Table(box=box.ROUNDED, border_style="gold1", expand=True)
        table.add_column("TIPE KENDALA", style="bold bright_cyan")
        table.add_column("VARIABEL TAMBAHAN", style="bold gold1")
        table.add_column("BENTUK PERSAMAAN STANDAR", style="bold bright_green")
        table.add_column("KETERANGAN & ARTI FISIK", style="white")

        table.add_row(
            "Kendala Kurang Dari (<=)\nContoh: 2x₁ + x₂ <= 100",
            "+ Slack (sᵢ >= 0)",
            "2x₁ + x₂ + s₁ = 100",
            "Slack mewakili kapasitas sumber daya yang MENGANGGUR / TIDAK TERPAKAI.",
        )
        table.add_row(
            "Kendala Lebih Dari (>=)\nContoh: x₁ + 3x₂ >= 15",
            "- Surplus (eᵢ >= 0)\n+ Artificial (aᵢ >= 0)",
            "x₁ + 3x₂ - e₁ + a₁ = 15",
            "Surplus mengukur kelebihan di atas batas minimum. Artificial dibutuhkan sebagai basis awal.",
        )
        table.add_row(
            "Kendala Sama Dengan (=)\nContoh: x₁ + x₂ = 50",
            "+ Artificial (aᵢ >= 0)",
            "x₁ + x₂ + a₁ = 50",
            "Hanya memerlukan variabel artifisial untuk membentuk matriks identitas awal.",
        )
        table.add_row(
            "Variabel Bebas\n(Unrestricted / Free x)",
            "Dua Variabel Non-Negatif\nx = x⁺ - x⁻",
            "x⁺ >= 0 dan x⁻ >= 0",
            "Memungkinkan variabel bernilai positif, nol, maupun negatif.",
        )
        self.view.console.print(table)

        note = Text()
        note.append("CATATAN PENTING NORMALISASI RHS (RUAS KANAN):\n", style="bold bright_yellow")
        note.append(
            "Jika nilai ruas kanan bᵢ bernilai negatif (misal: -2x₁ + x₂ <= -5), "
            "kedua ruas harus dikalikan dengan -1 terlebih dahulu dan tanda ketidaksamaan dibalik "
            "(menjadi: 2x₁ - x₂ >= 5). Aplikasi ini menangani normalisasi tersebut secara otomatis!",
            style="white",
        )
        self.view.console.print(Panel(note, box=box.ROUNDED, border_style="bright_yellow"))
        self.view.footer(hints=[("ENTER", "KEMBALI KE DAFTAR MATERI")], status="BACA MATERI")
        Prompt.ask("TEKAN ENTER UNTUK KEMBALI", default="", show_default=False, console=self.view.console)

    def _topic_two_phase_simplex(self) -> None:
        self.view.begin_screen("TOPIK 3: METODE SIMPLEKS DUA FASE", "ALGORITMA DUA TAHAP EFEKTIF & TRANSPARAN", active_tab="GUIDE")
        content = Text()
        content.append("MENGAPA DIBUTUHKAN DUA FASE?\n", style="bold bright_cyan")
        content.append(
            "Pada metode simpleks biasa, jika seluruh kendala bertanda <= dan RHS positif, basis awal diperoleh "
            "langsung dari variabel slack (titik origin 0,0). Namun jika ada kendala >= atau =, basis awal dari slack "
            "bernilai negatif sehingga tidak layak. Diperlukan variabel artifisial dan algoritma dua fase.\n\n",
            style="white",
        )
        content.append("FASE I: MENCARI SOLUSI LAYAK AWAL (INITIAL BFS)\n", style="bold gold1")
        content.append(
            " • Tujuan Fase 1: Meminimalkan jumlah seluruh variabel artifisial: Min W = ∑ aᵢ\n"
            " • Solusi Layak: Jika nilai optimal W = 0 dan seluruh aᵢ = 0, model memiliki solusi layak!\n"
            " • Deteksi Infeasible: Jika W > 0 dan tidak ada pivot perbaikan lagi, maka model INFEASIBLE (tidak layak).\n\n",
            style="white",
        )
        content.append("FASE II: MENGOPTIMALKAN FUNGSI TUJUAN SEBENARNYA\n", style="bold bright_green")
        content.append(
            " • Kolom variabel artifisial dihilangkan dari tabel simpleks.\n"
            " • Fungsi tujuan asli Z (Maks atau Min) dipulihkan ke dalam baris objektif.\n"
            " • Iterasi pivot Gauss-Jordan dilanjutkan hingga seluruh koefisien baris tujuan memenuhi syarat optimalitas "
            "(tidak ada reduced cost negatif untuk maksimasi).\n",
            style="white",
        )
        self.view.console.print(Panel(content, box=box.ROUNDED, border_style="bright_green", padding=(1, 2)))
        self.view.footer(hints=[("ENTER", "KEMBALI KE DAFTAR MATERI")], status="BACA MATERI")
        Prompt.ask("TEKAN ENTER UNTUK KEMBALI", default="", show_default=False, console=self.view.console)

    def _topic_sensitivity(self) -> None:
        self.view.begin_screen("TOPIK 4: INTERPRETASI BISNIS & SENSITIVITAS", "MEMBACA ARTI MANAJERIAL DARI HASIL OPTIMASI", active_tab="GUIDE")
        content = Text()
        content.append("1. KENDALA MENGIKAT / KRITIS (BINDING CONSTRAINTS / BOTTLENECK)\n", style="bold bright_red")
        content.append(
            " • Ditandai dengan SLACK = 0 (LHS = RHS).\n"
            " • Artinya: Sumber daya pada kendala ini HABIS TOTAL TERPAKAI 100%.\n"
            " • Dampak Manajerial: Sumber daya ini menjadi pembatas utama peningkatan keuntungan. "
            "Jika perusahaan ingin memperbesar keuntungan Z*, mereka harus menambah kapasitas sumber daya ini!\n\n",
            style="white",
        )
        content.append("2. KENDALA TIDAK MENGIKAT (NON-BINDING CONSTRAINTS)\n", style="bold bright_cyan")
        content.append(
            " • Ditandai dengan SLACK > 0 (LHS < RHS pada kendala <=).\n"
            " • Artinya: Terdapat SISA SUMBER DAYA / KAPASITAS MENGANGGUR (IDLE CAPACITY).\n"
            " • Dampak Manajerial: Menambah sumber daya ini tidak akan menambah keuntungan Z*, "
            "karena kapasitas saat ini saja belum habis terpakai.\n\n",
            style="white",
        )
        content.append("3. TINGKAT PEMANFAATAN KAPASITAS (UTILIZATION RATE)\n", style="bold gold1")
        content.append(
            "   Tingkat pemanfaatan dihitung dengan rumus:\n"
            "   Utilisasi (%) = (LHS / RHS) × 100%\n"
            "   Aplikasi ini menampilkan persentase ini secara otomatis pada tabel solusi Anda!\n",
            style="white",
        )
        self.view.console.print(Panel(content, box=box.ROUNDED, border_style="bright_cyan", padding=(1, 2)))
        self.view.footer(hints=[("ENTER", "KEMBALI KE DAFTAR MATERI")], status="BACA MATERI")
        Prompt.ask("TEKAN ENTER UNTUK KEMBALI", default="", show_default=False, console=self.view.console)

    def _topic_statuses(self) -> None:
        self.view.begin_screen("TOPIK 5: DIAGNOSA STATUS SOLVER", "PENYEBAB DAN ARTINYA BAGI PENGGUNA", active_tab="GUIDE")
        table = Table(box=box.ROUNDED, border_style="bright_magenta", expand=True)
        table.add_column("STATUS", style="bold")
        table.add_column("ARTI MATEMATIS", style="white")
        table.add_column("PENYEBAB DALAM DUNIA NYATA", style="dim white")

        table.add_row(
            "[bold green]OPTIMAL[/bold green]",
            "Titik sudut terbaik telah ditemukan dan diverifikasi memenuhi seluruh batasan.",
            "Rencana alokasi terbaik yang memaksimalkan laba atau meminimalkan biaya berhasil dirumuskan.",
        )
        table.add_row(
            "[bold red]INFEASIBLE[/bold red]",
            "Tidak ada satupun titik koordinat yang dapat memenuhi seluruh kendala secara simultan.",
            "Spesifikasi bertentangan. Misalnya target produksi terlalu tinggi namun bahan baku terlalu sedikit.",
        )
        table.add_row(
            "[bold yellow]UNBOUNDED[/bold yellow]",
            "Wilayah layak terbuka tanpa batas ke arah optimasi. Z bernilai +∞ atau -∞.",
            "Model kehilangan batasan penting di dunia nyata (misal lupa membatasi kapasitas maksimal pasar).",
        )
        table.add_row(
            "[bold cyan]ITERATION LIMIT[/bold cyan]",
            "Solver mencapai batas maksimum pivot (10.000 iterasi) sebelum konvergen.",
            "Dapat terjadi akibat fenomena degenerasi simpleks atau cycling.",
        )
        table.add_row(
            "[bold red]NUMERICAL FAILURE[/bold red]",
            "Terjadi pembagian mendekati nol, overflow, atau galat floating point.",
            "Koefisien dalam model memiliki rentang skala ekstrem (misal 1e-12 berdampingan dengan 1e12).",
        )
        self.view.console.print(table)
        self.view.footer(hints=[("ENTER", "KEMBALI KE DAFTAR MATERI")], status="BACA MATERI")
        Prompt.ask("TEKAN ENTER UNTUK KEMBALI", default="", show_default=False, console=self.view.console)
