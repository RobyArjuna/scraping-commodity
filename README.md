Proyek Scraper Harga SISKA Jatim (FastAPI + MySQL)

Sebuah aplikasi API (FastAPI) untuk melakukan scraping data harga komoditas dari website SISKA Jatim, membersihkannya, dan menyimpannya ke database MySQL.

Proyek ini dirancang untuk berjalan secara otomatis (via panggilan API) untuk mengambil data harian, melakukan pembersihan dan transformasi data, lalu menyimpannya dalam format long yang siap untuk dianalisis.

Fitur Utama

🚀 API Server: Dibangun dengan FastAPI untuk endpoint yang cepat dan dokumentasi otomatis (/docs).

🕷️ Scraper Canggih: Menggunakan Selenium (headless) untuk menangani website JavaScript-heavy.

🧹 Pembersihan Data: Menggunakan Pandas untuk membersihkan nama kolom, menghapus kategori, dan memvalidasi harga.

🔄 Transformasi Data: Secara otomatis mengubah data (unpivot/melt) dari format wide (ratusan kolom) ke format long (siap untuk database).

🗃️ Penyimpanan Database: Terintegrasi dengan MySQL menggunakan SQLAlchemy dan databases untuk operasi async.

Diagram Alur Kerja

User (atau sistem otomatis) memanggil endpoint POST /scrape-and-save.

FastAPI menerima permintaan dan memanggil fungsi orkestrator di scraper.py.

scraper.py menjalankan Selenium (secara headless) untuk membuka website SISKA Jatim, memilih "Kab. Blitar" dan "Pasar Wlingi", lalu mengambil data harga H-1.

Data mentah (format wide) dibersihkan oleh fungsi clean_siska_data() menggunakan Pandas.

Data bersih ditransformasi menjadi format long oleh fungsi transform_to_long_format().

List data bersih (format long) dikembalikan ke main.py.

main.py menyimpan data tersebut ke tabel harga_pasar di MySQL.

Teknologi yang Digunakan

Kategori

Teknologi

Versi/Spesifikasi

Backend

Python

3.7+

Framework API

FastAPI

0.100+

Server

Uvicorn

Standar

Database

MySQL

5.7+ / 8.0+

Scraping

Selenium

4.x

Data Handling

Pandas

2.x

ORM/Konektor DB

SQLAlchemy

Core

Konektor Async

databases

[mysql]

Driver MySQL

PyMySQL

-

Struktur Proyek

/proyek_scraper
    |-- venv/               # Folder virtual environment
    |-- temp_debug/         # (Otomatis dibuat) Menyimpan screenshot jika terjadi error
    |-- main.py             # Aplikasi utama FastAPI dan endpoint API
    |-- database.py         # Konfigurasi koneksi ke database MySQL
    |-- models.py           # Definisi skema tabel database (SQLAlchemy)
    |-- scraper.py          # Logika utama untuk scraping (Selenium) dan cleaning (Pandas)
    |-- requirements.txt    # Daftar library Python yang dibutuhkan
    |-- chromedriver.exe    # (Harus di-download, lihat Setup)
    `-- README.md           # (File ini)


Setup & Instalasi

Langkah-langkah ini hanya perlu dilakukan satu kali saat pertama kali setup.

1. Prasyarat

Python 3.7+

Server MySQL (Contoh: XAMPP, Laragon, Docker, atau MySQL Community Server)

Google Chrome (ter-install di sistem Anda)

2. Kloning & Virtual Environment

# 1. Kloning atau download proyek ini
# git clone ... (jika ada)
cd proyek_scraper

# 2. Buat virtual environment
python -m venv venv

# 3. Aktifkan venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate


3. Install Library

Pastikan (venv) Anda aktif, lalu install semua library yang ada di requirements.txt:

pip install -r requirements.txt


4. Download chromedriver (Wajib)

Cek versi Google Chrome Anda (Settings > About Chrome).

Download chromedriver yang versinya sesuai dari: https://googlechromelabs.github.io/chrome-for-testing/

Ekstrak file zip-nya dan letakkan file chromedriver.exe (atau chromedriver) di dalam folder utama proyek ini (sejajar dengan main.py).

Konfigurasi Database

Sebelum bisa menjalankan, Anda harus menghubungkan proyek ini ke database MySQL Anda.

Buat Database:
Buka phpMyAdmin/DBeaver/SQLYog, lalu buat database baru dengan nama db_scraper.

CREATE DATABASE db_scraper;


Setting Koneksi:
Buka file database.py dan edit bagian ini dengan kredensial MySQL Anda:

# --- GANTI BAGIAN INI DENGAN MILIK ANDA ---
DB_USER = "root"
DB_PASSWORD = "password_anda"  # <-- Ganti ini! (Jika XAMPP, biasanya "" atau "root")
DB_HOST = "localhost"
DB_NAME = "db_scraper"
# ------------------------------------------


Cara Menjalankan

Setelah semua setup selesai, ikuti 3 langkah ini untuk menjalankan aplikasi.

1️⃣ Langkah 1: Buat Tabel Database

Kita perlu membuat tabel harga_pasar di dalam db_scraper sesuai skema di models.py.

Jalankan file models.py langsung dari terminal:

python models.py


Output: Membuat tabel 'harga_pasar' ... Tabel berhasil dibuat.

2️⃣ Langkah 2: Jalankan Server FastAPI

Jalankan server Uvicorn. Server ini akan terus berjalan dan menunggu perintah.

uvicorn main:app --reload


Output: Uvicorn running on http://127.0.0.1:8000

3️⃣ Langkah 3: Trigger Scraper

Server yang berjalan tidak otomatis men-scrape. Anda perlu memicu-nya dengan cara memanggil API.

Buka browser dan kunjungi http://127.0.0.1:8000/docs

Anda akan melihat dokumentasi API. Klik endpoint POST /scrape-and-save.

Klik tombol "Try it out".

Klik tombol "Execute".

Sabar! Lihat terminal tempat uvicorn berjalan. Proses scraping Selenium akan memakan waktu 30-60 detik. Anda akan melihat log print() dari proses tersebut.

Setelah selesai, Anda akan mendapat respons JSON di browser dan data akan masuk ke database MySQL Anda.