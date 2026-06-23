# 🎵 YTMP3-Converter: YouTube to MP3 Web Application

**Selamat datang di dokumentasi lengkap proyek YTMP3-Converter.**  
Aplikasi web sederhana berbasis Flask ini memungkinkan pengguna untuk mengunduh audio dari video YouTube dan mengonversinya ke format MP3 dengan pilihan kualitas yang beragam. Proyek ini dirancang untuk mengatasi berbagai tantangan teknis yang dihadapi ketika mengakses YouTube, terutama terkait autentikasi, signature protection, dan pembatasan akses, tanpa mengharuskan pengguna untuk login atau menyimpan data sensitif.

---

## 📌 Daftar Isi

1. [Latar Belakang](#-latar-belakang)
2. [Tujuan Proyek](#-tujuan-proyek)
3. [Teknologi yang Digunakan](#-teknologi-yang-digunakan)
4. [Struktur Proyek](#-struktur-proyek)
5. [Alur Kerja (Workflow)](#-alur-kerja-workflow)
6. [Fitur Unggulan](#-fitur-unggulan)
7. [Keamanan](#-keamanan)
8. [Panduan Instalasi](#-panduan-instalasi)
9. [Panduan Penggunaan](#-panduan-penggunaan)
10. [Penjelasan Teknis Mendalam](#-penjelasan-teknis-mendalam)
11. [Troubleshooting Umum](#-troubleshooting-umum)
12. [Lisensi & Disclaimer](#-lisensi--disclaimer)
13. [Kesimpulan](#-kesimpulan)

---

## 📚 Latar Belakang

YouTube adalah platform video terbesar di dunia, tetapi menyediakan layanan streaming, bukan unduhan. Pengguna sering kali ingin menyimpan audio dari video untuk didengarkan secara offline, baik untuk keperluan pribadi, pendidikan, atau hiburan. Namun, YouTube secara aktif melindungi kontennya dengan mekanisme seperti:

- **Signature Protection**: Setiap URL video memiliki tanda tangan (signature) yang harus dipecahkan untuk mengakses file media.
- **Throttling**: Pembatasan kecepatan unduh untuk koneksi yang dianggap mencurigakan.
- **Age-restriction**: Video tertentu memerlukan verifikasi usia.
- **Region Locking**: Beberapa video hanya tersedia di negara tertentu.
- **Bot Detection**: YouTube dapat memblokir IP yang melakukan banyak permintaan dalam waktu singkat.

Alat-alat seperti `yt-dlp` telah dikembangkan untuk mengatasi hambatan ini, tetapi tetap memerlukan konfigurasi yang tepat dan sering kali pembaruan berkala. Proyek ini membungkus `yt-dlp` ke dalam aplikasi web yang ramah pengguna, dengan tambahan fitur untuk mengatasi pembatasan autentikasi menggunakan **Visitor Data** dan kombinasi **player_client** yang optimal.

---

## 🎯 Tujuan Proyek

- Menyediakan antarmuka web yang mudah digunakan untuk mengunduh dan mengonversi audio YouTube ke MP3.
- Mengatasi berbagai hambatan akses YouTube tanpa mengharuskan pengguna untuk login atau membagikan kredensial pribadi.
- Menampilkan proses secara real-time agar pengguna mengetahui kemajuan unduhan dan konversi.
- Memberikan pilihan kualitas audio (128, 192, 256, 320 kbps) sesuai kebutuhan.
- Menjaga keamanan dan privasi dengan tidak menyimpan cookie atau data pribadi pengguna.
- Menyertakan panduan lengkap tentang cara mendapatkan `Visitor Data` sebagai alternatif autentikasi yang aman.

---

## 🛠️ Teknologi yang Digunakan

| Komponen | Teknologi | Fungsi |
|----------|-----------|--------|
| **Backend** | Python 3.8+ + Flask | Menyediakan server web, menangani permintaan, dan menjalankan logika bisnis. |
| **Download Engine** | `yt-dlp` | Mengunduh audio dari YouTube dengan dukungan berbagai format dan proteksi. |
| **Audio Converter** | FFmpeg | Mengonversi format audio mentah ke MP3 dengan kualitas yang ditentukan. |
| **JavaScript Runtime** | Node.js / Deno | Digunakan oleh `yt-dlp` untuk mengeksekusi JavaScript guna memecahkan signature dan n-parameter YouTube. |
| **Real-time Communication** | Server-Sent Events (SSE) | Mengirim log proses dari server ke klien secara langsung tanpa polling. |
| **Frontend** | HTML5, CSS3, Vanilla JS | Antarmuka pengguna yang responsif dan interaktif. |
| **Package Manager** | pip (Python) | Mengelola dependensi Python. |

---

## 📁 Struktur Proyek

```
YTMP3-CONVERTER/
│
├── app.py                        # Aplikasi utama Flask
├── requirements.txt              # Dependensi Python (Flask, yt-dlp)
├── Visitor Data.pdf              # Panduan visitor_data
├── .gitignore                    # Daftar file yang dikecualikan dari Git
│
├── templates/
│   └── index.html                # Halaman antarmuka pengguna
│
└── venv/                         # Virtual environment (tidak disimpan di Git)
```

---

## 🔄 Alur Kerja (Workflow)

Berikut adalah alur lengkap yang terjadi ketika pengguna menekan tombol **"Konversi & Unduh"**:

```
1. Pengguna mengisi form:
   - URL YouTube (wajib)
   - Visitor Data (opsional)
   - Kualitas MP3 (pilihan)

2. Frontend mengirim data ke /download (POST) dengan FormData.

3. Backend membuat task_id unik dan antrian log (queue).

4. Thread terpisah menjalankan fungsi run_download() dengan parameter task_id.

5. Di dalam thread:
   a. Menyusun command yt-dlp dengan opsi:
      - format: bestaudio[ext=m4a]/bestaudio/best
      - postprocessors: ekstrak audio ke MP3 dengan quality pilihan
      - extractor_args: player_client = android, ios, web
      - visitor_data (jika ada)
   b. Menjalankan subprocess yt-dlp.
   c. Setiap baris output dikirim ke antrian log.

6. Frontend membuka koneksi SSE ke /progress/<task_id>.
   - Setiap pesan dari antrian log ditampilkan sebagai baris terbaru di halaman.

7. Jika proses selesai (return_code == 0):
   a. Cari file MP3 yang dihasilkan di direktori temp.
   b. Simpan path file ke task['file_path'].
   c. Kirim sinyal "DONE_SUCCESS" ke SSE.

8. Frontend menerima "DONE_SUCCESS", lalu otomatis mengunduh file melalui /download_file/<task_id>.

9. Setelah file dikirim, direktori temp dihapus dan task dihapus dari memori.
```

---

## ⭐ Fitur Unggulan

### 1. **Tanpa Login**
- Tidak memerlukan akun Google atau kredensial pribadi.
- Menggunakan `visitor_data` (token anonim) yang aman dan mudah didapat.

### 2. **Pilihan Kualitas Audio**
- Dropdown sederhana dengan opsi: 128, 192, 256, 320 kbps.
- Default 192 kbps untuk keseimbangan ukuran dan kualitas.

### 3. **Real-time Log (SSE)**
- Menampilkan output `yt-dlp` secara langsung di halaman web.
- Hanya baris terbaru yang ditampilkan agar tidak mengganggu tampilan.
- Memberikan transparansi dan umpan balik kepada pengguna.

### 4. **Fallback Otomatis**
- Jika `visitor_data` tidak tersedia, aplikasi tetap mencoba dengan konfigurasi `player_client` (android/ios/web) yang telah terbukti optimal.
- Menggunakan `player_js_variant=tv` yang dikenal sebagai workaround untuk banyak masalah.

### 5. **Auto-cleanup**
- File MP3 sementara disimpan di direktori temp unik per task.
- Dihapus otomatis setelah pengguna mengunduh file atau jika terjadi error.
- Tidak ada penumpukan file sampah di server.

### 6. **Panduan Visitor Data**
- Tautan langsung ke file PDF yang menjelaskan langkah-langkah mendapatkan `visitor_data` dari browser (incognito).
- Memudahkan pengguna yang kurang paham teknis.

### 7. **Dukungan JavaScript Runtime**
- Mendeteksi dan memanfaatkan Node.js atau Deno secara otomatis.
- Meningkatkan kemampuan `yt-dlp` dalam memecahkan signature dan n-parameter.

---

## 🔒 Keamanan

### Prinsip Keamanan yang Diterapkan
| Aspek | Implementasi |
|-------|--------------|
| **Autentikasi** | Tidak menggunakan cookies pribadi. Cukup `visitor_data` anonim. |
| **Penyimpanan Data** | Tidak ada data pengguna yang disimpan secara permanen. |
| **File Sementara** | Dihapus segera setelah digunakan. |
| **Serangan MITM** | Semua komunikasi dilakukan melalui localhost (development) atau HTTPS (produksi). |
| **Input Validation** | URL divalidasi sebelum diproses. |

### Peringatan Penting
- Jika menggunakan aplikasi di server publik, aktifkan HTTPS dan batasi akses.
- Pastikan `visitor_data` yang digunakan diperoleh dari sesi incognito untuk mengurangi risiko.

---

## 📦 Panduan Instalasi

### Prasyarat

Sebelum menjalankan aplikasi, pastikan sistem Anda memiliki:

| Komponen | Versi Minimum | Catatan |
|----------|---------------|---------|
| Python | 3.13.13+ | [Unduh](https://www.python.org/downloads/) |
| pip | Terbaru | `python -m pip install --upgrade pip` |
| FFmpeg | 4.0+ | [Unduh](https://ffmpeg.org/download.html), pastikan ada di PATH |
| Node.js | 24.15.0+ | [Unduh](https://nodejs.org/) – direkomendasikan |
| Deno | 1.30+ | [Unduh](https://deno.land/) – alternatif Node.js |

### Langkah Instalasi

1. **Clone repositori** (atau buat folder proyek baru):
   ```bash
   git clone https://github.com/username/YTMP3-Converter.git
   cd YTMP3-Converter
   ```

2. **Buat virtual environment** (disarankan):
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/Mac
   venv\Scripts\activate         # Windows
   ```

3. **Instal dependensi Python**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Pastikan FFmpeg terinstal**:
   ```bash
   ffmpeg -version
   ```
   Jika belum, instal sesuai sistem operasi Anda.

5. **Pastikan Node.js atau Deno terinstal** (untuk signature solving):
   ```bash
   node --version
   # atau
   deno --version
   ```

6. **Jalankan aplikasi**:
   ```bash
   python app.py
   ```

7. **Buka browser** dan akses `http://localhost:5000`.

---

## 📖 Panduan Penggunaan

### Antarmuka Pengguna

1. **URL YouTube**: Tempel link video yang ingin diunduh.
2. **Visitor Data (opsional)**: Isi dengan nilai cookie `VISITOR_INFO1_LIVE` dari browser incognito (lihat panduan PDF).
3. **Kualitas Audio**: Pilih dari dropdown (default 192 kbps).
4. **Tombol "Konversi & Unduh"**: Memulai proses.

### Cara Mendapatkan Visitor Data

1. Buka YouTube di browser dalam mode **incognito/private**.
2. Buka **DevTools** (F12) → tab **Application** → **Cookies** → `https://www.youtube.com`.
3. Cari baris dengan nama `VISITOR_INFO1_LIVE`.
4. Salin nilai di kolom **Value** (misal: `zaQc_QFxudI`).
5. Tempelkan ke kolom **Visitor Data** pada aplikasi.

> **Catatan**: Visitor Data bersifat anonim dan tidak mengandung informasi pribadi. Nilai ini dapat berubah setiap kali sesi baru dibuat.

### Proses Download

- Setelah menekan tombol, area status akan menampilkan **log real-time** dari `yt-dlp`.
- Jika berhasil, file MP3 akan otomatis terunduh.
- Jika gagal, pesan error akan ditampilkan.

---

## 🔬 Penjelasan Teknis Mendalam

### Mengapa Menggunakan `visitor_data`?

YouTube menggunakan `visitor_data` untuk melacak pengguna anonim. Dengan menyertakannya dalam permintaan, `yt-dlp` dianggap sebagai pengunjung biasa, bukan bot. Ini mengurangi kemungkinan pemblokiran dan memungkinkan akses ke format audio yang lebih baik.

### Peran `player_client`

| Client | Karakteristik |
|--------|---------------|
| `android` | Format audio berkualitas baik, lebih toleran terhadap pembatasan. |
| `ios` | Menyediakan format audio premium (AAC) dan sering tidak terpengaruh error 403. |
| `web` | Client default, tetapi paling ketat dan membutuhkan `po_token` untuk beberapa video. |

Menggabungkan ketiganya memastikan fallback jika salah satu gagal.

### Signifikan `player_js_variant=tv`

Varian JavaScript TV dikenal memiliki mekanisme signature solving yang lebih sederhana dan sering berhasil di mana varian lain gagal. Ini adalah workaround yang banyak digunakan di komunitas.

### Real-time Logging dengan SSE

Server-Sent Events memungkinkan server mengirim data ke klien melalui koneksi HTTP tunggal yang persisten. Berbeda dengan WebSocket, SSE lebih sederhana dan cukup untuk kasus satu arah (server → klien). Setiap baris output `yt-dlp` dikirim sebagai event `message` dan ditampilkan di halaman.

### Penanganan File Sementara

Setiap request membuat direktori unik di `/tmp` (atau folder temp sistem). Ini menghindari konflik antara pengguna yang berbeda. Setelah file dikirim, direktori dihapus secara rekursif menggunakan `shutil.rmtree()`. Jika terjadi error, direktori juga dibersihkan untuk mencegah penumpukan.

---

## 🐛 Troubleshooting Umum

| Masalah | Penyebab | Solusi |
|---------|----------|--------|
| **"Requested format is not available"** | Versi yt-dlp usang atau format yang diminta tidak tersedia. | Update yt-dlp: `pip install --upgrade yt-dlp`. Install Node.js/Deno. |
| **"Sign in to confirm you're not a bot"** | Tidak ada autentikasi atau visitor_data. | Isi visitor_data dengan nilai dari browser incognito. |
| **Proses terhenti tanpa error** | Throttling atau koneksi terputus. | Coba gunakan proxy atau tunggu beberapa menit lalu coba lagi. |
| **File MP3 tidak terunduh otomatis** | Browser memblokir pop-up atau unduhan. | Periksa pengaturan browser, izinkan unduhan dari situs ini. |
| **ffmpeg not found** | FFmpeg tidak terinstal atau tidak ada di PATH. | Instal FFmpeg dan pastikan perintah `ffmpeg` dapat dijalankan di terminal. |
| **Node.js/Deno not detected** | Runtime belum terinstal. | Instal Node.js atau Deno. Tanpa ini, signature solving mungkin gagal. |

---

## 📄 Lisensi & Disclaimer

### Lisensi
Proyek ini menggunakan lisensi **MIT** – bebas digunakan, dimodifikasi, dan didistribusikan untuk keperluan pribadi maupun komersial, dengan syarat mencantumkan atribusi kepada pembuat asli.

### Disclaimer
- **Penggunaan aplikasi ini sepenuhnya menjadi tanggung jawab pengguna.**
- Kami tidak bertanggung jawab atas pelanggaran hak cipta, ketentuan layanan YouTube, atau kerugian yang timbul dari penggunaan alat ini.
- **Dilarang** menggunakan aplikasi untuk mengunduh konten yang dilindungi hak cipta tanpa izin.
- Aplikasi ini dibuat untuk tujuan edukasi dan pembelajaran tentang integrasi `yt-dlp` dengan Flask.

---

## 🏁 Kesimpulan

**YTMP3-Converter** adalah solusi lengkap untuk mengunduh dan mengonversi audio YouTube ke MP3 dengan cara yang aman, mudah, dan transparan. Dengan mengandalkan `visitor_data`, `yt-dlp`, dan FFmpeg, aplikasi ini mengatasi berbagai hambatan teknis tanpa mengorbankan privasi pengguna. Fitur real-time log, pilihan kualitas, dan panduan terintegrasi menjadikannya alat yang ramah bagi pengguna awam sekaligus cukup canggih untuk pengguna berpengalaman.

---

## 🙏 Kontribusi & Dukungan

Jika Anda menemukan bug atau memiliki saran perbaikan, silakan buka *issue* di repositori GitHub.

**Terima kasih telah menggunakan YTMP3-Converter!** 🎵

---

> 📌 *Terakhir diperbarui pada: Juni 2026*