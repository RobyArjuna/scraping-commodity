from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from datetime import datetime, timedelta
import pandas as pd
import time
import os
from fastapi.concurrency import run_in_threadpool

# -----------------------------------------------------------------
# --- FUNGSI 1: KODE SCRAPING ANDA (SUDAH DIMODIFIKASI) ---
# -----------------------------------------------------------------
def scrape_siska_harga():
    """
    Scraper untuk mengambil data harga pasar dari SISKA Jatim.
    MODIFIKASI:
    - Mengambil data H-1 (kemarin) saja, agar cepat untuk API.
    - Tidak lagi menyimpan ke file CSV/Excel, tapi me-return DataFrame.
    """
    print("Memulai 'scrape_siska_harga'...")
    debug_dir = "temp_debug"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)

    chrome_options = Options()
    # PENTING: Untuk FastAPI/server, 'headless' biasanya WAJIB
    chrome_options.add_argument('--headless') 
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)
    
    all_data = []
    komoditas_order = [] 
    order_captured = False
    
    try:
        url = "https://siskaperbapo.jatimprov.go.id/harga/tabel"
        print(f"Membuka URL: {url}")
        driver.get(url)
        time.sleep(3)
        
        wait.until(EC.element_to_be_clickable((By.ID, "kabkota")))
        
        print("Memilih area: Kabupaten Blitar")
        area_select = Select(wait.until(EC.presence_of_element_located((By.ID, "kabkota"))))
        area_select.select_by_visible_text("Kabupaten Blitar")
        time.sleep(3) 
        
        print("Memilih pasar: Pasar Wlingi")
        pasar_select = Select(wait.until(EC.presence_of_element_located((By.ID, "pasar"))))
        pasar_select.select_by_visible_text("Pasar Wlingi")
        time.sleep(5) 
        
        # --- MODIFIKASI UNTUK API ---
        # Kita hanya ambil data 1 HARI SAJA (kemarin), agar API responsif.
        # Mengambil data berbulan-bulan via API akan timeout.
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday
        end_date = yesterday
        
        total_days = (end_date - start_date).days + 1
        
        print("="*60)
        print(f"PERIODE: {start_date.strftime('%Y-%m-%d')} (H-1 Saja)")
        print("="*60)
        
        current_date = start_date
        success_count = 0
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d") 
            date_print = current_date.strftime("%d/%m/%Y") 
            print(f"Mengambil data tanggal: {date_print} ...", end="", flush=True)
            
            try:
                max_retries = 2
                success = False
                
                for attempt in range(max_retries):
                    try:
                        date_picker = wait.until(EC.presence_of_element_located((By.ID, "tanggal")))
                        
                        driver.execute_script("arguments[0].removeAttribute('readonly');", date_picker)
                        date_picker.clear()
                        time.sleep(0.3)
                        driver.execute_script(f"arguments[0].value = '{date_str}';", date_picker)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", date_picker)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_picker)
                        time.sleep(0.5) 
                        
                        tampilkan_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Tampilkan')]")))
                        driver.execute_script("arguments[0].click();", tampilkan_button)
                        
                        try:
                            wait.until(EC.invisibility_of_element_located((By.ID, "overlay_container")))
                        except TimeoutException:
                            pass 
                        
                        time.sleep(2)
                        
                        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")))
                        tbody_rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                        
                        if len(tbody_rows) == 0: 
                            print("⚠ Data TIDAK TERSEDIA")
                            break
                        
                        komoditas_count = 0
                        
                        for row_idx, row in enumerate(tbody_rows):
                            cells = row.find_elements(By.TAG_NAME, "td")
                            
                            if not cells or len(cells) < 3:
                                continue
                            
                            try:
                                komoditas = cells[1].text.strip()
                                harga = None
                                
                                if len(cells) >= 5:
                                    harga = cells[4].text.strip()
                                
                                if (not harga or harga == "-" or not harga.replace(".", "").replace(",", "").isdigit()) and len(cells) >= 4:
                                    harga = cells[3].text.strip()
                                
                                if (not harga or harga == "-" or not harga.replace(".", "").replace(",", "").isdigit()) and len(cells) >= 3:
                                    harga = cells[2].text.strip()
                                
                                if not komoditas or not harga or harga == "-" or not any(char.isdigit() for char in harga):
                                    continue
                            
                            except Exception:
                                continue
                            
                            if not order_captured:
                                komoditas_order.append(komoditas)
                            
                            all_data.append({
                                'Tanggal': date_print, 
                                'Komoditas': komoditas,
                                'Harga': harga,
                            })
                            komoditas_count += 1
                        
                        if not order_captured and komoditas_count > 0:
                            order_captured = True
                        
                        print(f"✓ {komoditas_count} komoditas ditemukan.")
                        success_count += 1
                        success = True
                        break
                        
                    except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
                        if attempt < max_retries - 1:
                            print(f"↻ Retry {attempt + 1}...", end=" ", flush=True)
                            time.sleep(2)
                            continue
                        else:
                            raise e
            
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                try:
                    driver.save_screenshot(os.path.join(debug_dir, f"error_{date_str.replace('-', '_')}.png"))
                except: pass
            
            current_date += timedelta(days=1)
        
        print("\nScraping Selesai.")
        
        if all_data:
            df_long = pd.DataFrame(all_data)
            df_long['Harga_Clean'] = df_long['Harga'].astype(str).str.replace(r'[^\d]', '', regex=True).replace('', None)
            df_long['Harga_Clean'] = pd.to_numeric(df_long['Harga_Clean'], errors='coerce')

            df_pivot = df_long.pivot_table(
                index='Tanggal',
                columns='Komoditas',
                values='Harga_Clean',
                aggfunc='first' 
            ).reset_index()
            
            df_pivot['Tanggal_Sort'] = pd.to_datetime(df_pivot['Tanggal'], format='%d/%m/%Y')
            df_pivot = df_pivot.sort_values('Tanggal_Sort').drop('Tanggal_Sort', axis=1)
    
            available_komoditas = [k for k in komoditas_order if k in df_pivot.columns]
            df_pivot = df_pivot[['Tanggal'] + available_komoditas]
            
            print(f"✓ Pivot table (WIDE) berhasil dibuat: {df_pivot.shape[0]} baris x {df_pivot.shape[1]} kolom")
            
            # RETURN DataFrame, jangan simpan ke file
            return df_pivot
        else:
            print("✗ TIDAK ADA DATA yang berhasil di-scrape!")
            return None
        
    except Exception as e:
        print(f"\n✗ ERROR FATAL di Selenium: {str(e)}")
        try:
            driver.save_screenshot(os.path.join(debug_dir, "error_fatal_screenshot.png"))
        except: pass
        raise
        
    finally:
        print("Menutup browser...")
        driver.quit()

