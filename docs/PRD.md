# **Product Requirements Document (PRD) V2 - Updated**

**Nama Proyek:** Aplikasi Pemesanan Makanan Online Berbasis Python  
**Tujuan:** Proyek Ujian Akhir Semester (UAS) Mata Kuliah Pemrograman Berorientasi Objek (PBO)  
**Arsitektur:** Multi-Apps Sistem (User App & Restaurant App)

## **1. Latar Belakang & Gambaran Umum**

Aplikasi ini dirancang untuk mensimulasikan ekosistem pemesanan makanan secara real-time yang terdiri dari dua aplikasi terpisah: Aplikasi Pelanggan (User App) dan Aplikasi Restoran (Admin/Kasir App). Kedua aplikasi saling terhubung melalui basis data bersama untuk memperbarui status pesanan secara berkala tanpa intervensi manual dari pengguna (auto-update/polling).

## **2. Spesifikasi Aplikasi Pelanggan (User App)**

### **2.1 Fitur: Dashboard Utama (Katalog Restoran)**

Halaman beranda utama yang menampilkan seluruh mitra restoran yang aktif.  
**Business Rules:**

* Sistem secara otomatis memuat daftar restoran yang aktif dari database saat aplikasi dijalankan.  
* Pengguna wajib memilih salah satu restoran untuk melanjutkan ke halaman katalog menu.  
* Jika database restoran kosong, antarmuka wajib menampilkan teks indikator "Belum ada restoran yang terdaftar".

| Nama Field | Jenis Field | Deskripsi & Contoh Data |
| :---- | :---- | :---- |
| Pencarian Restoran | Filter Field | Kotak teks (Entry) untuk menyaring daftar nama restoran. |
| Daftar Restoran | Table Field | Area scrollable yang menampilkan card atau list nama restoran terdaftar. |
| Pilih Restoran | Form Field | Tombol navigasi untuk mengonfirmasi pilihan restoran. |

### **2.2 Fitur: Halaman Menu Restoran**

Menampilkan daftar makanan dan minuman berdasarkan pilihan restoran sebelumnya.  
**Business Rules:**

* Katalog menu yang ditampilkan dikunci secara eksklusif berelasi dengan ID restoran terpilih.  
* Input jumlah porsi divalidasi ketat hanya menerima nilai integer positif (> 0). Karakter teks, simbol, atau angka negatif akan ditolak otomatis.  
* Item masuk ke memori keranjang belanja jika kuantitas > 0 dan pengguna menekan tombol "Tambah".

### **2.3 Fitur: Keranjang Belanja & Checkout (Pajak, Layanan & Simulasi Pembayaran)**

Halaman rekapitulasi daftar pesanan sementara sebelum dikirimkan ke server restoran. Sistem sekarang mencakup kalkulasi pajak dan biaya layanan yang diatur oleh restoran, serta simulasi pembayaran interaktif.
**Business Rules:**

* Sistem menghitung nilai subtotal dinamis (Harga x Qty).  
* Sistem mengambil persentase **Pajak** dan **Biaya Layanan** dari pengaturan restoran untuk dikalkulasikan ke dalam **Grand Total**.
* Tombol checkout memicu pop-up **Simulasi Pembayaran** di mana pengguna harus memilih metode (Cash, VA/QRIS, E-Wallet, Kartu Kredit).
* **Penundaan Pengiriman Pesanan (15 Detik Grace Period):** Setelah pembayaran disimulasikan berhasil, pengguna diberikan waktu 15 detik untuk membatalkan pesanan. Jika batas waktu habis atau pengguna tidak membatalkan, pesanan baru akan dikirim ke database.

| Nama Field | Jenis Field | Deskripsi & Contoh Data |
| :---- | :---- | :---- |
| Nama Pemesan | Form Field | Input identitas pelanggan. |
| List Item Pesanan | Table Field | Rincian belanja (Nama Menu, Qty, Subtotal). |
| Pajak & Layanan | Table Field | Rincian biaya tambahan berdasarkan pengaturan restoran. |
| Grand Total | Table Field | Teks representasi nilai akhir akumulasi biaya. |
| Pilih Pembayaran | Form Field | Dropdown metode bayar (Cash, Virtual Account, dll). |
| Batalkan Pesanan (Timer) | Form Field | Tombol pembatalan yang muncul selama 15 detik sebelum data dikirim. |

### **2.4 Fitur: Lacak Pengiriman & Selesai**

Halaman monitoring interaktif pelacakan status pesanan secara real-time, termasuk riwayat pesanan yang dibatalkan.  
**Business Rules:**

