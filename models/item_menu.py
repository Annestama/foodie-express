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
    Pilar Polimorfisme: Meng-override method tampilkan_info().
    """

    def __init__(self, id: int, nama: str, harga: float, restoran_id: int):
        # Memanggil __init__ dari parent class (ItemMenu)
        super().__init__(id, nama, harga, restoran_id, tipe="makanan")

    def tampilkan_info(self) -> str:
        """
        OVERRIDE: Menampilkan informasi makanan.
        Pilar Polimorfisme — perilaku berbeda dari parent class.
        """
        return f"[Makanan] {self.nama}"

    def __repr__(self):
        return f"Makanan(id={self.id}, nama='{self.nama}', harga={self.harga})"


class Minuman(ItemMenu):
    """
    Child Class (Kelas Turunan) dari ItemMenu — merepresentasikan item minuman.

    Pilar Pewarisan: Mewarisi id, nama, harga, restoran_id dari ItemMenu.
    Pilar Polimorfisme: Meng-override method tampilkan_info().
    """

    def __init__(self, id: int, nama: str, harga: float, restoran_id: int):
        # Memanggil __init__ dari parent class (ItemMenu)
        super().__init__(id, nama, harga, restoran_id, tipe="minuman")

    def tampilkan_info(self) -> str:
        """
        OVERRIDE: Menampilkan informasi minuman.
        Pilar Polimorfisme — perilaku berbeda dari parent class maupun Makanan.
        """
        return f"[Minuman] {self.nama}"

    def __repr__(self):
        return f"Minuman(id={self.id}, nama='{self.nama}', harga={self.harga})"


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
            restoran_id=row['restoran_id']
        )
    elif row['tipe'] == 'minuman':
        return Minuman(
            id=row['id'],
            nama=row['nama'],
            harga=row['harga'],
            restoran_id=row['restoran_id']
        )
    else:
        return ItemMenu(
            id=row['id'],
            nama=row['nama'],
            harga=row['harga'],
            restoran_id=row['restoran_id']
        )
