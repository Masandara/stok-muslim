# 🕌 Sistem Manajemen Stok Produk Perlengkapan Muslim Pria
### Grand Mode — Ujian Kompetensi Kejuruan (UJK) Junior Web Programmer
**Universitas Duta Bangsa Surakarta**  
Mata Kuliah: Pemrograman Web | Dosen: Nibras Faiq Muhammad, M.Kom.

---

## 📌 Tema Kasus

**Grand Mode** adalah toko online yang menjual perlengkapan muslim pria, mencakup:
- **Baju Koko** (lengan panjang & pendek, berbagai bahan dan motif)
- **Kurta Pria** (busana khas Pakistan/India)
- **Jubah Pria** (jubah putih, jubah zipper, jubah kancing manset)

Sistem ini dibangun untuk mengelola **stok produk** secara efisien, dilengkapi autentikasi admin, fitur CRUD lengkap, laporan stok, dan peringatan stok rendah.

---

## 🛠️ Teknologi

| Komponen        | Teknologi                       |
|-----------------|---------------------------------|
| Bahasa          | Python 3.10+                    |
| Framework UI    | Streamlit                       |
| Database        | MySQL (via phpMyAdmin / XAMPP)  |
| Koneksi DB      | mysql-connector-python          |
| Enkripsi        | bcrypt (password hashing)       |
| Autentikasi     | Streamlit Session State         |

---

## 📁 Struktur Proyek

```
Sistem Manajemen Stok Produk Perlengkapan Muslim Pria/
│
├── app.py          ← Entry point utama (Dashboard, CRUD, Laporan)
├── auth.py         ← Modul login, logout, bcrypt hash/verify
├── koneksi.py      ← Koneksi ke database MySQL
├── database.sql    ← Export database lengkap (struktur + data)
├── README.md       ← Dokumentasi proyek ini
├── requirements.txt← Daftar library Python
│
└── images/         ← Folder gambar produk
    ├── Koko_lengan_panjang_bordir_2.jpeg
    └── ... (52 gambar produk)
```

---

## 🗄️ Struktur Database

### Database: `dbgrandmode`

#### Tabel `admin`
| Kolom      | Tipe         | Keterangan                        |
|------------|--------------|-----------------------------------|
| id         | INT PK AI    | ID admin                          |
| username   | VARCHAR(50)  | Username unik                     |
| password   | VARCHAR(255) | Password bcrypt hash (terenkripsi)|
| created_at | DATETIME     | Waktu dibuat                      |

#### Tabel `produk`
| Kolom       | Tipe           | Keterangan                  |
|-------------|----------------|-----------------------------|
| id          | INT PK AI      | ID produk                   |
| nama_produk | VARCHAR(100)   | Nama produk                 |
| bahan       | VARCHAR(50)    | Jenis bahan kain            |
| motif       | VARCHAR(50)    | Motif/corak produk          |
| warna       | VARCHAR(50)    | Warna produk                |
| ukuran      | VARCHAR(20)    | Ukuran (S/M/L/XL/XXL)       |
| kategori    | VARCHAR(50)    | Koko/Kurta/Jubah Pria       |
| harga       | DECIMAL(12,0)  | Harga satuan (Rupiah)       |
| stok        | INT            | Jumlah stok tersedia        |
| gambar      | VARCHAR(255)   | Nama file gambar            |
| created_at  | DATETIME       | Waktu ditambahkan           |
| updated_at  | DATETIME       | Waktu terakhir diupdate     |

---

## 📊 Data Penjualan / Stok Awal

| Kategori   | Jumlah SKU | Total Stok | Harga Min | Harga Max |
|------------|-----------|------------|-----------|-----------|
| Koko Pria  | 38        | 598        | Rp 145.000| Rp 210.000|
| Kurta Pria | 2         | 18         | Rp 235.000| Rp 235.000|
| Jubah Pria | 12        | 79         | Rp 285.000| Rp 325.000|
| **Total**  | **52**    | **695**    | Rp 145.000| Rp 325.000|

**Catatan:** Produk dengan stok < 10 pcs ditandai sebagai stok rendah dan memerlukan reorder segera.

---

## ✅ Fitur yang Diimplementasikan

### Autentikasi
- ✅ Halaman Login dengan validasi username & password
- ✅ Password dienkripsi menggunakan **bcrypt** (bukan MD5/SHA)
- ✅ Session management via `st.session_state` (Streamlit built-in)
- ✅ Semua halaman CRUD hanya bisa diakses setelah login
- ✅ Tombol Logout

### CRUD Produk
- ✅ **Create** — Form tambah produk baru dengan upload gambar
- ✅ **Read** — Tabel daftar produk dengan filter & pencarian
- ✅ **Update** — Form edit produk dengan preview gambar
- ✅ **Delete** — Hapus produk dengan konfirmasi

### Fitur Tambahan
- ✅ Dashboard dengan kartu statistik (total produk, stok, nilai)
- ✅ Peringatan otomatis untuk produk stok rendah (< 10 pcs)
- ✅ Filter produk (kategori, ukuran, level stok, pencarian teks)
- ✅ Laporan ringkasan per kategori
- ✅ Badge warna berbeda per kategori (Koko/Kurta/Jubah)
- ✅ Indikator warna stok (merah = rendah, hijau = aman)

---

## 🚀 Cara Menjalankan

### 1. Persiapkan Database
```bash
# Buka phpMyAdmin di: http://localhost/phpmyadmin
# Buat database baru bernama: dbgrandmode
# Import file: database.sql
```

### 2. Install Dependencies
```bash
pip install streamlit mysql-connector-python bcrypt pandas
```

Atau:
```bash
pip install -r requirements.txt
```

### 3. Sesuaikan Koneksi Database
Edit file `koneksi.py`:
```python
def get_koneksi():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",        # ← isi jika ada password MySQL
        database="dbgrandmode",
    )
```

### 4. Jalankan Aplikasi
```bash
streamlit run app.py
```

Buka browser: **http://localhost:8501**

### 5. Login Admin
| Field    | Value     |
|----------|-----------|
| Username | `admin`   |
| Password | `admin123`|

---

## 🔒 Catatan Keamanan

- Password admin **tidak disimpan dalam plain text**. Menggunakan algoritma **bcrypt** dengan salt rounds=12
- Hash contoh: `$2b$12$KIX...` (bcrypt format)
- Untuk mengubah password, gunakan fungsi `hash_password()` di `auth.py`:
  ```python
  from auth import hash_password
  print(hash_password("password_baru_anda"))
  ```
  Kemudian UPDATE field `password` di tabel `admin` dengan nilai hash tersebut.

---

## 👨‍💻 Informasi Mahasiswa

| Field     | Keterangan                         |
|-----------|------------------------------------|
| Tema      | Sistem Manajemen Stok Muslim Pria  |
| Toko      | Grand Mode                         |
| Framework | Python Streamlit                   |
| Database  | MySQL (phpMyAdmin)                 |
| Skema UJK | Junior Web Programmer (JWP)        |

---

*Dibuat untuk keperluan Ujian Kompetensi Kejuruan (UJK) — Universitas Duta Bangsa Surakarta*
