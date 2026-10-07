from dataclasses import dataclass

from pemrograman_linear_solution.models.problem import (
    Constraint,
    LinearProgram,
    ObjectiveDirection,
    Relation,
    Variable,
    VariableDomain,
)


@dataclass(frozen=True)
class ExampleCase:
    case_id: str
    title: str
    category: str
    story: str
    problem: LinearProgram
    notes: str


def get_example_cases() -> list[ExampleCase]:
    return [
        ExampleCase(
            case_id="1",
            title="OPTIMASI BAURAN PRODUKSI FURNITUR (MAKSIMASI KEUNTUNGAN)",
            category="MANUFAKTUR & PRODUKSI",
            story=(
                "SEBUAH PABRIK MEMPRODUKSI MEJA (M) DAN KURSI (K). "
                "KEUNTUNGAN PER UNIT MEJA ADALAH RP 300.000 DAN KURSI RP 200.000 (DALAM RIBU RUPIAH: 300 & 200). "
                "TERDAPAT 3 TAHAPAN PRODUKSI DENGAN KAPASITAS TERBATAS: "
                "PEMOTONGAN KAYU (MAKS 100 JAM), PERAKITAN (MAKS 70 JAM), DAN FINISHING (MAKS 80 JAM). "
                "TUJUAN: TENTUKAN KOMBINASI PRODUKSI MEJA DAN KURSI AGAR KEUNTUNGAN MAKSIMAL."
            ),
            notes="CONTOH KLASIK MAKSIMASI DENGAN KENDALA <= DAN HASIL OPTIMAL BULAT (M=40, K=20).",
            problem=LinearProgram(
                variables=(
                    Variable("MEJA", VariableDomain.NON_NEGATIVE),
                    Variable("KURSI", VariableDomain.NON_NEGATIVE),
                ),
                objective=(300.0, 200.0),
                direction=ObjectiveDirection.MAXIMIZE,
                constraints=(
                    Constraint((2.0, 1.0), Relation.LESS_EQUAL, 100.0),
                    Constraint((1.0, 1.0), Relation.LESS_EQUAL, 70.0),
                    Constraint((1.0, 2.0), Relation.LESS_EQUAL, 80.0),
                ),
            ),
        ),
        ExampleCase(
            case_id="2",
            title="PERENCANAAN DIET & NUTRISI RUMAH SAKIT (MINIMASI BIAYA)",
            category="KESEHATAN & GIZI",
            story=(
                "AHLI GIZI MERANCANG MENU DIET MENGGUNAKAN DUA BAHAN MAKANAN (F1 DAN F2). "
                "BIAYA F1 ADALAH RP 12.000/PORSI DAN F2 RP 18.000/PORSI. "
                "PASIEN WAJIB MEMENUHI MINIMAL 10 GRAM PROTEIN DAN MINIMAL 15 MG KALSIUM, "
                "SERTA TOTAL PORSI MAKANAN TIDAK BOLEH MELEBIHI 12 UNIT DEMI KESEHATAN LAMBUNG. "
                "TUJUAN: MINIMALKAN TOTAL BIAYA PENGADAAN MAKANAN."
            ),
            notes="CONTOH MINIMASI DENGAN KENDALA >= (SURPLUS & VARIABEL ARTIFISIAL FASE I).",
            problem=LinearProgram(
                variables=(
                    Variable("F1_PANGAN_A", VariableDomain.NON_NEGATIVE),
                    Variable("F2_PANGAN_B", VariableDomain.NON_NEGATIVE),
                ),
                objective=(12.0, 18.0),
                direction=ObjectiveDirection.MINIMIZE,
                constraints=(
                    Constraint((2.0, 1.0), Relation.GREATER_EQUAL, 10.0),
                    Constraint((1.0, 3.0), Relation.GREATER_EQUAL, 15.0),
                    Constraint((1.0, 1.0), Relation.LESS_EQUAL, 12.0),
                ),
            ),
        ),
        ExampleCase(
            case_id="3",
            title="PENCAMPURAN BAHAN KIMIA / BLENDING (KENDALA CAMPURAN <=, >=, =)",
            category="INDUSTRI KIMIA",
            story=(
                "PABRIK MEMPRODUKSI 100 LITER LARUTAN KHUSUS DARI 3 ZAT (Z1, Z2, Z3). "
                "KEUNTUNGAN MASING-MASING ADALAH 50, 40, DAN 60 PER LITER. "
                "TOTAL VOLUME HARUS TEPAT 100 LITER (KENDALA EQUALITY =). "
                "REAKTIVITAS MINIMAL 150 (KENDALA >=) DAN INDEKS TOKSISITAS MAKSIMAL 180 (KENDALA <=)."
            ),
            notes="MENUNJUKKAN KEMAMPUAN SOLVER MENANGANI KENDALA PERSAMAAN KETAT (=) DAN KETIDAKSAMAAN.",
            problem=LinearProgram(
                variables=(
                    Variable("Z1_AKTIF", VariableDomain.NON_NEGATIVE),
                    Variable("Z2_PELARUT", VariableDomain.NON_NEGATIVE),
                    Variable("Z3_STABILISATOR", VariableDomain.NON_NEGATIVE),
                ),
                objective=(50.0, 40.0, 60.0),
                direction=ObjectiveDirection.MAXIMIZE,
                constraints=(
                    Constraint((1.0, 1.0, 1.0), Relation.EQUAL, 100.0),
                    Constraint((2.0, 1.0, 3.0), Relation.GREATER_EQUAL, 150.0),
                    Constraint((1.0, 2.0, 1.0), Relation.LESS_EQUAL, 180.0),
                ),
            ),
        ),
        ExampleCase(
            case_id="4",
            title="STUDI KASUS KONTRADIKSI / INFEASIBLE (TIDAK LAYAK)",
            category="DEMONSTRASI TEORETIS",
            story=(
                "SEBUAH KASUS DI MANA SPESIFIKASI KONTRAK SALING BERTENTANGAN SECARA MATEMATIS: "
                "TOTAL PRODUKSI X1 + X2 TIDAK BOLEH LEBIH DARI 4 UNIT (<= 4), "
                "TETAPI PERMINTAAN MINIMAL PASAR MENSYARATKAN X1 + X2 HARUS SEKURANG-KURANGNYA 10 UNIT (>= 10). "
                "TIDAK ADA TITIK PADA BIDANG GEOMETRIS YANG DAPAT MEMENUHI KEDUA SYARAT INI."
            ),
            notes="FASE I SIMPLEKS AKAN GAGAL MENGELIMINASI VARIABEL ARTIFISIAL, MEMBUKTIKAN MODEL INFEASIBLE.",
            problem=LinearProgram(
                variables=(
                    Variable("X1", VariableDomain.NON_NEGATIVE),
                    Variable("X2", VariableDomain.NON_NEGATIVE),
                ),
                objective=(2.0, 3.0),
                direction=ObjectiveDirection.MAXIMIZE,
                constraints=(
                    Constraint((1.0, 1.0), Relation.LESS_EQUAL, 4.0),
                    Constraint((1.0, 1.0), Relation.GREATER_EQUAL, 10.0),
                ),
            ),
        ),
        ExampleCase(
            case_id="5",
            title="STUDI KASUS SOLUSI TAK TERBATAS / UNBOUNDED",
            category="DEMONSTRASI TEORETIS",
            story=(
                "MODEL DI MANA FUNGSI TUJUAN INGIN DIMAKSIMALKAN Z = 5*X1 + 4*X2, "
                "NAMUN KENDALA X1 - X2 <= 2 MEMBIARKAN X2 MEMBESAR BEBAS HINGGA TAK TERHINGGA "
                "DENGAN MENJAGA X1 = X2 TETAP MEMENUHI KENDALA. "
                "AKIBATNYA, NILAI TUJUAN Z DAPAT MENINGKAT MENUJU TAK HINGGA (INFINITY)."
            ),
            notes="SOLVER AKAN MENDETEKSI BAHWA RATIO TEST TIDAK MENEMUKAN KANDIDAT LEAVING VARIABLE.",
            problem=LinearProgram(
                variables=(
                    Variable("X1", VariableDomain.NON_NEGATIVE),
                    Variable("X2", VariableDomain.NON_NEGATIVE),
                ),
                objective=(5.0, 4.0),
                direction=ObjectiveDirection.MAXIMIZE,
                constraints=(
                    Constraint((1.0, -1.0), Relation.LESS_EQUAL, 2.0),
                ),
            ),
        ),
    ]
