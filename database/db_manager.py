"""
db_manager.py — Database Manager menggunakan SQLite

Mengelola koneksi, pembuatan tabel, dan semua operasi CRUD untuk
shared database yang digunakan oleh User App dan Restaurant App.
"""

import sqlite3
import os
import hashlib
from datetime import datetime


# Path database relatif ke root proyek
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pemesanan.db")


class DatabaseManager:
    """
    Singleton-like database manager untuk mengelola koneksi SQLite.
    Menyediakan semua operasi CRUD yang dibutuhkan User App & Restaurant App.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._inisialisasi_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Membuat koneksi baru ke SQLite dengan row_factory untuk akses kolom by name."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Agar hasil query bisa diakses seperti dict
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging untuk concurrent access
        conn.execute("PRAGMA foreign_keys=ON")   # Aktifkan foreign key constraint
        return conn

    def _inisialisasi_database(self):
        """Membuat semua tabel jika belum ada."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Tabel users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                username     TEXT UNIQUE NOT NULL,
                password     TEXT NOT NULL,
                nama_lengkap TEXT NOT NULL
            )
        """)

        # Tabel restoran
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS restoran (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                nama    TEXT NOT NULL,
                deskripsi TEXT DEFAULT '',
                aktif   INTEGER DEFAULT 1
            )
        """)

        # Tabel menu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                restoran_id INTEGER NOT NULL,
                nama        TEXT NOT NULL,
                harga       REAL NOT NULL,
                tipe        TEXT NOT NULL DEFAULT 'makanan',  -- 'makanan' atau 'minuman'
                FOREIGN KEY (restoran_id) REFERENCES restoran(id)
            )
        """)

        # Tabel pesanan (header)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pesanan (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                restoran_id     INTEGER NOT NULL,
                nama_pemesan    TEXT NOT NULL,
                waktu           TEXT NOT NULL,
                status          TEXT NOT NULL DEFAULT 'Menunggu Konfirmasi',
                total_harga     REAL NOT NULL DEFAULT 0,
                waktu_dikonfirmasi TEXT,
                waktu_diproses     TEXT,
                waktu_dikirim      TEXT,
                waktu_selesai      TEXT,
                FOREIGN KEY (restoran_id) REFERENCES restoran(id)
            )
        """)

        # Tabel detail pesanan (line items)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detail_pesanan (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                pesanan_id  INTEGER NOT NULL,
                menu_id     INTEGER NOT NULL,
                nama_menu   TEXT NOT NULL,
                qty         INTEGER NOT NULL,
                subtotal    REAL NOT NULL,
                FOREIGN KEY (pesanan_id) REFERENCES pesanan(id),
                FOREIGN KEY (menu_id) REFERENCES menu(id)
            )
        """)

        conn.commit()
        conn.close()

    # =========================================================================
    # RESTORAN OPERATIONS
    # =========================================================================

    def get_semua_restoran(self, keyword: str = "") -> list[dict]:
        """Mengambil daftar restoran aktif, opsional difilter berdasarkan keyword."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if keyword:
            cursor.execute(
                "SELECT * FROM restoran WHERE aktif = 1 AND nama LIKE ? ORDER BY nama",
                (f"%{keyword}%",)
            )
        else:
            cursor.execute("SELECT * FROM restoran WHERE aktif = 1 ORDER BY nama")

        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_restoran_by_id(self, restoran_id: int) -> dict | None:
        """Mengambil data satu restoran berdasarkan ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM restoran WHERE id = ?", (restoran_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    # =========================================================================
    # MENU OPERATIONS
    # =========================================================================

    def get_menu_by_restoran(self, restoran_id: int) -> list[dict]:
        """Mengambil daftar menu berdasarkan restoran_id."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM menu WHERE restoran_id = ? ORDER BY tipe, nama",
            (restoran_id,)
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_menu_by_id(self, menu_id: int) -> dict | None:
        """Mengambil data satu item menu berdasarkan ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM menu WHERE id = ?", (menu_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def tambah_menu(self, restoran_id: int, nama: str, harga: float, tipe: str) -> int:
        """Menambahkan menu baru ke database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO menu (restoran_id, nama, harga, tipe)
               VALUES (?, ?, ?, ?)""",
            (restoran_id, nama, harga, tipe)
        )
        menu_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return menu_id

    def update_menu(self, menu_id: int, nama: str, harga: float, tipe: str) -> bool:
        """Mengupdate informasi menu."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE menu 
               SET nama = ?, harga = ?, tipe = ?
               WHERE id = ?""",
            (nama, harga, tipe, menu_id)
        )
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def hapus_menu(self, menu_id: int) -> bool:
        """Menghapus menu dari database. Akan gagal jika menu sudah pernah dipesan."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM menu WHERE id = ?", (menu_id,))
            affected = cursor.rowcount
            conn.commit()
            success = affected > 0
        except sqlite3.IntegrityError:
            success = False
        finally:
            conn.close()
        return success

    # =========================================================================
    # STATISTIK OPERATIONS
    # =========================================================================

    def get_statistik_pendapatan(self, restoran_id: int) -> float:
        """Mengambil total pendapatan dari pesanan yang sudah selesai."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT SUM(total_harga) as total FROM pesanan
               WHERE restoran_id = ? AND status = 'Pesanan Selesai'""",
            (restoran_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row['total'] if row and row['total'] else 0.0

    def get_menu_terlaris(self, restoran_id: int) -> list[dict]:
        """Mengambil daftar menu terlaris (diurutkan berdasarkan total qty dipesan)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT m.id, m.nama, m.harga, SUM(dp.qty) as total_terjual, SUM(dp.subtotal) as total_pendapatan
               FROM detail_pesanan dp
               JOIN pesanan p ON dp.pesanan_id = p.id
               JOIN menu m ON dp.menu_id = m.id
               WHERE p.restoran_id = ? AND p.status = 'Pesanan Selesai'
               GROUP BY m.id
               ORDER BY total_terjual DESC""",
            (restoran_id,)
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    # =========================================================================
    # PESANAN OPERATIONS
    # =========================================================================

    def buat_pesanan(self, restoran_id: int, nama_pemesan: str, items: list[dict]) -> int:
        """
        Membuat pesanan baru ke database.

        Args:
            restoran_id: ID restoran tujuan
            nama_pemesan: Nama pelanggan
            items: List dict berisi {menu_id, nama, qty, subtotal}

        Returns:
            ID pesanan yang baru dibuat
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        total_harga = sum(item['subtotal'] for item in items)
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insert header pesanan
        cursor.execute(
            """INSERT INTO pesanan (restoran_id, nama_pemesan, waktu, status, total_harga)
               VALUES (?, ?, ?, 'Menunggu Konfirmasi', ?)""",
            (restoran_id, nama_pemesan, waktu, total_harga)
        )
        pesanan_id = cursor.lastrowid

        # Insert detail pesanan (line items)
        for item in items:
            cursor.execute(
                """INSERT INTO detail_pesanan (pesanan_id, menu_id, nama_menu, qty, subtotal)
                   VALUES (?, ?, ?, ?, ?)""",
                (pesanan_id, item['menu_id'], item['nama'], item['qty'], item['subtotal'])
            )

        conn.commit()
        conn.close()
        return pesanan_id

    def get_pesanan_by_id(self, pesanan_id: int) -> dict | None:
        """Mengambil data pesanan lengkap (header + detail) berdasarkan ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Ambil header
        cursor.execute(
            """SELECT p.*, r.nama AS restoran_nama
               FROM pesanan p
               JOIN restoran r ON p.restoran_id = r.id
               WHERE p.id = ?""",
            (pesanan_id,)
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        pesanan = dict(row)

        # Ambil detail items
        cursor.execute(
            "SELECT * FROM detail_pesanan WHERE pesanan_id = ?",
            (pesanan_id,)
        )
        pesanan['items'] = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return pesanan

    def get_status_pesanan(self, pesanan_id: int) -> str | None:
        """Mengambil HANYA kolom status dari pesanan tertentu (untuk polling)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM pesanan WHERE id = ?", (pesanan_id,))
        row = cursor.fetchone()
        conn.close()
        return row['status'] if row else None

    def get_pesanan_by_pemesan(self, nama_pemesan: str) -> list[dict]:
        """
        Mengambil semua pesanan berdasarkan nama pemesan.
        Digunakan oleh User App untuk menampilkan riwayat pesanan.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT p.*, r.nama AS restoran_nama
               FROM pesanan p
               JOIN restoran r ON p.restoran_id = r.id
               WHERE p.nama_pemesan = ?
               ORDER BY p.waktu DESC""",
            (nama_pemesan,)
        )
        pesanan_list = []
        for row in cursor.fetchall():
            p = dict(row)
            cursor2 = conn.cursor()
            cursor2.execute("SELECT * FROM detail_pesanan WHERE pesanan_id = ?", (p['id'],))
            p['items'] = [dict(r) for r in cursor2.fetchall()]
            pesanan_list.append(p)
        conn.close()
        return pesanan_list

    def get_semua_pesanan_restoran(self, restoran_id: int, filter_status: str = "Semua") -> list[dict]:
        """
        Mengambil semua pesanan untuk restoran tertentu, opsional difilter status.
        Digunakan oleh Restaurant App untuk menampilkan antrian.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if filter_status and filter_status != "Semua":
            cursor.execute(
                """SELECT p.*, r.nama AS restoran_nama
                   FROM pesanan p
                   JOIN restoran r ON p.restoran_id = r.id
                   WHERE p.restoran_id = ? AND p.status = ?
                   ORDER BY p.waktu DESC""",
                (restoran_id, filter_status)
            )
        else:
            cursor.execute(
                """SELECT p.*, r.nama AS restoran_nama
                   FROM pesanan p
                   JOIN restoran r ON p.restoran_id = r.id
                   WHERE p.restoran_id = ?
                   ORDER BY p.waktu DESC""",
                (restoran_id,)
            )

        pesanan_list = []
        for row in cursor.fetchall():
            p = dict(row)
            # Ambil detail items untuk setiap pesanan
            cursor2 = conn.cursor()
            cursor2.execute("SELECT * FROM detail_pesanan WHERE pesanan_id = ?", (p['id'],))
            p['items'] = [dict(r) for r in cursor2.fetchall()]
            pesanan_list.append(p)

        conn.close()
        return pesanan_list

    def update_status_pesanan(self, pesanan_id: int, status_baru: str) -> bool:
        """
        Mengupdate status pesanan di database.

        Args:
            pesanan_id: ID pesanan yang akan diupdate
            status_baru: Status baru yang valid

        Returns:
            True jika berhasil diupdate
        """
        status_valid = [
            "Menunggu Konfirmasi", "Dikonfirmasi",
            "Diproses", "Dikirim", "Pesanan Selesai"
        ]
        if status_baru not in status_valid:
            return False

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        col_to_update = None
        
        if status_baru == "Dikonfirmasi":
            col_to_update = "waktu_dikonfirmasi"
        elif status_baru == "Diproses":
            col_to_update = "waktu_diproses"
        elif status_baru == "Dikirim":
            col_to_update = "waktu_dikirim"
        elif status_baru == "Pesanan Selesai":
            col_to_update = "waktu_selesai"

        conn = self._get_connection()
        cursor = conn.cursor()
        
        if col_to_update:
            cursor.execute(
                f"UPDATE pesanan SET status = ?, {col_to_update} = ? WHERE id = ?",
                (status_baru, now, pesanan_id)
            )
        else:
            cursor.execute(
                "UPDATE pesanan SET status = ? WHERE id = ?",
                (status_baru, pesanan_id)
            )
            
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    # =========================================================================
    # UTILITY
    # =========================================================================

    def is_database_kosong(self) -> bool:
        """Mengecek apakah belum ada restoran sama sekali di database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM restoran")
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] == 0

    # =========================================================================
    # USER & AUTHENTICATION OPERATIONS
    # =========================================================================

    def _hash_password(self, password: str) -> str:
        """Meng-hash password menggunakan SHA-256."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def register_user(self, username: str, password: str, nama_lengkap: str) -> bool:
        """
        Mendaftarkan user baru.
        Mengembalikan True jika berhasil, False jika username sudah ada.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        hashed_pw = self._hash_password(password)
        try:
            cursor.execute(
                "INSERT INTO users (username, password, nama_lengkap) VALUES (?, ?, ?)",
                (username, hashed_pw, nama_lengkap)
            )
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            # Username sudah ada (UNIQUE constraint failed)
            success = False
        finally:
            conn.close()
        return success

    def authenticate_user(self, username: str, password: str) -> dict | None:
        """
        Memvalidasi login user.
        Mengembalikan dict data user jika berhasil, atau None jika gagal.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        hashed_pw = self._hash_password(password)
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, hashed_pw)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
