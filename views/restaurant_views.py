"""
restaurant_views.py — Semua Frame/Panel untuk Restaurant App (Tkinter UI)

Berisi komponen utama:
1. RestaurantDashboard    — Container utama dengan sistem Tab.
2. PesananFrame           — Daftar antrian pesanan masuk + filter status (polling 10 detik).
3. LaporanFrame           — Statistik pendapatan dan menu terlaris.
4. ManajemenMenuFrame     — Daftar menu, tambah menu baru, dan update menu.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ============================================================
# KONSTANTA WARNA & STYLE (Dark Theme — Restaurant App)
# ============================================================
BG_DARK       = "#f4f1ea"
BG_CARD       = "#faf9f6"
BG_CARD2      = "#ebe7dd"
BG_SIDEBAR    = "#e6e2d8"
ACCENT_ORANGE = "#e09f3e"
ACCENT_BLUE   = "#73a5c6"
ACCENT_GREEN  = "#6b9080"
ACCENT_YELLOW = "#e09f3e"
ACCENT_RED    = "#e56b6f"
TEXT_PRIMARY  = "#3a4042"
TEXT_MUTED    = "#808a8d"
TEXT_WHITE    = "#ffffff"
BORDER_COLOR  = "#d1cec7"
INPUT_BG      = "#ffffff"

FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_HEADER = ("Segoe UI", 13, "bold")
FONT_BODY   = ("Segoe UI", 11)
FONT_SMALL  = ("Segoe UI", 9)
FONT_BOLD   = ("Segoe UI", 11, "bold")
FONT_LARGE  = ("Segoe UI", 16, "bold")
FONT_GIANT  = ("Segoe UI", 24, "bold")

STATUS_COLORS = {
    "Menunggu Konfirmasi": ACCENT_YELLOW,
    "Dikonfirmasi":        ACCENT_BLUE,
    "Diproses":            ACCENT_ORANGE,
    "Dikirim":             ACCENT_GREEN,
    "Pesanan Selesai":     "#6b7280",
}

def styled_button(parent, text, command, bg=ACCENT_ORANGE, fg=TEXT_WHITE,
                  font_=FONT_BOLD, padx=16, pady=8, width=None, state="normal"):
    kwargs = dict(
        text=text, command=command,
        bg=bg, fg=fg, font=font_,
        relief="flat", cursor="hand2",
        padx=padx, pady=pady,
        activebackground="#1a1a2e", activeforeground=TEXT_WHITE,
        bd=0, state=state
    )
    if width:
        kwargs['width'] = width
    return tk.Button(parent, **kwargs)

def bind_mousewheel(widget, canvas):
    def _scroll(event):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")
    widget.bind("<MouseWheel>", _scroll)
    for child in widget.winfo_children():
        bind_mousewheel(child, canvas)


# ============================================================
# DASHBOARD CONTAINER (SISTEM TAB)
# ============================================================
class RestaurantDashboard(tk.Frame):
    """Container utama dengan Tab Navigasi."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.db = controller.db
        self.kasir = controller.kasir
        self.restoran = controller.restoran

        self.frames = {}
        self.tab_buttons = {}
        self.current_tab = None

        self._build_header()
        self._build_tabs()

    def _build_header(self):
        header = tk.Frame(self, bg=BG_CARD2)
        header.pack(fill="x")
        tk.Frame(header, bg=ACCENT_ORANGE, height=4).pack(fill="x")

        inner = tk.Frame(header, bg=BG_CARD2, padx=24, pady=16)
        inner.pack(fill="x")

        tk.Label(inner, text="Restaurant Apps",
                 font=FONT_TITLE, bg=BG_CARD2, fg=ACCENT_ORANGE).pack(side="left")

        info_right = tk.Frame(inner, bg=BG_CARD2)
        info_right.pack(side="right")

        text_info = tk.Frame(info_right, bg=BG_CARD2)
        text_info.pack(side="left", padx=(0, 16))

        tk.Label(text_info, text=self.restoran.get('nama', 'Restoran'),
                 font=FONT_BOLD, bg=BG_CARD2, fg=TEXT_PRIMARY).pack(anchor="e")
        tk.Label(text_info, text=f"Kasir: {self.kasir.nama}",
                 font=FONT_SMALL, bg=BG_CARD2, fg=TEXT_MUTED).pack(anchor="e")

        styled_button(info_right, "Ganti Akun", command=self.controller.logout,
                      bg=ACCENT_RED, fg=TEXT_WHITE, padx=12, pady=6).pack(side="right")

    def _build_tabs(self):
        tab_bar = tk.Frame(self, bg=BG_SIDEBAR)
        tab_bar.pack(fill="x")
        tk.Frame(self, bg=BORDER_COLOR, height=1).pack(fill="x")

        self.content_area = tk.Frame(self, bg=BG_DARK)
        self.content_area.pack(fill="both", expand=True)

        self.frames["Pesanan"] = PesananFrame(self.content_area, self)
        self.frames["Laporan"] = LaporanFrame(self.content_area, self)
        self.frames["Menu"] = ManajemenMenuFrame(self.content_area, self)

        for tab_name in ["Pesanan", "Laporan", "Menu"]:
            btn = tk.Button(tab_bar, text=tab_name, font=FONT_BOLD,
                            bg=BG_SIDEBAR, fg=TEXT_MUTED, relief="flat", bd=0,
                            cursor="hand2", padx=24, pady=12,
                            command=lambda n=tab_name: self.switch_tab(n),
                            activebackground=BG_CARD, activeforeground=ACCENT_ORANGE)
            btn.pack(side="left")
            self.tab_buttons[tab_name] = btn

        self.switch_tab("Pesanan")

    def switch_tab(self, tab_name):
        if self.current_tab == tab_name:
            return

        for name, btn in self.tab_buttons.items():
            if name == tab_name:
                btn.config(bg=BG_DARK, fg=ACCENT_ORANGE)
            else:
                btn.config(bg=BG_SIDEBAR, fg=TEXT_MUTED)

        if self.current_tab:
            self.frames[self.current_tab].pack_forget()
            if hasattr(self.frames[self.current_tab], 'on_hide'):
                self.frames[self.current_tab].on_hide()

        self.current_tab = tab_name
        self.frames[tab_name].pack(fill="both", expand=True)
        if hasattr(self.frames[tab_name], 'on_show'):
            self.frames[tab_name].on_show()

    def stop_polling(self):
        if hasattr(self.frames["Pesanan"], 'stop_polling'):
            self.frames["Pesanan"].stop_polling()


