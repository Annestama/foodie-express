"""
item_menu.py — Pewarisan & Polimorfisme (Pilar OOP #3 & #4)

Mendemonstrasikan:
- PEWARISAN: Class Makanan dan Minuman mewarisi atribut & method dari ItemMenu (parent)
- POLIMORFISME: Kedua subclass melakukan override pada method tampilkan_info()
  sehingga output berbeda meskipun nama method sama persis.
"""


class ItemMenu:
    """
    Parent Class (Kelas Induk) yang mendefinisikan atribut & behavior dasar
    untuk semua item menu, baik makanan maupun minuman.

    Pilar Pewarisan (Inheritance): Class ini adalah parent dari Makanan & Minuman.
    """

    def __init__(self, id: int, nama: str, harga: float, restoran_id: int, tipe: str = "umum"):
        self.id = id
        self.nama = nama
        self.harga = harga
        self.restoran_id = restoran_id
        self.tipe = tipe

    def tampilkan_info(self) -> str:
        """
        Method dasar yang akan di-override oleh subclass.
        Pilar Polimorfisme: subclass mengubah perilaku method ini.
        """
        return f"{self.nama} - Rp{self.harga:,.0f}"

    def get_harga(self) -> float:
        return self.harga

    def get_nama(self) -> str:
        return self.nama

    def __str__(self):
        return self.tampilkan_info()

    def __repr__(self):
        return f"ItemMenu(id={self.id}, nama='{self.nama}', harga={self.harga})"


class Makanan(ItemMenu):
    """
    Child Class (Kelas Turunan) dari ItemMenu — merepresentasikan item makanan.

    Pilar Pewarisan: Mewarisi id, nama, harga, restoran_id dari ItemMenu.
    Pilar Polimorfisme: Meng-override method tampilkan_info() dengan format
    yang menyertakan informasi level kepedasan.

    Tambahan atribut:
        level_pedas (str): Level kepedasan makanan (Tidak Pedas / Pedas / Sangat Pedas)
    """

    def __init__(self, id: int, nama: str, harga: float, restoran_id: int, level_pedas: str = "Tidak Pedas"):
        # Memanggil __init__ dari parent class (ItemMenu)
        super().__init__(id, nama, harga, restoran_id, tipe="makanan")
        self.level_pedas = level_pedas  # Atribut tambahan khusus subclass Makanan

    def tampilkan_info(self) -> str:
        """
        OVERRIDE: Menampilkan informasi makanan.
        Pilar Polimorfisme — perilaku berbeda dari parent class.
        """
        return f"[Makanan] {self.nama}"

    def __repr__(self):
        return f"Makanan(id={self.id}, nama='{self.nama}', harga={self.harga}, level_pedas='{self.level_pedas}')"


class Minuman(ItemMenu):
    """
    Child Class (Kelas Turunan) dari ItemMenu — merepresentasikan item minuman.

    Pilar Pewarisan: Mewarisi id, nama, harga, restoran_id dari ItemMenu.
    Pilar Polimorfisme: Meng-override method tampilkan_info() dengan format
    yang menyertakan informasi suhu minuman.

    Tambahan atribut:
        is_dingin (bool): True jika minuman disajikan dingin, False jika panas.
    """

    def __init__(self, id: int, nama: str, harga: float, restoran_id: int, is_dingin: bool = True):
        # Memanggil __init__ dari parent class (ItemMenu)
        super().__init__(id, nama, harga, restoran_id, tipe="minuman")
        self.is_dingin = is_dingin  # Atribut tambahan khusus subclass Minuman

    def tampilkan_info(self) -> str:
        """
        OVERRIDE: Menampilkan informasi minuman.
        Pilar Polimorfisme — perilaku berbeda dari parent class maupun Makanan.
        """
        return f"[Minuman] {self.nama}"

    def __repr__(self):
        return f"Minuman(id={self.id}, nama='{self.nama}', harga={self.harga}, is_dingin={self.is_dingin})"


def buat_item_dari_db(row: dict):
    """
    Factory function — membuat objek ItemMenu yang tepat berdasarkan data dari database.
    Mendemonstrasikan polimorfisme: satu pemanggilan menghasilkan objek berbeda.
    """
    if row['tipe'] == 'makanan':
        return Makanan(
            id=row['id'],
            nama=row['nama'],
            harga=row['harga'],
            restoran_id=row['restoran_id'],
            level_pedas=row.get('level_pedas', 'Tidak Pedas')
        )
    elif row['tipe'] == 'minuman':
        return Minuman(
            id=row['id'],
            nama=row['nama'],
            harga=row['harga'],
            restoran_id=row['restoran_id'],
            is_dingin=bool(row.get('is_dingin', True))
        )
    else:
        return ItemMenu(
            id=row['id'],
            nama=row['nama'],
            harga=row['harga'],
            restoran_id=row['restoran_id']
        )
