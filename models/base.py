"""
base.py — Abstract Base Class (Abstraksi / Pilar OOP #2)

Mendefinisikan kontrak desain program menggunakan Abstract Base Class.
Class Pengguna berfungsi sebagai blueprint yang mewajibkan setiap subclass
(Pelanggan, Kasir) untuk mengimplementasikan method tampilkan_dashboard() sendiri.
"""

from abc import ABC, abstractmethod


class Pengguna(ABC):
    """
    Abstract Base Class untuk semua jenis pengguna dalam sistem.
    Menerapkan pilar Abstraksi dengan mendefinisikan kontrak method
    tampilkan_dashboard() yang wajib diimplementasikan oleh subclass.
    """

    def __init__(self, nama: str):
        self.nama = nama

    @abstractmethod
    def tampilkan_dashboard(self):
        """
        Method abstrak yang wajib diimplementasikan oleh setiap subclass.
        Pelanggan akan menampilkan dashboard katalog restoran.
        Kasir akan menampilkan dashboard transaksi masuk.
        """
        pass

    def sapa(self) -> str:
        """Method konkret yang diwariskan ke semua subclass."""
        return f"Selamat datang, {self.nama}!"

    def __str__(self):
        return f"{self.__class__.__name__}(nama={self.nama})"
