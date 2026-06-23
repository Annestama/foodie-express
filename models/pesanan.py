"""
pesanan.py — Enkapsulasi (Pilar OOP #1)

Mendemonstrasikan enkapsulasi dengan menyembunyikan data sensitif pesanan
menggunakan atribut private (double underscore prefix).

Atribut private: __total_harga, __status_pengiriman
Akses & modifikasi hanya melalui getter/setter yang memiliki validasi.
"""


class Pesanan:
    """
    Class yang merepresentasikan satu transaksi pesanan makanan.

    Pilar Enkapsulasi (Encapsulation):
    - __total_harga    : Data finansial dilindungi, hanya bisa dibaca via get_total()
    - __status_pengiriman : Status hanya bisa diubah melalui set_status() yang
                            memvalidasi urutan status secara sequential (tidak bisa lompat).
    """

    # Urutan status yang WAJIB diikuti secara berurutan — tidak bisa dilompat
    STATUS_FLOW = [
        "Menunggu Konfirmasi",
        "Dikonfirmasi",
        "Diproses",
        "Dikirim",
        "Pesanan Selesai"
    ]

    def __init__(self, id: int, nama_pemesan: str, restoran_id: int,
                 items: list, total_harga: float, status: str = "Menunggu Konfirmasi",
                 waktu: str = None, restoran_nama: str = "", 
                 metode_pembayaran: str = "Cash", nominal_pembayaran: float = 0.0,
                 pajak_pesanan: float = 0.0, biaya_layanan_pesanan: float = 0.0):
        # Atribut public
        self.id = id
        self.nama_pemesan = nama_pemesan
        self.restoran_id = restoran_id
        self.items = items          # List of dict: {nama_menu, qty, subtotal}
        self.waktu = waktu
        self.restoran_nama = restoran_nama

        # Atribut PRIVATE (Enkapsulasi) — dilindungi dari akses langsung luar class
        self.__total_harga = total_harga
        self.__status_pengiriman = status
        self.__metode_pembayaran = metode_pembayaran
        self.__nominal_pembayaran = nominal_pembayaran
        self.__pajak_pesanan = pajak_pesanan
        self.__biaya_layanan_pesanan = biaya_layanan_pesanan

    # ===== GETTER METHODS =====
    def get_total(self) -> float:
        """Getter untuk total harga — satu-satunya cara membaca __total_harga."""
        return self.__total_harga

    def get_status(self) -> str:
        """Getter untuk status pengiriman — satu-satunya cara membaca __status_pengiriman."""
        return self.__status_pengiriman

    def get_status_index(self) -> int:
        """Mengembalikan index status saat ini dalam STATUS_FLOW."""
        try:
            return self.STATUS_FLOW.index(self.__status_pengiriman)
        except ValueError:
            return 0

    # ===== SETTER METHODS (dengan validasi) =====
    def set_status(self, new_status: str) -> bool:
        """
        Setter untuk mengubah status pengiriman.

        Validasi Sequential (Enkapsulasi):
        Status HANYA bisa maju 1 langkah ke depan dalam STATUS_FLOW.
        Tidak bisa mundur dan tidak bisa lompat langkah.

        Returns:
            True  — jika status berhasil diubah
            False — jika perubahan tidak valid
        """
        if new_status == "Dibatalkan":
            if self.__status_pengiriman in ["Menunggu Konfirmasi", "Dikonfirmasi", "Diproses"]:
                self.__status_pengiriman = new_status
                return True
            return False

        if new_status not in self.STATUS_FLOW:
            return False

        try:
            current_idx = self.STATUS_FLOW.index(self.__status_pengiriman)
            new_idx = self.STATUS_FLOW.index(new_status)
        except ValueError:
            return False

        # Validasi: hanya boleh maju 1 langkah
        if new_idx == current_idx + 1:
            self.__status_pengiriman = new_status
            return True

        return False

    def set_status_paksa(self, new_status: str):
        """
        Setter khusus untuk sinkronisasi dari database (bukan untuk aksi user).
        Digunakan saat loading data dari DB untuk menyesuaikan state objek.
        """
        if new_status in self.STATUS_FLOW:
            self.__status_pengiriman = new_status

    # ===== HELPER METHODS =====
    def get_next_status(self) -> str | None:
        """Mengembalikan status berikutnya yang bisa dituju, atau None jika sudah final."""
        current_idx = self.get_status_index()
        if current_idx < len(self.STATUS_FLOW) - 1:
            return self.STATUS_FLOW[current_idx + 1]
        return None

    def is_selesai(self) -> bool:
        """Mengecek apakah pesanan sudah selesai sepenuhnya."""
        return self.__status_pengiriman == "Pesanan Selesai"

    def is_siap_diterima(self) -> bool:
        """Mengecek apakah pesanan sudah dikirim (tombol selesai di user app bisa aktif)."""
        return self.__status_pengiriman == "Dikirim"

    def format_total(self) -> str:
        """Format total harga menjadi string rupiah yang mudah dibaca."""
        return f"Rp{self.__total_harga:,.0f}"

    def to_dict(self) -> dict:
        """Mengkonversi objek Pesanan ke dictionary untuk kebutuhan display."""
        return {
            'id': self.id,
            'nama_pemesan': self.nama_pemesan,
            'restoran_id': self.restoran_id,
            'restoran_nama': self.restoran_nama,
            'items': self.items,
            'total_harga': self.__total_harga,
            'status': self.__status_pengiriman,
            'metode_pembayaran': self.__metode_pembayaran,
            'nominal_pembayaran': self.__nominal_pembayaran,
            'pajak_pesanan': self.__pajak_pesanan,
            'biaya_layanan_pesanan': self.__biaya_layanan_pesanan,
            'waktu': self.waktu
        }

    def __str__(self):
        return (f"Pesanan #{self.id} | {self.nama_pemesan} | "
                f"{self.format_total()} | Status: {self.__status_pengiriman}")

    def __repr__(self):
        return f"Pesanan(id={self.id}, pemesan='{self.nama_pemesan}', status='{self.__status_pengiriman}')"
