# **Product Requirements Document (PRD) V2**

**Nama Proyek:** Aplikasi Pemesanan Makanan Online Berbasis Python  
**Tujuan:** Proyek Ujian Akhir Semester (UAS) Mata Kuliah Pemrograman Berorientasi Objek (PBO)  
**Arsitektur:** Multi-Apps Sistem (User App & Restaurant App)

## **1\. Latar Belakang & Gambaran Umum**

Aplikasi ini dirancang untuk mensimulasikan ekosistem pemesanan makanan secara real-time yang terdiri dari dua aplikasi terpisah: Aplikasi Pelanggan (User App) dan Aplikasi Restoran (Admin/Kasir App). Kedua aplikasi saling terhubung melalui basis data bersama untuk memperbarui status pesanan secara berkala tanpa intervensi manual dari pengguna (auto-update/polling).

## **2\. Spesifikasi Aplikasi Pelanggan (User App)**

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
* Input jumlah porsi divalidasi ketat hanya menerima nilai integer positif (\> 0). Karakter teks, simbol, atau angka negatif akan ditolak otomatis.  
* Item masuk ke memori keranjang belanja jika kuantitas \> 0 dan pengguna menekan tombol "Tambah".

| Nama Field | Jenis Field | Deskripsi & Contoh Data |
| :---- | :---- | :---- |
| Header Restoran | Table Field | Teks judul penunjuk nama restoran yang sedang diakses. |
| Katalog Menu & Harga | Table Field | Rincian item menu makanan (Contoh: "Rendang \- Rp25.000"). |
| Jumlah Porsi / Qty | Form Field | Input box atau komponen spinbox (+/-) kuantitas. |
| Tambah Keranjang | Form Field | Tombol aksi untuk merekam item pilihan ke memori sesi. |
| Kembali | Form Field | Tombol navigasi untuk kembali ke Dashboard Utama. |

### **2.3 Fitur: Keranjang Belanja & Checkout**

Halaman rekapitulasi daftar pesanan sementara sebelum dikirimkan ke server restoran.  
**Business Rules:**

* Sistem menghitung nilai subtotal dinamis (Harga x Qty) dan total akhir (Grand Total).  
* Apabila kuantitas diubah menjadi 0, item terkait langsung dihapus dari struktur data keranjang belanja.  
* Tombol checkout dinonaktifkan (disabled) secara otomatis apabila keranjang belanja kosong.  
* Saat checkout dieksekusi, pesanan dikunci, data dikirim ke database, dan status awal diinisialisasi sebagai "Menunggu Konfirmasi".

| Nama Field | Jenis Field | Deskripsi & Contoh Data |
| :---- | :---- | :---- |
| Nama Pemesan | Form Field | Input identitas pelanggan (Default otomatis: Zildjian Annesta). |
| List Item Pesanan | Table Field | Rincian belanja komparatif (Nama Menu, Qty, Subtotal). |
| Grand Total | Table Field | Teks representasi nilai akhir akumulasi biaya. |
| Edit / Hapus Item | Form Field | Tombol interaktif inline untuk memodifikasi baris item keranjang. |
| Konfirmasi Checkout | Form Field | Tombol finalisasi transaksi untuk beralih ke halaman Lacak. |

### **2.4 Fitur: Lacak Pengiriman & Selesai**

Halaman monitoring interaktif pelacakan status pesanan secara real-time.  
**Business Rules:**

* **Real-time Polling (User):** Sistem melakukan query otomatis ke database setiap 5 detik sekali secara background untuk mendeteksi pembaruan status tanpa refresh manual.  
* **Validasi Tombol Selesai:** Tombol "Konfirmasi Pesanan Selesai" terkunci (disabled) secara default. Komponen ini hanya akan aktif (enabled) ketika status pesanan dari database berubah menjadi "Dikirim".  
* Saat ditekan oleh pembeli, status diubah menjadi "Pesanan Selesai" dan siklus transaksi ditutup sepenuhnya.

| Nama Field | Jenis Field | Deskripsi & Contoh Data |
| :---- | :---- | :---- |
| ID / Nama Pesanan | Table Field | Identitas pelacakan pesanan (Contoh: "Pesanan a/n Zildjian Annesta"). |
| Indikator Status | Table Field | Teks dinamis representasi status terkini (Contoh: "Status: Sedang Dimasak"). |
| Konfirmasi Pesanan Selesai | Form Field | Tombol validasi penerimaan barang. Aktif hanya jika status \== "Dikirim". |

## **3\. Spesifikasi Aplikasi Restoran (Admin/Kasir App)**

### **3.1 Fitur: Dashboard Transaksi Masuk**

