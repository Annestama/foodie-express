"""
user_views.py — Semua Frame/Halaman untuk User App (Tkinter UI)

Berisi 5 halaman utama:
1. DashboardFrame  — Katalog restoran + search
2. MenuFrame       — Daftar menu restoran terpilih
3. KeranjangFrame  — Rekapitulasi pesanan & checkout
4. RiwayatFrame    — Riwayat semua pesanan + status real-time (polling 5 detik)
5. LacakFrame      — Tracking satu pesanan spesifik (dipakai dari RiwayatFrame)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from models.item_menu import buat_item_dari_db
from models.keranjang import KeranjangBelanja


# ============================================================
# KONSTANTA WARNA & STYLE (Lively Light Theme — User App)
# ============================================================
BG_DARK       = "#f4f1ea"  # Soft cream/beige
BG_CARD       = "#faf9f6"  # Off-white card
BG_CARD2      = "#ebe7dd"  # Slightly darker header
BG_CARD3      = "#dfdad0"  
ACCENT_GREEN  = "#6b9080"  # Soft Matcha green
ACCENT_PURPLE = "#a594f9"  # Soft Lavender
ACCENT_CYAN   = "#73a5c6"  # Soft blue
TEXT_PRIMARY  = "#3a4042"  # Soft charcoal
TEXT_MUTED    = "#808a8d"  
TEXT_WHITE    = "#ffffff"  
BORDER_COLOR  = "#d1cec7"  
SUCCESS_COLOR = "#6b9080"
WARNING_COLOR = "#e09f3e"
DANGER_COLOR  = "#e56b6f"
INPUT_BG      = "#faf9f6"
HOVER_COLOR   = "#f2efe9"

FONT_TITLE  = ("Segoe UI", 20, "bold")
FONT_HEADER = ("Segoe UI", 14, "bold")
FONT_BODY   = ("Segoe UI", 11)
FONT_SMALL  = ("Segoe UI", 9)
FONT_BOLD   = ("Segoe UI", 11, "bold")
FONT_LARGE  = ("Segoe UI", 16, "bold")
FONT_GIANT  = ("Segoe UI", 26, "bold")

STATUS_COLORS = {
    "Menunggu Konfirmasi": WARNING_COLOR,
    "Dikonfirmasi":        ACCENT_CYAN,
    "Diproses":            ACCENT_PURPLE,
    "Dikirim":             SUCCESS_COLOR,
    "Pesanan Selesai":     "#6b7280",
}


def styled_button(parent, text, command, bg=ACCENT_GREEN, fg=BG_DARK,
                  font_=FONT_BOLD, padx=20, pady=8, width=None, state="normal"):
    kwargs = dict(
        text=text, command=command,
        bg=bg, fg=fg, font=font_,
        relief="flat", cursor="hand2",
        padx=padx, pady=pady,
        activebackground=ACCENT_PURPLE, activeforeground=TEXT_WHITE,
        bd=0, state=state
    )
    if width:
        kwargs['width'] = width
    return tk.Button(parent, **kwargs)


def bind_mousewheel(widget, canvas):
    """Bind scroll mousewheel ke widget dan semua child-nya secara rekursif."""
    def _scroll(event):
        bbox = canvas.bbox("all")
        if bbox and (bbox[3] - bbox[1]) > canvas.winfo_height():
            canvas.yview_scroll(-1 * (event.delta // 120), "units")
    widget.bind("<MouseWheel>", _scroll)
    for child in widget.winfo_children():
        bind_mousewheel(child, canvas)


# ============================================================
# FRAME AUTH: LOGIN & REGISTER
# ============================================================
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.db = controller.db
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=BG_DARK)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="FoodOrder", font=FONT_GIANT, bg=BG_DARK, fg=ACCENT_GREEN).pack(pady=(0, 10))
        tk.Label(container, text="Login Pelanggan", font=FONT_TITLE, bg=BG_DARK, fg=TEXT_PRIMARY).pack(pady=(0, 30))

        tk.Label(container, text="Username", font=FONT_BOLD, bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w")
        self.username_var = tk.StringVar()
        entry_usr = tk.Entry(container, textvariable=self.username_var, font=FONT_BODY,
                             bg=INPUT_BG, fg=TEXT_PRIMARY, insertbackground=ACCENT_GREEN, relief="flat", bd=0)
        entry_usr.pack(fill="x", pady=(4, 15), ipady=8)

        tk.Label(container, text="Password", font=FONT_BOLD, bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w")
        self.password_var = tk.StringVar()
        entry_pwd = tk.Entry(container, textvariable=self.password_var, show="*", font=FONT_BODY,
                             bg=INPUT_BG, fg=TEXT_PRIMARY, insertbackground=ACCENT_GREEN, relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_GREEN)
        entry_pwd.pack(fill="x", pady=(4, 5), ipady=8)

        self.show_pwd_var = tk.BooleanVar(value=False)
        def toggle_pwd():
            entry_pwd.config(show="" if self.show_pwd_var.get() else "*")
            
        tk.Checkbutton(container, text="Show Password", variable=self.show_pwd_var, command=toggle_pwd,
                       bg=BG_DARK, fg=TEXT_MUTED, activebackground=BG_DARK, activeforeground=TEXT_MUTED,
                       selectcolor=BG_DARK, font=FONT_SMALL, relief="flat", bd=0).pack(anchor="w", pady=(0, 15))

        styled_button(container, text="Login", command=self.do_login, bg=ACCENT_PURPLE, fg=TEXT_WHITE, width=20).pack(fill="x", pady=(0, 15))

        btn_reg = tk.Label(container, text="Belum punya akun? Daftar di sini", font=FONT_BODY, bg=BG_DARK, fg=ACCENT_CYAN, cursor="hand2")
        btn_reg.pack()
        btn_reg.bind("<Button-1>", lambda e: self.controller.show_frame("RegisterFrame"))

    def do_login(self):
        usr = self.username_var.get().strip()
        pwd = self.password_var.get().strip()
        if not usr or not pwd:
            messagebox.showwarning("Peringatan", "Username dan password harus diisi!")
            return
        
        user_data = self.db.authenticate_user(usr, pwd)
        if user_data:
            self.controller.on_login_success(user_data)
        else:
            messagebox.showerror("Gagal", "Username atau password salah!")

class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.db = controller.db
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=BG_DARK)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Daftar Akun Baru", font=FONT_TITLE, bg=BG_DARK, fg=TEXT_PRIMARY).pack(pady=(0, 30))

        tk.Label(container, text="Nama Lengkap", font=FONT_BOLD, bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w")
        self.nama_var = tk.StringVar()
        tk.Entry(container, textvariable=self.nama_var, font=FONT_BODY,
                 bg=INPUT_BG, fg=TEXT_PRIMARY, insertbackground=ACCENT_GREEN, relief="flat", bd=0).pack(fill="x", pady=(4, 15), ipady=8)

        tk.Label(container, text="Username", font=FONT_BOLD, bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w")
        self.username_var = tk.StringVar()
        tk.Entry(container, textvariable=self.username_var, font=FONT_BODY,
                 bg=INPUT_BG, fg=TEXT_PRIMARY, insertbackground=ACCENT_GREEN, relief="flat", bd=0).pack(fill="x", pady=(4, 15), ipady=8)

        tk.Label(container, text="Password", font=FONT_BOLD, bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w")
        self.password_var = tk.StringVar()
        entry_pwd = tk.Entry(container, textvariable=self.password_var, show="*", font=FONT_BODY,
                 bg=INPUT_BG, fg=TEXT_PRIMARY, insertbackground=ACCENT_GREEN, relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_GREEN)
        entry_pwd.pack(fill="x", pady=(4, 5), ipady=8)

        self.show_pwd_var = tk.BooleanVar(value=False)
        def toggle_pwd_reg():
            entry_pwd.config(show="" if self.show_pwd_var.get() else "*")
            
        tk.Checkbutton(container, text="Show Password", variable=self.show_pwd_var, command=toggle_pwd_reg,
                       bg=BG_DARK, fg=TEXT_MUTED, activebackground=BG_DARK, activeforeground=TEXT_MUTED,
                       selectcolor=BG_DARK, font=FONT_SMALL, relief="flat", bd=0).pack(anchor="w", pady=(0, 15))

        styled_button(container, text="Daftar", command=self.do_register, bg=SUCCESS_COLOR, fg=BG_DARK, width=20).pack(fill="x", pady=(0, 15))

        btn_log = tk.Label(container, text="Sudah punya akun? Login di sini", font=FONT_BODY, bg=BG_DARK, fg=ACCENT_CYAN, cursor="hand2")
        btn_log.pack()
        btn_log.bind("<Button-1>", lambda e: self.controller.show_frame("LoginFrame"))

    def do_register(self):
        nama = self.nama_var.get().strip()
        usr = self.username_var.get().strip()
        pwd = self.password_var.get().strip()
        
        if not nama or not usr or not pwd:
            messagebox.showwarning("Peringatan", "Semua kolom harus diisi!")
            return
            
        success = self.db.register_user(usr, pwd, nama)
        if success:
            messagebox.showinfo("Berhasil", "Akun berhasil didaftarkan. Silakan login.")
            self.controller.show_frame("LoginFrame")
        else:
            messagebox.showerror("Gagal", "Username sudah digunakan!")


# ============================================================
# FRAME 1: DASHBOARD (Katalog Restoran)
# ============================================================
class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.db = controller.db
        self.restoran_list = []
        self._build_ui()
        self.muat_restoran()

    def _build_ui(self):
        # HEADER
        header = tk.Frame(self, bg=BG_CARD2)
        header.pack(fill="x")
        tk.Frame(header, bg=ACCENT_GREEN, height=4).pack(fill="x")
        inner_header = tk.Frame(header, bg=BG_CARD2, padx=30, pady=16)
        inner_header.pack(fill="x")
        tk.Label(inner_header, text="FoodOrder", font=FONT_TITLE,
                 bg=BG_CARD2, fg=ACCENT_GREEN).pack(side="left")
        tk.Label(inner_header,
                 text=f"Selamat datang, {self.controller.pelanggan.nama}!",
                 font=FONT_BODY, bg=BG_CARD2, fg=TEXT_MUTED).pack(side="right")

        # Tombol Logout dan Riwayat di header
        styled_button(inner_header, "Logout",
                      command=lambda: self.controller.do_logout(),
                      bg=DANGER_COLOR, fg=TEXT_WHITE,
                      padx=14, pady=6).pack(side="right", padx=(0, 16))

        styled_button(inner_header, "Riwayat Pesanan",
                      command=lambda: self.controller.show_riwayat(),
                      bg=ACCENT_PURPLE, fg=TEXT_WHITE,
                      padx=14, pady=6).pack(side="right", padx=(0, 16))

        # HERO
        hero = tk.Frame(self, bg=BG_DARK, pady=24, padx=40)
        hero.pack(fill="x")
        tk.Label(hero, text="Pilih Restoran Favoritmu",
                 font=FONT_GIANT, bg=BG_DARK, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(hero, text="Temukan makanan lezat dari mitra restoran terpercaya kami",
                 font=FONT_BODY, bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        # SEARCH BAR
        sf = tk.Frame(self, bg=BG_DARK, padx=40)
        sf.pack(fill="x")
        sc = tk.Frame(sf, bg=INPUT_BG, padx=14, pady=10, highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_GREEN)
        sc.pack(fill="x")
        tk.Label(sc, text="[ Cari ]", font=FONT_SMALL, bg=INPUT_BG, fg=TEXT_MUTED).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.muat_restoran())
        self.search_entry = tk.Entry(sc, textvariable=self.search_var,
                                     font=FONT_BODY, bg=INPUT_BG, fg=TEXT_MUTED,
                                     insertbackground=ACCENT_GREEN, relief="flat", bd=0)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=8)
        self._placeholder_text = "Cari nama restoran..."
        self.search_entry.insert(0, self._placeholder_text)

        def on_focus_in(e):
            if self.search_entry.get() == self._placeholder_text:
                self.search_entry.delete(0, "end")
                self.search_entry.config(fg=TEXT_PRIMARY)
        def on_focus_out(e):
            if not self.search_entry.get().strip():
                self.search_entry.insert(0, self._placeholder_text)
                self.search_entry.config(fg=TEXT_MUTED)
                self.search_var.set("")
        self.search_entry.bind("<FocusIn>", on_focus_in)
        self.search_entry.bind("<FocusOut>", on_focus_out)

        # Separator + count
        tk.Frame(self, bg=BORDER_COLOR, height=1).pack(fill="x", padx=40, pady=(15, 0))
        self.count_label = tk.Label(self, text="", font=FONT_SMALL, bg=BG_DARK, fg=TEXT_MUTED)
        self.count_label.pack(anchor="w", padx=40, pady=(10, 4))

        # BOTTOM BAR — harus di-pack SEBELUM list_frame!
        bottom_bar = tk.Frame(self, bg=BG_CARD2, padx=40, pady=14)
        bottom_bar.pack(fill="x", side="bottom")

        self.btn_pilih = styled_button(
            bottom_bar, text="Lihat Menu Restoran",
            command=self.pilih_restoran,
            bg=ACCENT_GREEN, fg=TEXT_WHITE, padx=30, pady=12
        )
        self.btn_pilih.pack(side="right")
        self.btn_pilih.config(state="disabled")

        self.selected_label = tk.Label(bottom_bar, text="Belum ada restoran dipilih",
                                       font=FONT_BODY, bg=BG_CARD2, fg=TEXT_MUTED)
        self.selected_label.pack(side="left")

        # LIST RESTORAN — di-pack SETELAH bottom_bar
        list_frame = tk.Frame(self, bg=BG_DARK, padx=40)
        list_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(list_frame, bg=BG_DARK, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_DARK)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_win = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_win, width=e.width))
        # Mousewheel pada canvas
        bind_mousewheel(self.canvas, self.canvas)
        bind_mousewheel(self.scrollable_frame, self.canvas)

    def muat_restoran(self):
        if not hasattr(self, 'scrollable_frame'):
            return
        keyword = self.search_var.get()
        if keyword == self._placeholder_text:
            keyword = ""
        self.restoran_list = self.db.get_semua_restoran(keyword=keyword)

        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        if not self.restoran_list:
            f = tk.Frame(self.scrollable_frame, bg=BG_DARK, pady=50)
            f.pack(fill="x")
            tk.Label(f, text="Belum ada restoran yang terdaftar",
                     font=FONT_HEADER, bg=BG_DARK, fg=TEXT_MUTED).pack()
            self.count_label.config(text="0 restoran ditemukan")
            return

        self.count_label.config(text=f"{len(self.restoran_list)} restoran ditemukan")
        self.selected_id = None
        self.card_widgets = {}

        for idx, resto in enumerate(self.restoran_list):
            self._buat_card(resto, idx)

    def _buat_card(self, resto, idx):
        nama_lower = resto['nama'].lower()
        if 'padang' in nama_lower:
            icon_text = "[Padang]"
        elif 'kopi' in nama_lower or 'cafe' in nama_lower:
            icon_text = "[Kopi]"
        elif 'sushi' in nama_lower or 'jepang' in nama_lower:
            icon_text = "[Sushi]"
        elif 'mie' in nama_lower or 'bakmi' in nama_lower:
            icon_text = "[Mie]"
        elif 'pizza' in nama_lower:
            icon_text = "[Pizza]"
        else:
            icon_text = "[Resto]"

        card = tk.Frame(self.scrollable_frame, bg=BG_CARD, padx=24, pady=18, cursor="hand2")
        card.pack(fill="x", pady=(0, 8))

        indicator = tk.Frame(card, bg=BORDER_COLOR, width=4)
        indicator.place(x=0, y=0, relheight=1)

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill="x", padx=(12, 0))

        row1 = tk.Frame(inner, bg=BG_CARD)
        row1.pack(fill="x")
        tk.Label(row1, text=icon_text, font=FONT_SMALL, bg=BG_CARD, fg=ACCENT_GREEN).pack(side="left")
        arrow = tk.Label(row1, text="", font=FONT_BOLD, bg=BG_CARD, fg=TEXT_MUTED)
        arrow.pack(side="right")

        tk.Label(inner, text=resto['nama'], font=FONT_HEADER, bg=BG_CARD, fg=TEXT_PRIMARY, anchor="w").pack(fill="x")
        desc = resto.get('deskripsi', '') or "Klik untuk melihat menu"
        tk.Label(inner, text=desc, font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED, anchor="w").pack(fill="x")

        self.card_widgets[resto['id']] = {'card': card, 'indicator': indicator, 'arrow': arrow}

        # Bind click & scroll pada semua widget dalam card
        def on_click(e, rid=resto['id']):
            self.select_restoran(rid)
        def on_enter(e, c=card, ind=indicator):
            c.config(bg=HOVER_COLOR)
            ind.config(bg=ACCENT_GREEN)
        def on_leave(e, c=card, ind=indicator, rid=resto['id']):
            c.config(bg=BG_CARD)
            ind.config(bg=ACCENT_GREEN if (hasattr(self, 'selected_id') and self.selected_id == rid) else BORDER_COLOR)
        def _safe_scroll(event):
            bbox = self.canvas.bbox("all")
            if bbox and (bbox[3] - bbox[1]) > self.canvas.winfo_height():
                self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

        for w in [card, inner, row1] + list(inner.winfo_children()) + list(row1.winfo_children()):
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<MouseWheel>", _safe_scroll)

    def select_restoran(self, rid):
        self.selected_id = rid
        for r_id, widgets in self.card_widgets.items():
            is_sel = (r_id == rid)
            widgets['card'].config(bg=BG_CARD2 if is_sel else BG_CARD)
            widgets['indicator'].config(bg=ACCENT_GREEN if is_sel else BORDER_COLOR)
            widgets['arrow'].config(fg=ACCENT_GREEN if is_sel else TEXT_MUTED)
        nama = next((r['nama'] for r in self.restoran_list if r['id'] == rid), "")
        self.selected_label.config(text=f"{nama} dipilih", fg=ACCENT_GREEN)
        self.btn_pilih.config(state="normal")

    def pilih_restoran(self):
        if not hasattr(self, 'selected_id') or not self.selected_id:
            messagebox.showwarning("Pilih Restoran", "Silakan pilih restoran terlebih dahulu!")
            return
        self.controller.show_menu(self.selected_id)


# ============================================================
# FRAME 2: MENU RESTORAN
# ============================================================
class MenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.db = controller.db
        self.restoran_id = None
        self.restoran_nama = ""
        self.menu_items = []
        self.qty_vars = {}

    def load(self, restoran_id):
        self.restoran_id = restoran_id
        resto = self.db.get_restoran_by_id(restoran_id)
        self.restoran_nama = resto['nama'] if resto else "Restoran"
        rows = self.db.get_menu_by_restoran(restoran_id)
        self.menu_items = [buat_item_dari_db(row) for row in rows]
        self.qty_vars = {}
        self._build_ui()

    def _build_ui(self):
        for w in self.winfo_children():
            w.destroy()

        # HEADER
        header = tk.Frame(self, bg=BG_CARD2)
        header.pack(fill="x")
        tk.Frame(header, bg=ACCENT_GREEN, height=4).pack(fill="x")
        inner = tk.Frame(header, bg=BG_CARD2, padx=30, pady=14)
        inner.pack(fill="x")
        tk.Button(inner, text="< Kembali", font=FONT_BODY,
                  bg=BG_CARD2, fg=TEXT_MUTED, relief="flat", cursor="hand2", bd=0,
                  command=lambda: self.controller.show_frame("DashboardFrame"),
                  activebackground=BG_CARD2, activeforeground=ACCENT_GREEN).pack(side="left")
        tk.Label(inner, text=f"  {self.restoran_nama}",
                 font=FONT_TITLE, bg=BG_CARD2, fg=TEXT_PRIMARY).pack(side="left", padx=16)
        total_in_cart = self.controller.keranjang.total_qty()
        self.badge_label = tk.Label(inner, text=f"Keranjang: {total_in_cart} item",
                                    font=FONT_BODY, bg=BG_CARD2, fg=TEXT_MUTED if total_in_cart == 0 else ACCENT_GREEN)
        self.badge_label.pack(side="right")

        # BOTTOM BAR — pack sebelum scrollable content
        bottom = tk.Frame(self, bg=BG_CARD2, padx=30, pady=14)
        bottom.pack(fill="x", side="bottom")
        styled_button(bottom, "Lihat Keranjang",
                      command=self.ke_keranjang,
                      bg=ACCENT_PURPLE, fg=TEXT_WHITE, padx=30, pady=12).pack(side="right")

        # SCROLLABLE MENU
        container = tk.Frame(self, bg=BG_DARK, padx=30, pady=16)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=BG_DARK, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_DARK)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_win = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_win, width=e.width))

        # Mousewheel — bind ke canvas & scroll_frame
        scroll_cb = lambda e: canvas.yview_scroll(-1*(e.delta//120), "units")
        canvas.bind("<MouseWheel>", scroll_cb)
        scroll_frame.bind("<MouseWheel>", scroll_cb)

        if not self.menu_items:
            tk.Label(scroll_frame, text="Menu belum tersedia",
                     font=FONT_HEADER, bg=BG_DARK, fg=TEXT_MUTED).pack(pady=60)
            return

        self._canvas_ref = canvas
        makanan = [m for m in self.menu_items if m.tipe == "makanan"]
        minuman = [m for m in self.menu_items if m.tipe == "minuman"]

        if makanan:
            self._section(scroll_frame, "Menu Makanan")
            for item in makanan:
                self._buat_menu_row(scroll_frame, item, canvas)
        if minuman:
            self._section(scroll_frame, "Menu Minuman")
            for item in minuman:
                self._buat_menu_row(scroll_frame, item, canvas)

    def _section(self, parent, text):
        tk.Label(parent, text=text, font=FONT_HEADER, bg=BG_DARK, fg=ACCENT_GREEN).pack(anchor="w", pady=(14, 6))
        tk.Frame(parent, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(0, 8))

    def _buat_menu_row(self, parent, item, canvas):
        scroll_cb = lambda e: canvas.yview_scroll(-1*(e.delta//120), "units")
        row = tk.Frame(parent, bg=BG_CARD, padx=20, pady=14)
        row.pack(fill="x", pady=(0, 6))
        row.bind("<MouseWheel>", scroll_cb)

        info = tk.Frame(row, bg=BG_CARD)
        info.pack(side="left", fill="both", expand=True)
        info.bind("<MouseWheel>", scroll_cb)

        # Polimorfisme: tampilkan_info() output berbeda untuk Makanan vs Minuman
        lbl_info = tk.Label(info, text=item.tampilkan_info(), font=FONT_BOLD,
                            bg=BG_CARD, fg=TEXT_PRIMARY, anchor="w")
        lbl_info.pack(fill="x")
        lbl_info.bind("<MouseWheel>", scroll_cb)

        lbl_harga = tk.Label(info, text=f"Rp{item.harga:,.0f}", font=FONT_BODY,
                             bg=BG_CARD, fg=ACCENT_GREEN, anchor="w")
        lbl_harga.pack(fill="x", pady=(2, 0))
        lbl_harga.bind("<MouseWheel>", scroll_cb)

        qty_frame = tk.Frame(row, bg=BG_CARD)
        qty_frame.pack(side="right")

        current_qty = 0
        for cart_item in self.controller.keranjang.get_items():
            if cart_item['menu_id'] == item.id:
                current_qty = cart_item['qty']
                break

        qty_var = tk.IntVar(value=current_qty)
        self.qty_vars[item.id] = qty_var

        def validate_qty(val):
            if val == "":
                return True
            try:
                return int(val) >= 0
            except ValueError:
                return False

        vcmd = (self.register(validate_qty), '%P')

        def on_qty_change(v, delta):
            new_val = v.get() + delta
            if new_val < 0: new_val = 0
            if new_val > 99: new_val = 99
            v.set(new_val)
            self.update_cart_qty(item, new_val)

        tk.Button(qty_frame, text="-", font=FONT_BOLD, bg=INPUT_BG, fg=TEXT_PRIMARY,
                  relief="flat", cursor="hand2", width=3, pady=4,
                  command=lambda v=qty_var: on_qty_change(v, -1),
                  activebackground=DANGER_COLOR, activeforeground=TEXT_WHITE).pack(side="left")

        qty_entry = tk.Entry(qty_frame, textvariable=qty_var, width=4, font=FONT_BOLD,
                             justify="center", bg=INPUT_BG, fg=TEXT_PRIMARY, relief="flat", bd=0,
                             validate="key", validatecommand=vcmd)
        qty_entry.pack(side="left", padx=4)

        def on_entry_change(event=None):
            try:
                new_val = int(qty_var.get())
            except ValueError:
                new_val = 0
            self.update_cart_qty(item, new_val)

        qty_entry.bind("<FocusOut>", on_entry_change)
        qty_entry.bind("<Return>", on_entry_change)

        tk.Button(qty_frame, text="+", font=FONT_BOLD, bg=INPUT_BG, fg=TEXT_PRIMARY,
                  relief="flat", cursor="hand2", width=3, pady=4,
                  command=lambda v=qty_var: on_qty_change(v, 1),
                  activebackground=SUCCESS_COLOR, activeforeground=BG_DARK).pack(side="left")

    def update_cart_qty(self, item, qty_baru):
        success = self.controller.keranjang.edit_qty(item.id, qty_baru)
        if not success and qty_baru > 0:
            self.controller.keranjang.tambah_item(item.id, item.nama, item.harga, qty_baru, item.tipe)
        
        total = self.controller.keranjang.total_qty()
        self.badge_label.config(text=f"Keranjang: {total} item", fg=TEXT_MUTED if total == 0 else ACCENT_GREEN)

    def ke_keranjang(self):
        if self.controller.keranjang.is_kosong():
            messagebox.showinfo("Keranjang Kosong", "Tambahkan item terlebih dahulu!")
            return
        self.controller.show_frame("KeranjangFrame")


# ============================================================
# FRAME 3: KERANJANG BELANJA & CHECKOUT
# ============================================================
class KeranjangFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.db = controller.db

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build_ui()

    def _build_ui(self):
        keranjang = self.controller.keranjang

        # HEADER
        header = tk.Frame(self, bg=BG_CARD2)
        header.pack(fill="x")
        tk.Frame(header, bg=ACCENT_PURPLE, height=4).pack(fill="x")
        inner = tk.Frame(header, bg=BG_CARD2, padx=30, pady=14)
        inner.pack(fill="x")
        tk.Button(inner, text="< Kembali ke Menu", font=FONT_BODY,
                  bg=BG_CARD2, fg=TEXT_MUTED, relief="flat", cursor="hand2", bd=0,
                  command=lambda: self.controller.show_frame("MenuFrame"),
                  activebackground=BG_CARD2, activeforeground=ACCENT_GREEN).pack(side="left")
        tk.Label(inner, text="  Keranjang Belanja", font=FONT_TITLE,
                 bg=BG_CARD2, fg=TEXT_PRIMARY).pack(side="left", padx=16)

        # BOTTOM BAR — pack sebelum table!
        bottom = tk.Frame(self, bg=BG_CARD2, padx=40, pady=14)
        bottom.pack(fill="x", side="bottom")

        has_items = not keranjang.is_kosong()
        self.btn_checkout = styled_button(
            bottom, text="Konfirmasi Checkout",
            command=self.checkout,
            bg=SUCCESS_COLOR if has_items else "#374151",
            fg=TEXT_WHITE, padx=30, pady=12,
            state="normal" if has_items else "disabled"
        )
        self.btn_checkout.pack(side="right")

        styled_button(bottom, text="Hapus Semua",
                      command=self.kosongkan_keranjang,
                      bg=DANGER_COLOR, fg=TEXT_WHITE, padx=20, pady=12).pack(side="right", padx=(0, 10))

        # TABEL
        tk.Label(self, text="Rincian Pesanan", font=FONT_HEADER,
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(anchor="w", padx=40, pady=(16, 6))

        table_frame = tk.Frame(self, bg=BG_DARK, padx=40)
        table_frame.pack(fill="both", expand=True)

        # Header kolom
        hrow = tk.Frame(table_frame, bg=BG_CARD2, padx=16, pady=8)
        hrow.pack(fill="x")
        for col, w in [("Nama Menu", 36), ("Qty", 8), ("Subtotal", 14), ("", 8)]:
            tk.Label(hrow, text=col, font=FONT_BOLD, bg=BG_CARD2,
                     fg=TEXT_MUTED, width=w, anchor="w").pack(side="left")

        # Scrollable rows
        canvas = tk.Canvas(table_frame, bg=BG_DARK, bd=0, highlightthickness=0, height=240)
        sf = tk.Frame(canvas, bg=BG_DARK)
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        scroll_cb = lambda e: canvas.yview_scroll(-1*(e.delta//120), "units")
        canvas.bind("<MouseWheel>", scroll_cb)
        sf.bind("<MouseWheel>", scroll_cb)

        if keranjang.is_kosong():
            tk.Label(sf, text="Keranjang kosong — tambah item dari menu!",
                     font=FONT_BODY, bg=BG_DARK, fg=TEXT_MUTED).pack(pady=30)
        else:
            for item in keranjang.get_items():
                self._buat_item_row(sf, item, scroll_cb)

        # GRAND TOTAL
        tf = tk.Frame(self, bg=BG_CARD, padx=40, pady=14)
        tf.pack(fill="x")
        tk.Label(tf, text="Grand Total:", font=FONT_HEADER, bg=BG_CARD, fg=TEXT_MUTED).pack(side="left")
        tk.Label(tf, text=keranjang.format_grand_total(),
                 font=FONT_LARGE, bg=BG_CARD, fg=ACCENT_GREEN).pack(side="right")

    def _buat_item_row(self, parent, item, scroll_cb):
        row = tk.Frame(parent, bg=BG_CARD, padx=16, pady=10)
        row.pack(fill="x", pady=(0, 2))
        row.bind("<MouseWheel>", scroll_cb)

        tk.Label(row, text=item['nama'], font=FONT_BODY, bg=BG_CARD,
                 fg=TEXT_PRIMARY, width=36, anchor="w").pack(side="left")

        qty_var = tk.IntVar(value=item['qty'])
        qty_entry = tk.Entry(row, textvariable=qty_var, width=5, font=FONT_BODY,
                             justify="center", bg=INPUT_BG, fg=TEXT_PRIMARY, relief="flat", bd=0)
        qty_entry.pack(side="left")

        subtotal_var = tk.StringVar(value=f"Rp{item['subtotal']:,.0f}")
        tk.Label(row, textvariable=subtotal_var, font=FONT_BODY, bg=BG_CARD,
                 fg=ACCENT_GREEN, width=14, anchor="w").pack(side="left")

        def update_qty(event=None, mid=item['menu_id'], qv=qty_var, sv=subtotal_var, h=item['harga']):
            try:
                new_qty = int(qv.get())
            except (ValueError, tk.TclError):
                return
            self.controller.keranjang.edit_qty(mid, new_qty)
            if new_qty > 0:
                sv.set(f"Rp{h * new_qty:,.0f}")
            else:
                self.refresh()

        qty_entry.bind("<FocusOut>", update_qty)
        qty_entry.bind("<Return>", update_qty)

        styled_button(row, "Hapus",
                      command=lambda mid=item['menu_id']: self.hapus_item(mid),
                      bg=DANGER_COLOR, fg=TEXT_WHITE, padx=10, pady=4).pack(side="left", padx=(8, 0))

    def hapus_item(self, menu_id):
        self.controller.keranjang.hapus_item(menu_id)
        self.refresh()

    def kosongkan_keranjang(self):
        if messagebox.askyesno("Hapus Semua", "Yakin ingin mengosongkan keranjang?"):
            self.controller.keranjang.kosongkan()
            self.refresh()

    def checkout(self):
        if self.controller.keranjang.is_kosong():
            messagebox.showwarning("Kosong", "Keranjang masih kosong!")
            return
        nama = self.controller.pelanggan.nama

        items = self.controller.keranjang.get_items()
        pesanan_id = self.db.buat_pesanan(
            restoran_id=self.controller.current_restoran_id,
            nama_pemesan=nama,
            items=items
        )
        self.controller.keranjang.kosongkan()
        # Simpan nama pemesan ke controller untuk query riwayat
        self.controller.nama_pemesan = nama

        messagebox.showinfo("Pesanan Dikirim!",
                            f"Pesanan berhasil dikirim!\nID: #{pesanan_id}\n\n"
                            f"Cek status di halaman Riwayat Pesanan.")
        # Arahkan ke halaman riwayat pesanan
        self.controller.show_riwayat()


# ============================================================
# FRAME 4: RIWAYAT PESANAN (Semua order + real-time tracking)
# ============================================================
class RiwayatFrame(tk.Frame):
    """
    Halaman riwayat semua pesanan user.
    Polling 5 detik untuk update status semua pesanan yang masih aktif.
    Menampilkan detail setiap pesanan dan tombol konfirmasi untuk status 'Dikirim'.
    """

    STATUS_LABELS = {
        "Menunggu Konfirmasi": "Menunggu Konfirmasi",
        "Dikonfirmasi":        "Dikonfirmasi",
        "Diproses":            "Sedang Dimasak",
        "Dikirim":             "Sedang Dikirim",
        "Pesanan Selesai":     "Selesai",
    }

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.db = controller.db
        self._polling_job = None
        self._expanded = {}  # {pesanan_id: bool} untuk toggle detail
        self._last_pesanan_data = None

    def refresh(self):
        """Dipanggil dari controller setiap kali frame ini ditampilkan."""
        self.stop_polling()
        self._expanded = {}
        self._last_pesanan_data = None
        self._build_ui()
        self._mulai_polling()

    def _build_ui(self):
        for w in self.winfo_children():
            w.destroy()

        # HEADER
        header = tk.Frame(self, bg=BG_CARD2)
        header.pack(fill="x")
        tk.Frame(header, bg=ACCENT_CYAN, height=4).pack(fill="x")
        inner = tk.Frame(header, bg=BG_CARD2, padx=30, pady=14)
        inner.pack(fill="x")

        tk.Button(inner, text="< Pesan Lagi", font=FONT_BODY,
                  bg=BG_CARD2, fg=TEXT_MUTED, relief="flat", cursor="hand2", bd=0,
                  command=self._pesan_lagi,
                  activebackground=BG_CARD2, activeforeground=ACCENT_GREEN).pack(side="left")

        tk.Label(inner, text="  Riwayat Pesanan", font=FONT_TITLE,
                 bg=BG_CARD2, fg=TEXT_PRIMARY).pack(side="left", padx=16)

        self.poll_label = tk.Label(inner, text="Memuat...", font=FONT_SMALL,
                                   bg=BG_CARD2, fg=TEXT_MUTED)
        self.poll_label.pack(side="right")

        # INFO USER
        nama = getattr(self.controller, 'nama_pemesan', self.controller.pelanggan.nama)
        info_bar = tk.Frame(self, bg=BG_CARD, padx=30, pady=10)
        info_bar.pack(fill="x")
        tk.Label(info_bar, text=f"Pesanan atas nama: {nama}",
                 font=FONT_BOLD, bg=BG_CARD, fg=TEXT_PRIMARY).pack(side="left")

        # SCROLLABLE LIST
        container = tk.Frame(self, bg=BG_DARK, padx=30, pady=16)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=BG_DARK, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=BG_DARK)
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_win = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_win, width=e.width))

        scroll_cb = lambda e: self.canvas.yview_scroll(-1*(e.delta//120), "units")
        self.canvas.bind("<MouseWheel>", scroll_cb)
        self.scroll_frame.bind("<MouseWheel>", scroll_cb)
        self._scroll_cb = scroll_cb

        self._render_list()

    def _render_list(self, force=False):
        """Render ulang daftar pesanan (dipanggil juga oleh polling)."""
        nama = getattr(self.controller, 'nama_pemesan', self.controller.pelanggan.nama)
        pesanan_list = self.db.get_pesanan_by_pemesan(nama)

        if not force and hasattr(self, '_last_pesanan_data') and self._last_pesanan_data == pesanan_list:
            # Data belum berubah, hindari glitch dengan hanya mengupdate jam
            import datetime
            now = datetime.datetime.now().strftime("%H:%M:%S")
            if hasattr(self, 'poll_label') and self.poll_label.winfo_exists():
                self.poll_label.config(text=f"Auto-refresh | {now}")
            return
            
        self._last_pesanan_data = pesanan_list

        # Simpan scroll state
        scroll_pos = self.canvas.yview()

        for w in self.scroll_frame.winfo_children():
            w.destroy()


        if not pesanan_list:
            f = tk.Frame(self.scroll_frame, bg=BG_DARK, pady=60)
            f.pack(fill="x")
            f.bind("<MouseWheel>", self._scroll_cb)
            tk.Label(f, text="Belum ada pesanan.", font=FONT_HEADER,
                     bg=BG_DARK, fg=TEXT_MUTED).pack()
            tk.Label(f, text="Buat pesanan pertamamu sekarang!",
                     font=FONT_BODY, bg=BG_DARK, fg=BORDER_COLOR).pack(pady=(6, 0))
            return

        # Update poll label
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        if hasattr(self, 'poll_label') and self.poll_label.winfo_exists():
            self.poll_label.config(text=f"Auto-refresh | {now}")

        for pesanan in pesanan_list:
            self._buat_card_pesanan(pesanan)

        # Bind scroll pada semua children di scroll_frame
        self._rebind_scroll(self.scroll_frame)
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(scroll_pos[0])

    def _rebind_scroll(self, widget):
        """Bind mousewheel ke semua widget secara rekursif."""
        widget.bind("<MouseWheel>", self._scroll_cb)
        for child in widget.winfo_children():
            self._rebind_scroll(child)

    def _buat_card_pesanan(self, pesanan):
        status = pesanan['status']
        color = STATUS_COLORS.get(status, TEXT_MUTED)
        is_expanded = self._expanded.get(pesanan['id'], False)

        # Card utama
        card = tk.Frame(self.scroll_frame, bg=BG_CARD, padx=0, pady=0)
        card.pack(fill="x", pady=(0, 10))

        # Top bar: indicator + info
        top = tk.Frame(card, bg=BG_CARD, padx=20, pady=14)
        top.pack(fill="x")

        # Indicator warna kiri
        tk.Frame(card, bg=color, width=5).place(x=0, y=0, relheight=1)

        inner_top = tk.Frame(top, bg=BG_CARD)
        inner_top.pack(fill="x", padx=(8, 0))

        # Baris 1: ID + badge status
        row1 = tk.Frame(inner_top, bg=BG_CARD)
        row1.pack(fill="x")
        tk.Label(row1, text=f"Pesanan #{pesanan['id']}  |  {pesanan.get('restoran_nama', '')}",
                 font=FONT_BOLD, bg=BG_CARD, fg=TEXT_PRIMARY).pack(side="left")

        badge = tk.Label(row1, text=self.STATUS_LABELS.get(status, status),
                         font=FONT_SMALL, bg=color, fg=BG_DARK, padx=8, pady=3)
        badge.pack(side="right")

        # Baris 2: waktu + total
        waktu = pesanan.get('waktu', '')[:16]
        total = sum(i['subtotal'] for i in pesanan.get('items', []))
        row2 = tk.Frame(inner_top, bg=BG_CARD)
        row2.pack(fill="x", pady=(4, 0))
        tk.Label(row2, text=f"{waktu}",
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED).pack(side="left")
        tk.Label(row2, text=f"Rp{total:,.0f}",
                 font=FONT_BOLD, bg=BG_CARD, fg=ACCENT_GREEN).pack(side="right")

        # Baris 3: tombol expand + konfirmasi selesai
        row3 = tk.Frame(inner_top, bg=BG_CARD)
        row3.pack(fill="x", pady=(10, 0))

        expand_text = "[ - Sembunyikan Detail ]" if is_expanded else "[ + Lihat Detail ]"
        btn_expand = tk.Button(row3, text=expand_text, font=FONT_SMALL,
                               bg=BG_CARD, fg=ACCENT_CYAN, relief="flat",
                               cursor="hand2", bd=0,
                               command=lambda pid=pesanan['id']: self._toggle_detail(pid))
        btn_expand.pack(side="left")

        # Tombol Konfirmasi Selesai — hanya aktif jika status == "Dikirim"
        if status == "Dikirim":
            styled_button(row3, "Konfirmasi Pesanan Diterima",
                          command=lambda pid=pesanan['id']: self._konfirmasi_selesai(pid),
                          bg=SUCCESS_COLOR, fg=TEXT_WHITE,
                          padx=16, pady=5).pack(side="right")
        elif status == "Pesanan Selesai":
            tk.Label(row3, text="Pesanan telah selesai",
                     font=FONT_SMALL, bg=BG_CARD, fg="#6b7280").pack(side="right")
        else:
            tk.Label(row3,
                     text=f"Menunggu restoran update status...",
                     font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED).pack(side="right")

        # Detail panel (collapsible)
        if is_expanded:
            detail = tk.Frame(card, bg=BG_CARD3, padx=28, pady=12)
            detail.pack(fill="x")
            tk.Frame(detail, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(0, 10))

            # Header kolom
            h = tk.Frame(detail, bg=BG_CARD3)
            h.pack(fill="x")
            tk.Label(h, text="Menu", font=FONT_BOLD, bg=BG_CARD3,
                     fg=TEXT_MUTED, width=30, anchor="w").pack(side="left")
            tk.Label(h, text="Qty", font=FONT_BOLD, bg=BG_CARD3,
                     fg=TEXT_MUTED, width=6, anchor="w").pack(side="left")
            tk.Label(h, text="Subtotal", font=FONT_BOLD, bg=BG_CARD3,
                     fg=TEXT_MUTED, width=14, anchor="w").pack(side="left")

            for item in pesanan.get('items', []):
                ir = tk.Frame(detail, bg=BG_CARD3)
                ir.pack(fill="x", pady=(4, 0))
                tk.Label(ir, text=item['nama_menu'], font=FONT_BODY,
                         bg=BG_CARD3, fg=TEXT_PRIMARY, width=30, anchor="w").pack(side="left")
                tk.Label(ir, text=f"x{item['qty']}", font=FONT_BODY,
                         bg=BG_CARD3, fg=TEXT_MUTED, width=6, anchor="w").pack(side="left")
                tk.Label(ir, text=f"Rp{item['subtotal']:,.0f}", font=FONT_BOLD,
                         bg=BG_CARD3, fg=ACCENT_GREEN, width=14, anchor="w").pack(side="left")

            tk.Frame(detail, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(12, 4))
            total_row = tk.Frame(detail, bg=BG_CARD3)
            total_row.pack(fill="x")
            tk.Label(total_row, text="Total:", font=FONT_HEADER,
                     bg=BG_CARD3, fg=TEXT_MUTED).pack(side="left")
            tk.Label(total_row, text=f"Rp{total:,.0f}",
                     font=FONT_LARGE, bg=BG_CARD3, fg=ACCENT_GREEN).pack(side="right")

            # Status timeline & timestamps
            tk.Frame(detail, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(10, 8))
            from models.pesanan import Pesanan
            flow = Pesanan.STATUS_FLOW
            timeline_container = tk.Frame(detail, bg=BG_CARD3)
            timeline_container.pack(fill="x")
            
            tk.Label(timeline_container, text="Jejak Status:", font=FONT_BOLD, bg=BG_CARD3, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 4))
            
            ts_data = {
                "Dikonfirmasi": pesanan.get('waktu_dikonfirmasi'),
                "Diproses": pesanan.get('waktu_diproses'),
                "Dikirim": pesanan.get('waktu_dikirim'),
                "Pesanan Selesai": pesanan.get('waktu_selesai')
            }
            
            try:
                cur_idx = flow.index(status)
            except ValueError:
                cur_idx = 0
                
            for i, s in enumerate(flow):
                s_short = s.replace("Konfirmasi", "Konfirm.").replace("Pesanan ", "")
                c = SUCCESS_COLOR if i < cur_idx else (color if i == cur_idx else BORDER_COLOR)
                fg_c = BG_DARK if c not in [BORDER_COLOR, TEXT_MUTED] else TEXT_MUTED
                
                row_status = tk.Frame(timeline_container, bg=BG_CARD3)
                row_status.pack(fill="x", pady=(0, 2))
                
                # Kotak status
                lbl = tk.Label(row_status, text=s_short, font=FONT_SMALL,
                               bg=c, fg=fg_c, padx=6, pady=2, width=15)
                lbl.pack(side="left")
                
                # Timestamp
                ts = ts_data.get(s)
                if not ts and s == "Menunggu Konfirmasi":
                    ts = pesanan.get('waktu')  # Waktu pesanan dibuat
                    
                ts_text = ts if ts else "-"
                tk.Label(row_status, text=ts_text, font=FONT_SMALL, bg=BG_CARD3, fg=TEXT_MUTED).pack(side="left", padx=(10, 0))

    def _toggle_detail(self, pesanan_id):
        self._expanded[pesanan_id] = not self._expanded.get(pesanan_id, False)
        self._render_list(force=True)

    def _konfirmasi_selesai(self, pesanan_id):
        if messagebox.askyesno("Konfirmasi", "Pesanan sudah kamu terima dengan baik?"):
            self.db.update_status_pesanan(pesanan_id, "Pesanan Selesai")
            messagebox.showinfo("Selesai!", "Terima kasih telah memesan! Pesanan telah dikonfirmasi selesai.")
            self._render_list()
            self._rebind_scroll(self.scroll_frame)

    def _mulai_polling(self):
        self._poll()

    def _poll(self):
        """Refresh data dari database setiap 5 detik."""
        try:
            if self.winfo_exists():
                self._render_list()
                self._rebind_scroll(self.scroll_frame)
        except tk.TclError:
            return
        # Cek apakah masih ada pesanan aktif (belum selesai semua)
        nama = getattr(self.controller, 'nama_pemesan', self.controller.pelanggan.nama)
        pesanan_list = self.db.get_pesanan_by_pemesan(nama)
        has_active = any(p['status'] != "Pesanan Selesai" for p in pesanan_list)
        if has_active or not pesanan_list:
            self._polling_job = self.after(5000, self._poll)

    def stop_polling(self):
        if self._polling_job:
            try:
                self.after_cancel(self._polling_job)
            except Exception:
                pass
            self._polling_job = None

    def _pesan_lagi(self):
        self.stop_polling()
        self.controller.reset_session()
