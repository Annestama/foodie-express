# Ringkasan Proyek UAS: Sistem Manajemen Pemesanan Restoran (FoodOrder/RestaurantOS)

Dokumen ini disusun sebagai panduan presentasi atau laporan UAS Anda. Proyek ini adalah aplikasi berbasis *Graphical User Interface* (GUI) menggunakan `Tkinter` dan *Database* `SQLite3`. Aplikasi ini memiliki dua sisi (dua *entry point*):
1. **User App (`user_app.py`)**: Sisi pelanggan untuk mendaftar akun, mencari restoran, memilih menu (keranjang), dan melakukan pesanan (checkout).
2. **Restaurant App (`restaurant_app.py`)**: Sisi kasir/admin untuk menerima pesanan masuk, memproses status pesanan (*polling real-time*), manajemen menu (CRUD), dan melihat laporan penjualan.

---

## Penerapan 4 Pilar Pemrograman Berorientasi Objek (OOP)

Aplikasi ini mendemonstrasikan secara kuat 4 pilar utama OOP pada struktur kode Python di bawah folder `models/`. Berikut adalah penjelasan letak implementasi dan bukti kodenya:

### 1. Abstraksi (*Abstraction*)
**Definisi:** Menyembunyikan kerumitan implementasi dan hanya menampilkan fungsionalitas yang penting (kontrak desain).
- **Letak Kode:** `models/base.py`
- **Penjelasan:** Terdapat class `Pengguna(ABC)` yang mewarisi `ABC` (Abstract Base Class). Class ini mendefinisikan sebuah *method* abstrak `@abstractmethod def tampilkan_dashboard(self)`.
- **Mengapa ini Abstraksi:** Class `Pengguna` hanya membuat aturan (kontrak) bahwa siapa pun yang menjadi *subclass*-nya harus membuat/mengimplementasikan `tampilkan_dashboard()`. Class `Pengguna` sendiri tidak bisa diinisiasi secara langsung.

### 2. Pewarisan (*Inheritance*)
**Definisi:** Mewariskan atribut dan *behavior* (method) dari sebuah class induk (*parent*) ke class turunan (*child*), menghindari duplikasi kode.
- **Letak Kode Utama:** `models/item_menu.py`
- **Penjelasan:** Terdapat sebuah *Parent Class* bernama `ItemMenu`. Di bawahnya, terdapat *Child Class* bernama `Makanan` dan `Minuman`.
- **Bukti Kode:** `class Makanan(ItemMenu):` dan `class Minuman(ItemMenu):`. Kedua *child class* ini secara otomatis mewarisi *atribut* (`id`, `nama`, `harga`, `restoran_id`) dari `ItemMenu` melalui pemanggilan `super().__init__(...)`.
- **Contoh Lain:** `class Pelanggan(Pengguna)` di `models/pelanggan.py` dan `class Kasir(Pengguna)` di `restaurant_app.py` yang mewarisi atribut nama dan method `sapa()`.

### 3. Polimorfisme (*Polymorphism*)
**Definisi:** Kemampuan satu method yang sama untuk memiliki perilaku (*behavior*) atau bentuk yang berbeda tergantung pada *object* pemanggilnya.
- **Letak Kode:** `models/item_menu.py`
- **Penjelasan:** *Parent class* `ItemMenu` memiliki method dasar `tampilkan_info()`. Namun, method ini di-*override* (ditimpa) oleh *subclass* `Makanan` dan `Minuman`.
- **Mengapa ini Polimorfisme:** Jika Anda memanggil `obj.tampilkan_info()`, hasilnya akan berbeda. Jika objeknya adalah makanan, ia akan mengembalikan *string* dengan label `[Makanan]`. Jika objeknya minuman, ia akan mengembalikan label `[Minuman]`. Padahal nama *method*-nya persis sama. Selain itu, fungsi `buat_item_dari_db()` juga menerapkan konsep polimorfisme saat membentuk *object* (*factory function*).

### 4. Enkapsulasi (*Encapsulation*)
**Definisi:** Membungkus data (*state*) dan menyembunyikan detail implementasi internal dari pihak luar. Akses ke dalam data hanya diizinkan melalui *method* tertentu (*getter/setter*).
- **Letak Kode:** `models/keranjang.py` (Class `KeranjangBelanja`) dan `database/db_manager.py` (Class `DatabaseManager`).
- **Penjelasan (KeranjangBelanja):** *State* atau data isi keranjang disimpan dalam variabel yang bersifat *protected* yaitu `self._items` (menggunakan awalan garis bawah/underscore `_`).
- **Mengapa ini Enkapsulasi:** Class luar (seperti UI) tidak diizinkan mengubah `_items` secara langsung (misal dengan `_items.append`). Untuk memodifikasi keranjang, mereka wajib menggunakan jalur resmi yang disediakan, yaitu fungsi `tambah_item()`, `edit_qty()`, `hapus_item()`, dan untuk membaca data wajib menggunakan `get_items()`. Hal ini menjaga validitas data di dalam keranjang (misalnya qty dilarang di bawah 0).