* **Real-time Polling (User):** Sistem melakukan query otomatis ke database setiap 5 detik sekali secara background.
* Tombol "Konfirmasi Pesanan Diterima" terkunci (disabled) secara default. Komponen ini hanya aktif ketika status pesanan menjadi "Dikirim".  
* **Status Pembatalan:** Jika pesanan dibatalkan oleh restoran, status akan berubah menjadi "Dibatalkan" dan menampilkan **Alasan Pembatalan** secara detail.

## **3. Spesifikasi Aplikasi Restoran (Admin/Kasir App)**

### **3.1 Fitur: Dashboard Transaksi Masuk**

Halaman utama bagi kasir/restoran untuk mengontrol antrean pesanan masuk.  
**Business Rules:**

* **Real-time Polling (Admin):** Aplikasi menarik data transaksi baru setiap 10 detik.
* Pesanan yang masuk memuat rincian nominal pembayaran, metode pembayaran, pajak, dan biaya layanan.

### **3.2 Fitur: Panel Manajemen & Update Status Pesanan**

Kontrol aksi operasional untuk memodifikasi status pesanan, termasuk pembatalan pesanan.  
**Business Rules:**

* Perubahan urutan status bersifat sekuensial mutlak: Menunggu ➔ Dikonfirmasi ➔ Diproses ➔ Dikirim.  
* **Pembatalan Pesanan (Restaurant Side):** Tersedia tombol "Batalkan Pesanan". Kasir diwajibkan untuk mengisi **Alasan Pembatalan** melalui pop-up dialog. Status pesanan akan berubah menjadi "Dibatalkan" secara permanen dan di-sync ke User App.

| Nama Field | Jenis Field | Deskripsi & Contoh Data |
| :---- | :---- | :---- |
| Tombol: Dikonfirmasi | Form Field | Aksi menerima pesanan. |
| Tombol: Diproses | Form Field | Aksi memasak makanan. |
| Tombol: Dikirim | Form Field | Aksi melepas pesanan ke kurir. |
| Tombol: Batalkan Pesanan | Form Field | Aksi membatalkan pesanan dengan input pop-up alasan pembatalan. |

### **3.3 Fitur: Pengaturan Restoran (Pajak & Biaya Layanan)**

Halaman baru untuk mengatur persentase beban biaya tambahan restoran.
**Business Rules:**
* Kasir dapat mengatur persentase Pajak (contoh: 11%) dan Biaya Layanan (contoh: 5%).
* Pengaturan ini akan langsung tersimpan di database dan diterapkan pada semua pesanan baru dari pengguna.

## **4. Implementasi Pilar Object-Oriented Programming (OOP)**

Proyek ini diwajibkan untuk mendemonstrasikan ke-empat pilar utama OOP. Berikut adalah penjabaran penerapan pilar tersebut pada logika backend/core program.

### **4.1 Enkapsulasi (Encapsulation)**

**Konsep:** Menyembunyikan dan melindungi data internal pada sebuah class menggunakan atribut *private*.  
**Penerapan:** Data konfidensial seperti `__total_harga` dan `__status_pengiriman` di dalam class `Pesanan` dilindungi. Modifikasi state hanya bisa dilakukan melalui validasi di dalam setter method `set_status()`, di mana `set_status()` mengimplementasikan pembatasan urutan alur pesanan dan izin khusus untuk status pembatalan.

### **4.2 Abstraksi (Abstraction)**

**Konsep:** Membuat blueprint atau cetak biru berupa Abstract Base Class (ABC).  
**Penerapan:** Menggunakan class abstrak `Pengguna` yang mendefinisikan abstract method `tampilkan_dashboard()`. User App dan Restoran App memiliki interface yang berbeda, mengimplementasikan versi dashboard mereka sendiri berdasarkan kontrak dari class `Pengguna`.

### **4.3 Pewarisan (Inheritance)**

**Konsep:** Child class dapat mewarisi state dan behavior (atribut & method) dari Parent class.  
**Penerapan:** Menggunakan class `ItemMenu` sebagai parent class yang memiliki atribut dasar (nama dan harga). Diwariskan ke child class `Makanan` dan `Minuman`. Class `Makanan` memiliki tambahan atribut `level_pedas`, sementara class `Minuman` memiliki tambahan atribut boolean `is_dingin`.

### **4.4 Polimorfisme (Polymorphism)**

**Konsep:** Method Overriding pada class turunan.  
**Penerapan:** Baik class `Makanan` dan `Minuman` melakukan overriding pada method `tampilkan_info()` yang diturunkan dari class `ItemMenu`. Aplikasi akan merender string format berbeda yang mendeskripsikan secara spesifik apakah itu Makanan (beserta info pedas) atau Minuman (beserta info suhu).