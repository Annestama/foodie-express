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
    LoginFrame,
    RegisterFrame,
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

        # ---- State session (Pelanggan di-set setelah login) ----
        self.pelanggan = None
        self.keranjang = KeranjangBelanja()
        self.current_restoran_id = None
        self.nama_pemesan = ""

        # ---- Konfigurasi Window ----
        self.title("FoodOrder -- Aplikasi Pelanggan")
        self.geometry("1000x700")
        self.minsize(900, 600)
        self.configure(bg="#f4f1ea")

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"1000x700+{x}+{y}")

        # ---- Styling ttk ----
        self._setup_ttk_styles()

        # ---- Container untuk semua frame ----
        self.container = tk.Frame(self, bg="#f4f1ea")
        self.container.pack(fill="both", expand=True)

        # ---- Buat semua frame ----
        self.frames = {}
        self._init_frames()

        # ---- Tampilkan login awal ----
        self.show_frame("LoginFrame")

        # ---- Handle close ----
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_ttk_styles(self):
        """Konfigurasi style untuk widget ttk."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TScrollbar",
                        background="#d1cec7",
                        troughcolor="#f4f1ea",
                        arrowcolor="#808a8d",
                        borderwidth=0)
        style.configure("TCombobox",
                        fieldbackground="#faf9f6",
                        background="#faf9f6",
                        foreground="#3a4042",
                        selectbackground="#a594f9",
                        selectforeground="#ffffff")
        style.map("TCombobox",
                  fieldbackground=[("readonly", "#faf9f6")],
                  foreground=[("readonly", "#3a4042")])

    def _init_frames(self):
        """Inisialisasi semua frame halaman awal."""
        for FrameClass in (LoginFrame, RegisterFrame):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

    def on_login_success(self, user_data):
        """Dipanggil setelah login berhasil."""
        self.pelanggan = Pelanggan(nama=user_data['nama_lengkap'], app_root=self)
        self.nama_pemesan = self.pelanggan.nama
        
        # Inisialisasi frame utama setelah login
        for FrameClass in (DashboardFrame, MenuFrame, KeranjangFrame, RiwayatFrame):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)
            
        self.pelanggan.tampilkan_dashboard()
        self.show_frame("DashboardFrame")

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

    def do_logout(self):
        """Handle logout flow."""
        self.pelanggan = None
        self.nama_pemesan = ""
        self.keranjang.kosongkan()
        self.current_restoran_id = None
        
        # Clear login form
        if "LoginFrame" in self.frames:
            self.frames["LoginFrame"].username_var.set("")
            self.frames["LoginFrame"].password_var.set("")
            
        self.show_frame("LoginFrame")

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
