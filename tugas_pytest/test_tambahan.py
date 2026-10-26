"""Test tambahan, ditulis SETELAH membaca laporan coverage putaran pertama.

Celah yang ditemukan:
  - baris 41 : cabang member 'umum' di tentukan_kuota_buku belum pernah diuji
  - baris 48 : validasi jumlah_buku <= 0 di proses_peminjaman belum pernah diuji
"""

import pytest

from perpustakaan import hitung_denda, proses_peminjaman, tentukan_kuota_buku


def test_kuota_member_umum_hanya_dua():
    assert tentukan_kuota_buku("umum", punya_tunggakan=False) == 2


@pytest.mark.parametrize("jumlah", [0, -1])      # batas: tepat 0 dan satu di bawahnya
def test_peminjaman_jumlah_buku_tidak_valid_ditolak(jumlah):
    with pytest.raises(ValueError, match="Jumlah buku"):
        proses_peminjaman(1, jumlah, "mahasiswa", "x@kampus.id")


def test_denda_member_umum_memakai_tarif_2000():
    assert hitung_denda(3, "umum") == 6_000