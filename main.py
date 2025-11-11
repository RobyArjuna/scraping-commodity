from fastapi import FastAPI, HTTPException
from datetime import datetime  # Pastikan ini diimpor
from database import database
from models import harga_pasar
from scraper import run_scrape_and_clean
import traceback  # Impor traceback untuk error

app = FastAPI(title="Scraper API")

@app.on_event("startup")
async def startup():
    print("Menghubungkan ke database...")
    try:
        await database.connect()
        print("Berhasil terhubung ke database.")
    except Exception as e:
        print(f"GAGAL terhubung ke database: {e}")

@app.on_event("shutdown")
async def shutdown():
    print("Memutuskan koneksi database...")
    await database.disconnect()
    print("Koneksi database terputus.")

@app.get("/")
def read_root():
    return {"message": "Selamat datang di Scraper API. Gunakan endpoint POST /scrape-and-save untuk memulai."}

@app.post("/scrape-and-save")
async def scrape_and_save_data(tanggal: str | None = None):
    """
    Endpoint ini akan memicu proses scraping, cleaning,
    transformasi (melt), dan penyimpanan ke database.

    Anda bisa menambahkan query parameter ?tanggal=YYYY-MM-DD
    untuk mengambil data di tanggal spesifik.
    """
    print(f"Menerima permintaan di /scrape-and-save... Tanggal diminta: {tanggal if tanggal else 'Default (H-1)'}")
    
    # --- BLOK 1: VALIDASI INPUT ---
    # Kita cek dulu input 'tanggal'.
    if tanggal:
        try:
            # Coba validasi formatnya
            datetime.strptime(tanggal, "%Y-%m-%d")
        except ValueError:
            # Jika format salah, langsung kirim error 400 ke user dan STOP
            print(f"Format tanggal salah: {tanggal}")
            raise HTTPException(
                status_code=400, # 400 Bad Request
                detail=f"Format tanggal '{tanggal}' salah. Harap gunakan format YYYY-MM-DD."
            )
            
    # --- BLOK 2: PROSES UTAMA ---
    # Jika kode sampai di sini, artinya 'tanggal' aman (valid atau None).
    # Kita HANYA perlu SATU blok try...except untuk menjalankan scraper.
    try:
        # Panggil scraper dengan tanggal (atau None)
        data_to_save = await run_scrape_and_clean(tanggal_str=tanggal)
        
        if not data_to_save:
            print("Tidak ada data baru untuk disimpan.")
            return {"status": "success", "message": "Proses selesai, namun tidak ada data baru untuk disimpan."}

        # Simpan ke database
        query = harga_pasar.insert()
        await database.execute_many(query=query, values=data_to_save)
        
        print(f"Berhasil menyimpan {len(data_to_save)} item ke database.")
        
        return {
            "status": "success", 
            "message": f"Berhasil scrape dan menyimpan {len(data_to_save)} item."
        }
        
    except Exception as e:
        # Jika terjadi error saat scraping (Selenium, dll), tangkap di sini
        print(f"Terjadi error internal saat scraping: {e}")
        traceback.print_exc() # Cetak error detail ke konsol
        raise HTTPException(
            status_code=500, # 500 Internal Server Error
            detail=f"Terjadi error internal pada server: {e}"
        )