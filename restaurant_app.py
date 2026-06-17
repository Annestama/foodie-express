"""
restaurant_app.py — Entry Point Aplikasi Restoran (Restaurant/Admin App)

Demonstrasi Pilar Abstraksi:
  Class Kasir mewarisi Pengguna (Abstract Base Class) dan
  mengimplementasikan method abstrak tampilkan_dashboard()
  dengan versi dashboard yang berbeda dari Pelanggan.

Jalankan: python restaurant_app.py
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Tambahkan root directory ke path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.base import Pengguna
from database.db_manager import DatabaseManager
from database.seed_data import seed
from views.restaurant_views import RestaurantDashboard


# ============================================================
# CLASS KASIR — Turunan dari Pengguna (Abstraksi & Pewarisan)
# ============================================================
class Kasir(Pengguna):
    """
    Class Kasir — subclass dari Abstract Base Class Pengguna.

    Pilar Abstraksi: Mengimplementasikan method abstrak tampilkan_dashboard()
    dengan versi dashboard kasir (berbeda dari Pelanggan — polimorfisme class).

    Pilar Pewarisan: Mewarisi atribut 'nama' dan method 'sapa()' dari Pengguna.
    """

    def __init__(self, nama: str, app_root: tk.Tk):
        super().__init__(nama)  # Memanggil __init__ parent class Pengguna
        self.app_root = app_root

    def tampilkan_dashboard(self):
        """
        Implementasi wajib dari abstract method Pengguna.tampilkan_dashboard().
        Pilar Abstraksi: Implementasi berbeda dari Pelanggan.tampilkan_dashboard().
        """
        self.app_root.deiconify()
        self.app_root.lift()
        print(f"[Restaurant App] {self.sapa()} -- Dashboard Kasir aktif.")


# ============================================================
# HALAMAN PILIH RESTORAN (Login Screen)
# ============================================================
class LoginFrame(tk.Frame):
    """
    Halaman pilih restoran sebelum masuk ke dashboard utama.
    Kasir memilih restoran mana yang akan dikelola.
    """

    BG_DARK    = "#f4f1ea"
    BG_CARD    = "#faf9f6"
    ACCENT     = "#e09f3e"
    TEXT_PRIMARY = "#3a4042"
    TEXT_MUTED = "#808a8d"
    TEXT_WHITE = "#ffffff"
    INPUT_BG   = "#ffffff"
    BORDER_COLOR = "#d1cec7"

    def __init__(self, parent, controller):
        super().__init__(parent, bg=self.BG_DARK)
        self.controller = controller
        self.db = controller.db
        self.selected_restoran = None
        self._build_ui()

    def _build_ui(self):
        # Center container
        center = tk.Frame(self, bg=self.BG_DARK)
        center.place(relx=0.5, rely=0.5, anchor="center", width=500)

        # Logo & title
        tk.Label(center, text="🏪", font=("Segoe UI", 60),
                 bg=self.BG_DARK, fg=self.ACCENT).pack()
        tk.Label(center, text="Restaurant",
                 font=("Segoe UI", 28, "bold"),
                 bg=self.BG_DARK, fg=self.TEXT_PRIMARY).pack(pady=(8, 4))
        tk.Label(center, text="Sistem Manajemen Pesanan Restoran",
                 font=("Segoe UI", 11),
                 bg=self.BG_DARK, fg=self.TEXT_MUTED).pack()

        tk.Frame(center, bg=self.ACCENT, height=3).pack(fill="x", pady=24)

        # Pilih restoran
        tk.Label(center, text="Pilih Restoran yang Dikelola:",
                 font=("Segoe UI", 12, "bold"),
                 bg=self.BG_DARK, fg=self.TEXT_MUTED).pack(anchor="w")

        restoran_list = self.db.get_semua_restoran()
        if not restoran_list:
            tk.Label(center,
                     text="⚠️ Tidak ada restoran di database.\nJalankan seed_data.py terlebih dahulu.",
                     font=("Segoe UI", 11), bg=self.BG_DARK, fg="#ef4444",
                     justify="center").pack(pady=16)
            return

        names = [r['nama'] for r in restoran_list]
        self.restoran_var = tk.StringVar(value=names[0])
        self.restoran_data = {r['nama']: r for r in restoran_list}

        combo = ttk.Combobox(center, textvariable=self.restoran_var,
                             values=names, state="readonly",
                             font=("Segoe UI", 12), width=40)
        combo.pack(pady=(8, 0), ipady=6)

        tk.Frame(center, bg=self.ACCENT, height=1).pack(fill="x", pady=2)

        # Nama kasir
        tk.Label(center, text="Nama Kasir:",
                 font=("Segoe UI", 12, "bold"),
                 bg=self.BG_DARK, fg=self.TEXT_MUTED).pack(anchor="w", pady=(16, 0))

        self.nama_var = tk.StringVar(value="Admin Kasir")
        nama_entry = tk.Entry(center, textvariable=self.nama_var,
                              font=("Segoe UI", 12),
                              bg=self.INPUT_BG, fg=self.TEXT_PRIMARY,
                              insertbackground=self.ACCENT,
                              relief="flat", bd=0)
        nama_entry.pack(fill="x", pady=(8, 0), ipady=10)
        tk.Frame(center, bg=self.ACCENT, height=2).pack(fill="x")

        # Tombol masuk
        tk.Button(
            center, text="🚀  Masuk ke Dashboard",
            command=self.masuk,
            bg=self.ACCENT, fg="#0d0d18",
            font=("Segoe UI", 13, "bold"),
            relief="flat", bd=0, pady=14,
            cursor="hand2",
            activebackground="#ea580c",
            activeforeground=self.TEXT_WHITE
        ).pack(fill="x", pady=(24, 0))

    def masuk(self):
        """Memproses pilihan restoran dan navigasi ke dashboard."""
        restoran_nama = self.restoran_var.get()
        nama_kasir = self.nama_var.get().strip()

        if not nama_kasir:
            messagebox.showwarning("Nama Kosong", "Masukkan nama kasir terlebih dahulu!")
            return

        restoran = self.restoran_data.get(restoran_nama)
        if not restoran:
            messagebox.showerror("Error", "Restoran tidak valid!")
            return

        self.controller.masuk_dashboard(restoran, nama_kasir)


# ============================================================
# APLIKASI UTAMA RESTAURANT APP
# ============================================================
class RestaurantApp(tk.Tk):
    """
    Controller utama Restaurant App.
    Mengelola navigasi antara halaman login dan dashboard.
    """

    def __init__(self):
        super().__init__()

        # ---- Inisialisasi Database ----
        self.db = DatabaseManager()
        seed()

        # ---- Placeholder kasir (dibuat setelah login) ----
        self.kasir = None
        self.restoran = None

        # ---- Konfigurasi Window ----
        self.title("RestaurantOS -- Manajemen Pesanan")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(bg="#f4f1ea")

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.winfo_screenheight() // 2) - (750 // 2)
        self.geometry(f"1200x750+{x}+{y}")

        # ---- Setup ttk styles ----
        self._setup_ttk_styles()

        # ---- Container ----
        self.container = tk.Frame(self, bg="#f4f1ea")
        self.container.pack(fill="both", expand=True)

        # ---- Tampilkan login screen ----
        self.login_frame = LoginFrame(self.container, self)
        self.login_frame.place(relwidth=1, relheight=1)

        self.dashboard_frame = None

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_ttk_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TScrollbar",
                        background="#d1cec7",
                        troughcolor="#f4f1ea",
                        arrowcolor="#808a8d",
                        borderwidth=0)
        style.configure("TCombobox",
                        fieldbackground="#ffffff",
                        background="#ffffff",
                        foreground="#3a4042",
                        selectbackground="#e09f3e",
                        selectforeground="#ffffff")
        style.map("TCombobox",
                  fieldbackground=[("readonly", "#ffffff")],
                  foreground=[("readonly", "#3a4042")])

    def masuk_dashboard(self, restoran: dict, nama_kasir: str):
        """Membuat Kasir dan masuk ke dashboard utama."""
        # Buat objek Kasir (implementasi Abstraksi)
        self.kasir = Kasir(nama=nama_kasir, app_root=self)
        self.kasir.tampilkan_dashboard()
        self.restoran = restoran

        # Update window title
        self.title(f"RestaurantOS -- {restoran['nama']}")

        # Buat dashboard frame
        if self.dashboard_frame:
            self.dashboard_frame.stop_polling()
            self.dashboard_frame.destroy()

        self.dashboard_frame = RestaurantDashboard(self.container, self)
        self.dashboard_frame.place(relwidth=1, relheight=1)
        self.dashboard_frame.tkraise()

    def logout(self):
        """Logout dari dashboard dan kembali ke halaman login."""
        from tkinter import messagebox
        if messagebox.askyesno("Konfirmasi", "Yakin ingin ganti akun (logout)?"):
            if self.dashboard_frame:
                self.dashboard_frame.stop_polling()
                self.dashboard_frame.destroy()
                self.dashboard_frame = None

            self.kasir = None
            self.restoran = None
            self.title("RestaurantOS -- Manajemen Pesanan")
            
            # Kembali ke frame login
            self.login_frame.tkraise()

    def on_close(self):
        """Handle window close — stop semua polling."""
        if self.dashboard_frame and hasattr(self.dashboard_frame, 'stop_polling'):
            self.dashboard_frame.stop_polling()
        self.destroy()


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  RestaurantOS -- Restaurant App")
    print("  Sistem Manajemen Pesanan Restoran")
    print("  UAS Pemrograman Berorientasi Objek")
    print("=" * 50)
    app = RestaurantApp()
    app.mainloop()
