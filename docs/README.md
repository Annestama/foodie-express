# 🍽️ Aplikasi Pemesanan Makanan Online

**UAS Pemrograman Berorientasi Objek (PBO)**  
Arsitektur: Multi-App System (User App & Restaurant App)

---

## 📁 Struktur Proyek

```
uas-pbo/
├── models/
│   ├── base.py         # Abstract Base Class: Pengguna  [Abstraksi]
│   ├── item_menu.py    # ItemMenu, Makanan, Minuman      [Pewarisan + Polimorfisme]
│   ├── pesanan.py      # Class Pesanan                   [Enkapsulasi]
│   └── keranjang.py    # Class KeranjangBelanja
├── database/
│   ├── db_manager.py   # SQLite CRUD Manager
│   └── seed_data.py    # Data awal restoran & menu
├── views/
│   ├── user_views.py       # UI User App (4 halaman)
│   └── restaurant_views.py # UI Restaurant App
├── user_app.py         # 🚀 Entry point User App
├── restaurant_app.py   # 🏪 Entry point Restaurant App
├── pemesanan.db        # SQLite database (auto-generated)
└── docs/PRD.md
```

---

## 🚀 Cara Menjalankan

### 1. Jalankan User App (Aplikasi Pelanggan)
```bash
python user_app.py
```

### 2. Jalankan Restaurant App (Aplikasi Kasir)
```bash
python restaurant_app.py
```

> **Tips:** Buka kedua app secara bersamaan untuk melihat real-time update!

---

## 🎯 Demonstrasi 4 Pilar OOP

### 1. Enkapsulasi (`models/pesanan.py`)
- Atribut `__total_harga` dan `__status_pengiriman` dilindungi (private)
- Hanya bisa diakses via getter: `get_total()`, `get_status()`
- Modifikasi status hanya via `set_status()` yang memvalidasi urutan sequential

### 2. Abstraksi (`models/base.py`)
- `class Pengguna(ABC)` mendefinisikan abstract method `tampilkan_dashboard()`
- Class `Pelanggan` dan `Kasir` **wajib** mengimplementasikan method ini
- Tidak bisa membuat objek `Pengguna` secara langsung

### 3. Pewarisan (`models/item_menu.py`)
- `ItemMenu` adalah parent class dengan atribut `nama`, `harga`
- `Makanan(ItemMenu)` mewarisi semua atribut + tambah `level_pedas`
- `Minuman(ItemMenu)` mewarisi semua atribut + tambah `is_dingin`

### 4. Polimorfisme (`models/item_menu.py`)
- `Makanan.tampilkan_info()` → output: `🍽️ Rendang Sapi | Rp32.000 | Pedas`
- `Minuman.tampilkan_info()` → output: `🥤 Es Teh | Rp8.000 | ❄️ Dingin`
- Nama method sama, perilaku berbeda!

---

## 🔄 Alur Penggunaan

```
User App:
  Dashboard → Pilih Restoran
  → Menu → Tambah ke Keranjang
  → Keranjang → Checkout
  → Lacak Pesanan (polling 5 detik)

Restaurant App:
  Login → Pilih Restoran
  → Dashboard Transaksi (polling 10 detik)
  → Pilih Pesanan → Update Status
  → Dikonfirmasi → Diproses → Dikirim
```

---

## 💾 Database (SQLite)

Tabel:
- `restoran` — Daftar restoran aktif
- `menu` — Daftar item menu per restoran
- `pesanan` — Header transaksi pesanan
- `detail_pesanan` — Line item per pesanan

Database dibuat otomatis saat pertama kali app dijalankan.

---

## ⚙️ Requirements

- Python 3.10+
- Tkinter (sudah built-in di Python)
- Tidak ada library eksternal yang dibutuhkan!
