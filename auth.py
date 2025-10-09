# auth.py
import os, binascii
from dotenv import load_dotenv
from argon2 import PasswordHasher
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import psycopg2
from db import get_conn

# ------------------------------------------------------------
# 🔹 Configuración inicial
# ------------------------------------------------------------
load_dotenv()
ENC_KEY = binascii.unhexlify(os.getenv("ENC_KEY_HEX"))   # 32 bytes (64 hex)
ph = PasswordHasher()  # Hash de contraseñas con Argon2id


# ------------------------------------------------------------
# 🔹 Función auxiliar para convertir datos binarios (fix memoryview)
# ------------------------------------------------------------
def _to_bytes(x):
    if x is None:
        return None
    if isinstance(x, (bytes, bytearray)):
        return bytes(x)
    if isinstance(x, memoryview):
        return x.tobytes()
    return x


# ------------------------------------------------------------
# 🔹 Cifrado y descifrado con ChaCha20-Poly1305
# ------------------------------------------------------------
def _enc(text: str | None, aad: bytes):
    """Cifra texto con ChaCha20-Poly1305 (retorna nonce, tag, ciphertext)."""
    if not text:
        return (None, None, None)
    aead = ChaCha20Poly1305(ENC_KEY)
    nonce = os.urandom(12)  # 96-bit nonce
    out = aead.encrypt(nonce, text.encode(), aad)  # ciphertext + tag
    return nonce, out[-16:], out[:-16]  # separa tag (últimos 16 bytes)


def _dec(nonce, tag, ct, aad: bytes):
    """Descifra texto con ChaCha20-Poly1305."""
    if not (nonce and tag and ct):
        return None
    nonce = _to_bytes(nonce)
    tag = _to_bytes(tag)
    ct = _to_bytes(ct)
    aead = ChaCha20Poly1305(ENC_KEY)
    pt = aead.decrypt(nonce, ct + tag, aad)  # unir ciphertext + tag
    return pt.decode()


# ------------------------------------------------------------
# 🔹 Registrar usuario (nombre, correo, teléfono cifrados)
# ------------------------------------------------------------
def register_user(username: str, password: str, name: str, email: str, phone: str | None):
    if not username or not password or not name or not email:
        raise ValueError("Faltan campos obligatorios")

    pw_hash = ph.hash(password)
    aad = username.encode()  # datos adicionales autenticados (AAD)

    n1, t1, c1 = _enc(name, aad)
    n2, t2, c2 = _enc(email, aad)
    n3, t3, c3 = _enc(phone, aad)

    sql = """
    INSERT INTO users (
      username, password_hash,
      name_nonce,  name_tag,  name_ct,
      email_nonce, email_tag, email_ct,
      phone_nonce, phone_tag, phone_ct
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    RETURNING id;
    """

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            sql,
            (
                username,
                pw_hash,
                psycopg2.Binary(n1),
                psycopg2.Binary(t1),
                psycopg2.Binary(c1),
                psycopg2.Binary(n2),
                psycopg2.Binary(t2),
                psycopg2.Binary(c2),
                psycopg2.Binary(n3) if n3 else None,
                psycopg2.Binary(t3) if t3 else None,
                psycopg2.Binary(c3) if c3 else None,
            ),
        )
        return cur.fetchone()[0]


# ------------------------------------------------------------
# 🔹 Verificar inicio de sesión
# ------------------------------------------------------------
def verify_login(username: str, password: str) -> bool:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT password_hash FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        if not row:
            return False
        try:
            return ph.verify(row[0], password)
        except Exception:
            return False


# ------------------------------------------------------------
# 🔹 Obtener perfil (descifrar datos del usuario)
# ------------------------------------------------------------
def get_profile(username: str) -> dict | None:
    sql = """
    SELECT name_nonce,name_tag,name_ct,
           email_nonce,email_tag,email_ct,
           phone_nonce,phone_tag,phone_ct
    FROM users WHERE username=%s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (username,))
        r = cur.fetchone()
        if not r:
            return None
        aad = username.encode()
        return {
            "name": _dec(r[0], r[1], r[2], aad),
            "email": _dec(r[3], r[4], r[5], aad),
            "phone": _dec(r[6], r[7], r[8], aad) if r[6] else None,
        }
