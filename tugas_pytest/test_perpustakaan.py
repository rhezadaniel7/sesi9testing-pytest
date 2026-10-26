from unittest.mock import patch

import pytest

import perpustakaan as perpustakaan
from perpustakaan import hitung_denda, proses_peminjaman, tentukan_kuota_buku


# ---------------------------------------------------------------- FIXTURE
@pytest.fixture
def riwayat_bersih():
    """Arrange: kosongkan state global sebelum test, lalu bersihkan lagi sesudahnya."""
    perpustakaan.riwayat_peminjaman.clear()
    yield perpustakaan.riwayat_peminjaman       # diberikan ke test
    perpustakaan.riwayat_peminjaman.clear()     # cleanup setelah test selesai


# ------------------------------------------------- PARAMETRIZE (BVA denda)
# Batas 1: hari_telat 0 -> 1 (mulai kena denda)
# Batas 2: denda mencapai plafon Rp50.000 pada hari ke-50 (tarif mahasiswa Rp1.000)
@pytest.mark.parametrize(
    "hari_telat, diharapkan",
    [
        (0, 0),            # min        : tepat di batas bawah
        (1, 1_000),        # min + 1
        (49, 49_000),      # plafon - 1
        (50, 50_000),      # tepat di plafon
        (51, 50_000),      # plafon + 1 : dipotong ke plafon
    ],
)
def test_denda_mahasiswa_batas(hari_telat, diharapkan):
    assert hitung_denda(hari_telat, "mahasiswa") == diharapkan


def test_denda_dosen_tarif_lebih_murah():
    assert hitung_denda(10, "dosen") == 5_000


# ---------------------------------------------------- pytest.raises (negatif)
def test_denda_hari_negatif_ditolak():
    with pytest.raises(ValueError, match="tidak boleh negatif"):
        hitung_denda(-1, "mahasiswa")


def test_denda_member_tidak_dikenal_ditolak():
    with pytest.raises(ValueError, match="tidak dikenal"):
        hitung_denda(5, "alumni")


def test_peminjaman_id_tidak_valid_ditolak(riwayat_bersih):
    with pytest.raises(ValueError, match="ID anggota"):
        proses_peminjaman(0, 1, "mahasiswa", "a@kampus.id")


# ------------------------------------------------------------- kuota buku
def test_kuota_tunggakan_nol():
    assert tentukan_kuota_buku("dosen", punya_tunggakan=True) == 0


def test_kuota_dosen_dan_mahasiswa():
    assert tentukan_kuota_buku("dosen", False) == 10
    assert tentukan_kuota_buku("mahasiswa", False) == 5


# ---------------------------------------------------- MOCK + fixture (isolasi)
def test_peminjaman_berhasil_dan_notifikasi_terkirim(riwayat_bersih):
    # patch di tempat nama DIPAKAI (perpustakaan.kirim_notifikasi), bukan di notifikasi.py
    with patch("perpustakaan.kirim_notifikasi", return_value=True) as palsu:
        hasil = proses_peminjaman(101, 3, "mahasiswa", "dina@kampus.id")

    assert hasil == "berhasil"
    assert riwayat_bersih == [(101, 3)]
    palsu.assert_called_once_with("dina@kampus.id", "Peminjaman 3 buku berhasil")


def test_peminjaman_notifikasi_gagal_ditangani(riwayat_bersih):
    with patch("perpustakaan.kirim_notifikasi", return_value=False):
        assert proses_peminjaman(102, 2, "dosen", "budi@kampus.id") == "berhasil, notifikasi gagal"


def test_peminjaman_layanan_email_timeout(riwayat_bersih):
    with patch("perpustakaan.kirim_notifikasi", side_effect=TimeoutError):
        with pytest.raises(TimeoutError):
            proses_peminjaman(103, 1, "mahasiswa", "citra@kampus.id")


def test_peminjaman_melebihi_kuota_tidak_kirim_notifikasi(riwayat_bersih):
    with patch("perpustakaan.kirim_notifikasi") as palsu:
        hasil = proses_peminjaman(104, 6, "mahasiswa", "eko@kampus.id")   # kuota mahasiswa = 5

    assert hasil == "ditolak: melebihi kuota"
    assert riwayat_bersih == []
    palsu.assert_not_called()


def test_peminjaman_tunggakan_ditolak(riwayat_bersih):
    with patch("perpustakaan.kirim_notifikasi") as palsu:
        hasil = proses_peminjaman(105, 1, "dosen", "fani@kampus.id", punya_tunggakan=True)

    assert hasil == "ditolak: masih ada tunggakan"
    palsu.assert_not_called()