# -----------------------------------------------------------------
# --- FUNGSI 2: KODE CLEANING ANDA (SUDAH DIMODIFIKASI) ---
# -----------------------------------------------------------------
def clean_siska_data(df_wide: pd.DataFrame):
    """
    Membersihkan data WIDE yang dihasilkan oleh 'scrape_siska_harga'.
    MODIFIKASI: Menerima DataFrame, bukan membaca file.
    """
    print("Memulai 'clean_siska_data'...")
    if df_wide is None or df_wide.empty:
        print("Data input kosong, proses cleaning dilewati.")
        return None
        
    df = df_wide.copy()
    
    columns_to_remove = []
    columns_to_rename = {}
    
    for col in df.columns:
        if col == 'Tanggal':
            continue
        
        col_letters_only = ''.join([c for c in col if c.isalpha()])
        
        if col_letters_only and col_letters_only.isupper():
            columns_to_remove.append(col)
        elif col.startswith('- '):
            new_name = col[2:] 
            columns_to_rename[col] = new_name
    
    print(f"Menghapus {len(columns_to_remove)} kolom kategori.")
    df_clean = df.drop(columns=columns_to_remove)
    
    print(f"Membersihkan {len(columns_to_rename)} nama kolom.")
    df_clean = df_clean.rename(columns=columns_to_rename)
    
    print(f"✓ Data WIDE bersih: {df_clean.shape[0]} baris x {df_clean.shape[1]} kolom")
    return df_clean

# -----------------------------------------------------------------
# --- FUNGSI 3: TRANSFORMASI (FUNGSI BARU) ---
# -----------------------------------------------------------------
def transform_to_long_format(df_clean: pd.DataFrame, kabupaten: str, pasar: str):
    """
    Mengubah (melt) data WIDE bersih menjadi data LONG
    agar siap dimasukkan ke database.
    """
    print("Memulai 'transform_to_long_format' (Melt)...")
    if df_clean is None or df_clean.empty:
        print("Data bersih kosong, proses transformasi dilewati.")
        return [] # Kembalikan list kosong

    # 1. "Melt" data
    df_long = df_clean.melt(
        id_vars=['Tanggal'],
        var_name='komoditas',
        value_name='harga'
    )
    
    # 2. Konversi 'Tanggal' ke format YYYY-MM-DD
    # (PENTING untuk tipe data DATE di MySQL)
    df_long['tanggal_dt'] = pd.to_datetime(df_long['Tanggal'], format='%d/%m/%Y')
    df_long['tanggal'] = df_long['tanggal_dt'].dt.date
    
    # 3. Hapus data yang harganya kosong (NaN)
    df_long = df_long.dropna(subset=['harga'])
    
    # 4. Pastikan harga adalah integer
    df_long['harga'] = df_long['harga'].astype(int)
    
    # 5. Tambahkan info statis
    df_long['kabupaten'] = kabupaten
    df_long['pasar'] = pasar
    
    # 6. Pilih hanya kolom yang sesuai dengan DB
    final_columns = ['tanggal', 'kabupaten', 'pasar', 'komoditas', 'harga']
    df_final = df_long[final_columns]
    
    # 7. Konversi ke List of Dictionaries
    data_for_db = df_final.to_dict('records')
    
    print(f"✓ Data LONG berhasil dibuat: {len(data_for_db)} baris data.")
    return data_for_db

# -----------------------------------------------------------------
# --- FUNGSI 4: WRAPPER UTAMA (DIMODIFIKASI) ---
# -----------------------------------------------------------------
async def run_scrape_and_clean():
    """
    Orkestrator: Menjalankan scraping, cleaning, dan transformasi.
    Semua fungsi 'sync' (Selenium, Pandas) dijalankan di thread pool.
    """
    print("Memulai job 'run_scrape_and_clean'...")
    
    # 1. Scrape (Selenium, butuh thread pool)
    # Kita hardcode nama pasar, bisa juga dijadikan parameter
    KABUPATEN = "Kabupaten Blitar"
    PASAR = "Pasar Wlingi"
    
    df_wide = await run_in_threadpool(scrape_siska_harga)
    
    if df_wide is None:
        print("Scraping tidak menghasilkan data. Berhenti.")
        return []
        
    # 2. Clean (Pandas, butuh thread pool)
    df_clean = await run_in_threadpool(clean_siska_data, df_wide)
    
    if df_clean is None:
        print("Cleaning tidak menghasilkan data. Berhenti.")
        return []
        
    # 3. Transform (Pandas, butuh thread pool)
    data_long = await run_in_threadpool(transform_to_long_format, df_clean, KABUPATEN, PASAR)
    
    print("Job 'run_scrape_and_clean' selesai.")
    return data_long