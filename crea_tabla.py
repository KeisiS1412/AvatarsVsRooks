import psycopg2, os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    dbname=os.getenv("PGDATABASE"),  # avataresdb
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    sslmode=os.getenv("PGSSLMODE","require"),
)
with conn, conn.cursor() as cur:
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,               -- Argon2 (hash, no reversible)
        -- Campos cifrados con ChaCha20-Poly1305:
        name_nonce  BYTEA, name_tag  BYTEA, name_ct  BYTEA,
        email_nonce BYTEA, email_tag BYTEA, email_ct BYTEA,
        phone_nonce BYTEA, phone_tag BYTEA, phone_ct BYTEA,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
print("Tabla users lista")
