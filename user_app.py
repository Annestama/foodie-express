"""
user_app.py — Entry Point Aplikasi Pelanggan (User App)

Demonstrasi Pilar Abstraksi:
  Class Pelanggan mewarisi Pengguna (Abstract Base Class) dan
  mengimplementasikan method abstrak tampilkan_dashboard().

Jalankan: python user_app.py
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Tambahkan root directory ke path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.base import Pengguna
from models.keranjang import KeranjangBelanja
from database.db_manager import DatabaseManager
from database.seed_data import seed
from views.user_views import (
    DashboardFrame,
    MenuFrame,
    KeranjangFrame,
    RiwayatFrame,
)


# ============================================================
# CLASS PELANGGAN — Turunan dari Pengguna (Abstraksi & Pewarisan)
# ============================================================
class Pelanggan(Pengguna):
    """
    Class Pelanggan — subclass dari Abstract Base Class Pengguna.

    Pilar Abstraksi: Mengimplementasikan method abstrak tampilkan_dashboard()
    sesuai kontrak yang didefinisikan di class Pengguna.

    Pilar Pewarisan: Mewarisi atribut 'nama' dan method 'sapa()' dari Pengguna.
    """

    def __init__(self, nama: str, app_root: tk.Tk):
        super().__init__(nama)  # Memanggil __init__ parent class Pengguna
        self.app_root = app_root

    def tampilkan_dashboard(self):
        """
        Implementasi wajib dari abstract method Pengguna.tampilkan_dashboard().
        Pilar Abstraksi: Setiap subclass memiliki implementasi dashboard sendiri.
        """
        self.app_root.deiconify()
        self.app_root.lift()
        print(f"[User App] {self.sapa()} -- Dashboard Pelanggan aktif.")


# ============================================================
# APLIKASI UTAMA USER APP
# ============================================================
class UserApp(tk.Tk):
    """
    Controller utama User App.
    Mengelola navigasi antar frame dan state session pelanggan.
    """

    def __init__(self):
        super().__init__()

        # ---- Inisialisasi Database (auto-seed jika kosong) ----
        self.db = DatabaseManager()
        seed()  # Otomatis skip jika sudah terisi

        # ---- Inisialisasi Pelanggan (implementasi Abstraksi) ----
        self.pelanggan = Pelanggan(nama="Zildjian Annesta", app_root=self)
        self.pelanggan.tampilkan_dashboard()

        # ---- State session ----
        self.keranjang = KeranjangBelanja()
        self.current_restoran_id = None
        self.nama_pemesan = self.pelanggan.nama  # Default sama dengan nama pelanggan

        # ---- Konfigurasi Window ----
        self.title("FoodOrder -- Aplikasi Pelanggan")
        self.geometry("1000x700")
        self.minsize(900, 600)
        self.configure(bg="#0f0f1a")

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"1000x700+{x}+{y}")

        # ---- Styling ttk ----
        self._setup_ttk_styles()

        # ---- Container untuk semua frame ----
        self.container = tk.Frame(self, bg="#0f0f1a")
        self.container.pack(fill="both", expand=True)

        # ---- Buat semua frame ----
        self.frames = {}
        self._init_frames()

        # ---- Tampilkan dashboard awal ----
        self.show_frame("DashboardFrame")

        # ---- Handle close ----
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_ttk_styles(self):
        """Konfigurasi style untuk widget ttk."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TScrollbar",
                        background="#2a2a3e",
                        troughcolor="#0f0f1a",
                        arrowcolor="#8892a4",
                        borderwidth=0)
        style.configure("TCombobox",
                        fieldbackground="#252540",
                        background="#252540",
                        foreground="#f0f0f0",
                        selectbackground="#7c3aed",
                        selectforeground="#ffffff")
        style.map("TCombobox",
                  fieldbackground=[("readonly", "#252540")],
                  foreground=[("readonly", "#f0f0f0")])

    def _init_frames(self):
        """Inisialisasi semua frame halaman."""
        for FrameClass in (DashboardFrame, MenuFrame, KeranjangFrame, RiwayatFrame):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

    def show_frame(self, frame_name: str):
        """Menampilkan frame tertentu ke depan."""
        # Stop polling riwayat jika pindah darinya
        if frame_name != "RiwayatFrame":
            riwayat = self.frames.get("RiwayatFrame")
            if riwayat and hasattr(riwayat, 'stop_polling'):
                riwayat.stop_polling()

        frame = self.frames[frame_name]

        # Refresh KeranjangFrame setiap kali dibuka
        if frame_name == "KeranjangFrame":
            frame.refresh()

        frame.tkraise()

    def show_menu(self, restoran_id: int):
        """Navigasi ke halaman menu dengan restoran tertentu."""
        self.current_restoran_id = restoran_id
        self.keranjang.kosongkan()  # Reset keranjang saat ganti restoran
        menu_frame = self.frames["MenuFrame"]
        menu_frame.load(restoran_id)
        self.show_frame("MenuFrame")

    def show_riwayat(self):
        """Navigasi ke halaman riwayat pesanan (dengan refresh & polling)."""
        riwayat = self.frames["RiwayatFrame"]
        riwayat.refresh()
        riwayat.tkraise()

    def reset_session(self):
        """Reset session untuk memesan lagi dari awal."""
        self.keranjang = KeranjangBelanja()
        self.current_restoran_id = None
        self.frames["DashboardFrame"].muat_restoran()
        self.show_frame("DashboardFrame")

    def on_close(self):
        """Handle window close — stop semua polling."""
        riwayat = self.frames.get("RiwayatFrame")
        if riwayat and hasattr(riwayat, 'stop_polling'):
            riwayat.stop_polling()
        self.destroy()


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  FoodOrder -- User App")
    print("  Aplikasi Pemesanan Makanan Online")
    print("  UAS Pemrograman Berorientasi Objek")
    print("=" * 50)
    app = UserApp()
    app.mainloop()
