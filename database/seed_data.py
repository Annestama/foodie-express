"""
seed_data.py — Script untuk mengisi data awal restoran & menu

Jalankan script ini SEKALI untuk mengisi database dengan data demo.
Data akan otomatis di-skip jika database sudah terisi.
"""

import sys
import os

# Tambahkan root project ke sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager


def seed():
    """Mengisi database dengan data restoran dan menu awal."""
    db = DatabaseManager()

    if not db.is_database_kosong():
        print("[OK] Database sudah terisi. Seed data di-skip.")
        return

    print("[*] Mengisi database dengan data awal...")

    conn = db._get_connection()
    cursor = conn.cursor()

    # =========================================================================
    # DATA RESTORAN
    # =========================================================================
    restoran_data = [
        (1, "Warung Padang Sederhana", "Masakan Minang otentik dengan cita rasa rumahan"),
        (2, "Sushi Tei Express", "Japanese cuisine segar berkualitas premium"),
        (3, "Kopi Kenangan Nusantara", "Kopi lokal spesial dan makanan ringan kekinian"),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO restoran (id, nama, deskripsi) VALUES (?, ?, ?)",
        restoran_data
    )

    # =========================================================================
    # DATA MENU — Warung Padang Sederhana (restoran_id = 1)
    # =========================================================================
    menu_padang = [
        # (restoran_id, nama, harga, tipe, level_pedas, is_dingin)
        (1, "Rendang Sapi",        32000, "makanan", "Pedas",        1),
        (1, "Ayam Pop",            25000, "makanan", "Tidak Pedas",  1),
        (1, "Gulai Ikan",          28000, "makanan", "Pedas",        1),
        (1, "Sayur Nangka",        15000, "makanan", "Tidak Pedas",  1),
        (1, "Telur Balado",        18000, "makanan", "Sangat Pedas", 1),
        (1, "Es Teh Manis",         8000, "minuman", "Tidak Pedas",  1),
        (1, "Es Jeruk Segar",      10000, "minuman", "Tidak Pedas",  1),
        (1, "Teh Tawar Panas",      5000, "minuman", "Tidak Pedas",  0),
    ]

    # =========================================================================
    # DATA MENU — Sushi Tei Express (restoran_id = 2)
    # =========================================================================
    menu_sushi = [
        (2, "Salmon Sashimi (5pcs)", 65000, "makanan", "Tidak Pedas",  1),
        (2, "Spicy Tuna Roll",       55000, "makanan", "Pedas",        1),
        (2, "Chicken Katsu Don",     48000, "makanan", "Tidak Pedas",  1),
        (2, "Ebi Tempura Roll",      58000, "makanan", "Tidak Pedas",  1),
        (2, "Takoyaki (6pcs)",       32000, "makanan", "Pedas",        1),
        (2, "Matcha Latte Dingin",   35000, "minuman", "Tidak Pedas",  1),
        (2, "Ocha Hot",              15000, "minuman", "Tidak Pedas",  0),
        (2, "Yuzu Sparkling",        30000, "minuman", "Tidak Pedas",  1),
    ]

    # =========================================================================
    # DATA MENU — Kopi Kenangan Nusantara (restoran_id = 3)
    # =========================================================================
    menu_kopi = [
        (3, "Kopi Susu Kenangan",   28000, "minuman", "Tidak Pedas",  1),
        (3, "Americano Es",         22000, "minuman", "Tidak Pedas",  1),
        (3, "Cappuccino Panas",     30000, "minuman", "Tidak Pedas",  0),
        (3, "Cokelat Es",           25000, "minuman", "Tidak Pedas",  1),
        (3, "Croissant Butter",     22000, "makanan", "Tidak Pedas",  1),
        (3, "Roti Bakar Selai",     18000, "makanan", "Tidak Pedas",  1),
        (3, "Pisang Goreng Keju",   20000, "makanan", "Tidak Pedas",  1),
        (3, "Nasi Goreng Kafe",     32000, "makanan", "Pedas",        1),
    ]

    semua_menu = menu_padang + menu_sushi + menu_kopi

    cursor.executemany(
        """INSERT OR IGNORE INTO menu
           (restoran_id, nama, harga, tipe, level_pedas, is_dingin)
           VALUES (?, ?, ?, ?, ?, ?)""",
        semua_menu
    )

    conn.commit()
    conn.close()

    print(f"[OK] Berhasil menambahkan {len(restoran_data)} restoran")
    print(f"[OK] Berhasil menambahkan {len(semua_menu)} item menu")
    print("[OK] Database siap digunakan!")


if __name__ == "__main__":
    seed()
