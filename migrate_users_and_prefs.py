# migrate_users_and_prefs.py
from db import get_conn

with get_conn() as conn, conn.cursor() as cur:
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name_nonce BYTEA,  name_tag BYTEA,  name_ct BYTEA,
        email_nonce BYTEA, email_tag BYTEA, email_ct BYTEA,
        phone_nonce BYTEA, phone_tag BYTEA, phone_ct BYTEA
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_prefs (
        username TEXT PRIMARY KEY REFERENCES users(username) ON DELETE CASCADE,
        hobby TEXT
    );
    """)
    conn.commit()
print("OK - tablas listas")
