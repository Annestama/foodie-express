"""
keranjang.py — Class KeranjangBelanja

Mengelola daftar item yang dipilih pelanggan dalam sesi belanja aktif (in-memory).
Bertanggung jawab untuk menambah, mengedit, menghapus item, dan menghitung grand total.
"""


class KeranjangBelanja:
    """
    Class yang merepresentasikan keranjang belanja sementara dalam memori sesi.
    Data disimpan dalam list of dict sebelum di-checkout ke database.
    """

    def __init__(self):
        # List item: masing-masing berformat {menu_id, nama, harga, qty, subtotal, tipe}
        self._items: list[dict] = []

    def tambah_item(self, menu_id: int, nama: str, harga: float, qty: int, tipe: str = "makanan"):
        """
        Menambahkan item ke keranjang.
        Jika item dengan menu_id yang sama sudah ada, qty-nya akan ditambah (bukan duplikat).

        Args:
            menu_id: ID menu dari database
            nama: Nama menu
            harga: Harga satuan
            qty: Jumlah yang dipesan (harus > 0)
            tipe: 'makanan' atau 'minuman'
        """
        if qty <= 0:
            return False

        # Cek apakah item sudah ada di keranjang
        for item in self._items:
            if item['menu_id'] == menu_id:
                item['qty'] += qty
                item['subtotal'] = item['harga'] * item['qty']
                return True

        # Item baru — tambahkan ke list
        self._items.append({
            'menu_id': menu_id,
            'nama': nama,
            'harga': harga,
            'qty': qty,
            'subtotal': harga * qty,
            'tipe': tipe
        })
        return True

    def edit_qty(self, menu_id: int, qty_baru: int) -> bool:
        """
        Mengubah kuantitas item dalam keranjang.
        Jika qty_baru == 0, item akan dihapus dari keranjang secara otomatis (sesuai PRD).

        Returns:
            True jika berhasil, False jika item tidak ditemukan
        """
        for i, item in enumerate(self._items):
            if item['menu_id'] == menu_id:
                if qty_baru <= 0:
                    # Hapus item jika qty diubah ke 0
                    self._items.pop(i)
                else:
                    item['qty'] = qty_baru
                    item['subtotal'] = item['harga'] * qty_baru
                return True
        return False

    def hapus_item(self, menu_id: int) -> bool:
        """
        Menghapus item dari keranjang berdasarkan menu_id.

        Returns:
            True jika berhasil dihapus, False jika tidak ditemukan
        """
        for i, item in enumerate(self._items):
            if item['menu_id'] == menu_id:
                self._items.pop(i)
                return True
        return False

    def kosongkan(self):
        """Mengosongkan seluruh isi keranjang."""
        self._items.clear()

    def hitung_grand_total(self) -> float:
        """Menghitung total akumulasi biaya dari semua item di keranjang."""
        return sum(item['subtotal'] for item in self._items)

    def format_grand_total(self) -> str:
        """Mengembalikan grand total dalam format rupiah."""
        return f"Rp{self.hitung_grand_total():,.0f}"

    def is_kosong(self) -> bool:
        """Mengecek apakah keranjang kosong."""
        return len(self._items) == 0

    def get_items(self) -> list[dict]:
        """Mengembalikan salinan list items (untuk menghindari modifikasi langsung)."""
        return list(self._items)

    def jumlah_item(self) -> int:
        """Mengembalikan jumlah jenis item dalam keranjang."""
        return len(self._items)

    def total_qty(self) -> int:
        """Mengembalikan total qty keseluruhan item."""
        return sum(item['qty'] for item in self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        if self.is_kosong():
            return "Keranjang kosong"
        lines = [f"Keranjang ({self.jumlah_item()} item):"]
        for item in self._items:
            lines.append(f"  - {item['nama']} x{item['qty']} = Rp{item['subtotal']:,.0f}")
        lines.append(f"  TOTAL: {self.format_grand_total()}")
        return "\n".join(lines)
