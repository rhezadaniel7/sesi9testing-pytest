"""Sistem Peminjaman Buku Perpustakaan Kampus.

Tiga fungsi berlogika bersyarat:
  1. hitung_denda          -> denda keterlambatan (ada batas maksimal)
  2. tentukan_kuota_buku   -> jumlah buku yang boleh dipinjam
  3. proses_peminjaman     -> memakai dua fungsi di atas + kirim notifikasi (dependensi eksternal)
"""

from notifikasi import kirim_notifikasi

DENDA_MAKSIMAL = 50_000
TARIF_PER_HARI = {"mahasiswa": 1_000, "dosen": 500, "umum": 2_000}

# Riwayat peminjaman disimpan di memori (state global -> perlu dibersihkan oleh fixture)
riwayat_peminjaman = []


def hitung_denda(hari_telat, jenis_member):
    """Denda = hari_telat x tarif member, maksimal Rp50.000."""
    if hari_telat < 0:
        raise ValueError("Hari telat tidak boleh negatif")
    if jenis_member not in TARIF_PER_HARI:
        raise ValueError(f"Jenis member tidak dikenal: {jenis_member}")
    if hari_telat == 0:
        return 0

    denda = hari_telat * TARIF_PER_HARI[jenis_member]
    if denda > DENDA_MAKSIMAL:
        return DENDA_MAKSIMAL
    return denda


def tentukan_kuota_buku(jenis_member, punya_tunggakan):
    """Anggota yang masih punya tunggakan denda tidak boleh meminjam."""
    if punya_tunggakan:
        return 0
    if jenis_member == "dosen":
        return 10
    if jenis_member == "mahasiswa":
        return 5
    return 2  # member umum


def proses_peminjaman(id_anggota, jumlah_buku, jenis_member, email, punya_tunggakan=False):
    if id_anggota <= 0:
        raise ValueError("ID anggota tidak valid")
    if jumlah_buku <= 0:
        raise ValueError("Jumlah buku harus lebih dari 0")

    kuota = tentukan_kuota_buku(jenis_member, punya_tunggakan)
    if kuota == 0:
        return "ditolak: masih ada tunggakan"
    if jumlah_buku > kuota:
        return "ditolak: melebihi kuota"

    riwayat_peminjaman.append((id_anggota, jumlah_buku))
    terkirim = kirim_notifikasi(email, f"Peminjaman {jumlah_buku} buku berhasil")
    return "berhasil" if terkirim else "berhasil, notifikasi gagal"