Halaman utama bagi kasir/restoran untuk mengontrol antrean pesanan masuk.  
**Business Rules:**

* **Real-time Polling (Admin):** Aplikasi melakukan penarikan data transaksi baru dari database secara berkala setiap 10 detik. Data baru otomatis merender daftar tanpa me-refresh window aplikasi.

| Nama Field | Jenis Field | Deskripsi & Contoh Data |
| :---- | :---- | :---- |
| Filter Status | Filter Field | Dropdown (OptionMenu) untuk menyaring list antrean transaksi (Contoh: "Baru Masuk"). |
| Daftar Transaksi Masuk | Table Field | Tabel scrollable berisi ID Pesanan, Waktu, Nama Pemesan, dan Rincian Menu. |

### **3.2 Fitur: Panel Manajemen & Update Status Pesanan**

Kontrol aksi operasional untuk memodifikasi status pesanan.  
**Business Rules:**

* Perubahan urutan status bersifat sekuensial mutlak: Menunggu ➔ Dikonfirmasi ➔ Diproses ➔ Dikirim.  
* Sistem menonaktifkan atau memvalidasi agar kasir tidak dapat melompati status (Contoh: status dari "Menunggu" tidak bisa langsung "Dikirim").  
* Aksi penekanan tombol update akan memperbarui record di database secara instan agar terbaca oleh mekanisme auto-update Aplikasi Pelanggan.

| Nama Field | Jenis Field | Deskripsi & Contoh Data |
| :---- | :---- | :---- |
| Tombol: Dikonfirmasi | Form Field | Aksi menerima/menyetujui pesanan baru yang dikirim pelanggan. |
| Tombol: Diproses | Form Field | Aksi menandai bahwa menu makanan sedang masuk tahap pembuatan/dimasak. |
| Tombol: Dikirim | Form Field | Aksi melepas pesanan ke kurir. Mengaktifkan tombol penyelesaian di sisi User. |

## **4\. Implementasi Pilar Object-Oriented Programming (OOP)**

Proyek ini diwajibkan untuk mendemonstrasikan ke-empat pilar utama OOP. Berikut adalah penjabaran penerapan pilar tersebut pada logika backend/core program.

### **4.1 Enkapsulasi (Encapsulation)**

**Konsep:** Menyembunyikan dan melindungi data internal pada sebuah class menggunakan atribut *private* agar tidak dimodifikasi sembarangan dari luar scope.  
**Penerapan:** Data konfidensial seperti \_\_total\_harga dan \_\_status\_pengiriman di dalam class Pesanan dilindungi. Modifikasi state (terutama pengubahan status dari "Menunggu" ke "Dikirim") hanya bisa dilakukan melalui validasi di dalam setter method set\_status().

### **4.2 Abstraksi (Abstraction)**

**Konsep:** Membuat blueprint atau cetak biru berupa Abstract Base Class (ABC) yang mewajibkan sub-class untuk mendefinisikan method tertentu (kontrak desain program).  
**Penerapan:** Menggunakan class abstrak Pengguna yang mendefinisikan abstract method tampilkan\_dashboard(). Karena User App dan Restoran App memiliki interface yang berbeda, entitas Pelanggan dan entitas Kasir masing-masing wajib mengimplementasikan versi dashboard mereka sendiri berdasarkan kontrak dari class Pengguna.

### **4.3 Pewarisan (Inheritance)**

**Konsep:** Child class (kelas turunan) dapat mewarisi state dan behavior (atribut & method) dari Parent class (kelas induk) untuk mengurangi redundansi baris kode.  
**Penerapan:** Menggunakan class ItemMenu sebagai parent class yang memiliki atribut dasar (nama dan harga). Atribut tersebut kemudian diwariskan ke child class Makanan dan Minuman. Class Makanan memiliki tambahan atribut level\_pedas, sementara class Minuman memiliki tambahan atribut boolean is\_dingin.

### **4.4 Polimorfisme (Polymorphism)**

**Konsep:** Sebuah object/class turunan dapat menggunakan nama method yang persis sama dari parent class atau saudaranya, namun perilakunya berubah sesuai implementasi spesifik di class tersebut (Method Overriding).  
**Penerapan:** Baik class Makanan dan Minuman melakukan \*overriding\* pada method tampilkan\_info() yang diturunkan dari class ItemMenu. Saat sistem meloop array daftar menu dan memanggil method tampilkan\_info() pada masing-masing objek, aplikasi akan merender string format berbeda yang mendeskripsikan secara spesifik apakah itu Makanan (beserta info pedas) atau Minuman (beserta info suhu).