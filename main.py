from fastapi import FastAPI, HTTPException

from database import database
# --- PERUBAHAN DI SINI ---
from models import harga_pasar  # Impor tabel 'harga_pasar' yang baru
# -------------------------
from scraper import run_scrape_and_clean

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
async def scrape_and_save_data():
    """
    Endpoint ini akan memicu proses scraping, cleaning,
    transformasi (melt), dan penyimpanan ke database.
    """
    print("Menerima permintaan di /scrape-and-save...")
    try:
        # 1. Panggil fungsi orkestrator
        # Ini sekarang mengembalikan data LONG (list of dicts)
        data_to_save = await run_scrape_and_clean()
        
        if not data_to_save:
            print("Tidak ada data baru untuk disimpan.")
            return {"status": "success", "message": "Proses selesai, namun tidak ada data baru untuk disimpan."}

        # 2. Siapkan query untuk memasukkan data
        # --- PERUBAHAN DI SINI ---
        query = harga_pasar.insert() # Gunakan tabel 'harga_pasar'
        # -------------------------
        
        # 3. Eksekusi query
        await database.execute_many(query=query, values=data_to_save)
        
        print(f"Berhasil menyimpan {len(data_to_save)} item ke database.")
        
        return {
            "status": "success", 
            "message": f"Berhasil scrape dan menyimpan {len(data_to_save)} item."
        }
        
    except Exception as e:
        print(f"Terjadi error: {e}")
        # Cetak traceback untuk info lebih detail
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Terjadi error: {e}")
