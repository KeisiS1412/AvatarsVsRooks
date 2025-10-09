import psycopg2
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

DB_HOST = "bytencr-db.postgres.database.azure.com"
DB_NAME = "postgres"
DB_USER = "adminuser"
DB_PASS = "bytencr2025*"  
DB_PORT = 5432

def encrypt_data(data, key):
    nonce = os.urandom(16)
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data.encode('utf-8'))
    return nonce, ciphertext

def decrypt_data(ciphertext, key, nonce):
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext)
    return plaintext.decode('utf-8')

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        sslmode="require"
    )
    print("Conexión exitosa a PostgreSQL en Azure")

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username TEXT,
            password BYTEA,
            nonce BYTEA
        );
    """)
    conn.commit()
    print("Tabla creada o verificada")

except Exception as e:
    print("Error al conectar:", e)

finally:
    if 'conn' in locals():
        conn.close()