# ============================================================
# FRAME 1: PESANAN MASUK (EKSISTING)
# ============================================================
class PesananFrame(tk.Frame):
    def __init__(self, parent, dashboard):
        super().__init__(parent, bg=BG_DARK)
        self.dashboard = dashboard
        self.db = dashboard.db
        self.restoran = dashboard.restoran
        self.pesanan_list = []
        self.selected_pesanan = None
        self._polling_job = None
        self._last_pesanan_data = None

        self._build_ui()

    def on_show(self):
        self.muat_pesanan(force=True)
        self._mulai_polling()

    def on_hide(self):
        self.stop_polling()

    def _build_ui(self):
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True)

        self.left_panel = tk.Frame(content, bg=BG_SIDEBAR, width=480)
        self.left_panel.pack(side="left", fill="y")
        self.left_panel.pack_propagate(False)
        self._build_left_panel(self.left_panel)

        tk.Frame(content, bg=BORDER_COLOR, width=1).pack(side="left", fill="y")

        self.right_panel = tk.Frame(content, bg=BG_DARK)
        self.right_panel.pack(side="left", fill="both", expand=True)
        self._build_right_panel_empty()

    def _build_left_panel(self, parent):
        filter_frame = tk.Frame(parent, bg=BG_SIDEBAR, padx=16, pady=12)
        filter_frame.pack(fill="x")
        tk.Label(filter_frame, text="Filter Status:", font=FONT_BOLD,
                 bg=BG_SIDEBAR, fg=TEXT_MUTED).pack(side="left")

        self.filter_var = tk.StringVar(value="Semua")
        filter_opts = ["Semua", "Menunggu Konfirmasi", "Dikonfirmasi",
                       "Diproses", "Dikirim", "Pesanan Selesai"]
        filter_menu = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                   values=filter_opts, state="readonly",
                                   font=FONT_BODY, width=20)
        filter_menu.pack(side="left", padx=(8, 0))
        filter_menu.bind("<<ComboboxSelected>>", lambda e: self.muat_pesanan(force=True))

        styled_button(filter_frame, "↻", command=lambda: self.muat_pesanan(force=True),
                      bg=ACCENT_BLUE, fg=TEXT_WHITE, padx=10, pady=4).pack(side="right")

        self.count_label = tk.Label(parent, text="", font=FONT_SMALL, bg=BG_SIDEBAR, fg=TEXT_MUTED)
        self.count_label.pack(anchor="w", padx=16)
        tk.Frame(parent, bg=BORDER_COLOR, height=1).pack(fill="x")

        list_container = tk.Frame(parent, bg=BG_SIDEBAR)
        list_container.pack(fill="both", expand=True)
        self.list_canvas = tk.Canvas(list_container, bg=BG_SIDEBAR, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.list_canvas.yview)
        self.list_scroll_frame = tk.Frame(self.list_canvas, bg=BG_SIDEBAR)

        self.list_scroll_frame.bind("<Configure>", lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")))
        canvas_win = self.list_canvas.create_window((0, 0), window=self.list_scroll_frame, anchor="nw")
        self.list_canvas.configure(yscrollcommand=scrollbar.set)
        self.list_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.list_canvas.bind("<Configure>", lambda e: self.list_canvas.itemconfig(canvas_win, width=e.width))
        self.list_canvas.bind("<MouseWheel>", lambda e: self.list_canvas.yview_scroll(-1*(e.delta//120), "units"))
        self.list_scroll_frame.bind("<MouseWheel>", lambda e: self.list_canvas.yview_scroll(-1*(e.delta//120), "units"))

        self.poll_label = tk.Label(parent, text="Auto-refresh: 10 detik", font=FONT_SMALL, bg=BG_SIDEBAR, fg=TEXT_MUTED)
        self.poll_label.pack(side="bottom", pady=6)

    def _build_right_panel_empty(self):
        for w in self.right_panel.winfo_children(): w.destroy()
        center = tk.Frame(self.right_panel, bg=BG_DARK)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text="📋", font=("Segoe UI", 60), bg=BG_DARK, fg=BORDER_COLOR).pack()
        tk.Label(center, text="Pilih pesanan untuk melihat detail", font=FONT_HEADER, bg=BG_DARK, fg=TEXT_MUTED).pack(pady=(12, 0))

    def _build_right_panel_detail(self, pesanan: dict):
        for w in self.right_panel.winfo_children(): w.destroy()
        detail_header = tk.Frame(self.right_panel, bg=BG_CARD2, padx=30, pady=20)
        detail_header.pack(fill="x")

        status = pesanan['status']
        status_color = STATUS_COLORS.get(status, TEXT_MUTED)

        tk.Label(detail_header, text=f"Pesanan #{pesanan['id']}", font=FONT_TITLE, bg=BG_CARD2, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(detail_header, text=f"a/n {pesanan['nama_pemesan']}", font=FONT_BODY, bg=BG_CARD2, fg=TEXT_MUTED).pack(anchor="w")
        tk.Label(detail_header, text=f"Waktu: {pesanan.get('waktu', '-')}", font=FONT_SMALL, bg=BG_CARD2, fg=TEXT_MUTED).pack(anchor="w")

        status_badge = tk.Frame(detail_header, bg=status_color, padx=12, pady=4)
        status_badge.pack(anchor="w", pady=(8, 0))
        tk.Label(status_badge, text=status, font=FONT_BOLD, bg=status_color, fg=BG_DARK).pack()

        tk.Label(self.right_panel, text="Rincian Pesanan:", font=FONT_HEADER, bg=BG_DARK, fg=TEXT_PRIMARY).pack(anchor="w", padx=30, pady=(20, 8))

        table_frame = tk.Frame(self.right_panel, bg=BG_DARK, padx=30)
        table_frame.pack(fill="x")
        header_row = tk.Frame(table_frame, bg=BG_CARD2, padx=16, pady=8)
        header_row.pack(fill="x")
        for col, w in [("Menu", 30), ("Qty", 8), ("Subtotal", 15)]:
            tk.Label(header_row, text=col, font=FONT_BOLD, bg=BG_CARD2, fg=TEXT_MUTED, width=w, anchor="w").pack(side="left")

        total = 0
        for item in pesanan.get('items', []):
            row = tk.Frame(table_frame, bg=BG_CARD, padx=16, pady=10)
            row.pack(fill="x", pady=(1, 0))
            tk.Label(row, text=item['nama_menu'], font=FONT_BODY, bg=BG_CARD, fg=TEXT_PRIMARY, width=30, anchor="w").pack(side="left")
            tk.Label(row, text=f"x{item['qty']}", font=FONT_BODY, bg=BG_CARD, fg=TEXT_MUTED, width=8, anchor="w").pack(side="left")
            tk.Label(row, text=f"Rp{item['subtotal']:,.0f}", font=FONT_BOLD, bg=BG_CARD, fg=ACCENT_GREEN, width=15, anchor="w").pack(side="left")
            total += item['subtotal']

        total_row = tk.Frame(table_frame, bg=BG_CARD2, padx=16, pady=12)
        total_row.pack(fill="x", pady=(4, 0))
        tk.Label(total_row, text="Grand Total:", font=FONT_HEADER, bg=BG_CARD2, fg=TEXT_MUTED).pack(side="left")
        tk.Label(total_row, text=f"Rp{total:,.0f}", font=FONT_LARGE, bg=BG_CARD2, fg=ACCENT_GREEN).pack(side="right")

        self._build_status_panel(pesanan, status, status_color)

    def _build_status_panel(self, pesanan: dict, status: str, status_color: str):
        from models.pesanan import Pesanan
        mgmt_frame = tk.Frame(self.right_panel, bg=BG_CARD, padx=30, pady=20)
        mgmt_frame.pack(fill="x", padx=0, pady=(24, 0))

        tk.Label(mgmt_frame, text="Manajemen Status Pesanan", font=FONT_HEADER, bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(mgmt_frame, text="Status diperbarui secara berurutan (tidak bisa lompat)", font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", pady=(2, 16))

        STATUS_FLOW = Pesanan.STATUS_FLOW
        try:
            current_idx = STATUS_FLOW.index(status)
        except ValueError:
            current_idx = 0

        btn_configs = [
            ("[1] Konfirmasi",   "Dikonfirmasi", ACCENT_BLUE),
            ("[2] Mulai Proses", "Diproses",     ACCENT_ORANGE),
            ("[3] Kirim Pesanan","Dikirim",       ACCENT_GREEN),
        ]

        for btn_text, target_status, btn_color in btn_configs:
            try:
                target_idx = STATUS_FLOW.index(target_status)
            except ValueError:
                continue

            is_next = (target_idx == current_idx + 1)
            is_done = (target_idx <= current_idx)

            if is_done:
                btn_bg, btn_fg, btn_txt, btn_state = "#374151", TEXT_MUTED, f"✓  {target_status} (Selesai)", "disabled"
            elif is_next:
                btn_bg, btn_fg, btn_txt, btn_state = btn_color, (BG_DARK if btn_color == ACCENT_GREEN else TEXT_WHITE), btn_text, "normal"
            else:
                btn_bg, btn_fg, btn_txt, btn_state = "#252540", TEXT_MUTED, btn_text, "disabled"

            btn = tk.Button(mgmt_frame, text=btn_txt, command=lambda pid=pesanan['id'], ts=target_status: self.update_status(pid, ts),
                            bg=btn_bg, fg=btn_fg, font=FONT_BOLD, relief="flat", bd=0, padx=20, pady=10, state=btn_state,
                            cursor="hand2" if btn_state == "normal" else "arrow", activebackground=btn_color, activeforeground=TEXT_WHITE)
            btn.pack(fill="x", pady=(0, 8))

        if current_idx >= len(STATUS_FLOW) - 1:
            tk.Label(mgmt_frame, text="Pesanan ini telah selesai sepenuhnya", font=FONT_BODY, bg=BG_CARD, fg=ACCENT_GREEN).pack(pady=(8, 0))

    def muat_pesanan(self, force=False):
        filter_status = self.filter_var.get() if hasattr(self, 'filter_var') else "Semua"
        pesanan_list_baru = self.db.get_semua_pesanan_restoran(self.restoran['id'], filter_status=filter_status)

        if not force and hasattr(self, '_last_pesanan_data') and self._last_pesanan_data == pesanan_list_baru:
            return

        self._last_pesanan_data = pesanan_list_baru
        self.pesanan_list = pesanan_list_baru

        scroll_pos = self.list_canvas.yview()
        for w in self.list_scroll_frame.winfo_children(): w.destroy()
        self.count_label.config(text=f"{len(self.pesanan_list)} transaksi")

        if not self.pesanan_list:
            empty = tk.Frame(self.list_scroll_frame, bg=BG_SIDEBAR, pady=40)
            empty.pack(fill="x")
            tk.Label(empty, text="📭", font=("Segoe UI", 36), bg=BG_SIDEBAR, fg=BORDER_COLOR).pack()
            tk.Label(empty, text="Belum ada transaksi masuk", font=FONT_BODY, bg=BG_SIDEBAR, fg=TEXT_MUTED).pack(pady=(8, 0))
            return

        for pesanan in self.pesanan_list:
            self._buat_pesanan_card(pesanan)

        self.list_canvas.update_idletasks()
        self.list_canvas.yview_moveto(scroll_pos[0])

        if self.selected_pesanan:
            updated = next((p for p in self.pesanan_list if p['id'] == self.selected_pesanan['id']), None)
            if updated:
                self.selected_pesanan = updated
                self._build_right_panel_detail(updated)

    def _buat_pesanan_card(self, pesanan: dict):
        status = pesanan['status']
        status_color = STATUS_COLORS.get(status, TEXT_MUTED)

        card = tk.Frame(self.list_scroll_frame, bg=BG_CARD, padx=16, pady=14, cursor="hand2")
        card.pack(fill="x", pady=(0, 2))

        indicator = tk.Frame(card, bg=status_color, width=4)
        indicator.place(x=0, y=0, relheight=1)

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill="x", padx=(12, 0))

        row1 = tk.Frame(inner, bg=BG_CARD)
        row1.pack(fill="x")
        tk.Label(row1, text=f"Pesanan #{pesanan['id']}", font=FONT_BOLD, bg=BG_CARD, fg=TEXT_PRIMARY).pack(side="left")
        tk.Label(row1, text=status, font=FONT_SMALL, bg=status_color, fg=BG_DARK, padx=6, pady=2).pack(side="right")

        tk.Label(inner, text=f"Pemesan: {pesanan['nama_pemesan']}", font=FONT_BODY, bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w", pady=(4, 0))

        n_items = len(pesanan.get('items', []))
        waktu_str = pesanan.get('waktu', '')[:16] if pesanan.get('waktu') else '-'
        tk.Label(inner, text=f"{waktu_str}  |  {n_items} item", font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")

        total = sum(i['subtotal'] for i in pesanan.get('items', []))
        tk.Label(inner, text=f"Rp{total:,.0f}", font=FONT_BOLD, bg=BG_CARD, fg=ACCENT_GREEN).pack(anchor="w", pady=(2, 0))

        scroll_cb = lambda e: self.list_canvas.yview_scroll(-1*(e.delta//120), "units")
        for widget in [card, inner, row1]:
            widget.bind("<Button-1>", lambda e, p=pesanan, c=card, ind=indicator: self.select_pesanan(p, c, ind))
            widget.bind("<MouseWheel>", scroll_cb)
        for child in inner.winfo_children():
            child.bind("<Button-1>", lambda e, p=pesanan, c=card, ind=indicator: self.select_pesanan(p, c, ind))
            child.bind("<MouseWheel>", scroll_cb)

        card.bind("<Enter>", lambda e, c=card: c.config(bg="#ebe7dd"))
        card.bind("<Leave>", lambda e, c=card: c.config(bg=BG_CARD))

    def select_pesanan(self, pesanan: dict, card=None, indicator=None):
        self.selected_pesanan = pesanan
        self._build_right_panel_detail(pesanan)

    def update_status(self, pesanan_id: int, status_baru: str):
        pesanan_data = self.db.get_pesanan_by_id(pesanan_id)
        if not pesanan_data: return

        from models.pesanan import Pesanan
        obj_pesanan = Pesanan(
            id=pesanan_data['id'], nama_pemesan=pesanan_data['nama_pemesan'],
            restoran_id=pesanan_data['restoran_id'], items=pesanan_data.get('items', []),
            total_harga=pesanan_data['total_harga'], status=pesanan_data['status']
        )

        if obj_pesanan.set_status(status_baru):
            self.db.update_status_pesanan(pesanan_id, status_baru)
            messagebox.showinfo("Status Diperbarui", f"Status pesanan #{pesanan_id} diubah menjadi:\n{status_baru}")
            self.muat_pesanan(force=True)
        else:
            messagebox.showwarning("Tidak Valid", "Status harus diubah secara berurutan!")

    def _mulai_polling(self):
        self._poll()

    def _poll(self):
        try:
            self.muat_pesanan()
            now = datetime.now().strftime("%H:%M:%S")
            if hasattr(self, 'poll_label') and self.poll_label.winfo_exists():
                self.poll_label.config(text=f"Diperbarui: {now}")
        except Exception:
            pass
        self._polling_job = self.after(10000, self._poll)

    def stop_polling(self):
        if self._polling_job:
            try:
                self.after_cancel(self._polling_job)
            except Exception:
                pass
            self._polling_job = None


# ============================================================
# FRAME 2: LAPORAN & STATISTIK
# ============================================================
class LaporanFrame(tk.Frame):
    def __init__(self, parent, dashboard):
        super().__init__(parent, bg=BG_DARK)
        self.dashboard = dashboard
        self.db = dashboard.db
        self.restoran = dashboard.restoran

    def on_show(self):
        """Dipanggil otomatis ketika tab ini dibuka."""
        for w in self.winfo_children(): w.destroy()
        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG_CARD, padx=40, pady=24)
        header.pack(fill="x")
        tk.Label(header, text="Laporan & Statistik", font=FONT_TITLE, bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(header, text="Statistik performa penjualan restoran", font=FONT_BODY, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", pady=(4,0))

        # Content Layout
        content = tk.Frame(self, bg=BG_DARK, padx=40, pady=24)
        content.pack(fill="both", expand=True)

        # Kartu Pendapatan
        total_pendapatan = self.db.get_statistik_pendapatan(self.restoran['id'])
        
        card_pendapatan = tk.Frame(content, bg=BG_CARD2, padx=30, pady=24)
        card_pendapatan.pack(fill="x", pady=(0, 24))
        
        tk.Label(card_pendapatan, text="Total Pendapatan", font=FONT_HEADER, bg=BG_CARD2, fg=TEXT_MUTED).pack(anchor="w")
        tk.Label(card_pendapatan, text=f"Rp{total_pendapatan:,.0f}", font=("Segoe UI", 36, "bold"), bg=BG_CARD2, fg=ACCENT_GREEN).pack(anchor="w", pady=(10, 0))
        tk.Label(card_pendapatan, text="*Dihitung dari seluruh pesanan yang telah 'Selesai'", font=FONT_SMALL, bg=BG_CARD2, fg=TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        # Tabel Menu Terlaris
        tk.Label(content, text="Menu Paling Sering Diorder (Top Menu)", font=FONT_HEADER, bg=BG_DARK, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0, 10))

        table_frame = tk.Frame(content, bg=BG_CARD)
        table_frame.pack(fill="both", expand=True)

        # Header Table
        h_row = tk.Frame(table_frame, bg=BG_CARD2, padx=20, pady=12)
        h_row.pack(fill="x")
        tk.Label(h_row, text="Peringkat", font=FONT_BOLD, bg=BG_CARD2, fg=TEXT_MUTED, width=10, anchor="w").pack(side="left")
        tk.Label(h_row, text="Nama Menu", font=FONT_BOLD, bg=BG_CARD2, fg=TEXT_MUTED, width=30, anchor="w").pack(side="left")
        tk.Label(h_row, text="Total Terjual", font=FONT_BOLD, bg=BG_CARD2, fg=TEXT_MUTED, width=15, anchor="w").pack(side="left")
        tk.Label(h_row, text="Total Pemasukan", font=FONT_BOLD, bg=BG_CARD2, fg=TEXT_MUTED, width=20, anchor="w").pack(side="left")

        menu_terlaris = self.db.get_menu_terlaris(self.restoran['id'])
        
        if not menu_terlaris:
            tk.Label(table_frame, text="Belum ada data penjualan", font=FONT_BODY, bg=BG_CARD, fg=TEXT_MUTED).pack(pady=40)
        else:
            for i, menu in enumerate(menu_terlaris):
                row = tk.Frame(table_frame, bg=BG_CARD, padx=20, pady=12)
                row.pack(fill="x")
                tk.Frame(table_frame, bg=BORDER_COLOR, height=1).pack(fill="x")

                color_rank = ACCENT_ORANGE if i < 3 else TEXT_MUTED
                tk.Label(row, text=f"#{i+1}", font=FONT_BOLD, bg=BG_CARD, fg=color_rank, width=10, anchor="w").pack(side="left")
                tk.Label(row, text=menu['nama'], font=FONT_BODY, bg=BG_CARD, fg=TEXT_PRIMARY, width=30, anchor="w").pack(side="left")
                tk.Label(row, text=f"{menu['total_terjual']} porsi", font=FONT_BODY, bg=BG_CARD, fg=TEXT_PRIMARY, width=15, anchor="w").pack(side="left")
                tk.Label(row, text=f"Rp{menu['total_pendapatan']:,.0f}", font=FONT_BOLD, bg=BG_CARD, fg=ACCENT_GREEN, width=20, anchor="w").pack(side="left")


# ============================================================
# FRAME 3: MANAJEMEN MENU
# ============================================================
class ManajemenMenuFrame(tk.Frame):
    def __init__(self, parent, dashboard):
        super().__init__(parent, bg=BG_DARK)
        self.dashboard = dashboard
        self.db = dashboard.db
        self.restoran = dashboard.restoran
        self.menu_list = []

    def on_show(self):
        """Dipanggil otomatis ketika tab ini dibuka."""
        self._load_data()
        self._build_ui()

    def _load_data(self):
        self.menu_list = self.db.get_menu_by_restoran(self.restoran['id'])

    def _build_ui(self):
        for w in self.winfo_children(): w.destroy()

        # Split Layout: Left (List Menu) | Right (Form)
        left_panel = tk.Frame(self, bg=BG_DARK, width=600)
        left_panel.pack(side="left", fill="both", expand=True)
        left_panel.pack_propagate(False)

        tk.Frame(self, bg=BORDER_COLOR, width=1).pack(side="left", fill="y")

        self.right_panel = tk.Frame(self, bg=BG_CARD2, width=400)
        self.right_panel.pack(side="left", fill="y")
        self.right_panel.pack_propagate(False)

        self._build_list_panel(left_panel)
        self._build_form_panel()

    def _build_list_panel(self, parent):
        header = tk.Frame(parent, bg=BG_DARK, padx=30, pady=24)
        header.pack(fill="x")
        tk.Label(header, text="Daftar Menu Restoran", font=FONT_TITLE, bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")
        styled_button(header, "+ Menu Baru", command=self._form_tambah, bg=ACCENT_GREEN, fg=BG_DARK, padx=16, pady=6).pack(side="right")

        table_frame = tk.Frame(parent, bg=BG_DARK, padx=30)
        table_frame.pack(fill="both", expand=True)

        h_row = tk.Frame(table_frame, bg=BG_CARD2, padx=16, pady=10)
        h_row.pack(fill="x")
        for col, w in [("Nama Menu", 25), ("Kategori", 15), ("Harga", 15), ("Aksi", 10)]:
            tk.Label(h_row, text=col, font=FONT_BOLD, bg=BG_CARD2, fg=TEXT_MUTED, width=w, anchor="w").pack(side="left")

        # Scrollable Canvas for Menu List
        canvas = tk.Canvas(table_frame, bg=BG_DARK, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_DARK)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        scroll_cb = lambda e: canvas.yview_scroll(-1*(e.delta//120), "units")
        canvas.bind("<MouseWheel>", scroll_cb)
        scroll_frame.bind("<MouseWheel>", scroll_cb)

        if not self.menu_list:
            tk.Label(scroll_frame, text="Belum ada menu, tambahkan sekarang!", font=FONT_BODY, bg=BG_DARK, fg=TEXT_MUTED).pack(pady=40)
            return

        for menu in self.menu_list:
            row = tk.Frame(scroll_frame, bg=BG_CARD, padx=16, pady=12)
            row.pack(fill="x", pady=(0, 4))
            row.bind("<MouseWheel>", scroll_cb)

            tk.Label(row, text=menu['nama'], font=FONT_BODY, bg=BG_CARD, fg=TEXT_PRIMARY, width=25, anchor="w").pack(side="left")
            kategori = "Makanan" if menu['tipe'] == 'makanan' else "Minuman"
            tk.Label(row, text=kategori, font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED, width=15, anchor="w").pack(side="left")
            tk.Label(row, text=f"Rp{menu['harga']:,.0f}", font=FONT_BOLD, bg=BG_CARD, fg=ACCENT_GREEN, width=15, anchor="w").pack(side="left")
            
            btn_edit = tk.Button(row, text="Edit", font=FONT_BOLD, bg=INPUT_BG, fg=ACCENT_BLUE, relief="flat", cursor="hand2", bd=0,
                                 command=lambda m=menu: self._form_edit(m))
            btn_edit.pack(side="left")
            
            for child in row.winfo_children():
                child.bind("<MouseWheel>", scroll_cb)

    def _build_form_panel(self, menu_data=None):
        for w in self.right_panel.winfo_children(): w.destroy()

        mode = "Edit Menu" if menu_data else "Tambah Menu Baru"
        
        f = tk.Frame(self.right_panel, bg=BG_CARD2, padx=30, pady=30)
        f.pack(fill="both", expand=True)

        tk.Label(f, text=mode, font=FONT_HEADER, bg=BG_CARD2, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0, 20))

        # Fields
        self.var_id = tk.IntVar(value=menu_data['id'] if menu_data else 0)
        self.var_nama = tk.StringVar(value=menu_data['nama'] if menu_data else "")
        self.var_harga = tk.StringVar(value=str(int(menu_data['harga'])) if menu_data else "")
        self.var_tipe = tk.StringVar(value=menu_data['tipe'] if menu_data else "makanan")

        def make_field(label_text, widget):
            tk.Label(f, text=label_text, font=FONT_BOLD, bg=BG_CARD2, fg=TEXT_MUTED).pack(anchor="w", pady=(10, 4))
            widget.pack(fill="x", ipady=6)

        entry_nama = tk.Entry(f, textvariable=self.var_nama, font=FONT_BODY, bg=INPUT_BG, fg=TEXT_PRIMARY, relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_ORANGE, insertbackground=ACCENT_ORANGE)
        make_field("Nama Menu", entry_nama)

        entry_harga = tk.Entry(f, textvariable=self.var_harga, font=FONT_BODY, bg=INPUT_BG, fg=TEXT_PRIMARY, relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_ORANGE, insertbackground=ACCENT_ORANGE)
        make_field("Harga (Rp)", entry_harga)

        tk.Label(f, text="Tipe", font=FONT_BOLD, bg=BG_CARD2, fg=TEXT_MUTED).pack(anchor="w", pady=(10, 4))
        frame_tipe = tk.Frame(f, bg=BG_CARD2)
        frame_tipe.pack(fill="x")
        tk.Radiobutton(frame_tipe, text="Makanan", variable=self.var_tipe, value="makanan", bg=BG_CARD2, fg=TEXT_PRIMARY, selectcolor=INPUT_BG, activebackground=BG_CARD2, activeforeground=ACCENT_ORANGE).pack(side="left")
        tk.Radiobutton(frame_tipe, text="Minuman", variable=self.var_tipe, value="minuman", bg=BG_CARD2, fg=TEXT_PRIMARY, selectcolor=INPUT_BG, activebackground=BG_CARD2, activeforeground=ACCENT_ORANGE).pack(side="left", padx=10)

        tk.Frame(f, bg=BG_CARD2, height=20).pack()
        
        btn_text = "Simpan Perubahan" if menu_data else "Tambah Menu"
        styled_button(f, btn_text, command=self._simpan_menu, bg=ACCENT_BLUE, fg=TEXT_WHITE, padx=20, pady=10).pack(fill="x", pady=(20, 0))
        
        if menu_data:
            styled_button(f, "Hapus Menu", command=self._hapus_menu, bg=ACCENT_RED, fg=TEXT_WHITE, padx=20, pady=10).pack(fill="x", pady=(10, 0))
            styled_button(f, "Batal Edit", command=self._form_tambah, bg=INPUT_BG, fg=TEXT_MUTED, padx=20, pady=10).pack(fill="x", pady=(10, 0))

    def _form_tambah(self):
        self._build_form_panel(None)

    def _form_edit(self, menu_data):
        self._build_form_panel(menu_data)

    def _hapus_menu(self):
        menu_id = self.var_id.get()
        if menu_id <= 0: return

        if messagebox.askyesno("Hapus Menu", f"Yakin ingin menghapus menu ini?"):
            if self.db.hapus_menu(menu_id):
                messagebox.showinfo("Sukses", "Menu berhasil dihapus.")
                self.on_show()
            else:
                messagebox.showerror("Gagal", "Menu tidak bisa dihapus karena sudah pernah dipesan (terdapat riwayat transaksi).")

    def _simpan_menu(self):
        nama = self.var_nama.get().strip()
        harga_str = self.var_harga.get().strip()
        tipe = self.var_tipe.get()
        pedas = "Tidak Pedas"
        dingin = 1
        menu_id = self.var_id.get()

        if not nama or not harga_str:
            messagebox.showwarning("Input Tidak Lengkap", "Nama dan Harga harus diisi!")
            return

        try:
            harga = float(harga_str)
        except ValueError:
            messagebox.showwarning("Harga Tidak Valid", "Harga harus berupa angka!")
            return

        if menu_id > 0:
            # Update
            self.db.update_menu(menu_id, nama, harga, tipe, pedas, dingin)
            messagebox.showinfo("Sukses", f"Menu '{nama}' berhasil diperbarui!")
        else:
            # Tambah
            self.db.tambah_menu(self.restoran['id'], nama, harga, tipe, pedas, dingin)
            messagebox.showinfo("Sukses", f"Menu '{nama}' berhasil ditambahkan!")

        # Refresh
        self.on_show()
