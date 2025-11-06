import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL tidak ditemukan di environment variables")

print(f"Menghubungkan ke database...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("Menghapus kolom status dari tabel orders...")
        conn.execute(text("ALTER TABLE orders DROP COLUMN status"))
        conn.execute(text("COMMIT"))
        print("Kolom status berhasil dihapus dari tabel orders")
except Exception as e:
    print(f"Error: {str(e)}")