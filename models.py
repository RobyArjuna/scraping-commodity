import sqlalchemy
from database import metadata, engine

# Kita ganti nama tabelnya menjadi 'harga_pasar'
# Ini adalah skema format LONG yang ideal
harga_pasar = sqlalchemy.Table(
    "hasil_pangan",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    
    # Informasi dari mana data berasal
    sqlalchemy.Column("kabupaten", sqlalchemy.String(100)),
    sqlalchemy.Column("pasar", sqlalchemy.String(100)),
    
    # Data utamanya
    sqlalchemy.Column("tanggal", sqlalchemy.Date), # Kita akan gunakan tipe Date
    sqlalchemy.Column("komoditas", sqlalchemy.String(255)),
    sqlalchemy.Column("harga", sqlalchemy.Integer) # Simpan harga sebagai Angka
)


def create_tables():
    """
    Fungsi untuk membuat semua tabel yang telah didefinisikan
    di 'metadata'.
    """
    print("Membuat tabel 'harga_pasar' di database (jika belum ada)...")
    metadata.create_all(engine)
    print("Tabel berhasil dibuat.")

# Jalankan file ini sekali untuk membuat tabel
if __name__ == "__main__":
    create_tables()