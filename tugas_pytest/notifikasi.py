"""Layanan notifikasi eksternal (simulasi).

Di dunia nyata fungsi ini memanggil server email/SMS. Pada unit test fungsi ini
TIDAK boleh dipanggil sungguhan, sehingga di-mock.
"""


def kirim_notifikasi(email, pesan):
    raise RuntimeError("Layanan email asli tidak boleh dipanggil saat unit test")