"""Verified regulation clauses (from carbonatix-ml#39), solo Clause interface."""
from dataclasses import dataclass

__all__ = ["CORPUS", "PLACEHOLDER_SENTINEL", "Clause", "has_placeholder_text", "select_clauses"]

PLACEHOLDER_SENTINEL = "PASTE THE VERBATIM ARTICLE TEXT HERE"

@dataclass(frozen=True)
class Clause:
    ref: str
    title: str
    text: str
    applies_to: str  # "deficit" | "surplus" | "always"

CORPUS: list[Clause] = [
    Clause(
        ref='Perpres 98/2021 Pasal 1 angka 2',
        title='perpres-98-2021 Pasal 1 angka 2',
        text='Nilai Ekonomi Karbon yang selanjutnya disingkat NEK adalah nilai terhadap setiap unit emisi gas rumah kaca yang dihasilkan dari kegiatan manusia dan kegiatan ekonomi.',
        applies_to='always',
    ),
    Clause(
        ref='Perpres 98/2021 Pasal 1 angka 17',
        title='perpres-98-2021 Pasal 1 angka 17',
        text='Perdagangan Karbon adalah mekanisme berbasis pasar untuk mengurangi Emisi GRK melalui kegiatan jual beli Unit Karbon.',
        applies_to='always',
    ),
    Clause(
        ref='Perpres 110/2025 Pasal 1 angka 3',
        title='perpres-110-2025 Pasal 1 angka 3',
        text='Nilai Ekonomi Karbon yang selanjutnya disingkat NEK adalah nilai terhadap setiap unit emisi gas rumah kaca yang dihasilkan dari kegiatan manusia dan kegiatan ekonomi.',
        applies_to='always',
    ),
    Clause(
        ref='Perpres 110/2025 Pasal 1 angka 22',
        title='perpres-110-2025 Pasal 1 angka 22',
        text='Perdagangan Karbon adalah mekanisme berbasis pasar untuk mengurangi Emisi GRK melalui kegiatan jual beli Unit Karbon.',
        applies_to='always',
    ),
    Clause(
        ref='Permen ESDM 16/2022 Pasal 1 angka 17',
        title='permen-esdm-16-2022 Pasal 1 angka 17',
        text='Persetujuan Teknis Batas Atas Emisi GRK Pelaku Usaha Pembangkit Tenaga Listrik yang selanjutnya disebut PTBAE-PU adalah penetapan kuota emisi yang diberikan kepada pelaku usaha untuk mengemisikan GRK dalam kurun waktu tertentu yang dinyatakan dalam ton karbon dioksida ekuivalen.',
        applies_to='deficit',
    ),
    Clause(
        ref='Permen ESDM 2/2023 Pasal 1 angka 10',
        title='permen-esdm-2-2023 Pasal 1 angka 10',
        text='Penangkapan dan Penyimpanan Karbon (Carbon Capture and Storage) yang selanjutnya disingkat CCS adalah kegiatan mengurangi Emisi GRK yang mencakup penangkapan Emisi Karbon dan/atau pengangkutan Emisi Karbon tertangkap, dan penyimpanan ke Zona Target Injeksi dengan aman dan permanen sesuai dengan kaidah keteknikan yang baik.',
        applies_to='always',
    ),
    Clause(
        ref='Permen ESDM 2/2023 Pasal 1 angka 11',
        title='permen-esdm-2-2023 Pasal 1 angka 11',
        text='Penangkapan, Pemanfaatan, dan Penyimpanan Karbon (Carbon Capture, Utilization and Storage) yang selanjutnya disingkat CCUS adalah kegiatan mengurangi Emisi GRK yang mencakup penangkapan Emisi Karbon dan/atau pengangkutan Emisi Karbon tertangkap, pemanfaatan Emisi Karbon tertangkap, dan penyimpanan ke Zona Target Injeksi dengan aman dan permanen sesuai dengan kaidah keteknikan yang baik.',
        applies_to='always',
    ),
    Clause(
        ref='Permen LHK 12/2024 Pasal 1 angka 29',
        title='permen-lhk-12-2024 Pasal 1 angka 29',
        text='Sistem Registri Nasional Pengendalian Perubahan Iklim yang selanjutnya disingkat SRN PPI adalah sistem pengelolaan, penyediaan data, dan informasi berbasis web mengenai aksi dan Sumber Daya untuk Mitigasi Perubahan Iklim, Adaptasi Perubahan Iklim, dan NEK di Indonesia.',
        applies_to='always',
    ),
]

def has_placeholder_text() -> bool:
    return any(PLACEHOLDER_SENTINEL in c.text for c in CORPUS)

def select_clauses(*, is_compliant: bool) -> list[Clause]:
    wanted = "surplus" if is_compliant else "deficit"
    return [c for c in CORPUS if c.applies_to in ("always", wanted)]
