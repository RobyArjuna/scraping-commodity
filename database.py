import databases
import sqlalchemy

DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "hasil_pangan"
# ------------------------------------------

# Format URL koneksi: "mysql+pymysql://<user>:<password>@<host>/<database_name>"
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Buat instance database yang akan digunakan di seluruh aplikasi
database = databases.Database(DATABASE_URL)

# SQLAlchemy metadata
metadata = sqlalchemy.MetaData()

# Engine SQLAlchemy (dibutuhkan untuk membuat tabel)
engine = sqlalchemy.create_engine(DATABASE_URL)